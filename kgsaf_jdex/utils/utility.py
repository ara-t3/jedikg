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


