#!/bin/bash
set -e 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 -m jdex.train \
  --dataset-dir ./data/datasets/unpack/YAGO3_39K_C_ROFF \
  --output-dir ./experiments/ \
  --model CompGCN \
  --num-epochs 200 \
  --embedding-dim 32 \
  --batch-size 128