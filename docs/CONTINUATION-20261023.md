# Verified development handoff — October 23

This separate development copy incorporates the reviewed post-freeze guidance patch and clearer image limitations. It is recommended for continued local demo rehearsal. It does not replace the frozen entry or certify hackathon eligibility. No model, threshold, credential policy or communication rule changed. No downloads, GPU workloads, public uploads, messages or automation changes occurred.

The original entry ZIP still hashes to `18cfcb73f3691deeb3c81fff3aea4b9bf593ed57ed4f2870800283f5e73fb105`. The original server remains at port 8765. This development server is at http://127.0.0.1:8766/ while its launcher remains running. The preferred port is chosen dynamically if already occupied.

## What improved

- Verification guidance now covers schools, services and other organizations through a known app/site or previously trusted contact record. Payment guidance asks users to independently confirm the amount, reason and instructions without inventing a bank-account-protection story. Display and input-free export share the same fixed text.
- How it works now leads with the installed image detector's failed release requirements and frequent historical inconclusives. Historical high scores for a different rejected candidate no longer distract from the installed model's limitations. Detailed qualified results remain in `submission/EVALUATION.md`.
- Submission rehearsal uses the three built-in constructed examples first. Screenshot and image remain optional extensions requiring a successful real check.

## Verification

463 Python tests passed, zero skips, including native Windows OCR and actual C2PA signing/tampering: 454 app tests plus nine detector-policy checks. All 17 offline controller tests passed. These are implementation checks, not population accuracy. A clean-machine dependency installation was not performed; the existing local environment was reused.

Ordinary Edge browser control now worked for page navigation and interaction. Verified in the development app: risky message action/evidence, normal code notification without a warning, disguised HTML email link, malformed URL error then successful correction, safe-account call with independent callback advice, recovery selection, practice feedback, How it works, keyboard Tab from text to Check, Enter submission, result focus, and Escape with dialog focus return. Safe-summary copy visibly succeeded and its clipboard text omitted the constructed input. Original-server Clear removed input and result; development clearing/stale-response behavior is also covered by controller tests. No claim of full screen-reader conformance is made.

Viewport observations at 320, 768 and 1440 pixels showed no document horizontal overflow; screenshots were visually inspected at 320 and 768 pixels. Desktop proof is `verification/browser-desktop.png`. Temporary viewport overrides were reset.

The screenshot fixture chooser reached a specific extension denial: enable “Allow access to file URLs” in the ChatGPT Edge extension. No setting was changed and no alternate browser, raw CDP or indirect UI bypass was used. Interactive screenshot OCR review and image upload remain unverified. Native OCR/C2PA regressions passed separately. Browser offline, forced clipboard denial and forced stale-network scenarios remain controller-only checks. Optional visual model inference was not rerun in this session.

## New constructed diagnostic

Contract SHA256: `3bfa938207d506b9cc0b5da8dd5d7d395e5f3211e6682a361feffd7aba820c35`, frozen before predictions, after rule inspection. Ten new root-authored cases: five negatives and five requests. Zero false warnings on the five negatives, zero required-request omissions on the five requests, and all ten required action titles present. This tests expected action selection, not human-rated action usefulness. Sender identity and actual safety remain unresolved for every case, irrespective of low/high risk labels.

Median rule-plus-guidance time was 0.245 ms; maximum 17.787 ms. Peak traced Python allocations after imports were 165,173 bytes. These exclude interpreter/import memory, HTTP/browser overhead, OCR and model inference; they are not end-to-end latency or process RSS. Raw reports and contract are in `verification/continuation-results.json` and `continuation-contract.json`. No rules were tuned after these predictions.

## Remaining human work

Rehearse the four-minute script with constructed examples; manually exercise file uploads and OCR review, including correcting text and confirming review. Record the actual app, resolve prior-component eligibility, and publish/submit only through a deliberate human decision. No user study, prevented-loss outcome or new accuracy claim exists. The scheduled sprint remains paused.

The review archive is a development candidate, not a replacement entry. Its receipt records its own checksum and the preserved original entry identity. Optional large weights and local configuration are excluded. Use the existing documented environment setup on another machine; optional image availability must be checked there.
