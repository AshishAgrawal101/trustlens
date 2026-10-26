# Desktop original-image comparison handoff

Implemented in static/index.template.html, static/styles.css, frontend.py, new static/original-preview.js and tests/original_preview.test.cjs. No app.js, Pocket or archives changed.

The existing image #preview now lives inside an explicit Compare with the original image disclosure. Its full aspect ratio replaces the cropped 68px thumbnail. Fit width, 150% and 200% buttons resize image width within a labelled, focusable scroll region; controls move focus to that region for native arrow-key scrolling. Percentage labels mean frame-width percentages, explicitly stated in live feedback. Filename feedback remains visible outside the disclosure. No second image/object URL, new file read, request, storage, export or automatic analysis was introduced.

Normal controller reset handlers continue removing src/revoking the object URL. The helper resets disclosure/size/scroll state on replacement, Clear, mode/demo/example actions, exit and persisted restore. Display failure has local actionable feedback. Existing OCR review checkbox remains required and edits invalidate confirmation.

Root-requested integration: compact neutral-blue What was checked card after result-safety, before credentials; IDs coverage-checked and coverage-unverified. Root owns population/reset. Low verdict tags use neutral blue; guarded/high styles untouched.

Validation: 38 targeted Node tests passed (frontend_state, frontend_intake, primary_flow, original_preview), zero failures/skips. Six new tests load the actual controller and helper together, cover source revocation/reset/late OCR/error handling/review guard/no automatic request and one-image/print constraints. In-memory render_frontend verified helper inlining, single preview and new integration IDs. The first test run found a cross-VM array assertion mismatch; the test now asserts elements/count and the rerun passes.

Limitations: DOM doubles do not validate visual layout, image decoding, native keyboard scrolling, screen-reader announcements or actual browser file selection. Browser file-upload permission remains denied; no bypass was attempted. Parent owns real-browser review/full integration tests. This is a source-and-regression-backed improvement, not user-study evidence.

## Coverage-card follow-up

Root delegated app.js and new tests/frontend_scope.test.cjs. Added fixed source-specific coverage for Message, Link, Email, Call, reviewed Screenshot, reviewed QR and Image reports. Image report kind takes precedence and makes no claim that any individual component ran. Incomplete-links evidence adds a fixed explicit warning. clearResult clears both coverage nodes, so normal edits, resets, cancellation and stale-response guards also cover this UI. Report data, original content, contact details and evidence are never interpolated into these strings; existing safe summary/print semantics are unchanged.

Independent source review found no new blocking UI regression in this change. Source-specific limitations remain prominent; image components point to actual evidence rather than implying success. Six new controller regressions cover every source, first-stage extraction, image precedence, input-free exports, incomplete links, resets/malformed retry and dismissed pending results. Targeted combined run: 34 tests passed, zero failures/skips (frontend_scope, frontend_state, frontend_response, original_preview). Full-suite and real-browser review belong to root.

At root request, How it works now explicitly labels the 36-case diagnostic frozen v7 historical, preserved before current parser fixes, and says it does not measure current rules. The frozen communication-evaluation.html contents were not edited.
