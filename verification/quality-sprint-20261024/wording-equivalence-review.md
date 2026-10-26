# Independent wording-equivalence review against v14

Read-only comparison with ../TrustLens-professional-20261023-quotes-v14-review.zip app/analyzers/text.py. Archive content uses CRCRLF; comparison normalized line endings in memory only. No archive, historical results or application source edited.

The meaningful diff is limited to horizontal-space/prohibition helpers, known code compound hyphens/spacing, existing sensitive noun phrase spacing, and the two existing negation checks. _wording_view/_source_excerpt, sentence/hard-break boundaries, literal URL extraction, scoring/confidence and communication result behavior are unchanged.

No blocking regression established. Independently ran wording_equivalence plus soft_hyphen_wording: 96 passed. Tiny additional constructed pairs retain live payment after a separate I-need-you clause, remote installation after an advice sentence, and secrecy after advice. Mixed soft-hyphen/NBSP/U2011 input keeps matched evidence excerpts as exact original slices. Horizontal repairs do not rewrite the text or URL string, so they do not introduce another coordinate mapping.

Bounded unresolved limitations, not new generalized grammar promises:

- Shallow coordinated-negation scope remains: 'You should not share your password, and send $50.' currently suppresses both requests. The existing v14 'Do not ... and ...' helper already has this interpretation; expanding should/must makes that same shallow scope available for those modal forms. A comma-and clause can be interpreted differently by a reader. Do not silently add a broad independent-clause model or claim contextual understanding from the equivalence patch. Stronger explicit boundary 'but' or semicolon preserves the payment request; 'and I need you to send $50' also retains it.
- Secrecy rule itself was not expanded: 'Do NBSP not call your bank' and 'You must not tell your family' remain unmatched by the secrecy rule. These are preexisting coverage limits, not proof that the wording is safe. The new equivalences do not constitute all-rule Unicode/negation normalization.
- Conditional/refusal interpretation and general obfuscation remain deferred. Current max-length tests bound a chosen workload, not a formal worst-case regex proof or real-world detection accuracy.

Parent's reported actual browser cases were not repeated by reviewer. No native model, remote source or private communication was used.
