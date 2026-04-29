from jdex import JDEX
from jdex.owl.modularization import ALCProfileFilter, ELProfileFilter
from rdflib import Graph
from pathlib import Path
import argparse
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import URIRef

def correct(reasoner):
    g = Graph()
    g.parse("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl")
    g.add((URIRef("http://example.org/"), RDF.type, OWL.Ontology))
    g.serialize("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl", format="xml")
    reasoner.conversion(
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl"),
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl"),
        format="owl"
    )
    
def merge_triples(reasoner):
    reasoner.merging([
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl"),
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_realized_ca.owl")
    ], 
    Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90_realized.owl"))
    

def consistency(reasoner):
    reasoner.consistency(Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl"), verbose=2)

def realization(reasoner):
    reasoner.realization(Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl"), Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_realized_ca.owl"), reasoner="konclude")

def mergetriples(reasoner):
    reasoner.merging([
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/triples_cleaned_90.nt"),
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/ca_cleaned_90.xml")
    ], 
    Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl"))
    
    g = Graph()
    g.parse("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl")
    
    for e in set(g.predicates(None, None)):
        g.add((e, RDF.type, OWL.ObjectProperty))
        g.remove((e, RDF.type, OWL.AnnotationProperty))
        
    g.serialize("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl", format="xml")
    reasoner.conversion(
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl"),
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl"),
        format="owl"
    )
    
def mergewithkg(reasoner):
    
    reasoner.merging([
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/facts/unpack/era_90.owl"),
        Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/schemas/unpack/ERA/materialized.owl")
    ], 
    Path("/home/navis/dev/kg-saf-workspace/kg-saf/era_90_full.owl"))


if __name__ == "__main__":
    """"""
    jdex = JDEX.from_json(Path("/home/navis/dev/kg-saf-workspace/kg-saf/data/configurations/ERA_90_RON.json"))
    #jdex.run()
    reasoner = jdex.reasoner
    merge_triples(reasoner)


                
    



    
    

    


  

