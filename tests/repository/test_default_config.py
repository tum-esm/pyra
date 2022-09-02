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
        config = json.load(f)
    types.validate_config_dict(config, skip_filepaths=True)

    with open(os.path.join(CONFIG_DIR, "tum_plc.config.default.json"), "r") as f:
        config_tum_plc = json.load(f)
    config["tum_plc"] = config_tum_plc
    types.validate_config_dict(config, skip_filepaths=True)

    with open(os.path.join(CONFIG_DIR, "helios.config.default.json"), "r") as f:
        config_helios = json.load(f)
    config["helios"] = config_helios
    types.validate_config_dict(config, skip_filepaths=True)

    with open(os.path.join(CONFIG_DIR, "upload.config.default.json"), "r") as f:
        config_upload = json.load(f)
    config["upload"] = config_upload
    types.validate_config_dict(config, skip_filepaths=True)
