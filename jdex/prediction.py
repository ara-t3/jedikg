#!/usr/bin/env python3

from __future__ import annotations

import gc
import heapq
import json
from pathlib import Path

import torch
from tqdm import tqdm
from pykeen.triples import TriplesFactory
from pykeen.predict import predict_target
from pykeen.models import RotatE
from rdflib import URIRef

def maybe_add_topk(heap, item, max_size: int) -> None:
    if len(heap) < max_size:
        heapq.heappush(heap, item)
    else:
        if item[0] > heap[0][0]:
            heapq.heapreplace(heap, item)


if __name__ == "__main__":
    cwd = Path("./WIP/inc_WIP")

    top_k_per_hr = 50
    global_top_k = 10000
    output_path = cwd / f"global_top_{global_top_k}.nt"

    with open(cwd / "mappings/entity_to_id.json", "r") as f:
        entity_to_id = json.load(f)

    with open(cwd / "mappings/relation_to_id.json", "r") as f:
        relation_to_id = json.load(f)

    id_to_entity = {v: k for k, v in entity_to_id.items()}
    id_to_relation = {v: k for k, v in relation_to_id.items()}

    triples = TriplesFactory.from_path(
        cwd / "triples.tsv",
        create_inverse_triples=False,
        entity_to_id=entity_to_id,
        relation_to_id=relation_to_id,
    )

    model = RotatE(
        triples_factory=triples,
        embedding_dim=128,
    )

    model.load_state_dict(
        torch.load(
            cwd / "model.pt",
            map_location=torch.device("cuda"),
        )
    )
    model.eval()

    hr_tensor = torch.unique(triples.mapped_triples[:, :2], dim=0)[:, :]

    best_triples_heap = []

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
        
        if top_k_per_hr is not None:
            df = df.nlargest(top_k_per_hr, columns="score")

        for row in df.itertuples(index=False):
            t_id = int(row.tail_id)
            score = float(row.score)

            maybe_add_topk(
                best_triples_heap,
                (score, h_id, r_id, t_id),
                max_size=global_top_k,
            )

        del pred, df
        if i % 100 == 0:
            gc.collect()
        

    # sort descending by score for final output
    best_triples_sorted = sorted(best_triples_heap, key=lambda x: x[0], reverse=True)

    with open(output_path, "w", encoding="utf-8") as out_f:
        for score, h_id, r_id, t_id in best_triples_sorted:
            h_label = id_to_entity[h_id]
            r_label = id_to_relation[r_id]
            t_label = id_to_entity[t_id]

            out_f.write(
                f"<{URIRef(h_label)}> "
                f"<{URIRef(r_label)}> "
                f"<{URIRef(t_label)}> "
                f'"{score}" .\n'
            )

    print(f"Wrote {len(best_triples_sorted)} triples to {output_path}")