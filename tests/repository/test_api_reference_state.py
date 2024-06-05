import os
from typing import Generator
import shutil
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)

src = f"{PROJECT_DIR}/packages/docs/docs/api-reference"
dst = f"{PROJECT_DIR}/packages/docs/docs/api-reference-backup"


@pytest.fixture
def setup() -> Generator[None, None, None]:
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    yield
    shutil.rmtree(dst)


@pytest.mark.order(2)
@pytest.mark.ci
def test_api_reference_state(setup: None) -> None:
    tum_esm_utils.shell.run_shell_command(
        "python scripts/update_api_reference.py",
        working_directory=PROJECT_DIR,
    )
    assert os.system(f"diff --recursive {src} {dst}", ) == 0
