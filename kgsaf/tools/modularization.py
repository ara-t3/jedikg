#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Set, Tuple

from rdflib import OWL, RDF, RDFS, BNode, Graph, URIRef
from kgsaf.tools.utils.conventions.builtins import BUILTIN_URIS

import kgsaf.tools.utils.conventions.paths as pc
from kgsaf.tools.utils.utility import verbose_print


class SignatureModularizer:
    """Exctract a Module from an OWL Ontology given a signature (Set of target URIs)"""

    def __init__(self, schema: Graph, seed: Set[URIRef]):
        """Initialize modularizer with graph to be modularized and signature

        Args:
            schema (Graph): Graph to be modularized
            seed (Set[URIRef]): Set of URIs to use as signature
        """
        self.schema = schema
        self.seed = seed

    def modularize(self, verbose: bool) -> Graph:
        """Modularize the graph and output a new RDFLib graph

        Args:
            verbose (bool): Log printing.

        Returns:
            Graph: Modularized sub graph
        """

        extracted_graph = Graph()
        elem_to_process = set(self.seed)
        processed = set()

        while elem_to_process:

            e = elem_to_process.pop()
            processed.add(e)

            verbose_print(f"Processing {e}", verbose)

            for s, p, o in self.schema.triples((e, None, None)):
                extracted_graph.add((s, p, o))

                if (o not in BUILTIN_URIS) and (o not in processed):

                    if isinstance(o, BNode):
                        elem_to_process.add(o)

                    if (o, RDF.type, OWL.Class) in self.schema:
                        elem_to_process.add(o)

                    if (o, RDF.type, OWL.ObjectProperty) in self.schema:
                        elem_to_process.add(o)

                    if (o, RDF.type, OWL.DatatypeProperty) in self.schema:
                        elem_to_process.add(o)

        return extracted_graph
