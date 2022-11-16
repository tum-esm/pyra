set -o errexit

echo "running static type analysis for PYRA Core"
python -m mypy run-pyra-core.py

echo "running static type analysis for PYRA CLI"
python -m mypy packages/cli/main.py