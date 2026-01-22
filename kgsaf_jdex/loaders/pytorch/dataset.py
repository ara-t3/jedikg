#!/usr/bin/env python3

from pathlib import Path

import json
import torch
from rdflib import OWL, URIRef
from torch.utils.data import Dataset

import kgsaf_jdex.utils.conventions.ids as idc
import kgsaf_jdex.utils.conventions.paths as pc


class KnowledgeGraph(Dataset):
    def __init__(
        self,
        path: str,
    ):
        """_summary_

        Args:
            path (str): _description_
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

    def _warning(self, count):
        print(f"WARNING: {count} complex URIs detected. These classes are skipped during loading.")

    def _load_mappings(self, file_location: str):
        with open(self.base_path / file_location, "r") as map_json:
            return json.load(map_json)

    def individual_to_id(self, individual_uri: str) -> int:
        return self._individual_to_id[individual_uri]

    def class_to_id(self, class_uri: str) -> int:
        return self._class_to_id[class_uri]

    def obj_prop_to_id(self, obj_prop_uri: str) -> int:
        return self._obj_prop_to_id[obj_prop_uri]

    def id_to_individual(self, individual_id: int) -> str:
        return self._id_to_individual[individual_id]

    def id_to_class(self, class_id: int) -> str:
        return self._id_to_class[class_id]

    def id_to_obj_prop(self, obj_prop_id: int) -> str:
        return self._id_to_obj_prop[obj_prop_id]

    def individual_classes(self, individual_id: int) -> torch.tensor:
        return self.class_assertions[self.class_assertions[:, 0] == individual_id, 1]

    def sup_classes(self, class_id: int) -> torch.tensor:
        return self.taxonomy[self.taxonomy[:, 0] == class_id, 1]

    def sub_classes(self, class_id: int) -> torch.tensor:
        return self.taxonomy[self.taxonomy[:, 1] == class_id, 0]
    
    def is_leaf(self, class_id: int) -> bool:
        return len(self.sub_classes(class_id)) == 0

    def sup_obj_prop(self, obj_prop_id: int) -> torch.tensor:
        return self.obj_props_hierarchy[
            self.obj_props_hierarchy[:, 0] == obj_prop_id, 1
        ]

    def sub_obj_prop(self, obj_prop_id: int) -> torch.tensor:
        return self.obj_props_hierarchy[
            self.obj_props_hierarchy[:, 1] == obj_prop_id, 0
        ]

    def obj_prop_domain(self, obj_prop_id: int) -> torch.tensor:
        return self.obj_props_domain[self.obj_props_domain[:, 0] == obj_prop_id, 1]

    def obj_prop_range(self, obj_prop_id: int) -> torch.tensor:
        return self.obj_props_range[self.obj_props_range[:, 0] == obj_prop_id, 1]

    # Getters

    @property
    def dataset_location(self) -> str:
        return str(self.base_path)

    @property
    def train(self) -> torch.tensor:
        return self._train_triples

    @property
    def valid(self) -> torch.tensor:
        return self._valid_triples

    @property
    def test(self) -> torch.tensor:
        return self._test_triples

    @property
    def class_assertions(self) -> torch.tensor:
        return self._class_assertions

    @property
    def taxonomy(self) -> torch.tensor:
        return self._taxonomy

    @property
    def obj_props_hierarchy(self) -> torch.tensor:
        return self._obj_prop_hierarchy

    @property
    def obj_props_domain(self) -> torch.tensor:
        return self._obj_prop_domain_range[
            self._obj_prop_domain_range[:, 1] == idc.DOMAIN
        ][:, [0, 2]]

    @property
    def obj_props_range(self) -> torch.tensor:
        return self._obj_prop_domain_range[
            self._obj_prop_domain_range[:, 1] == idc.RANGE
        ][:, [0, 2]]

    @property
    def obj_props_domains_range(self) -> torch.tensor:
        return self._obj_prop_domain_range

    # ABOX Loading Functions

    def _load_abox_triples(self, file_location: str):
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


