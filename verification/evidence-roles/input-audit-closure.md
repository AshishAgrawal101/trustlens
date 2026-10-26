# Input audit closure

Read-only review of root's fixes, 2026-10-23. Both findings in input-audit.md are closed in the current source:

* The literal HTTP(S) authority guard rejects `https:example.org/a`, `https:/example.org/a`, `https:///example.org/a` and four-slash repair forms before browser URL parsing can normalize them. Independent positive checks retained uppercase HTTPS, Unicode hostnames, bracketed IPv6 with port and explicit port0. No addresses were visited.
* Identical quotation observations now explicitly say “after trimming surrounding whitespace,” matching the performed normalization. No claim of semantic or factual equality is added.

Independent constructed review() checks verified the actual fixed nextStep priority: no source URL takes precedence; then supplied future publication date; then missing quotation; then opposite user roles on identical trimmed quotations; then support-only/challenge-only gaps; otherwise compare while unresolved. This is procedural triage, not reliability weighting or a truth verdict. A quote-only source still appropriately prompts locating an original account; supplied quotations are not visited or authenticated.

Opposite support/challenge labels on identical quotations produce the context-reread prompt and a qualified question explaining that the roles reflect interpretations, not a detected factual contradiction. Changing both roles to supports removes that opposed-label question and prompts looking for contrary evidence. A selected role without any address or quote does not count as an account. No new issue found in this bounded review.

The old analyze() contract remains exactly the original three keys: observations, questions, steps. The expanded review() adds labels/nextStep separately. Fixed outputs and exported plan omit the private constructed claim. Existing generation/reset/export protections remain in the controller.

Validation: 46 focused helper/role/controller/contract tests passed, zero skips, plus independent seven-case priority assertions, four malformed-URL negatives, three valid-URL positives and exact three-key compatibility assertion. These are Node/helper/DOM-double checks; no actual-browser/device, online-source, factual-accuracy, image/model or large-file claim. Only this closure note was written.
