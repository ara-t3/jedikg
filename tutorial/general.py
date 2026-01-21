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
from kgsaf_jdex.utils.conversion import OWLConverter, TSVConverter
from pykeen.triples.leakage import unleak