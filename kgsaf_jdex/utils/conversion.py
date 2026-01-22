#!/usr/bin/env python3

import json
from pathlib import Path

from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace
from rdflib.namespace import split_uri
from rdflib.term import URIRef

import kgsaf_jdex.utils.conventions.ids as idc
import kgsaf_jdex.utils.conventions.paths as pc
from kgsaf_jdex.utils.utility import verbose_print
from kgsaf_jdex.utils.conventions.builtins import BUILTIN_URIS


def rdf_list_to_python_list(graph: Graph, head: URIRef, depth: int, verbose: bool = True) -> list:
    """Convert an RDF list (rdf:first/rest/nil chain) into a Python list.


    Args:
        graph (Graph): RDFLib Graph to be parsed
        head (URIRef): List starting node
        depth (int): Recursion depth
        verbose (bool): Log printing. Defaults to True.

    Returns:
        list: Python list from RDF list
    """
    items = []
    while head and head != RDF.nil:
        first = next(graph.objects(head, RDF.first), None)
        verbose_print(f"{"\t"*depth}List Element {first}", verbose)
        if first is not None:
            items.append(bnode_to_dict(graph, first, depth + 1))
        head = next(graph.objects(head, RDF.rest), None)
    return items


def bnode_to_dict(graph: Graph, node: URIRef, depth: int = 1, verbose: bool = True) -> dict:
    """Recursively convert an RDF node (especially blank nodes) into JSON.

    Args:
        graph (Graph): RDFLib Graph to be parsed
        node (URIRef): Starting node
        depth (int, optional): Recursion depth. Defaults to 1.
        verbose (bool): Log printing. Defaults to True.

    Returns:
        dict: Python dict from RDF description
    """

    if isinstance(node, URIRef):
        return str(node)
    if isinstance(node, Literal):
        return str(node)
    if not isinstance(node, BNode):
        return str(node)

    node_dict = {}

    verbose_print(f"{"\t"*depth}Found BNode {node} Starting Recursive Evaluation", verbose)

    for _, p, o in graph.triples((node, None, None)):
        pred = str(p)

        verbose_print(f"{"\t"*depth}Evaluating  - {p} {o}", verbose)

        if pred in {
            str(OWL.unionOf),
            str(OWL.intersectionOf),
            str(OWL.oneOf),
            str(OWL.AllDisjointClasses),
            str(OWL.AllDisjointProperties),
        }:
            verbose_print(
                f"{"\t"*(depth+1)}Found Collection {pred} Starting Recursive Evaluation",
                verbose
            )
            node_dict[pred] = rdf_list_to_python_list(graph, o, depth + 1, verbose)
        else:
            node_dict.setdefault(pred, []).append(bnode_to_dict(graph, o, depth + 1, verbose))

    return node_dict


class OWLConverter:
    """Converts a subset of OWL Ontology axioms to JSON Serialization"""

    def __init__(
        self,
        path: str,
    ):
        """Initialize the converter with a dataset base path

        Args:
            path (str): Dataset location path
        """
        self.p_data = dict()
        self.base_path = Path(path).resolve().absolute()

    def preprocess(
        self,
        taxonomy: bool = True,
        class_assertions: bool = True,
        obj_prop_domain_range: bool = True,
        obj_prop_hierarchy: bool = True,
        verbose: bool = True
    ):
        """Preprocess a subset of the dataset schema into Python data structure

        Args:
            taxonomy (bool, optional): Load and convert taxonomy axioms. Defaults to True.
            class_assertions (bool, optional): Load and convert class assertions axioms. Defaults to True.
            obj_prop_domain_range (bool, optional): Load and convert object propoerty domain and range. Defaults to True.
            obj_prop_hierarchy (bool, optional): Load and convert object property hierarchy. Defaults to True.
            verbose (bool): Log printing. Defaults to True.
        """

        print(f"Processing Dataset at {self.base_path}")

        if taxonomy:
            print("Processing Taxonomy")
            self.p_data["taxonomy"] = (
                self.preprocess_taxonomy(verbose),
                self.base_path / pc.TAXONOMY,
            )

        if class_assertions:
            print("Processing Class Assertions")
            self.p_data["class_assertions"] = (
                self.preprocess_class_assertions(verbose),
                self.base_path / pc.CLASS_ASSERTIONS,
            )

        if obj_prop_hierarchy:
            print("Processing Object Property Hierarchy")
            self.p_data["obj_prop_hierarchy"] = (
                self.preprocess_obj_prop_hierarchy(verbose),
                self.base_path / pc.OBJ_PROP_HIERARCHY,
            )

        if obj_prop_domain_range:
            print("Processing Object Property Domain and Range")
            self.p_data["obj_prop_domain_range"] = (
                self.preprocess_obj_prop_domain_range(verbose),
                self.base_path / pc.OBJ_PROP_DOMAIN_RANGE,
            )

    def serialize(self):
        """Serialize loaded and converted data into JSON format"""
        for values in self.p_data.values():
            obj = values[0]
            path = values[1]

            with open(path, "w") as f:
                json.dump(obj, f, indent=4)

    def preprocess_taxonomy(self, verbose: bool) -> dict:
        """Process taxonomy data, the out dictionary will be formatted as:

        ```
        uri_class : ['uri_sup_class_1',..., 'uri_sup_class_n']
        ```

        If complex classes are found (restrictions or lists). These will be kept and recusively added as a Python dictionary

        Args:
            verbose (bool): Log printing.

        Returns:
            dict: Dictionary with list of classes and theri super classes
        """

        onto = Graph()
        onto.parse(self.base_path / pc.RDF_TAXONOMY)
        classes = set(onto.subjects(RDF.type, OWL.Class))

        out_json = {}

        for c in classes:
            verbose_print(f"Processing main class {c}", verbose)
            sup_c = []
            for o in set(onto.objects(c, RDFS.subClassOf)) - BUILTIN_URIS:
                sup_c.append(bnode_to_dict(onto, o, verbose=verbose))
            if sup_c:
                out_json[c] = sup_c

        return out_json

    def preprocess_class_assertions(self, verbose: bool) -> dict:
        """Process class assertions data, the out dictionary will be formatted as:

        ```
        uri_individuals : ['uri_class_1',...,'uri_class_n']
        ```

        Args:
            verbose (bool): Log printing.

        Returns:
            dict: Dictionary with list of individuals and their types
        """

        onto = Graph()
        onto.parse(self.base_path / pc.RDF_CLASS_ASSERTIONS)
        individuals = set(onto.subjects(RDF.type, OWL.NamedIndividual))

        out_json = {}

        for ind in individuals:
            ind_cls = []
            for cls in set(onto.objects(ind, RDF.type)) - BUILTIN_URIS:
                if cls != OWL.NamedIndividual:
                    ind_cls.append(cls)
            if ind_cls:
                out_json[ind] = ind_cls

        return out_json

    def preprocess_obj_prop_domain_range(self, verbose: bool) -> dict:
        """Process object properties domain and range, the out dictionary will be formatted as:

        ```
        uri_obj_prop : {
            domain : ['uri_c_1', ..., 'uri_c_n']
            range :  ['uri_c_1', ..., 'uri_c_m']
        }
        ```

        If complex classes are found (restrictions or lists). These will be kept and recusively added as a Python dictionary

        Args:
            verbose (bool): Log printing.

        Returns:
            dict: Dictionary with list of object properties and domain and range classes
        """

        onto = Graph()
        onto.parse(self.base_path / pc.RDF_OBJ_PROP)

        obj_props = set(onto.subjects(RDF.type, OWL.ObjectProperty))

        out_json = {}

        for prop in obj_props:
            prop_data = {}

            # Get domains
            domains = list(onto.objects(prop, RDFS.domain))
            prop_data["domain"] = (
                [bnode_to_dict(onto, d, verbose=verbose) for d in domains] if domains else [OWL.Thing]
            )

            # Get ranges
            ranges = list(onto.objects(prop, RDFS.range))
            prop_data["range"] = (
                [bnode_to_dict(onto, r, verbose=verbose) for r in ranges] if ranges else [OWL.Thing]
            )

            out_json[str(prop)] = prop_data

        return out_json

    def preprocess_obj_prop_hierarchy(self, verbose:bool) -> dict:
        """Process object properties hierarchy, the out dictionary will be formatted as:

        ```
        uri_obj_prop : ['sup_uri_obj_prop_1',...,'sup_uri_obj_prop_1']
        ```

        If complex classes are found (restrictions or lists). These will be kept and recusively added as a Python dictionary

        Args:
            verbose (bool): Log printing.

        Returns:
            dict: Dictionary with list of object properties and their hierarchy
        """

        onto = Graph()
        onto.parse(self.base_path / pc.RDF_OBJ_PROP)

        out_json = {}

        for r in onto.subjects(RDF.type, OWL.ObjectProperty):
            val = []
            for sup_r in set(onto.objects(r, RDFS.subPropertyOf)) - BUILTIN_URIS:
                val.append(bnode_to_dict(onto, sup_r, verbose=verbose))
            if val:
                out_json[r] = val

        return out_json


class TSVConverter:
    def __init__(
        self,
        path: str,
    ):

        self.p_data = dict()
        self.base_path = Path(path).resolve().absolute()

    def convert(
        self,
        triples: bool = True,
        splits: bool = True,
    ):

        if triples:
            self.p_data["triples"] = (
                self.preprocess_triples(self.base_path / "abox/obj_prop_assertions.nt"),
                self.base_path / "abox/obj_prop_assertions.tsv",
            )

        if splits:
            self.p_data["train"] = (
                self.preprocess_triples(self.base_path / pc.RDF_TRAIN),
                self.base_path / pc.TRAIN,
            )
            self.p_data["test"] = (
                self.preprocess_triples(self.base_path / pc.RDF_TEST),
                self.base_path / pc.TEST,
            )
            self.p_data["valid"] = (
                self.preprocess_triples(self.base_path / pc.RDF_VALID),
                self.base_path / pc.VALID,
            )


    def serialize(self):
        for key, values in self.p_data.items():
            obj = values[0]
            path = values[1]

            with open(path, "w") as f:
                if key in ["triples", "train", "valid", "test"]:
                    f.write(obj)

    def preprocess_triples(self, path):
        triples = Graph()
        triples.parse(path)
        out_str = ""
        for s, p, o in triples:
            out_str += f"{str(s)}\t{str(p)}\t{str(o)}\n"
        return out_str
    

class IDMapper:
    """Maps entity URIs to unique IDs"""

    def __init__(
        self,
        path: str,
    ):
        """Initialize the mapper with a dataset base path

        Args:
            path (str): Dataset location path
        """
        self.p_data = dict()
        self.base_path = Path(path).resolve().absolute()

        self.onto = Graph()
        self.onto.parse(self.base_path / pc.ONTOLOGY)

        self.ind_onto = Graph()
        self.ind_onto.parse(self.base_path / pc.INDIVIDUALS)

        self.out_data = dict()

    def map_to_id(self):

        classes =  set(self.onto.subjects(RDF.type, OWL.Class)) - BUILTIN_URIS
        classes = {c for c in classes if not isinstance(c, BNode)}

        properties = set(self.onto.subjects(RDF.type, OWL.ObjectProperty)) - BUILTIN_URIS
        individuals = set(self.ind_onto.subjects(RDF.type, OWL.NamedIndividual)) - BUILTIN_URIS

        classes = list(classes)
        properties = list(properties)
        individuals = list(individuals)

        classes.sort()
        properties.sort()
        individuals.sort()

        print("Classes", len(classes))
        print("Properties", len(properties))
        print("Individuals", len(individuals))

        self.out_data["c"] = ({str(c):i for i,c in enumerate(classes)}, self.base_path / pc.CLASS_MAPPINGS)
        self.out_data["i"] = ({str(c):i for i,c in enumerate(individuals)}, self.base_path / pc.INDIVIDUAL_MAPPINGS )
        self.out_data["p"] = ({str(c):i for i,c in enumerate(properties)}, self.base_path / pc.OBJ_PROP_MAPPINGS)


    def serialize(self):

        (self.base_path / pc.MAPPINGS).mkdir(exist_ok=True, parents=True)

        for _, data in self.out_data.items():
            mapping = data[0]
            path = data[1]

            with open(path, "w") as f:
                json.dump(mapping, f, indent=4)

