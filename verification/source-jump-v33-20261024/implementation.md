# First/Last match navigation

Changed only `static/source-context.js`, `static/quote-context.html` and new `tests/source_jump_navigation.test.cjs`. No existing fixtures/tests required edits. Root owns cache/export/package and docs.

Added initially-disabled **First five** / **Last five** beside existing Previous/Next controls, in First/Previous/Next/Last order. Existing wrapping/48px paging CSS applies without a stylesheet change. The hint explains jumping versus nearby-page browsing. A derived integer `lastPage` is assigned only after a successful current scan, reset on every invalidation, and used by guarded explicit navigation. All four controls disable on hidden/short results or reset. When a jump reaches its disabled endpoint, the existing live range receives focus; inputs are not changed.

The complete pure SourceContext/module-export prefix is byte-identical to the frozen pre-edit SHA pinned directly in the new test; matching, windows, Unicode behavior, counts and two-argument outputs are unchanged. No network, persistence, exports or automatic Find was added.

`contract.json` froze acceptance before edits. `red.txt` captured five failing new regressions before implementation. `green.txt` records 23/23 focused tests passing. New coverage includes exact 11th-match jump and return, actual 30,000-character controller scan → page5999/range29996–30000, Previous/Next after the jump, preserved drafts/formatting notice, zero/one/five sets, and all edit/native-invalid/shared-clear/example/exit/Back resets plus inert stale activations. `integration.txt` records the larger related source/paging-oracle/Unicode run. Browser geometry/offline version availability are root integration checks; this change does not establish source authenticity or factual truth.
