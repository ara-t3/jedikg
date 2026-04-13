#!/usr/bin/env python3

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any

import torch

from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
from jdex.cli import CLI

import gc

def cleanup_torch_objects(*objs):
    for obj in objs:
        try:
            del obj
        except Exception:
            pass

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


SUPPORTED_MODELS = {"TransE", "RotatE", "ComplEx", "CompGCN"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PyKEEN on pre-split triples.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        required=True,
        help="Folder containing train.tsv, valid.tsv, test.tsv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Folder where results and model checkpoint will be saved",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        choices=sorted(SUPPORTED_MODELS),
        help="Model to train",
    )
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=128,
        help="Embedding dimension",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning Rate",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1024,
        help="Batch size (hardware dependent)",
    )
    parser.add_argument(
        "--num-epochs",
        type=int,
        default=200,
        help="Maximum number of epochs",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=[None, "cpu", "cuda"],
        help="Force device. Default: auto-detect",
    )
    return parser.parse_args()


def resolve_device(requested: str | None) -> str:
    if requested is not None:
        return requested
    return "cuda" if torch.cuda.is_available() else "cpu"



def load_split_factories(paths: Dict[str, Path], model_name: str) -> tuple[TriplesFactory, TriplesFactory, TriplesFactory]:
    create_inverse_triples = model_name == "CompGCN"

    # Train defines the canonical mappings
    training = TriplesFactory.from_path(
        paths["train"],
        create_inverse_triples=create_inverse_triples,
    )

    # Validation and test MUST reuse the exact same mappings from training
    validation = TriplesFactory.from_path(
        paths["valid"],
        entity_to_id=training.entity_to_id,
        relation_to_id=training.relation_to_id,
        create_inverse_triples=create_inverse_triples,
    )

    testing = TriplesFactory.from_path(
        paths["test"],
        entity_to_id=training.entity_to_id,
        relation_to_id=training.relation_to_id,
        create_inverse_triples=create_inverse_triples,
    )

    return training, validation, testing


def build_model_kwargs(model_name: str, embedding_dim: int) -> Dict[str, Any]:
    if model_name in {"TransE", "RotatE", "ComplEx", "CompGCN"}:
        return {"embedding_dim": embedding_dim}
    raise ValueError(f"Unsupported model: {model_name}")


def save_id_mappings(training: TriplesFactory, output_dir: Path) -> None:
    mappings_dir = output_dir / "mappings"
    mappings_dir.mkdir(parents=True, exist_ok=True)

    with open(mappings_dir / "entity_to_id.json", "w", encoding="utf-8") as f:
        json.dump(training.entity_to_id, f, indent=2, ensure_ascii=False)

    with open(mappings_dir / "relation_to_id.json", "w", encoding="utf-8") as f:
        json.dump(training.relation_to_id, f, indent=2, ensure_ascii=False)


def main() -> None:
    ui = CLI(verbose=True)

    ui.logo("JDEX-PyKEEN Train ")

    ui.rule("Start Training Procedure")


    args = parse_args()
    device = resolve_device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cwd = Path(args.dataset_dir) / "abox/experiments_split"
    owd = Path(args.output_dir) / f"{Path(args.dataset_dir).name}_{args.model}_E{args.num_epochs}_D{args.embedding_dim}"
    owd.mkdir(parents=True, exist_ok=True)


    training, validation, testing = load_split_factories({
        "train" : cwd / "train.tsv",
        "test": cwd / "test.tsv",
        "valid" :  cwd / "valid.tsv"
    }
    , args.model)

    ui.subrule("Loading Triples")

    ui.panel("Dataset & Training Info", data=[
        ("Train triples", training.num_triples),
        ("Valid triples", validation.num_triples),
        ("Test triples", testing.num_triples),
        ("Entities", training.num_entities),
        ("Relations", training.num_relations),
        ("Model", args.model),
        ("Device", device),
    ])
    

    model_kwargs = build_model_kwargs(args.model, args.embedding_dim)

    ui.subrule("Training and Model Parameters")

    ui.panel("Model Configuration", data=[
        ("Model", args.model),
        ("Embedding Dim", args.embedding_dim),
        ("Batch Size", args.batch_size),
        ("Epochs (max)", args.num_epochs),
        ("Training Loop", "sLCWA"),
        ("Negative Sampling", "Random (h, t only)"),
        ("Evaluation", "Filtered, Tail Only"),
        ("Inverse Triples", "Yes" if args.model == "CompGCN" else "No"),
        ("Learning Rate", args.lr)
    ])

    
    ui.subrule("Start Training")

    try:

        # Run training
        result = pipeline(
            training=training,
            validation=validation,
            testing=testing,
            model=args.model,
            model_kwargs=model_kwargs,
            random_seed=args.random_seed,
            device=device,

            optimizer="Adam",
            optimizer_kwargs={
             "lr":args.lr,
             },
            lr_scheduler="ExponentialLR",
            lr_scheduler_kwargs={
                "gamma": 0.99,
            },
            training_loop="sLCWA",
            training_kwargs={
                "num_epochs": args.num_epochs,
                "batch_size": args.batch_size,
            },
            negative_sampler="basic",
            negative_sampler_kwargs={
                "corruption_scheme": ["head", "tail"],
            },
            evaluator="RankBasedEvaluator",
            evaluator_kwargs={
                "filtered": True,
            },
            evaluation_kwargs={
                "batch_size": args.batch_size,
                "targets": ["tail"],
            },
            stopper="early",
        )

        ui.subrule("Results Serialization")
        
        model_path = owd / f"{owd.name}.pt"
        torch.save(result.model.state_dict(), model_path)

        save_id_mappings(training, owd)

        # Save a lightweight metrics summary
        metrics = result.metric_results.to_dict()
        with open(owd / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # Save config used for reproducibility
        config = {
            "dataset_dir": str(args.dataset_dir),
            "output_dir": str(owd),
            "model": args.model,
            "embedding_dim": args.embedding_dim,
            "batch_size": args.batch_size,
            "num_epochs": args.num_epochs,
            "random_seed": args.random_seed,
            "device": device,
            "inverse_triples_only_for_gnn": True,
            "filtered_evaluation": True,
            "prediction_target": "tail",
            "negative_sampling": "random_head_tail_only",
            "lr_scheduler": {
                "name": "ExponentialLR",
                "gamma": 0.99,
            },
            "optimizer_kwargs" : {
                "lr" : args.lr
            }
        }
        with open(owd / "run_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("\nTraining complete.")
        print(f"Saved full results to: {owd}")
        print(f"Saved model checkpoint to: {model_path}")
        print(f"Saved metrics to: {args.output_dir / 'metrics.json'}")
    
    finally:
        try:
            if result is not None and getattr(result, "model", None) is not None:
                result.model.cpu()
        except Exception:
            pass

        del result
        del training
        del validation
        del testing



if __name__ == "__main__":
    main()
