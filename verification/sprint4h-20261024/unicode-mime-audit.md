# Raw pasted Unicode versus encoded MIME boundary

Read-only. No parser, tests, source or prior frozen results edited. Frozen34case matrix unicode-mime-contract.json SHA2561389f4313156dcb2878c842d40d607649e5a849d7fb5af09a76ea7635d125e4b preceded evaluation. Separate36proper-encoding construction controls were frozen before execution in unicode-mime-encoding-controls.json/SHA. Full decoded text, errors/defects and analyzer reports retained in unicode-mime-results.json; actual JSON API-path comparisons in unicode-mime-api-results.json. All examples constructed, no user content/cloud/network/model.

## Concrete supported-path defect

The email UI accepts pasted visible/body-only text as well as supplied headers. Its /api/analyze/email JSON route receives a Unicode string (app/main.py:116–118), analyze_email uses Parser.parsestr (:160–162), then analyze_message calls part.get_content(errors='strict') (:187) and replacement-decoding fallback (:190). It therefore reinterprets already-decoded body text as a wire payload. This is not caused by browserJSON encoding: actual ASGI JSON posts reproduce it while direct text mode preserves the exact same string.

Paired body-only reproductions:

- `You must\u00A0not share your password.` (actual NBSP) becomes `You must\uFFFDnot share your password.` in MIME decoded body; email returns request:code plus email:incomplete, high. Proper UTF8EmailMessage bytes preserve NBSP and return text:none/low. Direct /api/analyze/text also returns no code concern. Corrupting horizontal whitespace defeats the existing supported prohibition guard, creating a false concern.
- `Send me your verifi\u00ADcation code.` becomes `Send me your verifi\uFFFDcation code.`; email returns text:none plus email:incomplete (guarded), while properly encoded bytes and direct text mode return request:code/high. The soft-hyphen source-offset rule cannot operate after replacement corruption, losing a current supported pattern.
- Ordinary `Réunion au café à six heures.` similarly gains replacement characters/email:incomplete. ASCII code-request control remains unchanged. This is a text-fidelity defect independent of request interpretation.

The existing incomplete guard is meaningful: these replacement paths emit email:incomplete and warn that interpretation was partial; they are NOT silently labelled safe. Email's MIME-incomplete summary overrides the usual low/high wording and a low result becomes guarded. But warnings computed after altered characters may still be false/missing, and the submitted body-only Unicode text was valid for the product's documented paste workflow.

## Exact parser mechanism

Local stdlib Message.get_payload(decode=True), called by get_content, first encodes a string payload as ASCII with surrogateescape. On ordinary non-ASCII Unicode input it falls back to raw-unicode-escape, explicitly treating this as outside RFC-compliant ASCII string input. Thus NBSP/SHY/Latin1letters become single byte values such asA0/AD, which are invalid in defaultASCII or declaredUTF8. Strict decoding raises, then replacement fallback inserts U+FFFD. The original parser payload before get_content still contains the correct Unicode characters; loss happens at the payload-to-bytes bridge, not HTMLParser, IDNA, JSON or text-rule normalization.

A raw HTML string with declaredUTF8 and `//bücher.example` becomes b-replacement-cher, yielding HTML/MIME incomplete and no host evidence. Correctly encoded UTF8 MIME bytes produce actualhost xn--bcher-kva.example and the existing IDNnotice. This explains the earlier test-fixture mismatch; properly encoding the fixture did not fix the product's broader body-only paste defect.

## What is valid, invalid or ambiguous

All27 representable proper MIMEencoding controls (UTF8/Latin1 and ASCIIcontrols with base64/quoted-printable/8bit) decode strictly without errors. Their bytes-path and libraryserialized-string-path reports are exactly equal. Nine construction attempts correctly fail because ASCII cannot represent the supplied non-ASCII text; these are not valid references. Preserve these paths unchanged.

Raw Unicode with an explicit ISO8859-1 header happens to roundtrip these Latin1characters because raw-unicode-escape bytes agree with that charset. That accidental success is not a generally correct browserUnicode strategy. Raw Unicode plus declaredUTF8/defaultASCII/8bit corrupts these fixtures. Raw Unicode literally placed into declaredbase64/quoted-printable transfer payload is intentionally invalid serialized MIME; partial/error handling there is appropriate, and must NOT be relaxed to make the constructed message behave like a properly encoded reference. Real base64/QP bodies remain ASCIIencoded transport text and already work correctly. No evidence here justifies dropping all MIMEencoding validation or treating invalidwirebytes as safe.

## Minimal next-fix proposal (not implemented)

Separate clearly body-only decoded-paste intake from wire-MIME intake. For the supported no-header body-only paste case, preserve the original Unicode string and call existing text/report machinery for email kind with the existing email limitations; do not push it through get_content's ASCIIwire bridge. Preserve body-only original excerpts, NBSP/SHY, sender-unverified guidance and no links fetched. Verify exact no-header detection against real header-looking text; do not silently reinterpret supplied MIMEheaders/CTE as already decoded. Headerful raw Unicode remains a separate boundary needing an explicit product policy (prefer truthful partial preservation/disclosure over invented original bytes); there is no universally correct originalcharset reconstruction from an already-decoded pasted string.

Acceptance before any fix: ASCII/body-only normalcontrols; NBSPprohibition and SHYrequest paired with correctly encoded bytes and directtext; ordinary Unicode literalfidelity; body-only text containing colon but not genuineheaders; proper UTF8/Latin1 base64/QP/8bit exactunchanged; invalidtransferencoding remains partial; declaredcharsetmismatch not silently rewritten; duplicate/MIMEheaders/attachments/HTMLhiddenrules preserved; fixed private exports never contain originaltext. Do not change detectors/negation or “repair” replacementcharacters after decoding. Root should approve exact body-only/headerful scope first.

No population accuracy, real browser/physical-device or all-charset coverage claim. These fixtures isolate a deterministic parser/input-contract mismatch and retain the existing incompleteness protection.
