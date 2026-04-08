from jdex import JDEX
from jdex.owl.reasoning import PresetAxioms
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib import Graph, Namespace, URIRef, Literal

if __name__ == "__main__":
    jdex = JDEX.from_json(Path("./data/configurations/DBPEDIA_100K_C_ROFF.json"))
    jdex.run()





  

