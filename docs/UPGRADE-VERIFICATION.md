# Family-first upgrade verification

October 21, 2026, America/Chicago. This supplements the preserved v1 verification record.

## Completed

- **99 Python tests passed, zero skipped**, 8.61 seconds, including actual Windows OCR and native C2PA signing/tampering. Local receipt: `artifacts/pytest-upgrade.xml`.
- **7 offline JavaScript controller tests passed.** They exercise the required OCR review, blank OCR/manual correction, clear/switch reset, late-response rejection, timeout/error recovery, clipboard denial, input-free copying, recovery selection and invalid upload state. These use a minimal DOM double; they do not establish visual layout or assistive-technology behavior.
- The 32 developer-constructed English rule cases went from **18 exact expected matches to 32** after refinement. Five ordinary source/discount/dress/postal/programming-code cases no longer trigger security-code warnings. Added cases cover safe-account transfers, overpayment refunds, advance fees and personal details. The fixture was used to improve the rules, so this is regression evidence, not independent accuracy.
- Actual loopback HTTP: screenshot upload → native OCR → separately submitted text analysis → tailored actions. All responses HTTP 200. One constructed screenshot took approximately 0.55 seconds for OCR plus text analysis on this machine; not a throughput benchmark. Blank image returns editable empty text. Invalid image returns 400; unavailable OCR gives an actionable 503.
- Recovery endpoint exposes four fixed paths without collecting incident details. Summary tests exclude supplied names, codes, phone numbers and URLs.
- All 53 original baseline files remain unchanged in the installed package. Eight frozen-runtime copy files match the original byte for byte. No image weights, preprocessing, thresholds or C2PA worker changed. The historical actual CPU model smoke remains applicable to that unchanged path; no new accuracy evaluation was performed.

## Browser limits

The user explicitly reauthorized local browser testing. A saved browser security policy nevertheless denied `http://127.0.0.1:8765/`. No alternative browser, raw CDP, automation backdoor or permission workaround was used. Final visual layout, full keyboard/screen-reader behavior, browser download contents and actual browser OCR interaction remain **unverified**. Offline JavaScript tests do not replace those checks. The earlier observed v1 browser checks are historical, not proof of the revised interface.

## Reproduce

Run `python -m pytest -q tests` with `TRUSTLENS_CREDENTIALS_PYTHON` pointing to the installed credentials environment and `TRUSTLENS_TEST_NATIVE_OCR=1` on Windows with English OCR. Run `node --test tests/frontend_state.test.cjs` for the offline controller checks. Run `python scripts/check_requests.py` for the labeled regression cases. `tests/fixtures/request_cases.json` is included in the source bundle.

Before recording, manually verify: screenshot upload/review checkbox, payment recovery selection, Clear during an active check, keyboard Tab/Escape, 320/768/1440-pixel layout, copy/download content and Image mode's separate credentials output.

## Sources and limits

- Native API: [Microsoft Windows OcrEngine](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine?view=winrt-26100).
- Action guidance: [FTC avoiding scams](https://consumer.ftc.gov/articles/how-avoid-scam) and [FTC recovery guidance](https://consumer.ftc.gov/articles/what-do-if-you-were-scammed). These are general U.S. actions, not personalized recovery advice or a promise of refunded funds.
- No victim story, exact loss, testimonial, local prevalence, prevented loss or usability outcome has been published in this bundle. The entrant's family context guides product priorities; it does not establish measured impact.
