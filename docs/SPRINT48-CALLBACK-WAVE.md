# Callback advice and truthful execution metadata

A new constructed 12-case challenge was frozen before API evaluation. Its first result was 11/12: an explicit instruction to end a call was incorrectly presented as a current code request. The advice recognizer now additionally accepts only the subject “the caller” and refusal “end the call”, with the same bounded span and delimiter guards. Later independent requests remain positive. A rerun of this now-examined set satisfies all 12 contracts; the other 11 reports are unchanged except execution metadata. The original failure and full raw outputs are retained locally.

A separate manual review found rule-only communication reports inherited model metadata. Message, email, call and URL reports now explicitly return decision_basis=rules and model_ran=false. Image-model and credentials paths preserve their existing semantics and protected files.

Root verification: 450 app tests passed, zero skips, including native Windows OCR and actual C2PA signing/tampering. Four endpoint metadata regressions, 24 advice/current-request controls, and live API comparisons cover the change. All eight protected image/C2PA runtime files remain unchanged. Earlier 24-case results are historical examined development evidence; neither set establishes representative accuracy, sender identity, fraud, or safety.

The frontend is unchanged and retains its prior 17 offline controller test passes. Real-browser visual/keyboard checks remain unverified. The optional NLI candidate remains rejected, with development unscored; no new image model or release pass is claimed.
