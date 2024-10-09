import pytest
from packages.core import types, threads


@pytest.mark.integration
def test_opus_connection() -> None:
    config = types.Config.load()
    try:
        threads.OpusControlThread.test_setup(config)
    finally:
        threads.opus_control_thread.OpusProgram.stop()
