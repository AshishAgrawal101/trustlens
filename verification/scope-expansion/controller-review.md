# Independent claim controller review

Read-only scope: static/claim-review.js, tests/claim_controller.test.cjs and current HTML/CSS contract. No source edits, browser interactions or actual clipboard/download writes performed.

## Resolved download compatibility concern

The controller clicks a detached anchor and immediately revokes its blob URL. This can revoke the resource before a browser consumes an asynchronously initiated download; the existing main controller instead appends its anchor and defers revoke. Recommend the same append/click/remove plus delayed revocation pattern here, including handling failure without leaving a private URL (the current blob is fixed/input-free). This is a source-established timing risk, not a reproduced browser failure: the DOM double asserts click/revocation only, not a saved file. Parent notified.

## No additional concrete privacy/state defect found

- Every export uses fixed PLAN; claim/context/source URL/quote/date never enter copy or download bytes. Structured observations/questions are fixed strings, rendered textContent; no source URLs are made navigable/fetched.
- Clipboard has a bounded 1.5-second race, generation guard and download fallback. Clearing/editing/review replacement invalidates late feedback and prevents stale export buttons from being enabled. The pending OS clipboard operation itself cannot be cancelled, but its content is always the same input-free plan.
- Normal field input invalidates outputs; Clear/pagehide/persisted pageshow erase all eight private values and result lists. No local/session storage or history is created. Browser/process termination cannot be certified by these handlers.
- Exact source URLs require HTTP(S), no credentials/control/space/backslash; no destination is visited. Dates are calendar-valid and future dates generate uncertainty questions rather than a falsehood verdict. Identical quotes/different hosts do not become corroboration claims.
- Examples use getAttribute('data-claim-example') correctly, so caption/headline buttons do not rely on misread dataset keys. Filling an example does not review automatically.
- Names are absent from private inputs; submit starts disabled and is enabled only after handlers are installed. Failed JS cannot serialize private fields as native GET parameters. Native validation supplements controller validation.
- Focus moves to result or actionable error; Clear restores claim input. Live copy status and labels/fieldsets are present. Browser native validation, screen-reader announcements and real clipboard/download behavior remain unverified.

Validation: independently ran claim_controller + claim_markup: 10 tests passed, zero failures/skips. These are minimal DOM/static contract tests, not actual browser downloads or user-study evidence. Parent owns broader pure analyzer tests and browser/full integration.


## Closure verification

Root aligned download initiation with the existing main-app pattern: append anchor, click, remove anchor, then revoke after one second. Independently reviewed current source and reran all six controller tests after the change; all passed, including no premature revocation and deferred cleanup. The identified timing concern is resolved by source alignment and regression coverage. An actual saved download file remains unverified; this does not claim cross-browser download success.

Root separately reports browser verification of the caption example, 320px layout without horizontal overflow and Clear erasing all eight fields. Those checks were not repeated by this reviewer. No application edits made during review/closure.
