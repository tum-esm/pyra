from packages.core.modules import vbdsd

def test_cam():
    cam = vbdsd._VBDSD()
    cam.init_cam()
    
"""
def test_vbdsd():
    vbdsd.main(infinite_loop=False)
    assert False
"""
