from packages.core.modules import vbdsd

    
def test_vbdsd():
    vbdsd = vbdsd.VBDSD_Thread()
    vbdsd.main(infinite_loop=False)
    assert False

