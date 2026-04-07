from jdex import JDEX
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib import Graph, Namespace, URIRef, Literal

if __name__ == "__main__":
    jdex = JDEX.from_json(Path("./data/configurations/DBPEDIA_100K_C_ROFF.json"))
    jdex.run()

    """
    g1 = Graph()
    g1.parse("/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia100k.owl")

    rem = Graph()
    rem.parse("/Users/navis/dev/projects/kg-saf/data/documentation/removed_inconsistencies/dbpedia100k.nt")

    g1 -= rem

    g1.serialize("/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia100k_fix.owl", format="xml")
    jdex.reasoner.conversion(
        "/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia100k_fix.owl",
        "/Users/navis/dev/projects/kg-saf/data/facts/unpack/dbpedia100k_fix.owl",
        format="owl"
    )
    """



  

