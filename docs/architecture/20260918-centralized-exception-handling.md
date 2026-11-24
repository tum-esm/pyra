# Central exception handling

Status: committed code at `2a6bd8d`. Pending producer changes are not included.

## Implemented

`KNOWN_EXCEPTIONS` is the shared catalog of identifiers, subjects and descriptions. Expected failures use a specific entry; unexpected failures use `UNEXPECTED_ERROR` with a traceback.

Core threads and the CLI use `ExceptionsInterface`:

- `add_exception(...)` records a fault. Repeated reports from the same origin preserve its original `raised_at`.
- `resolve_exception(...)` clears one type or all faults from an origin, with optional exclusions.
- `update_exception_notifications(...)` sends due emails, retries failed notifications and removes cleared records. After an occurrence email, it sends one recovery email when no email-enabled faults remain.

Records persist the catalog metadata, details, traceback and raised/notified/cleared timestamps. Emails show the description, details and traceback separately. Old config and state formats need no compatibility on this development branch.

## Email patience

Configure seconds under `error_email.exception_patience`, keyed by exception identifier:

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

- Allowed: finite values from **-1 to 86400**, inclusive. Exactly **-1 disables emails**; zero or a negative fraction is eligible on the next notification update.
- Defaults: **90s** for `cover-did-not-close`, **0s** for `tum-enclosure-rain-detected-cover-not-closed`, **300s** for the other configurable entries.
- `unexpected-error` is not configurable and always uses **0s**. Any type without a configurable field uses **300s**.
- Missing settings use defaults. Unknown keys and invalid values are rejected. Partial updates merge by identifier.
- Patience starts when the fault is recorded. Changing configuration does not reset its age or resend an already-sent occurrence email.
- Muted faults stay in state until resolved but do not block recovery emails. Unmuting an unnotified fault uses its original age.

The config fields are explicit. The default JSON includes every supported key. The UI groups them by general, TUM and AEMET errors, hiding hardware-specific fields when that hardware is not configured.

Field descriptions come from the catalog. `scripts/sync_schemas.py` exports the config schema to `packages/ui/src/config.schema.json`; the UI uses it for descriptions and checked field access. Repository tests check schema synchronization and run `bun install` / `bun run build` through the Python CI workflow.

## Current producer behavior

Email patience is centralized. Detection delays, retries and recovery still depend on each producer; any delay before recording a fault adds to email patience.

| Producer | Committed behavior |
| --- | --- |
| TUM | Initial PLC connection failures are recorded only after a 360s grace period; retries wait 60s. Rain checks allow 15s for closing, normal closing waits over 62s, and reset attempts allow 180s or 30s. Some faults can remain stuck because recovery uses a persistent flag. |
| AEMET | Cover validation waits 180s after a requested-state change and requires two invalid checks. Averia faults are rechecked after 90s inside automatic control; caught datalogger errors are persisted. |
| OPUS / EM27 | OPUS connection errors are recorded after operational timeouts. Recovery waits for 180s of successful thread runtime. EM27 pings use a 300s interval and 90s timeout, but ping timeouts currently fall through to `UNEXPECTED_ERROR`. Failure retries wait 180s. |
| CamTracker | Cover checks have a 180s startup allowance, then wait `(3 × seconds_per_core_iteration) + 5` seconds. Recent bad weather cancels the fault. The wait does not refresh the cover position. |
| Helios | The first three consecutive image errors retry after 30s; the fourth records `HELIOS_CAMERA_ERROR`. A successful image resets the counter, and a successful processing iteration clears faults. Initialization failures only log and retry after 30s; they never enter exception state. |
| Upload | Failures use `UNEXPECTED_ERROR`, so email patience is 0s. Retries take about 20 minutes. Success or a configured upload becoming inactive clears faults; removing upload configuration returns before cleanup. |

## Remaining work

- Remove producer delays used only to suppress reporting. Keep connection timeouts, movement allowances, retry intervals and Helios's three-error tolerance.
- Record Helios initialization failures and classify EM27 connectivity failures correctly.
- Clear faults after confirmed recovery or when the operation is no longer required, including disabled/unconfigured producers and test mode. Preserve `raised_at` across repeated failures.
- Verify detection, retries, recovery before notification and cleanup when requirements change.
