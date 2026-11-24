import os
import subprocess

import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
UI_DIR = os.path.join(PROJECT_DIR, "packages", "ui")


@pytest.mark.ci
def test_ui_build() -> None:
    """Catch UI type errors, including missing schema properties, and bundling failures."""
    subprocess.run(["bun", "install"], cwd=UI_DIR, check=True)
    subprocess.run(["bun", "run", "build"], cwd=UI_DIR, check=True)
