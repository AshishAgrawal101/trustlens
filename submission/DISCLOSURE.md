# Build provenance and assistance disclosure

This folder was planned and implemented on October 21–22, 2026 (America/Chicago). OpenAI Codex assisted with planning, code, tests, interface design, technical research and submission drafts. The owner directs the project and must review final claims and eligibility.

## Earlier work reused

The app began from the existing `trustlens-current` package. Earlier code/model artifacts exist before October 16. Reused components include the FastAPI/Pydantic structure, image validation/inference, frozen classifier/metadata, C2PA worker/trust snapshots, decision policy, frontend embedding helper, launcher socket/readiness logic and native signature tests. `docs/baseline-manifest.json` records initial-copy hashes. The final bundle manifest records shipped files.

New or substantially revised in this build: explicit risky-request rules and benign handling; combined message/link evidence; email-body analysis and untrusted header labeling; call-transcript API and UI; local screenshot OCR with review before analysis; request-specific safe actions and private-input-free summaries; four recovery checklists; redesigned responsive interface; practice mode; partial image-service results; local host/origin protections; new software tests and submission materials.

Do not describe the entire project or models as newly created during the hackathon. The user stated development during October 16; the saved older components nevertheless require accurate disclosure. The [official rules](https://neighborhoodhacks.org/rules/) permit disclosed libraries and AI assistance but prohibit submitting a pre-existing project. Organizers decide whether this extension is eligible. No organizer approval has been obtained by this build.

## Third-party components

- [FastAPI](https://github.com/fastapi/fastapi), Pydantic, Starlette and Uvicorn: local API and validation.
- [OpenCLIP](https://github.com/mlfoundations/open_clip) and OpenAI CLIP ViT-L/14: frozen visual features. Existing local weights are not included in the source ZIP.
- [Community Forensics](https://github.com/owensgroup/Community-Forensics): published detector; existing local checkpoint `OwensLab/commfor-model-384`, revision `6076002bf0d9dd37537f965ee2f06f826c333b61`. The checkpoint is not included in the ZIP.
- PyTorch, torchvision, timm, safetensors, scikit-learn, NumPy, SciPy, joblib and Pillow: local inference and image handling. Model metadata pins relevant digests.
- [C2PA Python bindings](https://github.com/contentauth/c2pa-python), version 0.38.0: optional native verification. Local trust material retains source URLs and hashes in `app/trust/snapshot.json` (fetched October 9). No live revocation lookup.
- pytest and HTTPX: tests. Native signature fixtures use a separate ephemeral test root, never the app's trust store.
- [Windows OCR](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine?view=winrt-26100): installed Windows platform component, accessed through Windows PowerShell 5.1. The bundle does not redistribute the engine or language assets. The demo screenshot is a locally generated constructed message, not a victim's screenshot.
- [FTC consumer guidance](https://consumer.ftc.gov/scams): general independent-verification and reporting guidance, paraphrased. FTC does not endorse the app.

No external image assets, stock illustrations, remote fonts, paid analysis APIs or remote LLM calls are used by the product. Practice scenarios are original constructed examples. This attribution does not replace upstream license terms. Review licenses before redistributing any additional model or dataset.

The family-safety focus was selected from user-provided context. Personal family details, names and loss amounts are excluded from the app, examples and submission drafts. Any later use of a relative's experience needs that person's consent.

No public deployment, repository publication, outreach message or Devpost submission was performed automatically. No new model accuracy result or research-novelty claim was created by this build.

The October 22 revision adds literal HTML link-label comparison, stricter shared URL validation, action-first grouped results, three constructed practice-check buttons and erasure of private result nodes on Clear. These are engineering changes to established techniques, not new detector research.

The separate October 23 professional development version adds guarded balance-settlement wording, component configuration reporting, mobile/error/focus improvements, and Pocket's static offline checklist/share-target receiver. Pocket is separate from the desktop detector and requires user-selected topics; it is not an installed native Android app or automatic SMS classifier. Three additional Codex subagents assisted with communication, frontend and image evaluation/review. Public scam fixtures contain only short attributed educational excerpts; image diagnostics reused already admitted development assets, not private user images or newly acquired data. Icons are locally drawn geometric lens symbols. No additional model or cloud analysis service was installed.

The subsequent local intake revision adds optional [OpenCV Python](https://github.com/opencv/opencv-python), installed opencv-python-headless 5.0.0.93 (distribution metadata: Apache 2.0), for QR decoding only. Existing installed binaries were reused; the optional requirements file pins that distribution. No QR destination is visited. Python's standard-library BytesParser supports original `.eml` uploads. The fixed Pocket guide is reused for user-selected desktop next steps. Native QR fixtures are locally encoded safe examples, and robustness controls reuse two admitted COCO photos; these do not establish scam or image-origin accuracy. FTC-pattern diagnostic cases are newly written adaptations with source URLs, not victim messages.


## October 23 iPhone and visual workspace continuation

This separate development wave adds the main deep-ink/bright-workstation redesign, locally drawn CSS lens artwork, character counts, native-validation keyboard submission and draft-preserving client dismissal. Existing result meanings, explicit screenshot/QR review and input-free exports are retained. The new URL anatomy panel returns normalized host/component counts while omitting credential/path/query/fragment values and visiting no destination. Host parsing now directly uses the pinned `idna` package (nontransitional UTS #46; upstream [python-idna](https://github.com/kjd/idna)); it does not establish site ownership or implement all browser URL behavior.

Pocket adds a coordinated dark mobile layout, fixed navigation, explicit permission-based paste, and native sharing controls for fixed input-free guidance. Apple-source-linked iPhone onboarding explains manual copy/paste, Live Text and Home Screen setup. The optional Apple Shortcuts recipe is fixed text for manual construction, not an installed or signed Shortcut/native Share Extension. Messages input is never put into a generated URL. Apple/WebKit references and their limits are documented in `docs/IPHONE-COMPANION.md`; linked help pages need internet. System clipboard, Photos and OS sync remain outside Pocket's clearing controls.

No automatic SMS/Messages access, notification monitoring, clipboard polling or background protection was added. Physical iPhone installation, Shortcuts execution, native Share-sheet delivery and physical Android sharing remain unverified. Browser file upload remains denied by the extension; no alternate access was used. The desktop stays loopback-only, with no deployed secure origin supplied for a phone. No external visual assets, remote fonts or cloud content service were introduced. No model fitting, accepted replacement, new accuracy result or trust-material change belongs to this wave; the frozen visual detector remains below release requirements.

Root's final suites passed: 690 Python and 111 JavaScript checks, zero failures/skips. Pocket v11 and the iPhone guide reloaded with the local server stopped; checklist/Clear/practice and repeated navigation were verified in the desktop browser. Six prior archives, 104 original source files and 34 protected runtime/model/C2PA/trust files remain unchanged. Receipts are in `verification/iphone-visual/`. The new `TrustLens-professional-20261023-iphone-v5-review.zip` archive and portable verification are still pending root's external package receipt. See `docs/IPHONE-VISUAL-20261023.md`. Earlier dated assistance/provenance statements and archives remain preserved.


## Further reliability wave

The development copy adds explicit Message/Call wording transfer, HTML inline/block reconstruction, duplicate-Subject manual-review reporting, readable malformed-PNG rejection, response validation and keyboard practice feedback focus.728 Python+121 JavaScript checks passed, zero skips. These are software regressions, not real-world accuracy. See docs/RELIABILITY-NEXT-20261023.md and the external reliability-v6 package receipt. Prior frozen diagnostics and entries remain unchanged; physical devices/browser uploads/native delivery remain unverified. The only protected source exception is shared input-decoder error normalization; no model runtime, weights or thresholds changed.


## October24 source-context and reliability continuation

Codex and three reused subagents implemented/reviewed an exact quotation finder inside the existing Quote & context page, factual finite invisible-character presence notices, contextual navigation, and constructed email/URL parser regressions. The finder uses standard JavaScript literal matching; it does not use an LLM, search the internet, authenticate a source or decide meaning/truth. Invisible controls retain legitimate language/emoji uses and are not an intent label. New email and URL handling rejects or marks incomplete ambiguous input instead of asserting a clean interpretation. No dependency, model, training set, cloud content service or public upload was added. Current software-check counts, actual browser evidence, parser audit outcomes and portable verification belong to the matching v16 handoff/receipt; earlier dated counts remain historical. Human community evidence, student authorship, challenge eligibility, physical phones and browser image-upload validation remain outstanding.


## October24 offline context continuation

Codex and the three reused review roles added one script-free Pocket context guide, four authored context Practice questions (preserving six earlier cases), answer/lifecycle guards, explicit cache-version readiness, and bounded URL-reference validation. Existing phone CSS/native details and JavaScript URL parsing are reused; no new library, model, dataset or external asset was added. Desktop/Pocket malformed-scheme guards preserve bare decimal host ports and explicit uncertainty. The final shellv13 and context/practice were exercised from desktop browser cache while only the development server was stopped, then restored. This is not physical-phone or human-learning evidence. One native QA click invoked Share in error; the app reported failure, its payload was only fixed input-free guidance, and no delivery was verified. Full scope, null results, software checks and portable receipt are recorded in the v17 handoff. No public submission, deployment or private-content upload was performed.


## v18 offline Pocket review checkpoint

Pocket includes three existing browser-local workspaces: claim context, counts/denominators, and literal quote comparison with exact passage finding. One shared renderer serves desktop-backed Pocket routes and generates the static companion export; the exact fixed assets are cached only after complete preparation. Local Edge tests of the extracted export ran all three while its loopback server was stopped. These tools organize supplied information; they do not authenticate sources, determine truth, establish source independence, significance or cause. Source suites pass 1,138 Python and 422 JavaScript tests. Physical iPhone/Android integration, human outcomes, public deployment and submission remain unperformed; no new model or accuracy claim.
