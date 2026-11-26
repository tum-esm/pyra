import threading
from unittest.mock import Mock, call

import pytest

from packages.core import types
from packages.core.threads import ExceptionEmailThread, exception_email_thread
from tests.fixtures import SAMPLE_CONFIG

pytestmark = pytest.mark.ci


class _StopThread(BaseException):
    pass


@pytest.fixture()
def worker_io(monkeypatch: pytest.MonkeyPatch) -> tuple[Mock, Mock, Mock]:
    monkeypatch.setattr(exception_email_thread.utils, "Logger", Mock())
    monkeypatch.setattr(exception_email_thread.tum_esm_utils.sqlitelock, "SQLiteLock", Mock())
    load_config = Mock(return_value=SAMPLE_CONFIG.model_copy(deep=True))
    notify = Mock()
    sleep = Mock(side_effect=[None, _StopThread()])
    monkeypatch.setattr(types.Config, "load", load_config)
    monkeypatch.setattr(
        exception_email_thread.interfaces.ExceptionsInterface,
        "update_exception_notifications",
        notify,
    )
    monkeypatch.setattr(exception_email_thread.time, "sleep", sleep)
    return load_config, notify, sleep


@pytest.mark.parametrize("enabled", [False, True])
def test_always_runs(enabled: bool) -> None:
    """Keep cleanup running even in test mode or with email notifications disabled."""
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.general.test_mode = not enabled
    config.error_email.notify_recipients = enabled
    assert ExceptionEmailThread.should_be_running(config, Mock())


def test_refreshes_config(worker_io: tuple[Mock, Mock, Mock]) -> None:
    """Apply live email settings and polling changes without restarting the worker."""
    load_config, notify, sleep = worker_io
    first = SAMPLE_CONFIG.model_copy(deep=True)
    second = first.model_copy(deep=True)
    second.general.seconds_per_core_iteration = 60
    second.error_email.notify_recipients = not first.error_email.notify_recipients
    load_config.side_effect = [first, second]

    with pytest.raises(_StopThread):
        ExceptionEmailThread.main(threading.Lock())

    assert [c.args[2] for c in notify.call_args_list] == [first, second]
    assert sleep.call_args_list == [call(first.general.seconds_per_core_iteration), call(60)]


@pytest.mark.parametrize("failure", ["config", "notification"])
def test_continues_after_error(worker_io: tuple[Mock, Mock, Mock], failure: str) -> None:
    """A config or notification error must back off and leave the worker able to continue."""
    load_config, notify, sleep = worker_io
    config = load_config.return_value
    if failure == "config":
        load_config.side_effect = [ValueError("invalid config"), config]
    else:
        notify.side_effect = [RuntimeError("state unavailable"), None]

    with pytest.raises(_StopThread):
        ExceptionEmailThread.main(threading.Lock())

    assert load_config.call_count == 2
    assert notify.call_count == (1 if failure == "config" else 2)
    assert sleep.call_args_list == [call(15), call(config.general.seconds_per_core_iteration)]
