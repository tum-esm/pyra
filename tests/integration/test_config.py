import os
import sys
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

sys.path.append(PROJECT_DIR)
from packages.core import types


@pytest.mark.order(1)
@pytest.mark.integration
def test_config() -> None:
    types.Config.load()
