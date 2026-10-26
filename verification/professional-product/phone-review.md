# Phone companion review — 2026-10-23

Read-only review of static/phone source, capabilities endpoint, mount/fallback and new tests. No implementation changes. Validation: six phone JS tests and two capabilities API tests passed.

## Actionable findings

1. **P2 — Default image configuration is falsely unavailable.** `app/capabilities.py` sets `TRUSTLENS_COMMUNITY_WEIGHTS` default to an empty string, so `community.is_file()` is false when the environment variable is absent. `ai_detector/image_ensemble.py` supports the default `root.parent.parent / work/community-forensics/model.safetensors`. A valid default install can run image analysis while the new tool panel says required assets were not found. Use the same default path and add a temporary-fixture test with that variable unset. This does not require loading a model or touching protected image assets.

2. **P2 — Unconditional server-transmission privacy wording exceeds the fallback guarantee.** The textarea hint says the app does not send messages to a server. The tested successful service-worker share route does satisfy that promise, but an unhandled POST reaches `/phone/share` with the original request body when the worker is unavailable, not controlling the navigation, or unregistered. The fallback neither reads nor echoes it, but it cannot prevent transmission that has already happened. Qualify sharing privacy to successful installed-worker interception and make the fallback limitation explicit; do not claim the fallback can undo transmission. Ordinary pasted text remains local. Reproducible evidence: existing fallback test sends `PRIVATE-MESSAGE` to the ASGI server and receives 409.

3. **P3 — Offline preparation heading remains misleading after failure.** `prepareOffline()` updates only the explanatory paragraph in unsupported and failed cases, leaving the strong heading `Preparing offline access…` indefinitely. Change the heading to `Offline access unavailable` / `Offline preparation failed` in those branches. The retry remains functional.

## Verified source properties

- Share target uses bounded form POST rather than private text in a query URL. Worker handles the exact same-origin route locally and does not fetch or cache the dynamic share response.
- Shared text is escaped into a textarea, including closing tags and replacement tokens; page scripts render results with textContent. No dynamic HTML evaluation found.
- Shell cache allowlist contains only fixed public app files. Query-bearing shell requests are not added. The only fetches are fixed app assets; checked message destinations are never fetched.
- URL display uses hostname only and exports omit message text and addresses. Requests are selected by the user; no automatic scam verdict is implied.
- Clear erases both textarea value and default textContent (important for shared HTML), selections and result nodes. pagehide and restored pages clear content. Successful share navigation replaces history URL with `/phone/` without input.
- Android/secure-origin/install limitations are explicitly stated. No device testing claim, SMS permission, overlay permission or notification interception appears.

## Coverage limits

Tests exercise guide helpers, request parsing, escaping and service-worker routing. They do not execute phone.js DOM behavior, browser lifecycle, installation, platform share delivery, or actual screen-reader/mobile layout. Root owns ordinary browser verification. No extension upload bypass attempted. The POST fallback/privacy nuance is architectural and remains possible regardless of the controlled-worker unit test.
