# Independent in-page Numbers drafts

Changed `static/numbers-context.js`, `static/numbers-context.html`, new `tests/numbers_method_drafts.test.cjs`, and the two authorized existing contracts: `tests/reported_percentages_controller.test.cjs` method-change title/value assertion, and `tests/reported_percentages_markup.test.cjs` method-help assertions. No fixture rewrite or backend, phone, cache, export, package, README or task edit.

Method selection now calls existing `invalidate()` and `syncMethod()` instead of `clear()`. Raw independent values remain in the six existing unnamed DOM fields for this page visit; active fields enable, inactive fields hide/disable, and previous result/error/status clears. No values are converted or inferred and Compare remains explicit. Existing active-only Swap and pure math functions are unchanged; `retention-preservation.json` confirms the entire pure module prefix byte-exact.

Clear continues wiping both drafts while retaining the selected method. Constructed example replacement wipes both first, then populates only the active example. Pagehide/restored Back still wipe both and reset Counts default. Updated help states those boundaries and makes no storage/history claim.

TDD: acceptance frozen in `retention-contract.json`; `retention-red.txt` captures three new failures and one existing wipe-boundary control passing before edits. `retention-green.txt`: **89/89** Numbers/reported-percentage tests pass, zero failures/skips. New regressions use input/change/submit events for both-direction raw-string/precise-decimal roundtrips, active validation excluding inactive invalid entries, unchanged focus, no automatic result, active-only Swap and all wipe boundaries. Existing math, acceptance, rounded display and privacy/controller suites remain green.

Limits: controller/DOM evidence does not prove browser preservation of an unfinished native-number editing buffer whose `.value` is inaccessible; this feature preserves readable raw `.value` strings. Root owns actual browser and refreshed Pocket canonical-cache/export checks. No network, clipboard, download or persistence operation was added.
