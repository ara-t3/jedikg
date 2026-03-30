#!/usr/bin/env python3

from rdflib import Graph, RDF, OWL, BNode
from rdflib.term import URIRef
from pathlib import Path
import sys
import subprocess
import json
sys.path.append(str(Path.cwd().parent))
from kgsaf_jdex.utils.conventions.builtins import BUILTIN_URIS
from kgsaf_jdex.utils.modularization import SignatureModularizer, SchemaDecomposer 
from pykeen.triples import TriplesFactory
from pykeen.triples.splitting import CoverageSplitter
from kgsaf_jdex.utils.conversion import OWLConverter, TSVConverter, IDMapper
from pykeen.triples.leakage import unleak
from kgsaf_jdex.utils.reason import ReasonerUtility
from kgsaf_jdex.utils.reasoner import Reasoner
import kgsaf_jdex.utils.conventions.paths as pc

import argparse
import logging


from kgsaf_jdex.config import JDEXConfig
from typing import Any, Literal
from pathlib import Path
import shutil
import json



class JDEX:
    def __init__(self, config: JDEXConfig):
        self.config = config
        self.cwd = self.config.paths.output / self.config.dataset_name
        self.reasoner = Reasoner(
                reasoners_path=Path("./reasoners/").absolute(),
                java8_path=self.config.reasoning.java_8_home,
                java11_path=self.config.reasoning.java_11_home,
                java_max_ram=20
        ) 
        
    def vprint(self, str):
        if self.config.verbose:
            print(str)

    def kill(self):
        print("[INF] JDEX Suite Terminated")
        sys.exit(1)
        
    @classmethod
    def from_json(cls, json_path: str | Path) -> "JDEX":
        json_path = Path(json_path)

        if not json_path.exists():
            raise FileNotFoundError(f"Config file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JDEX":
        return cls(JDEXConfig.from_dict(data))

    def config_summary(self) -> str:
        return self.config.pretty_print()
    
    def run(self):

        self.vprint("[INF] Starting JDEX Dataset Generation Suite")

        # ----------------------------------
        # MAKE BASE WORKING FOLDER 
        # ----------------------------------

        if self.cwd.exists():
            shutil.rmtree(self.cwd)
        self.cwd.mkdir(parents=True, exist_ok=True)

        self.vprint("[SUC] Base Folder Created")

        # ----------------------------------
        # CONVERT SCHEMA TO BASE FORMAT
        # ----------------------------------

        self.vprint(f"[INF] Converthing Schema File {self.config.paths.schema} to OWL format")
        self.reasoner.conversion(self.config.paths.schema, self.cwd / pc.ONTOLOGY, format="owl", verbose=self.config.verbose)
        self.vprint(f"[SUC] Temporary Conversion saved as {self.cwd / pc.ONTOLOGY}")

        # -----------------------------------
        # CHECK APPLICABILITY OF REASONING SERVICES
        # ----------------------------------

        if (not self.config.reasoning.filter_unsatisfiable):
            if  (self.config.reasoning.materialization or self.config.reasoning.realization):
                unsatifiable_classes = self.reasoner.satisfiability(
                    input_ontology=self.config.paths.schema, 
                    verbose=self.config.verbose
                )
                if not(unsatifiable_classes):
                    self.vprint("[SUC] No Unsatisfiable Classes / Object Properties Found")
                else:
                    self.vprint(f"[ERR] Reasoning services cannot be activated on ontologies with unsatisfiable classes / roles. Unsatisfiable classes found: [{",".join(unsatifiable_classes)}]. Please run with 'filter_unsatisfiable':true. """)
                    self.kill()
        else:
            sc_it_number = 0
            tot_removed = 0
            self.vprint("[INF] Starting Removal of Unsatisfiable Classes / Roles")
            while True:
                unsatifiable_classes = self.reasoner.satisfiability(
                    input_ontology=self.cwd / pc.ONTOLOGY, 
                    verbose=self.config.verbose
                )
                
     


        # -----------------------------------
        # SUBFOLDERS GENERATIONS
        # ----------------------------------

        (self.cwd / "abox").mkdir(parents=True, exist_ok=True)
        (self.cwd / "tbox").mkdir(parents=True, exist_ok=True)
        (self.cwd / "rbox").mkdir(parents=True, exist_ok=True)

        self.vprint("[SUC] Subfolders ABox / TBox / RBox created")

        if self.config.split.enabled:
            (self.cwd / "abox" / "splits").mkdir(parents=True, exist_ok=True)
            self.vprint("[SUC] Split Subfolder created")

        if self.config.post_processing.id_mapping:
            (self.cwd / "mappings").mkdir(parents=True, exist_ok=True)
            self.vprint("[SUC] ID Mappings Subfolder created")


        # -----------------------------------
        # SUBFOLDERS GENERATIONS
        # ----------------------------------







     







        

            

if __name__ == "__main__":
    jdex = JDEX.from_json("/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_jdex/config.json")
    jdex.run()






# """
# def main(args):
#     """
#     KG-SaF-JDeX Full Workflow
#     """

#     logger.info(f"Done!")

#     # =====================
#     # KNOWLEDGE GRAPH CONVERSION
#     # =====================

#     reasoner.convert_owl(KG_FILE, OUTPUT_FILE)


#     # =====================
#     # FILTERING OF UNSATISFIABLE CLASSES
#     # =====================


#     if REASONER:
#         reasoner.filter_unsatisfiable(OUTPUT_FILE, OUTPUT_FILE)

#     # =====================
#     # REASONING UTILITIES
#     # =====================

#     if REASONER:
#         properties = [
#             "SubClass",
#             "EquivalentClass",
#             "EquivalentObjectProperty",
#             "InverseObjectProperties",
#             "ObjectPropertyCharacteristic",
#             "SubObjectProperty",
#             "ObjectPropertyRange",
#             "ObjectPropertyDomain",
#             "ClassAssertion"
#         ]

#         debug_path = DATASET_PATH / "debug.owl"
#         reasoner.reason(properties, OUTPUT_FILE, OUTPUT_FILE, debug_path)

#     # =====================
#     # ABOX FILTERING
#     # =====================

#     print("Parsing and Loading Target Knowledge Graph...")
#     kg = Graph()
#     kg.parse(OUTPUT_FILE)
#     print("Done!")

#     print("Filtering <NamedIndividual, ObjectPropety, NamedIndividual> Triples")

#     triples_graph = Graph()
#     for s,p,o in kg:
#         if (s, RDF.type, OWL.NamedIndividual) in kg and (p, RDF.type, OWL.ObjectProperty) in kg and (o, RDF.type, OWL.NamedIndividual) in kg:
#             triples_graph.add((s,p,o))

#     print(f"Initial Dataset: {len(triples_graph)} triples found (OWL.NamedIndividual, OWL.ObjectProperty, OWL.NamedIndividual) Found")

#     predicates = set()

#     print("Analyzing Object Properties")

#     for prop in triples_graph.predicates(None, None):
#         if (prop, RDF.type, OWL.DatatypeProperty) not in kg:
#             predicates.add(prop)
#         else:
#             print(f"Predicate {prop} removed from dataset. Defined as DatatypeProperty")

#     print(f"Initial Dataset: {len(predicates)} predicates (OWL.ObjectProperty) Found")


#     individuals = set()

#     print("Analyzing SUBJECTS")
#     for ind in triples_graph.subjects(None, None):
#         if (ind, RDF.type, OWL.Class) not in kg:
#             individuals.add(ind)
#         else:
#             print(f"Individual {ind} removed from dataset. Defined as Class")

#     print("Analyzing OBJECTS")
#     for ind in triples_graph.objects(None, None):
#         if (ind, RDF.type, OWL.Class) not in kg:
#             individuals.add(ind)
#         else:
#             print(f"Individual {ind} removed from dataset. Defined as Class")

#     print(f"Dataset will contain a total of {len(individuals)} individuals (OWL.NamedIndividual)")

#     print(f"Removing Triples...")

#     for s,p,o in triples_graph:
#         if (s not in individuals) or (o not in individuals):
#             triples_graph.remove((s,p,o))

#     print(f"Dataset will contain a total of {len(triples_graph)} triples (OWL.NamedIndividual, OWL.ObjectProperty, OWL.NamedIndividual)")

#     print("Serializing Intermediate File...")
#     triples_graph.serialize(DATASET_PATH / "obj_prop_assertion.nt", format="nt", robot_jar=ROBOT_JAR)

#     with open(DATASET_PATH / "obj_prop_assertion.tsv", "w") as f:
#         for s, p, o in triples_graph:
#             f.write(f"{s}\t{p}\t{o}\n")
#     print("Done")

#     # =====================
#     # DATASET SPLITTING AND INVERSION LEAKAGE 
#     # =====================


#     triples = TriplesFactory.from_path(DATASET_PATH / "obj_prop_assertion.tsv")

#     entity_mappings = {v:k for k,v in triples.entity_id_to_label.items()}
#     relation_mappings = {v:k for k,v in triples.relation_id_to_label.items()}

#     train, valid, test = triples.split(
#         ratios=[0.85, 0.05, 0.1],
#         random_state=42,
#         method=CoverageSplitter(),      
#     )

#     train_clean = TriplesFactory.from_labeled_triples(
#         triples=train.triples,
#         entity_to_id=entity_mappings,
#         relation_to_id=relation_mappings
#     )

#     valid_clean = TriplesFactory.from_labeled_triples(
#         triples=valid.triples,
#         entity_to_id=entity_mappings,
#         relation_to_id=relation_mappings
#     )

#     test_clean = TriplesFactory.from_labeled_triples(
#         triples=test.triples,
#         entity_to_id=entity_mappings,
#         relation_to_id=relation_mappings
#     )

#     train_unleak, valid_unleak, test_unleak = unleak(
#         train_clean,
#         *[valid_clean, test_clean],
#         n=None,
#         minimum_frequency=0.97
#         )

#     print("Serializing NT Splits and Full Dataset...")

#     targets = [
#         (DATASET_PATH / "abox/splits/train", train_unleak.triples),
#         (DATASET_PATH / "abox/splits/valid", valid_unleak.triples),
#         (DATASET_PATH / "abox/splits/test", test_unleak.triples)
#     ]

#     for path, split in targets:
#         out_graph = Graph()
#         for triple in split:
#             s = URIRef(triple[0])
#             p = URIRef(triple[1])
#             o = URIRef(triple[2])
#             out_graph.add((URIRef(s), URIRef(p), URIRef(o)))

#         print(f"\tSerializing {path}")
#         out_graph.serialize(path.with_suffix(".nt"), format="nt")

#     print(f"\tSerializing  Full Dataset")
#     input_folder = DATASET_PATH / "abox" / "splits"
#     output_file = DATASET_PATH / "abox" / "obj_prop_assertions.nt"
#     input_files = list(input_folder.glob("*.nt"))
#     print("Done")

#     input_files = list(input_folder.glob("*.nt"))
#     if not input_files:
#         raise FileNotFoundError(f"No .nt files found in {input_folder}")

#     cmd = ["cat"] + [str(f) for f in input_files]

#     with open(output_file, "wb") as f_out:
#         result = subprocess.run(cmd, stdout=f_out)

#     if result.returncode != 0:
#         raise RuntimeError(f"Failed to concatenate NT files, return code {result.returncode}")

#     print(f"All NT files merged into {output_file}")

#     # =====================
#     # ABOX Serialization
#     # =====================

#     print("Serializing NamedIndividuals...")
#     out_graph = Graph()

#     for ind in individuals:
#         out_graph.add((ind, RDF.type, OWL.NamedIndividual))

#     reasoner.serialize(out_graph, DATASET_PATH / "abox" / "individuals")
#     del out_graph
#     print("Done!")

#     print("Serializing ClassAssertions...")
#     class_assertions_graph = Graph()

#     for ind in individuals:
#         for ca in set(kg.objects(ind, RDF.type)) - BUILTIN_URIS:
#             if (ca, RDF.type, OWL.Class) in kg:
#                 class_assertions_graph.add((ind, RDF.type, ca))
#             else:
#                 print(f"Not a Class {ca}")

#     reasoner.serialize(class_assertions_graph, DATASET_PATH / "abox" / "class_assertions")
#     print("Done!")


#     # =====================
#     # Schema Modularization 
#     # =====================

#     seed_obj_props = predicates
#     print("Seed Object Properties", len(seed_obj_props))

#     seed_classes = set(class_assertions_graph.objects(None, RDF.type))
#     print("Seed Classes", len(seed_classes))

#     modularizer = SignatureModularizer(kg, seed_classes | seed_obj_props)
#     out_graph = modularizer.modularize(verbose=False)

#     reasoner.serialize(out_graph, DATASET_PATH / "ontology")

#     # =====================
#     # Schema Decomposition 
#     # =====================

#     onto_graph = Graph()
#     onto_graph.parse(DATASET_PATH / "ontology.owl")

#     decomposer = SchemaDecomposer(onto_graph)
#     rbox_graph, taxonomy_graph, schema_graph = decomposer.decompose(verbose=False)

#     reasoner.serialize(rbox_graph, DATASET_PATH / "rbox" / "roles")
#     reasoner.serialize(taxonomy_graph, DATASET_PATH / "tbox" / "taxonomy")
#     reasoner.serialize(schema_graph, DATASET_PATH / "tbox" / "schema")

#     # =====================
#     # File Removal 
#     # =====================

#     (DATASET_PATH / "intermediate_kg.owl").unlink()
#     (DATASET_PATH / "obj_prop_assertion.nt").unlink()
#     (DATASET_PATH / "obj_prop_assertion.tsv").unlink()

#     # =====================
#     # Full KG Decomposition 
#     # =====================

#     inputs = [
#         DATASET_PATH / pcc.ONTOLOGY,
#         DATASET_PATH / pcc.INDIVIDUALS,
#         DATASET_PATH / pcc.RDF_TRIPLES,
#         DATASET_PATH / pcc.RDF_CLASS_ASSERTIONS
#     ]

#     output_file = DATASET_PATH / "knowledge_graph.owl"
#     cmd = ["java", "-Xmx20G", "-jar", str(ROBOT_JAR), "merge"]

#     for infile in inputs:
#         cmd += ["--input", str(infile)]

#     cmd += ["--output", str(output_file)]

#     result = subprocess.run(cmd, capture_output=False, text=True)

#     if result.returncode != 0:
#         raise RuntimeError(f"ROBOT merge failed with return code {result.returncode}")

#     print(f"Merged knowledge graph saved to {output_file}")


#     # =====================
#     # Machine Learning Utilities
#     # =====================


#     print(f"\t Converting Dataset {DATASET_PATH.name}")
#     processor = TSVConverter(DATASET_PATH)
#     processor.convert()
#     processor.serialize()


#     print(f"\tProcessing Dataset {DATASET_PATH.name}")
#     processor = OWLConverter(DATASET_PATH)
#     processor.preprocess(verbose=False)
#     processor.serialize()


#     print(f"Mapping Dataset {DATASET_PATH.name}")
#     mapper = IDMapper(DATASET_PATH)
#     mapper.map_to_id()
#     mapper.serialize()

#     logging.info("Finish!")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Process KG and optionally run reasoner")
#     parser.add_argument("--reasoner", action="store_true", help="Run reasoning services")
#     parser.add_argument("--kg_file", required=True, help="Input KG file path")
#     parser.add_argument("--output_path", required=True, help="Output dataset folder")
#     parser.add_argument("--dataset_name", default="kg_consistent", help="Base dataset name")
#     parser.add_argument("--robot_jar", required=True, help="Path to ROBOT jar")
     
#     args = parser.parse_args()
#     main(args)
