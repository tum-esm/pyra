import os
import shutil
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)


def _rmdir(path: str) -> None:
    """Remove a repository-relative directory and its contents if it exists."""
    path = os.path.join(PROJECT_DIR, path)
    if os.path.isdir(path):
        shutil.rmtree(path)


def _rm(path: str) -> None:
    """Remove repository-relative paths, allowing shell wildcard patterns."""
    path = os.path.join(PROJECT_DIR, path)
    os.system(f"rm -rf {path}")  # type: ignore


@pytest.mark.order(1)
@pytest.mark.ci
def test_static_types() -> None:
    """Clear relevant mypy caches and type-check the Core, CLI, and test entry points."""
    _rmdir(".mypy_cache/3.10/packages")
    _rmdir(".mypy_cache/3.10/tests")
    _rm(".mypy_cache/3.10/run_pyra_core.*")

    for path in [
        "run_pyra_core.py",
        "packages/cli/main.py",
        "tests/",
    ]:
        assert os.system(f"cd {PROJECT_DIR} && python -m mypy {path}") == 0  # type: ignore


@pytest.mark.order(1)
@pytest.mark.ci
def test_with_pyright() -> None:
    """Run Pyright with the repository's configuration and require it to pass."""
    assert os.system(f"cd {PROJECT_DIR} && python -m pyright") == 0  # pyright: ignore[reportDeprecated]
