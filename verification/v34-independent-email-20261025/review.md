# Independent email CTE review

## Required follow-up: non-ASCII CTE whitespace can still look complete

Reproduced a remaining incomplete-coverage gap for `.eml` bytes: `Content-Transfer-Encoding: U+00A0base64U+00A0` or `base64U+2003`, with the UTF-8 header and base64 body `U2VuZCBtZSB5b3VyIHZlcmlmaWNhdGlvbiBjb2RlLg==` (constructed “Send me your verification code.”). `analyze_email_bytes()` returns low with `text:none`, no `email:incomplete`, and the generic export omits incomplete status. The same pasted Unicode header decodes and matches the request. `whitespace-probes.json` preserves six actual outcomes including ASCII-space controls.

The new admission guard uses `str(value).strip().lower()`: the displayed header's Unicode whitespace is accepted, while the raw byte decoder does not interpret that header identically. Recommend bounded ASCII MIME-token/whitespace validation before admitting the body; reject or mark opaque/incomplete for unsupported non-ASCII header forms. Do not invent a decoding heuristic or classify encoded bytes as ordinary visible body text. The implementation owner/root received exact reproductions; this reviewer made no source edits.

## Reviewed boundaries

Compared normalized line-ending source with immutable `TrustLens-professional-20261024-passage-jumps-v33-review.zip`. Functional diff is confined to `body_parts()` optional incomplete accumulator, CTE admission before text yield/multipart recursion, and passing that accumulator from `analyze_message()`. Attachment return precedes admission, so opaque attachment headers/content do not contaminate readable siblings. Unknown multipart containers skip descendants while independent Subject/readable sibling warnings remain possible. Existing checked-part defects and duplicate-header checks remain intact. Supported base64/quoted-printable on multipart probes already produce incomplete via parser defects; they did not produce a newly complete clean result.

The fixed unsupported-encoding reason exposes no header token or opaque body, uses existing unknown/incomplete evidence/schema and server-authoritative generic export handling, and preserves independent positive warnings. `targeted.txt` records 61 focused tests passing (new unknown-CTE and duplicate-MIME suites). Those existing cases do not cover the non-ASCII-byte discrepancy above.

This is bounded constructed-source/controller evaluation, not full MIME standards conformance, message authenticity, population accuracy or arbitrary-encoding support. No external data, network, attachment execution, browser upload or source changes occurred. Keep the issue open until a dedicated byte-header regression and targeted fix pass; historical outcomes above should remain preserved.

## Re-review — October 25, 2026: finding closed

The implementation owner narrowed only the admission trim to ASCII space/tab/CR/LF. Independently reran the original NBSP-wrapped and trailing EM SPACE base64 headers in both paste and UTF-8 `.eml` paths: all now retain opaque bodies, report guarded/incomplete and include the existing incomplete export notice. Ordinary ASCII-space, tab and folded-header controls still decode and retain the code-request warning without incomplete evidence. `whitespace-rereview.json` records all ten constructed outcomes; original `whitespace-probes.json` remains unchanged. The updated narrow CTE suite passes 50/50 (`rereview-targeted.txt`). No additional concrete blocker found in this bounded re-review; the original finding is resolved. This does not broaden supported encodings or establish arbitrary MIME conformance. No source edits by this reviewer.

