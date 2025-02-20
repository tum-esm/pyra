import pytest
from packages.core import utils, types


@pytest.mark.order(2)
@pytest.mark.integration
def test_emailing() -> None:
    config = types.Config.load()
    utils.ExceptionEmailClient.send_test_email(config)
