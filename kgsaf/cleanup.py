from kgsaf.jdex import JDEX
from pathlib import Path
from kgsaf.tools.reasoner import PresetAxioms

if __name__ == "__main__":
    jdex = JDEX.from_json("./test/test_data/config.json")
    reasoner = jdex.reasoner

    if True:
        satif = reasoner.satisfiability(Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/datasets/unpack/ATRAVEL_ROFF/ontology.owl"), verbose=2)

    if False:

        base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/datasets/old_unpack/ATRAVEL-BASE/abox")
        out_base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/facts/unpack/atravel.owl")
        

        reasoner.merging([
            base / "obj_prop_assertions.nt",
            base / "individuals.owl",
            base / "class_assertions.owl"
        ],
            out_base, verbose=2)
        
        #reasoner.filtering(out_base, out_base, uris=["file:///c:/opt/maas/build/procedure_ICCD/NCTR05/"], verbose=2)
