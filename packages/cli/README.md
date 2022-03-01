# Pyra CLI

Interacting with pyra from the command line (locally or via SSH). Here are some use cases of the CLI:

## 1. Running Pyra

-   Start/stop pyra-core
-   Check if pyra-core is running
-   Start/stop pyra-ui

Both pyra-core and pyra-ui should possibly run in the background without an attached terminal interface. On Linux one can use the `screen` utility for that, I don't know, wich tool on Windows to use for that.

## 2. Configuration

-   Set all variables in `config/parameters.default.json`, can be done anytime
-   Set all variables in `config/setup.default.json`, pyra-core should not be running
-   Validate the correctness of these two config-files, use the existing validation from pyra-core

Both config files should be locked during read operations so that pyra-core cannot stumble across an inconsistent config and pyra-cli does not modify the config during a read operation of pyra-core.

A semaphore on files can probably be implemented using the python module `filelock` https://pythonawesome.com/a-platform-independent-file-lock-for-python/.

## 3. Check State of Measurements

-   Basic statistics about the system (system resources usage, etc.)
-   Basic statistics about the measurements (How many measurements today, weather conditions, etc.)
