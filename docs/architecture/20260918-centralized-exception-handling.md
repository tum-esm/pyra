# Central exception handling

## Catalog and reporting

`KNOWN_EXCEPTIONS` defines stable identifiers, email subjects, descriptions and default email patience. `CataloguedError` carries its catalog entry through Python exception handling; other caught errors become `UNEXPECTED_ERROR`.

Producers use `ExceptionsInterface`:

- `add_exception(...)` records a fault without sending email. Repeated reports from the same origin preserve its original `raised_at`.
- `resolve_exception(...)` clears one type or all faults from an origin, with optional exclusions.
- Records persist metadata, details, traceback and raised/notified/cleared timestamps.

Recovery follows producer checks. Faults are also cleared when their operation no longer applies, including disabled checks and unconfigured producers. Operational timeouts, movement allowances, retries, OPUS recovery timing and Helios's three-image-error tolerance remain producer responsibilities.

## Notification lifecycle

The always-enabled `ExceptionEmailThread` loads config and checks notifications independently of the main loop and system monitor. Its polling interval uses `seconds_per_core_iteration`. The CLI can also invoke notification updates directly.

Email patience starts when a fault is recorded. Only unresolved, unnotified faults whose patience has elapsed are emailed. Configuration changes preserve fault age. After an occurrence email, one recovery email is sent when no email-enabled faults remain. Cleared records are removed.

Test mode pauses automatic occurrence and recovery emails. The explicit test-email command sends in either mode.

SMTP runs outside the shared state lock. A separate notification lock serializes senders; state is reloaded after delivery to preserve concurrent producer changes. Failed delivery leaves notifications pending and suppresses further email attempts for a fixed 10 minutes. The cooldown is process-local and resets on restart. SMTP connections use a 30-second socket timeout.

## Configuration and generated documentation

Explicit fields under `error_email.exception_patience` accept finite values from -1 to 86400 seconds. Exactly -1 mutes an exception. `unexpected-error` is not configurable and always uses 0 seconds. An exception without a configurable field falls back to 300 seconds. Muted faults remain recorded but do not block recovery emails.

The default config includes every supported key. The UI groups fields by general, TUM and AEMET errors, hides hardware-specific fields when unconfigured, and reads descriptions from the exported config schema.

Run `python scripts/sync_schemas.py` after catalog or schema changes. It generates:

- `packages/ui/src/config.schema.json` for UI descriptions and checked field access.
- [Known Exceptions](../../packages/docs/docs/user-guide/known-exceptions.md), the user-facing patience guide and catalog reference with descriptions and defaults.

The repository pytest suite checks both generated files by comparing checksums before and after regeneration. CI also checks the UI build. Old config and state formats need no compatibility on this development branch.
