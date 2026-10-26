# Consistent literal URL boundaries v36

The main Link check and address-anatomy action now pass the supplied URL and reference unchanged to the shared parser. URL request fields no longer strip outer control characters first. The parser still accepts ordinary surrounding spaces and nonbreaking spaces, while its existing control/formatting-character rejection applies consistently. The 4,096-character limit is checked against the original field value.

An empty or ASCII-space-only optional reference is omitted by the main checker. Other reference content is passed through for validation, including a control-only value. Message, email, call and organization-name trimming remain unchanged. There is no new URL rule, destination visit, redirect handling or reputation lookup.

This corrects a low-severity interpretation inconsistency. The audit did not demonstrate a different destination hostname, credential leak or safety bypass. Before the change, the same BOM-prefixed field could be trimmed by Check but rejected by address anatomy; request validation also stripped outer TAB/newline before either API could inspect them.

## Verification

Source: **1,587 Python and 596 JavaScript tests passed, with zero failures or skips**, including the configured native OCR and local signing environment. Dedicated tests cover both endpoints, both controller payloads, original length limits, ordinary whitespace, rejected controls, optional references and unchanged other-mode behavior. No previous test assertion needed changing. Independent review found no required fix.

Actual browser at 320 pixels: an ordinary URL/reference returned an exact-host comparison; a leading BOM produced a fixed error with unchanged input and no old result; a TAB-only reference was validated rather than silently omitted; an ASCII-space-only reference was omitted without inventing a comparison. Input/error focus and Clear/reload were checked. Client and scroll widths were both 305 pixels. No destination was visited.

Evidence: `verification/url-boundary-v36-20261025/`, `verification/v36-independent-url-20261025/` and `verification/v36-root-browser-20261025/`. Preservation checks verified 54 earlier source/phone artifacts, 104 original files and 34 protected files relative to v33 unchanged. The matching external archive receipt records the fresh extracted test run and exact hashes when completed. Pocket v35/cache v30 is unchanged by this desktop-only slice.

Physical phone work and browser file uploads remain unperformed. Model-release and real-world accuracy limitations remain unchanged. No recording, publication, competition submission or continuous-work duration is claimed.
