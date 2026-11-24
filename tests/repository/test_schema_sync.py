import hashlib
import os
import subprocess
import sys

import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
SCHEMA_PATH = os.path.join(PROJECT_DIR, "packages", "ui", "src", "config.schema.json")


@pytest.mark.ci
def test_config_schema_is_in_sync() -> None:
    """Prevent stale UI schema metadata by checking that regeneration leaves it unchanged."""
    with open(SCHEMA_PATH, "rb") as f:
        checksum_before = hashlib.sha256(f.read()).digest()

    subprocess.run(
        [sys.executable, os.path.join(PROJECT_DIR, "scripts", "sync_schemas.py")],
        cwd=PROJECT_DIR,
        check=True,
    )

    with open(SCHEMA_PATH, "rb") as f:
        checksum_after = hashlib.sha256(f.read()).digest()

    assert checksum_before == checksum_after, (
        "Config schema was out of sync. Commit the regenerated packages/ui/src/config.schema.json."
    )
