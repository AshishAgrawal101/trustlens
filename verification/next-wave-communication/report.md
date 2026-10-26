# HTML boundaries and ambiguous subject correction

Initial read-only audit independently reproduced two parsing/context bugs with11new constructed cases frozen before prediction. The scope is separate from earlier FTC-pattern and Pocket diagnostics. Frozen SHA256:23c8adb964fbf2d8d3f06c27285d1228b1072f346903f2d4abab8fc48c3e980e. Original results.json preserves pre-change predictions and source pins. Root then explicitly authorized the two candidate fixes. No earlier frozen labels, diagnostic results, runtime detector, model, threshold or private content were edited/read.

## Demonstrated defects

VisibleText gathered inline HTML text nodes, but analyze_message joined every node with a synthetic space. Rendering-equivalent verifi<strong>cation</strong> and Se<span>nd</span> broke sensitive request words and missed their warnings. More seriously, Do <span>n</span>ot and Ne<span>ver</span> broke negation and turned safety advice into high request concerns. Plain visible-text counterparts correctly retained the positive/negative distinction. Both pasted email and EML byte intake reproduced every mismatch.

Duplicate Subject headers were silently reduced to the first field. Reminder followed by a sensitive request Subject returned low/no incomplete marker; the reverse order warned but still claimed no parse limitation. Subject display is ambiguous when a supplied message violates single-subject structure, so choosing an apparently clean first field is not a complete interpretation.

## Authorized minimal fix

Only app/analyzers/email.py changed. Inline data nodes now concatenate without invented spaces. A finite semantic block-tag set and br insert newline boundaries; no CSS rendering engine or webpage fetch was added. Block end boundaries also separate subsequent text. The script/style hidden-content counter and anchor label/destination collection remain unchanged. Destination strings are appended on separate lines so links cannot merge with visible words or each other.

All Subject fields are joined as separate text lines for inspection. Multiple Subjects add the existing email:incomplete mechanism with a specific ambiguity explanation; no single displayed subject is authenticated or selected as the winner. Existing guidance/UI then request review of the original email. Standard text/API/EML intake bounds remain unchanged, including the250kEML byte boundary. No new route, schema, export field or dependency was required.

Caller audit before editing: VisibleText only feeds analyze_message (no outside runtime consumer). Both Parser and BytesParser entrypoints converge there; main pasted-email endpoint and intake.py EML-file endpoint call those entrypoints. Existing link-label/mailto comparison, IDNA, attachment coverage, MIME-defect, intake, example and privacy/export tests were read/run. Private input-free guidance remains generated from fixed actions; both ambiguous subjects are omitted from exports.

## Verification

New tests/test_email_text_boundaries.py:31tests, including frozen11pairs in both paste/byte modes, inline versus br/block boundaries, live request after separate negated block, hidden script/style, intact split-inline anchor comparisons and duplicate-subject private-summary omission. RED:14failed,17passed before fix. GREEN final combined run:453passed, zero failures/skips in6.59s. tests.txt preserves the concise receipt.

Run covered new parser cases plus existing email/MIME, link/email-label/mailto, file intake/native fixtures, attachment coverage/export, IDNA, demo EML, link-coverage/export, negation, community/API, history and reference suites. No full model attempt occurred; intake checks use existing controlled fixtures. The new helper audit after.json records current results/source hashes and byte/paste equivalence. Evaluator reconstruction now uses concatenated nodes to reflect the corrected parser; the original before-results file was not overwritten.

## Residual limits

This is semantic HTML token handling, not a browser rendering model. CSS display/visibility, tables with complex layout, pseudo-elements, image alt text, malformed browser DOM repair and content hidden through styling remain unresolved. Plaintext whitespace/newline handling and linguistic inference are unchanged. A caller asking indirectly can evade existing rules. Subject incompleteness is structural uncertainty, not proof of fraud. These regressions establish parser behavior, not phishing accuracy or broad generalization.

Skipped browser/model/download work and any tuning of frozen public-pattern misses. Root owns independent review/integration. Risk remains finite presentation/grammar coverage; negative advice and inline requests now agree on the demonstrated equivalence pairs.
