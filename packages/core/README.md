Pyra-Core is the program that is constantly running on the enclosure and operates it.

<br/>

All scripts that output statements in the process should use the `logging` module:

```python
import logging
logger = logging.getLogger("pyra.core")

logger.debug("...")
logger.info("...")
logger.warning("...")
logger.critical("...")
logger.error("...")
```

Messages from all log levels can be found in `logs/debug.log`, messages from levels info/warning/critical/error can be found in `logs/info.log`.
