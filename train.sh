#!/bin/bash
set -e 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 -m jdex.train \
  --dataset-dir ./data/datasets/unpack/WHOW_5_ROFF \
  --output-dir ./experiments/ \
  --model ComplEx \
  --num-epochs 65 \
  --embedding-dim 128 \
  --batch-size  8192 \
  --lr 0.001
