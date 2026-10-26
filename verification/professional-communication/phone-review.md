# Read-only communication and phone review — 2026-10-23

Reviewed static/phone/index.html, guide.js, phone.js, static/index.template.html, app/capabilities.py, and the desktop result/configuration rendering in static/app.js. This review changed no runtime file. It did not run an Android device, install the companion, exercise an offline share, or inspect service-worker privacy/cache behavior.

## Concrete findings

1. Low-severity wording mismatch: desktop index.template.html introduces Pocket with “Offline checks are limited”, while Pocket is a user-selected checklist plus literal address parsing. The destination itself clearly states that users identify the requests and there is no automatic classification. Calling it an offline guide/checklist in the desktop entry would align expectations before navigation; the existing destination prevents a serious misrepresentation.

2. Low-severity incomplete address display: guide.js stops at 12 parsed URL matches, but the result UI does not say it displays only the first 12. A message with 13 distinct HTTP(S) addresses omits the last address without an incomplete notice. The UI correctly disclaims reputation and hidden-link checks, so this is bounded display completeness, not a fraud verdict. Explicitly saying “up to 12 addresses” would match the existing behavior.

3. Human selection remains the main useful limit: submitting no topics produces only independent-verification steps, even when the pasted wording contains an explicit code request. This matches the prominently stated design. The no-topic message says that no selection establishes no safety, so this is not a correctness bug or evidence of automatic detection. Do not describe Pocket as detecting scam requests in handoff materials.

## False reassurance and accusation checks

Desktop neutral output combines “STILL UNVERIFIED”, “No strong signs matched”, and the persistent no-warning-does-not-prove-safety statement. Guarded balance warnings say there is more to check rather than calling a sender fraudulent. The legitimate payment regression therefore causes verification friction, not an accusation in displayed wording. Image labeling and the About copy explicitly separate origin from fraud and state failed detector release requirements.

Pocket never assigns a fraud/risk score. User selections produce fixed action steps; a legitimate request can lead to the same pause/verify guidance as a scam. Its no-selection text, fixed exported summary, and result note preserve uncertainty. Copy/download call summary(selected), so hostnames and message text are absent from these exports by inspection. Message edits and checkbox edits clear stale results. No topic selection requires the user to trust an implied automatic judgment.

Capabilities returns configuration flags only; OCR text distinguishes installed language support from worker files, image text distinguishes asset/dependency presence from loading/inference, and provenance text requires a file check. The frontend repeats runtime-not-verified. No readiness or accuracy promise was found in this path.

## Public excerpt and scope audit

Both frozen public excerpts match the authoritative wording retrieved in this review task's research history. The FBI toll case is the exact final sentence of the quoted scam example at https://www.ic3.gov/PSA/2024/PSA240412 (April 12, 2024). The FTC USPS case matches the opening sentence of the public example in the indexed accessible excerpt for https://www.ftc.gov/system/files/ftc_gov/pdf/texts-spotlight-final.pdf (June 2023, page 2). FTC's plain PDF text extraction omits the screenshot bubble; exact verification relied on its accessible search excerpt, not an invented reconstruction. Neither is claimed to be a complete received message.

Count correction to report.md: simple whitespace word counts are 13 words for the FBI excerpt and 20 for the FTC excerpt, not the earlier stated 19 and 23. Both remain below 25 words per source. The frozen input was not changed. No complete source document was downloaded or redistributed. Only short attributed excerpts are stored; this is bounded educational quotation, not a claim to a dataset redistribution license. No explicit separate dataset license was obtained, and the local fixtures should not be advertised as a licensed comprehensive corpus.

Public scam labels are grounded in the authorities' descriptions of fraud examples, not in a spam label. Constructed benign controls and the constructed legitimate sensitive request are explicitly separate. The results report the residual USPS miss and the legitimate payment warning; they do not turn warning rate into fraud accuracy. The 0/2 to 1/2 in-sample improvement is too small and selected to establish generalization.

Skipped Android/device/offline-share execution and service-worker validation; root owns those checks. Residual user risk is missed requests or extra verification friction, with the current UI explicitly preserving that uncertainty.
