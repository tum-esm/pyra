import filelock
from typing import Any, Callable, TypeVar, cast

# FileLock = Mark, that a file is being used and other programs
# should not interfere. A file "*.lock" will be created and the
# existence of this file will make the wrapped function wait until
# it no longer exists.

# A timeout of -1 means that the code waits forever

F = TypeVar("F", bound=Callable[..., Any])


def with_filelock(file_lock_path: str, timeout: float = -1):
    def with_fixed_filelock(function: F) -> F:
        def locked_function(*args, **kwargs):
            with filelock.FileLock(file_lock_path, timeout=timeout):
                return function(*args, **kwargs)

        return cast(F, locked_function)

    return with_fixed_filelock
