from kgsaf.jdex import JDEX
from pathlib import Path

if __name__ == "__main__":
    jdex = JDEX.from_json("./test/test_data/config.json")
    reasoner = jdex.reasoner

    if True:
        satif = reasoner.satisfiability(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/datasets/unpack/WHOW_5_ROFF/ontology.owl"), verbose=2)

    if False:

        base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/datasets/old_unpack/WHOW25-5-BASE/abox")
        out_base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/triples/whow5.owl")
        

        reasoner.merging([
            base / "obj_prop_assertions.nt",
            base / "individuals.owl",
            base / "class_assertions.owl"
        ],
            out_base, verbose=2)
        
        #reasoner.filtering(out_base, out_base, uris=["file:///c:/opt/maas/build/procedure_ICCD/NCTR05/"], verbose=2)
