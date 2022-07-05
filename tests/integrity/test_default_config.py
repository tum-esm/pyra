import json
import os
from packages.core.utils.validation import Validation

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))

DEFAULT_CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "config.default.json")
DEFAULT_CONFIG_PATH_TUM_PLC = os.path.join(
    PROJECT_DIR, "config", "tum_plc.config.default.json"
)
DEFAULT_CONFIG_PATH_VBDSD = os.path.join(PROJECT_DIR, "config", "vbdsd.config.default.json")


def test_default_config():
    with open(DEFAULT_CONFIG_PATH, "r") as f:
        DEFAULT_CONFIG: dict[str, dict[str]] = json.load(f)

    with open(DEFAULT_CONFIG_PATH_TUM_PLC, "r") as f:
        DEFAULT_CONFIG_TUM_PLC: dict = json.load(f)

    with open(DEFAULT_CONFIG_PATH_VBDSD, "r") as f:
        DEFAULT_CONFIG_VBDSD: dict = json.load(f)

    for k1 in DEFAULT_CONFIG.keys():
        if DEFAULT_CONFIG[k1] is not None:
            for k2 in DEFAULT_CONFIG[k1].keys():
                if k2.endswith("_path"):
                    DEFAULT_CONFIG[k1][k2] = os.path.join(PROJECT_DIR, ".gitignore")

    Validation.check(DEFAULT_CONFIG)

    DEFAULT_CONFIG["tum_plc"] = DEFAULT_CONFIG_TUM_PLC
    Validation.check(DEFAULT_CONFIG)

    DEFAULT_CONFIG["vbdsd"] = DEFAULT_CONFIG_VBDSD
    Validation.check(DEFAULT_CONFIG)
