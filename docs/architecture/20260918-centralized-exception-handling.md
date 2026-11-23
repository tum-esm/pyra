# Central Exception Handling

PYRA now uses `KNOWN_EXCEPTIONS` as the canonical catalog for exceptions that are persisted and reported. Each catalog entry has a stable identifier, subject, description, and patience bounds. Expected failures use their specific catalog entry, while unexpected failures use `UNEXPECTED_ERROR` and include their traceback.

`ExceptionsInterface` is the only interface used by Core threads and the CLI to change exception state:

- `add_exception(origin, exception_type, traceback=None, details=None)` adds a catalogued exception and prevents duplicate active records.
- `resolve_exception(origin, exception_type=None, exclude_exception_types=None)` resolves one type or every active exception from an origin, optionally preserving selected types.
- `update_exception_notifications(...)` emails exceptions once their configured patience has elapsed, removes cleared records, retries failed notifications, and sends a recovery email when all email-enabled exceptions have cleared.

Persistent exception records contain the catalog metadata, optional details and traceback, and Unix timestamps for when they were raised, notified, and cleared. The occurrence email renders the description, details, and traceback as separate sections.

All previous direct exception-state mutations were migrated to this interface. Focused tests cover catalog validation, persistence, deduplication, resolution and exclusions, notification timing and retries, email rendering, and staggered resolution. Compatibility with old config or state files is not required on this development branch.

## Configurable email patience

`ExceptionPatienceConfig` explicitly lists configurable exception identifiers and their email delays in seconds. The default is 90 seconds for `COVER_DID_NOT_CLOSE`, zero for `TUM_ENCLOSURE_RAIN_DETECTED_COVER_NOT_CLOSED`, and 300 seconds for every other field. Any finite value from -1 through 86400 seconds (one day), inclusive, is allowed. Exactly -1 disables emails; values between -1 and zero are eligible on the next notification update. The config schema is independent of the exception catalog.

Override defaults in full or partial configuration using stable identifiers:

```json
{
  "error_email": {
    "exception_patience": {
      "opus-connection-error": 600,
      "cover-did-not-close": 90,
      "storage-error": -1
    }
  }
}
```

Omitting `exception_patience` or an individual identifier uses the explicit config field defaults. The default config JSON lists every supported key and its default value for the UI. Partial updates merge overrides by identifier. Unknown fields, nonfinite numbers, and values outside the allowed range are rejected. `-1` disables email reporting for that type. `UNEXPECTED_ERROR` is not configurable and always has zero email patience; an `unexpected-error` config key is rejected.

Patience starts at `raised_at`, when a fault is recorded. An active, unnotified exception is due when its age is greater than or equal to its effective patience. Zero means eligible on the next notification update. Configuration changes apply to existing active exceptions without resetting timestamps. Any exception without a configurable field uses 300 seconds, even if it exists in the catalog with different patience metadata, except `UNEXPECTED_ERROR`, which always uses zero.

Muted exceptions remain in state until resolved and are never marked notified merely because they are muted. They do not block recovery emails. After a prior occurrence email, clearing or muting the last email-enabled exception sends one recovery email: "All email-enabled exceptions have been resolved." Unmuting an unnotified exception uses its original age; unmuting an already-notified exception does not resend its occurrence email.

Connection timeouts, retry intervals, and other operational timing remain local and unchanged. Existing producer-side suppression also remains for now, so delays before recording a fault still add to email patience. No configuration or persisted-state migration is needed for this addition.

## Patience behavior at the initial migration

The following table records behavior before configurable patience was added: the migration introduced a shared five-minute email delay. References to "current behavior" in this table describe that migration snapshot; the configurable defaults and overrides above now replace its fixed 300-second delay.

| Exception or path | Before the migration | Current behavior |
| --- | --- | --- |
| Normal Core exception | The main loop emailed a newly added exception on its next iteration, with no general patience period. | Every active exception is emailed only after it has remained in state for more than 300 seconds. |
| `OPUS_CONNECTION_ERROR` | Starting the OPUS HTTP interface could wait up to 90 seconds. The first `ConnectionError` was then suppressed. An exception was added only if another connection error occurred within 10 minutes; after a gap longer than 10 minutes, the next error was treated as a new first occurrence and suppressed again. | Every `ConnectionError` is added immediately after the existing connection/start timeout and uses the shared 300-second notification delay. The 10-minute repeat window was removed. |
| OPUS resolution | OPUS exceptions were not cleared until a restarted OPUS thread had run successfully for at least 180 seconds. | The 180-second successful-runtime requirement still exists. Because notification patience is 300 seconds from `raised_at`, this recovery delay affects whether a transient OPUS exception is emailed. |
| EM27 ping failure | While measurements were expected, EM27 was pinged at most once every 300 seconds. A ping attempt could wait up to 90 seconds before raising. The resulting exception was then emailed on the next main iteration. | The 300-second ping interval and 90-second timeout remain. A resulting exception additionally needs to remain in state for more than 300 seconds before email. |
| Upload failure | The exception was stored with `send_emails=False`, so it was never included in occurrence or all-resolved emails. The upload thread waited about 20 minutes before retrying. | Upload failures use the normal catchall entry and shared 300-second notification delay. The 20-minute retry loop remains. |
| `PYRA_CORE_CRASHED` | The CLI sent the email immediately when it first detected an ungraceful Core shutdown and marked the exception as notified itself. | The CLI adds the exception and runs the shared updater. Repeated CLI checks can send the email once the exception is older than 300 seconds. |
| `TUM_ENCLOSURE_PLC_CONNECTION_ERROR` | Failed initial PLC connections were retried every 60 seconds and entered exception state only after the connection had been unavailable for more than 360 seconds. | The 360-second producer delay remains, followed by the shared 300-second notification delay. Effective email delay is therefore greater than roughly 11 minutes. |
| `TUM_ENCLOSURE_RAIN_DETECTED_COVER_NOT_CLOSED` | After rain was detected with a nonzero cover angle, the thread waited 15 seconds and checked the angle again before adding the exception. | The 15-second confirmation remains, followed by the shared 300-second notification delay. |
| TUM `COVER_DID_NOT_CLOSE` | After disabling tracker synchronization and requesting angle 0°, the thread retried control/reset operations and added the exception only after more than 62 seconds. | The greater-than-62-second confirmation remains, followed by the shared 300-second notification delay. |
| `TUM_ENCLOSURE_PLC_RESET_FAILED` | Reset attempts ran for up to 180 seconds by default. The cover-closing path used a 30-second reset timeout. Only after that timeout was the exception added and immediately eligible for the old email loop. | The 180/30-second reset windows remain, followed by the shared 300-second notification delay. |
| AEMET `COVER_DID_NOT_OPEN` / `COVER_DID_NOT_CLOSE` | Cover validation waited 180 seconds after the requested sun-evaluation state changed. The first invalid check only set an `invalid-once` marker; the exception was added on the next invalid iteration. | Both the 180-second wait and second-check confirmation remain, followed by the shared 300-second notification delay. |
| `AEMET_ENCLOSURE_DATALOGGER_ERROR` for an Averia code | A nonzero Averia fault code was rechecked after 90 seconds. If still active, a `DataloggerError` was raised, logged, and retried after 60 seconds, but that inner error was not persisted for email. | The 90-second confirmation remains. The error is now added to state with its traceback and uses the shared 300-second notification delay. Other caught datalogger errors are added immediately and use the same delay. |
| CamTracker `COVER_DID_NOT_OPEN` | Cover checks started only after CamTracker had run for 180 seconds. A closed cover was then allowed to persist for `(3 × seconds_per_core_iteration) + 5` seconds, with checks every 5 seconds. Recent bad weather within 180 seconds cancelled the exception. | All of these producer-side checks remain, followed by the shared 300-second notification delay. |
| `HELIOS_CAMERA_ERROR` while taking images | Three consecutive camera errors were tolerated, with a 30-second reinitialization wait after each. The fourth consecutive error reached the persistent exception state and was emailed on the next main iteration. | The three-error tolerance remains. The fourth error is added to state and must then remain active for more than 300 seconds before email. |
| Helios camera initialization failure | Initialization failures were retried every 30 seconds and never reached persistent exception state through this path. | This behavior is unchanged, so this path still bypasses the unified notification lifecycle entirely. It should be addressed when patience becomes catalog-driven. |

As follow-up work, review each producer-side suppression timer or retry counter and move email suppression into catalog patience. Retain operational connection timeouts, retry intervals, and time needed for physical operations or fault confirmation as separate controls.
