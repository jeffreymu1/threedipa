#!/bin/bash

# macOS bash script for uv build and sync
# This script can be run in Terminal on macOS

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

