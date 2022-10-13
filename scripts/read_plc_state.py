import json
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)

from packages.core import types, interfaces


class PLCConnection:
    def __init__(self, initial_config: types.ConfigDict):
        self.config = initial_config
        self.initialized = False
        self.plc_interface = interfaces.PLCInterface(
            self.config["tum_plc"]["version"], self.config["tum_plc"]["ip"]
        )

    def read(self) -> types.PlcStateDict:
        self.plc_interface.connect()
        plc_state = self.plc_interface.read()
        self.plc_interface.disconnect()

        return plc_state


if __name__ == "__main__":
    config = interfaces.ConfigInterface.read()
    plc_connection = PLCConnection(config)
    plc_state = plc_connection.read()

    print(json.dumps(plc_state, indent=4))
