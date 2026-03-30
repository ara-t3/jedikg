from kgsaf_jdex.utils.reasoner import Reasoner, PresetAxioms
from pathlib import Path

if __name__ == "__main__":

    JAVA_HOME_8 = "/usr/lib/jvm/java-1.8.0-openjdk-amd64"
    JAVA_HOME_11 = "/usr/lib/jvm/java-1.11.0-openjdk-amd64"
    REASONERS_HOME = Path("/home/navis/dev/kg-saf-workspace/kg-saf/reasoners")
    ONTOLOGY_PATH = Path(
        "/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/ARCO-2026/ontology.owl"
    )
    MATERIALIZED_PATH = Path(
        "/home/navis/dev/kg-saf-workspace/kg-saf/kgsaf_data/ontologies/unpack/ARCO-2026/materialized.owl"
    )

    reasoner = Reasoner(
        reasoners_path=REASONERS_HOME,
        java8_path=JAVA_HOME_8,
        java11_path=JAVA_HOME_11,
    )

    """

    reasoner.consistency(input_ontology=ONTOLOGY_PATH, verbose=1)
    
    unsatif = reasoner.satisfiability(
        input_ontology=ONTOLOGY_PATH,
        verbose=1
    )
   

    print(unsatif)

    exit()

    reasoner.filtering(ONTOLOGY_PATH,  MATERIALIZED_PATH, unsatif, verbose=2)

    exit()
    """
    
    axioms = [
        "SubClass",
        "EquivalentClass",
        "EquivalentObjectProperty",
        "InverseObjectProperties",
        "SubObjectProperty",
        ]


    reasoner.materialization(
        input=ONTOLOGY_PATH,
        output=MATERIALIZED_PATH,
        axioms=axioms,
        safety_check=False,
        verbose=2,
    )



    
   
