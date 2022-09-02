# PYRA

**For installation, see https://github.com/tum-esm/pyra-setup-tool**

<br/>

## Repository Management & CI

**Branches:** `development-...`, `integration-x.y.z`, `main`, `release`, `prerelease`

**Hierarchy:** `development-...` contains stuff in active development and will be merged into `integration-x.y.z`. `integration-x.y.z`: Is used during active integration on the stations and will be merged into `main`. `main` contains the latest running version that passed the integration and will be merged into `release` once enough changes have accumulated. Any branch can be released into `prerelease` to run the CI-Pipeline on demand. `prerelease` will not be merged into anything else and is just used for development purposes.

**Continuous Integration:** The CI-Pipeline runs every time a commit/a series of commits is added to the `release` branch. The CI compiles and bundles the frontend code into an installable windows-application. Then it creates a new release draft and attaches the `.msi` file to the draft. We can then manually add the release description and submit the release.

**Testing (not in an active CI):** We could add automated tests to the main- and integration branches. However, most things we could test make use of OPUS, Camtracker, Helios, or the enclosure, hence we can only do a subset of our tests in an isolated CI environment without the system present.

**Issues:** Things we work on are managed via issues - which are bundled into milestones (each milestone represents a release). The issues should be closed once they are on the `main` branch via commit messages ("closes #87", "fixes #70", etc. see [this list of keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)). Issues that have been finished but are not on the `main` branch yet, can be labeled using the white label "implemented". This way, we can oversee incompleted issues, but don't forget to merge them.

<br/>

## Elements

### FileLocks

Since we have parallel processes interacting with state, config, and logs, we need to control the access to these resources to avoid race conditions. We use the python module [filelock](https://pypi.org/project/filelock/) for this. Before working with one of these resources, a process has to acquire a file lock for the respective `.state.lock`/`.config.lock`/`.logs.lock` file. When it cannot acquire a lock for 10 seconds, it throws a `TimeoutError`.

When running into a deadlock, with timeout errors (never happened to us yet), the CLI command `pyra-cli remove-filelocks` removes all present lock files.

### Version numbers

Versions up to `4.0.4` are alpha and beta versions that should not be used regularly. PYRA can be generally used starting from version `4.0.5`.

Inside the codebase, the version number is included 3 times: `pyproject.toml`, `packages/ui/package.json`, `packages/ui/src-tauri/tauri.conf.json`. The script `scripts/sync_version_numbers.py` takes the version number from the `.toml` file and pastes it into the other locations. This script can be run in a [git-hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks).
