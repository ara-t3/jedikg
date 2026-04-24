#!/usr/bin/env python3
from __future__ import annotations

import torch
import argparse
from pathlib import Path
from jdex.owl.reasoning import Reasoner
from jdex.cli import CLI
from rdflib import Graph
import gc
from tqdm import tqdm
import math


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

    ui.logo("JDEX Prediction Consistency Check")
    ui.rule("Start Prediction Consistency Check")

    args = parse_args()

    reasoner = Reasoner(
        reasoners_path=Path("./reasoners/unpack").absolute(),
        java8_path=".",
        java11_path="/opt/homebrew/opt/openjdk@11/"
    )

    kg = Graph()
    kg.parse(Path(args.dataset_dir) / "knowledge_graph.owl")


    kg.serialize(Path("work_kg.nt"), format="ntriples")
    base_bytes = Path("work_kg.nt").read_bytes()

    with open(Path(args.predictions_dir) / "ARCO_10_ROFF_TransE_E200_D128.nt", "rb") as f:
        prediction_lines = [
            line for line in f
            if line.strip() and not line.lstrip().startswith(b"#")
        ]

    ui.subrule("Consistency Check")

    LAST_CONSISTENT = 2677
    LAST_INCONSISTENT = 2687
    CHECK_CONSISTENT = int(len(prediction_lines) / 2)
    CHECK_CONSISTENT = 2682

    i = 0
    while True:
        i += 1
        print(f"===== Step {i} =====")
        print(f"LAST CONSISTENT AT {LAST_CONSISTENT}")
        print(f"LAST INCONSISTENT AT {LAST_INCONSISTENT}")
        print(f"Checking Consistency at {CHECK_CONSISTENT}")
        batch = prediction_lines[: CHECK_CONSISTENT]
        with open(Path("merged.owl"), "wb") as out:
            out.write(base_bytes)
            if not base_bytes.endswith(b"\n"):
                out.write(b"\n")

            for line in batch:
                out.write(line)

        ans = reasoner.consistency(Path("merged.owl"), verbose=0)
        print(ans)

        t = math.ceil((CHECK_CONSISTENT - LAST_CONSISTENT) / 2)
        print(t)

        if ans:
            LAST_CONSISTENT = CHECK_CONSISTENT
            CHECK_CONSISTENT = CHECK_CONSISTENT + t
        else:
            LAST_INCONSISTENT = CHECK_CONSISTENT           
            CHECK_CONSISTENT = CHECK_CONSISTENT - t


        if (LAST_INCONSISTENT - LAST_CONSISTENT) == 1:
            print(f"Inconsistent after {LAST_CONSISTENT}")
            break
            
    



if __name__ == "__main__":
    main()
