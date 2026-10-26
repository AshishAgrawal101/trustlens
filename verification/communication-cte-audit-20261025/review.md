# Candidate: unsupported MIME transfer encoding silently treated as readable text

Read-only audit, 25 October 2026. No application/tests/frozen assets changed. Six authored cases frozen before execution in contract.json, SHA256 6a9fc593a3a0aa65df922117a23d06c21d872cbacd5ea5ba860d296e06b5f0c0. results.json retains twelve full outputs (paste and .eml). This is a parser correctness diagnostic, not scam accuracy.

## Reproduction and user-visible consequence

Supply MIME-Version: 1.0, Content-Type: text/plain; charset=ascii, Content-Transfer-Encoding: x-private, blank line, then U2VuZCBtZSB5b3VyIHZlcmlmaWNhdGlvbiBjb2RlLg==. Both analyze_email(str) and analyze_email_bytes(bytes) return only text:none, low risk, normal no-strong-warning summary and no email:incomplete observation. Python's parser records no defects. The same body with the declared known base64 encoding yields request:code/high. It is NOT legitimate to assume the private encoding actually means Base64; the expected correction is explicit unknown coverage, never guessed decoding.

An x-private body containing readable request wording also gets request:code/high but no incomplete marker. Its raw bytes may not represent the interpreted body at all. Existing invalid-Base64 control correctly produces guarded/email:incomplete; 7bit and base64 controls preserve expected requests, and 8bit ordinary control remains low without incomplete. Thus this issue is missing encoding support validation, not negation grammar, a model miss or blanket decode failure.

## Root cause and standards boundary

app/analyzers/email.py body_parts selects solely declared content type. analyze_message invokes get_content and relies on decode exceptions/part.defects plus duplicate headers. Python treats an unknown transfer token as identity for this call, without a defect. The later checked-parts loop tests only duplicates, not supported transfer mechanisms. Accordingly a check can appear fully interpreted when the decoder never knew the supplied mechanism.

RFC 2045 section6.4 requires unrecognized transfer encodings to be treated as opaque application/octet-stream regardless of declared media type: https://www.rfc-editor.org/rfc/rfc2045.html#section-6.4 (opened directly during this audit). The same specification permits private extension tokens; unknown does not by itself mean malformed intent or fraud. Recognized mechanisms are 7bit,8bit,binary,quoted-printable,base64, case-insensitively; absent header defaults7bit. No standard quote reproduced here.

## Small bounded fix proposal, awaiting root authorization

At the shared MIME body boundary, explicitly recognize supported transfer encoding before treating a part as decoded readable content. Unknown/empty/malformed declared values should add fixed input-free email:incomplete explanation and skip opaque body interpretation; never infer Base64 from characters. Preserve readable independent subjects/sibling parts and their existing warnings. Reuse current incomplete summary/actions/export consumer, without new fraud score, schema or decoder. Inspect multipart handling separately: composite encodings have narrower permitted identity mechanisms; do not broaden this candidate without paired tests. Existing duplicate-header policy remains.

Focused new test module proposal: paired paste/.eml unknown opaque vs knownBase64, unknown readable vs known7bit, mixed-case supported encodings, absent header, empty/parameterized invalid header, nested unsupported leaf with independent valid sibling/subject. Assert exact incomplete marker, no claim to interpret opaque body, independent positives retained, fixed privacy-safe reason/export, no input echo or new network. Existing valid charset/CTE/duplicate/strictbytes/rawUnicode tests must remain unchanged. The frozen six-case outputs stay as before evidence; any implementation gets separate after-results.

No runtime crash, model change or private-content use found in this slice. Current wording summary still says no match does not verify safety, reducing but not eliminating misleading full-coverage presentation. Severity: medium correctness/coverage, relevant to pasted raw MIME and imported .eml rather than ordinary header-free text.
