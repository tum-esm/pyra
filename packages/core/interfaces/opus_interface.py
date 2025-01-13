from typing import Optional
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
