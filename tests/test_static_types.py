import os
import shutil
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=2)


def _rmdir(path: str) -> None:
    path = os.path.join(PROJECT_DIR, path)
    if os.path.isdir(path):
        shutil.rmtree(path)


def _rm(path: str) -> None:
    path = os.path.join(PROJECT_DIR, path)
    os.system(f"rm -rf {path}")


@pytest.mark.ci
def test_static_types() -> None:
    _rmdir(".mypy_cache/3.10/packages")
    _rmdir(".mypy_cache/3.10/tests")
    _rm(".mypy_cache/3.10/run_pyra_core.*")

    for path in [
        "run_pyra_core.py",
        "packages/cli/main.py",
        "tests/",
    ]:
        os.system(f"cd {PROJECT_DIR} && .venv/bin/python -m mypy {path}")
