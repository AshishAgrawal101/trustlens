# iPhone label / dark-base / native-share integration review

Updated onboarding page, its selectable Shortcut recipe and IPHONE-COMPANION.md to the actual main button label Paste copied text. Added explicit replacement wording to the onboarding step and a markup regression for exact label alignment. No Pocket index, base CSS, phone.js or service-worker source was edited.

## Static layout and contrast

Reviewed own ios.css against root's new dark phone.css. At320CSSpixels with zero safe-area inset, main has288px after16px side padding. A mobile card has246px after20px padding and borders. List/paragraph content wraps; path links use flex-wrap; recipe pre uses white-space:pre-wrap and overflow-wrap:anywhere, so its long placeholder/instructions have no min-content width floor. Controls have no fixed oversized width. Header wraps at460px. This is a static constraint check, not proof of rendered device layout.

One owned-style correction: root base intro uses overflow:hidden; on the mobile full-width primary link that could clip the visible keyboard focus outline. Own ios.css now sets overflow:visible on its intro; this page has no decorative object requiring clipping.

Computed sRGB foreground/background contrast ratios for the primary text pairs are in contrast.json. Body15.67:1, card12.77:1, muted7.69:1, secondary8.96:1, links11.06:1, lime-action10.67:1, recipe12.53:1 and button9.77:1. These exceed4.5:1 for those static color pairs; they are not an accessibility-conformance or rendered-state claim. Browser/zoom/focus/device checks remain root-owned.

## Native share review

No concrete privacy or stale-status defect found in root's shareChecklist/main/recovery handlers. Native sharing is initiated by explicit user clicks only, uses the fixed PocketGuide.summary or fixed recoverySummary, and passes only title/text to navigator.share. Message text, comparison host/reference, snippets and user URLs are not included. No installed/native-SMS receipt is claimed. Unsupported/cancelled/rejected cases get actionable copy/download fallback; arbitrary platform exception text is not printed. Current-version/visible-result or selected-recovery guards prevent pending completion from labeling cleared/newer results. Successful promise completion explicitly does not verify delivery. The device's share UI is outside app control and no real iPhone native share test occurred.

Targeted tests:8iPhone +4native-share =12passed, no failures/skips. Existing controller tests use offline doubles. No browser/device claim follows.

## Suggested main-page idle instruction (root owns markup)

“Paste copied text replaces the current message. Or touch and hold the field and choose Paste.”

Prefer a persistent helper sentence linked to the button with aria-describedby, rather than relying solely on paste-status: ios.js intentionally clears that live status on edits, so a static hint remains visible exactly when edited text might be replaced. The status can continue to announce permission/errors/success. No confirmation dialog is needed for the explicit Paste action.

Skipped browser/device execution; root is checking the v9 test build next. Reachable trusted HTTPS and browser paste permission remain required for real phone setup; manual Paste stays available when the API cannot read.
