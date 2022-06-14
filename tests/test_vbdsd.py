from packages.core.modules import vbdsd


def test_vbdsd():
    vbdsd.main(infinite_loop=False)
    assert False
