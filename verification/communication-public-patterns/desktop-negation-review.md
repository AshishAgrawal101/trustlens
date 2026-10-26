# Desktop negation-boundary review / manual guidance assessment — 2026-10-23

Read-only reproduction with the unchanged primary request_evidence. No text.py or other runtime source was edited. No new public diagnostic miss was tuned. The existing Python environment ran only constructed text in process.

## Reproduction

| Input | Current weighted evidence |
|---|---|
| Do not send $1.00 or buy gift cards. | request:payment (0.8), incorrect current-request concern |
| Send $1.00 or buy gift cards. | request:payment (0.8), useful direct contrast |
| Do not visit example.com and install AnyDesk. | request:remote (0.8), incorrect current-request concern |
| Visit example.com and install AnyDesk. | request:remote (0.8), useful direct contrast |
| Never ask Mr. Smith to share your password. | request:code (0.8), incorrect current-request concern |
| Ask Mr. Smith to share your password. | request:code (0.8), useful direct contrast |
| Never share your password. Install AnyDesk. | request:remote (0.8), correctly retains independent live request |
| Never share your password. NEWLINE Install AnyDesk. | request:remote (0.8), correctly retains independent live request |

The root cause is broader than punctuation splitting alone. The existing sentence splitter discards every period; its per-family negated_end resets at each fragment. But merely retaining dotted amounts/domains/abbreviations does not fully fix the domain or Mr. controls: the direct prefix guard only recognizes negation immediately before the matched verb, and the negated_end chain requires a prior matched request of the same family. Neither visit nor ask is that prior remote/code match.

## Smallest justified proposed fix — pending root agreement

Keep the existing sentences list, historical quote spans and adjacent-reference loop exactly unchanged. Pocket's whole-line suppression must not be copied into desktop: it would regress the explicitly supported independent same-line request, quoted live/history pairs and reference templates.

Add one narrow original-text negation-scope guard for current request matches. Its scope should begin only with an explicit do-not/don't/never/avoid clause, extend through that clause's and/or-linked requested actions or ask-person-to construction, and stop at a real sentence boundary, newline, semicolon, quote boundary or contrasting but clause. Dots inside currency numbers, domain tokens and the finite recognized honorific abbreviations must not reset this guard. Preserve original offsets by computing scope separately rather than replacing characters in analyzed text. Existing direct-negation/advice/history handlers remain authoritative, and nonnegated/direct counterpart behavior is unchanged. Unsupported wording remains unresolved; do not expand every negation form or call this general English understanding.

This is a small clause-context helper plus one request-match guard, not a replacement sentence parser or whole-line veto. It requires paired regressions for all three reproduced controls, both independent-live boundaries above, but/semicolon resets, quotes/history and text/email/call propagation. All existing reference/history/context tests must remain the acceptance gate. The exact implementation is not yet approved, so this report makes no assertion that an untested prototype already preserves every regression.

If root wants an even smaller first increment, fix only decimal/dotted-token segmentation for direct-negation chains and explicitly leave domain/ask scope unresolved. That would be incomplete for the reported class; the separate clause guard is the smallest complete direction identified here.

## Manual missed-topic desktop guidance: usefulness vs complexity

Useful: the frozen FTC diagnostic misses delivery/card, onward-check and task/job-payment paraphrases even while generic verification remains. Letting the user explicitly select a perceived request can expose existing code/privacy/payment/check-review actions without changing any risk level, evidence or count. This provides a concrete next step for a miss rather than pretending the matcher identified it.

Smallest complete version: one optional disclosure with existing request-action topics; user selects one, then sees the fixed REQUEST_ACTIONS plan plus VERIFY. Label it “Based on the topic you selected; not an analyzer finding.” Serve fixed plans through a read-only no-content endpoint serialized directly from REQUEST_ACTIONS, avoiding duplicated action copy in JS. No stored input/contact/account fields are needed. Clear/input-mode changes must invalidate this manual selection. If copied, its fixed summary must retain the user-selected label and remain separate from the analyzer's warning count.

Complexity is moderate UI/controller plumbing and one static-data route, with no new detection logic or model. It is justified if root completes its label, clear/stale-state and input-free export tests. Avoid auto-selecting it from diagnostic phrases or merging chosen topics into evidence/risk: those would hide the original miss and recreate false-detection claims. A full incident questionnaire or contact book is not needed.

Skipped runtime edits, prototype parser execution and browser checks. Risk remains false current-request concerns on dotted/abbreviated negative advice until a scoped fix is implemented and verified; manual topic guidance improves actions without resolving detection.
