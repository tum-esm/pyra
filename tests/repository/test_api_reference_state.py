import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)


get_api_reference_checksum = lambda: tum_esm_utils.shell.run_shell_command(
    "find packages/docs/docs/api-reference -type f -exec md5sum {} + | LC_ALL=C sort | md5sum",
    working_directory=PROJECT_DIR,
)


@pytest.mark.ci
def test_api_reference_state() -> None:
    checksum_before_update = get_api_reference_checksum()
    tum_esm_utils.shell.run_shell_command(
        "python scripts/update_api_reference.py", working_directory=PROJECT_DIR
    )
    checksum_after_update = get_api_reference_checksum()
    assert checksum_before_update == checksum_after_update, "API reference is not up to date"
