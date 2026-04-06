from jdex import JDEX
from pathlib import Path

if __name__ == "__main__":
    jdex = JDEX.from_json(Path("./data/configurations/DBPEDIA_50K_C_RON.json"))
    jdex.run()

