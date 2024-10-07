import os
import sys
import time
from typing import Any, Optional
import psutil
import tum_esm_utils
from packages.core import types, utils, interfaces

logger = utils.Logger(origin="opus")


class DDEConnection:
    """TODO: docstring"""
    def __init__(self):
        self.server: Optional[Any] = None
        self.conversation: Optional[Any] = None

    def setup(self) -> None:
        """TODO: docstring"""
        assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"
        import dde  # type: ignore

        logger.info("Establishing new DDE connection")
        self.server = dde.CreateServer()  # type: ignore
        time.sleep(0.5)
        self.server.Create("Client")
        time.sleep(0.5)
        self.conversation = dde.CreateConversation(self.server)  # type: ignore
        self.logger.info("DDE connection established")
        time.sleep(0.5)

        for i in range(10):
            try:
                self.logger.info("Trying to connect to OPUS")
                self.conversation.ConnectTo("OPUS", "OPUS/System")
                assert self.conversation.Connected() == 1
                logger.info("Connected to OPUS DDE Server.")
            except:
                logger.info(
                    "Could not connect to OPUS DDE Server." +
                    (" Retrying in 10 seconds." if i < 9 else "")
                )
                if i == 9:
                    raise TimeoutError("Could not connect to OPUS DDE Server after 10 tries.")
                else:
                    time.sleep(10)

    def is_working(self) -> bool:
        """TODO: docstring"""
        if self.conversation is None:
            return False
        return self.conversation.Connected() == 1

    def teardown(self, logger: utils.Logger) -> None:
        """TODO: docstring"""
        if self.server is not None:
            logger.info("Destroying DDE connection")
            self.server.Shutdown()
            self.server.Destroy()
            self.server = None
            self.conversation = None
            logger.info("Destroyed DDE connection")

    def request(self, command: str) -> str:
        """TODO: docstring"""
        if self.conversation is None:
            self.setup()
        assert self.conversation is not None
        return self.conversation.Request(command)

