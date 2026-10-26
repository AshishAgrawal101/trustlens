# Independent copied-text boundary investigation

No application source was changed during this audit. Cases were authored and frozen before current predictions; they are independent of the CAC diagnostic. These constructed probes establish parser behavior, not accuracy on messages in use.

## Hard line separators

Frozen cases: `frozen-cases.json`, SHA256 `0583d5fb49ab237024700de5098f04876b844b699b52e7b007d3b7fff15d8cfc`. Results: `baseline.json` (source hash included).

Ordinary text `Please send the meeting notes` followed by a line separator and `Your verification code is 847261.` produces request:code for CR, form-feed, NEL, Unicode line separator and paragraph separator. LF and CRLF do not. Direct requests, negative advice and independent subsequent requests have paired controls. The sentence regex excludes only LF; Python dot also treats these other characters differently from LF. Expand the hard boundary set consistently in sentence segmentation and the original-offset negation guard. Preserve all original text and offsets.

Python defines the complete splitlines boundaries at https://docs.python.org/3/library/stdtypes.html#str.splitlines . A test matrix should include VT and the information separators too before implementation.

## OCR/layout continuation

Separate frozen cases: `layout-cases.json`, SHA256 `c21fe41544573c8c5ec6a3e87e984a89a6dea1cee430f1195cfde8ee31c8e1b1`. Baseline: `layout-baseline.json`.

Three direct probes miss: `Send us the\nverification code.`, `Share your verification\ncode.`, and `Install the\nTeamViewer application.` Paired negation probes correctly remain without positive requests. A paragraph/control probe demonstrates why globally joining line breaks is unsafe: an unrelated meeting-notes request can borrow a code from another line. A blank-line fragment is ambiguous and deliberately unscored.

Candidate scope for root review: allow a single nonblank continuation only at an incomplete determiner or unfinished sensitive noun phrase; create an equal-length matching view with continuation characters replaced by spaces, preserving original evidence offsets and text. Never bridge blank lines, ordinary completed clauses or paragraph separators. Keep history recognition on original input. This needs explicit regression design before implementation; no blanket DOTALL or whitespace collapse is proposed.

## Separate unresolved Unicode issue

Soft-hyphen direct `Send me your veri\u00adfication code.` misses; `Do n\u00adot share your password.` falsely flags. The ordinary source-code control stays clear. Defer a normalization fix until source-offset mapping and evidence fidelity are designed. Unicode describes soft hyphen as an invisible intraword break hint: https://unicode.org/reports/tr14/ .

The complete 31-case original matrix has seven mismatches: five separator false concerns and two soft-hyphen defects. The nine-case layout matrix has three direct misses among eight scored cases; ambiguity is excluded. These are diagnostic counts, not population performance. Existing frozen evaluations remain unchanged.
