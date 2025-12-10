#!/bin/bash

# Bash script to create virtual environment and build threedipa package

set -e  # Exit on error

echo "=== UV Build and Sync Script ==="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed or not in PATH"
    read -p "Install UV? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        echo "Please install UV manually: https://github.com/astral-sh/uv"
        exit 1
    fi
    echo "Please close and reopen your terminal to use UV"
    exit 1
fi

echo "uv is installed: $(uv --version)"
echo ""

read -p "Do you want to create threedipa virtual environment? (y/n): " -n 1 -r
echo ""
if [ ! -e .venv]; then
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Run uv build
        echo "=== Running uv build ==="
        uv build
        echo ""

        # Run uv sync
        echo "=== Running uv sync ==="
        uv sync
        echo ""

        echo "=== Build and sync complete! ==="
    else
        echo "Please create threedipa virtual environment manually: uv venv"
        exit 1
    fi
fi

# Open venv and install package in editable mode
echo "=== Opening virtual environment and building ThreeDIPA package ==="
source .venv/bin/activate
uv pip install -e .
echo "=== Build complete! ==="
echo "=== Type 'deactivate' to exit the virtual environment ==="

