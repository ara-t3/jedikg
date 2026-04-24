from jdex.cli import CLI
from pathlib import Path
import os
import stat
import shutil
from jdex.owl.reasoning import Reasoner
from jdex.utils.postprocessing import TSVConverter, IDMapper, OWLConverter
from jdex.cli import CLI
from rdflib import Graph
from jdex.utils.conventions import paths as pc
import json
from rdflib import URIRef
from rdflib.namespace import RDF, RDFS
from jdex.utils.conventions.builtins import BUILTIN_URIS
from jdex.owl.modularization import (
    SignatureModularizer,
    ELProfileFilter,
    ALCProfileFilter,
)
from jdex.owl.decomposition import SchemaDecomposer
from pykeen.triples import TriplesFactory
from pykeen.triples.splitting import CoverageSplitter
from jdex.utils.postprocessing import OWLConverter, TSVConverter, IDMapper
from pykeen.triples.leakage import unleak
from jdex.owl.reasoning import Reasoner, PresetAxioms
import jdex.utils.conventions.paths as pc
from jdex.utils.postprocessing import TSVConverter, IDMapper, OWLConverter
import numpy as np

if __name__ == "__main__":
    ui = CLI(verbose=1)
    cwd = Path.cwd() / "data/datasets/unpack"
    datasets = [e for e in cwd.iterdir() if e.is_dir() and "ROFF" in e.name]

    for d in datasets:
        ui.rule(f"Processing {d}")
        g = Graph()
        g.parse(d / pc.RDF_TRIPLES)

        ui.info(f"Original Triples: {len(g)}")

        with open(d / pc.CLASS_ASSERTIONS, "r") as casrt_json:
            data = json.load(casrt_json)

        for ind_uri in data:
            for class_uri in data[ind_uri]:
                g.add((URIRef(ind_uri), RDF.type, URIRef(class_uri)))

        triples = TriplesFactory.from_labeled_triples(np.array(g))
        del g
        del data

        ui.panel(
            "Dataset Statistics",
            [
                ("Triples", triples.num_triples),
                ("Entities", triples.num_entities),
                ("Relations", triples.num_relations)
            ]
        )


        train, valid, test = triples.split(
            ratios=[0.80, 0.10],
            random_state=42,
            method=CoverageSplitter(),
        )

        ui.panel(
            f"Splitting Overview",
            data=[
                ("Train Triples", train.num_triples),
                ("Validation Triples", valid.num_triples),
                ("Test Triples", test.num_triples),
            ],
        )

        train, valid, test = unleak(
            train,
            valid,
            test,
            n=None,
            minimum_frequency=0.97,
        )

        ui.panel(
            f"Leakage Filtered Splitting Overview",
            data=[
                ("Train Triples", train.num_triples),
                ("Validation Triples", valid.num_triples),
                ("Test Triples", test.num_triples),
            ],
        )

        targets = [
            (d / "abox/experiments_split/train.tsv", train.triples),
            (d / "abox/experiments_split/valid.tsv", valid.triples),
            (d / "abox/experiments_split/test.tsv", test.triples),
        ]

        (d / "abox/experiments_split").mkdir(parents=True, exist_ok=True)

        with open(d / "triples.tsv", "w") as full:
            for outfile, split in targets:
                with open(outfile, "w") as f:
                    for s, p, o in ui.progress(split, f"Writing {outfile.name}"):
                        out_str = f"{str(s)}\t{str(p)}\t{str(o)}\n"
                        f.write(out_str)
                        full.write(out_str)


        ui.rule("Done")
