**Work in progress! Do not use it yet.**

<br/>

# Pyra Version 4

## Set up with

Dependency management using https://python-poetry.org/.

```bash
# create a virtual environment (copy of the python interpreter)
python3.10 -m venv .venv

# activate the virtual environment
source .venv/bin/activate   # unix
.venv\Scripts\activate.bat  # windows

# when your venv is activated your command line has a (.venv) prefix
# install dependencies using poetry
poetry install
```

<br/>

## Configuration Files

Two types of config files:

1. **`setup.json`** contains all information about the static setup: Which parts does the enclosure consist of? This should be written once and only change when the hardware changes.
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

Less Secure Apps have been deactivated.
https://support.google.com/accounts/answer/6010255?hl=de&visit_id=637914296292859831-802637670&p=less-secure-apps&rd=1

Solution: Use "App passwords", which require 2FA

<br/>

## Repository Management & CI

**Branches:** `development-...`, `integration-x.y.z`, `main`, `release`, `prerelease`

**Hierarchy:** `development-...` contains stuff in active development and will be merged into `integration-x.y.z`. `integration-x.y.z`: Is used during active integration on the stations and will be merged into `main`. `main` contains the latest running version that passed the integration and will be merged into `release` once enough changes have accumulated. Any branch can be released into `prerelease` to run the CI-Pipeline on demand. `prerelease` will not be merged into anything else and is just used for development purposes.

**Continuous Integration:** The CI-Pipeline runs every time a commit/a series of commits is added to the `release` branch. The CI compiles and bundles the frontend code into an installable windows-application. Then it creates a new release draft and attaches the `.msi` file to the draft. We can then manually add the release description and submit the release.

**Testing (not in an active CI):** We could add automated tests to the main- and integration branches. However, most things we could test make use of OPUS, Camtracker, Helios, or the enclosure, hence we can only do a subset of our tests in an isolated CI environment without the system present.

**Issues:** Things we work on are managed via issues - which are bundled into milestones (each milestone represents a release). The issues should be closed once they are on the `main` branch via commit messages ("closes #87", "fixes #70", etc. see [this list of keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)). Issues that have been finished but are not on the `main` branch yet, can be labeled using the white label "implemented". This way, we can oversee incompleted issues, but don't forget to merge them.
