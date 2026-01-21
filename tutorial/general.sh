#!/bin/bash
# run_dataset.sh
# Usage: ./run_dataset.sh <kg_file> <output_path> <dataset_name> <robot_jar> [--reasoner]

# Always run from this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Forward ALL arguments exactly as received
python3 general.py "$@"