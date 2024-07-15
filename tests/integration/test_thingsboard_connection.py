import pytest
from packages.core import types


@pytest.mark.integration
def test_uploading() -> None:
    config = types.Config.load()
    if config.upload is None:
        return

    raise Exception("Could not establish a connection to ThingsBoard.")
