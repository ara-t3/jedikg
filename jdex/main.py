from jdex import JDEX
from pathlib import Path
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run JDEX with a configuration file.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration JSON file"
    )
    
    args = parser.parse_args()
    jdex = JDEX.from_json(Path(args.config))
    jdex.run()



  

