#!/usr/bin/env python3
from __future__ import annotations

import torch

import argparse
from pathlib import Path

from jdex.owl.reasoning import Reasoner

from jdex.cli import CLI

from rdflib import Graph

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
    parser = argparse.ArgumentParser(
        description="Train PyKEEN on pre-split triples.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        required=True,
        help="Folder containing train.tsv, valid.tsv, test.tsv",
    )
    parser.add_argument(
        "--predictions-dir",
        type=Path,
        required=True,
        help="Folder where predictions will be saved",
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


def main() -> None:
    ui = CLI(verbose=True)

    ui.logo("JDEX-PyKEEN Prediction Consistency Check")

    ui.rule("Start Prediction Consistency Check")

    args = parse_args()

    predictions = Graph()

    with open(Path(args.predictions_dir) / "test.nt") as f:
        for line in f:
            parts = line.strip().rsplit(" ")
            triple = " ".join(parts[:3]) + " ."
            predictions.parse(data=triple, format="nt")

    kg = Graph()
    kg.parse(Path(args.dataset_dir) / "knowledge_graph.owl")

    kg.addN((s, p, o, kg) for (s, p, o) in predictions.triples((None, None, None)))

    reasoner = Reasoner(
        reasoners_path=Path("./reasoners/unpack").absolute(),
        java8_path=".",
        java11_path="."
    )
    ui.subrule("Consistency Check")

    ans = reasoner.consistency(kg)

    print(ans)


if __name__ == "__main__":
    main()
