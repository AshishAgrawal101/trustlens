# TrustLens Pocket: phone workflow and installation limits

Pocket is a separate on-device checklist and literal HTTP(S) hostname viewer. It is not the desktop detector, automatic SMS scanning, notification monitoring, live-call analysis, image inference or OCR. Users review shared/pasted text, identify requests themselves, then receive fixed independent next steps. No topic selected does not establish safety.

## What works now

Open `/phone/` on the running local app. Prepare offline access. Paste text, select the requests present, show next steps, inspect up to 12 literal addresses and copy/download an input-free action summary. Clear removes private text, selected topics and result nodes. Message/selection edits invalidate the displayed result. Page exit clears the message; no app history, localStorage or IndexedDB holds it. The service worker caches a fixed list of public application assets only.

The guide loaded and worked through ordinary Edge browser control with the local server deliberately stopped. Narrow 320/390-pixel layout and no horizontal overflow were checked. Clipboard permission remained pending in this browser; the tested three-second fallback directs users to Download. Exports omit message text and hostnames. Download functionality is controller-tested; a phone download was not exercised.

## Android path

The manifest declares a POST text share target. On a supporting browser, an installed Pocket can appear in the share sheet of a messaging app that supports sharing selected text. Review comes before guidance. This follows [Chrome's installed web share-target API](https://developer.chrome.com/docs/capabilities/web-apis/web-share-target); [Android's receiving guidance](https://developer.android.com/develop/ui/compose/sharing/receive) also recommends allowing review/editing before using shared text.

1. Serve these public application assets from `/phone/` on a secure origin reachable by the phone. Localhost is device-specific: the desktop's 127.0.0.1 address does not reach the computer from Android. The existing desktop server remains loopback-only. No LAN exposure, public hosting or tunnel was configured.
2. Open Pocket on the phone and prepare offline access. Install using the supported browser's menu or the offered Install button. A shortcut alone may not register a share target.
3. In an app that supports text sharing, select a message → Share → TrustLens Pocket. If absent, copy/paste into Pocket. Browser and messaging-app support vary.
4. Review/edit the text, identify the requests and show next steps. This does not authenticate a sender or certify safety.

No physical Android device, Android share sheet, native APK or Play Store distribution was tested or shipped. An install prompt appeared in desktop Edge, but installation was not performed. Secure phone hosting/device connectivity is an outstanding setup step, not a completed deployment. No Android SDK/build chain was found in the inspected command paths. Do not describe this as an installed Android app or automatic pop-up protection.

## Privacy boundary

Pasted-text processing is entirely in the page. When the prepared service worker controls a share, it handles its bounded POST locally, escapes the text into an uncached response, and makes no network request or stored message entry. Tests exercise hostile markup, replacement tokens, oversized/duplicate/unsupported fields, no-network share handling and shell-only caching.

If that worker is unavailable or not controlling the share, a POST may reach the hosting origin. Our local server rejects it with a generic 409, never analyzes or echoes it, and does not log its body. This fallback is not an end-to-end no-transmission guarantee for arbitrary hosting providers. Keep testing local; do not enter private content on an unreviewed remote deployment. Browser extensions, the OS share sheet, clipboard, screenshots and user-created downloads are outside app erasure controls. No external analysis APIs are called.

For a real phone release, verify the actual Android/browser share flow, secure local hosting and uncontrolled-share failure path with non-sensitive fixtures before using private messages. No permission to read SMS, notifications, accessibility services or overlays is requested.

## Verified local handoff follow-up

The constructed demo at `/phone/share-demo.html` checks the current receiver/cache version before enabling its read-only example form. A real browser form POST was verified with the local server stopped: text arrived for review without auto-analysis, the URL contained no message, selected topics produced guidance/hostname observations, and Clear plus reload returned an empty form. Readiness now requires activation plus an exact-version, complete-cache handshake with a single bounded timeout. See POCKET-RELIABILITY-20261023.md. This verifies the browser receiver rather than an Android OS share sheet.

## Comparison and recovery additions

Pocket now compares up to twelve literal HTTP(S) hostnames with a website you supply, strictly on-device, with no subdomain/brand-name trust inference or safety verdict. A selectable four-situation recovery panel provides fixed input-free steps and exports. Both features were exercised with the local server stopped; Clear/offline reload removed the private working state. See USEFULNESS-20261023.md. The Android OS and remote-hosting caveats above still apply.

## Topic hints, practice and quick access

The optional Help me spot request topics section makes conservative English literal suggestions only after a click. It quotes bounded wording; each Apply topic action is separate. A no-match result explicitly does not establish safety. Line-wide advice/history suppression intentionally misses some mixed requests. The fixed six-scenario practice lesson includes an ordinary reminder, gives feedback after a choice and saves no answers. Both new scripts are included in the public offline shell.

The manifest now declares Recovery and Practice shortcuts, following [Google's app-shortcut documentation](https://web.dev/articles/web-apps/shortcuts). In supporting installed browsers these can open the respective fixed panel. Direct in-browser fragment navigation is tested separately from the untested actual Android launcher menu. No additional permission is requested.

Prepare explicitly checks for a worker update and verifies the exact complete cache. If a different version is prepared, a Reload updated companion button warns that reloading clears pasted text. Offline update-fetch failure can still use a complete matching cache. This does not silently refresh a page holding private text.
