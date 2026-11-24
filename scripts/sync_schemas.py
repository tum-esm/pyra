"""Export the backend config schema for the UI: python scripts/sync_schemas.py."""

import json
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from packages.core.types.config import Config


def main() -> None:
    schema = Config.model_json_schema(by_alias=True)
    with open(os.path.join(PROJECT_DIR, "packages", "ui", "src", "config.schema.json"), "w") as f:
        json.dump(schema, f, indent=4)
        f.write("\n")


if __name__ == "__main__":
    main()
