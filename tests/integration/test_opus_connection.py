import pytest
from packages.core import types, threads


@pytest.mark.integration
def test_opus_connection() -> None:
    config = types.Config.load()
    try:
        threads.OpusThread.test_setup(config)
    finally:
        threads.opus_thread.OpusProgram.stop()
