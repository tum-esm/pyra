import json
import os

dir = os.path.dirname
PROJECT_DIR = dir(dir(os.path.abspath(__file__)))

TOML_PATH = os.path.join(PROJECT_DIR, "pyproject.toml")
PACKAGE_JSON_PATH = os.path.join(PROJECT_DIR, "packages", "ui", "package.json")
TAURI_JSON_PATH = os.path.join(PROJECT_DIR, "packages", "ui", "src-tauri", "tauri.conf.json")

# load version number
with open(TOML_PATH, "r") as f:
    while True:
        line = f.readline()
        if not line.startswith("version"):
            continue
        version = line.split("=")[1].replace('"', "").replace(" ", "").replace("\n", "")
        break

# update package.json
with open(PACKAGE_JSON_PATH, "r") as f:
    json_content = json.load(f)
    json_content["version"] = version
with open(PACKAGE_JSON_PATH, "w") as f:
    json.dump(json_content, f, indent=4)

# update tauri.conf.json
with open(TAURI_JSON_PATH, "r") as f:
    json_content = json.load(f)
    json_content["package"]["version"] = version
with open(TAURI_JSON_PATH, "w") as f:
    json.dump(json_content, f, indent=4)
