from typing import Optional
import os
import time
import socket


class OPUSHTTPInterface:
    """Interface to the OPUS HTTP interface.

    It uses the socket library, because the HTTP interface of OPUS does not
    reuturn valid HTTP/1 or HTTP/2 headers. It opens and closes a new socket
    because OPUS closes the socket after the answer has been sent."""

    @staticmethod
    def _request(request: str) -> list[str]:
        answer_lines: Optional[list[str]] = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8)
            s.connect(("localhost", 80))
            url = f"/OpusCommand.htm?{request.replace(' ', '%20')}"
            s.sendall(f"GET {url}\r\nHost: localhost\r\n\r\n".encode("utf-8"))
            answer = s.recv(4096).decode("utf-8").strip("\r\n\t ")
            answer_lines = [l.strip(" \r\t") for l in answer.split("\n")]
            answer_lines = [l for l in answer_lines if len(l) > 0]
            s.close()
            return answer_lines
        except:
            raise ConnectionError(
                f"Invalid response from OPUS HTTP interface: "
                + ("no answer" if answer_lines is None else str(answer_lines))
            )

    @staticmethod
    def get_version_number() -> str:
        """Get the version number of OPUS via the HTTP interface."""

        answer = OPUSHTTPInterface._request("GET_VERSION_EXTENDED")
        try:
            assert len(answer) == 1
            return answer[0]
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def is_working() -> bool:
        """Check if the OPUS HTTP interface is working. Does NOT raise a ConnectionError
        but only returns `True` or `False`."""

        try:
            answer = OPUSHTTPInterface._request("COMMAND_SAY hello")
            assert len(answer) == 1
            assert answer[0] == "hello"
            return True
        except:
            return False

    @staticmethod
    def get_main_thread_id() -> int:
        """Get the main thread ID of OPUS."""

        answer = OPUSHTTPInterface._request("FIND_FUNCTION 0")
        try:
            assert len(answer) == 2
            assert answer[0] == "OK"
            return int(answer[1])
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def some_macro_is_running() -> bool:
        """Check if any macro is currently running in OPUS.

        In theory, we could also check whether the correct macro is running using
        `READ_PARAMETER MPT` and `READ_PARAMETER MFN`. However, these variables do
        not seem to be updated right away, so we cannot rely on them."""

        main_thread_id = OPUSHTTPInterface.get_main_thread_id()
        active_thread_ids: set[int] = set()

        # some common functions executed inside Macro routines that take some time
        common_functions = [
            "MeasureReference",
            "MeasureSample",
            "MeasureRepeated",
            "MeasureRapidTRS",
            "MeasureStepScanTrans",
            "UserDialog",
            "Baseline",
            "PeakPick",
            "Timer",
            "SendCommand",
        ]

        # check twice for any thread that is executing a common function
        for i in range(2):
            for function in common_functions:
                answer = OPUSHTTPInterface._request(f"FIND_FUNCTION {function}")
                try:
                    assert len(answer) >= 1
                    assert answer[0] == "OK"
                    for thread_id in answer[1:]:
                        active_thread_ids.add(int(thread_id))
                except:
                    raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")
            if i == 0:
                time.sleep(3)

        # the main thread always runs some common functions for some reason
        if main_thread_id in active_thread_ids:
            active_thread_ids.remove(main_thread_id)

        # if there is any thread that is not the main thread, then a macro is running
        return len(active_thread_ids) > 0

    @staticmethod
    def get_loaded_experiment() -> Optional[str]:
        """Get the path to the currently loaded experiment."""

        # Set the parameter mode (opus vs. file parameters)
        answer1 = OPUSHTTPInterface._request("OPUS_PARAMETERS")
        try:
            assert len(answer1) == 1
            assert answer1[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer1}")

        # Get the path to the experiment file
        xpp_answer = OPUSHTTPInterface._request("READ_PARAMETER XPP")
        try:
            assert len(xpp_answer) == 2
            assert xpp_answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {xpp_answer}")

        # Get the name of the experiment file
        exp_answer = OPUSHTTPInterface._request("READ_PARAMETER EXP")
        try:
            assert len(exp_answer) == 2
            assert exp_answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {exp_answer}")

        return os.path.join(xpp_answer[1], exp_answer[1])

    @staticmethod
    def load_experiment(experiment_path: str) -> bool:
        """Load an experiment file into OPUS."""

        answer = OPUSHTTPInterface._request(f"LOAD_EXPERIMENT {experiment_path}")
        try:
            assert answer is not None
            assert len(answer) == 1
            assert answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def start_macro(macro_path: str) -> int:
        """Start a macro in OPUS. Returns the macro ID."""

        answer = OPUSHTTPInterface._request(f"RUN_MACRO {macro_path}")
        try:
            assert len(answer) == 2
            assert answer[0] == "OK"
            return int(answer[1])
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def macro_is_running(macro_id: int) -> bool:
        """Check if the given macro is running."""

        answer = OPUSHTTPInterface._request(f"MACRO_RESULTS {macro_id}")
        # The OPUS documentation is ambiguous about the return value. It
        # seems that 0 means "there is no result yet", i.e. the macro is
        # still running
        try:
            assert len(answer) == 2
            assert answer[0] == "OK"
            return int(answer[1]) == 0
        except:
            return ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def stop_macro(macro_path: str) -> None:
        """Stop a macro in OPUS."""

        answer = OPUSHTTPInterface._request(f"KILL_MACRO {os.path.basename(macro_path)}")
        try:
            assert len(answer) == 1
            assert answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def unload_all_files() -> None:
        """Unload all files in OPUS. This should be done before closing it."""

        answer = OPUSHTTPInterface._request("COMMAND_LINE UnloadAll()")
        try:
            assert len(answer) == 1
            assert answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")

    @staticmethod
    def close_opus() -> None:
        """Close OPUS."""

        answer = OPUSHTTPInterface._request("CLOSE_OPUS")
        try:
            assert len(answer) == 1
            assert answer[0] == "OK"
        except:
            raise ConnectionError(f"Invalid response from OPUS HTTP interface: {answer}")


if __name__ == "__main__":
    t1 = time.time()
    print(OPUSHTTPInterface.get_version_number())
    t2 = time.time()
    print(OPUSHTTPInterface.get_version_number())
    t3 = time.time()
    print(OPUSHTTPInterface.get_version_number())
    t4 = time.time()

    print(f"Request 1: {t2 - t1:.6f}")
    print(f"Request 2: {t3 - t2:.6f}")
    print(f"Request 3: {t4 - t3:.6f}")

    print(OPUSHTTPInterface.is_working())
    print(OPUSHTTPInterface.get_main_thread_id())
