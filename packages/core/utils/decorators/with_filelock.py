import filelock
from typing import Any, Callable, TypeVar, cast
from functools import wraps

# FileLock = Mark, that a file is being used and other programs
# should not interfere. A file "*.lock" will be created and the
# existence of this file will make the wrapped function wait until
# it no longer exists.

# A timeout of -1 means that the code waits forever

# def with_filelock(file_lock_path: str, timeout: float = -1):
#     def with_fixed_filelock(f):
#         def locked_function(*args, **kwargs):
#             with filelock.FileLock(file_lock_path, timeout=timeout):
#                 return function(*args, **kwargs)
#         return locked_function
#     return with_fixed_filelock
#
# typing of higher level decorators:
# https://github.com/python/mypy/issues/1551#issuecomment-253978622

F = TypeVar("F", bound=Callable[..., Any])


class with_filelock:
    def __init__(self, file_lock_path: str, timeout: float = -1) -> None:
        self.file_lock_path = file_lock_path
        self.timeout = timeout

    def __call__(self, f: F) -> F:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            with filelock.FileLock(self.file_lock_path, timeout=self.timeout):
                return function(*args, **kwargs)

        return cast(F, wrapper)
