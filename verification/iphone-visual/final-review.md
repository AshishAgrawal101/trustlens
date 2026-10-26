# Final independent integration review — 2026-10-23

Read-only review of current static/link-details.js, app/main.py validation handling, url_details.py/schema/API tests, Pocket native sharing/navigation, ios.js clipboard/navigation and targeted controller tests. No app/runtime/cache/source edits were made. No model, dataset, image payload, external content API or browser/device action was used.

## Actionable findings

No concrete security, private-content export, data-loss or platform-claim regression found in the reviewed scope. No additional source change is recommended from this pass. This is a bounded code/test review, not a production-security or assistive-technology certification.

## Evidence and line references

- static/link-details.js:23–25 sends literal URL and optional known reference in a local POST body, never a browser navigation or URL query. app/analyzers/url_details.py _components returns host/structural counts while omitting credentials and private component text. The local API does not fetch/DNS-resolve the supplied destination. tests/test_inspect_url_api.py:6–16 verifies omissions, POST-only behavior, no-store and unrelated-Origin rejection.
- static/link-details.js:29–37 rejects wrong scalar types, malformed reference comparisons and out-of-range port/count values before rendering any rows. Lines10–12 use textContent, so a host/display spelling cannot become HTML. It validates but does not display the server notice verbatim; its visible fixed notice at51 still qualifies ownership/redirects/private-component omissions and refuses matching-is-safe. No finding depends on treating a hostname match as identity evidence.
- static/link-details.js:6–8 aborts and clears prior results;27 and53–58 guard late success/error/focus by generation.62–66 cover input/reference edits, Clear/example, mode/demo changes and page exit/restoration. A ten-second abort bounds ordinary fetch waiting. Focus restoration only happens if the clicked button originally had focus and the user did not move it to another field. Existing targeted tests verify both retained and moved focus.
- app/main.py:35–37 registers a fixed RequestValidationError response. It does not serialize errors(), input values, invalid extra fields or private decoder details into the response. Normal privacy middleware supplies no-store. tests/test_inspect_url_api.py:19–28 exercises oversized private query text, private extra fields and wrong-type private email content with exactly the fixed422message and no reflected input. This sacrifices field-specific validation detail intentionally while preserving actionable format/length guidance.
- static/phone/phone.js:66–85 shares only PocketGuide.summary(selected) after explicit user click and a visible result; the payload has fixed title/text with no URL argument, message, matched excerpt or reference host.106–124 (current recovery copy/share region) uses a fixed selected recoverySummary. Version predicates prevent native/clipboard completion from labeling cleared/newer results; success says delivery is not verified. Unavailable/cancelled/rejected paths offer copy/download. Existing tests assert private-looking messages cannot enter either native payload.
- static/phone/ios.js:7–40 invokes readText only in the Paste copied text click handler, with30kbound,3secondwait, fixed errors and current-text preservation on rejection. Input/Clear/example/submit/topic/lifecycle invalidation guards late completion. Successful paste dispatches the ordinary input event rather than submitting or classifying. The persistent root paste hint now discloses replacement before action. Navigation handler in its #shortcut block prevents default only for an already-current hash, then opens/focuses; different-hash behavior and repeated same-hash focus have paired tests. None of these handlers reads clipboard during load/navigation.

## Checks run

Focused Node command only: node --test tests/link_details.test.cjs tests/pocket_native_share.test.cjs tests/ios_companion.test.cjs —19passed, no skips,143.237ms. Covers anatomy schema/failure/stale/focus, explicit fixed native shares, iPhone paste bounds/denial/timeout/stale events and repeated-hash behavior.

Focused API command only: existing main Python -m pytest tests/test_inspect_url_api.py -q —4passed, no skips,0.64s. No full-suite rerun duplicated root's integration work.

## Limits / claims

These are controller-double and local API checks. Native Safari paste permissions, physical iPhone installation/Shortcuts execution, actual share delivery, rendering/zoom/screen-reader behavior and phone HTTPS deployment remain unverified here. Documentation and UI retain those limits and describe the Shortcut as manual setup text, not a downloadable installed native integration. Selected FTC-pattern diagnostic outcomes remain explicitly adapted/constructed, with preserved misses and no population-accuracy or FTC-endorsement claim.

Skipped broader tests/browser/device/model work. Residual risks are the documented parser/grammar limits, user-selected topic/reference fallibility, optional clipboard/native-share support and ordinary OS clipboard/share behavior outside Pocket's control.
