# Opened-primary-source excerpt diagnostic

Seven short, exact published excerpts were frozen before app prediction: frozen-manifest.json SHA256 1a20943215977476f11c71df256abd210ceb98ea68ce78828226e82256f9da17. Current request_evidence source SHA256 b64db071b30e6a72023d75d5babeea6413c74842c0463dff0f0c405dce8f41eb. The unchanged analyzer ran once on each snippet. No model, download, private input, final/Arena data or cloud content analysis was used. No grammar tuning followed.

## Source and quote scope

Each source was opened and its main article text inspected; no search-only quotation or public comment/victim log was admitted. The manifest retains exact excerpts, contiguous selection boundaries, titles, source URLs, retrieved date 2026-10-24 UTC, displayed date precision and context/rationale. Where no date was visible, publication date is null; the FTC loan URL supports month precision only, not an invented day. USPIS displays a last-updated date.

Four records are official educational message/subject illustrations, not evidence that these exact texts were sent to victims. Three are official safety advice/policy statements. The short loan fragment is explicitly ambiguous when isolated. Published context informed hand labels; source authority does not make an isolated phrase determinately malicious.

Quoted snippet totals per unique page are 17,10,17,23,13 whitespace words, all within the requested 25-word budget across records. This is limited attributed quotation for evaluation, not a copied corpus, source license grant or claim of open licensing. No complete page or image was archived. No snippet contains a URL; source attribution URLs are official informational pages, not analyzed destinations. The FTC PDF was opened, but its illustrative message screenshots were excluded because the screenshot tool returned no inspectable pixels. A task-scam page fetch failed and was excluded instead of relying on search text.

Sources: [FTC loan illustrations](https://consumer.ftc.gov/consumer-alerts/2026/01/can-you-spot-fake-loan-text-scam), [Microsoft phishing illustrations](https://www.microsoft.com/en-us/security/business/security-101/what-is-phishing-email), [FTC gift-card advice](https://consumer.ftc.gov/avoiding-reporting-gift-card-scams), [USPIS delivery advice](https://www.uspis.gov/news/scam-article/smishing-package-tracking-text-scams), [Microsoft support policy](https://support.microsoft.com/en-us/accounts-billing/security/why-is-microsoft-texting-me).

## All outcomes

| Record ID | Frozen label | Exact request_evidence outcome | Interpretation |
|---|---|---|---|
| ftc-loan-reply | warning | [] | Missed the authored warning expectation; no explicit sensitive-disclosure pattern matched. |
| ftc-loan-fragment | ambiguous, unscored | [] | Short fragment lacks sufficient action context; not counted as correct or missed. |
| microsoft-security-subject | warning | [] | Missed the authored warning expectation; subject-only action demand is outside current finite wording. |
| microsoft-invoice-subject | warning | request:urgency, medium, weight0.35 | Only speed-pressure wording matched; not payment authentication or proof of fraud. |
| ftc-gift-advice | advice | [] | No false request concern on this protective sentence. |
| uspis-delivery-advice | advice | [] | No false request concern on this protective sentence. |
| microsoft-support-policy | advice | [] | No false request concern on this policy statement. |

results.json retains the full raw evidence object and per-case elapsed time. Three warning-labelled excerpts produced one wording concern and two misses; all three advice excerpts produced none. Ambiguity remains unscored. Do not pool these into accuracy, call them independent real-message validation or infer performance on spam/fraud populations. Selection is tiny, source/quote-budget constrained and author-labelled; subject/fragment truncation deliberately omits cues outside the admitted excerpt.

Observed request_evidence elapsed median 0.075 ms, maximum 4.956 ms. These single local calls exclude imports, browser/API handling and full-message/link analysis; the first call includes regex compilation effects. They are not a deployment latency benchmark.

The diagnostic ran request_evidence only, so it makes no end-to-end action-guidance, email-header, URL or report-summary claim. Generic independent verification remains necessary; no matched concern establishes safety or fraud. The evaluator refuses to overwrite retained outputs and asserts unchanged source bytes across execution. Existing historical diagnostics are untouched, and these misses are retained rather than converted into training examples or all-pass tests.
