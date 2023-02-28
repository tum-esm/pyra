#!/bin/bash

set -o errexit

echo "Removing old mypy cache"
rm -rf .mypy_cache 

echo "Checking run-pyra-core.py"
python -m mypy run-pyra-core.py

echo "Checking packages/cli/main.py"
python -m mypy packages/cli/main.py
