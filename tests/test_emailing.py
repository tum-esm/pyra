import os
from packages.core.utils import json_file_interaction, email_client

PROJECT_DIR = os.path.abspath(__file__)


def test_emailing():
    _SETUP, _PARAMS = json_file_interaction.Config().read()

    try:
        raise Exception("some exception name")
    except Exception as e:
        email_client.handle_occured_exception(_SETUP, e)
        email_client.handle_resolved_exception(_SETUP)
