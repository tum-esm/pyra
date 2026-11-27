import pytest
from packages.core import utils, types


@pytest.mark.order(2)
@pytest.mark.integration
def test_emailing() -> None:
    """Send a test message through the station's configured SMTP server."""
    config = types.Config.load()
    utils.ExceptionEmailClient.send_test_email(config)
