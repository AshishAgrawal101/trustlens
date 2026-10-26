# Professional product handoff

Implemented 2026-10-23. Exclusive frontend scope; no backend, model, recovery guidance, phone companion source, or build outputs changed.

## Design contract

Keep the existing paper/green visual system and local checker. The primary job is choosing the right intake and understanding a safe next step. Preserve the existing two-column desktop / single-column mobile layout, all element IDs, privacy/export behavior, and explicit screenshot review. New states must remain readable without color or animation. No external visual reference was supplied; existing components and tokens are the reference.

## Changes

- Prominent normal `/phone/` link identifies the separate text-only companion and its limited offline checks.
- Intake guidance distinguishes wording/address/email/call checking, two-step screenshot OCR, and image origin versus transaction safety.
- Expandable local tool panel fetches `/api/capabilities` only after Check availability. The panel starts with unknown availability; component configuration is explicitly not runtime verification. Refresh failures replace stale claims with unknown. No input accompanies this request.
- Invalid upload and failed check focus the existing error alert; form busy state starts and ends with requests and resets on Clear/mode change. Existing cancellation and stale-response guards remain in place.
- Mobile spacing, link/button targets, wrapping, result heading, long evidence, dialog scrolling and capability text reuse current design tokens. Existing reduced-motion support remains.

## Integration contract

GET `/api/capabilities` returns `message_rules` boolean and `screenshot_ocr`, `image_detector`, `content_credentials` objects with `configured` boolean and optional `detail` string. These are configuration observations, never successful-runtime claims. The coordinator owns this endpoint and `/phone/`. Main backend remains loopback only.

## Verification

`node --test tests/frontend_state.test.cjs tests/frontend_professional.test.cjs`: 22/22 passed. Five new regressions verify on-demand no-content capability requests, failed/malformed capability recovery, contextual intake guidance, error focus/busy lifecycle, and honest companion link wording. Seventeen existing regressions cover screenshot review, clear/cancellation, previews, sharing, recovery and result grouping.

The new tests reuse the existing offline DOM double without changing its file. They do not establish browser rendering, mobile layout, screen-reader behavior or a working physical Android installation. Coordinator must run ordinary permitted browser checks; this worker deliberately avoided browser use to prevent conflicting sessions. File upload remains explicitly denied by the extension; no bypass attempted.

## Limits

Availability is intentionally user-triggered and configuration-only. Optional image runtime may fail after configuration succeeds. No new image accuracy claims, persistence, external calls, browser permissions, dependencies, model changes or automatic input analysis.
