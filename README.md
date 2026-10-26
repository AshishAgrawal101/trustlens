# TrustLens — a second look, before you act

Current source checkpoint: [Native count correction and Screenshot contrast guidance v42](docs/INPUT-RECOVERY-V42-20261025.md). Numbers identifies count-over-total errors at the existing count fields while preserving pure arithmetic, separate drafts and explicit Compare. Screenshot adds manual opaque-contrast help and a blank-result notice; runtime OCR/image/QR processing is unchanged. Final source tests pass 1,616 Python and 618 JavaScript checks, zero skips. Actual desktop and Pocket42/cache35 server-off correction/reset checks pass. Use the matching external release receipt for archive/extracted/preservation verification; physical phone, human-study, publication and model-release limits remain open.

A local content-trust prototype for messages, claims, source context and images. The checker reviews request wording, address structure and optional image-origin evidence. The new Claim & context workspace organizes a supplied claim beside two source accounts, publication dates and missing checks. It does not decide factual truth, authenticate sources, declare people scammers or guarantee safety.

## Run this build

On the development computer, double-click **Start-TrustLens.cmd**. Its local configuration uses the existing Python environments and frozen weights. The app opens its own available address starting at **http://127.0.0.1:8765/**. Keep the launcher open; Ctrl+C stops it. No training or scheduled process is started.

On another computer with Python 3.12:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python serve.py
```

The four communication checks work without model weights, accounts, API keys or remote services. Image uploads return an honest partial result if optional components are unavailable. Dependency installation needs internet; checking content does not.

## What works

| Input | Actual check | Deliberate limit |
|---|---|---|
| Message | English request patterns, quoted wording, up to eight embedded links | Rules can miss context; not a calibrated scam model |
| Link | Actual hostname, user-info disguise, HTTP, IDN, subdomains, numeric host, known shorteners | No page visit, redirect expansion or reputation lookup |
| Email | Plain/HTML body, displayed-address vs link-host comparison, supplied headers; attachments excluded | Legitimate tracking links can differ; plain text can hide a destination; pasted authentication results are untrusted |
| Call | Transcript wording and independent callback guidance | No recording, transcription, caller ID verification or voice-clone detection |
| Claim & context | Supplied claim, two source accounts, optional event/publication date comparisons and a fixed checking plan | Manual organizer; no truth verdict, source authentication or live search |
| Screenshot | Native Windows English OCR → editable text → explicit review → message analysis | Windows English OCR must be installed; small text and links can be misread |
| QR image | Local OpenCV decoding → editable values → explicit review → message/link checks | Optional decoder required; damaged or small codes can be missed; no destination opens |
| Quote & context | Local literal comparison, exact quotation search with five-window paging through all matches, and factual invisible-format notices | Changes do not determine meaning, source authenticity or truth |
| Numbers & context | Local counts/denominators or reported percentages, rates/changes and explicit A/B swap | Descriptive arithmetic; no significance, cause or truth conclusion |
| Media context | Local file dimensions and bounded editable metadata, with caption/source questions | Metadata does not establish scene, location, origin or caption truth; no reverse search |
| Image | Local frozen CLIP/CommunityForensics model and embedded C2PA verification | AI origin is distinct from fraudulent intent |

Results put an actionable next step first, then group warning signs, observed facts and unknowns. Actions adapt to matched requests for money, codes, remote access or personal details, and misleading link structure. A recovery guide covers sent money, exposed accounts, remote access and opened links, with links to FTC guidance. No incident details are required. Recovery is not guaranteed.

Three practice-check buttons load a constructed code request, disguised email link or ordinary security reminder; they require an explicit Check action. A separate constructed photo-claim link loads the worksheet without running Review. The ten-scenario Practice journey covers communications, source independence, media dates, numbers, quotations, headline context and advertising disclosures, with reviewed progress, completion, retry and restart; it does not assess real-world ability. Copy/download includes only fixed guidance and a count of matched signs, never original wording, contact details or user-supplied URLs. Clear erases rendered result nodes as well as the input.

## Screenshot setup

On Windows, the app uses the installed English OCR engine through Windows PowerShell 5.1. No OCR library or language-model download is made by the app. If that OS component is unavailable, paste or type the message in Message mode. OCR normalizes the image and limits its longest dimension to 3,000 pixels; crop to the relevant message if small text is lost. Review all wording and links before checking.

The worker has a 30-second timeout, runs hidden, allows one OCR operation at a time and removes its temporary PNG on success or failure. Screenshot mode does not check C2PA or visual AI origin. Image mode retains those separate checks.

## Optional image components

The bundle deliberately excludes large foundation weights. It includes the frozen small classifier and its checksum metadata. Existing model policy, preprocessing and weights are unchanged. Only load trusted model files; joblib is an executable serialization format.

Install `requirements-ai.txt` into the inference environment if needed. Exact versions used on the development computer are in `docs/tested-environment.json`; CPU was tested. Configure local paths using `local-runtime.json` (not committed or bundled):

```json
{
  "TRUSTLENS_CLIP_CACHE": "C:/models/clip",
  "TRUSTLENS_COMMUNITY_WEIGHTS": "C:/models/community/model.safetensors",
  "TRUSTLENS_CREDENTIALS_PYTHON": "C:/envs/credentials/Scripts/python.exe",
  "TRUSTLENS_DEVICE": "cpu"
}
```

The CLIP directory must contain exactly one `open_clip_model.safetensors`. Required digests are in `models/image_pipeline.json`. The launcher sets offline mode; it never fetches weights. Upstream sources and version requirements are listed in `submission/DISCLOSURE.md`. This repository is not a license to redistribute those upstream weights.

For C2PA, create a separate CPU environment and install `requirements-credentials.txt`. Point `TRUSTLENS_CREDENTIALS_PYTHON` to that Python executable. Verification uses the pinned local trust files in `app/trust/`; no remote manifest or revocation lookup is made. Synthetic test roots never enter the production trust store.

## Verify

```sh
python -m pytest -q tests ai_detector
node --test
```

Set `TRUSTLENS_CREDENTIALS_PYTHON` before running tests to include actual signing/tampering tests. Set `TRUSTLENS_TEST_NATIVE_OCR=1` on Windows with English OCR to include real OCR integration. Optional native checks are otherwise explicitly skipped. Node tests use offline controller/service-worker doubles; browser observations are recorded separately. Use the current checkpoint linked at the top and its matching archive receipt for verified results and remaining checks. The [v11 handoff](docs/EVIDENCE-V11-20261023.md) is historical. Earlier dated records and measured failures are preserved. Tests demonstrate implementation behavior, not population accuracy or a real iPhone/native Share-sheet test.

## Design

`app/main.py` validates requests and serves the API. `app/analyzers/` contains narrow rule, MIME, URL, image and credentials paths. `app/guidance.py` adds fixed safe next steps and private-input-free sharing. `static/` is dependency-free HTML/CSS/JavaScript; `frontend.py` embeds it into the served page. The C2PA worker runs in an isolated subprocess. The model runtime is reused and serialized by its existing lock.

The local server does not retain submitted content. Images may use temporary multipart buffers during a request; those files are closed afterward. It binds only to loopback, rejects unrelated Host/Origin values and never fetches a submitted URL. Do not expose this development server publicly without a separate deployment/security review.

## Review and recording materials

- [Broader park-post rehearsal](submission/CAC-BROADER-STORY-DRAFT.md): the latest connected Quote → Numbers → Claim draft; browser-rehearsed, not filmed or timed.
- [CAC preparation packet](submission/CAC-2026.md): existing requirements sources and unresolved identity, contribution and eligibility checks.
- [Disclosure](submission/DISCLOSURE.md) and [evaluation limits](submission/EVALUATION.md): AI assistance, reused components and retained results.
- [Device and usability worksheet](docs/DEVICE-AND-USABILITY-TEST.md): blank observations for deferred physical-phone and consented user checks.

Use the checkpoint linked at the top and its adjacent archive receipt for current software verification. The older four-minute script belongs to historical competition material; it is not the current CAC rehearsal. No recording, public publication, submission, eligibility approval or student contribution is established by this source bundle.

<details>
<summary>Historical submission and development notes — earlier totals and plans</summary>

These notes preserve prior checkpoints. Their words “current”, “latest” and “active” refer to the date of that checkpoint, not the present build. Current status is linked above.

## Submission materials

- `tasks/plan.md`: plan written before implementation.
- `tasks/upgrade.md`: family-first upgrade plan and verification scope.
- `tasks/upgrade-v3.md`: action-first results and deceptive-link upgrade plan.
- `tasks/sprint48-plan.md`: active local-only parallel sprint, submission freeze and model admission criteria.
- `submission/JUDGE-GUIDE.md`: short feature map and evidence for the demo.
- `submission/DEVPOST.md`: honest draft with missing community evidence marked.
- `submission/DEMO.md`: approximately four-minute walkthrough.
- `submission/COMMUNITY.md`: short consent-based usability worksheet.
- `submission/DISCLOSURE.md`: AI assistance, prior components and third-party attribution.
- `submission/EVALUATION.md`: actual model evidence and limits.

The local build is not a submitted or accepted hackathon entry. A public repository, recorded narration, actual community observations and an eligibility determination for reused components remain outside this package. Do not claim the older project was created entirely during the event.

## October 23 development continuation

This is a separate review candidate, not a frozen-entry replacement. See [verified development handoff](docs/CONTINUATION-20261023.md) for current browser checks, 463 Python and 17 controller passes, new constructed diagnostics and remaining upload checks. `scripts/package.py` writes only the separately named development review ZIP.

## Professional upgrade and phone companion

Start with [current professional handoff](docs/PROFESSIONAL-UPGRADE-20261023.md), which supersedes earlier verification totals. The current local build adds an explicit tool-configuration panel, guarded balance-payment wording and improved mobile/error states. [TrustLens Pocket setup](docs/ANDROID-COMPANION.md) explains the separate offline-capable human-guided checklist and Android share-target implementation; Android installation is not yet device-verified. No automatic SMS access is requested.

Verification: 474 Python tests (zero skips) and 31 controller/share tests. Short real public scam excerpts and actual admitted-image C2PA results have explicit limits. The image model's contained native attempt stopped at RAM admission and produced no scores. Source packaging writes a new professional review archive and refuses overwrites.

## Latest reliability follow-up

See [Pocket reliability handoff](docs/POCKET-RELIABILITY-20261023.md): the actual browser share POST/review/selection/Clear flow now works with the local server stopped. Offline readiness verifies the current worker and all cached assets; stale copy status, IPv6 parsing and image/provenance caveats are corrected. Current checks: 478 Python tests, zero skips, plus 42 JavaScript tests. Earlier totals above are historical. Physical Android installation remains unverified.

## Current usefulness release

[Latest handoff](docs/USEFULNESS-20261023.md): on-device exact-host comparison against a website you supply, selectable offline recovery checklists, and explicit incomplete reports/exports when more than eight literal links are present. Current checks: 486 Python tests, zero skips, and 51 JavaScript tests. Earlier verification sections are historical. Physical Android and image-accuracy limits remain unchanged.

## Current development additions

Email accepts an original `.eml` file up to 250,000 bytes as an alternative to pasted text. MIME encodings are preserved; attachments remain unscanned. Link mode optionally compares the exact hostname with a website you already know. A matching host does not establish safety. Print safe checklist prints fixed guidance without the source text, filename or addresses. Leaving the desktop page clears transient private state, including browser Back restoration.

QR decoding is optional: install `requirements-qr.txt` in the Python environment used to launch TrustLens. This build reused installed OpenCV 5.0.0; no dependency was downloaded. QR reading is bounded to one CPU worker, 15 seconds, 20 million input pixels and 16 decoded values/30,000 characters. The user must review the values before a separate check. QR extraction may briefly use an automatically removed local temporary image. It never visits a decoded address.

Pocket adds optional literal English topic hints with individual Apply actions, six offline practice scenarios, and manifest shortcuts for recovery/practice in supporting installed browsers. These are guide features, not automatic SMS protection. See `docs/ANDROID-COMPANION.md` for installation limits and `verification/communication-public-patterns/report.md` for retained misses on public-pattern adaptations.

## iPhone and visual workspace wave

The current main app uses a dark local workspace, a bright checking surface, four primary communication modes and a separate image-tools disclosure. Character counts, validated Ctrl/Cmd+Enter and draft-preserving Cancel make the core flow clearer. Link mode optionally explains normalized hostnames and private-value-free component counts without fetching an address or changing the verdict.

[The iPhone guide](docs/IPHONE-COMPANION.md) covers manual copy/paste, Safari Home Screen setup and a fixed-URL Apple Shortcuts recipe. Pocket adds explicit paste/share controls and mobile navigation; it does not read Messages/SMS automatically. Physical iPhone/native Share/Shortcuts behavior and browser file uploads remain unverified. A phone needs a trusted reachable secure origin; this work does not open the desktop loopback server to the network. See [current feature and verification limits](docs/IPHONE-VISUAL-20261023.md) and [root integration evidence](verification/iphone-visual/integration-receipt.json). Pocket v11 and the iPhone guide reloaded with the local server stopped; this does not verify a physical iPhone or native Share sheet. The frozen image detector remains unaccepted for release. The newly named iphone-v5 review archive is still awaiting root packaging and portable verification.

</details>
