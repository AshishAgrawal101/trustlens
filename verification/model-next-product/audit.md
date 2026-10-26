# Cross-check product audit and bounded proposal

Read-only source audit of the active development copy: app/models.py, app/analyzers/image.py, provenance.py, content_credentials_worker.py, app/capabilities.py, ai_detector/image_ensemble.py, decision_policy.py, models/image_pipeline.json, main image route, guidance.py and current main UI. No model installed/loaded, image analyzed, source edited or accuracy measurement performed. Existing archives unchanged.

## What actually exists

- The installed metadata selects clip_community_v1, CLIP probe plus CommunityForensics, equal-weight combined score and .35 final cutoff. It has historical 670-image clean binary metrics with generator_disjoint false. These metadata numbers do not establish current real-world accuracy or a release acceptance pass.
- A successful ensemble score reports image:clip, image:community and image:model. The combined value is derived from the same two component outputs. Three score rows are not three independent models or corroborating votes. Both components receive the same source image and can share biases; statistical independence/correlation has not been measured here.
- image:disagreement compares branch scores at .5. In the active v1 policy opposite sides force inconclusive, despite the combined classifier cutoff being .35. The .5 comparison is not the final decision threshold. Other supported policies can resolve branch disagreement outside a frozen uncertainty band; an explicit disagreement does not universally imply inconclusive for every supported pipeline.
- model_ran records whether the image detector returned a result. decision_basis distinguishes content_credentials/model/rules, but the credentials-unavailable fallback still uses content_credentials as basis even when neither check succeeded. It must not be treated as successful verification.
- Trusted, asset-bound signed generated declaration short-circuits pattern inference: model_ran false is intentional, not a failed second opinion. Trusted edited/other declarations can coexist with detector output.
- C2PA status separates verified, untrusted, invalid, absent, unavailable and external. Verified authenticates signature/binding/trust under local snapshots, not the truth of the scene. External means deliberately not fetched; absent is a completed absence finding, not a detector verdict. Untrusted/invalid declarations must never become trusted cross-check evidence.
- ContentCredentials carries tool, signed_at, validation_state, trust_list and validation_codes; the present credential card displays only status/detail/signer/declaration. Evidence identifies branches by fixed IDs/sources but no per-report pipeline/version/hash.

## Concrete representation gaps

1. **Unavailable versus failed cannot be reconstructed reliably.** read_credentials returns unavailable for missing environment, process error, timeout, oversized/invalid worker output. ImageModelUnavailable covers missing assets and startup/integrity failures. The fallback model_ran false does not distinguish skipped/not configured/failed. Existing capabilities is explicitly configuration-only and cannot fill this gap for a file result. UI must say no result/unavailable, not guess failed or not installed.
2. **Correlation is not explained in the score area.** Generic evidence lists the combined score alongside two branch scores without a short statement that the combined value is derived, so a superficial count can look like three independent confirmations. Existing general experimental limits are useful but do not resolve this immediate interpretation risk.
3. **Cross-check absence is not agreement.** No image:disagreement marker can mean one branch/legacy path, skipped model, no model output or same .5 sides. It does not prove agreement with provenance. Edited signed history and photograph patterns are compatible; missing credentials and a model prediction are not conflicting votes.
4. **File-specific identity is incomplete.** The active metadata names a frozen pipeline and integrity hashes, but report evidence omits that identity. Any displayed exact candidate identity should be reported by the runtime, not inferred from current disk metadata/configuration which could differ from an already-cached runtime.

## Recommended small presentation, using current result only

Add image-only **Checks behind this result** with compact labelled rows, no count/percent agreement indicator:

| Row | Source of truth | Safe wording |
| --- | --- | --- |
| Signed history | content_credentials.status | Validated signature and binding under local trust snapshot / signer not trusted / validation failed / none embedded / unavailable / external credentials not fetched |
| CLIP pattern classifier | exact image:clip evidence present | Result reported; retain existing non-probability score detail |
| CommunityForensics pattern classifier | exact image:community evidence present | Result reported; retain existing non-probability score detail |
| Combined pattern decision | image:model present | Derived from pattern components, not an independent third check |

Omit branch rows not present, or explicitly say component result not reported without claiming why. If model_ran false and verified/generated, fixed note: detector was skipped because the signed declaration supplied the decision. Otherwise no detector result was returned, without inventing a failure reason. Display explicit image:disagreement as Models disagree; preserve existing policy/summary instead of recomputing the verdict from score text. Never parse numeric evidence strings to synthesize another vote.

Below rows: **These checks answer different questions and are not independent votes. A signed declaration does not verify the scene or transaction; matching model outputs do not prove origin.** Keep the existing experimental/not-accepted disclosure and context verification actions.

This can be built without new inference, network requests, user input export or changed model decisions. Fixed labels/status text only; detailed evidence stays inspectable. If branch IDs/status shapes are missing or malformed, show unknown/not reported, never a positive checkmark.

## Better backend contract only if assigned

For explicit failure/skip distinctions, add per-component structured status (completed/skipped/unavailable/failed), stable runtime identity, optional fixed reason code and dependency relationship. Include combined's inputs, distinguish processing status from origin assertion, and preserve C2PA declaration trust. Avoid copying exception messages, filenames, private image bytes or URLs into the component receipt. Do not add this merely for feature count; current-field matrix can be the first bounded slice.

## Meaningful validation before shipping

Tests should cover credentials-only generated skip; absent/external/untrusted/invalid/unavailable credentials; model failure with partial credentials; two actual branches with explicit disagreement; derived combined score not counted as a third model; legacy single model; edited declaration plus photograph-pattern not labelled contradiction; reset/mode/late response and no raw input in exports. Browser/a11y review must check table/card wrapping and announcement order. Physical-device/user-study/model reliability improvement claims remain unverified.
