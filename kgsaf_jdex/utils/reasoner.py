#!/usr/bin/env python3
"""
CONSISTENCY CHECK (Konclude)
If no abox is present, will always ouput TRUE

SATISFIABILITY CHECK (HermiT)
Does not work with uncosistent ontology due to Robot limitations, adivsed to use only on the schema part of the ontology (whitout the assertions)

REALIZATION (Konclude)
Writes in a new file all the class assertions. Note, if the ontology is inconsistent or unsatisfiable, it will still work, but it will output entities as membership to nothing for all entitites 

MATERIALIZATION (HermiT)
Does not work with unconsistent / unsatisfiable ontologies due to Robot limitatios, advides to use only on the schema part of the ontology (whitout the assertions)

CONVERSION (No Reasoner)
No notes

FILTER (Robot)
Removes unsatisfiable uris 




"""



from pathlib import Path
import sys
import subprocess
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace
from rdflib.namespace import split_uri
from rdflib.term import URIRef
import re
import time

sys.path.append(str(Path.cwd().parent))

class Reasoner:
    def __init__(self, reasoners_path: Path):
        self.konclude = reasoners_path / "konclude" / "Konclude"
        self.robot = reasoners_path / "robot" / "robot.jar"
        self.temp_dir = reasoners_path / "temp"

    def check_result(self, result, label, t):
        """
        Check the result of a subprocess execution. Prints whether the command completed successfully based on the return code.

        Args:
            result (subprocess.CompletedProcess): Result returned by subprocess.run.
        """
    
        if result.returncode == 0:
            print(f"Reasoning: {label} - completed successfully in {t:4.3f}s!")
        else:
            print(f"Reasoning: {label} -  failed with return code:", result.returncode)


    def satisfiability(self, input_ontology: Path, log: bool = True) -> list:

        onto = Path(input_ontology)

        if not self.consistency(input_ontology, log=False):
            raise Exception("Cannot Run Satisfiabiality on Inconsistent Ontologies due to Robot Limitations")
            
        out_result = (self.temp_dir / (onto.stem+ "_temp_satifiability") ).with_suffix(".owl")

        cmd = [
            "java", "-Xmx20G", "-jar", str(self.robot),
            "reason",
            "-vvv",
            "--reasoner", "HermiT",
            "--input", str(input_ontology),
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if result.returncode == 1:
            result.returncode = 0

        if log:
            self.check_result(result, f"SATISFIABILITY CHECK (HermiT)", elapsed)

        output = (result.stdout or "") + "\n" + (result.stderr or "")

        unsatisfiable_classes = re.findall(
            r"unsatisfiable:\s*(\S+)",
            output,
            re.IGNORECASE
        )

        return unsatisfiable_classes



    def consistency(self, input_ontology: Path, log: bool = True) -> bool:

        cmd = [
            str(self.konclude),
            "consistency",
            "-w AUTO",
            "-i", f'"{str(input_ontology)}"',
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"CONSISTENCY CHECK (Konclude)", elapsed)

        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if result.returncode != 0:
            raise RuntimeError(f"Command failed with return code {result.returncode}")

        if re.search(r"\bis inconsistent\.", output, re.IGNORECASE):
            return False

        if re.search(r"\bis consistent\.", output, re.IGNORECASE):
            return True
        

    def realization(self, input, output, log: bool = True):
        cmd = [
            str(self.konclude),
            "realization",
            "-w AUTO",
            "-i", f'"{str(input)}"',
            "-o", f'"{str(output)}"'
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"REALIZATION (Konclude)", elapsed)


    def materialization(self, input, output, axioms, log: bool = True):

        unsatisfiable_classes = self.satisfiability(input)
        if len(unsatisfiable_classes) > 0:
            raise Exception("Cannot Run Materialization on Unsatisfiable / Inconsistent Ontologies")
        
        prop_string = ""
        for p in axioms:
            prop_string += " " + p
        
        cmd = [
            "java", "-Xmx20G", "-jar", str(self.robot),
            "reason",
            "-vvv",
            "--reasoner", "HermiT",
            "--input", str(input),
            "--output", str(output),
            "--axiom-generators", prop_string,
            "--remove-redundant-subclass-axioms", "false",
            "--exclude-tautologies", "structural",
            "--include-indirect", "true",
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if result.returncode == 1:
            result.returncode = 0

        if log:
            self.check_result(result, f"MATERIALIZATION (HermiT)", elapsed)

        

        
    def filtering(self, input, output, uris, log:bool = True):
        cmd = [
            "java",
            "-Xmx20G",
            "-jar", str(self.robot),
            "remove",
            "--input", str(input),
            "--output", str(output)
        ]

        for iri in uris:
            cmd.extend(["--term", iri])

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"FILTERING (Robot)", elapsed)
        



    
    def conversion(self, input, output, format="owl", log: bool = True):
        cmd = [
            "java",
            "-Xmx20G",
            "-jar", str(self.robot),
            "convert",
            "--input", str(input),
            "--format", str(format),
            "--output", str(output),
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"CONVERSION (Robot)", elapsed)

            


if __name__ == "__main__":
    input_ontology = Path("/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/TESTING/consistent.owl")
    output_ontology = Path("/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/TESTING/out.owl")
    reasoners = Path("/home/navis/dev/kg-saf-workspace/kg-saf/reasoners")

    axioms = [
        "SubClass",
        "EquivalentClass",
        "EquivalentObjectProperty",
        "InverseObjectProperties",
        "ObjectPropertyCharacteristic",
        "SubObjectProperty",
        "ObjectPropertyRange",
        "ObjectPropertyDomain",
    ]

    reasoner = Reasoner(reasoners)

    reasoner.consistency(input_ontology) # returns a bool
    unsatisfiable_classes = reasoner.satisfiability(input_ontology) # returns a list of unsatisfiable class iris 
    reasoner.filtering(input_ontology, output_ontology, unsatisfiable_classes)


    
    #reasoner.realization(input_ontology, output_ontology) # writes on a file
    #reasoner.conversion(input_ontology, output_ontology, format="ttl") # writes on a file 
    #reasoner.materialization(input_ontology, output_ontology, axioms=axioms) # writes on a file
    
