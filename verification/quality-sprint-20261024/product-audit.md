# Product workflow source audit — 2026-10-24 sprint

Read-only application audit of current app.js, index.template.html, primary-flow.js, original-preview.js, link-details.js, tools.html and Claim/Media/Numbers/Quote HTML/CSS/controllers. No application files edited, no browser uploads attempted, no user tabs/screenshots accessed. This is source-based heuristic review, not a user study or browser accessibility certification.

## Priority 1: private main input can become a query parameter if JS fails

Evidence: static/index.template.html line 23 form#check-form has no explicit native-submit safeguard; line26 textarea#content still has name="content"; line37 submit is initially enabled. No noscript explanation is present. Under disabled/failed JS, native form submission defaults to GET and serializes the message as content in the current URL. Hidden-by-CSS textarea drafts can also be successful named controls. This contradicts the privacy intent and differs from hardened standalone workspaces, whose controls are unnamed and initially disabled.

Minimal fix: remove name="content" (controller reads by ID), set form autocomplete=off, initially disable submit, enable only after app.js installs handlers, and provide a clear noscript message. Keep native required validation in the JS path. Root notified immediately. Severity is high impact for confidentiality when the script is unavailable; no real private data was sent in review.

Acceptance: static contract forbids names on private main controls, initial submit disabled/noscript; initialize actual controller and verify submit becomes enabled; normal Message, file extraction and Ctrl/Cmd+Enter flows still work; root browser with JS-disabled or failed-script scenario confirms input cannot appear in query/history. Do not use real private text for this test.

## Priority 2: directory links do not open the tool they describe

Evidence: tools.html lines6 and13 both link /#workspace. The Image-origin card tells the user to find More tools then Image origin; the communication card similarly hides Link/Email/Call/QR behind instructions. The actual destination defaults to Message, so the directory requires rediscovering the tool after choosing it. This is concrete friction rather than a missing analysis feature.

A safe minimal direct-navigation route is feasible. Use a closed map of exact mode-only fragments, for example /#check=text, screenshot, url, email, call, qr, image (one exact recognized value, no arbitrary IDs or query payloads). A helper loaded after the main controller should find the existing matching data-mode button and invoke its normal click handler, then focus the corresponding visible input and scroll the workspace. This reuses reset/abort/review-mode logic and primary-flow listeners, rather than directly mutating controller globals or input fields. No content/file/source value is transferred, fetched, saved or auto-submitted. Unknown/malformed fragments must do nothing.

Suggested directory presentation: separate clearly labelled links for Message/Screenshot/Link/Email/Call/QR and a direct Image-origin link. Keep the existing limits beside these links. Do not store navigation state or put private material in fragments. A same-mode link should retain the controller's existing same-mode behavior; a user-selected different mode uses the existing explicit reset semantics.

Acceptance: every link targets one whitelisted mode; all seven modes open with correct aria-pressed/group disclosure/input label; initial navigation makes zero analysis requests and preserves review requirements; unsupported/encoded/injected fragments do not select modes or populate inputs; same-page route change aborts/dismisses stale output using normal handlers; Clear/lifecycle privacy remains; keyboard focus lands on the tool's input without scrolling away. Root browser should verify direct open, Back/forward behavior, narrow layouts and native focus.

## Other reviewed paths and boundaries

- Main async generations, cancel/edit/reset and page exit clear private result/export state; screenshot/QR keep separate explicit review submissions. The original-image disclosure reuses one source and existing URL revocation. Source review found no further reproducible stale-output bug here.
- Claim roles are fixed user labels, not detected claims; invalid roles fail closed and PLAN remains input-free. Existing change-only and copy-race regressions cover lifecycle/reset risks.
- Media multipart includes only the image file, never caption. Its exact result schema rejects extra coordinate fields before rendering; textContent handles metadata labels. The previously reported generic server-error feedback has now been corrected in current source: 400 file-format text,413 size,other errors local-inspector guidance. No new issue from that old finding.
- Numbers uses BigInt cross-products before floating display, validates safe integers/count<=total, and treats zero baseline as undefined relative change. Main comparison remains descriptive and supplies no significance/causality verdict.
- Quote is bounded by4000characters/800segments per version. Diff output uses text nodes and explicit visible change-label chips. Current quote-context.css already uses inline-block visible small labels, separate from strike/underline decoration; no further style edit required. Its scroll region is keyboard focusable, output resets on edits/exit and printing suppresses private content.
- Standalone forms have unnamed controls/disabled initial submits, labelled fields/errors/results and fixed print omission. Browser-native validation, screen-reader announcements, clipboard writes/downloaded files and upload flows were not tested by this source pass.

Recommendation: fix main no-JS privacy first, then implement direct tool links as the bounded usability improvement. No new pages, models or server features are needed for either.
