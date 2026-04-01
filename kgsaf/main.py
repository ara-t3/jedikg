from kgsaf.jdex import JDEX
from pathlib import Path

if __name__ == "__main__":
    base_folder = Path("./kgsaf/data/configurations/")
    for conf in base_folder.glob("**/*"):
        jdex = JDEX.from_json(conf)
        jdex.run()

