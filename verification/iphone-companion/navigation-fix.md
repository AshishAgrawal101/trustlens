# iPhone disclosure navigation / setup installation metadata

Fixed owned onboarding navigation so I use Shortcuts opens the #shortcut details and focuses its summary on initial deep-link load, hash changes and explicit anchor clicks. The click listener handles reopening after a user closes the disclosure while the URL hash remains unchanged; native hash scrolling is preserved. Only the fixed #shortcut target is handled. No clipboard read or private content operation occurs in navigation.

Added the same Pocket manifest link, icon-192 Apple touch icon and Apple web-app metadata as the main page. The manifest's start_url remains /phone/, so adding from the setup page has the same app start target instead of inventing a separate onboarding app. This config is not evidence of a real iPhone install.

Two focused regressions failed before editing, then passed. Ten iPhone plus four native-share tests now pass:14/14, no skips. navigation-tests.txt is the raw result. Existing privacy/clipboard, unsupported/denial/timeout and stale-completion checks remain green. docs/IPHONE-COMPANION.md test count was updated; root's newer expand-Offline-access instructions were preserved.

Root-owned main intro still has a minor focus-outline clipping risk: .intro overflow:hidden clips the left edge of the full-offset focus outline on .phone-setup-link. Suggested shortest root fix is .phone-setup-link:focus-visible{outline-offset:-3px}, keeping its outline inside its box without exposing the decorative ring's overflow. No main CSS/index/controller/service-worker file was edited by this worker. Own onboarding intro already permits its primary-link outline.

Skipped real browser/mobile390 verification, iPhone installation and native Shortcut execution; root owns the next visual/offline run. No external navigation/deep scheme or automatic clipboard access was added.
