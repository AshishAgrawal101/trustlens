# Pocket reliability handoff

Scope: only `static/phone/phone.js`, `tests/phone_companion.test.cjs`, and this directory. No service-worker/share parser/guide/markup/backend changes and no browser use.

## Implemented

- Offline preparation now has one 15-second bound covering registration, worker activation and cache-status confirmation. Registration can no longer hang the disabled Prepare button indefinitely.
- Uses the registration returned by register(), prioritizing its installing/waiting worker over an old active worker. Installation alone does not establish readiness; redundant workers fail honestly.
- After activation, asks that worker for POCKET_STATUS through MessageChannel. Only ready=true and the exact HTML pocket-version content establish success. This coordinates with root-owned metadata/cache v4 changes; no private text enters the handshake.
- Timeout/failure removes listeners, closes status ports and restores controls. Late registration completion cannot attach listeners or rewrite failure/retry state. Duplicate prepare requests while pending are ignored.
- Each result rebuild/clear increments an in-memory version. Both clipboard success and failure require the captured version to remain current, preventing an old clipboard operation from labeling a newer result.

## Validation

`node --test tests/phone_companion.test.cjs`: 15/15 passing (existing eight plus seven targeted regressions).
`node --check static/phone/phone.js`: passing.

Regressions cover old ready registration versus newly installing worker, installed versus activated state, redundant update followed by retry, pending registration timeout/late completion, activation timeout/listener removal/retry, stale clipboard success and failure, exact cache version and complete-cache requirement, and unanswered status timeout.

No storage, content network requests, dependencies, models, downloads or additional workers introduced. The status exchange is fixed metadata on the existing service worker.

## Limits

No browser/device/install test performed here; root owns permitted browser checks. Existing tests use bounded DOM/service-worker doubles. A timeout releases the UI but the browser's underlying registration operation is not cancellable; a later browser update may finish independently and can be checked by retrying. Current markup and SW must ship matching pocket-version and POCKET_STATUS support; mismatches fail preparation honestly.
