from packages.core.threads.helios_thread import HeliosThread
import time


def test_helios():
    """Pictures are saved in C:\pyra-4\runtime-data\helios"""
    helios = HeliosThread()
    helios.start()
    time.sleep(30)
    helios.stop()
