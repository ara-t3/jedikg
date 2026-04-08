#!/usr/bin/env python3

from pathlib import Path

import json
import torch
from rdflib import OWL, URIRef
from torch.utils.data import Dataset

import jdex.utils.conventions.ids as idc
import jdex.utils.conventions.paths as pc


class KnowledgeGraph(Dataset):
    """
    PyTorch dataset wrapper for ontology-aware knowledge graph data.

    This class loads a dataset organized around standard knowledge graph
    components together with selected ontology-derived structures. It provides
    access to:

    - ABox object-property triples for train, validation, and test splits
    - Class assertions for individuals
    - TBox taxonomy relations between classes
    - RBox object-property hierarchy and domain/range constraints
    - URI-to-ID and ID-to-URI mappings for individuals, classes, and properties

    All loaded symbolic data is converted into ``torch.Tensor`` objects so it
    can be consumed directly by downstream machine learning pipelines.

    Notes:
        - The dataset assumes that mapping files and serialized ontology-derived
          JSON files have already been generated.
        - Some complex OWL expressions are only partially supported. In
          particular, ``owl:unionOf`` is handled in domain/range loading, while
          other complex constructs are skipped with a warning.
    """
    def __init__(
        self,
        path: str,
    ):
        """
        Initialize the knowledge graph dataset from a dataset directory.

        Args:
            path (str): Path to the root folder of the prepared dataset.
        """

        super().__init__()


        # Dataset BASE Folder

        self.base_path = Path(path).resolve().absolute()

        # Mapping URIS to IDs and Back

        self._individual_to_id = self._load_mappings(pc.INDIVIDUAL_MAPPINGS)
        self._class_to_id = self._load_mappings(pc.CLASS_MAPPINGS)
        self._obj_prop_to_id = self._load_mappings(pc.OBJ_PROP_MAPPINGS)

        self._class_to_id[str(OWL.Thing)] = idc.THING
        self._class_to_id[str("http://schema.org/Thing")] = idc.THING

        self._id_to_individual = {v: k for k, v in self._individual_to_id.items()}
        self._id_to_class = {v: k for k, v in self._class_to_id.items()}
        self._id_to_obj_prop = {v: k for k, v in self._obj_prop_to_id.items()}

        # ABox

        self._train_triples = self._load_abox_triples(pc.TRAIN)
        self._test_triples = self._load_abox_triples(pc.TEST)
        self._valid_triples = self._load_abox_triples(pc.VALID)

        self._class_assertions = self._load_abox_class_assertions()

        # TBox

        self._taxonomy = self._load_tbox_taxonomy()

        # RBox

        self._obj_prop_domain_range = self._load_rbox_domain_range()
        self._obj_prop_hierarchy = self._load_rbox_hierarchy()

    # General Functions

    def _warning(self, count:int):
        """
        Print a warning about skipped complex ontology expressions.

        This warning is issued when some ontology elements cannot be converted
        into the simplified tensor representation used by this loader.

        Args:
            count (int): Number of complex expressions skipped during loading.
        """
        print(f"WARNING: {count} complex URIs detected. These classes are skipped during loading.")

    def _load_mappings(self, file_location: str):
        """
        Load a URI-to-ID mapping from a JSON file.

        Args:
            file_location (str): Relative path to the mapping file within the
                dataset directory.

        Returns:
            dict: Dictionary mapping entity URIs to integer IDs.
        """        
        with open(self.base_path / file_location, "r") as map_json:
            return json.load(map_json)

    def individual_to_id(self, individual_uri: str) -> int:
        """
        Convert an individual URI into its integer ID.

        Args:
            individual_uri (str): URI of the target individual.

        Returns:
            int: Integer ID assigned to the individual.
        """
        return self._individual_to_id[individual_uri]

    def class_to_id(self, class_uri: str) -> int:
        """
        Convert a class URI into its integer ID.

        Args:
            class_uri (str): URI of the target class.

        Returns:
            int: Integer ID assigned to the class.
        """
        return self._class_to_id[class_uri]

    def obj_prop_to_id(self, obj_prop_uri: str) -> int:
        """
        Convert an object property URI into its integer ID.

        Args:
            obj_prop_uri (str): URI of the target object property.

        Returns:
            int: Integer ID assigned to the object property.
        """
        return self._obj_prop_to_id[obj_prop_uri]

    def id_to_individual(self, individual_id: int) -> str:
        """
        Convert an individual ID back into its URI.

        Args:
            individual_id (int): Integer ID of the target individual.

        Returns:
            str: URI corresponding to the given individual ID.
        """
        return self._id_to_individual[individual_id]

    def id_to_class(self, class_id: int) -> str:
        """
        Convert a class ID back into its URI.

        Args:
            class_id (int): Integer ID of the target class.

        Returns:
            str: URI corresponding to the given class ID.
        """
        return self._id_to_class[class_id]

    def id_to_obj_prop(self, obj_prop_id: int) -> str:
        """
        Convert an object property ID back into its URI.

        Args:
            obj_prop_id (int): Integer ID of the target object property.

        Returns:
            str: URI corresponding to the given object property ID.
        """
        return self._id_to_obj_prop[obj_prop_id]

    def individual_classes(self, individual_id: int) -> torch.tensor:
        """
        Return all asserted classes for a given individual.

        Args:
            individual_id (int): Integer ID of the individual.

        Returns:
            torch.tensor: Tensor containing the class IDs asserted for the
            individual.
        """
        return self.class_assertions[self.class_assertions[:, 0] == individual_id, 1]

    def sup_classes(self, class_id: int) -> torch.tensor:
        """
        Return the direct superclasses of a class.

        Args:
            class_id (int): Integer ID of the class.

        Returns:
            torch.tensor: Tensor containing the superclass IDs of the input
            class.
        """
        return self.taxonomy[self.taxonomy[:, 0] == class_id, 1]

    def sub_classes(self, class_id: int) -> torch.tensor:
        """
        Return the direct subclasses of a class.

        Args:
            class_id (int): Integer ID of the class.

        Returns:
            torch.tensor: Tensor containing the subclass IDs of the input class.
        """
        return self.taxonomy[self.taxonomy[:, 1] == class_id, 0]
    
    def is_leaf(self, class_id: int) -> bool:
        """
        Check whether a class has no known subclasses in the taxonomy.

        Args:
            class_id (int): Integer ID of the class.

        Returns:
            bool: True if the class has no subclasses, False otherwise.
        """
        return len(self.sub_classes(class_id)) == 0

    def sup_obj_prop(self, obj_prop_id: int) -> torch.tensor:
        """
        Return the direct super-properties of an object property.

        Args:
            obj_prop_id (int): Integer ID of the object property.

        Returns:
            torch.tensor: Tensor containing the IDs of the super-properties.
        """
        return self.obj_props_hierarchy[
            self.obj_props_hierarchy[:, 0] == obj_prop_id, 1
        ]

    def sub_obj_prop(self, obj_prop_id: int) -> torch.tensor:
        """
        Return the direct sub-properties of an object property.

        Args:
            obj_prop_id (int): Integer ID of the object property.

        Returns:
            torch.tensor: Tensor containing the IDs of the sub-properties.
        """
        return self.obj_props_hierarchy[
            self.obj_props_hierarchy[:, 1] == obj_prop_id, 0
        ]

    def obj_prop_domain(self, obj_prop_id: int) -> torch.tensor:
        """
        Return the declared domain classes of an object property.

        Args:
            obj_prop_id (int): Integer ID of the object property.

        Returns:
            torch.tensor: Tensor containing the class IDs occurring in the
            property's domain.
        """
        return self.obj_props_domain[self.obj_props_domain[:, 0] == obj_prop_id, 1]

    def obj_prop_range(self, obj_prop_id: int) -> torch.tensor:
        """
        Return the declared range classes of an object property.

        Args:
            obj_prop_id (int): Integer ID of the object property.

        Returns:
            torch.tensor: Tensor containing the class IDs occurring in the
            property's range.
        """
        return self.obj_props_range[self.obj_props_range[:, 0] == obj_prop_id, 1]

    # Getters

    @property
    def dataset_location(self) -> str:
        """str: Absolute path to the dataset root directory."""
        return str(self.base_path)

    @property
    def train(self) -> torch.tensor:
        """torch.tensor: Training ABox triples as ``[subject, predicate, object]`` rows."""
        return self._train_triples

    @property
    def valid(self) -> torch.tensor:
        """torch.tensor: Validation ABox triples as ``[subject, predicate, object]`` rows."""
        return self._valid_triples

    @property
    def test(self) -> torch.tensor:
        """torch.tensor: Test ABox triples as ``[subject, predicate, object]`` rows."""
        return self._test_triples

    @property
    def class_assertions(self) -> torch.tensor:
        """torch.tensor: Class assertions as ``[individual_id, class_id]`` rows."""
        return self._class_assertions

    @property
    def taxonomy(self) -> torch.tensor:
        """torch.tensor: Taxonomy edges as ``[subclass_id, superclass_id]`` rows."""
        return self._taxonomy

    @property
    def obj_props_hierarchy(self) -> torch.tensor:
        """torch.tensor: Object-property hierarchy as ``[subproperty_id, superproperty_id]`` rows."""
        return self._obj_prop_hierarchy

    @property
    def obj_props_domain(self) -> torch.tensor:
        """torch.tensor: Object-property domain assertions as ``[property_id, class_id]`` rows."""
        return self._obj_prop_domain_range[
            self._obj_prop_domain_range[:, 1] == idc.DOMAIN
        ][:, [0, 2]]

    @property
    def obj_props_range(self) -> torch.tensor:
        """torch.tensor: Object-property range assertions as ``[property_id, class_id]`` rows."""
        return self._obj_prop_domain_range[
            self._obj_prop_domain_range[:, 1] == idc.RANGE
        ][:, [0, 2]]

    @property
    def obj_props_domains_range(self) -> torch.tensor:
        """torch.tensor: Combined domain/range assertions as ``[property_id, marker, class_id]`` rows."""
        return self._obj_prop_domain_range

    # ABOX Loading Functions

    def _load_abox_triples(self, file_location: str):
        """
        Load ABox object-property triples from a TSV file.

        Each line is expected to contain three tab-separated URIs:
        subject, predicate, and object. These are converted into integer IDs.

        Args:
            file_location (str): Relative path to the TSV triple file.

        Returns:
            torch.tensor: Tensor of shape ``(n, 3)`` containing encoded triples.
        """
        triples = []
        with open(self.base_path / file_location, "r") as triples_txt:
            for t in triples_txt.readlines():
                triple_split = t.strip().split("\t")
                s = self.individual_to_id(triple_split[0])
                p = self.obj_prop_to_id(triple_split[1])
                o = self.individual_to_id(triple_split[2])
                triples.append([s, p, o])

        return torch.tensor(triples, dtype=torch.int64)

    def _load_abox_class_assertions(self):
        """
        Load individual class assertions from the serialized JSON file.

        The JSON structure is expected to map individual URIs to lists of class
        URIs. Only individuals present in the loaded mappings are included.

        Returns:
            torch.tensor: Tensor of shape ``(n, 2)`` containing
            ``[individual_id, class_id]`` pairs. Returns an empty tensor if the
            class-assertion file does not exist.
        """

        if not (self.base_path / pc.CLASS_ASSERTIONS).exists():
            return torch.tensor([])

        casrt = []

        with open(self.base_path / pc.CLASS_ASSERTIONS, "r") as casrt_json:
            data = json.load(casrt_json)

        for ind_uri in data:
            if ind_uri in self._individual_to_id.keys():
                ind_id = self.individual_to_id(ind_uri)
                for class_uri in data[ind_uri]:
                    class_id = self.class_to_id(class_uri)
                    casrt.append([ind_id, class_id])

        return torch.tensor(casrt, dtype=torch.int64)

    # TBOX Loading Functions

    def _load_tbox_taxonomy(self):
        """
        Load class taxonomy edges from the serialized JSON taxonomy file.

        Only simple superclass URIs are converted. Complex superclass
        expressions represented as dictionaries are skipped and counted for
        warning purposes.

        Returns:
            torch.tensor: Tensor of shape ``(n, 2)`` containing
            ``[subclass_id, superclass_id]`` pairs. Returns an empty tensor if
            the taxonomy file does not exist.
        """

        if not (self.base_path / pc.TAXONOMY).exists():
            return torch.tensor([])

        taxonomy = []
        complex_uri = 0

        with open(self.base_path / pc.TAXONOMY, "r") as taxonomy_json:
            data = json.load(taxonomy_json)

        for c_uri in data:
            c_id = self.class_to_id(c_uri)
            for sup_c_uri in data[c_uri]:

                if isinstance(sup_c_uri, dict):
                    complex_uri += 1
                    
                else:
                    sup_c_id = self.class_to_id(sup_c_uri)
                    taxonomy.append([c_id, sup_c_id])

        if complex_uri > 0:
            self._warning(complex_uri)
                
        return torch.tensor(taxonomy, dtype=torch.int64)

    # RBOX Loading Functions

    def _load_rbox_domain_range(self):
        """
        Load object-property domain and range constraints from JSON.

        Domain and range entries are converted into rows of the form
        ``[property_id, marker, class_id]``, where ``marker`` distinguishes
        between domain and range using predefined constants.

        Complex expressions are partially supported through
        ``_compute_domain_range``. Unsupported complex expressions are skipped
        and counted for warning purposes.

        Returns:
            torch.tensor: Tensor containing encoded domain/range assertions, or
            an empty tensor if the hierarchy file is missing.
        """
        if not (self.base_path / pc.OBJ_PROP_HIERARCHY).exists():
            return torch.tensor([])
        
        complex_uri = 0

        with open(self.base_path / pc.OBJ_PROP_DOMAIN_RANGE, "r") as role_dm_json:
            data = json.load(role_dm_json)

        dm = []

        for r_uri in data:
            r_id = self.obj_prop_to_id(r_uri)
            domain, ex_d = self._compute_domain_range(data[r_uri]["domain"])
            range, ex_r = self._compute_domain_range(data[r_uri]["range"])

            complex_uri += ex_d
            complex_uri += ex_r

            for id in domain:

                dm.append([r_id, idc.DOMAIN, id])
            for id in range:
                dm.append([r_id, idc.RANGE, id])

        if complex_uri > 0:
            self._warning(complex_uri)

        return torch.tensor(dm, dtype=torch.int64)

    def _compute_domain_range(self, subdata):
        """
        Convert a domain/range JSON fragment into class IDs.

        Supported cases:
            - Plain class URIs
            - ``owl:unionOf`` expressions represented as dictionaries

        Unsupported complex dictionary expressions are skipped.

        Args:
            subdata: List-like JSON fragment describing domain or range entries.

        Returns:
            tuple[list[int], int]: A pair containing:
                - the list of extracted class IDs
                - the number of skipped unsupported complex expressions
        """
        out = []
        excluded = 0
        for elem in subdata:
            if type(elem) is dict and str(OWL.unionOf) in elem.keys():
                for unionclass in elem[str(OWL.unionOf)]:
                    out.append(self.class_to_id(unionclass))
            elif type(elem) is dict:
                excluded += 1
            else:
                out.append(self.class_to_id(elem))
        return out, excluded

    def _load_rbox_hierarchy(self):
        """
        Load object-property hierarchy edges from the serialized JSON file.

        Only simple super-property URIs are converted. Complex property
        expressions represented as dictionaries are skipped and counted for
        warning purposes.

        Returns:
            torch.tensor: Tensor of shape ``(n, 2)`` containing
            ``[subproperty_id, superproperty_id]`` pairs. Returns an empty
            tensor if the object-property hierarchy file does not exist.
        """
        if not (self.base_path / pc.OBJ_PROP_HIERARCHY).exists():
            return torch.tensor([])

        rh = []
        complex_uri = 0

        with open(self.base_path / pc.OBJ_PROP_HIERARCHY, "r") as role_h_json:
            data = json.load(role_h_json)

        for r_uri in data:
            r_id = self.obj_prop_to_id(r_uri)
            for sup_r_uri in data[r_uri]:
                if type(sup_r_uri) is dict:
                    complex_uri += 1
                else:
                    rh.append([r_id, self.obj_prop_to_id(sup_r_uri)])

        if complex_uri > 0:
            self._warning(complex_uri)

        return torch.tensor(rh, dtype=torch.int64)