#!/bin/bash
set -e 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 -m jdex.prediction \
  --model "TransE" \
  --model-path ./WHOW_5_ROFF_TransE_E200_D128.pt \
  --dataset-dir ./data/datasets/unpack/WHOW_5_ROFF/abox/experiments_split \
  --mappings-dir ./experiments/models/WHOW_5_ROFF_TransE_E200_D128/mappings \
  --output-dir ./experiments/predictions \
  --embedding-dim 128 \