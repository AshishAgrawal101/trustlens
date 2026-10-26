# Integrated v6 Pocket review — 2026-10-23

Reviewed practice.js, integrated Pocket index markup and suggestions.js for privacy, accessibility and interaction. Existing compare/recovery/share/controller tests were run alongside the new suggestions/practice tests after root's v6 fixture/cache change. No existing index, CSS, service worker or model source was edited by this worker.

## Fix made in owned suggestion widget

Repeated Apply topic controls had identical standalone accessible names, despite representing different topics. A keyboard/screen-reader user navigating buttons could not distinguish them without reading surrounding content. Added a topic-specific aria-label for each Apply/already-selected button, updated when checkbox state changes. The visible compact button text is unchanged. Extended the existing interaction regression to verify the initial and selected accessible names. No heuristic or matching result changed.

## Practice/integration findings

No additional concrete defect requiring a root edit found. Practice uses fixed constructed scenarios, never accesses private-message elements, does not read or export answers, and renders with textContent. Start/Next focuses the scenario title; an answer disables its choices and focuses feedback, which has tabindex -1 and status semantics. Closing practice or leaving the page resets the session. The routine appointment example teaches verification without labeling routine notices fraudulent. No score or user history is stored.

Integrated optional suggestions markup has an explicit button inside the disclosure, a status region and list results; all existing request checkboxes retain their labels. Initial suggestion does not select a checkbox. Apply uses the existing change handler to invalidate stale guide results and focuses the selected checkbox. Message edits and lifecycle/Clear/example events remove excerpt nodes. Live statuses preserve uncertainty and exports still use fixed independent guide/recovery content. The pure helper diagnostic remains 18/24 exact constructed topic sets with six explicitly retained misses; the accessibility change does not alter it.

## Verification

Command: node --test tests/phone_companion.test.cjs tests/phone_recovery.test.cjs tests/pocket_compare.test.cjs tests/pocket_practice.test.cjs tests/pocket_share_flow.test.cjs tests/pocket_suggestions.test.cjs

33 passed, no failures/skips. Raw receipt: all-pocket-tests.txt. This includes v6 worker cache/version contracts, share payload parsing/erasure, bounded readiness and clipboard failures, recovery, comparison, practice and suggestion interactions. These are offline Node/controller doubles, not physical Android or screen-reader evidence.

## One proposed next feature — not implemented

A user-selected Changed payment instructions verification path would fill a concrete workflow gap. The current money checklist handles every payment generically, while the new practice module specifically teaches supplier bank-detail changes. Let a user explicitly choose “Payment instructions changed” and receive a short fixed sequence: pause the new payment, call the established contact from prior records, confirm the exact change outside the current email thread, and contact the payment provider promptly if already sent. It should require no bank details, contact storage, automatic classification, new fraud pattern or model. This would carry a practiced high-risk scenario into real next steps without asking users to trust another detector.

Skipped browser/screen-reader/Android verification; root owns those integration checks. Remaining risk is incomplete literal topic coverage and fallible user selection, not removed by practice or accessibility names.
