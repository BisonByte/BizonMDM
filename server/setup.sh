#!/bin/bash
set -e

# Determine the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python dependencies
pip install -r "$SCRIPT_DIR/Servidor/requirements.txt"

# Run installation script (will prompt for configuration if needed)
python "$SCRIPT_DIR/install.py"

# Launch the server
python "$SCRIPT_DIR/Servidor/server.py"
