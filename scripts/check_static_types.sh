#!/bin/bash

set -o errexit

echo "Removing old mypy cache"
rm -rf .mypy_cache 

echo "Checking run_pyra_core.py"
mypy run_pyra_core.py

echo "Checking packages/cli/main.py"
mypy packages/cli/main.py

echo "Checking tests/"
mypy tests/