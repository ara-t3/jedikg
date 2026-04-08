#!/usr/bin/env python3

import json
from pathlib import Path

from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace
from rdflib.namespace import split_uri
from rdflib.term import URIRef

import jdex.utils.conventions.ids as idc
import jdex.utils.conventions.paths as pc
from jdex.utils.conventions.builtins import BUILTIN_URIS

import shutil
from rdflib import Graph
import jdex.utils.conventions.paths as pc
import sys
from pathlib import Path
from jdex.cli import CLI
from jdex.owl.reasoning import Reasoner



def verbose_print(msg: str, verbose: bool):
    """Print a message only when verbose logging is enabled.

    Args:
        msg (str): Message to print.
        verbose (bool): If True, the message is printed; otherwise it is ignored.
    """
    if verbose:
        print(msg)





def rdf_list_to_python_list(graph: Graph, head: URIRef, depth: int, verbose: bool = True) -> list:
    """Convert an RDF collection into a standard Python list.

    This function traverses an RDF list encoded with ``rdf:first``,
    ``rdf:rest``, and ``rdf:nil`` and recursively converts each element
    into a Python representation through ``bnode_to_dict``.

    Args:
        graph (Graph): RDFLib graph containing the RDF collection.
        head (URIRef): Head node of the RDF list.
        depth (int): Current recursion depth, used for indented verbose logging.
        verbose (bool, optional): Whether to print traversal logs. Defaults to True.

    Returns:
        list: Python list containing the converted RDF list elements.
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
    """Recursively convert an RDF node into a JSON-serializable Python object.

    URI references and literals are converted to strings directly. Blank nodes
    are recursively expanded into dictionaries keyed by predicate URI, with
    support for OWL collection constructs such as ``owl:unionOf``,
    ``owl:intersectionOf``, and ``owl:oneOf``.

    Args:
        graph (Graph): RDFLib graph containing the node description.
        node (URIRef): Node to convert. This may be a URIRef, Literal, or BNode.
        depth (int, optional): Current recursion depth, used for indented verbose
            logging. Defaults to 1.
        verbose (bool, optional): Whether to print traversal logs. Defaults to True.

    Returns:
        dict: A Python dictionary representation for blank nodes, or a string
        representation for URIRefs, Literals, and unsupported node types.
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
    """Convert selected OWL ontology components into JSON-serializable structures.

    This converter loads ontology fragments from a dataset directory and
    transforms selected parts of the schema and assertions into Python
    dictionaries that can later be serialized as JSON.
    """

    def __init__(
        self,
        path: str,
    ):
        """Initialize the converter with the dataset base directory.

        Args:
            path (str): Path to the root directory of the dataset to process.
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
        """Load and preprocess selected ontology components.

        Depending on the enabled flags, this method parses the corresponding
        ontology files and stores their converted Python representations for
        later serialization.

        Args:
            taxonomy (bool, optional): Whether to preprocess class taxonomy
                axioms. Defaults to True.
            class_assertions (bool, optional): Whether to preprocess individual
                class assertions. Defaults to True.
            obj_prop_domain_range (bool, optional): Whether to preprocess object
                property domain and range axioms. Defaults to True.
            obj_prop_hierarchy (bool, optional): Whether to preprocess object
                property hierarchy axioms. Defaults to True.
            verbose (bool, optional): Whether to print progress and traversal
                logs. Defaults to True.
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
        """Serialize all preprocessed ontology components to JSON files.

        Each preprocessed object stored in ``self.p_data`` is written to the
        corresponding target path using pretty-printed JSON formatting.
        """
        for values in self.p_data.values():
            obj = values[0]
            path = values[1]

            with open(path, "w") as f:
                json.dump(obj, f, indent=4)

    def preprocess_taxonomy(self, verbose: bool) -> dict:
        """Convert class taxonomy axioms into a dictionary representation.

        The output maps each class URI to the list of its direct superclasses.
        Complex superclass expressions, such as restrictions or OWL collections,
        are recursively represented as nested Python dictionaries.

        Output format::

            uri_class : ['uri_superclass_1', ..., 'uri_superclass_n']

        Args:
            verbose (bool): Whether to print traversal logs.

        Returns:
            dict: Mapping from class URIs to lists of superclass expressions.
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
        """Convert individual class assertions into a dictionary representation.

        The output maps each named individual URI to the list of classes it
        belongs to, excluding built-in OWL entities such as
        ``owl:NamedIndividual``.

        Output format::

            uri_individual : ['uri_class_1', ..., 'uri_class_n']

        Args:
            verbose (bool): Whether to print traversal logs.

        Returns:
            dict: Mapping from individual URIs to their asserted class URIs.
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
        """Convert object property domain and range axioms into a dictionary.

        For each object property, this method collects its declared domains and
        ranges. If no explicit domain or range is present, ``owl:Thing`` is
        used as the default value. Complex class expressions are recursively
        converted to nested Python structures.

        Output format::

            uri_obj_prop : {
                "domain": ['uri_c_1', ..., 'uri_c_n'],
                "range":  ['uri_c_1', ..., 'uri_c_m']
            }

        Args:
            verbose (bool): Whether to print traversal logs.

        Returns:
            dict: Mapping from object property URIs to their domain/range data.
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
        """Convert object property hierarchy axioms into a dictionary.

        The output maps each object property URI to the list of its direct
        super-properties. Complex property expressions, if present, are
        recursively converted to nested Python structures.

        Output format::

            uri_obj_prop : ['super_obj_prop_1', ..., 'super_obj_prop_n']

        Args:
            verbose (bool): Whether to print traversal logs.

        Returns:
            dict: Mapping from object property URIs to lists of super-properties.
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
    """Convert RDF triple files into TSV representations.

    This class reads RDF triple files from a dataset directory and prepares
    tab-separated ``subject predicate object`` text outputs, either for the
    full triple set or for train/validation/test splits.
    """
    def __init__(
        self,
        path: str,
    ):
        """
        Initialize the converter with the dataset base directory.

        Args:
            path (str): Path to the root directory of the dataset.
        """

        self.p_data = dict()
        self.base_path = Path(path).resolve().absolute()

    def convert(
        self,
        triples: bool = True,
        splits: bool = True,
    ):
        """
        Precompute TSV representations from RDF triple files.

        Depending on the enabled flags, this method converts the complete ABox
        object-property assertion file and/or the train/validation/test split
        files into TSV-formatted strings stored in memory for later writing.

        Args:
            triples (bool, optional): Whether to convert the complete set of
                object-property assertion triples. Defaults to True.
            splits (bool, optional): Whether to convert train, validation, and
                test split files. Defaults to True.      
        """

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
        """
        Write all prepared TSV outputs to disk.

        Only entries corresponding to triple TSV outputs are written. The method
        assumes that ``convert`` has already been called and that the in-memory
        TSV strings are available in ``self.p_data``.
        """
        for key, values in self.p_data.items():
            obj = values[0]
            path = values[1]

            with open(path, "w") as f:
                if key in ["triples", "train", "valid", "test"]:
                    f.write(obj)

    def preprocess_triples(self, path):
        """
        Convert an RDF graph file into a TSV-formatted string.

        The produced output contains one triple per line in the format
        ``subject<TAB>predicate<TAB>object``.

        Args:
            path (Path): Path to the RDF triple file to parse.

        Returns:
            str: TSV-formatted text containing all triples from the input graph.
        """
        triples = Graph()
        triples.parse(path)
        out_str = ""
        for s, p, o in triples:
            out_str += f"{str(s)}\t{str(p)}\t{str(o)}\n"
        return out_str
    

class IDMapper:
    """Create deterministic integer ID mappings for ontology entities.

    This class loads ontology and individual files, extracts classes, object
    properties, and named individuals, and assigns each entity a stable integer
    identifier based on lexicographic sorting of URIs.
    """

    def __init__(
        self,
        path: str,
    ):
        """Initialize the mapper with the dataset base directory.

        Args:
            path (str): Path to the root directory of the dataset.
        """
        self.p_data = dict()
        self.base_path = Path(path).resolve().absolute()

        self.onto = Graph()
        self.onto.parse(self.base_path / pc.ONTOLOGY)

        self.ind_onto = Graph()
        self.ind_onto.parse(self.base_path / pc.INDIVIDUALS)

        self.out_data = dict()

    def map_to_id(self):
        """
        Generate deterministic URI-to-integer mappings for ontology entities.

        IDs are assigned after lexicographically sorting the extracted URIs,
        which ensures reproducible mappings across runs for the same ontology
        content. Separate mappings are produced for:

        - classes
        - object properties
        - named individuals
        """

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
        """
        Write generated entity-ID mappings to JSON files.

        The method creates the mappings output directory if needed, then writes
        the class, individual, and object-property mappings stored in
        ``self.out_data`` as pretty-printed JSON files.
        """

        (self.base_path / pc.MAPPINGS).mkdir(exist_ok=True, parents=True)

        for _, data in self.out_data.items():
            mapping = data[0]
            path = data[1]

            with open(path, "w") as f:
                json.dump(mapping, f, indent=4)