# TrustLens Pocket on iPhone

Use [the iPhone setup page](../static/phone/ios.html), served at `/phone/ios.html`, for the short visual walkthrough. This is a local-first web checklist, not a native iPhone app or automatic SMS reader. Physical iPhone installation, Messages sharing and Safari clipboard prompts have not been device-tested here.

## Reach Pocket first

Open Pocket in Safari using a trusted, reachable HTTPS address. `127.0.0.1` on your iPhone refers to that phone; it cannot reach the desktop launcher. This change does not expose the loopback server, configure a certificate or deploy a public site.

In Safari, open the page menu/Share menu and select Add to Home Screen. Leave Open as Web App enabled if offered, then Add. Prepare offline access inside Pocket and verify the ready state in the view you plan to use. Apple documents this [Home Screen workflow](https://support.apple.com/guide/iphone/open-as-web-app-iphea86e5236/ios); menus vary by version.

## Bring text into the review field

In Messages, touch and hold the message and use Copy, or Select then Copy when available. Open Pocket, press Paste copied text to replace the current review field, and respond to the browser's paste prompt if shown. Manual fallback: touch and hold the review field and select Paste. Review the wording, select request topics and explicitly show next steps. Nothing checks automatically. Apple's [Messages guide](https://support.apple.com/en-ca/guide/iphone/iph82fb73ba3/ios) and [text editing guide](https://support.apple.com/guide/iphone/select-edit-and-move-text-iph1a9cae52c/ios) describe these controls.

The paste button calls `navigator.clipboard.readText()` only in its click handler; it never inspects your clipboard on load, focus or a timer. It accepts up to 30,000 UTF-16 units, matching the textarea limit. Denial, unsupported API, empty text, oversize and a three-second unanswered prompt preserve the existing message and explain manual paste. Edits, Clear, example replacement, topic changes, guide submission and page exit invalidate a pending paste. See [WebKit's clipboard model](https://webkit.org/blog/10855/async-clipboard-api/) for user-gesture and permission behavior; button support is not guaranteed by this build.

For screenshots, use Photos/Live Text to select and copy wording, then paste and correct recognition errors. Copy text instead of opening detected links. This does not upload a screenshot or invoke desktop OCR. Availability varies by device, region and language; see [Apple's Live Text guide](https://support.apple.com/en-gb/guide/iphone/iph37fdd714b/ios). A screenshot saved in Photos remains outside Pocket's clearing controls.

## Optional manual Shortcut

The setup page offers copyable instructions, not an installed or signed `.shortcut` download. Build a Shortcut yourself with Show in Share Sheet and Text-only input, then:

1. Copy to Clipboard → Shortcut Input. Enable Local Only and a short Expire At time when offered.
2. URL → a fixed trusted HTTPS Pocket address such as `https://YOUR-TRUSTED-HOST/phone/`, replacing the placeholder.
3. Open URLs → the fixed URL action's output. Never substitute Shortcut Input, clipboard text, a private query string or fragment for this URL.
4. In Pocket, explicitly paste and review.

Only apps offering appropriate shared Text can run that path. Messages may offer Copy without the needed Share action; copy/paste remains the reliable workflow to try. Open URLs may open Safari rather than the Home Screen app, so prepare the view you use. Apple documents [Share Sheet shortcuts](https://support.apple.com/guide/shortcuts/run-a-shortcut-from-another-app-apd163eb9f95/ios), [input types](https://support.apple.com/en-gb/guide/shortcuts/apd7644168e1/ios), [launching content with Open URLs](https://support.apple.com/en-asia/guide/shortcuts/apdaf74d75a5/ios) and [clipboard Local Only/expiry options](https://support.apple.com/en-ke/guide/shortcuts/apd081d9d61f/ios).

Clipboard contents, Universal Clipboard/Handoff, iCloud, other apps and OS settings remain outside Pocket's control. Local Only applies to that Shortcut action; it is not an app-wide promise that the clipboard never leaves the phone. Clear removes Pocket's text/results, not Photos, system clipboard or external copies.

## Scope and verification

This build offers manual copy/paste and a recipe for Apple's supported Shortcuts actions. It does not promise iOS Web Share Target reception. WebKit lists a [neutral standards position](https://webkit.org/standards-positions/) for that API; a standards position is not proof of a shipped implementation. A native Share Extension would require a separate native app/toolchain and was not fabricated here.

New files: `static/phone/ios.html`, `ios.css`, `ios.js`; root owns links, `#paste-message`/`#paste-status` markup and offline shell inclusion/version. The onboarding page uses fixed links and no third-party executable resources. The recipe copies only fixed setup instructions; private content never enters a generated URL, request, storage or export.

Ten new offline Node tests cover explicit access, boundary/denial/timeout handling, stale completion, normal input-event invalidation, safe fixed recipe copying, standalone onboarding, repeated Shortcut disclosure navigation, shared manifest/start URL and asset/privacy markup. These are controller tests, not evidence of a real iPhone installation or working Shortcuts execution. Apple/WebKit references checked 23 October 2026; external help links need internet and receive no message from Pocket.
