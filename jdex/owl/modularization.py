#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from typing import Set, Tuple

from rdflib import OWL, RDF, RDFS, BNode, Graph, URIRef

import jdex.utils.conventions.paths as pc
from jdex.utils.conventions.builtins import BUILTIN_URIS

from typing import Set, Optional

from rdflib import OWL, RDF, RDFS, BNode, Graph, URIRef
from rdflib.collection import Collection

from jdex.utils.conventions.builtins import BUILTIN_URIS



from abc import ABC, abstractmethod
from typing import Optional, Set

from rdflib import BNode, Graph, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS



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
    


class BaseDLProfileFilter(ABC):
    """Abstract base class for Description Logic profile filtering.

    This class defines the common infrastructure for syntactically filtering an
    OWL ontology represented as an RDFLib graph into a restricted Description
    Logic (DL) profile.

    Subclasses implement the profile-specific admissibility test for OWL class
    expressions, while this base class provides:

    - ontology graph initialization,
    - namespace preservation,
    - common axiom traversal,
    - recursive copying of accepted class expressions,
    - RDF list copying,
    - common declaration preservation.

    The filtering is purely syntactic: unsupported axioms are discarded rather
    than rewritten, normalized, or approximated.

    Typical subclass responsibilities:
        - decide whether a class expression is valid in the target profile,
        - decide whether profile-specific axioms (e.g. disjointness) are kept,
        - optionally retain additional role/property axioms.

    Attributes:
        onto_graph (Graph): The source ontology graph.
    """

    CARDINALITY_PREDICATES = {
        OWL.minCardinality,
        OWL.maxCardinality,
        OWL.cardinality,
        OWL.minQualifiedCardinality,
        OWL.maxQualifiedCardinality,
        OWL.qualifiedCardinality,
    }

    DISALLOWED_COMMON = {
        OWL.hasValue,
        OWL.hasSelf,
        OWL.oneOf,
    }

    def __init__(self, input_graph: Graph):
        """Initialize the filter with an ontology graph.

        Args:
            input_graph: RDFLib graph containing the ontology to be filtered.

        Notes:
            The input graph is never modified. Filtering always produces a new
            RDFLib graph.
        """
        self.onto_graph = input_graph

    def filter_graph(self, verbose: bool = False) -> Graph:
        """Filter the ontology graph according to the concrete DL profile.

        This method scans the ontology graph and builds a new graph containing
        only the axioms and structures accepted by the current profile.

        The following common elements are handled here:
            - namespace bindings,
            - ontology declaration,
            - named class declarations,
            - object property declarations,
            - `rdfs:subClassOf` axioms,
            - `owl:equivalentClass` axioms.

        Additional profile-specific axioms may be added by subclasses through
        `_copy_profile_specific_axioms()`.

        Args:
            verbose: Whether to emit debug/progress messages through
                `verbose_print`.

        Returns:
            A new RDFLib graph containing only axioms compatible with the
            selected Description Logic fragment.
        """
        out = Graph()

        self._copy_namespaces(out)
        self._copy_ontology_declaration(out)
        self._copy_named_class_declarations(out)
        self._copy_object_property_declarations(out)
        self._copy_common_tbox_axioms(out, verbose)
        self._copy_profile_specific_axioms(out, verbose)

        return out

    def _copy_namespaces(self, out: Graph) -> None:
        """Copy namespace bindings from the input graph.

        Args:
            out: Output graph receiving the namespace bindings.
        """
        for prefix, ns in self.onto_graph.namespaces():
            out.bind(prefix, ns)

    def _copy_ontology_declaration(self, out: Graph) -> None:
        """Copy ontology declaration triples, if present.

        This preserves triples of the form:
            `?ontology rdf:type owl:Ontology`

        Args:
            out: Output graph receiving ontology declaration triples.
        """
        for triple in self.onto_graph.triples((None, RDF.type, OWL.Ontology)):
            out.add(triple)

    def _copy_named_class_declarations(self, out: Graph) -> None:
        """Copy named OWL class declarations.

        Only URI-based class declarations are preserved. Built-in OWL/RDF
        vocabulary URIs are excluded through `BUILTIN_URIS`.

        Args:
            out: Output graph receiving class declarations.
        """
        for c in set(self.onto_graph.subjects(RDF.type, OWL.Class)) - BUILTIN_URIS:
            if isinstance(c, URIRef):
                out.add((c, RDF.type, OWL.Class))

    def _copy_object_property_declarations(self, out: Graph) -> None:
        """Copy object property declarations.

        Only simple declarations are copied here:
            `?p rdf:type owl:ObjectProperty`

        More expressive role/property axioms are left to subclasses if needed.

        Args:
            out: Output graph receiving object property declarations.
        """
        for p in set(self.onto_graph.subjects(RDF.type, OWL.ObjectProperty)) - BUILTIN_URIS:
            out.add((p, RDF.type, OWL.ObjectProperty))

    def _copy_common_tbox_axioms(self, out: Graph, verbose: bool) -> None:
        """Copy common TBox axioms accepted by the profile.

        This method preserves:
            - subclass axioms (`rdfs:subClassOf`)
            - equivalence axioms (`owl:equivalentClass`)

        An axiom is copied only if both participating class expressions are
        accepted by `_is_allowed_class_expr()`.

        Args:
            out: Output graph receiving accepted axioms.
            verbose: Whether to emit debug/progress messages.
        """
        for s, p, o in self.onto_graph.triples((None, RDFS.subClassOf, None)):
            if self._is_allowed_class_expr(s) and self._is_allowed_class_expr(o):
                verbose_print(f"KEEP subclass: {s} ⊑ {o}", verbose)
                out.add((s, p, o))
                self._copy_class_expr(s, out)
                self._copy_class_expr(o, out)

        for s, p, o in self.onto_graph.triples((None, OWL.equivalentClass, None)):
            if self._is_allowed_class_expr(s) and self._is_allowed_class_expr(o):
                verbose_print(f"KEEP equiv: {s} ≡ {o}", verbose)
                out.add((s, p, o))
                self._copy_class_expr(s, out)
                self._copy_class_expr(o, out)

    @abstractmethod
    def _copy_profile_specific_axioms(self, out: Graph, verbose: bool) -> None:
        """Copy axioms specific to the concrete DL profile.

        Subclasses implement this method to preserve profile-dependent axioms,
        such as:
            - disjointness axioms in ALC,
            - simple role inclusion axioms in EL.

        Args:
            out: Output graph receiving accepted axioms.
            verbose: Whether to emit debug/progress messages.
        """
        raise NotImplementedError

    @abstractmethod
    def _is_allowed_class_expr(self, node, visited: Optional[Set] = None) -> bool:
        """Check whether a node encodes an allowed class expression.

        Subclasses implement the admissibility test according to the target
        Description Logic fragment.

        Args:
            node: RDF node representing a named class or anonymous class
                expression.
            visited: Set of already visited nodes used to avoid infinite
                recursion on cyclic graph structures.

        Returns:
            True if the node encodes a class expression allowed in the target
            profile, False otherwise.
        """
        raise NotImplementedError

    def _is_named_or_builtin_class(self, node, allow_nothing: bool) -> bool:
        """Check whether a node is an allowed named or built-in class.

        Args:
            node: RDF node to inspect.
            allow_nothing: Whether `owl:Nothing` is allowed in the current
                profile.

        Returns:
            True if the node is:
                - a named OWL class URI,
                - `owl:Thing`,
                - or `owl:Nothing` when allowed.
        """
        if not isinstance(node, URIRef):
            return False

        if node == OWL.Thing:
            return True

        if node == OWL.Nothing:
            return allow_nothing

        return (node, RDF.type, OWL.Class) in self.onto_graph

    def _is_allowed_list(self, list_head: BNode, visited: Set) -> bool:
        """Check whether every element of an RDF collection is allowed.

        This helper is used for OWL constructs encoded as RDF lists, such as
        `owl:intersectionOf` and `owl:unionOf`.

        Args:
            list_head: Head node of the RDF list.
            visited: Set of already visited nodes to avoid recursive loops.

        Returns:
            True if the list is well-formed, non-empty, and all members are
            allowed class expressions in the current profile.
        """
        try:
            members = list(Collection(self.onto_graph, list_head))
        except Exception:
            return False

        if not members:
            return False

        return all(self._is_allowed_class_expr(m, visited.copy()) for m in members)

    def _copy_class_expr(
        self,
        node,
        out: Graph,
        visited: Optional[Set] = None,
    ) -> None:
        """Copy the RDF structure defining an accepted class expression.

        This method recursively copies the triples needed to preserve the meaning
        of a class expression already known to be allowed. It handles:
            - named class typing,
            - anonymous expression blank nodes,
            - restriction fillers,
            - boolean constructor operands,
            - referenced object property declarations.

        Args:
            node: RDF node representing the class expression to copy.
            out: Output graph receiving the copied triples.
            visited: Set of already visited nodes used to avoid duplicate work
                and infinite recursion.

        Notes:
            This method assumes that `node` has already passed the profile
            admissibility check.
        """
        if visited is None:
            visited = set()

        if node in visited:
            return
        visited.add(node)

        if (node, RDF.type, OWL.Class) in self.onto_graph:
            out.add((node, RDF.type, OWL.Class))

        if isinstance(node, URIRef):
            return

        for s, p, o in self.onto_graph.triples((node, None, None)):
            out.add((s, p, o))

            if p == OWL.onProperty and (o, RDF.type, OWL.ObjectProperty) in self.onto_graph:
                out.add((o, RDF.type, OWL.ObjectProperty))

            if p in {OWL.someValuesFrom, OWL.allValuesFrom, OWL.complementOf}:
                self._copy_class_expr(o, out, visited)

            if p in {OWL.intersectionOf, OWL.unionOf}:
                self._copy_rdf_list(o, out, visited)

    def _copy_rdf_list(self, head, out: Graph, visited: Set) -> None:
        """Copy an RDF list and recursively copy its members.

        This preserves both the raw RDF collection structure and the class
        expressions referenced by its elements.

        Args:
            head: Head of the RDF list.
            out: Output graph receiving the copied triples.
            visited: Set of already visited expression nodes.
        """
        try:
            members = list(Collection(self.onto_graph, head))
        except Exception:
            return

        current = head
        seen = set()

        while current and current != RDF.nil and current not in seen:
            seen.add(current)
            for triple in self.onto_graph.triples((current, None, None)):
                out.add(triple)
            current = self.onto_graph.value(current, RDF.rest)

        for m in members:
            self._copy_class_expr(m, out, visited)


class ELProfileFilter(BaseDLProfileFilter):
    """Filter an ontology graph to the Description Logic profile EL.

    This class retains only OWL axioms whose class expressions belong to the
    lightweight EL fragment.

    Supported EL constructs:
        - named classes,
        - `owl:Thing`,
        - conjunction (`owl:intersectionOf`),
        - existential restrictions (`owl:someValuesFrom`) on object properties.

    Rejected constructs include:
        - disjunction,
        - negation,
        - universal restrictions,
        - cardinality restrictions,
        - nominals,
        - value/self restrictions.

    Additionally, this implementation preserves simple object property inclusion
    axioms of the form:
        `R rdfs:subPropertyOf S`
    when both sides are declared object properties.
    """

    def _copy_profile_specific_axioms(self, out: Graph, verbose: bool) -> None:
        """Copy EL-specific axioms.

        In this implementation, EL preserves simple role inclusion axioms:
            `R rdfs:subPropertyOf S`
        provided that both `R` and `S` are declared as object properties.

        Args:
            out: Output graph receiving accepted axioms.
            verbose: Whether to emit debug/progress messages.
        """
        for s, p, o in self.onto_graph.triples((None, RDFS.subPropertyOf, None)):
            if (
                (s, RDF.type, OWL.ObjectProperty) in self.onto_graph
                and (o, RDF.type, OWL.ObjectProperty) in self.onto_graph
            ):
                verbose_print(f"KEEP subProperty: {s} ⊑ {o}", verbose)
                out.add((s, p, o))
                out.add((s, RDF.type, OWL.ObjectProperty))
                out.add((o, RDF.type, OWL.ObjectProperty))

    def _is_allowed_class_expr(self, node, visited: Optional[Set] = None) -> bool:
        """Check whether a node encodes an EL-compatible class expression.

        EL accepts:
            - named classes,
            - `owl:Thing`,
            - conjunctions,
            - existential restrictions over object properties.

        EL rejects:
            - `owl:Nothing`,
            - disjunctions,
            - complements,
            - universal restrictions,
            - cardinalities,
            - nominals and value/self restrictions.

        Args:
            node: RDF node representing the class expression.
            visited: Set of already visited nodes to avoid recursive loops.

        Returns:
            True if the node encodes an EL-compatible class expression,
            False otherwise.
        """
        if visited is None:
            visited = set()

        if node in visited:
            return True
        visited.add(node)

        if self._is_named_or_builtin_class(node, allow_nothing=False):
            return True

        if not isinstance(node, BNode):
            return False

        for pred in self.DISALLOWED_COMMON | self.CARDINALITY_PREDICATES:
            if (node, pred, None) in self.onto_graph:
                return False

        if (node, OWL.intersectionOf, None) in self.onto_graph:
            lst = self.onto_graph.value(node, OWL.intersectionOf)
            return self._is_allowed_list(lst, visited)

        if (node, OWL.unionOf, None) in self.onto_graph:
            return False

        if (node, OWL.complementOf, None) in self.onto_graph:
            return False

        if (node, RDF.type, OWL.Restriction) in self.onto_graph:
            on_prop = self.onto_graph.value(node, OWL.onProperty)
            if on_prop is None:
                return False

            if (on_prop, RDF.type, OWL.ObjectProperty) not in self.onto_graph:
                return False

            if (node, OWL.someValuesFrom, None) in self.onto_graph:
                filler = self.onto_graph.value(node, OWL.someValuesFrom)
                return self._is_allowed_class_expr(filler, visited)

            return False

        return False


class ALCProfileFilter(BaseDLProfileFilter):
    """Filter an ontology graph to the Description Logic profile ALC.

    This class retains OWL axioms whose class expressions belong to the ALC
    fragment, which is strictly more expressive than EL.

    Supported ALC constructs:
        - named classes,
        - `owl:Thing`,
        - `owl:Nothing`,
        - conjunction (`owl:intersectionOf`),
        - disjunction (`owl:unionOf`),
        - negation (`owl:complementOf`),
        - existential restrictions (`owl:someValuesFrom`),
        - universal restrictions (`owl:allValuesFrom`),
        - disjointness axioms (`owl:disjointWith`).

    Rejected constructs include:
        - cardinality restrictions,
        - nominals,
        - value/self restrictions,
        - advanced role axioms outside plain ALC.
    """

    DISALLOWED_ALC_ROLE_AXIOMS = {
        OWL.inverseOf,
        OWL.TransitiveProperty,
        OWL.FunctionalProperty,
        OWL.InverseFunctionalProperty,
        OWL.SymmetricProperty,
        OWL.AsymmetricProperty,
        OWL.ReflexiveProperty,
        OWL.IrreflexiveProperty,
    }

    def _copy_profile_specific_axioms(self, out: Graph, verbose: bool) -> None:
        """Copy ALC-specific axioms.

        In this implementation, ALC preserves class disjointness axioms:
            `C owl:disjointWith D`
        when both participating class expressions are ALC-compatible.

        Args:
            out: Output graph receiving accepted axioms.
            verbose: Whether to emit debug/progress messages.
        """
        for s, p, o in self.onto_graph.triples((None, OWL.disjointWith, None)):
            if self._is_allowed_class_expr(s) and self._is_allowed_class_expr(o):
                verbose_print(f"KEEP disjoint: {s} ⊓ {o} ⊑ ⊥", verbose)
                out.add((s, p, o))
                self._copy_class_expr(s, out)
                self._copy_class_expr(o, out)

    def _is_allowed_class_expr(self, node, visited: Optional[Set] = None) -> bool:
        """Check whether a node encodes an ALC-compatible class expression.

        ALC accepts:
            - named classes,
            - `owl:Thing`,
            - `owl:Nothing`,
            - conjunctions,
            - disjunctions,
            - complements,
            - existential restrictions over object properties,
            - universal restrictions over object properties.

        ALC rejects:
            - cardinality restrictions,
            - nominals,
            - value/self restrictions.

        Args:
            node: RDF node representing the class expression.
            visited: Set of already visited nodes to avoid recursive loops.

        Returns:
            True if the node encodes an ALC-compatible class expression,
            False otherwise.
        """
        if visited is None:
            visited = set()

        if node in visited:
            return True
        visited.add(node)

        if self._is_named_or_builtin_class(node, allow_nothing=True):
            return True

        if not isinstance(node, BNode):
            return False

        for pred in self.DISALLOWED_COMMON | self.CARDINALITY_PREDICATES:
            if (node, pred, None) in self.onto_graph:
                return False

        if (node, OWL.intersectionOf, None) in self.onto_graph:
            lst = self.onto_graph.value(node, OWL.intersectionOf)
            return self._is_allowed_list(lst, visited)

        if (node, OWL.unionOf, None) in self.onto_graph:
            lst = self.onto_graph.value(node, OWL.unionOf)
            return self._is_allowed_list(lst, visited)

        if (node, OWL.complementOf, None) in self.onto_graph:
            filler = self.onto_graph.value(node, OWL.complementOf)
            return self._is_allowed_class_expr(filler, visited)

        if (node, RDF.type, OWL.Restriction) in self.onto_graph:
            on_prop = self.onto_graph.value(node, OWL.onProperty)
            if on_prop is None:
                return False

            if (on_prop, RDF.type, OWL.ObjectProperty) not in self.onto_graph:
                return False

            if (node, OWL.someValuesFrom, None) in self.onto_graph:
                filler = self.onto_graph.value(node, OWL.someValuesFrom)
                return self._is_allowed_class_expr(filler, visited)

            if (node, OWL.allValuesFrom, None) in self.onto_graph:
                filler = self.onto_graph.value(node, OWL.allValuesFrom)
                return self._is_allowed_class_expr(filler, visited)

            return False

        return False
