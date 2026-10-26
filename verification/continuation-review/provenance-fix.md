# Provenance wording correction — 2026-10-23

Implemented the second targeted-review finding in the development candidate only. No trust, parsing, cryptographic validation, model source, scoring, policy, status, timeout, or original/frozen source was changed.

Scope/callers inspected before editing: content_credentials_worker.verify and main, provenance.read_credentials subprocess wrapper and analyze_image_with_credentials fallback, main.py image endpoint, static/app.js credentials rendering, tests/credentials_crypto_check.py and tests/test_content_credentials.py. The worker returns the same status fields and metadata; the app remains responsible for reporting model_ran.

## Exact runtime diff

Only four detail string literals in app/analyzers/content_credentials_worker.py changed:

- Two external-manifest error returns: `External Content Credentials were not fetched. The detector will analyze the image.` → `External Content Credentials were not fetched.`
- Invalid verifier fallback: `Content Credentials could not be validated; the detector will analyze the image.` → `Content Credentials could not be validated.`
- Main unavailable fallback: `Content Credentials verification is unavailable; the detector will analyze the image.` → `Content Credentials verification is unavailable.`

This removes a future detector promise when ImageModelUnavailable can prevent a run. External, invalid and unavailable statuses remain identical. The ordinary non-embedded-manifest detail already described only actual provenance checks and was unchanged.

## Verification

New tests/test_provenance_wording.py covers the specific RemoteManifest exception, pinned SDK generic Remote-error form, other verifier error, main unsupported-input exception fallback, and composition with a mocked unavailable model. Test placeholders are deliberately not image payloads. RED: all four tests failed on the original promise wording. GREEN: all pass.

Targeted/native command used main Python C:/Users/round/Documents/Codex/2026-10-05/con/work/venv/Scripts/python.exe with TRUSTLENS_CREDENTIALS_PYTHON=C:/Users/round/Documents/Codex/2026-10-05/con/work/credentials-venv/Scripts/python.exe:

`python -m pytest tests/test_provenance_wording.py tests/test_content_credentials.py tests/test_image_disagreement.py -q`

20 passed in 2.05s, no skips. Includes the existing actual native signing/tampering, trusted/unknown signer, external-manifest, subprocess-wrapper and API composition tests. Those tests create their own synthetic tiny crypto fixtures in temporary storage; no development/final/user image was opened. Existing image-decision tests use mocked runtimes; no model was loaded. Raw concise result is in provenance-tests.txt.

Skipped full app/browser testing; root owns integration and the result caveat. Residual: provenance outcomes cannot establish fraud or image origin by themselves, and an optional detector may still be unavailable; the corrected wording now reflects that rather than promising a run.
