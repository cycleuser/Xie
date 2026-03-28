#!/bin/bash
# Upload to PyPI

set -e

echo "Building package..."
python -m build

echo "Uploading to PyPI..."
python -m twine upload dist/*

echo "Done!"
