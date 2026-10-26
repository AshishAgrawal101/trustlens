# TrustLens 48-hour improvement sprint

Authorized October 22, 2026: plan and execute, parallel agents allowed; all inputs stay local. “1000x” is an aspiration, not a performance claim. Root coordinates three bounded workers; maximum four concurrent agents, one GPU workload.

## Timing and shipping priority

- Start: 2026-10-23 03:27:50 UTC / October 22, 10:27 p.m. America/Chicago.
- End/report: 2026-10-25 03:27:50 UTC / October 24, 10:27 p.m. Chicago.
- Devpost currently says October 24, 12:00 a.m. CDT, which is the end of October 23. That leaves about 25.5 hours at sprint start, not two full days. Source checked October 22: https://neighborhood-hacks-2026.devpost.com/ . Official rules: https://neighborhoodhacks.org/rules/ .
- Freeze a submission-ready source archive by October 23, 8 p.m. Chicago (2026-10-24 01:00 UTC). After freeze, only critical verified fixes may replace it before the deadline, with new hashes and explicit receipts. Later improvement work is separate from the frozen entry.
- Work runs in scheduled sessions while the computer/app is available; no promise of 48 continuous compute hours. Each session implements or evaluates a concrete task, rather than merely polling. Report measured progress/blockers and the frozen package; stop the schedule at the end.

## Architecture and model decision

Keep FastAPI, typed evidence, vanilla frontend, local OCR and the established frozen image/C2PA path. No accounts or cloud calls. C2PA is cryptographic provenance, not an ML model or a fraud vote. OCR is transcription, not a detector.

Evaluate distinct candidate models across modalities: the existing CLIP and CommunityForensics branches, available PE features, another image backbone only if an admitted local asset exists, and a local language classifier only with licensed relevant data and a defensible evaluation. This is a candidate queue, not a claim that five models are installed. Five prompts to one model, correlated fine-tunes or five uncalibrated scores do not establish independent agreement.

Before adding a model: compare on identical admitted development sources with original/JPEG60 results separate; measure false accusations, missed cases, abstention, latency/memory and conditional error overlap. Keep it only if it adds useful information at feasible cost. No simple majority vote presented as a probability. Fitting/calibration/development roles remain separate; final/Arena/user inputs never enter fitting or selection. Old examined finals cannot be called fresh or retried unchanged. Release acceptance rules remain binding.

## Work streams, dependencies and acceptance

### 1. Challenge set and communication fixes (first 0–6 hours)

Owner: communication_quality. Independently author and hash a constructed challenge set before examining rule implementations. Record baseline gaps, then fix shared parsing/request handling with negative controls. Touch owned analyzer files and a dedicated test module only after root assigns them.

Acceptance: preserve existing cases, reduce documented misses without converting ordinary reminders into warnings, and report every residual failure. Constructed cases are regression/development evidence, not population accuracy. Verification: fixed-case before/after receipts and targeted pytest, then root full suite.

### 2. Product reliability and image availability (first 0–6 hours; parallel)

Owner: product_quality. Fix observed data-erasure and misleading-availability states. Preserve draft/OCR review when the active tab is clicked; clear all private preview metadata; unavailable image services must remain visibly unavailable.

Acceptance: dedicated controller/API regressions, unchanged model/credential workers, no fake success from missing services. Browser policy currently denies localhost; no alternative browser/CDP/shell-render workaround. Static/API/DOM-double checks cannot claim real-browser verification.

### 3. Model complementarity and feasible local additions (0–16 hours)

Owner: image_evaluation. Inventory actual weights/features, license/provenance and current resources first. Prefer a bounded comparison of already admitted fitting/calibration/development caches; freeze its protocol before fitting/scoring. No repeated unchanged audit or old failed-candidate final retry.

Acceptance: a reproducible report with baseline versus candidate, per-view metrics, genuine false positives, coverage and runtime limitations. A null result is retained. GPU tasks require actual free locks/no STOP/resource check and a separately audited launch; cached-feature timing is not encoder-training speed. This task does not block shipping a reliable existing runtime.

### 4. Evidence coverage and stable handoff (6–20 hours; after 1–2)

Owner: root. Integrate only completed, tested changes. Expose which checks actually ran and which could not; never imply unavailable models voted. Keep input-free exports, bounded requests, stale-result rejection and honest uncertainty. Recheck complete API flows, native OCR/C2PA, original runtime identities and source archive manifests.

Acceptance: stable running local app; tests reflect errors as well as successful paths; reproducible launch and known missing model behavior; updated demo/README/disclosure. No public publication or messages without specific authorization.

### 5. Submission freeze (by October 23, 8 p.m. Chicago)

Root creates a timestamped immutable entry archive/checksums and a concise return report with what works, measured evidence, limitations and exact human steps (community evidence, eligibility, video/repository/submission). Preserve earlier archives. The family story and loss amount stay private.

### 6. Remaining time (after entry freeze to 48-hour end)

Continue only a useful bounded local comparison or clearly isolated post-entry fix. Do not alter the frozen entry silently. If no justified next change survives evaluation, finish early with a reproducible report rather than invent work. At the end report outcomes and pause the sprint schedule.

## Resources and safety boundaries

Authoritative prior allowance: 300,000,000,000 bytes charged downloads AND total D: TrustLens storage, at least 20 GiB free, protect existing final reserves. Count existing data/weights/features/checkpoints. No new dataset/weight payload without pinned official source, revision, license, size/digest, allocation and precharged ledger. First wave uses existing assets only. No unrelated deletion, Windows power changes, permission bypass, paid API/rented GPU or external content transmission. User explicitly selected local-only on October 22.

## Coordination and durable state

Only root changes the plan, task checklist, shared sprint state, automation or integration package. Agents write assigned files only and never spawn additional workers. Three initial audit receipts are under `artifacts/sprint48/`; root keeps `state.json` there. The old research/training automation scope must never resume. Useful scheduled work ends at the sprint cutoff, on explicit human pause, or an unavoidable resource/user-action block.
