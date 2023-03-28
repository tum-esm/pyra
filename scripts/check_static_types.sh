#!/bin/bash

set -o errexit

echo "Removing old mypy cache"
rm -rf .mypy_cache 

echo "Checking run_pyra_core.py"
python -m mypy run_pyra_core.py

echo "Checking packages/cli/main.py"
python -m mypy packages/cli/main.py

echo "Checking tests/"
python -m mypy tests/