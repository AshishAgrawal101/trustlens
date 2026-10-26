# Recovery retry can be poisoned by invalid successful payloads

Highest-value bounded failure-UX issue found: `static/app.js` assigns `(await response.json()).plans` to persistent `recoveryPlans` before validating it. An invalid truthy payload then prevents every later opening from fetching again, even though the fixed error explicitly tells the user to reopen to retry.

## Reproduction and boundaries

Used the actual main controller/harness with ordinary recovery-open and native-dialog-close actions. First simulated local API response: HTTP200 `{plans:{}}`; second response made available after close: a valid constructed plan. First open shows the fixed failure and no options; reopening shows the failure again with **only one request total**, so it never reaches the corrected response. HTTP200 `{plans:[]}` is worse UX: no error/status and no options on either open, again only one request. Exact outcomes are preserved in `recovery-cache-repro.json`.

This is a constructed malformed-response fault injection, **not evidence that the current fixed `/api/recovery` actually emits invalid data**. Current backend `app/main.py` serves fixed `RECOVERY_PLANS` from `app/guidance.py`. A 503→valid response control correctly makes two requests and recovers (`http-failure-control.json`). The defect is the successful-response/cache boundary and misleading retry instruction, not generic offline failure, a source-authentication issue or a demonstrated exploit.

Existing `frontend_lifecycle.test.cjs` covers recovery pending-close/exit and clipboard staleness; `frontend_state.test.cjs` covers normal recovery/copy. None validates recovery response shape before caching. A partial list can also render a button whose missing `steps` causes a later uncaught selection error; fix admission rather than patching each consumer.

## Minimal proposed slice

Validate a nonempty bounded plan list into a local variable before assigning the cache or rendering any option. Check each record’s fixed required id/label/title/steps string shape, unique IDs and sensible bounded lengths/counts; do not render/cache partial data or echo payload details. Keep cache null on rejection so normal close/reopen can actually retry. Retain the fixed error/FTC fallback, existing timeout/token/dialog-open guards, fixed plan semantics and input-free clipboard behavior. No new API, storage or dependency is needed.

Scope: `static/app.js` and a dedicated main recovery-response regression using the established harness; HTML is not required. Test null/object/empty/partial/missing steps/duplicate IDs as single-response failures followed by normal corrected retry; no partial options/export state; valid response cached once; existing close/lifecycle/copy guards still pass. Constrain the validator to the actual endpoint contract rather than a new recovery-framework abstraction.

The broader audit read manual selected-step guidance, optional helper failure handling, bounded clipboard fallback and lifecycle tests. No new ordinary-flow stale/private-state bug was reproduced there; no prior Media/Claim/Source optional-control issue is being re-reported. This recommendation is moderate robustness work, not a release-blocking claim about current normal responses. No app edits, browser uploads, external data, network or native-phone checks occurred.
