from packages.core.modules.vbdsd import VBDSD_Thread

    
def test_vbdsd():
    """Pictures are saved in C:\pyra-4\runtime-data\vbdsd"""
    vbdsd = VBDSD_Thread()
    vbdsd.main(infinite_loop=False)
    

