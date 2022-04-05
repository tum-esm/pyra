Pyra-Core is the program that is constantly running on the enclosure and operates it.

<br/>

All scripts that output statements in the process should use the `Logger` class:

```python
from packages.core.logger import Logger

Logger.debug("...")
Logger.info("...")
Logger.warning("...")
Logger.critical("...")
Logger.error("...")
```

You can set a custom log origin:

```python
# Will log from a "pyra.core" origin
Logger.debug("...")

# Will log from a "pyra.core.camtracker" origin
Logger.debug("...", origin="pyra.core.camtracker")
```

Messages from all log levels can be found in `logs/debug.log`, messages from levels info/warning/critical/error can be found in `logs/info.log`.
