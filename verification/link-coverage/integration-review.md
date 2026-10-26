# Link coverage / hostname comparison integration review — 2026-10-23

Read-only scope: app/guidance.py, static/app.js, static/phone/guide.js compareHosts, static/phone/compare.js and their HTML/control context. No browser, model, external service, dataset, app edit or URL visit was used.

## One actionable presentation weakness

Trigger: a high-severity finding among the first eight links plus a ninth unique link (for example the existing test's first-link userinfo warning). static/app.js showReport gives incompleteLinks precedence over risk_level=high for the main heading. The previously strongest “Don’t act on this request yet” becomes “Some links still need review.” The summary and actions retain the real concern, so this is not a false clean verdict, but the highest-priority instruction is weakened by adding unchecked content.

Shortest fix: keep the incomplete tag/evidence and link-review action, while giving high-severity concern precedence in the heading, or use a combined heading such as “Pause; some links also remain unchecked.” A controller regression should combine high concern with analysis:links_incomplete, rather than testing only a neutral overflow. No risk-level or detector change is needed.

## Checks without additional findings

- Main UI recognizes analysis:links_incomplete and no longer uses the neutral no-signs headline on neutral overflow. The fixed export says link review was incomplete and describes the eight-unique-link limit without including counts extracted from text, URLs or private wording. It does not count a zero-weight coverage limitation as a fraud warning.
- Link-review guidance explicitly directs users to a known route instead of opening unchecked links to investigate. It remains present even when the first two request-specific actions fill their slots.
- compareHosts uses URL parsing only, normalizes one trailing hostname dot, and compares exact parsed hostname equality; the reference rejects credentials/@, unsupported protocols, spaces, control characters and backslashes. Subdomain differences, IDNs and normalization are not treated as sender proof. Ignoring paths/ports is consistent with the explicitly hostname-only comparison. A user-supplied “known” domain is never authenticated, and both input guidance and output preserve this limit.
- Comparison rendering uses textContent and creates no clickable supplied URL. A matching host still says safety is unestablished; a mismatch acknowledges legitimate subdomains/tracking. No ownership/sender verdict was found.
- Message/reference input, selected-topic changes, guide submission, Clear, example replacement and page lifecycle events invalidate the rendered comparison. Compare is synchronous, so there is no late network response to repopulate state. Clear and pagehide also erase the reference value. Reference text is not incorporated into PocketGuide.summary or desktop share_summary.
- Pocket's existing twelve-address display limit is visible in its host section, which also contains comparison. The comparison does not claim to compare omitted hidden links or prove that a reference site is legitimate.

Skipped dynamic controller/browser execution because root is performing integration. Residual: user selection and supplied reference remain fallible, and exact hostname equality is not safety; current wording consistently states those limits.
