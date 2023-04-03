import filelock
from typing import Any, Callable, TypeVar, cast
from functools import wraps

# typing of higher level decorators:
# https://github.com/python/mypy/issues/1551#issuecomment-253978622
F = TypeVar("F", bound=Callable[..., Any])

# TODO: use tum_esm_utils


class with_filelock:
    """Decorator that wraps a semaphor around a function.

    FileLock = Mark, that a file is being used and other programs
    should not interfere. A file "*.lock" will be created and the
    content of this file will make the wrapped function possibly
    wait until other programs are done using it.

    See https://en.wikipedia.org/wiki/Semaphore_(programming)
    """

    def __init__(self, file_lock_path: str, timeout: float = -1) -> None:
        """A timeout of -1 means that the code waits forever"""
        self.file_lock_path: str = file_lock_path
        self.timeout: float = timeout

    def __call__(self, f: F) -> F:
        @wraps(f)
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            with filelock.FileLock(self.file_lock_path, timeout=self.timeout):
                return f(*args, **kwargs)

        return cast(F, wrapper)
