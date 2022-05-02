
from packages.core.main import load_config
from packages.core.modules import vbdsd

def test_vbdsd():
    _SETUP, _PARAMS = load_config()
    
    vbdsd.main(infinite_loop = False)
    
    assert(False)

