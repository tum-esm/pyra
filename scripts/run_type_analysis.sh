echo "running static type analysis for PYRA Core"
python -m mypy run-pyra-core.py --strict --implicit-reexport --no-warn-unused-ignores

echo "running static type analysis for PYRA CLI"
python -m mypy packages/cli/main.py --strict --implicit-reexport --no-warn-unused-ignores