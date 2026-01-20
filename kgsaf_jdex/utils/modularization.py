#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Set, Tuple

from rdflib import OWL, RDF, RDFS, BNode, Graph, URIRef
from kgsaf_jdex.utils.conventions.builtins import BUILTIN_URIS

import kgsaf_jdex.utils.conventions.paths as pc
from kgsaf_jdex.utils.utility import verbose_print


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


class SchemaDecomposer:
    """Decompose a given Ontology into TBox and RBox components."""

    def __init__(self, input_graph: Graph):
        """Initialize Decomposer with input Graph

        Args:
            input_graph (Graph): Graph to be decomposed.
        """
        self.onto_graph = input_graph

    def decompose(self, verbose: bool) -> Tuple[Graph, Graph, Graph]:
        """Decompose a Graph into RBox, Taxonomy and Classes

        Args:
            verbose (bool): Log printing.

        Returns:
            Tuple[Graph, Graph, Graph]: RBox graph, Taxonomy Graph and Class definitions Graph
        """
        return (
            self._rbox_decompose(verbose),
            self._taxonomy_decompose(verbose),
            self._schema_decompose(verbose),
        )

    def _rbox_decompose(self, verbose: bool) -> Graph:
        """Extract RBox information from target Graph

        Args:
            verbose (bool): Log printing.

        Returns:
            Graph: RBox only graph.
        """
        rbox_graph = Graph()
        for prop in (
            set(self.onto_graph.subjects(RDF.type, OWL.ObjectProperty)) - BUILTIN_URIS
        ):
            rbox_graph += self._extract_description(prop, verbose)

        for prop in (
            set(self.onto_graph.subjects(RDF.type, OWL.DatatypeProperty)) - BUILTIN_URIS
        ):
            rbox_graph += self._extract_description(prop, verbose)
        return rbox_graph

    def _taxonomy_decompose(self, verbose: bool) -> Graph:
        """Extract Taxonomy (TBox) information from target Graph

        Args:
            verbose (bool): Log printing.

        Returns:
            Graph: Taxonomy only graph.
        """
        taxonomy_graph = Graph()

        for c in set(self.onto_graph.subjects(RDF.type, OWL.Class)) - BUILTIN_URIS:
            for s, p, o in self.onto_graph.triples((c, None, None)):
                if p == RDFS.subClassOf:
                    taxonomy_graph.add((s, p, o))
                    if isinstance(o, BNode):
                        taxonomy_graph += self._extract_description(o, verbose)

        return taxonomy_graph

    def _schema_decompose(self, verbose: bool) -> Graph:
        """Extract Non Taxonomic Axioms (TBox) from target Graph

        Args:
            verbose (bool): Log printing.

        Returns:
            Graph: Non Taxonomix Axioms only graph.
        """
        schema_graph = Graph()

        for c in set(self.onto_graph.subjects(RDF.type, OWL.Class)) - BUILTIN_URIS:
            if not isinstance(c, BNode):
                for s, p, o in self.onto_graph.triples((c, None, None)):
                    if p != RDFS.subClassOf:

                        schema_graph.add((s, p, o))

                        for elem in self.onto_graph.objects(o, RDF.type):
                            schema_graph.add((o, RDF.type, elem))

                        if isinstance(o, BNode):
                            print(f"Found BNODE in Triple {s, p, o}")
                            schema_graph += self._extract_description(o, verbose)

        return schema_graph

    def _extract_description(self, elem: URIRef, verbose: bool) -> Graph:
        """Recursively extract closure information of a node from a Graph. If a element is found but should be inserted in another file, only its definition is added.

        Args:
            elem (URIRef): Starting elem from which gather recursive description
            verbose (bool): Log pringing.

        Returns:
            Graph: Closure of Graph on input node
        """

        extracted_graph = Graph()
        elem_to_process = {elem}
        processed = set()

        while elem_to_process:

            e = elem_to_process.pop()
            processed.add(e)

            verbose_print(f"Processing {e}", verbose)

            for s, p, o in self.onto_graph.triples((e, None, None)):
                extracted_graph.add((s, p, o))

                if (o not in BUILTIN_URIS) and (o not in processed):
                    if isinstance(o, BNode):
                        elem_to_process.add(o)

                    if (o, RDF.type, OWL.Class) in self.onto_graph:
                        extracted_graph.add((o, RDF.type, OWL.Class))

                    if (o, RDF.type, OWL.ObjectProperty) in self.onto_graph:
                        extracted_graph.add((o, RDF.type, OWL.ObjectProperty))

                    if (o, RDF.type, OWL.DatatypeProperty) in self.onto_graph:
                        extracted_graph.add((o, RDF.type, OWL.DatatypeProperty))

        return extracted_graph
