# Real-image diagnostics: visual model stopped; C2PA completed

One root-authorized, separately contained CPU integration attempt ran and stopped at a live resource gate before image decoding or inference. There are no native scores, JPEG60 outputs, accuracy estimates or release results. The worker was terminated and reaped; no model retry followed.

A separately authorized C2PA-only check subsequently completed on the same four admitted originals. The exact production content_credentials_worker.main stdin/parser/verifier and pinned trust snapshots returned `absent` for each: no embedded Content Credentials were found. This does not establish whether an image is real or generated. No visual model or fraud score ran.

## Separate native C2PA evidence

c2pa-protocol.json was frozen before its image reads, pinning source files, the credentials Python environment, installed c2pa package/native libraries, trust snapshots, four source hashes and the unchanged resource rules. All four hashes were rechecked, all 24 historical OS locks held, STOP scope preserved, and a separate Job-contained supervisor/worker pair ran with the same 1.75 GiB inclusive abort, 1.25 GiB import admission including reserve, half-available-RAM gate and a 60 second deadline. Both exited successfully and the worker was reaped.

The installed native C2PA worker parsed each original and returned `absent`; there were no reported SDK/transport errors or timeouts. Per-file observed latency was 0–16 ms at the available timer resolution; zero readings are below that clock's effective resolution, not proof of zero work. These times exclude process startup/imports. Inclusive retained peaks were 608,636,928 resident bytes and 593,309,696 private bytes, below the enforced abort threshold.

The production worker main function was executed unchanged with in-process stdin/stdout adaptation inside the externally contained worker. This exercised native parsing and production JSON output; it did not exercise read_credentials' subprocess wrapper. Each completed parse was below its ordinary 15 second timeout; the external 60 second guard bounded the diagnostic. No external URLs, GPU, visual-model imports, fitting or final images were used. The absence result carries no class/accuracy inference.

Receipts: c2pa-attempt/prelaunch.json, containment.json, results.json and supervisor-result.json. The original model-attempt protocol, audit and completion receipts remain unchanged and continue to describe that distinct stopped attempt.

## Frozen inputs and authorization

The original protocol freezes four already admitted, already examined development sources: two genuine COCO photographs and two generated OpenFake images, selected by lexical source ID within each class before viewing or scoring. Source records, expected byte/pixel hashes, local license statements and validation roles are in protocol.json. Its unchanged SHA256 is 9bc51f2adcfe7adc17e4c6b556d7f5d3d8c83b3b73d9414863980b663e87d277.

Root reviewed this freeze and authorized one native plumbing attempt in root-authorization-amendment.json. Labels were contextual only; aggregate accuracy, selection and retry after resource failure were prohibited. The planned eight views were original and JPEG quality 60 per source, without resizing. Authorization was granted, but did not waive resource admission.

For the visual-model attempt, all four original files were read solely to verify their byte SHA256 values against the admitted records. All matched. That attempt accessed image payloads but did not decode, view, transform or score any image; the later separate C2PA check parsed originals only for embedded provenance. Expected pixel hashes were preserved from the manifest, not recomputed. Local admission licenses and official-train/validation roles were checked, runtime source pins rechecked, and all 24 historical OS locks held during the attempt and released afterward without changing their bytes. Final, Arena and user images remained unopened.

The installed metadata remains clip_community_v1: 0.5 CLIP + 0.5 Community, cutoff 0.35, inconclusive when branches disagree across 0.5. Source, metadata and probe hashes are pinned. Large backbone identities remain declared metadata identities, not newly verified weight hashes. No cache reconstruction is represented as native inference.

## Actual resource outcome

A dedicated supervisor reused the existing Windows Job containment code unchanged. It capped child/supervisor private memory and resident working sets at 1408/192 MiB, restricted CPU affinity to four cores, and enforced a 1792 MiB inclusive current/retained-peak abort plus the existing 1280 MiB import admission including a 256 MiB reserve. The deadline was 600 seconds. Windows limits cannot guarantee zero allocation overshoot; retained peaks were also checked.

Scientific imports were attempted. Torch imported far enough to reach the first recorded admission check: private memory 1,037,221,888 bytes plus 268,435,456 reserve was below the 1,342,177,280 import-admission bound at that instant. Model readiness was never established. The supervisor subsequently stopped the attempt with `2 GiB reservation exceeds half available RAM` as system availability changed.

The worker exited after termination with code 125 and was reaped. Retained inclusive peak private memory was 1,594,400,768 bytes; retained inclusive peak resident memory was 1,489,846,272 bytes, both below the 1.75 GiB abort threshold. This is a current measured failure, distinct from the historical import-admission failure retained in audit-receipt.json.

The preserved historical training STOP remained SHA256 c19c82e1d90a42542c305e1cc984e7ce16151e0e0925f1f65f4d1d822b212ada; root scoped it to the paused original run, and its hash was continuously checked. Other STOPs remained abort conditions. No STOP, model or production runtime was edited.

The ordinary local API was inspected without image uploads. At that snapshot port 8765 belonged to PID 48848, bundled primary-runtime Python running serve.py, with roughly 52 MB resident/42 MB private and 57 MB peak resident memory. It did not contain a warmed CLIP + Community runtime; its lazy loader would incur a new native load on a valid image. Health success did not establish source working directory, inherited CPU environment or native admission, so it was not used as an alternative to containment. Measurements are preserved in current-resource-receipt.json.

## Limits and durable evidence

Complete installed-v1 fitting/calibration/exact/near/prompt overlap lineage for these sources remains unresolved. The broader manifest establishes its own roles and protected-input exclusions, not independence from every historical installed-v1 fitting/calibration source or unknown foundation pretraining exposure. This did not bar the authorized plumbing attempt, but bars independence/release claims. License statements are preserved local admissions, not new upstream legal verification.

Existing acceptance failures remain unchanged: the historical 670-image binary result is not current correct-definite/all acceptance; installed legacy cached-feature development reconstructions were approximately 51–52% clean and 48–50% JPEG60 correct-definite/all, with historical Arena worse. No eligible new installed-v1 release receipt or fresh retry is established. This four-source diagnostic cannot support population accuracy.

completion.json pins attempt/prelaunch.json, containment.json, worker-memory.json and supervisor-result.json. The original protocol and metadata-only audit receipts retain their original historical statements and bytes; this report describes the final state after the authorized attempt.

Native Windows OCR on the selected ordinary photographs was considered and skipped: these assets have no admitted message-text ground truth, and OCR output would not validate the requested image-origin path or screenshot-message accuracy. The screenshot analyzer explicitly treats OCR as message intake and states that it does not check image origin. No photo decoding or OCR was added merely to produce unrelated smoke output.

Skipped: inference, image decoding/JPEG transformations, new weight hashing, final/Arena/user inputs, training, GPU/downloads, model edits, automation and OCR.
Risk: visual-model integration remains unverified because its one allowed attempt failed resource admission; visual performance fields remain null. The completed C2PA absence checks establish only the four reported provenance outcomes.

