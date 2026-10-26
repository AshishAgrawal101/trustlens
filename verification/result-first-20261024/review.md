# Result-first workspace independent review

Reviewed the current Claim, Numbers and Quote HTML, shared and page CSS, and existing controller result/reset/lifecycle hooks. No application files changed in this review.

## Judgment

No concrete regression found in this bounded change. Each complete result section now precedes the full static limits in DOM order, so both reading order and the mobile visual order agree. The limits remain an expanded visible section after results; no qualification has been removed or collapsed. Fixed caveats directly below each result heading retain the relevant boundary: supplied counts have no significance/causal conclusion; quote differences remain literal and both versions unverified; claim material and user labels remain unverified.

## Retained safeguards

- All three results remain initially `hidden`, labelled by their existing unique heading, and focusable with `tabindex="-1"`. Controllers still reveal and focus the same result after successful explicit submission. Error focus remains separate.
- Numbers and Quote empty guidance still disappears on results and returns on invalidation. Claim introductory text is general context, not an instruction to resubmit.
- Existing edit/Clear/pagehide/persisted-pageshow paths still hide results and remove constructed private output; the reorder changes no controller hook or field identity. Claim export availability and generation guards remain unchanged.
- Shared `[hidden]` CSS still wins with `!important`. Mobile single-column layout remains in natural DOM order; no CSS order/focus-order mismatch was introduced.
- Private print protection remains inherited from `claim-review.css`: all body children are hidden and only a fixed omission notice prints. Numbers/Quote override only that notice. Moving results does not move them outside the protected main element.
- Forms remain unnamed/autocomplete-off with initially disabled submit controls and no-script notices. This change adds no network, storage, export, input interpolation or source-verification claim.

## Independent checks

Ran Node tests `workspace_result_order.test.cjs`, `numbers_markup.test.cjs`, `quote_markup.test.cjs`, `claim_markup.test.cjs`: **13 passed, 0 failed/skipped**. Order tests check complete result-before-limits, initial hidden state, immediately adjacent fixed caveats, retained full limits and absence of collapsed limits. Source review additionally checked controller reset/focus and print rules.

Reviewed HTML SHA-256: Claim `07b4a0fa4fda77d69acb9de7fb3c1ecfcfe8309656f884a59c97b0dc4427e97e`; Numbers `ad3c2e7e407896b4ff0e98fa4d600f0e7f27decfd0ce8b073d0f32569da81842`; Quote `a48a53c435084b095aa634f52087c258fb728a9caf2b297246434cad893a087b`.

## Limits

This is source and targeted automated review, not an independent browser, screen-reader, physical-phone, print-output or downloaded-export test. Root owns current cache-v16/export-v19 and actual browser verification. Existing arithmetic, literal comparison and claim organization are unchanged; no accuracy or authenticity conclusion follows from this layout improvement.

## Subsequent root browser finding: focus position follow-up

After this source check, root observed a long Claim result where `#claim-result` was the active element but its heading was above the viewport (reported top -842px; first questions -120px). This limits the source-only conclusion: focusing a tall section does not reliably expose its beginning. Recommended minimal follow-up: add `tabindex="-1"` to each existing result heading and focus that heading after reveal, consistently across all three workspaces. This retains a semantic keyboard announcement while providing a bounded scroll target. Acceptance should assert the heading is active after success and browser-check the heading plus fixed caveat at 320/390px with long Claim output; error/Clear/lifecycle behavior must remain unchanged. No fix applied by this reviewer; root owns implementation and evidence.

## Final v21 focus follow-up review

Independently read the current three templates and controllers after the follow-up. Each existing result h3 now has `tabindex="-1"`; successful submission reveals the existing result, focuses that heading, then explicitly calls `scrollIntoView({block:'start'})` on the same bounded heading. This closes the previously reported tall-section positioning issue without changing calculations, output, field identity or export content. These headings remain outside sequential Tab order; section `aria-labelledby` still points to the same heading. Errors, invalidation, Clear and lifecycle handlers retain their previous targets and erasure behavior. Full static limits remain immediately after the complete results, visible and expanded, and fixed caveats remain directly under the headings. Shared print omission rules remain unchanged.

Independent focused run: `workspace_result_order.test.cjs`, `claim_controller.test.cjs`, `numbers_controller.test.cjs`, `quote_controller.test.cjs`: **21 passed, 0 failed/skipped**. Root reports full Node **425 passed**; that full run was not independently repeated in this bounded review.

Root-provided actual fresh-offline v21/cache-v18 browser measurements close the viewport concern: Claim at 320px heading top -0.03px and caveat 59.9px, client/scroll width 305/305; Quote at 320px heading 0.437px and diff 423.7px, 305/305; Numbers at 390px heading 0px and first fact 185.875px, 375/375. These are root browser evidence, not a separate reviewer browser session. No horizontal overflow is indicated in those measured states.

Root reports Pocket v21 export SHA-256 `e78d0451cb151468f2e6f04a4905786d557c6ea2899d9ffac4e0a76fc0c10e0d`, 32 ZIP entries, 29 canonical HTTP assets and 31 verified manifest entries. Reviewer did not rehash or reopen that archive. Python final run and source packaging remain pending at this review checkpoint. This closes the scoped source/UI review concern only; it is not a claim of overall goal completion, physical-phone testing, source verification or classifier accuracy.
