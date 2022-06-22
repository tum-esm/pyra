**CLI tasks**

-   [x] merged config
-   [x] add default
-   [x] test config
-   [x] test core
-   [ ] test logs (later, when api is completer)

**UI tasks**

-   [x] merged config
-   [x] new measurement triggers formats
-   [x] nullable tum-plc/vbdsd
-   [x] start/stop pyra-core buttons
-   [x] decision mode toggle
-   [x] manual decision toggle
-   [ ] read automatic/cli decision
-   [ ] read state and config periodically

```
Traceback (most recent call last):
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/__init__.py\", line 23, in <module>
    from . import multiarray
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/multiarray.py\", line 10, in <module>
    from . import overrides
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/overrides.py\", line 6, in <module>
    from numpy.core._multiarray_umath import (
ImportError: dlopen(/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/_multiarray_umath.cpython-310-darwin.so, 0x0002): tried: '/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/_multiarray_umath.cpython-310-darwin.so' (mach-o file, but is an incompatible architecture (have 'arm64', need 'x86_64'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/__init__.py\", line 144, in <module>
    from . import core
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/__init__.py\", line 49, in <module>
    raise ImportError(msg)
ImportError:

IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!

Importing the numpy C-extensions failed. This error can happen for
many reasons, often due to issues with your setup or how NumPy was
installed.

We have compiled some common reasons and troubleshooting tips at:

    https://numpy.org/devdocs/user/troubleshooting-importerror.html

Please note and check the following:

  * The Python version is: Python3.10 from \"/Users/moritz/Documents/research/pyra/.venv/bin/python\"
  * The NumPy version is: \"1.22.3\"

and make sure that they are the versions you expect.
Please carefully study the documentation linked above for further help.

Original error was: dlopen(/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/_multiarray_umath.cpython-310-darwin.so, 0x0002): tried: '/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/numpy/core/_multiarray_umath.cpython-310-darwin.so' (mach-o file, but is an incompatible architecture (have 'arm64', need 'x86_64'))

Traceback (most recent call last):
  File \"/Users/moritz/Documents/research/pyra/packages/cli/main.py\", line 9, in <module>
    from packages.cli.commands.config import config_command_group
  File \"/Users/moritz/Documents/research/pyra/packages/__init__.py\", line 1, in <module>
    from . import cli
  File \"/Users/moritz/Documents/research/pyra/packages/cli/__init__.py\", line 1, in <module>
    from . import main
  File \"/Users/moritz/Documents/research/pyra/packages/cli/main.py\", line 9, in <module>
    from packages.cli.commands.config import config_command_group
  File \"/Users/moritz/Documents/research/pyra/packages/cli/commands/config.py\", line 14, in <module>
    from packages.core.utils import Validation
  File \"/Users/moritz/Documents/research/pyra/packages/core/__init__.py\", line 1, in <module>
    from .utils import validation
  File \"/Users/moritz/Documents/research/pyra/packages/core/utils/__init__.py\", line 4, in <module>
    from .astronomy import Astronomy
  File \"/Users/moritz/Documents/research/pyra/packages/core/utils/astronomy.py\", line 1, in <module>
    import astropy.coordinates as astropy_coordinates
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/__init__.py\", line 41, in <module>
    from . import config as _config  # noqa: E402
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/config/__init__.py\", line 10, in <module>
    from .configuration import *
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/config/configuration.py\", line 24, in <module>
    from astropy.utils import find_current_module, silence
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/utils/__init__.py\", line 17, in <module>
    from .codegen import *  # noqa
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/utils/codegen.py\", line 13, in <module>
    from .introspection import find_current_module
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/utils/introspection.py\", line 14, in <module>
    from astropy.utils.decorators import deprecated_renamed_argument
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/utils/decorators.py\", line 14, in <module>
    from .exceptions import (AstropyDeprecationWarning, AstropyUserWarning,
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/astropy/utils/exceptions.py\", line 11, in <module>
    from erfa import ErfaError, ErfaWarning  # noqa
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/erfa/__init__.py\", line 5, in <module>
    from .version import version as __version__  # noqa
  File \"/Users/moritz/Documents/research/pyra/.venv/lib/python3.10/site-packages/erfa/version.py\", line 25, in <module>
    from . import ufunc
ImportError: numpy.core.multiarray failed to import
```
