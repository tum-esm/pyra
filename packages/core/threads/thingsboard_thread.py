from .abstract_thread import AbstractThread
from packages.core import types, utils, interfaces
from tb_device_mqtt import TBDeviceMqttClient  # type: ignore
import threading
import time
from typing import Dict, Union, Optional


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
        if config.thingsboard.ca_cert is not None:
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
                state: Dict[str, Optional[Union[str, bool, int, float]]] = {
                    "state_file_last_updated":
                        str(current_state.last_updated),
                    "helios_indicates_good_conditions":
                        current_state.helios_indicates_good_conditions,
                    "measurements_should_be_running":
                        current_state.measurements_should_be_running,
                    "os_memory_usage":
                        current_state.operating_system_state.memory_usage,
                    "os_filled_disk_space_fraction":
                        current_state.operating_system_state.
                        filled_disk_space_fraction,
                    "enclosure_actor_fan_speed":
                        current_state.plc_state.actors.fan_speed,
                    "enclosure_actor_current_angle":
                        current_state.plc_state.actors.current_angle,
                    "enclosure_control_auto_temp_mode":
                        current_state.plc_state.control.auto_temp_mode,
                    "enclosure_control_manual_control":
                        current_state.plc_state.control.manual_control,
                    "enclosure_control_manual_temp_mode":
                        current_state.plc_state.control.manual_temp_mode,
                    "enclosure_control_sync_to_tracker":
                        current_state.plc_state.control.sync_to_tracker,
                    "enclosure_sensor_humidity":
                        current_state.plc_state.sensors.humidity,
                    "enclosure_sensor_temperature":
                        current_state.plc_state.sensors.temperature,
                    "enclosure_state_cover_closed":
                        current_state.plc_state.state.cover_closed,
                    "enclosure_state_motor_failed":
                        current_state.plc_state.state.motor_failed,
                    "enclosure_state_rain":
                        current_state.plc_state.state.rain,
                    "enclosure_state_reset_needed":
                        current_state.plc_state.state.reset_needed,
                    "enclosure_state_ups_alert":
                        current_state.plc_state.state.ups_alert,
                    "enclosure_power_heater":
                        current_state.plc_state.power.heater,
                    "enclosure_power_spectrometer":
                        current_state.plc_state.power.spectrometer,
                }

                telemetry_with_ts = {
                    "ts": int(round(time.time() * 1000)),
                    "values": state,
                }

                try:
                    # Sending telemetry without checking the delivery status (QoS1)
                    result = client.send_telemetry(telemetry_with_ts)
                    logger.info(f"Published with result: {result}")
                except Exception as e:
                    logger.exception(e)
                    logger.info("Failed to publish last telemetry data.")

            if config.thingsboard is not None:
                time.sleep(config.thingsboard.seconds_per_publish_interval)
