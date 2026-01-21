#!/usr/bin/env python3

import subprocess
import pathlib
from pathlib import Path
import rdflib

def verbose_print(msg: str, verbose: bool):
    """Primg msg if verbose is true

    Args:
        msg (str): Message to print
        verbose (bool): Verbose toggle
    """
    if verbose:
        print(msg)


def serialize(graph, path, robot_jar):
    xml_path = path.with_suffix(".xml")
    owl_path = path.with_suffix(".owl")
    graph.serialize(xml_path, format="xml")

    cmd = [
        "java",
        "-Xmx20G",
        "-jar", str(robot_jar),
        "merge",
        "--input", str(xml_path),
        "--output", str(owl_path)
    ]
    
    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ROBOT merge failed with return code {result.returncode}")

    xml_path.unlink()
    print(f"Serialized graph saved to {owl_path}")