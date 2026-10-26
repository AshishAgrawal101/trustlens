# Pocket browser workspaces — v18 checkpoint, 24 October 2026

Pocket now includes the existing Claim, Numbers and Quote workspaces for local browser use after successful offline preparation. The server and static export share one renderer; the feature does not duplicate their templates, calculations or controllers.

## What is included

| Canonical Pocket page | Existing behavior reused |
| --- | --- |
| `/phone/workspace/claims.html` | Organize a claim, supplied source accounts and user-selected evidence labels; produce questions and a fixed input-free checking plan. |
| `/phone/workspace/numbers.html` | Compare counts with denominators, rates, percentage-point differences and relative change, with a zero-baseline limit. |
| `/phone/workspace/quotes.html` | Compare two supplied versions, find exact wording in a longer supplied passage, and disclose selected invisible formatting characters without changing the text. |

Navigation returns to Pocket or its context guide. Existing field IDs, fragment links, script order, limits, disabled-startup/unnamed-form guards, edit invalidation and page-exit/Back clearing remain in use. No input is transferred between pages automatically. These browser workspaces do not add offline email, image-model, metadata, screenshot OCR or QR services.

`app/pocket_workspaces.py` exposes a closed three-page map, eight fixed assets and `render_pocket_workspace(tool, static_dir=STATIC)`. The trusted template directory is server/export configuration, never request input. Aliases are registered before the generic `/phone` static mount. Unknown keys return a fixed 404; query values are not reflected in generated HTML.

The exact shared asset list is:

- `/static/claim-review.css`
- `/static/claim-review.js`
- `/static/numbers-context.css`
- `/static/numbers-context.js`
- `/static/quote-context.css`
- `/static/quote-context.js`
- `/static/source-context.js`
- `/static/unicode-notice.js`

An early fixed meta Content Security Policy sets `connect-src 'none'; form-action 'none'; base-uri 'none'`. It travels with both server-rendered and exported HTML, intersecting the server policy when present. The fixed local CSS/scripts remain available; worksheet content does not need a connection to an analysis API or source website.

## Offline and static-export checkpoint

Pocket cache version is `trustlens-pocket-v15`. Its scope remains `/phone/`, with exact same-origin shell entries for the three canonical HTML documents and eight shared assets. This is not root-scope interception or general `/static` caching. Query-bearing requests, private API responses and entered worksheet state are not added to the shell cache.

The v18 static companion ZIP contains 32 entries and materializes the three HTML documents through the same renderer. It includes the eight explicit shared assets without copying another implementation. The static export was extracted and checked locally; its receipt reports verified bytes, no deployment and no physical-device test. Merely opening a ZIP is not offline preparation or installation.

## Verified evidence at this checkpoint

Source test receipts report **1,138 Python tests and 422 Node tests passed**, with zero failures/skips. Independent renderer acceptance tests cover closed keys/assets, fixed navigation, preserved IDs/script order, early meta policy, trusted-template propagation, canonical HTML responses, query non-reflection and unchanged original pages. These checks are regression evidence, not content-analysis accuracy or proof of user learning.

Root also exercised the extracted static export in local Edge, prepared the matching v15 shell, stopped its loopback server and confirmed connection refusal before opening all three workspaces:

- Numbers: constructed 20/100 versus 30/200 produced 20% and 15%, −5 percentage points for B minus A, and −25% relative to A. The supplied groups do not imply cause, significance or time order.
- Quotes: supplied “may close for repairs” versus “will close permanently” produced literal change marks. A separate exact passage search worked with Revised version blank and returned one match, without source/meaning verification.
- Claims: a constructed claim and quotation manually labelled as challenging produced the user's label and missing-address/date/context checks, without a truth or independence verdict.

A 320px claim-result check showed no horizontal overflow. Root did not invoke clipboard, download, native Share or file upload for these checks. The browser evidence is in `verification/offline-workspaces-20261024/browser-portable.md`; source receipts are `pytest-final.xml` and `node-final.txt` in that directory. The static-export receipt is separate from a final source-archive receipt.

## Still pending or outside the claim

Clear/edit/Back and Unicode-notice browser checks passed: edits hide prior results, navigation Back restores empty quote fields, and U+200B is named without changing text. A 390px number-result check showed no horizontal overflow. All 29 exported shell paths returned canonical HTTP200 with correct HTML/JS/CSS types; 31 manifest files matched extracted bytes. Preservation checks passed for 19 earlier source archives, three phone bundles, 104 original files and 34 protected files relative to v17. Final source packaging/extracted validation and receipt integration remain pending at this documentation checkpoint.

Physical-phone setup, iPhone/Android native behavior, public deployment/HTTPS hosting, native sharing, actual saved downloads, JavaScript-disabled native behavior, screen-reader testing and human usability/learning studies remain unverified or deferred. No browser permission or upload restriction was bypassed.

These tools do not visit sources, authenticate quotations, establish source independence, determine truth or produce reliable-model/accuracy claims. They organize supplied material and literal/descriptive observations. Offline use depends on prior successful preparation and retained browser storage; storage eviction or a different origin/browser can require preparation again. Existing model-release and publishing/eligibility limits remain unchanged.
