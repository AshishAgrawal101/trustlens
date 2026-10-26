# v18 feasibility/spec: reuse three browser workspaces inside Pocket scope

Proposal only; no application changes before v17 freeze. Source-inspected existing Claim, Numbers, Quote, Source finder, Unicode notice, main route order, Pocket worker and static-phone exporter. Local-browser offline feature only. Physical-phone setup/publication/native Share remains deferred. v17/v16 archives and prior receipts remain immutable.

## Bounded feature

Three fixed document entries:

| Pocket GET alias | Existing source template | Browser controllers in existing order |
| --- | --- | --- |
| /phone/workspace/claims | static/claim-review.html | /static/claim-review.js |
| /phone/workspace/numbers | static/numbers-context.html | /static/numbers-context.js |
| /phone/workspace/quotes | static/quote-context.html | /static/quote-context.js, /static/source-context.js, /static/unicode-notice.js |

Use existing algorithms, markup IDs, no-script guards, field limits, lifecycle clearing and fixed safe Claim-plan exports. Do not duplicate math, diff, finder or role logic. No Message/Image/Media backend/API capability is added offline. Claim source URLs remain labels only; no source is visited. Quotes include both comparison and passage finding because the current template/controllers already support them.

The eight unique required same-origin assets are:

- /static/claim-review.css
- /static/claim-review.js
- /static/numbers-context.css
- /static/numbers-context.js
- /static/quote-context.css
- /static/quote-context.js
- /static/source-context.js
- /static/unicode-notice.js

Keep the existing responsive workspace stylesheet; do not layer global phone.css onto these templates because overlapping global body/main/input rules would create a new layout contract. A fixed Pocket-workspace label and navigation rewrite can identify the environment without a second UI implementation.

## Minimal renderer and route shape

A small pure renderer, e.g. app/pocket_workspaces.py, accepts only the keys claims/numbers/quotes from a closed map to known template filenames. Read and return those saved source templates; do not accept arbitrary paths, query/body/form input, user HTML or script names. Unknown key yields404. No private input is part of the generated document.

Rewrite only known fixed navigation hrefs/text:

- href="/" -> /phone/; brand accessible name and Back/Return-to-checker labels -> Pocket.
- href="/static/tools.html" -> /phone/context.html; labels -> Pocket context guide, avoiding an offline promise for the desktop directory.
- href="/static/claim-review.html" -> /phone/workspace/claims, retaining no automatic input transfer.
- Retain all #fragment links unchanged, including finder-to-Original and skip links.
- Retain CSS/script /static asset URLs unchanged and explicitly cache them.

Fixed replacements are reasonable for these three controlled templates; test expected occurrences/invariants so template changes do not silently leave desktop navigation behind. Do not run a general user-content HTML rewrite. Include a concise fixed notice: browser-local worksheets; offline after successful Pocket preparation; no source verification/automatic content transfer; return to Pocket to prepare or check status. No startup controller is needed for that notice.

**Route order matters:** current app.mount('/phone', StaticFiles(...)) precedes most endpoints. Register /phone/workspace/{key} BEFORE that mount, otherwise the mount will consume the request and return404 instead of falling through to the later alias route. Prefer direct200HTML responses at the exact documented paths, without a network-only redirect surprise. Choose canonical slash behavior explicitly and test it; do not accidentally cache one spelling while navigation lands on another.

Existing privacy headers can remain no-store/no-referrer/nosniff. These aliases are fixed public shell HTML, so explicit worker CacheStorage storage contains no user state. Optional stricter alias CSP can use connect-src none/form-action none because controllers need no network, but current privacy_headers overwrites CSP unconditionally; a route-only CSP header would be replaced. Do not claim the stricter policy exists unless middleware behavior is deliberately changed/tested. No broader CSP work is required for the first slice.

## Worker/cache scope

Keep registration scope /phone/. Controlled /phone/workspace clients may request the eight explicit /static assets; scope governs controlled documents, not a requirement that every resource URL begin /phone/. Existing same-origin + exact SHELL path guard can intercept those assets once intentionally listed. Do not register a root worker or intercept all /static paths.

Extend only fixed SHELL with the three alias paths and eight assets. Continue to reject queries, non-GET/private API caching and foreign origins. Existing share POST interception remains separate/body-only/no-store; do not route workspace forms through it. No dynamic rendered DOM, runtime entered values, hashes, query payloads, POST responses or API reports enter cache. Build/prepare must never cache a filled page snapshot.

Bump cache version only after route/asset integration. Atomic addAll/complete-SHELL handshake should fail honestly if any required alias/asset is missing; old cache behavior/update UI must remain covered. Cache readiness proves required shell responses exist, not device compatibility or successful controller execution. Test actual offline computations on the aliases after server stop separately.

## Portable export pitfall / explicit scope decision

Current export_phone.py exports a fixed phone/ asset allowlist and has no dynamic route renderer. A new worker requiring /phone/workspace/... would fail preparation on that static host if those documents/assets are absent. Do not silently produce a broken new companion ZIP. v17 static bundle can remain unchanged; defer a v18 portable bundle until export integration is designed and tested.

If a portable export is required later, generate alias documents from this SAME renderer at export time (no copied source templates), include only the eight fixed assets, and decide canonical static-host paths/MIME types. Extensionless file names may be served as application/octet-stream; directory index hosting may redirect to a trailing slash that is not in SHELL. A local FastAPI200alias test does not establish static-host portability. An export contract must verify every required worker shell URL maps to an exported response with the right content type and canonical navigation. Do not broad-glob the workspace or include private files/models/configuration. This decision must precede shipping a v18 static-phone artifact.

## Meaningful test scope

1. Pure renderer: exactly three keys; traversal/encoded/injected/unknown values rejected. Output contains each original DOM contract/controller order, unchanged initial disabled/unnamed forms, no user input interpolation and only approved navigation anchors. Exact eight asset dependencies exist. Shared source changes propagate without a second template copy.
2. ASGI GET: all aliases200text/html BEFORE mount, sensible unknown404, no query/body echo, no backend inference/API call. Canonical trailing-slash behavior explicit. Original /static pages and /phone/share handling unchanged.
3. Worker: exact new fixed allowlist only, same scope/origin/query/method guards; readiness requires every asset; missing alias/asset cannot claim prepared; old update/cached-shell/share tests remain green. Assert no /api paths or dynamic input/cache puts.
4. Reuse existing controller regressions against rendered alias markup when practical. Claim input/role invalidation, fixed-plan bytes, numbers zero/safe-integer boundaries, quote/source/Unicode order and lifecycle must remain green. Do not fork controller implementations or weaken old tests.
5. Actual local browser: prepare current cache, open each alias, stop server, reload alias and run constructed example; confirm no analyzer/source network requests. Follow only mapped Pocket/internal links. Clear/edit invalidates results; navigate away and Back erases private values. Test source finder with Revised blank and restored Unicode notice resets. Check320/390px/keyboard focus; these are local browser checks, not physical-phone proof.
6. No-script/failed-controller: unnamed controls + disabled startup submit preserved, fixed fallback notice available, no native private query. No profile/permission changes or upload bypass to manufacture evidence.

## Limits to keep beside the feature

No truth/credibility/independence verdict, no significance/causality inference, no source fetching, no automatic SMS/background access, no media/QR/OCR/model service offline. Clipboard/download support remains browser-dependent and user-initiated; Claim exports fixed input-free plan only. Browser storage eviction, platform installation and secure-origin availability remain real limits. No actual physical-device or user-study result is implied.

Recommended next slice: renderer + correctly ordered aliases + exact cache entries + reused-controller/ASGI tests, followed by stopped-server local-browser evidence. Keep portable export and device deployment explicitly deferred unless their separate canonical-host contract is also completed.

## Implemented canonical/export decision — 2026-10-24

Canonical entries use `/phone/workspace/claims.html`, `numbers.html`, and `quotes.html`. The `.html` suffix deliberately supports static-host HTML MIME without extensionless or directory redirects. The shared renderer supplies both ASGI responses and generated static export entries. Exact eight static assets are included in the export and worker shell. Early meta CSP restricts connect-src, form-action and base-uri to none in both forms. Cache version v15 includes all three documents and eight assets. No additional root worker scope. Root integration targeted27 tests and full1138 Python tests pass; browser/stopped-server verification remains pending at this checkpoint.
