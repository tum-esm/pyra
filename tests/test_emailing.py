import os
from packages.core.utils import email_client, ConfigInterface

PROJECT_DIR = os.path.abspath(__file__)


def test_emailing():
    _CONFIG = ConfigInterface().read()

    try:
        raise Exception("some exception name")
    except Exception as e:
        email_client.handle_occured_exception(_CONFIG["error_email"], e)
        email_client.handle_resolved_exception(_CONFIG["error_email"])
