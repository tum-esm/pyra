import threading

import pytest

from packages.core import types
from packages.core.utils.functions import timeout_lock


@pytest.mark.ci
def test_failed_lock_acquisition_skips_body() -> None:
    """A timed-out acquisition must leave the protected code untouched and the owner locked."""
    lock = threading.Lock()
    lock.acquire()
    try:
        with pytest.raises(types.LockTimeoutError):
            with timeout_lock(lock, timeout=0, label="test lock"):
                pytest.fail("Entered without acquiring the lock")
        assert lock.locked()
    finally:
        lock.release()


@pytest.mark.ci
def test_body_timeout_releases_lock_without_reclassification() -> None:
    """A timeout inside protected code is not a lock failure, and must still release the lock."""
    lock = threading.Lock()
    error = TimeoutError("operation timed out")
    with pytest.raises(TimeoutError) as caught:
        with timeout_lock(lock, timeout=0, label="test lock"):
            raise error
    assert caught.value is error
    assert not lock.locked()
