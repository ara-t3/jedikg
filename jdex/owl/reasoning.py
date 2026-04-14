#!/usr/bin/env python3

import os
import re
import subprocess
import sys
import time
from pathlib import Path

from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace
from rdflib.namespace import split_uri
from rdflib.term import URIRef
from jdex.cli import CLI


def split_top_level(expr: str):
    """Split a comma-separated expression only at the top syntactic level.

    This helper walks through the input string and splits on commas that are
    not enclosed in parentheses. It is useful for parsing functional-style OWL
    expressions where nested constructs may also contain commas.

    Args:
        expr (str): Input expression to split.

    Returns:
        list[str]: Top-level components extracted from the input expression.
    """
    parts = []
    current = []
    depth = 0

    for char in expr:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current).strip())

    return parts


class PresetAxioms:
    @staticmethod
    def tbox_materialization() -> list[str]:
        """Return the default ROBOT axiom generators for TBox materialization.

        The returned list contains the supported axiom generator names used to
        materialize inferred schema-level axioms with ROBOT.

        Returns:
            list[str]: Default axiom generators for TBox materialization.
        """
        return [
            "SubClass",
            "EquivalentClass",
            "EquivalentObjectProperty",
            "InverseObjectProperties",
            "ObjectPropertyCharacteristic",
            "SubObjectProperty",
            "ObjectPropertyRange",
            "ObjectPropertyDomain",
        ]

    def realization() -> list[str]:
        """Return the ROBOT axiom generators needed for realization only.

        Realization is limited here to inferred class assertions, so the method
        returns only the corresponding ROBOT generator.

        Returns:
            list[str]: A list containing only ``"ClassAssertion"``.
        """
        return ["ClassAssertion"]


class Reasoner:
    """Unified wrapper around multiple ontology reasoning command-line tools.

    This class provides a Python abstraction over several external reasoners
    and ontology utilities, enabling ontology reasoning workflows directly from
    Python code. Supported operations include:

    - Consistency checking via Konclude
    - Satisfiability checking via ROBOT using HermiT or ELK
    - Materialization via ROBOT using HermiT or ELK
    - Realization via Konclude or ROBOT
    - Filtering axioms/entities via ROBOT
    - Merging ontologies via ROBOT
    - Format conversion via ROBOT
    - Justification for inconsistencies via Pellet

    Notes:
        - ROBOT-based operations require Java 11.
        - Pellet justification requires Java 8.
        - Konclude is used as a native executable.
    """

    def __init__(
        self,
        reasoners_path: Path,
        java8_path: Path,
        java11_path: Path,
        java_max_ram: int = 20,
    ):
        """Initialize paths and runtime configuration for the reasoning tools.

        Args:
            reasoners_path (Path): Root directory containing the installed
                reasoning tools (Konclude, ROBOT, Pellet).
            java8_path (Path): Path to the Java 8 installation used by Pellet.
            java11_path (Path): Path to the Java 11 installation used by ROBOT.
            java_max_ram (int, optional): Maximum Java heap size in gigabytes
                for Java-based reasoners. Defaults to 20.
        """
        self.konclude = reasoners_path / "konclude" / "Binaries" / "Konclude"
        self.robot = reasoners_path / "robot" / "robot.jar"
        self.pellet = reasoners_path / "pellet" / "cli/target/pelletcli/bin/pellet"
        self.java8_path = java8_path
        self.java11_path = java11_path
        self.jram = java_max_ram
        self.supported_reasoners = ["hermit", "elk"]
        self.ui = CLI(verbose=1)

    def _run_process(
        self, command: list, env=None
    ) -> tuple[subprocess.CompletedProcess, float]:
        """Execute a subprocess command and measure its runtime.

        Args:
            command (list): Command and arguments to execute.
            env (dict, optional): Environment variables for the subprocess.
                Defaults to None.

        Returns:
            tuple[subprocess.CompletedProcess, float]: The completed subprocess
            result and the elapsed execution time in seconds.
        """
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
        """Validate a subprocess result and raise on unexpected exit codes.

        Args:
            result (subprocess.CompletedProcess): Subprocess execution result.
            label (str): Human-readable label for the executed task.
            elapsed_time (float): Execution duration in seconds.
            verbose (int, optional): Verbosity level. Defaults to 1.
            succesful_returns (list, optional): Exit codes considered
                successful. Defaults to [0].

        Raises:
            RuntimeError: If the subprocess exits with a code not listed in
                ``succesful_returns``.
        """
        if result.returncode in succesful_returns:
            if verbose > 0:
                self.ui.reason(
                    f"Reasoning: {label} - completed successfully in {elapsed_time:4.3f}s!"
                )
        else:
            if verbose > 0:
                self.ui.reason(
                    f"Reasoning: {label} -  failed after {elapsed_time:4.3f}s - Stack Trace Available Below:"
                )
                self.ui.reason(f"===== STACK TRACE START =====")
                self.ui.reason(f"{result.stderr}")
                self.ui.reason(f"===== STACK TRACE END =====")
            raise RuntimeError(f"Command failed with returncode {result.returncode}.")

    def _get_env(self, java_version: int):
        """Build an execution environment for a specific Java version.

        Args:
            java_version (int): Java major version to use. Supported values are
                8 and 11.

        Returns:
            dict: Environment variables configured with the requested
            ``JAVA_HOME`` and updated ``PATH``.

        Raises:
            RuntimeError: If the requested Java version is not supported.
        """
        env = os.environ.copy()

        match java_version:
            case 8:
                env["JAVA_HOME"] = self.java8_path
            case 11:
                env["JAVA_HOME"] = self.java11_path
            case _:
                raise RuntimeError(
                    f"Java JDK Version {java_version} is not supported yet!"
                )

        env["PATH"] = env["JAVA_HOME"] + "/bin:" + env["PATH"]
        return env

    def consistency(self, input_ontology: Path, verbose: int = 1) -> bool:
        """Run a consistency check on an ontology using Konclude.

        Args:
            input_ontology (Path): Path to the input ontology file.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.

        Returns:
            bool: ``True`` if the ontology is consistent, ``False`` if it is
            inconsistent.
        """

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

    def satisfiability(
        self,
        input_ontology: Path,
        reasoner: str = "hermit",
        safety_check: bool = False,
        verbose: int = 1,
    ) -> list:
        """Check ontology satisfiability and collect unsatisfiable entities.

        This method invokes ROBOT with the selected reasoner and parses its
        output to extract the IRIs of unsatisfiable classes and properties.

        Args:
            input_ontology (Path): Path to the input ontology file.
            reasoner (str, optional): ROBOT reasoner backend to use. Supported
                values are ``"hermit"`` and ``"elk"``. Defaults to ``"hermit"``.
            safety_check (bool, optional): If ``True``, first verify ontology
                consistency before running satisfiability analysis. Defaults to
                False.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.

        Returns:
            list: List of URIs corresponding to unsatisfiable classes or
            properties.

        Raises:
            ValueError: If the selected reasoner is not supported.
            Exception: If ``safety_check`` is enabled and the ontology is
                inconsistent.
        """

        if reasoner not in self.supported_reasoners:
            raise ValueError(f"Reasoner {reasoner} not supported by ROBOT OBO Utility")

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
            str(reasoner),
            "--input",
            str(input_ontology),
        ]

        result, elapsed = self._run_process(cmd, env=self._get_env(java_version=11))
        self._check_result(
            result,
            f"SATISFIABILITY CHECK ({reasoner.upper()})",
            elapsed,
            succesful_returns=[0, 1],
            verbose=verbose,
        )

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

    def _konclude_realization(self, input: Path, output: Path, verbose: int = 1):
        """Run realization with Konclude.

        Args:
            input (Path): Input ontology file.
            output (Path): Output file where realized assertions will be stored.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.
        """
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
        self._check_result(result, f"REALIZATION (KONCLUDE)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

    def _robot_realization(
        self,
        input: Path,
        output: Path,
        reasoner: str = "hermit",
        verbose: int = 1,
    ):
        """Run realization through ROBOT by materializing class assertions.

        Args:
            input (Path): Input ontology file.
            output (Path): Output ontology file.
            reasoner (str, optional): ROBOT reasoner backend to use.
                Defaults to ``"hermit"``.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.
        """
        self.materialization(
            input,
            output,
            reasoner=reasoner,
            axioms=PresetAxioms.realization(),
            safety_check=False,
            verbose=verbose,
        )

    def realization(
        self, input: Path, output: Path, reasoner: str = "konclude", verbose: int = 1
    ):
        """Run ontology realization with the selected reasoner backend.

        Realization computes inferred class assertions for individuals in the
        ontology.

        Args:
            input (Path): Input ontology file.
            output (Path): Output file where realized assertions will be saved.
            reasoner (str, optional): Reasoner to use. Supported values are
                ``"konclude"``, ``"hermit"``, and ``"elk"``. Defaults to
                ``"konclude"``.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.

        Raises:
            ValueError: If the requested reasoner is not supported.
        """
        if reasoner == "konclude":
            self._konclude_realization(input, output, verbose)
        elif reasoner in self.supported_reasoners:
            self._robot_realization(input, output, reasoner, verbose)
        else:
            raise ValueError(f"Reasoner {reasoner} not supported by ROBOT OBO Utility")

    def materialization(
        self,
        input: Path,
        output: Path,
        reasoner: str = "hermit",
        axioms: list = PresetAxioms.tbox_materialization(),
        safety_check: bool = False,
        verbose: int = 1,
    ):
        """Materialize inferred axioms into an ontology using ROBOT.

        Args:
            input (Path): Input ontology file.
            output (Path): Output ontology file for the materialized result.
            reasoner (str, optional): ROBOT reasoner backend to use. Supported
                values are ``"hermit"`` and ``"elk"``. Defaults to ``"hermit"``.
            axioms (list, optional): ROBOT axiom generators to materialize.
                Defaults to ``PresetAxioms.tbox_materialization()``.
            safety_check (bool, optional): If ``True``, first verify that the
                ontology has no unsatisfiable classes or properties. Defaults
                to False.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.

        Raises:
            ValueError: If the selected reasoner is not supported.
            Exception: If ``safety_check`` is enabled and the ontology is
                unsatisfiable or inconsistent.
        """

        if reasoner not in self.supported_reasoners:
            raise ValueError(f"Reasoner {reasoner} not supported by ROBOT OBO Utility")

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
            str(reasoner),
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
        self._check_result(
            result,
            f"MATERIALIZATION ({reasoner.upper()})",
            elapsed,
            succesful_returns=[0, 1],
            verbose=verbose,
        )

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

    def filtering(self, input: Path, output: Path, uris: list, verbose: int = 1):
        """Remove axioms involving specified URIs from a knowledge graph.

        Args:
            input (Path): Input ontology or knowledge graph file.
            output (Path): Output file for the filtered ontology.
            uris (list): List of URIs to remove from the ontology signature.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.
        """

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

    def justification(
        self, input: Path, output: Path, safety_check: bool = False, verbose: int = 1
    ) -> list[str]:
        """Generate a justification for ontology inconsistency using Pellet.

        The method extracts the first MUPS explanation reported by Pellet,
        writes it in OWL functional syntax, converts it to OWL format, and
        returns the explanation components.

        Args:
            input (Path): Input ontology file.
            output (Path): Output file for the generated justification.
            safety_check (bool, optional): If ``True``, skip justification when
                the ontology is already consistent. Defaults to False.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.

        Returns:
            list[str]: List of OWL functional syntax expressions that form the
            extracted explanation. Returns an empty list when no explanation is
            found.
        """

        if safety_check:
            if self.consistency(input, verbose=False):
                print("Ontology Consistent: No Consistency Justification is Needed")
                return 0

        cmd = [
            str(self.pellet),
            "explain",
            "--inconsistent",
            "-v",
            str(input),
        ]

        result, elapsed = self._run_process(cmd, env=self._get_env(8))
        self._check_result(result, f"JUSTIFICATION (Pellet)", elapsed, verbose=verbose)

        # If PROCESS Successful =>
        if verbose >= 2:
            print(result.stderr, result.stdout)

        match = re.search(r"MUPS 1:\s*(\[.*\])", result.stderr)
        if match:
            content = match.group(1).strip("[]")
            explanation = split_top_level(content)

            out_str = f"""Ontology(
            {"\n".join(explanation)}
            )"""
            with open(output, "w") as f:
                f.write(out_str)
            self.conversion(output, output, format="owl", verbose=False)
            return explanation
        return []

    def conversion(self, input: Path, output: Path, format="owl", verbose: int = 1):
        """Convert an ontology file to another serialization format using ROBOT.

        Args:
            input (Path): Input ontology file.
            output (Path): Output ontology file.
            format (str, optional): Target serialization format accepted by
                ROBOT. Defaults to ``"owl"``.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.
        """

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

    def merging(self, input_ontologies: list[str], output, verbose: int = 1):
        """Merge multiple ontologies into a single output ontology using ROBOT.

        Args:
            input_ontologies (list[str]): List of ontology paths or IRIs to
                merge.
            output: Output file path for the merged ontology.
            verbose (int, optional): Verbosity level for status output.
                Defaults to 1.
        """

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
