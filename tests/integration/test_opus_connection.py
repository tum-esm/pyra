from typing import Generator
import psutil
import pytest
from packages.core import types, modules


@pytest.fixture(scope="function")
def terminate_opus() -> Generator[None, None, None]:
    yield
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


@pytest.mark.integration
def test_opus_connection(terminate_opus: None) -> None:
    config = types.Config.load()
    modules.opus_measurement.OpusMeasurement(config).test_setup()
