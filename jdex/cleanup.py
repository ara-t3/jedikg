from jdex.engine import JDEX
from pathlib import Path
from jdex.owl.reasoning import PresetAxioms
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from pathlib import Path
from collections import defaultdict
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD




if __name__ == "__main__":
    jdex = JDEX.from_json("./test/configurations/test.json")
    reasoner = jdex.reasoner

    if False:
        reasoner.materialization(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/ontology.owl"), Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/materialized.owl"), axioms=PresetAxioms.tbox_materialization(), verbose=2)
    
    if False:
        unsatif = reasoner.satisfiability(input_ontology=Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/materialized.owl"), verbose=2)
        print(unsatif)
        if unsatif:
            reasoner.filtering(input=Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/materialized.owl"), output=Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/materialized.owl"), uris=unsatif, verbose=2)


        

    if False:
        OWL = Namespace("http://www.w3.org/2002/07/owl#")

        g = Graph()
        g.parse("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/ontology.owl", format="xml")

        # Clear and rebind preferred prefixes
        g.namespace_manager.bind("rdf", RDF, override=True)
        g.namespace_manager.bind("rdfs", RDFS, override=True)
        g.namespace_manager.bind("owl", OWL, override=True)

        xml_output = g.serialize("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/lamadonna.owl", format="xml")
        print(xml_output)

    if False:
        reasoner.conversion(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/lamadonna.owl"), Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/lamadonna2.owl"), format="owl")


    if False:
        p = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/ontology.owl").absolute()
        
        g = Graph()
        g.parse(p)
        g.add((URIRef("http://example.org/"), RDF.type, OWL.Ontology))
        g.serialize("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/ontology.xml", format="xml")

        #reasoner.realization(input=p, output=Path("/home/navis/Devel/PhD/kg-saf/test.owl"), verbose=2)

    if False:
        reasoner.conversion(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/ontology.xml"), Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO3/ontology.owl"), format="owl")
       

    if False:
        satif = reasoner.satisfiability(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/schemas/unpack/YAGO4/materialized.owl"), verbose=2)

    if False:

        base = Path("/home/navis/Devel/PhD/kg-saf/data/datasets/old_unpack/DBPEDIA25-100K-C-BASE/abox")
        out_base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/facts/unpack/dbpedia100k.owl")
        
        reasoner.merging([
            base / "obj_prop_assertions.nt",
            base / "individuals.owl",
            base / "class_assertions.owl"
        ],
            out_base, verbose=2)
        
        #reasoner.filtering(out_base, out_base, uris=["file:///c:/opt/maas/build/procedure_ICCD/NCTR05/"], verbose=2)

    if True:
        p = Path("/home/navis/Devel/PhD/kg-saf/diagnosi.owl")
        out = Path("/home/navis/Devel/PhD/kg-saf/why.owl")
        print(reasoner.consistency(p))
        reasoner.justification(p, out)
