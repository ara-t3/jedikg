from jdex import JDEX
from jdex.owl.modularization import ALCProfileFilter, ELProfileFilter
from rdflib import Graph
from pathlib import Path
import argparse
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import URIRef


if __name__ == "__main__":
    """"""
    #jdex = JDEX.from_json(Path("/Users/navis/dev/projects/kg-saf/data/configurations/TEST.json"))
    #jdex.run()

    g = Graph()
    g.parse("/home/navis/dev/kg-saf-workspace/kg-saf/data/schemas/unpack/ERA/ontology.owl")

    obj_props = set(g.subjects(RDF.type, OWL.ObjectProperty))
    data_props = set(g.subjects(RDF.type, OWL.DatatypeProperty))

    print(obj_props & data_props)

    with open("/home/navis/dev/kg-saf-workspace/kg-saf/data.txt", "r") as f:
        d = f.readlines()
        vals = {URIRef(a.strip("<>").strip("\n").strip(">")) for a in d}

    print(len(obj_props & vals))
    print(len(obj_props - data_props))

    tot = 33628772

                
    



    
    

    


  

