#!/usr/bin/env python3

from __future__ import annotations

import argparse
import gc
import heapq
import json
from pathlib import Path

import torch
from tqdm import tqdm
from pykeen.triples import TriplesFactory
from pykeen.predict import predict_target
from pykeen.models import RotatE, TransE, ComplEx, CompGCN
from rdflib import URIRef


SUPPORTED_MODELS = {"TransE", "RotatE", "ComplEx", "CompGCN"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate predictions from a trained PyKEEN model.")
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        choices=sorted(SUPPORTED_MODELS),
        help="Model type (must match the trained model)",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        required=True,
        help="Path to the trained model checkpoint (model.pt)",
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        required=True,
        help="Folder containing triples.tsv",
    )
    parser.add_argument(
        "--mappings-dir",
        type=Path,
        default=None,
        help="Folder containing mappings",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Folder where predictions will be saved",
    )
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=128,
        help="Embedding dimension (must match the trained model)",
    )
    parser.add_argument(
        "--top-k-per-hr",
        type=int,
        default=50,
        help="Top K predictions per head-relation pair",
    )
    parser.add_argument(
        "--global-top-k",
        type=int,
        default=10000,
        help="Global top K predictions to output",
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


def get_model_class(model_name: str):
    """Return the PyKEEN model class for the given model name."""
    if model_name == "TransE":
        return TransE
    elif model_name == "RotatE":
        return RotatE
    elif model_name == "ComplEx":
        return ComplEx
    elif model_name == "CompGCN":
        return CompGCN
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def maybe_add_topk(heap, item, max_size: int) -> None:
    if len(heap) < max_size:
        heapq.heappush(heap, item)
    else:
        if item[0] > heap[0][0]:
            heapq.heapreplace(heap, item)


if __name__ == "__main__":
    args = parse_args()
    device = resolve_device(args.device)

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Define output path
    output_path = args.output_dir / f"global_top_{args.global_top_k}.nt"

    # Determine mappings directory
    mappings_dir = args.mappings_dir

    # Load entity and relation mappings
    with open(mappings_dir / "entity_to_id.json", "r") as f:
        entity_to_id = json.load(f)

    with open(mappings_dir / "relation_to_id.json", "r") as f:
        relation_to_id = json.load(f)

    id_to_entity = {v: k for k, v in entity_to_id.items()}
    id_to_relation = {v: k for k, v in relation_to_id.items()}

    # Load triples
    triples = TriplesFactory.from_path(
        args.dataset_dir / "triples.tsv",
        create_inverse_triples=False,
        entity_to_id=entity_to_id,
        relation_to_id=relation_to_id,
    )

    # Initialize model
    model_class = get_model_class(args.model)
    model = model_class(
        triples_factory=triples,
        embedding_dim=args.embedding_dim,
    )

    # Load trained weights
    model.load_state_dict(
        torch.load(
            args.model_path,
            map_location=torch.device(device),
        )
    )
    model.eval()
    

    num_samples = 50_000
    # --- Step 1: get valid heads from triples ---
    heads = torch.unique(triples.mapped_triples[:, 0])

    # --- Step 2: sample 50k heads from this pool ---
    num_head_samples = min(num_samples, heads.shape[0])

    perm = torch.randperm(heads.shape[0])[:num_head_samples]
    sampled_heads = heads[perm]

    # --- Step 3: assign random relations ---
    nr = triples.num_relations

    r_rand = torch.randint(high=nr, size=(num_head_samples,))

    hr_tensor = torch.stack([sampled_heads, r_rand], dim=1)

    # Remove accidental duplicates (optional but safer)
    hr_tensor = torch.unique(hr_tensor, dim=0)

        
    type_rel_label = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

    if type_rel_label not in relation_to_id:
        raise ValueError(f"Relation '{type_rel_label}' not found in mapping")

    type_r_id = relation_to_id[type_rel_label]

    e_sample = torch.unique(sampled_heads)
    print(e_sample.shape[0])

    type_pairs = torch.stack(
        [e_sample, torch.full((e_sample.shape[0],), type_r_id)],
        dim=1
    )

    # Merge and ensure uniqueness again
    hr_tensor = torch.unique(torch.cat([hr_tensor, type_pairs], dim=0), dim=0)

    best_triples_heap = []

    # Generate predictions for each head-relation pair
    for i in tqdm(range(hr_tensor.shape[0]), desc="Collecting global top triples"):
        h_id = int(hr_tensor[i, 0].item())
        r_id = int(hr_tensor[i, 1].item())

        pred = predict_target(
            model=model,
            head=h_id,
            relation=r_id,
            tail=None,
            triples_factory=triples,
        ).filter_triples(triples.mapped_triples)

        df = pred.df
        
        if args.top_k_per_hr is not None:
            df = df.nlargest(args.top_k_per_hr, columns="score")

        for row in df.itertuples(index=False):
            t_id = int(row.tail_id)
            score = float(row.score)

            maybe_add_topk(
                best_triples_heap,
                (score, h_id, r_id, t_id),
                max_size=args.global_top_k,
            )

        del pred, df
        if i % 100 == 0:
            gc.collect()
        

    # Sort descending by score for final output
    best_triples_sorted = sorted(best_triples_heap, key=lambda x: x[0], reverse=True)

    # Write predictions to output file
    with open(output_path, "w", encoding="utf-8") as out_f:
        for score, h_id, r_id, t_id in best_triples_sorted:
            h_label = id_to_entity[h_id]
            r_label = id_to_relation[r_id]
            t_label = id_to_entity[t_id]

            out_f.write(
                f"<{URIRef(h_label)}> "
                f"<{URIRef(r_label)}> "
                f"<{URIRef(t_label)}> .\n"
            )

    print(f"Wrote {len(best_triples_sorted)} triples to {output_path}")