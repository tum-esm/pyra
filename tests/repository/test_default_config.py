import os
import sys
import pytest
import tum_esm_utils

PROJECT_DIR = tum_esm_utils.files.get_parent_dir_path(__file__, current_depth=3)
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

sys.path.append(PROJECT_DIR)
from packages.core import types


@pytest.mark.order(2)
@pytest.mark.ci
def test_default_config() -> None:

    with open(os.path.join(CONFIG_DIR, "config.default.json"), "r") as f:
        types.Config.load(f.read(), ignore_path_existence=True)

    with open(os.path.join(CONFIG_DIR, "tum_enclosure.config.default.json"), "r") as f:
        types.config.TumPlcConfig.model_validate_json(f.read())

    with open(os.path.join(CONFIG_DIR, "helios.config.default.json"), "r") as f:
        types.config.HeliosConfig.model_validate_json(f.read())

    with open(os.path.join(CONFIG_DIR, "upload.config.default.json"), "r") as f:
        types.config.UploadConfig.model_validate_json(
            f.read(),
            context={"ignore-path-existence": True},
        )
