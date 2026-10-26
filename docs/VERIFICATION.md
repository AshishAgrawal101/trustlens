# Verification record — October 21, 2026, America/Chicago

## Scope

Local prototype verification only. No training, new final evaluation, deployment, user study or organizer approval. Existing frozen image algorithms, classifier, thresholds and trust worker are preserved. The development computer uses Python 3.12 and the versions in `tested-environment.json`.

## Automated checks

Final run: **50 passed in 5.15 seconds**, zero failures or skips. Saved JUnit receipt: `artifacts/pytest.xml` (machine-local). JavaScript syntax check also passed. The packaged Windows launcher reached application-ready state on loopback port 8765. All 53 source files in the initial-copy manifest remain unchanged in the original installed package; eight key frozen-runtime files also match byte for byte in this copy.

Run `python -m pytest -q tests` with the optional credentials Python configured. The suite covers:

- Concrete code, payment, remote-access, secrecy and threat requests; benign code notifications and negated warnings.
- Input-free summary privacy; no original names, OTPs, phone numbers, email addresses or input URLs in exports.
- Malformed URLs, disguised hostnames, whitespace/oversize inputs and all four communication endpoints.
- Untrusted pasted authentication headers, visible HTML and link analysis, and exclusion of an attached email's body.
- Cross-origin POST and unrelated Host rejection; no-store and restrictive page response headers.
- Invalid images and a missing detector's partial credentials result.
- Actual C2PA signing, trusted vs untrusted roots, tampered hard binding, missing manifests, generated vs edited declarations, external manifests and native-worker API behavior. Synthetic test roots remain isolated.
- Frozen model disagreement and decision-policy checks.
- Launcher port collision, unexpected bind failure, readiness-gated opening, failed-start behavior and frontend embedding.

The Windows sandbox stalled the asynchronous event loop. Tests and the loopback server were run with approved local execution outside that sandbox. This does not bypass a browser permission decision.

## Actual inference

A constructed 640×480 geometric PNG was submitted to the real local HTTP image endpoint using the existing weights. HTTP 200; `model_ran=true`; C2PA status `absent`; the models disagreed and correctly returned inconclusive. CPU cold request: approximately 26.39 seconds on this computer. This is one runtime smoke test, not a speed benchmark or accuracy result. No final, Arena or user example was used.

Machine-local receipt: `artifacts/real-runtime-smoke.json` (excluded from the portable source bundle).

## Browser observations completed

The actual app was opened in the Codex in-app browser. Observed working:

- Suspicious message → quoted evidence and safe next steps.
- Ordinary code notification → no strong signs matched, still unverified.
- Copy safe summary → success status.
- Email example → copied authentication explicitly unverified.
- Call example → independent callback first action.
- Malformed URL → visible error; example retry → correct destination after @.
- Actual image file selection, preview, local upload and inconclusive result.
- All three practice scenarios, feedback, next controls and return to checker.
- No horizontal document overflow at widths 320, 768, 1024 and 1440 before the final mobile adjustment.

At 320 pixels, the first visual check found cramped mode tabs and a missing space in the heading. These were corrected in CSS/HTML. Browser access was subsequently declined. No alternative browser or indirect UI-control route was used to bypass that decision.

## Remaining checks and limits

The final 320px visual recheck, full keyboard/screen-reader audit, downloaded-summary file inspection, explicit browser offline failure, forced stale-response timing and a second-machine setup remain unverified. Clipboard success was observed; clipboard-denial fallback was inspected in code, not forced in a browser. API tests cover missing-model and malformed input behavior. The browser before the final adjustment was checked, but no saved screenshot file is included because the later capture was denied.

The source archive is CRC- and SHA256-verified by `scripts/package.py`; that is not a clean-machine installation test. Large weights and local environment paths are excluded. Core dependencies are pinned to the tested versions.

No general scam accuracy or community impact follows from these checks. Real users and unfamiliar inputs can expose failures not represented in the fixtures.
