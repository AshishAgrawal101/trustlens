# One recommended increment: focused advertising practice

## Concrete gap

The useful advertising scenarios already exist, but a person interested in an endorsement cannot start with them. `static/learning-practice.js` always opens its ten-item queue at index zero; the two ads cases are ninth and tenth. `static/phone/practice.js` similarly starts its twelve-case sequence at zero, with those cases eleventh and twelfth. Reaching them therefore requires eight or ten unrelated answer/Next cycles. This is source-observed navigation friction, not a measured learning-outcome claim.

The discovery flow is already sound: `static/tools.html` links Ads & endorsements to `/context-guide.html#ads`; `render_desktop_context()` in `app/pocket_workspaces.py` renders the canonical `static/phone/context.html` outside the stale Pocket service-worker scope. The guide gives concise checks and an explicit manual Claim-workspace link. Adding another ad-analysis form, scoring system or guide would duplicate this work.

## Recommended bounded scope

Add one explicit **Practice ads & endorsements · 2 situations** start action alongside the existing all-scenarios start action, in the existing desktop Practice dialog and Pocket Practice disclosure. Reuse the two current cases, unchanged, in their current order. No new questions, page, route, fragment contract or automatic dialog opening. The ordinary start action continues to cover all cases.

Use a small session queue in each current controller. Desktop already has one; Pocket can replace its direct case index progression with queue-position lookup. Selected-session progress must say two situations, and restart/repeat should repeat that selected session. Desktop’s existing **Restart all scenarios** must still mean all ten; retain its explicit label and behavior. Existing close, exit, Back and stale-answer guards must erase the selected queue/session along with answers. No topic choice or progress is persisted.

This gives a short, relevant daily-information exercise without introducing a detector or another workspace. It exercises both missing comparison conditions and selected-testimonial evidence, rather than making a paid/unpaid truth judgment.

## Callers and tests

- Markup/controller scope: `static/index.template.html`, `static/learning-practice.js`, `static/phone/index.html`, `static/phone/practice.js`; reuse existing practice button styles, with scoped CSS only if the row needs wrapping. The desktop renderer already includes the learning module. No backend or shared context renderer change is needed.
- New focused controller tests should start the two-item session, assert the exact existing case identities/order, correct 0/2 through 2/2 progress, answer locking, finish/repeat behavior and all-scenarios restart. Retained removed callbacks must not change a restarted or closed session.
- Test close/pagehide/persisted pageshow resetting the focused session; keyboard activation/focus and 320px button wrapping; no fetch, storage, exports or private-input access. Preserve the old all-case journey tests and frozen case bytes/order.
- Pocket changes require the normal cache/version/export refresh and offline check by the integration owner; this proposal does not claim current cached clients contain the enhancement. Existing practice tests are `learning_practice.test.cjs`, `pocket_practice.test.cjs`, `pocket_context_practice.test.cjs` and `ads_practice.test.cjs`.

Approximately a 30-minute implementation slice with focused regressions, excluding packaging/browser receipts. No application files were changed, no browsing was needed, and no new factual, legal, accuracy or physical-phone claim is proposed.
