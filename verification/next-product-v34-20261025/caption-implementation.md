# Caption planning without repeated file inspection

Changed `static/media-context.js` and `static/media-context.html`, added `tests/media_caption_notes.test.cjs`, and made the two explicitly authorized narrow contract updates in `tests/media_context.test.cjs` and `tests/media_controller_extra.test.cjs`. No fixture, backend, schema, package, export, README or task file changed.

Caption input no longer runs the file-inspection invalidator. Completed independent file facts/questions and pending file-only requests remain intact. If there is neither a visible result nor a pending inspection, caption input clears the old status text; this preserves the existing Cancel-acknowledgement edit convention without admitting a canceled response or restarting a request. Existing help now explicitly says editing notes keeps the independent inspection/results. Caption text remains local, unparsed and unverified, absent from request bodies and rendered file facts.

Every real file/control boundary still uses the original generation/abort guard: selection change, Clear, explicit Cancel, native-invalid form events and lifecycle exit/restored Back. Clear still wipes notes, selected preview and result. The pure validator/module prefix is byte-identical (`caption-preservation.json`).

Caller audit found caption-abort expectations in exactly two old tests; those caption branches were removed under root authorization, retaining their complete Cancel and Clear assertions. Their remaining single branches were simplified, not replaced with weaker expectations. Existing Cancel-acknowledgement, native-invalid, schema, timeout, preview and privacy tests remain.

TDD: `caption-contract.json` froze the scope before edits; `caption-red.txt` records the completed/pending preservation failures before implementation. The new four tests cover completed facts and focus, pending signal/controls/file-only FormData, every late-response invalidation boundary after note input, and Cancel/edit acknowledgement behavior. `caption-green.txt`: **39/39 media tests pass, zero failures/skips**. A transient VM cross-realm array assertion was corrected with host `Array.from`; no production workaround was introduced.

Evidence is constructed controller/DOM execution, not an actual browser upload or native-file-processing claim. Browser upload permission remains denied and was not bypassed. No new source-authenticity, image-origin, caption-truth or physical-phone conclusion follows.
