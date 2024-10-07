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


class OpusProgram:
    """TODO: docstring"""
    @staticmethod
    def start(config: types.Config) -> None:
        """Starts the OPUS.exe with os.startfile()."""

        interfaces.ActivityHistoryInterface.add_datapoint(opus_startups=1)

        # works only >= python3.10 because it requires the "cwd" argument
        assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"
        assert sys.version_info.major >= 3 and sys.version_info.minor >= 10, "this function requires python >= 3.10"

        os.startfile(  # type: ignore
            os.path.basename(config.opus.executable_path.root),
            cwd=os.path.dirname(config.opus.executable_path.root),
            arguments=f"/LANGUAGE=ENGLISH /DIRECTLOGINPASSWORD={self.config.opus.username}@{self.config.opus.password}",
            show_cmd=2,
        )
        tum_esm_utils.timing.wait_for_condition(
            is_successful=OpusProgram.is_running,
            timeout_message="OPUS.exe did not start within 90 seconds.",
            timeout_seconds=90,
            check_interval_seconds=8,
        )

    @staticmethod
    def is_running() -> bool:
        """Checks if OPUS is already running by searching for processes with
        the executable `opus.exe` or `OpusCore.exe`

        Returns: `True` if Application is currently running and `False` if not."""

        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    return True
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass

        return False

    @staticmethod
    def stop(dde_connection: Optional[DDEConnection] = None) -> None:
        """Closes OPUS via DDE/force kills it via psutil. If no DDEConnection
        is provided, the function will force kill OPUS right away."""

        if (dde_connection is not None) and dde_connection.is_working():
            assert sys.platform == "win32", f"this function cannot be run on platform {sys.platform}"

            logger.info(f"Requesting to stop OPUS via DDE")
            dde_connection.request("CLOSE_OPUS")

            logger.info(f"Waiting for OPUS to close gracefully")
            try:
                tum_esm_utils.timing.wait_for_condition(
                    is_successful=lambda: not OpusMeasurement.opus_is_running(),
                    timeout_message="OPUS.exe did not stop within 60 seconds.",
                    timeout_seconds=60,
                    check_interval_seconds=4,
                )
                logger.info("OPUS.exe stopped successfully.")
                return
            except TimeoutError:
                logger.warning("OPUS.exe did not stop gracefully within 60 seconds.")

        for p in psutil.process_iter():
            try:
                if p.name() in ["opus.exe", "OpusCore.exe"]:
                    p.kill()
            except (
                psutil.AccessDenied,
                psutil.ZombieProcess,
                psutil.NoSuchProcess,
                IndexError,
            ):
                pass


