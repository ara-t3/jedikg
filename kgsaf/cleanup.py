from kgsaf.jdex import JDEX
from pathlib import Path

if __name__ == "__main__":
    jdex = JDEX.from_json("./test/test_data/config.json")
    reasoner = jdex.reasoner


    base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/datasets/old_unpack/ARCO25-10-BASE/abox")
    out_base = Path("/home/navis/Devel/PhD/kg-saf/kgsaf/data/triples/arco10.owl")
    

    reasoner.merging([
        base / "obj_prop_assertions.nt",
        base / "individuals.owl",
        base / "class_assertions.owl"
    ],
        out_base, verbose=2)
    
    reasoner.filtering(out_base, out_base, uris=["file:///c:/opt/maas/build/procedure_ICCD/NCTR05/"], verbose=2)
