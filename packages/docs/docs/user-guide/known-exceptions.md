# Known Exceptions

Below you can find a list of known exceptions that can be raised by Pyra. These can happen if OPUS does not start properly, CamTracker doesnt behave as expected, the enclosure PLCs are not reachable, or the system disk is full, and so on. For each of these exceptions you can configure whether you want to receive an email notification and how long Pyra should wait before sending the email.

"Patience" is the time, in seconds, that a recorded fault must remain unresolved before Pyra will send an email notification. I.e. for urgent errors like "rain detected but cover is not closed" you can send an email right away. But for less urgent errors that might self-resolve, like "OPUS did not start properly", you can configure a longer patience time so that you only get an email if the error persists for a while.

If the station is offline when an exception occurs, it will continue to operate and try to self-resolve the issue on its own. Once the station is back online, it will send an email notification if the exception is still unresolved.

## Exception reference

### `cover-did-not-open`

Enclosure cover did not open.

This error might have been caused by the enclosures rain sensor being triggered long enough to cause the cover to be closed but too short for PYRA to read from rain sensor in time. This is usually self-resolving after some time since the cover either opens or the rain sensor is triggered long enough for PYRA to read it. If not resolving, the cover might be stuck/the motor might be broken and needs to be checked.

**Default email patience:** 300 seconds.

### `cover-did-not-close`

Enclosure cover did not close.

Even though Pyra requested the enclosure cover to close, it did not reach the closed position. The cover could be blocked or the motor could have an issue. Please check the enclosure cover and motor.

**Default email patience:** 90 seconds.

### `storage-error`

The system disk is more than 90% full.

The system disk is more than 90% full. This can make the operating system unstable and might indicate that the system is producing data faster than it can upload it.

**Default email patience:** 300 seconds.

### `low-energy-error`

The system battery level is below 30%.

The system battery level is below 30%. Check the power supply.

**Default email patience:** 300 seconds.

### `pyra-core-crashed`

Pyra Core is not running and has not been shut down properly.

Pyra core did not shutdown with a graceful shutdown message. Normally this should only happen if the operating system forcefully killed the Pyra core process. This can also happen if the system lost power and booted back up. This error is usually raised by the Pyra UI calling "pyra-cli core is-running" to check whether a proper shutdown happened. It is automatically resolved when the Pyra core is starting again.

**Default email patience:** 300 seconds.

### `tum-enclosure-plc-connection-error`

Could not connect to TUM enclosure PLC.

PYRA could not establish a connection to the TUM enclosure PLC for several consecutive retries.

**Default email patience:** 300 seconds.

### `tum-enclosure-rain-detected-cover-not-closed`

Rain detected but cover is not closed.

The TUM enclosure reports rain, but the cover did not close yet.

**Default email patience:** 0 seconds.

### `tum-enclosure-plc-reset-failed`

TUM enclosure PLC reset was required but did not work

The TUM enclosure PLC reported that a reset was required but triggering the reset did not resolve the issue.

**Default email patience:** 300 seconds.

### `tum-enclosure-plc-error`

The TUM enclosure PLC responded unexpectedly.

Communication with the TUM enclosure PLC failed or a requested PLC value did not update as expected.

**Default email patience:** 300 seconds.

### `aemet-enclosure-datalogger-error`

The AEMET enclosure datalogger responded in an unexpected way.

Communication with the AEMET enclosure datalogger or related power plug failed, returned invalid data, or did not update as expected.

**Default email patience:** 300 seconds.

### `camtracker-configuration-error`

PYRA could not read the CamTracker configuration file.

PYRA could not read the CamTracker configuration file or determine the coordinates from it. Please make sure to configure the correct path for the CamTracker configuration file in the PYRA configuration.

**Default email patience:** 300 seconds.

### `helios-camera-error`

Helios camera is not working as expected.

Helios could not initialize the camera, determine usable exposure settings, open the camera, or take images. This issues is typically raised if the camera is not responding for a while.

**Default email patience:** 300 seconds.

### `opus-connection-error`

The OPUS HTTP interface is not reachable.

OPUS started, but the OPUS HTTP interface did not become reachable in time. This can happen if OPUS did not start properly (normally should not happen) or if the localhost is occupied by another application. You can check whether the latter is true by opening http://localhost:8080 in a web browser and checking whether any other application is running there.

**Default email patience:** 300 seconds.

### `em27-connection-error`

The EM27 HTTP interface is not reachable.

The EM27 web interface could not be reached under the configured IP.

**Default email patience:** 300 seconds.

### `lock-timeout-error`

PYRA could not acquire a required lock in time.

Pyra uses a lock file to ensure that only one thread can access certain resources at a time. If this lock cannot be acquired in time, this error is raised. In normal operation this should not happen. If you see this error, your computer might be under heavy load so that the operating system does not allow writing to a file in time. Or your disk might be 100% occupied.

**Default email patience:** 300 seconds.

### `unexpected-error`

An unexpected error occurred.

PYRA encountered an error that could not be assigned to a more specific sdocumented exception type. Refer to the traceback for the underlying cause.

**Default email patience:** 0 seconds.
