# Competition-readiness communication diagnostic

Local preregistered development diagnostic,23 October 2026. The 36 cases and intended warning/action expectations were finalized before any predictions on these cases. This is an internal freeze, not an external preregistration service. The cases were authored by an agent familiar with the current implementation, so they are selected and examined material, not a blind/held-out benchmark. No app, rule, threshold or model was tuned during or after this run.

## Contract and artifacts

frozen-contract.json SHA256:8e6125b637a6a5acc5f1d37eec63ed48ad3f72ef7bd0c631960773fdb47d2927. There are 9 ordinary, 9 advice, 9 adapted scam-pattern and 9 ambiguous cases; 12 each use text,email and call entrypoints. Cases include unfamiliar indirect credential/photo, cheque remainder, task-wallet, road-charge, payment-details and remote-control requests. All wording is newly authored, not actual received/private messages or bulk source quotations. Ordinary/ambiguous labels are authored scenario assumptions; sources provide related guidance, not FTC labels for these exact strings. No spam label was treated as fraud.

- results.json: per-row raw predictions, evidence IDs, fixed actions, action-theme proxy, scalar uncertainty checks, latency and source SHA256 pins.
- results.html: readable table with expandable wording/expectations/actions and related official references. It has no JavaScript, analytics, executable external asset or message-upload path.
- manual-review.json and case-review.md: manual action-usefulness notes for every row ID.
- summary.json: group counts, every miss/extra-concern/unresolved ID and explicit refusal of a pooled accuracy score.
- evaluate.py: reproducible local evaluator; CLI refuses to overwrite the original result. evaluate() supports an explicit in-memory repeat; render() only renders existing output.
- tests/test_cac_evaluation_contract.py:2 integrity checks freeze the contract digest,balance,unique IDs,source domains,expectation propagation,unscored ambiguity,repeatability flag and complete manual row coverage. Both passed,0.09 s. No assertion requires perfect analyzer outcomes.

## Preregistered measures

A warning is any positive-weight evidence. Desired warnings are scored only where the frozen expectation is Boolean; all 9 ambiguous expectations are null and remain unscored. A missing warning means no requested verification prompt matched, not that the input was certified safe. An extra concern is friction versus the authored ordinary/advice scenario, not proof the app accused a person of fraud.

Specific-action coverage checks the presence of preregistered fixed action themes. Generic Verify through a separate route is recorded separately and cannot satisfy a specific action requirement. Presence of a title is only a proxy; details and scenario fit are manually reviewed for each row. Advice inputs already contain protective instructions, so failure to repeat a desired theme is often optional-reminder absence rather than a harmful new recommendation.

Uncertainty checks require null risk_index,low confidence,no model run and rules basis. Those scalar contracts do not prove calibration, contextual understanding or correctness of a high/low risk label. One sequential local analysis+add_guidance call per case was timed, excluding imports/HTTP/browser; this is not a device or performance benchmark.

## Complete warning outcomes

| Group | Selected rows | Observed weighted warnings | Interpretation |
|---|---:|---:|---|
| Ordinary |9|5|Extra concerns in ordinary gift,reimbursement,urgent coordination,legal-information event and past account closure.|
| Advice |9|0|No protective wording was recast as a current weighted request.|
| Adapted scam pattern |9|3|Code disclosure,secure-account transfer and secrecy matched;6indirect requests did not.|
| Ambiguous |9|3|All9remain unresolved/unscored regardless of whether wording matched.|

All 6 misses are preserved: cac-scam_pattern-03(gift-card photos),05(indirect cheque remainder),06(personal-fund task wallet),07(indirect road charge),08(payment-digit/expiry collection),09(indirect remote control). Generic separate-route guidance appears in each, and the call-mode remote case gets independent callback advice, but those do not substitute for detecting the specific request.

All 5 extra concerns are preserved: cac-ordinary-01(gift),03(legitimate repayment),06(scheduling urgency),08(legal event),09(past closure record). The resulting wording remains a pause/verify instruction with explicit limits; nevertheless unnecessary high/medium concern and call-back framing can create avoidable friction.

All 9 unresolved cases are preserved as cac-ambiguous-01 through cac-ambiguous-09. The quoted password,possible suspension and mixed rehearsal/live gift wording warned; six indirect/unclear contexts did not. There is no ground truth for currentness,referent,authority or sender in these authored ambiguous cases, so neither side is counted correct or incorrect. No pooled accuracy is computed.

## Action usefulness and uncertainty

Every case has a row-by-row manual note in case-review.md/manual-review.json. On the 9 adapted patterns,2 contained all requested specific themes,2 contained some,5 had only generic verification relative to the preregistered desired themes. The secrecy/cash case lacks an explicit payment-pause action; indirect remote control lacks remote-access guidance despite useful callback advice. On advice, 8 requested specific reminders were not selected automatically, while the protective input itself often already supplied the right step. Those proxy gaps are deliberately distinguished from unsafe recommendations.

All 36 automatic reports include the generic separate trusted route. All 36 pass the four scalar uncertainty contracts. This preserves the software's no-probability/no-model promise; it does not eliminate false reassurance from a missed request or friction from a benign concern. The evaluator measures only automatic report/guidance entrypoints, not the UI's optional human-selected guidance,practice or recovery flows. Their added usefulness needs separate walkthrough evidence; no participant task study was performed here.

## Repetition and timing

The evaluator ran the same 36 cases twice without changing source. All normalized outputs excluding latency were identical, and SHA256 pins were identical before/after. This is deterministic repeatability, not independent validation. The first pass median was 0.170 ms and maximum 5.107 ms in the existing main Python process. No HTTP/network/native-image/model cost is included. Current results are tied to the source hashes in results.json; later app changes do not rewrite this receipt.

## Official source grounding

The FTC task,job,gift-card and delivery pages were reread where needed; the same-session official bank,code,toll and family guidance supplies the other pattern bases. Source URLs are in the contract and clickable per row in results.html. No third-party result supplied a label. The texts are concise adaptations, not real FTC message transcripts or claimed licensed datasets.

- Bank transfer/code patterns: https://consumer.ftc.gov/consumer-alerts/2024/06/got-call-about-fraud-activity-your-bank-account-it-could-be-scammer
- Account codes: https://consumer.ftc.gov/consumer-alerts/2024/03/whats-verification-code-why-would-someone-ask-me-it
- Gift cards: https://consumer.ftc.gov/articles/avoiding-and-reporting-gift-card-scams
- Jobs/checks: https://consumer.ftc.gov/articles/job-scams
- Task deposits: https://consumer.ftc.gov/consumer-alerts/2025/08/how-spot-avoid-task-scams
- Delivery: https://consumer.ftc.gov/consumer-alerts/2025/04/think-text-message-usps-it-could-be-scam
- Toll demands: https://consumer.ftc.gov/consumer-alerts/2025/01/got-text-about-unpaid-tolls-its-probably-scam
- Family emergencies: https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money

Skipped app/rule tuning,models,downloads,private data,final sets,public submission and user-study claims. Competition-readiness implication: demonstrate the independent-verification workflow and its limits,not general scam-detection accuracy. The six missed indirect patterns and five ordinary concerns remain reviewable evidence,not hidden failures or a reason to retune this diagnostic.
