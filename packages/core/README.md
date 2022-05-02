# `pyra-core`

`pyra-core` is the program that is constantly running on the enclosure and operates it.

<br/>
<br/>

## Logging

All scripts that output messages at runtime should use the `Logger` class:

```python
from packages.core.utils.logger import Logger

logger = Logger()

logger.debug("...")
logger.info("...")
logger.warning("...")
logger.critical("...")
logger.error("...")


# By default, it will log from a "pyra.core" origin
logger = Logger()

# Here, it will log from a "pyra.core.camtracker" origin
logger = Logger(origin="pyra.core.camtracker")
```

Messages from all log levels can be found in `logs/debug.log`, messages from levels INFO/WARNING/CRITICAL/ERROR can be found in `logs/info.log`.
