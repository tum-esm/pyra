import pytest
from packages.core import types
from tb_device_mqtt import TBDeviceMqttClient  # type: ignore
import time


@pytest.mark.integration
def test_thingsboard_connection() -> None:
    config = types.Config.load()
    if config.thingsboard is None:
        return

    # initialize MQTT client
    client = TBDeviceMqttClient(
        config.thingsboard.host, username=config.thingsboard.access_token
    )

    client.connect()
    time.sleep(2)
    assert client.is_connected()
    client.disconnect()
