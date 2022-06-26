from packages.core.modules.vbdsd import VBDSD_Thread
import time

    
def test_vbdsd():
    """Pictures are saved in C:\pyra-4\runtime-data\vbdsd"""
    vbdsd = VBDSD_Thread()
    vbdsd.start()
    time.sleep(30)
    vbdsd.stop()
    

