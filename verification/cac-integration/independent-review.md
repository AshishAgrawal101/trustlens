# Independent bounded review — CAC workflow integration

Reviewed source and targeted tests on October 23, 2026. Scope: `static/verification-plan.js`, its two `app.js` hooks and low-concern headline; `scripts/export_phone.py`, `tests/test_phone_bundle.py` and `tests/verification_plan.test.cjs`. No app/script/export implementation was edited. This is a bounded engineering review, not an eligibility or release-acceptance determination.

## Result

No unresolved privacy, stale-export, invalid-mode or reset-consistency defect was found in the reviewed changes. The minor reset finding below was fixed by root and independently retested. Root reported the broader 731 Python / 133 JavaScript passes; this reviewer reran only the targeted five verification-plan tests and one static-phone-bundle test, all passing.

## Minor actionable finding

**Resolved P3 — reset previously left the route heading in hidden DOM.** `VerificationPlan.reset()` clears selection, steps, status and pressed states, and hides both sections, but does not erase `verification-heading`. Reproduction through the actual controller/test harness: show a communication result, choose the known-number route, then Clear. The plan/choice are hidden and steps empty, while the heading remains `Start a new call using a known number`.

Root applied the minimal fix: reset now clears `verification-heading.textContent`, and the existing reset regression asserts an empty title. The reviewer reran the five plan tests after this fix; all passed. The original condition was not an active export leak: `selected` becomes null, panel is hidden, and both copy/download guards reject the stale plan. No original request text is present in the fixed title. It was a completeness/consistency issue and is now resolved.

## Verification-plan review

- The panel is initially reset, shown only after the controller accepts and renders a non-image report, and reset by the existing `clearResult()` path. That path covers edits, Clear, examples, mode switches, rechecks, cancellation and page exit/Back restoration.
- Selecting a route requires a visible panel and an own key in the fixed route table. It does not call a phone number, open a link, submit another analysis, read private source text or mark verification complete.
- Every route contains fixed next steps. Exports use only that fixed title/step list plus an explicit not-completed-verification disclaimer. The report object, evidence, risk, original safe summary and original print content remain separate.
- Copy captures the current fixed text and version before calling the shared bounded clipboard helper. Route changes/reset increment that version; late completion cannot label a new route or cleared page. Download requires both visible panel and current selection and uses the existing input-free blob helper.
- Native buttons expose `aria-pressed`; the group has a label and selected heading is focusable and explicitly focused. The visible plan and exported text say it is user-selected and not completed verification. The reviewer did not run a browser or assistive-technology session.
- The main low-concern headline now says the request is still unverified. It preserves the existing warning/evidence structure and original export semantics rather than presenting a clean-looking safety certification.

Targeted checks: five `verification_plan.test.cjs` tests passed. They cover explicit selection, all three fixed exports, image exclusion, original report/print preservation, reset paths, timeout fallback and stale route completion. Test inputs are constructed markers, not private user messages. This review did not perform an actual clipboard write or native Share action.

## Static Pocket bundle review

- The exporter reads a fixed tuple of eighteen named shell assets. It does not walk arbitrary directories, include backend/model/runtime configuration, inspect the clipboard or collect message content. All eighteen current paths are distinct regular source files, not symlinks.
- Archive entry names are fixed under `phone/`, plus the fixed device-test README and manifest. No input-derived archive path or private source value enters an entry name. The manifest records byte lengths and SHA-256 of the captured bytes.
- Existing destinations are protected by both a precheck and exclusive ZIP creation (`x`). The test verifies an existing bundle stays byte-for-byte unchanged when a second build is refused.
- The targeted test injects a constructed `PRIVATE.txt` into a temporary source directory; the fixed allowlist/entry-count checks keep it out. It verifies every manifest digest, archive integrity, expected public assets and absence of backend/config/weights paths.
- Exporting packages static bytes only. It does not deploy them, alter binding, expose the loopback server, create a tunnel/certificate, install an iPhone app or change host permissions. The README correctly requires a user-controlled trusted HTTPS origin with fixed `/phone/` paths.
- The README distinguishes browser preparation from physical-device evidence and requests constructed text for the first test. The companion-only host may lack the desktop root route; that is explicitly documented. Native sharing remains user-controlled and unverified on a physical device.

Targeted check: `pytest tests/test_phone_bundle.py -q` passed (one test). This created only a temporary test bundle; no production phone bundle or deployment was created by this reviewer.

## Boundaries

The static-source allowlist prevents unrelated added files from being exported; it is not a substitute for reviewing edits made to the allowlisted application files themselves. No claim is made that a temporary test archive proves physical iPhone installation, offline storage retention, Safari permissions, Messages reception, native Share delivery or community usability.

Root's browser observations (1280/320 plan visibility, clearing, focus and non-verified wording) are separate evidence. Physical-device, interactive upload, actual copy/share and user-study checks remain unperformed unless an explicit later receipt records them. Earlier v5 and other immutable archives are outside this review's write scope.

## Final reviewed identities

- `static/verification-plan.js` SHA-256: `1028b9531d0a24e22f9ef27383294b113377025f8fd54f33ef6b91cf99bbd294`
- `static/app.js` SHA-256: `57de07c499b219f691ccf351ba07692ad70aa46695b5c72d766ecfd5a24f6ba0`
- `scripts/export_phone.py` SHA-256: `f7f9a4e7008988698c30a1891232f1ed02b1e1d243b9d69ddbf371bac6c84b4c`
- `tests/verification_plan.test.cjs` SHA-256: `e48b8e2cd7dcf0540e567398696f505c4a5c2a857ce4a77a23eb69f15a0c75c3`
- `tests/test_phone_bundle.py` SHA-256: `f32168d2cd4476f2c4ffab9e9d8eb43a7fcdb10635d8017f3c0f689686af8ecc`

These identities include the root heading-reset fix. Root owns any subsequent integrated Node rerun and packaging receipt.
