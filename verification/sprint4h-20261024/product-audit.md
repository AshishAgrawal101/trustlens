# Product workflow audit after v21

Read-only source/controller review, 24 October 2026. No app changes or archive changes. Inspected home/intake/results, directory routing, Claim/Media/Numbers/Quote and source finder, Pocket context/onboarding and lifecycle paths. Ranked by concrete user impact; these are bounded improvements, not a recommendation for more tools. No browser, upload, phone, screen-reader or human-study evidence was collected in this pass.

## 1. P2 — Revoking screenshot/QR review leaves a current exportable result (and does not invalidate a pending check)

**Flow:** extract → check review confirmation → analyze → uncheck “I reviewed the text and corrected any errors.” The current UI still presents the previous result and permits Copy/Download/Print, although its scope describes text as reviewed. The analogous pending response can still arrive after confirmation is withdrawn.

**Evidence:** `static/app.js:28` makes `reviewed` required, line 132 checks it only at submission, and line 44 invalidates on text edits. There is no `reviewed` change listener. The existing frontend harness independently reproduced extraction and analysis followed by unchecking and firing `change`: result remained visible; print-summary remained “Input-free summary”; Copy wrote that summary. `reviewed` had no registered change handlers. This is a review-state inconsistency, not a claim that the analyzed wording changed or an input leak.

**Bounded fix:** attach confirmation-change invalidation using existing `clearResult()` so generation/abort/export/print guards apply; keep extracted text, original image, source mode and review controls. Rechecking must not automatically analyze. Do not alter classification.

**Acceptance:** tests for Screenshot and QR after visible result and while pending; uncheck hides result, clears print/export/manual/verification state, invalidates late response, and retains recognized text/one preview URL. Recheck alone sends no request. Existing edited-text/review-required and lifecycle regressions remain green. Browser keyboard Space on the checkbox must produce the same state as pointer activation.

## 2. P2 — Two remaining result journeys retain the tall-section navigation pattern fixed in v21

**Flow/evidence:** `static/media-context.html:12–13` still places the full metadata limits card before `#media-result`; `static/media-context.js:75` focuses the whole result section. `static/source-context.js` success handler likewise focuses the entire `#source-result`; up to five context windows can make this much taller than a viewport. `tests/source_controller.test.cjs:12` currently explicitly expects section focus. In contrast, the three v21 primary workspaces focus their bounded h3 and explicitly scroll it to the top. Prior root browser evidence proved tall-section focus can leave a result heading above the viewport; this pass establishes the remaining code paths, not an independently reproduced browser position for them.

**Bounded fix:** finish the existing result-first pattern for Media (complete result before expanded limits plus one short fixed metadata caveat), and focus/scroll the existing result headings for Media and Source finder. Preserve source windows, labels, full limits, region scrolling and print omissions. No file upload is needed to test constructed controller data.

**Acceptance:** result initially hidden; full Media limits still expanded after result; caveat adjacent to heading; successful constructed report/find focuses heading and calls start alignment. Long/five-window finder and constructed long Media output at 320/390 show heading and caveat with no horizontal overflow. Clear/edit/error/page-exit/Back/preview revocation remain unchanged. Browser file upload remains unverified unless separately authorized.

## 3. P3 — Explicit cancellation provides no confirmation or explanation of what was retained

**Flow/evidence:** main `static/app.js:39` Cancel calls `clearResult()` then focuses the input. That hides loading and returns the generic empty-result state, clears feedback and leaves the draft/file. Media `static/media-context.js:56` similarly calls `invalidate()` and focuses the file control; invalidate empties `media-status`. Neither path tells the user whether cancellation was acknowledged, whether the selected image/text was kept, or that a fresh explicit check is needed. The safe implementation already aborts the client request and uses generations; the gap is feedback, not worker termination or a stale-response bug.

**Bounded fix:** a fixed, short cancellation status in an existing/new dedicated live region: “Stopped waiting for this check. Your input was kept. Check again when ready.” Avoid claiming the server/native worker stopped. Clear it on a new check, edits, mode change, Clear and lifecycle exit. Do not put source text/filename in the message.

**Acceptance:** cancel during pending main and Media request announces fixed feedback, retains drafts/file/one preview, restores submit and focus, and late completion cannot replace the cancellation state or result. Retry works; Clear/Back erases status. No error alert is needed for a voluntary cancel.

## Navigation and scope observations

The directory already exposes all seven main modes through an exact startup-only whitelisted fragment and provides direct context-workspace links. Input is not transferred in fragments. Claim/Numbers/Quote retain unnamed fields, initially disabled submission, fixed caveats and lifecycle erasure. Pocket context offers the existing three offline worksheets through fixed aliases, and onboarding explicitly states reachable HTTPS/setup and physical-phone limits. I found no concrete higher-priority navigation/privacy defect in those inspected paths. Do not broaden scope to hosting, native setup, source fetching, model promotion or stored drafts to address the three issues above.
