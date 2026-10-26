# Local communication model and Unicode proposal

Read-only audit: no application edits, new inference, downloads, private-content transfer or evaluation-set tuning.

## Candidate eligibility

The existing communication runtime is inspectable wording rules plus an independent structural URL parser; email adds MIME, sender/header and displayed-link consistency checks. Guidance selects fixed action plans from evidence IDs. There is no learned communication model wired into app/capabilities.py or text.py. Agreement between these components cannot establish message safety or sender identity.

The retained original session-calibration-null.json was read directly. Its digest and exact six operating-point counts are recorded in eligibility-receipt.json. MoritzLaurer/deberta-v3-base-zeroshot-v2.0-c, revision bddf8c5411c34ac3565e16e04384fd68b2618dda, remains ineligible: best correct determinate coverage 1/14 versus 8/14 required; all six points have zero wrong-confident predictions and abstain on both uncertain passages. The sixteen development passages remain unscored. High abstention is not strong safety performance. No rejected candidate retuning or development scoring is proposed. No second eligible learned communication model has been established by this audit; this is not an exhaustive inventory of unrelated machine caches.

## Smallest independent observable cross-check

A bounded structural formatting check can independently report hidden formatting characters present in the submitted text: counts and code-point names only, unknown evidence class, info severity, weight zero. Suggested wording: “Invisible formatting characters were found. They can change how copied words are matched. Review the displayed text; this does not establish intent.” It must never say obfuscation proves fraud, convert absence into safety, vote with semantic rules or claim to be a model. It is independent of semantic pattern recognition, not a second semantic judgment. Existing URL structure and email link-label discrepancies already provide stronger observable cross-checks where present. Prefer fixing the reproduced parser defect first; do not add an ornamental model counter.

If formatting evidence is implemented later, an explicit apply-free summary and input-free export policy needs root integration review. The check should be one linear pass, bounded by existing input limits, no external calls, no corpus fitting and no full text in logs. Avoid treating every Unicode format character as malicious: legitimate multilingual shaping and directionality exist.

## Exact soft-hyphen fix proposal

The independent frozen separator audit already reproduced two defects: Send me your veri<U+00AD>fication code misses, while Do n<U+00AD>ot share your password falsely warns. The ordinary source-code control remains clear. U+00AD is an intraword optional break hint (Unicode Line Breaking Algorithm, https://unicode.org/reports/tr14/), not a hard paragraph boundary.

1. Inside request_evidence only, retain original_text and build a separate matching view. Remove U+00AD only when its immediately preceding and following original characters are letters using isalpha(). Do not remove leading/trailing characters, cross whitespace or line separators, apply NFKC, delete all Cf characters, repair spelling or join lines. Repeated soft-hyphen runs are unsupported initially.
2. While constructing the view, retain a monotonically increasing source index for each kept character. Convert each normalized half-open [start,end) span to original [source_index[start], source_index[end-1]+1). Empty spans require an explicit boundary helper rather than indexing -1. This preserves interior soft hyphens in exact original excerpts.
3. Run the complete existing history, sentence, advice, reference and negation logic on the same matching view. Mixing original and normalized offsets is forbidden. For ordinary positive evidence and conditional-advice excerpts, map the final excerpt bounds back and slice original_text. The historical context output contains no excerpt and needs no display remapping. _negative_clause_before receives normalized coordinates. Never map its position into original while supplying normalized text.
4. analyze_text continues URL extraction on the original string. Do not normalize destinations; link interpretation has separate security semantics. Editable input, OCR text and caller state remain unchanged. Preserve null risk_index, low confidence, model_ran false and existing evidence weights.
5. Before coding, freeze paired acceptance covering split request/negation words, ordinary source code, independent live clauses, historical quoted examples, conditional advice, original exact excerpt slices, all existing hard boundaries, leading/trailing U+00AD, adjacent punctuation and repeated runs. Run existing history/reference/negation/email/call/guidance regressions and maximum input work guard. Save new results without overwriting any frozen baseline.

Implementation should add a tiny matching-view/span-map helper and two mapped excerpt call sites, not duplicate RULES or recursively run analyzers on multiple rewrites. No majority vote, confidence boost, new fraud rule or CAC-miss tuning is part of this proposal. Parser equivalence regressions do not establish population accuracy.

## Remaining limitations

OCR line wrapping remains unresolved: joining lines makes independently reproduced ordinary paragraph text borrow sensitive words. Soft-hyphen removal does not solve arbitrary zero-width spaces, bidi interpretation, homoglyphs, discretionary hyphen plus newline or language comprehension. A format notice can expose uncertainty but cannot decide these meanings. Real stronger local semantic modeling would need a separately eligible model, preregistered useful coverage/cost requirements and fresh admitted calibration/development sources; none is currently established.
