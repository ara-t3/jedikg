from jdex import JDEX
from jdex.owl.modularization import ALCProfileFilter, ELProfileFilter
from rdflib import Graph
from pathlib import Path
import argparse
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import URIRef


if __name__ == "__main__":
    """"""
    jdex = JDEX.from_json(Path("/Users/navis/dev/projects/kg-saf/data/configurations/TEST.json"))
    jdex.run()
    
    



    
    

    


  

