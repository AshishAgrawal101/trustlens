# Independent cross-check UI review

Read-only review of static/app.js:19,70–79 and tests/frontend_cross_checks.test.cjs against app/analyzers/provenance.py and content_credentials_worker.py. No concrete actionable defect found in reviewed paths. No source edits.

The panel appears only for image results. Component rows require their exact reported evidence IDs; the combined output explicitly is not a third independent model. Missing disagreement evidence never establishes agreement. An explicit image:disagreement produces a component-disagreement statement, without claiming provenance conflict or calculating another verdict. model_ran false says no model result returned, which also covers a deliberately skipped trusted AI-generation declaration without asserting that it was attempted.

Credential labels preserve verified/untrusted/invalid/absent/unavailable/external distinctions. The verified description matches the worker's required signature, hard binding, trust and failure checks, scoped to its local trust snapshot. The panel does not claim a true scene, live revocation, trusted transaction, independent vote, calibrated probability or successful model execution from configuration. Signed generated versus edited declarations do not manufacture model agreement.

Rows and status use fixed strings and textContent, not private evidence text or HTML. Input changes, Clear, modes, pagehide and persisted pageshow clear and hide the panel; generation guards stop late responses reviving it. Copy/print still consume the existing safe summary rather than these display rows. Targeted controller run: 5 tests pass (183.7 ms total process duration). Tests cover all credential states, component subsets, explicit disagreement, private-string omission, reset/lifecycle and late-response behavior. This is source/controller verification, not browser accessibility or real-model execution evidence.

## OCR wrapping decision

Keep the native OCR wrapped-request defect explicitly unresolved this pass. The frozen independent ordinary control proves that global line joining invents a sensitive request across unrelated text. A finite determiner/unfinished-noun continuation grammar would add new ambiguity policy and requires separate frozen acceptance and source-offset design. The repaired soft-hyphen path does not join any lines and must not be described as fixing OCR layout. Practical current mitigation remains the existing mandatory editable OCR review; it does not guarantee a user will repair every wrap or remove the limitation.
