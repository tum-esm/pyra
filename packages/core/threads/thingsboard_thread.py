from .abstract_thread import AbstractThread
from packages.core import types, utils, interfaces
from tb_device_mqtt import TBDeviceMqttClient  # type: ignore
import threading
import time


class ThingsBoardThread(AbstractThread):

    @staticmethod
    def should_be_running(config: types.Config) -> bool:
        """Based on the config, should the thread be running or not?"""

        # only publish data when Thingsboard is configured
        if config.thingsboard is None:
            return False

        # don't publish in test mode
        if config.general.test_mode:
            return False

        return True

    @staticmethod
    def get_new_thread_object() -> threading.Thread:
        """Return a new thread object that is to be started."""
        return threading.Thread(target=ThingsBoardThread.main, daemon=True)

    @staticmethod
    def main(headless: bool = False) -> None:
        """Main entrypoint of the thread. In headless mode,
        don't write to log files but print to console."""

        logger = utils.Logger(origin="thingsboard", just_print=headless)
        config = types.Config.load()
        assert config.thingsboard is not None

        # initialize MQTT client
        client = TBDeviceMqttClient(
            config.thingsboard.host, username=config.thingsboard.access_token
        )

        # connect to MQTT broker
        if config.thingsboard.ca_cert:
            client.connect(tls=True, ca_certs=config.thingsboard.ca_cert)
        else:
            client.connect()

        logger.info("Succesfully connected to Thingsboard Broker.")

        while True:
            # Read latest config
            config = types.Config.load()
            if not ThingsBoardThread.should_be_running(config):
                logger.info("ThingsboardThread shall not be running anymore.")
                client.disconnect()
                return

            # publish if client is connected
            if not client.is_connected():
                logger.warning(
                    "Client is currently not connected. Waiting for reconnect."
                )
            else:
                # read latest state file
                current_state = interfaces.StateInterface.load_state()

                # TODO: inset state file parameters into telemetry payload
                telemetry_with_ts = {
                    "ts": int(round(time.time() * 1000)),
                    "values": {"temperature": 42.1, "humidity": 70},
                }

                try:
                    # Sending telemetry without checking the delivery status (QoS0)
                    client.send_telemetry(telemetry_with_ts)
                except Exception as e:
                    logger.exception(e)
                    logger.info("Failed to publish last telemetry data.")

            time.sleep(config.general.seconds_per_core_interval)
