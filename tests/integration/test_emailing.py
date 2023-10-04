import pytest
from packages.core import utils, types


@pytest.mark.integration
def test_emailing() -> None:
    config = types.Config.load()

    try:
        raise Exception("some exception name")
    except Exception as e:
        utils.ExceptionEmailClient.handle_occured_exception(config, e)
        utils.ExceptionEmailClient.handle_resolved_exception(config)
