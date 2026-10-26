# Cross-check reliability — v9

This pass improves input parsing, model failure behavior and the visibility of actual corroborating evidence. It does not train, add or promote model weights, improve measured origin accuracy, or establish model independence.

## What changed

- Image results show reported CLIP and CommunityForensics branches, their derived combination and separate signed-history status. A combined output is not counted as a third model. No disagreement marker does not establish agreement; no output is not a negative vote. Credential absence, unavailable verification, invalid credentials, untrusted signature, verified signature and unfetched external credentials remain distinct. Components appear only when their exact evidence IDs are present.
- Model inference/output failures become unavailable results while preserving any independent C2PA result. Missing, boolean, nonfinite and out-of-range scores or invalid thresholds cannot produce origin conclusions. Invalid uploads remain input errors. Expected runtime, memory, numeric, indexing, interface and I/O exceptions are bounded by a fixed error message; original input/private error details do not enter the response. This catches Python failures; it does not contain native crashes, enforce RAM limits or terminate cancelled native work.
- Intra-letter U+00AD soft hyphens are ignored for wording matching, including negation/history context, with a source-position map restoring exact original evidence excerpts. Literal URLs, editable input and line boundaries are untouched. The 15-row paired acceptance contract was frozen before repair. OCR wrapping, repeated soft hyphens and other invisible characters remain unsupported.

## Additional-model investigation

The existing NLI experiment remains rejected: best coverage was 1/14 versus the fixed 8/14 requirement; its development split remains unscored. It was not retuned or installed.

B-Free is an available different image-model candidate, but remains unadmitted for execution. Streamed local ZIP MD5 matches the authors' published checksum; checkpoint SHA256 matches historical records. Official nonprofit/informational license terms were read from the [upstream license](https://github.com/grip-unina/B-Free/blob/main/LICENSE.txt). No weights or code were downloaded, extracted or executed. Current recorded RAM failed the unchanged gate; CPU parity/containment, acquisition source revision and fitting/evaluation role/overlap proof remain open. Its historical examined results are not fresh validation. Source pins, exact checksums and conditional next protocol are under verification/model-next-image/. No final/Arena/user images were opened or rerun, no STOP was removed, and no GPU job ran.

Other small NLI cards were inspected as research only; none was downloaded or admitted. Extra model count without task-specific evidence would not justify a product claim.

## Validation and preservation

830 Python + 150 JavaScript tests passed, zero skips, with native OCR and C2PA test environments enabled. Focused failure injection is distinct from actual native image-model success. Browser checks confirmed both hidden-character advice staying unflagged and the hidden-character direct request warning with the source excerpt preserved. The image cross-check UI has controller tests; real browser image-result rendering remains unverified because file access was denied. No permission bypass occurred.

Independent review found three missing exception classes; root reproduced the failures, fixed them and the reviewer independently closed the finding. Reviews and outputs are in verification/model-next-{communication,product,integration}/. Historical diagnostic files and their misses remain unchanged; old v7/v8/CAC results are not current accuracy.

Ten earlier source archives, the phone-test artifact and 104 original source entries remain unchanged. Of 34 protected v8 files, 33 match exactly; app/analyzers/image.py is the sole reviewed exception for output validation/error fallback. Model/runtime policy/trust files and Pocket files are unchanged. The external v9 receipt records the extracted-package checks with existing dependencies, not a clean install.

Phone setup, publishing, actual device/human studies and CAC student-authorship eligibility remain open. The image model remains unaccepted. AI assistance must be disclosed, and significant student technical contribution and understanding must be established by real human work.
