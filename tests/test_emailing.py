import os
from packages.core.utils import ConfigInterface, ExceptionEmailClient

PROJECT_DIR = os.path.abspath(__file__)


def test_emailing():
    _CONFIG = ConfigInterface().read()

    try:
        raise Exception("some exception name")
    except Exception as e:
        ExceptionEmailClient.handle_occured_exception(_CONFIG["error_email"], e)
        ExceptionEmailClient.handle_resolved_exception(_CONFIG["error_email"])
