from jdex import JDEX
from jdex.owl.reasoning import PresetAxioms
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib import Graph, Namespace, URIRef, Literal

if __name__ == "__main__":
    jdex = JDEX.from_json(Path("./data/configurations/DBPEDIA_50K_C_ROFF.json"))
    jdex.run()

    
    # jdex.reasoner.materialization(
    #     Path("/Users/navis/dev/projects/kg-saf/data/schemas/unpack/DBPEDIA-2026/ontology_test.owl"),
    #     output=Path("/Users/navis/dev/projects/kg-saf/data/schemas/unpack/DBPEDIA-2026/materialized_test.owl"),
    #     axioms=PresetAxioms.tbox_materialization(),
    #     verbose=1
    # )
   
   
    # g1 = Graph()
    # g1.parse("/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia50k_old.owl")

    # rem = Graph()
    # rem.parse("/Users/navis/dev/projects/kg-saf/data/documentation/removed_inconsistencies/dbpedia50k.nt")

    # g1 -= rem

    # g1.serialize("/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia50k.owl", format="xml")
    # jdex.reasoner.conversion(
    #     "/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia50k.owl",
    #     "/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia50k.owl",
    #     format="owl"
    # )



    # g1 = Graph()
    # g1.parse("/Users/navis/dev/projects/kg-saf/data/schemas/unpack/DBPEDIA-2026/ontology_test.owl")
    
    # to_remove = set()
    
    # for s,p,o in g1.triples((None, RDF.type, OWL.ObjectProperty)):
    #     if (s, RDF.type, OWL.DatatypeProperty) in g1:
    #         print(s, "is also DATATYPE")
    #         to_remove.add(s)

 

    # for s,p,o in g1.triples((None, RDF.type, OWL.DatatypeProperty)):
    #     if (s, RDF.type, OWL.ObjectProperty) in g1:
    #         print(s, "is also OBJECT PROP")
    #         to_remove.add(s)

    # print(to_remove, len(to_remove))

    # for i in to_remove:
    #     print(i)
 





  

