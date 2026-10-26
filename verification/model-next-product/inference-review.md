# Independent inference-failure / wording-map review

Read-only review of app/analyzers/image.py, provenance.py, text.py and corresponding new regressions. No source edits, model loading or actual image-model execution.

## Resolved P2: three runtime exception types bypassed partial provenance fallback

The new analyze_image wrapper catches RuntimeError, MemoryError, ValueError, TypeError, KeyError and ArithmeticError. IndexError, AttributeError and OSError still escape. Reproduced each with a valid constructed 2x2 PNG, stub runtime.score raising that exception, and read_credentials returning verified/edited. analyze_image_with_credentials raises the original exception instead of returning the valid C2PA result with model_ran false. The endpoint only catches InvalidImage/ImageModelUnavailable, so these paths become server errors rather than partial reports.

Invalid-output indexing and incompatible output/interface access can raise IndexError/AttributeError; runtime asset/I/O operations can raise OSError. Suggested bounded correction: normalize those exception types to the same fixed ImageModelUnavailable message, with regression ensuring preserved provenance and no private exception string. Avoid catching BaseException/control-flow termination. Root notified; this review does not edit the owned implementation.

## Confirmed behavior and limitations

- New score guards reject nonfinite/out-of-range/bool scalar output, invalid cutoffs, malformed/missing component dictionaries and policy bounds. Successful existing scoring and thresholds are unchanged. The original tests exercise representative invalid branches without real inference.
- Provenance predecode still keeps invalid upload separate. Trusted generated declarations intentionally skip model execution; verified edited history survives already-covered inference failures. Missing environment, startup/integrity failure and inference failure remain collapsed to unavailable/no result, not separately identified.
- Soft-hyphen wording view drops only an individual intra-letter U+00AD, with monotonically retained source indices. Evidence excerpts map normalized offsets back to original exact slices, including soft hyphens. Literal URL extraction/parsing still uses original input. No concrete source mapping defect found.
- Deliberately limited normalization does not remove consecutive soft hyphens, digits/newlines around soft hyphens, zero-width characters or general obfuscation. This is bounded rule coverage, not an accuracy or generalized model robustness claim.

Validation: tests/test_image_inference_failure.py plus tests/test_soft_hyphen_wording.py: 47 passed. Independent three-exception reproducer confirms fallback gap. Full suite/browser/model inference not run by reviewer.


## Independent closure verification

Root replaced KeyError with its LookupError superclass (covering KeyError and IndexError), and added AttributeError/OSError to the normalized exception set. InvalidImage/ImageModelUnavailable are still re-raised first, preserving invalid-upload behavior. Reviewed current source and independently reran all 21 inference-failure tests: all passed. Repeated the original valid-PNG plus verified/edited provenance reproducer for IndexError, AttributeError and OSError: all now retain verified credentials, model_ran false, risk_index null, no pattern evidence and no private exception text. This finding is closed; no application edits by reviewer.

These are injected Python runtime exceptions and synthetic image bytes, not actual native-model runs. Catching Python MemoryError or a RuntimeError can produce a fallback only if control returns to Python. It does not impose RAM/VRAM limits, terminate inference on client cancellation, prevent native crashes/OS process kills or prove recovery from real resource exhaustion. No process isolation, hard memory containment or successful device inference is claimed.
