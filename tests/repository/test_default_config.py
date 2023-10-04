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
        config = types.Config.load(f.read(), ignore_path_existence=True)

    assert config.tum_plc is None
    assert config.helios is None
    assert config.upload is None
    config_dict = config.model_dump()

    with open(
        os.path.join(CONFIG_DIR, "tum_plc.config.default.json"), "r"
    ) as f:
        config_dict["tum_plc"] = json.load(f)

    with open(os.path.join(CONFIG_DIR, "helios.config.default.json"), "r") as f:
        config_dict["helios"] = json.load(f)

    with open(os.path.join(CONFIG_DIR, "upload.config.default.json"), "r") as f:
        config_dict["upload"] = json.load(f)

    # validate the full config with all optional subconfigs
    config = types.Config.load(config_dict, ignore_path_existence=True)
