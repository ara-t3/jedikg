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

JUSTIFICATION (Pellet)
saves the justification in OWL sytax




"""



from pathlib import Path
import sys
import subprocess
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace
from rdflib.namespace import split_uri
from rdflib.term import URIRef
import re
import time
import os

sys.path.append(str(Path.cwd().parent))

class Reasoner:
    def __init__(self, reasoners_path: Path, java8_path, java11_path):
        self.konclude = reasoners_path / "konclude" / "Konclude"
        self.robot = reasoners_path / "robot" / "robot.jar"
        self.pellet = reasoners_path / "pellet" / "cli/target/pelletcli/bin/pellet"
        self.temp_dir = reasoners_path / "temp"
        self.java8_path = java8_path
        self.java11_path = java11_path

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

        env = os.environ.copy()
        env["JAVA_HOME"] = self.java11_path
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]

        cmd = [
            "java", "-Xmx20G", "-jar", str(self.robot),
            "reason",
            "-vvv",
            "--reasoner", "HermiT",
            "--input", str(input_ontology),
        ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
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

        unsatisfiable_classes = self.satisfiability(input, log=False)
        if len(unsatisfiable_classes) > 0:
            raise Exception("Cannot Run Materialization on Unsatisfiable / Inconsistent Ontologies")
        
        prop_string = ""
        for p in axioms:
            prop_string += " " + p

        env = os.environ.copy()
        env["JAVA_HOME"] = self.java11_path
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]
        
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
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        end = time.perf_counter()
        elapsed = end - start  

        if result.returncode == 1:
            result.returncode = 0

        if log:
            self.check_result(result, f"MATERIALIZATION (HermiT)", elapsed)

        

        
    def filtering(self, input, output, uris, log:bool = True):

        env = os.environ.copy()
        env["JAVA_HOME"] = self.java11_path
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]

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
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"FILTERING (Robot)", elapsed)
        


    def justification(self, input, output, log:bool = True):

        onto = Path(input_ontology)

        if self.consistency(input_ontology, log=False):
            print("Ontology Consistent: No Consistency Justification is Needed")
            return 0

        env = os.environ.copy()
        env["JAVA_HOME"] = self.java8_path
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]

        cmd = [
                str(self.pellet),
                "explain",
                "--inconsistent",
                "-v",
                str(input),
            ]

        start = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"JUSTIFICATION (Pellet)", elapsed)

        match = re.search(r"MUPS 1:\s*(\[.*\])", result.stderr)
        if match:
            explanation = [e.strip() for e in match.group(1).strip("[]").split(",")]
            out_str = f"""Ontology(
            {"\n".join(explanation)}
            )"""
            with open(output_ontology, "w") as f:
                f.write(out_str)
            self.conversion(output_ontology, output_ontology, format="ttl", log=False)
    

    
    def conversion(self, input, output, format="owl", log: bool = True):

        env = os.environ.copy()
        env["JAVA_HOME"] = self.java11_path
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]

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
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        end = time.perf_counter()
        elapsed = end - start  

        if log:
            self.check_result(result, f"CONVERSION (Robot)", elapsed)

            


if __name__ == "__main__":
    java8 = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
    java11 = "/usr/lib/jvm/java-1.11.0-openjdk-amd64"
    input_ontology = Path("/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/TESTING/unsatif_inconsistent.owl")
    output_ontology = Path("/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/TESTING/out.ttl")
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

    reasoner = Reasoner(reasoners, java8, java11)
    print(reasoner.consistency(input_ontology)) # returns a bool
    #reasoner.satisfiability(input_ontology) # returns a list of unsatisfiable class iris 
    #reasoner.filtering(input_ontology, output_ontology, [])
    #reasoner.realization(input_ontology, output_ontology) # writes on a file
    #reasoner.conversion(input_ontology, output_ontology, format="ttl") # writes on a file 
    #reasoner.materialization(input_ontology, output_ontology, axioms=axioms) # writes on a file
    reasoner.justification(input_ontology, output_ontology)


    
