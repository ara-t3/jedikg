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


class PresetAxioms:
    @staticmethod
    def tbox_materialization():
        return  [
        "SubClass",
        "EquivalentClass",
        "EquivalentObjectProperty",
        "InverseObjectProperties",
        "ObjectPropertyCharacteristic",
        "SubObjectProperty",
        "ObjectPropertyRange",
        "ObjectPropertyDomain",
        ]


class Reasoner:
    def __init__(self, reasoners_path: Path, java8_path: Path, java11_path: Path, java_max_ram: int = 20):
        self.konclude = reasoners_path / "konclude" / "Konclude"
        self.robot = reasoners_path / "robot" / "robot.jar"
        self.pellet = reasoners_path / "pellet" / "cli/target/pelletcli/bin/pellet"
        self.java8_path = java8_path
        self.java11_path = java11_path
        self.jram = java_max_ram

        

    def _run_process(self, command: list, env = None) -> tuple[subprocess.CompletedProcess, float]:
        start = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        end = time.perf_counter()
        elapsed = end - start
        return result, elapsed

    def _check_result(
        self,
        result: subprocess.CompletedProcess,
        label: str,
        elapsed_time: float,
        verbose: int = 1,
        succesful_returns: list = [0],
    ):
        if result.returncode in succesful_returns:
            if verbose > 0:
                print(
                    f"Reasoning: {label} - completed successfully in {elapsed_time:4.3f}s!"
                )
        else:
            if verbose > 0:
                print(
                    f"Reasoning: {label} -  failed after {elapsed_time:4.3f}s - Stack Trace Available Below:"
                )
                print(f"===== STACK TRACE START =====")
                print(f"{result.stderr}")
                print(f"===== STACK TRACE END =====")
            raise RuntimeError(f"Command failed with returncode {result.returncode}.")
        

    def _get_env(self, java_version: int):
        env = os.environ.copy()

        match java_version:
            case 8:
                env["JAVA_HOME"] = self.java8_path
            case 11:
                env["JAVA_HOME"] = self.java11_path
            case _:
                raise RuntimeError(f"Java JDK Version {java_version} is not supported yet!")
            
        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]
        return env

    def consistency(self, input_ontology: Path, verbose: int = 1) -> bool:

        cmd = [
            str(self.konclude),
            "consistency",
            "-w AUTO",
            "-i",
            f'"{str(input_ontology)}"',
        ]

        result, elapsed = self._run_process(cmd)
        self._check_result(
            result, f"CONSISTENCY CHECK (Konclude)", elapsed, verbose=verbose
        )

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

        output = (result.stdout or "") + "\n" + (result.stderr or "")
        if re.search(r"\bis inconsistent\.", output, re.IGNORECASE):
            return False

        if re.search(r"\bis consistent\.", output, re.IGNORECASE):
            return True

    def satisfiability(self, input_ontology: Path, safety_check: bool = False, verbose: int = 1) -> list:

        if safety_check:
            if not self.consistency(input_ontology, verbose=False):
                raise Exception(
                    "Cannot Run Satisfiabiality on Inconsistent Ontologies due to Robot Limitations"
                )

        cmd = [
            "java",
            f"-Xmx{self.jram}G",
            "-jar",
            str(self.robot),
            "reason",
            "-vvv",
            "--reasoner",
            "HermiT",
            "--input",
            str(input_ontology),
        ]
        
        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(result, f"SATISFIABILITY CHECK (HermiT)", elapsed, succesful_returns=[0,1], verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

        output = (result.stdout or "") + "\n" + (result.stderr or "")

        unsatisfiable_entities = re.findall(
            r"unsatisfiable(?:\s+property)?\s*:\s*(\S+)",
            output,
            re.IGNORECASE,
        )

        return unsatisfiable_entities


    def realization(self, input: Path, output: Path, verbose: int = 1):
        cmd = [
            str(self.konclude),
            "realization",
            "-w AUTO",
            "-i",
            f'"{str(input)}"',
            "-o",
            f'"{str(output)}"',
        ]
        result, elapsed = self._run_process(cmd)
        self._check_result(result, f"REALIZATION (Konclude)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)


    def materialization(self, input: Path, output:Path, axioms: list, safety_check: bool = False, verbose: int = 1):
        
        if safety_check:
            if len(self.satisfiability(input, verbose=False)) > 0:
                raise Exception(
                    "Cannot Run Materialization on Unsatisfiable / Inconsistent Ontologies"
                )

        cmd = [
            "java",
            f"-Xmx{self.jram}G",
            "-jar",
            str(self.robot),
            "reason",
            "-vvv",
            "--reasoner",
            "HermiT",
            "--input",
            str(input),
            "--output",
            str(output),
            "--axiom-generators",
            " ".join(axioms),
            "--remove-redundant-subclass-axioms",
            "false",
            "--exclude-tautologies",
            "structural",
            "--include-indirect",
            "true",
        ]

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(result, f"MATERIALIZATION (HermiT)", elapsed, succesful_returns=[0,1], verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)



    def filtering(self, input: Path, output: Path, uris: list, verbose: int = 1):

        cmd = [
            "java",
            f"-Xmx{self.jram}G",
            "-jar",
            str(self.robot),
            "remove",
            "--input",
            str(input),
            "--output",
            str(output),
        ]

        for iri in uris:
            cmd.extend(["--term", iri])

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(result, f"FILTERING (Robot)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

    def justification(self, input: Path, output: Path, verbose: int = 1):

        if self.consistency(input_ontology, verbose=False):
            print("Ontology Consistent: No Consistency Justification is Needed")
            return 0

        cmd = [
            str(self.pellet),
            "explain",
            "--inconsistent",
            "-v",
            str(input),
        ]

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=8))
        self._check_result(result, f"JUSTIFICATION (Pellet)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

        match = re.search(r"MUPS 1:\s*(\[.*\])", result.stderr)
        if match:
            explanation = [e.strip() for e in match.group(1).strip("[]").split(",")]
            out_str = f"""Ontology(
            {"\n".join(explanation)}
            )"""
            with open(output_ontology, "w") as f:
                f.write(out_str)
            self.conversion(output_ontology, output_ontology, format="ttl", verbose=False)



    def conversion(self, input, output, format="owl", verbose: int = 1):

        cmd = [
            "java",
            f"-Xmx{self.jram}G",
            "-jar",
            str(self.robot),
            "convert",
            "--input",
            str(input),
            "--format",
            str(format),
            "--output",
            str(output),
        ]

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(result, f"CONVERSION (Robot)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

    def merging(self, input_ontologies : list[str], output, verbose: int = 1):
            
        cmd = [
            "java",
            f"-Xmx{self.jram}G",
            "-jar",
            str(self.robot),
            "merge",
            "--output",
            str(output),
        ]

        for iri in input_ontologies:
            cmd.extend(["--input", iri])

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(result, f"MERGING (Robot)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)




if __name__ == "__main__":
    java8 = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
    java11 = "/usr/lib/jvm/java-1.11.0-openjdk-amd64"
    input_ontology = Path(
        "/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/TESTING/unsatif.owl"
    )
    output_ontology = Path(
        "/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/TESTING/out.ttl"
    )
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
    print(reasoner.consistency(input_ontology))  # returns a bool
    print(reasoner.satisfiability(input_ontology, verbose=2)) # returns a list of unsatisfiable class iris
    reasoner.filtering(input_ontology, output_ontology, [], verbose=2)
    #reasoner.realization(input_ontology, output_ontology) # writes on a file
    #reasoner.conversion(input_ontology, output_ontology, format="ttl") # writes on a file
    #reasoner.materialization(input_ontology, output_ontology, axioms=axioms) # writes on a file
    #reasoner.justification(input_ontology, output_ontology)
