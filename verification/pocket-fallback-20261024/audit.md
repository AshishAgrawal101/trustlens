# Pocket no-JavaScript / partial-controller fallback audit

Read-only source audit of Pocket index/phone.js/guide.js/worker/share shell plus in-memory probes in probes.json. No application edits, browser JavaScript/profile/permission changes, uploads, external requests or real private data. Performance audit finalized separately with no optimization; traced timeout and all measurement receipts preserved.

## P2: native request-topic submission can put choices in the URL

Current form#guide has no method/action, four successful named checkbox controls (name=request, values money/code/device/secret), an initially enabled submit and no noscript explanation. If phone.js does not execute, ordinary form submission defaults to GET. Constructed two-topic serialization is request=money&request=code. This exposes only selected topic categories, **not** pasted message/known-host text: message is outside the form and unnamed; known-host is also unnamed/outside guide. Do not describe this as full message-text exfiltration.

Topic choices can still reveal incident context and enter request URLs/history on a hosted or static deployment. The normal app CSP lacks form-action restriction. Worker-generated share-response CSP form-action none blocks native submission in that special response, but does not protect the ordinary Pocket entry or portable static host.

Worker ignores GETs with url.search. Synthetic worker event for /phone/?request=money&request=code is not intercepted. Thus a disabled/failed-controller submit can also leave a prepared offline page for a query navigation that needs the network. This is source/in-memory evidence, not actual disabled-JS browser proof.

Minimal recommendation: remove topic names and use a non-submitting data attribute with existing value (update phone.js/suggestions.js selectors/tests), add an initially disabled guide submit enabled only after dependency/controller readiness, and a noscript notice linking the script-free /phone/context.html fallback. Never put message or topic state into action/query/fragment fields. Keep guide selection behavior and all privacy reset guards intact.

## P3: no-script status/control text implies a working guide

Initial offline heading says Preparing offline access although no preparation occurs if JS never executes. Status says the guide can be used, while the result buttons are inert/no native fallback exists. No noscript guidance is available. Clear private text also has no native clearing action without its listener; do not imply it erases browser text when the controller did not start.

Prefer a neutral initial Offline access not checked state and clear JS-required fallback guidance. Preparation and readiness statements should be written by successfully initialized code. The context page is already script-free and a useful fixed offline fallback after preparation; do not imply JS-disabled users can newly prepare/install the worker from that page.

## P3: missing guide helper has no actionable feedback

In-memory actual phone.js harness with PocketGuide deliberately absent: core script registers submit prevention; submitting prevents native navigation, calls clearResult, then throws ReferenceError at PocketGuide.nextSteps. Result stays hidden, no fixed unavailable message is displayed. This path does **not** leak through native GET because preventDefault already ran. It does fail silently from the user's perspective. Offline asset presence/readiness checks do not prove that helper JavaScript successfully executed.

Recommend validating the small core helper API before enabling submit and showing fixed unavailable/reload/context-guide text if missing. Do not fail by interpolating an exception or user input. Keep Clear/lifecycle handlers installed even when a helper is unavailable; do not move a dependency failure before privacy cleanup registration.

## Existing protections and comparison with main v15

Main now has unnamed private controls, initial disabled submission, autocomplete off/noscript and final-line controller enable. Its JS-disabled browser behavior remains unverified; this audit did not change settings to test it. Pocket share demo is different: its named text is a fixed read-only constructed example, method POST and initial submit disabled pending receiver readiness. It is not a private-message native GET form.

Script-free Pocket context contains no inputs/form/scripts and only fixed internal navigation. No new desktop/offline capability is inferred. The inspected core worker shell allowlist does not cache topic-query URLs or private input, and the share interception retains no-store/body-only handling. None of these mitigates ordinary native form URL serialization by itself.

## Suggested regression/browser acceptance

- Assert no private/topic input names in Pocket guide and disabled initial core submit; selectors discover all four topics through data attributes and existing values.
- Actual controller initializes all privacy cleanup handlers, validates helper methods, then enables submit. Missing helper leaves it disabled with fixed feedback; Clear/exit still erase text.
- No-JS markup has an honest requirement/fixed-guide link and no perpetual preparation claim. Static/native form contract contains no serializable private state, irrespective of whether CSP is supplied by host.
- Normal guide topics, suggestions/apply, safe exports and lifecycle tests still pass. Worker share parser/POST behavior remains separate and unchanged.
- Root may verify ordinary no-JS navigation only through permitted mechanisms. Do not change browser profile/permissions or bypass the prior upload denial. Native GET/focus, real device and offline browser effects remain unverified by reviewer.

## Authorized startup fix closure

Root selected the minimum disabled-native-submit contract, preserving name=request selectors for core/suggestions compatibility. Assigned changes are only phone.js/index.html and new tests/pocket_startup_fallback.test.cjs; root retains worker/version integration. No topic name removal or suggestions.js change was made.

New guide-submit and Prepare start disabled. Initial copy states offline access/readiness not checked. Noscript explains JavaScript is required, topic submission is disabled to avoid choices in a URL, links the fixed script-free context guide with its preparation limit and tells users to remove text manually if controls cannot respond. Core submit prevention remains installed before readiness enable. Only after all handlers/lifecycle cleanup are registered and nextSteps/hostCoverage/summary functions exist are core submission and Prepare enabled. Explicit submit with missing/incomplete helper stays disabled, gives fixed actionable reload/context guidance and never evaluates an absent helper. Core Clear and page exit still erase text in that fallback. Offline preparation is not attempted from missing-helper startup.

Regression first:three tests failed on original markup/controller. After fix, new three plus existing18core tests all pass; complete Node suite420passed, zero failures/skips. Existing offline registration/update/handshake/timeouts, clipboard race and shortcut/navigation regressions remain green.

Topic controls still have names, so programmatic form.submit() can bypass normal event/disabled-button safeguards if another script deliberately calls it. Such a call is not made by this app. No claim of forbidding arbitrary same-origin scripts is made. The selected fix addresses ordinary native user submission with unavailable controller; browser JavaScript-disabled behavior remains unverified. Root owns normal-ready browser and cachev14/package verification. No browser settings, permissions or uploads changed.
