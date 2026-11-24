Tests for the repositories state.

1. Are the default configs in a valid state (all validation rules except paths)
2. Is the static type analysis running through?
3. Is the UI config schema in sync with the backend?
4. Does the UI pass TypeScript checks and build successfully?

These tests can be run in a CI environment. The UI build test requires Bun and Node.js.
