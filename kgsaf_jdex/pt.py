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
import numpy as np
import argparse
import logging
import time




from kgsaf_jdex.config import JDEXConfig
from typing import Any, Literal
from pathlib import Path
import shutil
import json
from kgsaf_jdex.cli import CLI






class JDEX:

    def __init__(self, config: JDEXConfig):
        self.config = config
        self.ui = CLI(self.config.verbose)
        self.cwd = (self.config.paths.output / self.config.dataset_name).absolute()
        self.reasoner = Reasoner(
                reasoners_path=Path("./reasoners/unpack").absolute(),
                java8_path=self.config.reasoning.java_8_home,
                java11_path=self.config.reasoning.java_11_home,
                java_max_ram=20
        ) 
        
    def kill(self, code: int = 1):
        self.ui.rule("JDEX Suite Terminated")
        sys.exit(code)

    def startup_screen(self):
        self.ui.logo()
        
    @classmethod
    def from_json(cls, json_path: str | Path) -> "JDEX":
        json_path = Path(json_path)

        if not json_path.exists():
            raise FileNotFoundError(f"Config file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)
    
    def interactive_menu(self) -> str:
        return self.ui.choose(
            "What do you want to do?",
            [
                "Run dataset generation",
                "Show configuration summary",
                "Exit",
            ],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JDEX":
        return cls(JDEXConfig.from_dict(data))

    def config_summary(self) -> str:
        return self.config.pretty_print()
    

    def filter_unsatisfiable(self):
        sc_it_number = 1
        tot_removed = 0
        self.ui.info("Starting Removal of Unsatisfiable Classes / Roles")
        while True:
            unsatifiable_classes = self.reasoner.satisfiability(
                input_ontology=self.cwd / pc.ONTOLOGY, 
                verbose=self.config.verbose
            )
            self.ui.info(f"Unsatisfiability Removel Step {sc_it_number}. Found {len(unsatifiable_classes)} Unsatisfiable URI")
            if unsatifiable_classes:
                self.ui.info(f"Unsatisfiable Uris Found: {unsatifiable_classes}")
                self.reasoner.filtering(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, uris=unsatifiable_classes, verbose=self.config.verbose)
                sc_it_number +=1
                tot_removed += len(unsatifiable_classes)
            else:
                self.ui.success(f"Filtered {tot_removed} unsatisfiable URIs in {sc_it_number} steps")
                return sc_it_number, tot_removed


    def run(self):

        self.startup_screen()

        while True:
            choice = self.interactive_menu()
            match choice:
                case "Show configuration summary":
                    self.ui.summary("Configuration", self.config_summary())
                case "Exit":
                    self.kill(0)
                case "Run dataset generation":
                    break
        
        start = time.perf_counter()
        self.ui.rule("JDEX Pipeline")
        self.ui.subrule("Initial Configuration and Safety Checks")
        self.ui.info("Starting JDEX Dataset Generation Suite")

        # ----------------------------------
        # MAKE BASE WORKING FOLDER 
        # ----------------------------------

        if self.cwd.exists():
            shutil.rmtree(self.cwd)
        self.cwd.mkdir(parents=True, exist_ok=True)

        self.ui.success(f"Base Folder Created at {self.cwd.absolute()}")

        # ----------------------------------
        # CONVERT SCHEMA TO BASE FORMAT
        # ----------------------------------

        self.ui.info(f"Converthing Schema File {self.config.paths.schema.absolute()} to OWL format")
        self.reasoner.conversion(self.config.paths.schema, self.cwd / pc.ONTOLOGY, format="owl", verbose=self.config.verbose)
        self.ui.success(f"Temporary Conversion saved as {(self.cwd / pc.ONTOLOGY).absolute()}")

        self.ui.info(f"Converthing Assertions File {self.config.paths.data.absolute()} to OWL format")
        self.reasoner.conversion(self.config.paths.data, self.cwd / pc.ASSERTIONS)
        self.ui.success(f"Temporary Conversion saved as {(self.cwd / pc.ASSERTIONS).absolute()}")


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
                    self.ui.success("No Unsatisfiable Classes / Object Properties Found")
                else:
                    self.ui.warning(f"Reasoning services cannot be activated on ontologies with unsatisfiable classes / roles. Unsatisfiable classes found: [{unsatifiable_classes}]. Please run with 'filter_unsatisfiable':true. """)
                    confirm = self.ui.confirm("Want to run Unsatisfiable URIs Removal Now?")
                    if confirm:
                        self.filter_unsatisfiable()
                    else:
                        self.kill(1)
        else:
            self.filter_unsatisfiable()


        # -----------------------------------
        # SUBFOLDERS GENERATIONS
        # ----------------------------------


        (self.cwd / "abox").mkdir(parents=True, exist_ok=True)
        self.ui.success("TBox Subfolder created")

        if self.config.reasoning.decomposition.tbox:
            (self.cwd / "tbox").mkdir(parents=True, exist_ok=True)
            self.ui.success("TBox Subfolder created")

        if self.config.reasoning.decomposition.rbox:
            (self.cwd / "rbox").mkdir(parents=True, exist_ok=True)
            self.ui.success("RBox Subfolder created")

        if self.config.split.enabled:
            (self.cwd / "abox" / "splits").mkdir(parents=True, exist_ok=True)
            self.ui.success("Split Subfolder created")

        if self.config.post_processing.id_mapping:
            (self.cwd / "mappings").mkdir(parents=True, exist_ok=True)
            self.ui.success("ID Mappings Subfolder created")

       

        # -----------------------------------
        # TBOX / RBOX Materialization
        # ----------------------------------

        if self.config.reasoning.materialization.enabled:
            self.ui.subrule("Materialization of Schema Axioms")
            self.ui.info("Running Materialization Using HermiT (Robot)")
            self.ui.info(f"Using Axiom Generators: {self.config.reasoning.materialization.axioms}")
            self.reasoner.materialization(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, axioms=self.config.reasoning.materialization.axioms, verbose=self.config.verbose, safety_check=False)
            self.ui.success("Materialization Completed")


        # -----------------------------------
        # ABox Check and Filtering
        # ----------------------------------


        self.ui.subrule("Assertions Checks and Filtering")

        self.ui.info("Loading Assertions in Memory")
        assertions = Graph()
        assertions.parse(self.cwd / pc.ASSERTIONS)
        self.ui.success(f"Loaded {len(assertions)} triples in memory")

        self.ui.info("Loading Schema in Memory")
        schema = Graph()
        schema.parse(self.cwd / pc.ONTOLOGY)
        self.ui.success(f"Loaded {len(schema)} schema triples in memory")

        

        self.ui.info("Filtering Object Property Assertions and Class Assertions")
        self.ui.info("NamedIndividuals also defined as Classes will be removed")
        self.ui.info("ObjectProperties also defined as DatatypeProperties will be removed")

        op_triples = Graph()
        ca_triples = Graph()

        individuals = set()
        classes = set()
        object_properties = set()

        null_individuals = set()
        null_object_properties = set()

        for s,p,o in self.ui.progress(assertions, "Filtering Assertions", total=len(assertions)):
            if (s, RDF.type, OWL.NamedIndividual) in assertions and (p, RDF.type, OWL.ObjectProperty) in schema and (o, RDF.type, OWL.NamedIndividual) in assertions:
            
                if s not in individuals and (s, RDF.type, OWL.Class) in schema:
                    null_individuals.add(s)
                    continue
                else:
                    individuals.add(s)
                
                if o not in individuals and (o, RDF.type, OWL.Class) in schema:
                    null_individuals.add(o)
                    continue
                else:
                    individuals.add(o)

                if p not in object_properties and (p, RDF.type, OWL.DatatypeProperty) in schema:
                    null_object_properties.add(p)
                    continue
                else:
                    object_properties.add(p)

                op_triples.add((s,p,o))

        
            elif (s, RDF.type, OWL.NamedIndividual) in assertions and (p == RDF.type) and (o, RDF.type, OWL.Class) in schema:

                if s not in individuals and (s, RDF.type, OWL.Class) in schema:
                    null_individuals.add(s)
                    continue
                else:
                    individuals.add(s)
                
                ca_triples.add((s,p,o))
                classes.add(o)

        del assertions

        self.ui.panel(
            title="Assertions Overview",
            data=[
                ("Individuals Found", len(individuals)),
                ("Object Properties Found", len(object_properties)),
                ("Classes Found", len(classes)),
                ("Object Property Assertions", len(op_triples)),
                ("Class Assertions", len(ca_triples)),
            ]
        )

        self.ui.panel(title="Removed Overview", data=[
            ("Individuals Removed", len(null_individuals) ),
            ("Object Properties Removed", len(null_object_properties))
        ])

        self.ui.success("Assertions Filtered Successfully")


        # -----------------------------------
        # Machine Learning Pre Processing
        # ----------------------------------

        
        self.ui.subrule("Machine Learning Pre-Processing")

        if self.config.split.enabled:

            self.ui.info("Splitting Object Property Assertions in Train/Test/Val")

            triples = TriplesFactory.from_labeled_triples(np.array(op_triples))

            if self.config.split.transductive:

                self.ui.info(f"Splitting with Transductive Setting using {CoverageSplitter}")
                self.ui.info(f"Using Ratio {self.config.split.train_percent}/{self.config.split.validation_percent}/{self.config.split.test_percent}")

                train_ratio = self.config.split.train_percent / 100
                valid_ratio = self.config.split.validation_percent / 100


                train, valid, test = triples.split(
                    ratios=[train_ratio, valid_ratio],
                    random_state=42,
                    method=CoverageSplitter(),
                )

                self.ui.panel(f"Splitting Overview", data=[
                    ("Train Triples", train.num_triples),
                    ("Validation Triples", valid.num_triples),
                    ("Test Triples" , test.num_triples)
                ])

                self.ui.success("Machine Learning Splits Created Successfully")

            else:
                self.ui.error("Inductive Splits are not supported yet, process will be terminated")
                self.kill(1)
            
            if self.config.split.test_leakage_filtering.enabled:

                self.ui.info("Checking and Filtering Test Leakage")
                train, valid, test = unleak(
                    train,
                    valid,
                    test,
                    n=None,
                    minimum_frequency=self.config.split.test_leakage_filtering.minimum_frequency,
                )

                self.ui.panel(f"Leakage Filtered Splitting Overview", data=[
                    ("Train Triples", train.num_triples),
                    ("Validation Triples", valid.num_triples),
                    ("Test Triples" , test.num_triples)
                ])
                
                self.ui.success("Leakage Filtering Successfull")


                self.ui.info(f"Serializing Split in {(self.cwd / pc.SPLITS).absolute()}")

                targets = [
                    (self.cwd / pc.RDF_TRAIN, train.triples),
                    (self.cwd / pc.RDF_VALID, valid.triples),
                    (self.cwd / pc.RDF_TEST, test.triples)
                ]

                for path, split in targets:
                    with open(path, "w") as split_file:
                        for triple in split:
                            outstr = f"<{URIRef(triple[0])}> <{URIRef(triple[1])}> <{URIRef(triple[2])}> .\n"
                            split_file.write(outstr)

                    self.ui.success(f"{path.name.split(".")[0].capitalize()} split serialized at {(path).absolute()}")

        self.ui.info("Serialization of Object Property Assertions Started")
        self.ui.info(f"Object Property Assertions will be saved at {self.cwd / pc.RDF_TRIPLES}") 

        if self.config.split.enabled:
            cmd = ["cat"] + [str(f) for f in list((self.cwd / pc.SPLITS).glob("*.nt"))]
            with open(self.cwd / pc.RDF_TRIPLES, "w") as f_out:
                result = subprocess.run(cmd, stdout=f_out)
                if result.returncode != 0:
                    self.ui.error("Unexpected Error during split file concatenation")
                    self.kill(1)

        else:    
            op_triples.serialize(self.cwd / pc.RDF_TRIPLES, format="ntriples")


        self.ui.success("Object Property Assertions Saved")

        # -----------------------------------
        # Individuals Serialization
        # ----------------------------------


        self.ui.subrule("Individuals Serialization")

        self.ui.info("Serializing Individual Informations")

        out_graph = Graph()
        for ind in individuals:
            out_graph.add((ind, RDF.type, OWL.NamedIndividual))
        out_graph.serialize(self.cwd / pc.INDIVIDUALS, format="xml")
        self.reasoner.conversion(self.cwd / pc.INDIVIDUALS, self.cwd / pc.INDIVIDUALS, format="owl")

        self.ui.success(f"Individuals serialized at {self.cwd / pc.INDIVIDUALS}")

        # -----------------------------------
        # Class Assertions Serialization
        # ----------------------------------


        self.ui.subrule("Class Assertions Serialization")

        self.ui.info("Serializing Class Assertions")

        ca_triples.serialize(self.cwd / pc.RDF_CLASS_ASSERTIONS, format="xml")
        self.reasoner.conversion(self.cwd / pc.RDF_CLASS_ASSERTIONS, self.cwd / pc.RDF_CLASS_ASSERTIONS, format="owl")

        self.ui.success(f"Class Assertions serialized at {self.cwd / pc.RDF_CLASS_ASSERTIONS}")

        # -----------------------------------
        # Temporary Files removal
        # ----------------------------------

        (self.cwd / pc.ASSERTIONS).unlink(missing_ok=True)

        # -----------------------------------
        # Consistency Check and Justification
        # ----------------------------------

        if self.config.reasoning.realization.enabled:

            self.ui.subrule("Consistency Check and Justification of Inconsistencies")
            self.ui.info("Realization Enabled, Checking KB Consistency")
            self.ui.info(f"Merging Assertions with Schema at {self.cwd / pc.KNOWLEDGE_GRAPH}")

            self.reasoner.merging(input_ontologies=[\
                self.cwd / pc.ONTOLOGY,
                self.cwd / pc.RDF_TRIPLES,
                self.cwd / pc.INDIVIDUALS,
                self.cwd / pc.RDF_CLASS_ASSERTIONS
                ],
                output=self.cwd / pc.KNOWLEDGE_GRAPH,
                verbose=self.config.verbose
                )
            consistent = self.reasoner.consistency(self.cwd / pc.KNOWLEDGE_GRAPH, verbose=self.config.verbose)

            if consistent:
                self.ui.success("Knowledge Graph Consistent")
            else:
                self.ui.warning("Knowledge Graph is Inconsistent, cannot run realization services")
                confirm = self.ui.confirm("Want to run justification using Pellet?")
                if confirm:
                    self.ui.info("Running Justification on Target Knowledge Graph")
                    justification = self.reasoner.justification(input=self.cwd / pc.KNOWLEDGE_GRAPH, output=self.cwd / "justification.ttl", verbose=self.config.verbose)
                    self.ui.list("Inconsistency Justification", justification)
                    self.ui.success(f"Justification saved at {self.cwd / "justification.ttl"}")
                    self.kill(0)

        # -----------------------------------
        # Class Assertions Realization
        # ----------------------------------

        if self.config.reasoning.realization.enabled:
            self.ui.subrule("Realization Reasoning Services")
            self.ui.info("Running Realization (Konclude) on target Knowledge Base")
            self.reasoner.realization(
                input=self.cwd / pc.KNOWLEDGE_GRAPH,
                output=self.cwd / pc.RDF_CLASS_ASSERTIONS,
                verbose=self.config.verbose
            )
            self.reasoner.conversion(self.cwd / pc.RDF_CLASS_ASSERTIONS, self.cwd / pc.RDF_CLASS_ASSERTIONS, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Realiation Output stored at {self.cwd / pc.RDF_CLASS_ASSERTIONS}")


        # -----------------------------------
        # Schema Modularization
        # ----------------------------------

        if self.config.reasoning.modularization.enabled:
            self.ui.subrule("Schema Modularization")
            self.ui.info("Running Signature-Based Schema Modularization (PROMPTFACTOR) on target Knowledge Base")

            if self.config.reasoning.realization.enabled:
                self.ui.info("Re-Loading Class Assertions in Memory after Realization")
                ca_triples = Graph()
                ca_triples.parse(self.cwd / pc.RDF_CLASS_ASSERTIONS)
                self.ui.success("Realized class assertions loaded")
                classes = set(ca_triples.subjects(RDF.type, OWL.Class))

            if self.config.split.enabled:
                self.ui.info("Re-Loading Object Property Assertions in Memory after Machine Learning Processing")
                op_triples = Graph()
                op_triples.parse(self.cwd / pc.RDF_TRIPLES)
                self.ui.success("Object Property Assertions loaded")
                object_properties = set(op_triples.predicates(None, None))

            seed_obj_props = object_properties
            seed_classes = classes

            self.ui.panel("Modularization Signature", data=[
                ("Seed Classes", len(seed_classes)),
                ("Seed Object Properties", len(seed_obj_props))
            ])

            modularizer = SignatureModularizer(schema, seed_classes | seed_obj_props)
            modularized_schema = modularizer.modularize(verbose=False)
            modularized_schema.serialize(self.cwd / pc.ONTOLOGY)
            self.reasoner.conversion(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, format="owl", verbose=self.config.verbose)

            self.ui.panel("Modularization Statistics", data=[
                ("Schema Axioms", len(schema)),
                ("Modularized Schema Axioms", len(modularized_schema))
            ])

            self.ui.success(f"Modularization successfull, stored at {self.cwd / pc.ONTOLOGY}")
            schema = modularized_schema

        # -----------------------------------
        # Schema Decomposition
        # ----------------------------------

        decomposer = SchemaDecomposer(schema)

        if self.config.reasoning.decomposition.tbox:

            self.ui.subrule("TBox Decomposition")

            self.ui.info("Running Decomposition of Schema Axioms / Class Definition")
            d_schema = decomposer._schema_decompose(verbose=False)
            d_schema.serialize(self.cwd / pc.RDF_SCHEMA, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_SCHEMA, self.cwd / pc.RDF_SCHEMA, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Schema Decomposition stored at {self.cwd / pc.RDF_SCHEMA}")
           
            self.ui.info("Running Decomposition of Schema Taxonomy")
            d_taxonomy = decomposer._taxonomy_decompose(verbose=False)
            d_taxonomy.serialize(self.cwd / pc.RDF_TAXONOMY, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_TAXONOMY, self.cwd / pc.RDF_TAXONOMY, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Taxonomy Decomposition stored at {self.cwd / pc.RDF_TAXONOMY}")

        
        if self.config.reasoning.decomposition.rbox:
            self.ui.subrule("RBox Decomposition")
            self.ui.info("Running Decomposition on Roles Definitions and Axioms")
            d_roles = decomposer._rbox_decompose(verbose=False)
            d_roles.serialize(self.cwd / pc.RDF_OBJ_PROP, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_OBJ_PROP, self.cwd / pc.RDF_OBJ_PROP, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Roles Decomposition stored at {self.cwd / pc.RDF_OBJ_PROP}")

        # -----------------------------------
        # Full KG Reconstruction and Safety Checks
        # ----------------------------------

        self.ui.subrule("Compolete Knowledge Graph Reconstruction and Safety Checks")
        self.ui.info(f"Merging full KG at {self.cwd / pc.KNOWLEDGE_GRAPH}")

        self.reasoner.merging(input_ontologies=[\
                self.cwd / pc.ONTOLOGY,
                self.cwd / pc.RDF_TRIPLES,
                self.cwd / pc.INDIVIDUALS,
                self.cwd / pc.RDF_CLASS_ASSERTIONS
                ],
                output=self.cwd / pc.KNOWLEDGE_GRAPH,
                verbose=self.config.verbose
        )

        self.ui.success(f"Mergin successful")
        self.ui.info(F"Constistency check on full KG")
        consistent = self.reasoner.consistency(self.cwd / pc.KNOWLEDGE_GRAPH, verbose=self.config.verbose)

        if consistent:
            self.ui.success("Knowledge Graph Consistent")
        else:
            self.ui.warning("Knowledge Graph is Inconsistent")
            confirm = self.ui.confirm("Want to run justification using Pellet?")
            if confirm:
                self.ui.info("Running Justification on Target Knowledge Graph")
                justification = self.reasoner.justification(input=self.cwd / pc.KNOWLEDGE_GRAPH, output=self.cwd / "justification.ttl", verbose=self.config.verbose)
                self.ui.list("Inconsistency Justification", justification)
                self.ui.success(f"Justification saved at {self.cwd / "justification.ttl"}")
                self.kill(1)

        end = time.perf_counter()
        elapsed = end - start
        self.ui.success(f"JDEX Pipeline Complete in {elapsed:4.2f} seconds. Closing Process.")
        self.kill(0)



if __name__ == "__main__":
    jdex = JDEX.from_json("/home/navis/Devel/PhD/kg-saf/kgsaf_data/configurations/DBPEDIA-100K-BASE.json")
    jdex.run()

