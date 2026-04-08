#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Set, Tuple

from rdflib import OWL, RDF, RDFS, BNode, Graph, URIRef

import jdex.utils.conventions.paths as pc
from jdex.utils.conventions.builtins import BUILTIN_URIS


def verbose_print(msg: str, verbose: bool):
    """Print a message only when verbose mode is enabled.

    Args:
        msg (str): Message to print.
        verbose (bool): If True, the message is printed; otherwise it is ignored.
    """
    if verbose:
        print(msg)


class SignatureModularizer:
    """Extract a module (subgraph) from an OWL ontology based on a signature.

    This class implements a simple signature-based modularization strategy.
    Starting from an initial set of URIs (the seed/signature), it iteratively
    explores the ontology graph and extracts all triples that are relevant
    to those entities, including related classes, properties, and blank nodes.

    The result is a reduced RDF graph that preserves the local context of
    the given signature.
    """

    def __init__(self, schema: Graph, seed: Set[URIRef]):
        """Initialize the modularizer.

        Args:
            schema (Graph): The RDFLib graph representing the ontology to be modularized.
            seed (Set[URIRef]): Initial set of URIs defining the signature (starting points
                for the module extraction).
        """
        self.schema = schema
        self.seed = seed

    def modularize(self, verbose: bool) -> Graph:
        """Extract a subgraph (module) from the ontology based on the signature.

        The algorithm performs a graph traversal starting from the seed URIs.
        For each processed element, it:
            - Adds all outgoing triples to the extracted graph.
            - Recursively explores related nodes if they are:
                - Blank nodes (BNodes),
                - OWL classes,
                - Object properties,
                - Datatype properties.

        Built-in OWL/RDF URIs are excluded from further expansion.

        Args:
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Graph: A new RDFLib graph containing the extracted module.
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