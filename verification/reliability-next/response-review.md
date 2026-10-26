# Independent frontend response review

No actionable regression or failure-state leak found in the reviewed validReport, response JSON parsing, or extraction-notice changes.

Reviewed at 2026-10-23T21:03:52.3268829Z. Source pins: static/app.js SHA256 f9acdb3bdd13650ec7ca6d61c920dfe8a8fc650f93d0f8c99b16a37dc248558a; tests/frontend_response.test.cjs SHA256 904c98cb28312bb804a9e2b824dffc31db71182ada690b0b36cfc02ce5b0d2b4. Review was read-only apart from this note; no app, model or runtime files changed.

The renderer checks the report fields it actually consumes before setting currentReport, exposing result nodes or enabling exports. Each submission first clears the prior report and print summary. Malformed reports therefore leave input available for retry without a partial currentReport or stale export. Optional/null model_ran and Content Credentials fields match the actual Pydantic model shapes. All six supported credential statuses are accepted; optional signer/declaration strings are handled safely through textContent.

A separate read-only check passed 23 actual analyzer/Pydantic report shapes through the exact current validReport function: ordinary and concerning message reports, call, URL and email reports, plus all six Content Credentials statuses across true/false/null model_ran. None was rejected. No native image model or credential verifier was invoked.

The JSON parse catch replaces unreadable success/error bodies with fixed feedback instead of exposing SyntaxError or body text. Timed-out requests still use the timeout message; Clear/mode changes invalidate old generations, so a late parse failure cannot replace current state. Extraction validation runs before populating editable text or changing review readiness. Actual screenshot and QR APIs return string notices. QR requires review_required=true; screenshot always imposes the same explicit review checkbox in the controller even if that response flag is omitted. This preserves existing screenshot fixture compatibility without removing review.

Focused controller tests passed: node --test tests/frontend_response.test.cjs tests/frontend_state.test.cjs tests/frontend_professional.test.cjs — 29 passed, zero failed/skipped. They cover malformed report values, unreadable success/error JSON and retry, malformed notices, stale responses after Clear, explicit reviewed-text submission, busy/timeout recovery and clearing exports/private result nodes.

The guard is a renderer compatibility check, not a complete independent copy of every Pydantic constraint or an authenticity check for a compromised server. Fields not read by this renderer, such as confidence and risk_index, are not made stricter unnecessarily. Existing local API error-detail strings still display as text; no newly introduced HTML rendering or private-input logging was found.

Skipped: browser rendering/accessibility checks and native image inference. No further source change is recommended for this slice.
