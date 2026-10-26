# Connected worksheets without persistence

Recommend the bounded new-tab continuation slice. Current Quote, Numbers and Media result-side **Open Claim & context** links navigate in the same tab. Their existing `pagehide` handlers intentionally erase inputs/results. Claim’s Tools link similarly leaves and clears its potentially long draft. Thus a person following the product’s suggested “put the claim beside its sources” workflow loses the file/wording/arithmetic they were meant to consult. The new-tab option is useful for the existing park-post rehearsal and ordinary independent source checking; it does not need another workspace or automatic transfer.

## Smallest coherent contract

1. Change only the three result-side continuation anchors to ordinary fixed-URL `target="_blank" rel="noopener"` links, visibly labelled **Open Claim & context (new tab)**. Explain adjacent to each: nothing transfers; this worksheet remains available in its current tab; Clear before closing or handing over the computer. Keep Home, Back, directory and other normal navigation unchanged.
2. Add one explicit Claim workspace action **Open other tools (new tab)** linking to the fixed directory. Place it by the workspace introduction or source-planning area so it can be used without scrolling past the whole form. Do not change every navigation link to new-tab behavior. Include the same no-transfer/current-tab/clear guidance.
3. Do not retain anything beyond the current open page: no storage, URL inputs, clipboard, postMessage, opener reference, iframe/router, beforeunload dialog or automatic window creation. Reload/closing/leaving the original tab continues clearing it; a browser may discard a background tab, so do not promise recoverable saved drafts. Users must return via their browser’s tab controls; new-tab focus/foreground behavior is browser-controlled.

This is an explicit, labelled action rather than an unexpected new browsing context. The existing native anchors give keyboard, context-menu and open-in-tab support even without JavaScript. Keep the new-tab phrase visible (not only an icon/title), normal focus rings and 44–48px target. Allow wrapping at 320px rather than forcing a single line.

## Source and canonical integration

Likely application scope: `static/quote-context.html`, `static/numbers-context.html`, `static/media-context.html`, `static/claim-review.html`; minimal shared/style additions only if the new Claim action needs layout. Controllers and validators need no change. The existing `.continue a` inline-flex patterns can serve the result-side actions.

`app/pocket_workspaces.py` already rewrites exact unfragmented Claim/directory href attributes, independent of added `target`/`rel`. Preserve those fixed href spellings. New Claim link wording must be added to the renderer’s fixed label-rewrite table: its existing **Explore all local tools →** rewrite will not match a new **Open other tools (new tab)** label. Pocket should say **Open context guide (new tab)** and retain `/phone/context.html`, never advertise uncached desktop Tools offline. Media remains desktop-only; do not add a Pocket alias. Root owns cache/export refresh and actual offline checks.

## Acceptance and risks

- Markup tests assert exactly these four intentional actions have visible new-tab labels, fixed internal hrefs, `_blank` and `noopener`; no private parameters/fields. Normal Back/Home links remain ordinary same-tab links. Existing no-JS form and private-print contracts remain unchanged.
- Renderer tests assert canonical Pocket Claim links, rewritten guide link/label and the same target/rel behavior. Preserve fixed CSP; no new script or source fetch.
- Desktop browser check without uploads: enter/Compare constructed Numbers or Quote input, activate continuation by keyboard, then use browser tab controls to return. Original draft and result remain available; destination Claim is blank with no transferred content and no opener. From populated Claim, open directory separately and return; original remains. Clear/reload/exit in the original still erase it. Use actual two-tab UI; do not fake navigation with direct controller calls.
- Narrow-width check verifies readable wrapping and focus. Offline check applies only to prepared canonical workspaces/guide and remains a desktop-browser observation, not physical-phone testing.

The tradeoff is two open tabs containing local private material, intentionally controlled by the user. Clear/close each when finished; this is not saved history or a promise to preserve drafts across reload/discard. This tradeoff is preferable to silently destroying the original while inviting a related task, and far smaller than a persistence/transfer mechanism.

No application edits, browsing, uploads, downloads or physical-phone tests were performed for this proposal.
