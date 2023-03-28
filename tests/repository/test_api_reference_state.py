import os
import shutil
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)


src = f"{PROJECT_DIR}/packages/docs/docs/api-reference"
dst = f"{PROJECT_DIR}/packages/docs/docs/api-reference-backup"


@pytest.mark.ci
def test_api_reference_state() -> None:
    shutil.copytree(src, dst)

    tum_esm_utils.shell.run_shell_command(
        "python scripts/update_api_reference.py", working_directory=PROJECT_DIR
    )

    a = os.system(f"diff --recursive {src} {dst}")
    assert a == 0

    shutil.rmtree(dst)
