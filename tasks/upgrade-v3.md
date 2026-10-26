# TrustLens: clearer decisions and stronger email checks

October 22, 2026. Requested: plan and execute a substantial hackathon improvement. “100x” is an aspiration, not a measurable claim.

## Plan and scope

1. **Inspect deceptive links accurately.** Compare an HTML email's displayed web address with its actual link host. Explain legitimate tracking differences; never visit the destination or label the sender a scammer. Reuse one strict address parser in URL and email checks; reject malformed domains rather than displaying misleading parsed facts. Reach: URL/email analyzers, guidance, API regressions and constructed fixtures.
2. **Put the useful decision first.** Put the first recommended action above details, group warning signs / observed facts / unknowns, and keep uncertainty visible. Keep model/C2PA evidence separate from fraud. Reach: template, stylesheet, controller and offline state tests.
3. **Make the demonstration self-contained.** Add three clearly constructed one-click examples (code request, disguised email link, ordinary safety message), with an explicit Check step. Keep screenshot OCR, recovery and image credentials accessible. Reach: frontend, controller tests and demo/judge instructions.
4. **Verify and hand off.** Run relevant regression/API/native OCR/C2PA checks, preserve frozen image/runtime identities, check exports never include private text, rebuild and verify the source archive, and launch the updated local app without opening the browser.

## Boundaries and risks

- No new dependency, account, paid API, model retraining, changed image thresholds, real victim details, automatic messages or publication.
- Email label/host differences also occur in legitimate tracking. A finding is a reason to inspect; no match is not a safety certificate. This parser does not render mail-client layout or follow redirects.
- Existing interfaces and private-input-free summaries remain compatible. No stored inputs/history are introduced.
- Browser policy again denied localhost on October 22. Do not work around it. API/DOM-double tests are distinct from visual, keyboard and assistive-technology checks.

## Completion

- [x] Link checks, strict parser and tailored guidance implemented and tested.
- [x] Action-first grouped results and constructed demo choices tested with an offline DOM double.
- [x] Native and regression checks, baseline identity, docs and local launch verified; source archive verified by the packaging step.
- [ ] Real-browser visual / keyboard / export verification (blocked by browser policy).

Integration found one additional false alarm in “We will never ask you to read us a verification code.” Fixed negated-request handling and retained later positive requests with 13 regressions. Clear also now erases private evidence nodes instead of only hiding the result. Final software checks: 144 Python tests, 11 offline controller tests. See `docs/UPGRADE-V3-VERIFICATION.md`.
