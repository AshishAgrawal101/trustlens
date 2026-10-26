# Desktop focused advertising practice

Implemented only in `static/learning-practice.js` and `static/index.template.html`. The dialog now offers **Practice ads & endorsements · 2 situations**, initially disabled until setup completes. Fixed help states that starting replaces practice choices. It uses the existing secondary button styling; no CSS or Pocket files changed.

The handler requires an open dialog, resets current progress/answers, selects the existing `sponsored-comparison` and `selected-testimonial` cases by stable IDs in that order, and displays the first choice. The scenario/module-data prefix SHA-256 is unchanged and pinned in the new regression. No case is copied or rewritten. Existing queue-based progress, missed-only retry, completion recap and epoch guards apply to the selected session. Header Practice and **Restart all scenarios** retain all ten cases. Close/reopen, page exit and persisted Back reset to the all-case default without retaining choices or stealing lifecycle focus. Explicit Close still returns to the header opener.

Tests: `tests/ads_focused_desktop.test.cjs` adds four tests covering markup/setup, exact identities/order/progress/completion/scoped retry, replacement/restart/stale callbacks, and close/lifecycle focus/privacy resets. The only existing-test edit is the `learning_practice.test.cjs` fixture ID and initial disabled property for the real new button; assertions are preserved.

Evidence: frozen `desktop-contract.json`; `desktop-red.txt` captures three failures and one passing lifecycle control before implementation; `desktop-green.txt` has 11/11 focused passes. `desktop-integration.txt` has 20/20 passes across those suites plus existing advertising and frontend-response tests, with zero failures/skips. The new test pins its hash directly and does not depend on verification artifacts being packaged.

No network, storage, exports, private-input access, new route or automatic dialog launch. Actual browser button wrapping and keyboard geometry remain integration-owner checks; no physical-phone or learning-outcome claim follows from these tests.
