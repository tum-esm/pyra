**Work in progress! Do not use it yet.**

<br/>

# Pyra Version 4

## Set up with

Dependency management using https://python-poetry.org/.

```bash
# create a virtual environment (copy of the python interpreter)
python3.10 -m venv .venv

# activate virtual environment
source .venv/bin/activate   # unix
.venv\Scripts\activate.bat  # windows

# when your venv is activated your command line has a (.venv) prefix
# install dependencies using poetry
poetry install
```

<br/>

## Configuration Files

Two types of config files:

1. **`setup.json`** contains all information about the static setup: Which parts does the enclosure consist of? This should be written once and only changes when the hardware changes.
2. **`parameters.json`** contains all dynamic parameters that can be set when operating pyra. This should be manipulated either via the CLI (coming soon) or the graphical user interface (coming soon, similar to Pyra version <= 3).

For each file, there is a `*.default.json` file present in the repository. A full reference can be found here soon.

<br/>

## CLI

_documentation coming soon_

Make `pyra-cli` command available:

```bash
alias pyra-cli=".../.venv/bin/python .../packages/cli/main.py"
```

TODO: Find a way to set up autocompletion on the `pyra-cli` command.

<br/>

## Graphical User Interface

_documentation coming soon_
