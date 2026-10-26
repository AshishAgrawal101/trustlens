# iPhone onboarding and explicit paste handoff — 2026-10-23

New owned source: static/phone/ios.html, ios.css, ios.js; tests/ios_companion.test.cjs; docs/IPHONE-COMPANION.md. Existing Pocket markup/controller/base CSS/service worker, backend, detector and protected originals were not edited by this worker. Root owns adding the main-page controls/link/scripts/cache assets/version and browser verification.

## User flow and source grounding

The new onboarding page uses the existing phone.css base plus scoped deep-ink/teal/lime styles. It offers message, screenshot and manual-Shortcut paths, Home Screen steps, clear HTTPS/desktop-loopback limits, explicit private clipboard limits and fixed Apple/WebKit references. Layout uses wrapping actions and prewrapped recipe text, native details/navigation and keyboard focus outlines; no external font, image or executable resource was added.

Apple's current documentation supports Add to Home Screen/Open as Web App; selecting/copying Messages text; Live Text copying; Share Sheet Shortcuts with restricted Text input; Copy to Clipboard Local Only/Expire At; and Open URLs. Official pages are linked at the point of use in onboarding and docs. Research was read-only. A neutral WebKit standards position is not used as proof that a Web Share Target implementation ships; no iPhone Web Share Target reception, SMS access, device installation or native Share Extension is claimed.

The copyable Shortcut recipe is ordinary selectable setup text. No .shortcut artifact, signed-install link, bookmarklet, private-text query or URL scheme is fabricated. It puts Shortcut Input only into Copy to Clipboard, then opens a separately fixed HTTPS Pocket URL. Local Only/expiry is recommended, with OS clipboard/Handoff/iCloud explicitly outside app control. Open URLs may open Safari rather than an installed Home Screen view; the page says to prepare the view used. If the source app lacks text sharing, copy/paste is the fallback.

## Paste behavior

Expected main-page IDs: paste-message button, paste-status live region, existing message textarea. ios.js is safe to include on either Pocket or its onboarding page; it binds only controls present. The button calls navigator.clipboard.readText synchronously within its explicit click, before awaiting anything. No read occurs on page load, focus, automatic lifecycle event or a timer. It never analyzes or submits content.

Accepted text replaces the textarea and dispatches the normal input event so existing results/comparisons/suggestions invalidate. Review remains mandatory in the user flow. Up to30000UTF-16units matches the textarea's browser limit. Denial, missing API, empty/oversized result or a3second unanswered permission prompt preserve the current textarea and give manual touch-and-hold Paste instructions. The browser request cannot itself be revoked after timeout, but a late response has no assignment path. Input/Clear/example/topic changes/guide submission/pagehide/bfcache restoration invalidate pending completion and release the button. No returned exception text or private snippet is printed in status.

Root markup should indicate Paste replaces the review field and use role=status on paste-status. The clipboard is not cleared by Pocket's Clear; this is explicitly documented. External help links receive no message from this script. No network/storage/export/URL operation involves clipboard contents.

## Checks and handoff

Tests first failed with missing ios.js, then passed after implementation. Eight new tests cover no-auto-read, explicit success/input dispatch/focus, unavailable/denied/empty/oversize preservation, exact30000/30001bound, stale invalidation on every relevant event, unanswered permissions/late resolution, fixed recipe copy and selectable fallback, standalone onboarding without main controls, and privacy/install/asset markup.

All Pocket+iPhone Node suites:46passed, no failures/skips, in234.826ms. Receipt: tests.txt. This uses offline DOM/controller doubles; it does not establish native Safari paste permission behavior, actual Shortcuts action execution, iPhone installation, browser rendering or real-device offline access.

A new Android anchor link points to /phone/#android; root was asked to supply the corresponding existing instruction-section ID. Main cache inclusion, version bump and browser layout/fallback integration remain root-owned.

Skipped SDK/native app, signed Shortcut generation, phone networking/deployment, screenshot uploads, browser clipboard permission interaction and device testing. Risk: Safari may require manual Paste, Messages may lack suitable text sharing, and a trusted reachable HTTPS origin remains necessary for actual phone setup.
