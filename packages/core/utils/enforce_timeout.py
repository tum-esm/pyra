import signal
import time

# Used example from https://code-maven.com/python-timeout


class TimeOutException(Exception):
    pass


def _raise_timeout_exception(*args):
    raise TimeOutException()


def with_timeout(timeout_seconds: int):
    def with_fixed_timeout(function):
        def bounded_function(*args, **kwargs):
            signal.signal(signal.SIGALRM, _raise_timeout_exception)
            signal.alarm(timeout_seconds)
            function_result = function(*args, **kwargs)
            signal.alarm(0)
            return function_result

        return bounded_function

    return with_fixed_timeout


if __name__ == "__main__":

    @with_timeout(5)
    def example_function(start_value=1):
        n = start_value
        while True:
            print(f"n = {n}")
            n += 1
            time.sleep(1)

    try:
        example_function()
    except TimeOutException:
        print("function call 1 timed out")

    try:
        example_function(start_value=4)
    except TimeOutException:
        print("function call 2 timed out")
