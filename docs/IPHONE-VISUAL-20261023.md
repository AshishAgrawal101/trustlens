# iPhone and visual workspace wave — October 23, 2026

Current development handoff for `TrustLens-development-20261023`. This supersedes the intake/reliability handoff as the current feature description; earlier reports, receipts and archives remain historical evidence. Plan: [iPhone and visual plan](../tasks/iphone-visual-plan-20261023.md). Final root checks passed: **690 Python tests and 111 JavaScript tests, zero failures or skips**. The consolidated evidence is [integration-receipt.json](../verification/iphone-visual/integration-receipt.json). The matching external iphone-v5 receipt verifies archive creation and extracted-source checks. The newer reliability handoff records subsequent changes.

## A clearer main workspace

The desktop interface now uses a deep-ink shell, teal/lime accents, a locally drawn luminous CSS lens and a bright, readable checking surface. There are no downloaded images, remote fonts or third-party UI dependencies. Four communication choices are visible first; Screenshot, QR and Image origin remain available in a separate disclosure. Constructed practice examples are expandable, and recovery/phone guides have separate support cards. Evidence, actions and uncertainty retain their existing meanings.

The input shows its current character count and mode-specific limit. Ctrl/Cmd+Enter submits only after native form validation passes; ordinary Enter, composition and alternate modifiers are left alone. Cancel dismisses the client check and preserves the draft/file preview. It aborts the browser request and invalidates late results; it does not promise to terminate work already running on the local server. Clear removes the input, preview and results. Page exit and restored Back pages erase transient private state. Copy operations have bounded fallbacks and stale-completion guards.

A user-selected missed-request checklist remains distinct from detected evidence and risk. Its fixed exports are separate from the original report summary. The original print stylesheet still exposes only the dedicated input-free summary, including when printing without pressing the app's Print button; interactive print-preview verification remains open.

Root's ordinary-browser review verified a readable 1280-pixel desktop view and 320/390-pixel main views without horizontal overflow. The actual keyboard shortcut submitted a check and the character counter matched the entered text. The URL inspector restored focus, omitted private values and cleared on edit. These are desktop-browser observations, not a physical-phone or assistive-technology certification. See [the integration receipt](../verification/iphone-visual/integration-receipt.json).

## Explain a link without opening it

Link mode has an optional **Understand this address** inspection. It reports normalized ASCII hostname, a Unicode display spelling when different, scheme, effective port, presence of text before @, path-segment/query-field counts and fragment presence. An optional known reference can be compared by exact normalized host, scheme and port. No path content, query names/values, credentials or fragment content is returned in those details. Counts describe literal structure, not the meaning or safety of the destination.

Inspection is explicit, local and bounded; no address, DNS record, redirect, reputation service or website is fetched. Source edits, mode/example replacement, Clear and page exit invalidate the result. This panel does not change the communication verdict or the existing input-free exports.

Shared hostname parsing uses the pinned `idna` package with nontransitional UTS #46 normalization, rather than Python's older transitional mapping. Hidden control/formatting characters and invalid labels are rejected. ASCII normalization is the comparison basis; Unicode spelling is a display aid, not the original spelling, proof of ownership or a guarantee that every browser parses every URL identically. A matching host, HTTPS or matching port never establishes safety. The source includes targeted IDNA/structure checks; root spot-checked a ß hostname against the browser URL parser.

Validation failures now use a fixed 422 message rather than returning the submitted value or Pydantic input/error details. Existing upload limits and privacy headers remain. This does not turn the loopback development server into a reviewed public deployment.

## Pocket and iPhone paths

Pocket has a coordinated dark mobile interface, safe-area spacing, Home Screen metadata/icon, an expandable offline-status control and persistent Review/Recover/Practice/iPhone navigation. Repeated navigation opens and focuses the intended panel, including after the user closes it. Root reviewed the earlier same-hash and keyboard-focus issues and implemented fixes. No navigation hash carries message text.

The main app links directly to the [iPhone setup guide](IPHONE-COMPANION.md), served at `/phone/ios.html`. The guide describes Safari Home Screen setup, copy/paste and copying screenshot wording with Apple's Live Text. Live Text is an Apple feature outside Pocket; Pocket receives only the text the user pastes, not the screenshot. It is not desktop OCR running on an iPhone.

**Paste copied text** requests clipboard access only on an explicit click. It replaces the review field after permission and accepts up to 30,000 UTF-16 units. Denial, unsupported access, empty/oversize text and a three-second unanswered request offer a manual-paste fallback. Edits, topic changes, Clear and page exit prevent stale paste completion from restoring old text. Pasting never starts a check. Users still review the words, choose topics and explicitly show steps.

An optional **manual Apple Shortcuts recipe** is fixed setup text, not an installed, signed or downloadable native Shortcut. It receives Text only, copies that input to the system clipboard and opens a fixed trusted Pocket URL. The message must never become the URL, query or fragment. Local Only and clipboard expiry are suggested only when available. Apps may offer Copy without the needed Share action; manual copy/paste remains the fallback. The recipe does not install Pocket or configure hosting.

Pocket also implements explicit native sharing buttons for fixed input-free next steps/recovery checklists, with copy/download fallback. No message, source URL, host comparison or incident detail is attached. The user controls the destination through their platform; native delivery is not verified on a physical device here.

The source now identifies the offline shell as `trustlens-pocket-v11` and includes the iPhone guide/assets. Preparation checks registration/update/activation and an exact-version, complete-cache handshake under a timeout. A different prepared version offers an explicit reload that clears the page text. Offline capability still depends on successful preparation, browser storage and the view used. Root verified this exact v11 shell with the local server stopped: Pocket and the iPhone guide reloaded, the offline checklist worked, Clear erased state and practice gave feedback. Repeated Recover/Shortcut navigation opened and focused its panel. The server was restarted and viewport restored. This was server-stopped browser operation, not a physically disconnected iPhone or native sharing test.

## Limits that remain visible

- Physical iPhone Home Screen installation, Safari permission prompts, Apple Shortcuts execution, native Share-sheet delivery and physical Android installation/sharing remain unverified.
- Browser file selection for screenshot/image/QR/.eml intake remains blocked by the extension's file-access setting. Backend native fixtures and controller tests do not replace that interactive step. No bypass was used.
- Pocket does not automatically read Messages/SMS, inspect the clipboard on load, monitor notifications, provide background protection or promise iOS Web Share Target reception. It is a human-guided web checklist, not a native SMS-protection app.
- A phone needs a trusted reachable secure origin. `127.0.0.1` on the phone points to the phone itself. This work did not expose the desktop server to the LAN, deploy hosting or create certificates.
- Clear affects Pocket's page state, not Photos, the operating-system clipboard, Universal Clipboard/Handoff, iCloud or copies held by other apps. A clipboard timeout cannot cancel an operating-system request already in progress.
- The frozen visual detector remains experimental and has not passed release requirements. This wave adds no accepted replacement model, image/scam accuracy claim, fitting, GPU work or new model evaluation. C2PA provenance still does not establish transaction safety.
- Full screen-reader, clean-machine and physical-device checks remain separate work. No user/community observations, public deployment, external message or submission were invented.

## Evidence and delivery status

Targeted controller tests cover the new keyboard/count/cancel controls, privacy erasure, selected guidance, link details, clipboard access and iPhone setup paths. Targeted native/API checks cover URL normalization, safe component output and input-free validation failures. They establish software behavior on the development environment, not population accuracy or physical iPhone integration.

Final evidence:

- [Python final XML](../verification/iphone-visual/pytest-final.xml): 690 tests, zero errors/failures/skips.
- [JavaScript final output](../verification/iphone-visual/node-final.txt): 111 passes, zero failures/skips.
- [Integration/browser receipt](../verification/iphone-visual/integration-receipt.json): v11 server-stopped checks, actual inspector/keyboard/navigation behavior and remaining device limits.
- [Live API smoke](../verification/iphone-visual/live-smoke.json): four communication routes and inspector, fixed no-input 422 errors, private-value omission and foreign-origin rejection.
- [Preservation receipt](../verification/iphone-visual/preservation.json): six prior archives, 104 original source files and 34 protected runtime/model/C2PA/trust files unchanged.
- [Bounded contrast audit](../verification/iphone-visual/contrast.json): 58 sampled text/button/focus cases pass. Root resolved the original focus-color failure and three small-text failures; their original ratios remain recorded. The smallest final sampled text ratio is 4.5464:1. This numerical color sample is not a complete rendered-page or accessibility audit.

The review bundle is named `TrustLens-professional-20261023-iphone-v5-review.zip`. Its matching external receipt records the final archive digest, ZIP/manifest verification and extracted-source test outcome. The receipt is external so that recording the archive digest does not mutate the archive. Keep the earlier [intake handoff](INTAKE-RELIABILITY-20261023.md), [Pocket reliability handoff](POCKET-RELIABILITY-20261023.md), [Android guide](ANDROID-COMPANION.md) and their archives intact.
