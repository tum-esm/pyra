# `pyra-core`

`pyra-core` is the program that is constantly running on the enclosure and operates it.

<br/>
<br/>

## Logging

All scripts that output messages at runtime should use the `Logger` class:

```python
from packages.core.utils.logger import Logger

Logger.debug("...")
Logger.info("...")
Logger.warning("...")
Logger.critical("...")
Logger.error("...")

# By default, it will log from a "pyra.core" origin
Logger.debug("...")

# Here, it will log from a "pyra.core.camtracker" origin
Logger.debug("...", origin="pyra.core.camtracker")
```

Messages from all log levels can be found in `logs/debug.log`, messages from levels INFO/WARNING/CRITICAL/ERROR can be found in `logs/info.log`.
