import json
import os
import sys
import pytest

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

sys.path.append(PROJECT_DIR)
from packages.core import types


@pytest.mark.ci
def test_default_config() -> None:

    with open(os.path.join(CONFIG_DIR, "config.default.json"), "r") as f:
        types.Config.load(f.read(), ignore_path_existence=True)

    with open(
        os.path.join(CONFIG_DIR, "tum_plc.config.default.json"), "r"
    ) as f:
        types.config.TumPlcConfig.model_validate_json(f.read())

    with open(os.path.join(CONFIG_DIR, "helios.config.default.json"), "r") as f:
        types.config.HeliosConfig.model_validate_json(f.read())

    with open(os.path.join(CONFIG_DIR, "upload.config.default.json"), "r") as f:
        types.config.UploadConfig.model_validate_json(
            f.read(),
            context={"ignore-path-existence": True},
        )
