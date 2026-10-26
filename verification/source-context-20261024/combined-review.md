# Combined adversarial review: source finder, Unicode notice and email interpretation

Started as read-only review of source-context.js, unicode-notice.js, quote HTML and email.py. Root then explicitly assigned a minimal email fix after the duplicate-header reproducer. Only app/analyzers/email.py and new tests/test_email_duplicate_mime_headers.py were changed for that fix; no quote/UI source, archive or historical result was changed. No browser/uploads/external data used.

## Resolved P2: duplicate MIME interpretation headers looked complete

Constructed message with Content-Transfer-Encoding:7bit then Content-Transfer-Encoding:base64 and base64 text for 'Send your password.' returned low/text:none without email:incomplete. A duplicate Content-Type plain/html message also chose one interpretation silently. Existing ambiguity checks covered From/Reply-To/Subject but not MIME interpretation headers.

Regression first: ten failures and one passing skipped-attachment case. Minimal implementation now flags repeated Content-Type or Content-Transfer-Encoding on checked parts (top-level and readable body parts) through the existing incomplete-result path. It does not try alternative decoding, merge interpretations or turn one interpretation into trusted content. Readable signs remain visible and high-risk findings remain high; otherwise incomplete low results become guarded under the existing policy. Header values/filenames are not included in the new fixed caveat. Attachments remain skipped and cannot contaminate readable-body findings.

Validation: new eleven regressions cover both header orders, top-level/nested checked bodies, preserved readable password requests, conflicting transfer encodings through text and bytes entry points, safe summary incomplete disclosure and skipped attachments. Combined email suite83 passed, zero failures. This confirms the bounded fix, not full MIME support or independent sender authentication. Nested container/header cases outside checked readable parts remain governed by existing parser-defect/unscanned coverage; no comprehensive alternative parser was added.

## Source finder and Unicode notice: no additional concrete blocker found

Independently ran source_context/source_controller/unicode_notice:35 Node tests passed. Exact case/whitespace/non-overlapping semantics, capped windows/total count, edge ellipses, source example clearing and original/finder jump links remain consistent. Both texts are unverified. Hit and no-hit wording does not authenticate, establish meaning or declare fabrication. Quote Original/Revised requirement and comparison-only segment limits now explicitly scope the shared field, closing the prior copy issue.

Unicode inspection counts a finite named list and does not normalize or rewrite input. Legitimate shaping/emoji explanations prevent formatting presence from becoming a maliciousness conclusion; no notice when none are found is not a positive assurance. The source notice scans the whole supplied source, including characters outside displayed windows. Actual underlying match behavior remains literal.

Controller order is quote then source then Unicode notice. Successful submit updates result before notice reads its visibility; failed/native-invalid submissions and input/example/clear/lifecycle reset the notice. Notices use fixed field labels, code point names/counts and textContent, never copy original private wording into the summary. No network/storage/export API or unsafe markup rendering was introduced. Bidi controls can still change how supplied snippets are displayed; the notice explicitly warns rather than claiming to sanitize or verify them. This is a visibility aid, not universal Unicode detection or rendering containment.

Remaining limits: native screen-reader announcements, actual browser history snapshots, source jump/focus and exact visual rendering were not independently tested in this pass. Root browser evidence remains separately attributed. No real email/source data or native model was used. Full application tests/package verification remain root-owned.
