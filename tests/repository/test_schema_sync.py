import hashlib
import os
import subprocess
import sys

import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
GENERATED_PATHS = (
    "packages/ui/src/config.schema.json",
    "packages/docs/docs/user-guide/known-exceptions.md",
)


@pytest.mark.ci
def test_schema_and_exception_reference_are_in_sync() -> None:
    """Catch uncommitted schema or exception documentation updates by regenerating both."""
    checksums_before: dict[str, bytes] = {}
    for path in GENERATED_PATHS:
        with open(os.path.join(PROJECT_DIR, path), "rb") as f:
            checksums_before[path] = hashlib.sha256(f.read()).digest()

    subprocess.run(
        [sys.executable, os.path.join(PROJECT_DIR, "scripts", "sync_schemas.py")],
        cwd=PROJECT_DIR,
        check=True,
    )

    for path in GENERATED_PATHS:
        with open(os.path.join(PROJECT_DIR, path), "rb") as f:
            checksum_after = hashlib.sha256(f.read()).digest()
        assert checksums_before[path] == checksum_after, (
            f"{path} was out of sync. Run python scripts/sync_schemas.py and commit the output."
        )
