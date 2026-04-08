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


class SchemaDecomposer:
    """Decompose an ontology graph into RBox and TBox-related components.

    This class separates an ontology into three logical parts:

    - RBox: object and datatype property definitions
    - Taxonomy: subclass relations and their supporting descriptions
    - Schema: non-taxonomic class axioms and their supporting descriptions

    The decomposition is performed over an RDFLib graph and preserves the
    recursive description of blank nodes and referenced entities where needed.
    """

    def __init__(self, input_graph: Graph):
        """Initialize the decomposer with the ontology graph to process.

        Args:
            input_graph (Graph): RDFLib graph representing the ontology to be decomposed.
        """
        self.onto_graph = input_graph

    def decompose(self, verbose: bool) -> Tuple[Graph, Graph, Graph]:
        """Decompose the ontology into RBox, taxonomy, and schema graphs.

        Args:
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Tuple[Graph, Graph, Graph]: A tuple containing:
                - the RBox graph,
                - the taxonomy graph,
                - the non-taxonomic schema graph.
        """
        return (
            self._rbox_decompose(verbose),
            self._taxonomy_decompose(verbose),
            self._schema_decompose(verbose),
        )

    def _rbox_decompose(self, verbose: bool) -> Graph:
        """Extract the RBox component from the ontology graph.

        The RBox includes descriptions of object properties and datatype
        properties, along with any recursively required supporting structure.

        Args:
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Graph: RDFLib graph containing only the extracted RBox component.
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
        """Extract the class taxonomy component from the ontology graph.

        The taxonomy graph contains ``rdfs:subClassOf`` axioms for named
        classes, together with any recursively required descriptions for
        blank-node superclass expressions.

        Args:
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Graph: RDFLib graph containing only taxonomy-related axioms.
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
        """Extract non-taxonomic class schema axioms from the ontology graph.

        This includes class-related axioms other than ``rdfs:subClassOf``,
        together with type declarations and recursively required descriptions
        for referenced blank nodes.

        Args:
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Graph: RDFLib graph containing non-taxonomic class schema axioms.
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
                            if verbose:
                                print(f"Found BNODE in Triple {s, p, o}")
                            schema_graph += self._extract_description(o, verbose)

        return schema_graph

    def _extract_description(self, elem: URIRef, verbose: bool) -> Graph:
        """Recursively extract the local description of a graph element.

        Starting from the given element, this method traverses outgoing triples
        and builds a closure over relevant blank nodes. For referenced classes
        and properties, only their type declarations are added unless they are
        themselves recursively expanded as blank nodes.

        Built-in RDF/OWL entities are not expanded.

        Args:
            elem (URIRef): Starting node whose description should be extracted.
            verbose (bool): Whether to print progress and traversal logs.

        Returns:
            Graph: RDFLib graph containing the recursively extracted description
            of the input element.
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