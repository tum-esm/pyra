"""Sync the UI config schema and exception reference: python scripts/sync_schemas.py."""

import json
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from packages.core.types.config import Config
from packages.core.types.exceptions import KNOWN_EXCEPTIONS


def main() -> None:
    schema = Config.model_json_schema(by_alias=True)
    with open(os.path.join(PROJECT_DIR, "packages", "ui", "src", "config.schema.json"), "w") as f:
        json.dump(schema, f, indent=4)
        f.write("\n")

    reference = """# Known Exceptions

Below you can find a list of known exceptions that can be raised by Pyra. These can happen if OPUS does not start properly, CamTracker doesnt behave as expected, the enclosure PLCs are not reachable, or the system disk is full, and so on. For each of these exceptions you can configure whether you want to receive an email notification and how long Pyra should wait before sending the email.

"Patience" is the time, in seconds, that a recorded fault must remain unresolved before Pyra will send an email notification. I.e. for urgent errors like "rain detected but cover is not closed" you can send an email right away. But for less urgent errors that might self-resolve, like "OPUS did not start properly", you can configure a longer patience time so that you only get an email if the error persists for a while.

If the station is offline when an exception occurs, it will continue to operate and try to self-resolve the issue on its own. Once the station is back online, it will send an email notification if the exception is still unresolved.

## Exception reference
"""
    for exception in KNOWN_EXCEPTIONS.all():
        reference += (
            f"\n### `{exception.identifier}`\n\n"
            f"{exception.error_message}\n\n"
            f"{exception.long_description}\n\n"
            f"**Default email patience:** {exception.default_patience:g} seconds.\n"
        )
    with open(
        os.path.join(PROJECT_DIR, "packages", "docs", "docs", "user-guide", "known-exceptions.md"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(reference)


if __name__ == "__main__":
    main()
