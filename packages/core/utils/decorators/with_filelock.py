import filelock

# FileLock = Mark, that a file is being used and other programs
# should not interfere. A file "*.lock" will be created and the
# existence of this file will make the wrapped function wait until
# it no longer exists.

# A timeout of -1 means that the code waits forever


def with_filelock(file_lock_path, timeout=-1):
    def with_fixed_filelock(function):
        def locked_function(*args, **kwargs):
            with filelock.FileLock(file_lock_path, timeout=timeout):
                return function(*args, **kwargs)

        return locked_function

    return with_fixed_filelock
