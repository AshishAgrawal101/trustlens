# Independent media controller review

Read-only app review of static/media-context.js and existing media-context/markup tests. Added tests/media_controller_extra.test.cjs only; no application/backend edits or browser-upload attempts.

No concrete privacy, lifecycle, stale-response or schema-rendering defect found. The controller creates one image object URL on valid selection and revokes/removes it on replacement/Clear/exit/Back. Selection alone does not fetch. Explicit inspect multipart contains only file; caption is never sent, parsed or exported. Caption edits invalidate pending output. Cancel dismisses client request and preserves draft; no claim is made that it kills the backend worker.

Response shape is exact-key validated before DOM mutation. Dimensions/orientation/bytes/clock/optional text/GPS boolean are bounded. Metadata labels are intentionally presented as unverified and rendered via textContent, so HTML-like labels remain literal text. Unknown keys (including private coordinates) or malformed/missing fields cannot become partial visible results. Notice is validated but not echoed. Fixed schema/error text excludes decoder/backend body details. No exports or persistence were introduced.

P3 feedback issue: all HTTP errors other than 413 are described as choosing a readable image within limits, including 500/503 server unavailability. This can send the user back to replacing an otherwise valid image. Recommend fixed unavailable/launcher/retry feedback for server errors while continuing to omit arbitrary server details. Parent notified; no fix made by reviewer.

Added three actual-controller regressions through the existing harness prefix: timeout aborts the request signal/restores controls while preserving draft; Clear/caption invalidation aborts and suppresses a late rejection including focus; missing schema/HTML-like metadata cannot produce partial output or execute markup, and request/URL count remains bounded. Combined media-context + extra + markup run: 13 passed, zero failures/skips.

Limitations: these minimal DOM tests do not certify native file selection, image decode/display, keyboard-scroll behavior, saved browser history guarantees, screen-reader announcements or worker/resource isolation. Browser file-upload permission remains denied; no bypass attempted. No real private image was uploaded by reviewer. Root owns native browser/backend integration checks.
