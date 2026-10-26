# TrustLens v23 — compare reported percentages

Numbers & context now accepts either counts with totals or two reported percentages. You no longer need to invent sample sizes to examine a published percentage claim. Changing method clears the numbers and previous result; a calculation still requires an explicit action.

For 1.2% versus 1.8%, the descriptive difference is 0.6 percentage points and the relative change compared with Group A is 50%. The result explicitly records that underlying counts and totals were not supplied. It cannot infer sample size, significance, cause, data quality or truth. Reported percentages may already be rounded.

The new parser accepts bounded ordinary decimal strings from 0 to 100 and uses exact integer cross-products before display rounding. Scientific notation, percent signs and hidden characters are rejected. Zero baselines produce an undefined relative change, not infinity. The original counts function is byte-for-byte unchanged from v22. Display uses six significant digits; exact arithmetic cannot recover precision missing from a source.

Clear removes values and results while retaining the selected method. Leaving the page or returning through Back clears values and resets the counts method. Inactive required fields are disabled; the method and submit controls remain disabled until their controller is ready. No inputs are sent, stored or exported by this worksheet.

Independent Fraction-based acceptance, preserved RED/GREEN evidence and counts-function hashes are in verification/reported-percentages-20261024/. The source Node suite passed 489 tests before final packaging. Actual Edge checks covered both methods, keyboard submission/selection, zero/range handling, reset and narrow rendering. The extracted static Pocket v23 bundle ran both methods with its HTTP server stopped after successful cache-v19 preparation.

The matching external receipt records final source/extracted suites, manifest and preservation verification. Earlier v22 is an immutable reliability fallback. Physical phones, native sharing, public HTTPS hosting, screen readers and human usability studies remain unverified or deferred. This feature adds no model, source lookup or accuracy claim.
