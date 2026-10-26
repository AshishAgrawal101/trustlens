# Public-pattern communication diagnostic — 2026-10-23

Read-only diagnostic of the unchanged local text/email/call analyzers plus add_guidance. All 22 message texts were newly authored adaptations or constructed controls informed by official FTC consumer guidance. None is a real received/user message, verbatim FTC transcript or spam-corpus item. Sources establish the underlying scam patterns and safer actions, not empirical fraud labels for the exact authored text. No private content was uploaded; no supplied link was visited; no model, GPU, external content-analysis API or runtime rule edit occurred.

## Freeze and reproducibility

frozen-contract.json was written before analyzer execution, pinning source URLs, wording, mode, expected warning and intended action for each case. SHA256: 6d2457f412ff2f44631b0f879e646d6a386320633ddf69c9e27e4f498d80fff5. The current source hashes are recorded in results.json and verified identical before/after execution. No test-case selection or heuristic tuning followed these outcomes. The previous frozen diagnostics remain untouched.

There are 14 adapted scam-pattern scenarios, seven ordinary/advice controls and one legitimate sensitive payment. Expected warning means a useful independent-verification prompt, never a binary fraud label. A current request can legitimately warn; an ordinary gift control can reveal overly broad concern. These selected examined cases are not a benchmark, held-out set or estimate of real-world detection accuracy.

Run from development root with PYTHONPATH set there: python verification/communication-public-patterns/evaluate.py. Uses the existing local main Python environment. Email inputs get a neutral Subject plus body wrapper; calls use kind=call; text uses normal analyze_text. Native HTTP/browser paths are not exercised.

## Results and action usefulness

Eight of the 14 adapted pattern scenarios emitted a weighted warning; six did not. Six of seven ordinary/advice controls avoided a weighted concern; the birthday gift request triggered one. The legitimate lunch repayment warned intentionally. No result established fraud or sender identity. All 22 retained risk_index=null and confidence=low.

| Case | Warning outcome | Action usefulness against frozen expectation |
|---|---|---|
| delivery-fee | Miss | Generic separate-route verification helps, but no delivery-specific or payment-pause action appears. |
| delivery-details | Miss | Generic verification helps; no specific hold-card-details instruction appears. |
| toll-urgent | Warning | Independent verification is useful; urgency alone does not select a payment-pause action. |
| toll-balance | Warning | Payment pause plus separate route fits the intended intervention. |
| bank-protection | Warning | Call-back independently plus payment pause fits. |
| bank-code | Warning | Explicit code privacy plus independent call-back fits. |
| job-onward-check | Miss | Generic verification omits the key check/available-balance distinction and bank-review instruction. |
| job-entry-fee | Miss | Generic verification helps; it does not explicitly address paying to obtain work. |
| task-deposit | Warning | Payment pause is useful; guidance does not specifically explain paying for supposed earnings. |
| task-topup | Miss | Generic verification omits the own-funds/top-up trap. |
| gift-demand | Warning | Payment pause helps; card-number confidentiality is not specifically selected. |
| gift-number-only | Miss | Generic verification omits the immediate gift-card credential risk. |
| family-wire | Warning | Independent call-back, payment pause and trusted-person steps fit. |
| family-courier | Warning | Independent call-back/trusted-person advice fits, though cash handover is not specifically discussed. |
| control-code-notification | No concern | Appropriate distinction from disclosure; generic output lacks unexpected-code account-activity advice. |
| control-bank-advice | No concern | Avoids recasting protective advice as a current transfer. |
| control-toll-check | No concern | Separate-route action remains consistent with protective wording. |
| control-delivery-tracking | No concern | Sender/intent remain unverified; no new sensitive request is invented. |
| control-task-advice | No concern | Avoids recasting advice as a current crypto request. |
| control-gift-birthday | Extra concern | High payment-pause warning is overcautious for the stated gift; it does not accuse fraud, but lacks ordinary-gift context. |
| control-family-check | No concern | Independent contact advice is consistent; generic end-call framing assumes a call context but proves no caller identity. |
| legitimate-sensitive-lunch | Warning as intended | Pause/verification is mechanically appropriate for a sensitive request; high urgency may add unnecessary friction for legitimate repayment. |

The six misses are not resolved by the no-strong-signs wording: the existing summary correctly says it cannot verify safety, and every result still offers a separate trusted route. That caveat limits false reassurance but does not make missing request-specific advice equivalent to detecting the request. Action usefulness above is a manual comparison with frozen intent, not a scored user study.

## Timing

One sequential local in-process call per case, including add_guidance and excluding module imports: median 0.122 ms, maximum 10.772 ms. Imports took 353.240 ms separately; the first case includes initial regex cache work. Timings use perf_counter and include no HTTP, browser, model, network or device cost. This tiny single pass is descriptive plumbing evidence, not a latency guarantee or comparative benchmark. Per-case raw timings and source pins are in results.json.

## Source lineage and publication scope

Only official FTC consumer pages were used as evidence; no third-party search result, comment, video, linked destination or dataset supplied a case label. Initial search returned other domains, but only the official pages listed in frozen-contract.json were opened/used. The body advice on the FTC pages supports these authored patterns. No bulk source text is reproduced and no upstream dataset redistribution license is claimed; the contract stores concise paraphrases, citations and newly written message wording.

- Delivery: https://consumer.ftc.gov/consumer-alerts/2025/04/think-text-message-usps-it-could-be-scam
- Toll: https://consumer.ftc.gov/consumer-alerts/2025/01/got-text-about-unpaid-tolls-its-probably-scam
- Bank: https://consumer.ftc.gov/consumer-alerts/2024/06/got-call-about-fraud-activity-your-bank-account-it-could-be-scammer
- Jobs: https://consumer.ftc.gov/articles/job-scams
- Tasks: https://consumer.ftc.gov/consumer-alerts/2025/08/how-spot-avoid-task-scams
- Gift cards: https://consumer.ftc.gov/articles/avoiding-and-reporting-gift-card-scams
- Family emergencies: https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money
- Code notifications/privacy: https://consumer.ftc.gov/consumer-alerts/2024/03/whats-verification-code-why-would-someone-ask-me-it

## Optional demo material

Four concise candidates in demo-candidates.json carry the visible label Adapted FTC pattern, mode, citation and teaching note. Bank code, family wire and task deposit currently warn. The delivery-fee candidate is explicitly marked as a current rule miss and must not be presented as a successful automatic detection. These are educational examples, not real user messages or proof of accuracy. Root can choose to integrate them; this worker added none to the app.

Skipped rule tuning, model work, broader corpus claims and browser/API integration. Residual: indirect payments, onward-check wording, card-photo requests and delivery details can evade current literals; ordinary gift or repayment requests can be over-warned.
