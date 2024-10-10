import pytest
from packages.core import types, threads, utils


@pytest.mark.integration
def test_opus_connection() -> None:
    config = types.Config.load()
    logger = utils.Logger(origin="opus", just_print=True)
    try:
        threads.OpusThread.test_setup(config, logger)
    finally:
        threads.opus_thread.OpusProgram.stop(logger)
