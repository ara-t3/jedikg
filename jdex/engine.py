#!/usr/bin/env python3

import gc
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import psutil
from pykeen.triples import TriplesFactory
from pykeen.triples.leakage import unleak
from pykeen.triples.splitting import CoverageSplitter
from rdflib import OWL, RDF, Graph
from rdflib.term import URIRef

import jdex.utils.conventions.paths as pc
from jdex.cli import CLI
from jdex.config import JDEXConfig
from jdex.owl.decomposition import SchemaDecomposer
from jdex.owl.modularization import (ALCProfileFilter, ELProfileFilter,
                                     SignatureModularizer)
from jdex.owl.reasoning import Reasoner
from jdex.utils.postprocessing import IDMapper, OWLConverter, TSVConverter

process = psutil.Process(os.getpid())

def mem_mb():
    return process.memory_info().rss / (1024 ** 2)

class JDEX:

    def __init__(self, config: JDEXConfig):
        self.config = config
        self.ui = CLI(self.config.verbose)
        self.ontology_node = URIRef("http://example.org/")
        self.cwd = (self.config.paths.output / self.config.dataset_name).absolute()
        self.reasoner = Reasoner(
                reasoners_path=Path("./reasoners/unpack").absolute(),
                java8_path=self.config.reasoning.java_8_home,
                java11_path=self.config.reasoning.java_11_home,
                java_max_ram=20
        ) 
        
    def kill(self, code: int = 1):
        self.ui.rule("JDEX Execution Stopped")
        sys.exit(code)

    def startup_screen(self):
        self.ui.logo()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ui.error("Forcing Shut Down. Closing Process")
        gc.collect()

        
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
            "Select an action:",
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
        self.ui.info(f"Starting unsatisfiable class and role removal using {self.config.reasoning.satisfiability.reasoner.upper()}")
        while True:
            unsatifiable_classes = self.reasoner.satisfiability(
                input_ontology=self.cwd / pc.ONTOLOGY,
                verbose=self.config.verbose,
                reasoner=self.config.reasoning.satisfiability.reasoner,
            )
            self.ui.info(f"Unsatisfiability cleanup step {sc_it_number}: found {len(unsatifiable_classes)} unsatisfiable URI(s)")
            if unsatifiable_classes:
                self.ui.info(f"Unsatisfiable URIs detected: {unsatifiable_classes}")
                self.reasoner.filtering(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, uris=unsatifiable_classes, verbose=self.config.verbose)
                sc_it_number +=1
                tot_removed += len(unsatifiable_classes)
            else:
                self.ui.success(f"Unsatisfiability cleanup completed: removed {tot_removed} URI(s) across {sc_it_number} step(s)")
                return sc_it_number, tot_removed
            
    def consistency_check(self):
        if self.config.reasoning.consistency.convert_ntriples:
            self.ui.info("Converting the knowledge graph to N-Triples format for consistency checking")
            fg = Graph()
            fg.parse(self.cwd / pc.KNOWLEDGE_GRAPH)
            fg.serialize(self.cwd / "knowledge_graph.nt", format="ntriples", encoding="UTF-8")
            self.ui.info(f"N-Triples knowledge graph saved to {self.cwd / 'knowledge_graph.nt'}")
            return self.reasoner.consistency(self.cwd / "knowledge_graph.nt", verbose=self.config.verbose)
        else:
            return self.reasoner.consistency(self.cwd / pc.KNOWLEDGE_GRAPH, verbose=self.config.verbose)
    
    
    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            self.ui.error("Forcing Shut Down. Closing Process")
            gc.collect()

    def _run(self):

        self.startup_screen()

        if self.config.interactive_shell:
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
        self.ui.subrule("Initial Setup and Validation")
        self.ui.info("Starting the JDEX dataset generation pipeline")

        # ----------------------------------
        # MAKE BASE WORKING FOLDER 
        # ----------------------------------

        if self.cwd.exists():
            shutil.rmtree(self.cwd)
        self.cwd.mkdir(parents=True, exist_ok=True)

        self.ui.success(f"Working directory created at {self.cwd.absolute()}")

        # ----------------------------------
        # CONVERT SCHEMA TO BASE FORMAT
        # ----------------------------------

        self.ui.info(f"Converting schema file {self.config.paths.schema.absolute()} to OWL format")
        self.reasoner.conversion(self.config.paths.schema, self.cwd / pc.ONTOLOGY, format="owl", verbose=self.config.verbose)
        self.ui.success(f"Temporary schema conversion saved to {(self.cwd / pc.ONTOLOGY).absolute()}")

        self.ui.info(f"Converting assertions file {self.config.paths.data.absolute()} to OWL format")
        self.reasoner.conversion(self.config.paths.data, self.cwd / pc.ASSERTIONS, format="owl", verbose=self.config.verbose)
        self.ui.success(f"Temporary assertions conversion saved to {(self.cwd / pc.ASSERTIONS).absolute()}")

        # -----------------------------------
        # CHECK APPLICABILITY OF REASONING SERVICES
        # ----------------------------------
        if self.config.description_logic_profile:
            if self.config.description_logic_profile.lower() in {"alc", "el"}:
                profile = self.config.description_logic_profile.lower()
                self.ui.subrule(f"Description Logic Profile Filtering: {profile.upper()}")

                g = Graph()
                g.parse(self.cwd / pc.ONTOLOGY)

                match profile:
                    case "el":
                        utility = ELProfileFilter(g)
                    case "alc":
                        utility = ALCProfileFilter(g)

                pg = utility.filter_graph()

                self.ui.panel(f"{profile.upper()} Profile Ontology", data=[
                    ("Original axioms", len(g)),
                    (f"{profile.upper()}-compatible axioms", len(pg))
                ])

                pg.serialize(self.cwd / pc.ONTOLOGY, format="xml")

                self.reasoner.conversion(
                    self.cwd / pc.ONTOLOGY,
                    self.cwd / pc.ONTOLOGY
                )

                self.ui.success("Description logic profile filtering completed successfully")


        # -----------------------------------
        # CHECK APPLICABILITY OF REASONING SERVICES
        # ----------------------------------

        if (not self.config.reasoning.satisfiability.filter_unsatisfiable):
            if  (self.config.reasoning.materialization or self.config.reasoning.realization):
                if self.config.interactive_shell:
                    confirm = self.ui.confirm("Reasoning services are enabled, but unsatisfiable classes and roles are not being filtered. Would you like to run a satisfiability check?")
                    if confirm:
                        self.ui.info(f"Running satisfiability analysis with {self.config.reasoning.satisfiability.reasoner.upper()} (ROBOT)")
                        unsatifiable_classes = self.reasoner.satisfiability(
                            input_ontology=self.config.paths.schema, 
                            reasoner=self.config.reasoning.satisfiability.reasoner,
                            verbose=self.config.verbose
                        )
                        if not(unsatifiable_classes):
                            self.ui.success("No unsatisfiable classes or object properties were found")
                        else:
                            self.ui.warning(f"Reasoning services cannot run safely on ontologies with unsatisfiable classes or roles. Detected unsatisfiable entities: [{unsatifiable_classes}]. Please run with 'filter_unsatisfiable': true.")
                            confirm = self.ui.confirm("Would you like to remove unsatisfiable URIs now?")
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
        self.ui.success("ABox subfolder created")

        if self.config.reasoning.decomposition.tbox:
            (self.cwd / "tbox").mkdir(parents=True, exist_ok=True)
            self.ui.success("TBox subfolder created")

        if self.config.reasoning.decomposition.rbox:
            (self.cwd / "rbox").mkdir(parents=True, exist_ok=True)
            self.ui.success("RBox subfolder created")

        if self.config.split.enabled:
            (self.cwd / "abox" / "splits").mkdir(parents=True, exist_ok=True)
            self.ui.success("Split subfolder created")

        """
        if self.config.post_processing.id_mapping:
            (self.cwd / "mappings").mkdir(parents=True, exist_ok=True)
            self.ui.success("ID Mappings Subfolder created")
        """
       

        # -----------------------------------
        # TBOX / RBOX Materialization
        # ----------------------------------

        if self.config.reasoning.materialization.enabled:
            self.ui.subrule("Schema Axiom Materialization")
            self.ui.info(f"Running materialization with {self.config.reasoning.materialization.reasoner} (ROBOT)")
            self.ui.info(f"Using axiom generators: {self.config.reasoning.materialization.axioms}")
            self.reasoner.materialization(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, axioms=self.config.reasoning.materialization.axioms, verbose=self.config.verbose, safety_check=False, reasoner=self.config.reasoning.satisfiability.reasoner)
            self.ui.success("Schema materialization completed successfully")


        # -----------------------------------
        # ABox Check and Filtering
        # ----------------------------------


        self.ui.subrule("Assertion Validation and Filtering")

        self.ui.info("Loading assertions into memory")
        assertions = Graph()
        assertions.parse(self.cwd / pc.ASSERTIONS)
        self.ui.success(f"Loaded {len(assertions)} assertion triple(s)")

        self.ui.info("Loading schema into memory")
        schema = Graph()
        schema.parse(self.cwd / pc.ONTOLOGY)
        self.ui.success(f"Loaded {len(schema)} schema triple(s)")

        

        self.ui.info("Filtering object property assertions and class assertions")
        self.ui.info("Named individuals that are also declared as classes will be removed")
        self.ui.info("Object properties that are also declared as datatype properties will be removed")

        op_triples = Graph()
        ca_triples = Graph()

        ca_triples.add((self.ontology_node, RDF.type, OWL.Ontology))

        individuals = set()
        classes = set()
        object_properties = set()

        null_individuals = set()
        null_object_properties = set()

        for s,p,o in self.ui.progress(assertions, "Filtering assertions", total=len(assertions)):
            if (s, RDF.type, OWL.NamedIndividual) in assertions and (p, RDF.type, OWL.ObjectProperty) in schema and (o, RDF.type, OWL.NamedIndividual) in assertions:
            
                if s not in individuals and (s, RDF.type, OWL.Class) in schema:
                    null_individuals.add((s, "Also declared as Class"))
                    continue
                else:
                    individuals.add(s)
                
                if o not in individuals and (o, RDF.type, OWL.Class) in schema:
                    null_individuals.add((s, "Also declared as Class"))
                    continue
                else:
                    individuals.add(o)

                if p not in object_properties and (p, RDF.type, OWL.DatatypeProperty) in schema:
                    null_object_properties.add((p, "Also declared as DatatypeProperty"))
                    continue
                else:
                    object_properties.add(p)

                op_triples.add((s,p,o))

        
            elif (s, RDF.type, OWL.NamedIndividual) in assertions and (p == RDF.type) and (o, RDF.type, OWL.Class) in schema:

                if s not in individuals and (s, RDF.type, OWL.Class) in schema:
                    null_individuals.add((s, "Also declared as Class"))
                    continue
                else:
                    individuals.add(s)
                
                ca_triples.add((s,p,o))
                classes.add(o)

        

        self.ui.panel(
            title="Assertions Overview",
            data=[
                ("Individuals found", len(individuals)),
                ("Object properties found", len(object_properties)),
                ("Classes found", len(classes)),
                ("Object property assertions", len(op_triples)),
                ("Class assertions", len(ca_triples)),
            ]
        )

        self.ui.panel(title="Removed Entities Overview", data=[
            ("Individuals removed", len(null_individuals) ),
            ("Object properties removed", len(null_object_properties))
        ])

        self.ui.success("Assertion filtering completed successfully")

        if null_individuals or null_object_properties:
            if self.config.interactive_shell:
                confirm = self.ui.confirm("Would you like to inspect the removed URIs?")
                if confirm:
                    if null_individuals:
                        self.ui.list("Removed Individuals", [f"{a} -> {b}" for a,b in null_individuals])
                    if null_object_properties:
                        self.ui.list("Removed Object Properties",  [f"{a} -> {b}" for a,b in null_object_properties])

        
        start_usage = mem_mb()
        self.ui.info("Memory cleanup: removing temporary assertion data from memory")
        del assertions
        del null_individuals
        del null_object_properties
        gc.collect()
        end_usage = mem_mb()
        self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage} MB")


        # -----------------------------------
        # Machine Learning Pre Processing
        # ----------------------------------

        
        self.ui.subrule("Machine Learning Preprocessing")

        if self.config.split.enabled:

            self.ui.info("Splitting object property assertions into train, validation, and test sets")

            triples = TriplesFactory.from_labeled_triples(np.array(op_triples))

            if self.config.split.transductive:

                self.ui.info(f"Using transductive splitting with {CoverageSplitter}")
                self.ui.info(f"Configured ratios: {self.config.split.train_percent}/{self.config.split.validation_percent}/{self.config.split.test_percent}")

                train_ratio = self.config.split.train_percent / 100
                valid_ratio = self.config.split.validation_percent / 100


                train, valid, test = triples.split(
                    ratios=[train_ratio, valid_ratio],
                    random_state=42,
                    method=CoverageSplitter(),
                )

                self.ui.panel(f"Split Overview", data=[
                    ("Train triples", train.num_triples),
                    ("Validation triples", valid.num_triples),
                    ("Test triples" , test.num_triples)
                ])

                self.ui.success("Dataset splits created successfully")

            else:
                self.ui.error("Inductive splits are not supported yet. The process will now stop")
                self.kill(1)
            
            if self.config.split.test_leakage_filtering.enabled:

                self.ui.info("Checking for and filtering test leakage")
                train, valid, test = unleak(
                    train,
                    valid,
                    test,
                    n=None,
                    minimum_frequency=self.config.split.test_leakage_filtering.minimum_frequency,
                )

                self.ui.panel(f"Leakage-Filtered Split Overview", data=[
                    ("Train triples", train.num_triples),
                    ("Validation triples", valid.num_triples),
                    ("Test triples" , test.num_triples)
                ])
                
                self.ui.success("Leakage filtering completed successfully")


                self.ui.info(f"Serializing splits to {(self.cwd / pc.SPLITS).absolute()}")

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

                    self.ui.success(f"{path.name.split('.')[0].capitalize()} split saved to {(path).absolute()}")

            start_usage = mem_mb()
            self.ui.info("Memory cleanup: removing temporary PyKEEN structures from memory")
            del train, valid, test, triples, targets
            gc.collect()
            end_usage = mem_mb()
            self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage:8.2f} MB")



        self.ui.info("Starting serialization of object property assertions")
        self.ui.info(f"Object property assertions will be written to {self.cwd / pc.RDF_TRIPLES}") 

        if self.config.split.enabled:
            cmd = ["cat"] + [str(f) for f in list((self.cwd / pc.SPLITS).glob("*.nt"))]
            with open(self.cwd / pc.RDF_TRIPLES, "w") as f_out:
                result = subprocess.run(cmd, stdout=f_out)
                if result.returncode != 0:
                    self.ui.error("Unexpected error while concatenating split files")
                    self.kill(1)

        else:    
            op_triples.serialize(self.cwd / pc.RDF_TRIPLES, format="ntriples")

        start_usage = mem_mb()
        self.ui.info("Memory cleanup: object property assertions are no longer needed in memory")
        del op_triples
        gc.collect()
        end_usage = mem_mb()
        self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage:8.2f} MB")


        self.ui.success("Object property assertions saved successfully")

        # -----------------------------------
        # Individuals Serialization
        # ----------------------------------


        self.ui.subrule("Individual Serialization")

        self.ui.info("Serializing individual declarations")

        out_graph = Graph()
        out_graph.add((self.ontology_node, RDF.type, OWL.Ontology))

        for ind in individuals:
            out_graph.add((ind, RDF.type, OWL.NamedIndividual))
        out_graph.serialize(self.cwd / pc.INDIVIDUALS, format="xml")
        self.reasoner.conversion(self.cwd / pc.INDIVIDUALS, self.cwd / pc.INDIVIDUALS, format="owl")

        self.ui.success(f"Individuals serialized to {self.cwd / pc.INDIVIDUALS}")

        start_usage = mem_mb()
        self.ui.info("Memory cleanup: temporary individual graph is no longer needed")
        del out_graph
        gc.collect()
        end_usage = mem_mb()
        self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage:8.2f} MB")

        # -----------------------------------
        # Class Assertions Serialization
        # ----------------------------------


        self.ui.subrule("Class Assertion Serialization")

        self.ui.info("Serializing class assertions")

        ca_triples.serialize(self.cwd / pc.RDF_CLASS_ASSERTIONS, format="xml")
        self.reasoner.conversion(self.cwd / pc.RDF_CLASS_ASSERTIONS, self.cwd / pc.RDF_CLASS_ASSERTIONS, format="owl")

        self.ui.success(f"Class assertions serialized to {self.cwd / pc.RDF_CLASS_ASSERTIONS}")

        start_usage = mem_mb()
        self.ui.info("Memory cleanup: class assertion graph is no longer needed")
        del ca_triples
        gc.collect()
        end_usage = mem_mb()
        self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage:8.2f} MB")

        # -----------------------------------
        # Temporary Files removal
        # ----------------------------------

        (self.cwd / pc.ASSERTIONS).unlink(missing_ok=True)

        # -----------------------------------
        # Consistency Check and Justification
        # ----------------------------------

        if self.config.reasoning.realization.enabled:

            self.ui.subrule("Consistency Check and Inconsistency Justification")
            self.ui.info("Realization is enabled, so the knowledge graph consistency will be checked first")
            self.ui.info(f"Merging schema and assertions into {self.cwd / pc.KNOWLEDGE_GRAPH}")

            self.reasoner.merging(input_ontologies=[\
                self.cwd / pc.ONTOLOGY,
                self.cwd / pc.RDF_TRIPLES,
                self.cwd / pc.INDIVIDUALS,
                self.cwd / pc.RDF_CLASS_ASSERTIONS
                ],
                output=self.cwd / pc.KNOWLEDGE_GRAPH,
                verbose=self.config.verbose
                )
            
            consistent = self.consistency_check()

            if consistent:
                self.ui.success("Knowledge graph is consistent")
            else:
                self.ui.warning("Knowledge graph is inconsistent; realization cannot proceed")
                if self.config.interactive_shell:
                    confirm = self.ui.confirm("Would you like to generate an inconsistency justification using Pellet?")
                    if confirm:
                        self.ui.info("Running justification on the target knowledge graph")
                        justification = self.reasoner.justification(input=self.cwd / pc.KNOWLEDGE_GRAPH, output=self.cwd / "justification.owl", verbose=self.config.verbose)
                        self.ui.list("Inconsistency Justification", justification)
                        self.ui.success(f"Justification saved to {self.cwd / 'justification.ttl'}")
                        self.kill(0)



        # -----------------------------------
        # Class Assertions Realization
        # ----------------------------------

        if self.config.reasoning.realization.enabled:
            self.ui.subrule("Class Assertion Realization")
            self.ui.info(f"Running realization with {self.config.reasoning.realization.reasoner} on the target knowledge base")
   
            self.reasoner.realization(
                    input=self.cwd / pc.KNOWLEDGE_GRAPH,
                    output=self.cwd / pc.RDF_CLASS_ASSERTIONS,
                    verbose=self.config.verbose,
                    reasoner=self.config.reasoning.realization.reasoner
                )
               
            if self.config.reasoning.realization.reasoner in ["hermit", "elk"]:

                self.ui.info("Filtering class assertions from the full realization output")
                in_graph = Graph()
                in_graph.parse(self.cwd / pc.RDF_CLASS_ASSERTIONS)
                out_graph = Graph()

                for s,p,o in self.ui.progress(in_graph, "Filtering class assertions", total=len(in_graph)):
                    if s in individuals and p == RDF.type:
                        out_graph.add((s,p,o))

                out_graph.serialize(self.cwd / pc.RDF_CLASS_ASSERTIONS, format="xml")
                self.ui.success("Class assertion filtering completed")
                del in_graph
                del out_graph
                del individuals
                gc.collect()

            
            self.reasoner.conversion(self.cwd / pc.RDF_CLASS_ASSERTIONS, self.cwd / pc.RDF_CLASS_ASSERTIONS, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Realization output saved to {self.cwd / pc.RDF_CLASS_ASSERTIONS}")


        # -----------------------------------
        # Schema Modularization
        # ----------------------------------

        if self.config.reasoning.modularization.enabled:
            self.ui.subrule("Schema Modularization")
            self.ui.info("Running signature-based schema modularization (PROMPTFACTOR) on the target knowledge base")

            if self.config.reasoning.realization.enabled:
                self.ui.info("Reloading class assertions after realization")
                ca_triples = Graph()
                ca_triples.parse(self.cwd / pc.RDF_CLASS_ASSERTIONS)
                self.ui.success("Realized class assertions loaded")
                classes = set(ca_triples.subjects(RDF.type, OWL.Class))
                del ca_triples
                gc.collect()


            if self.config.split.enabled:
                self.ui.info("Reloading object property assertions after machine learning preprocessing")
                op_triples = Graph()
                op_triples.parse(self.cwd / pc.RDF_TRIPLES)
                self.ui.success("Object property assertions loaded")
                object_properties = set(op_triples.predicates(None, None))
                del op_triples
                gc.collect()

            seed_obj_props = object_properties
            seed_classes = classes

            self.ui.panel("Modularization Signature", data=[
                ("Seed classes", len(seed_classes)),
                ("Seed object properties", len(seed_obj_props))
            ])

            modularizer = SignatureModularizer(schema, seed_classes | seed_obj_props)
            modularized_schema = modularizer.modularize(verbose=False)
            modularized_schema.add((self.ontology_node, RDF.type, OWL.Ontology))
            modularized_schema.serialize(self.cwd / pc.ONTOLOGY)
            self.reasoner.conversion(self.cwd / pc.ONTOLOGY, self.cwd / pc.ONTOLOGY, format="owl", verbose=self.config.verbose)

            self.ui.panel("Modularization Statistics", data=[
                ("Schema axioms", len(schema)),
                ("Modularized schema axioms", len(modularized_schema))
            ])

            self.ui.success(f"Schema modularization completed successfully and saved to {self.cwd / pc.ONTOLOGY}")
            
            start_usage = mem_mb()
            self.ui.info("Memory cleanup: removing the original non-modularized schema from memory")
            del schema
            gc.collect()
            end_usage = mem_mb()
            self.ui.success(f"Memory cleanup completed: freed {start_usage - end_usage:8.2f} MB")


            schema = modularized_schema

        # -----------------------------------
        # Schema Decomposition
        # ----------------------------------

        decomposer = SchemaDecomposer(schema)

        if self.config.reasoning.decomposition.tbox:

            self.ui.subrule("TBox Decomposition")

            self.ui.info("Decomposing schema axioms and class definitions")
            d_schema = decomposer._schema_decompose(verbose=False)
            d_schema.add((self.ontology_node, RDF.type, OWL.Ontology))
            d_schema.serialize(self.cwd / pc.RDF_SCHEMA, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_SCHEMA, self.cwd / pc.RDF_SCHEMA, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Schema decomposition saved to {self.cwd / pc.RDF_SCHEMA}")
            del d_schema
            gc.collect()
           
            self.ui.info("Decomposing schema taxonomy")
            d_taxonomy = decomposer._taxonomy_decompose(verbose=False)
            d_taxonomy.add((self.ontology_node, RDF.type, OWL.Ontology))
            d_taxonomy.serialize(self.cwd / pc.RDF_TAXONOMY, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_TAXONOMY, self.cwd / pc.RDF_TAXONOMY, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Taxonomy decomposition saved to {self.cwd / pc.RDF_TAXONOMY}")
            del d_taxonomy
            gc.collect()

        
        if self.config.reasoning.decomposition.rbox:
            self.ui.subrule("RBox Decomposition")
            self.ui.info("Decomposing role definitions and role axioms")
            d_roles = decomposer._rbox_decompose(verbose=False)
            d_roles.add((self.ontology_node, RDF.type, OWL.Ontology))
            d_roles.serialize(self.cwd / pc.RDF_OBJ_PROP, format="xml")
            self.reasoner.conversion(self.cwd / pc.RDF_OBJ_PROP, self.cwd / pc.RDF_OBJ_PROP, format="owl", verbose=self.config.verbose)
            self.ui.success(f"Role decomposition saved to {self.cwd / pc.RDF_OBJ_PROP}")
            del d_roles
            gc.collect()

        # -----------------------------------
        # Full KG Reconstruction and Safety Checks
        # ----------------------------------

        self.ui.subrule("Complete Knowledge Graph Merging and Consistency Checks")
        self.ui.info(f"Merging the full knowledge graph into {self.cwd / pc.KNOWLEDGE_GRAPH}")

        self.reasoner.merging(input_ontologies=[\
                self.cwd / pc.ONTOLOGY,
                self.cwd / pc.RDF_TRIPLES,
                self.cwd / pc.INDIVIDUALS,
                self.cwd / pc.RDF_CLASS_ASSERTIONS
                ],
                output=self.cwd / pc.KNOWLEDGE_GRAPH,
                verbose=self.config.verbose
        )

        self.ui.success("Knowledge graph merge completed successfully")
        self.ui.info("Running consistency check on the full knowledge graph")


        consistent = self.consistency_check()



        if consistent:
            self.ui.success("Knowledge graph is consistent")
        else:
            self.ui.warning("Knowledge graph is inconsistent")
            if self.config.interactive_shell:
                confirm = self.ui.confirm("Would you like to generate an inconsistency justification using Pellet?")
                if confirm:
                    self.ui.info("Running justification on the target knowledge graph")
                    justification = self.reasoner.justification(input=self.cwd / pc.KNOWLEDGE_GRAPH, output=self.cwd / "justification.ttl", verbose=self.config.verbose)
                    self.ui.list("Inconsistency Justification", justification)
                    self.ui.success(f"Justification saved to {self.cwd / 'justification.ttl'}")
                    self.kill(1)


        # -----------------------------------
        # Post Processing Utilities
        # ----------------------------------

        if self.config.post_processing.id_mapping or self.config.post_processing.json_conversion or self.config.post_processing.tsv_conversion:
            self.ui.subrule("Machine Learning Postprocessing")

        if self.config.post_processing.id_mapping:
            self.ui.info("Computing ID mappings")
            utility = IDMapper(self.cwd)
            utility.map_to_id()
            utility.serialize()
            self.ui.success("ID mapping completed successfully")

        if self.config.post_processing.json_conversion:
            self.ui.info("Computing JSON conversion")
            utility = OWLConverter(self.cwd)
            utility.preprocess(verbose=False)
            utility.serialize()
            self.ui.success("JSON conversion completed successfully")

        if self.config.post_processing.tsv_conversion:
            self.ui.info("Computing TSV conversion")
            utility = TSVConverter(self.cwd)
            utility.convert()
            utility.serialize()
            self.ui.success("TSV conversion completed successfully")

        end = time.perf_counter()
        elapsed = end - start
        self.ui.success(f"JDEX pipeline completed in {elapsed:4.2f} seconds. Shutting down cleanly")
        self.ui.rule("Process Terminated")




