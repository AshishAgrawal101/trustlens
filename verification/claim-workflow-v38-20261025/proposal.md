# Claim workflow: make a rejected source repairable

The most useful bounded improvement found is **field-specific source-error recovery**, rather than another field, example or inference rule.

## Concrete task and current failure

A person has entered a claim and two source accounts, closes optional Sources, and selects Review. One pasted HTTP(S) address contains embedded login text (valid URL syntax, rejected by this worksheet’s additional policy). The controller correctly clears stale output, preserves every draft and opens Sources. However, it focuses an error below the entire disclosure that says only “Use an HTTP or HTTPS address without embedded login details or control characters.” It never identifies Source A versus B or gives a route back to the offending address.

`source-error-probe.json` reproduces this with the real controller, actual input events and submit, using the established URL-capable fixture. Changing only the failing side yields the exact same error/focus/open state for A and B. No eventless invalid-state trick was needed. Existing `tests/claim_sources_disclosure.test.cjs` intentionally covers disclosure reopening and alert focus, but not knowing which account to repair. This is a recovery/wayfinding gap, not a wrong truth verdict or privacy leak.

## Smallest complete approach

Attach a fixed, allowlisted field identifier to custom source URL validation errors; prefix the displayed fixed message with **Source A address** or **Source B address**. Keep current alert focus so the reason is announced. Offer one adjacent native button **Correct Source A address** / **Correct Source B address** that opens Sources and focuses the actual existing input. Associate that error with the input via `aria-describedby` and `aria-invalid` while applicable. Do not parse prose to guess the field, echo the rejected URL, create a source hyperlink, or erase either account.

Limit the first slice to custom source-address failures; ordinary native invalid events already open the closest disclosure before browser focus, and should keep doing so. Global length/date/role errors can keep their existing behavior unless implementation reveals a direct dependency. Do not add a new form library or general error framework. If a simpler direct field-focus solution is chosen, preserve an accessible announcement of the fixed reason rather than silently moving focus.

Clear the correction action and ARIA error state on edits, successful review, example replacement, Clear and lifecycle reset. A hidden/obsolete correction action must be inert. Pure successful `review()`/`analyze()` outputs and PLAN bytes must remain exact; error-object metadata is an intentional contract extension, not a new finding or report field.

## Scope, tests and harms

Likely files: `static/claim-review.js`, `static/claim-review.html`, scoped `claim-review.css` only if existing button styles do not suffice; a dedicated controller/accessibility regression. Shared Pocket renderer/module automatically reuses the change; root owns cache/export/version/browser evidence. No backend, URL fetch, storage, source opening or private export.

Acceptance: valid A/invalid B and reverse identify the right fixed field; drafts survive; Sources opens; alert announces reason and correction reaches the matching input; successful repair requires separate Review; repeated errors do not leave stale ARIA/action state; native invalid/default focus behavior, pending-copy invalidation and no private URL echo remain. Snapshot successful pure outputs and PLAN against v37. Existing pure-prefix hash assertions would need explicit intentional updates for error metadata only; never alter historical before hashes/receipts or weaken their preservation meaning.

Benefit is reduced hunting through two long account fieldsets after a common paste failure. Risk is focus/announcement duplication or stale error association; keep one fixed correction action and existing alert announcement, and test keyboard order. This is moderate priority, not a release-blocking vulnerability. It is more valuable than more source fields: existing context/quote entries already accommodate methodology, provenance and uncertainty notes, while the worksheet deliberately does not interpret their factual meaning.

No app edits, browser upload, external data or source visits were performed for this audit.
