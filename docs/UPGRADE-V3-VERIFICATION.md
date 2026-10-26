# October 22: decision and email-link upgrade

## What changed

- HTML email analysis compares a literal displayed web address with its actual link host. It handles nested label markup, IDNA/case/trailing-dot equivalence, malformed and unfinished anchors, duplicate findings and a maximum of eight mismatch findings. A difference is an observation, not proof of fraud; legitimate tracking may also differ. No destination is contacted.
- A shared URL parser rejects invalid domain labels, malformed ports and ambiguous short numeric hosts. Embedded IPv6 links retain their brackets during extraction.
- Results place the recommended actions before the evidence, then group warning signs, observed facts and unknowns. Image evidence remains explicitly separate from a fraud verdict.
- Three clearly constructed examples load a code request, disguised HTML link or ordinary security reminder. Loading does not submit automatically.
- Clear erases the private result text, evidence and signer fields from the page's elements, as well as clearing the input. Copy/download remains based only on the fixed input-free summary.

## Verification

**144 Python tests passed, zero skipped, in 7.66 seconds** in the final run. This includes native Windows English OCR, actual C2PA signing/tampering and retained image-policy regressions. Receipt: `artifacts/pytest-upgrade-v3.xml`.

**11 offline JavaScript controller tests passed.** Added checks cover explicit demo submission, evidence groups, keeping image results separate, erasing private DOM-double nodes and inspecting the generated download Blob. These use a minimal DOM double, not a browser.

The first live API smoke caught a false alarm in “We will never ask you to read us a verification code.” The rule was corrected and 13 request-context regressions added. These also require a later positive request to remain flagged after earlier negated advice (code, payment, remote access, personal details, overpayment and upfront fees). This failed attempt is retained in the smoke receipt; passing test counts do not describe independent accuracy.

The final running-server API smoke verified:

- Security-code request → high / keep codes private.
- Ordinary security reminder → no matched warning, with identity still unverified.
- Different displayed/link hosts → guarded / use a known address.
- Safe-account call request → high / independent callback.
- Malformed domain → HTTP 400.
- Native screenshot extraction → explicit separate text request → security-code finding; four recovery paths available.

All successful API responses were HTTP 200. The one constructed OCR-plus-text example took 0.538 seconds; this is not a throughput benchmark. See `artifacts/smoke-v3.json`.

All 53 files in the original baseline manifest remain unchanged in the installed package. The eight frozen model/C2PA copy files match byte for byte. The updated page has 58 unique IDs, all explicit label/ARIA/fragment references resolve, and the embedded page matches its sources. The v2 source archive was preserved before rebuilding. See `artifacts/identity-v3.json` and `artifacts/package-receipt.json`.

## Limits and handoff

Browser access was denied again by the saved origin policy after the visible permission change. No browser workaround was used. Final layout, actual browser OCR interaction, downloaded-file behavior, full keyboard and screen-reader checks remain unverified. API and DOM-double checks do not substitute for them. The server is launched without opening a browser.

Link comparisons require the underlying HTML and a literal displayed URL. Plain text and screenshots may omit the real link target. CSS visibility/layout, JavaScript links and redirect destinations are not analyzed. English request rules still miss paraphrases and context. No real-world scam accuracy, new image-model accuracy, prevented loss or research novelty is claimed.

Before recording: manually check the three example buttons, Screenshot review, mobile widths, Tab/Escape, safe summary contents, Clear during a request, recovery and image credentials. Prior-component eligibility, repository publication, consented community testing, video recording and submission remain human handoff steps.
