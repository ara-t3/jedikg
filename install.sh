#!/bin/bash

set -e 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "Running from: $SCRIPT_DIR"
echo "Using Python:"
python3 --version
echo "Upgrading pip..."
python3 -m pip install --upgrade pip
echo "Installing requirements..."
python3 -m pip install -r requirements.txt
echo "Running Installation Script..."
clear
python3 -m install
