from typing import Optional
import time
import socket


class OPUSHTTPInterface:
    """Interface to the OPUS HTTP interface.

    It uses the socket library, because the HTTP interface of OPUS does not
    reuturn valid HTTP/1 or HTTP/2 headers. It opens and closes a new socket
    because OPUS closes the socket after the answer has been sent."""

    @staticmethod
    def _request(request: str) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect(("localhost", 80))
            s.sendall(f"GET /OpusCommand.htm?{request}\r\nHost: localhost\r\n\r\n".encode("utf-8"))
            answer = s.recv(4096).decode("utf-8").strip("\r\n\t ")
            s.close()
            return answer
        except Exception as e:
            return None

    @staticmethod
    def get_version_number() -> Optional[str]:
        """Get the version number of OPUS via the HTTP interface."""
        return OPUSHTTPInterface._request("GET_VERSION_EXTENDED")


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
