# Conservative line segmentation correction — 2026-10-23

Independent review demonstrated that splitting at every period could detach a request from preceding advice. New eight-case diagnostic was frozen before baseline prediction and editing: segmentation-cases.json SHA256 3F794086322E271CF835849B7906A7C7BC22E021CCAE34D01F9C2BE7BB0A5074. Baseline and after topic sets are retained in segmentation-baseline.json and segmentation-after.json.

Minimal helper change: split only on CR/LF lines instead of punctuation. The existing context marker rules and topic patterns were unchanged. A one-line shortcut comment now states that an entire line containing advice/history/quotes is suppressed and same-line live requests may be missed. This supersedes older report references to sentence-based suppression.

The three reproduced controls (decimal amount, dotted domain and Mr. abbreviation) wrongly suggested money/device/code before the fix and suggest nothing after. Direct decimal and abbreviation counterparts still suggest their topics. A direct bank.test-domain counterpart is included in the regression and still suggests device.

Honest residuals: the frozen direct example.com counterpart now also produces no suggestion because the existing teaching-context marker “example” matches that domain token when the whole line is retained. The direct bank.test test is an additional positive contrast, not a replacement frozen case. No context-pattern retuning was added to chase this miss. A valid later request after negation on the same line is intentionally suppressed; placing the independent request on a new line still permits it. New diagnostic exact topic sets go from 5/8 to 6/8, with two retained misses (domain-direct and same-line-independent). No accuracy/generalization claim follows from these examined cases.

The original 24-case diagnostic bytes remain unchanged. Re-evaluation is in after-segmentation.json: the same 18/24 exact topic sets and same six residual failures as before. No old result receipt was rewritten. No NN/model, desktop rule or rejected candidate was touched.

Regression RED: one new paired-boundary test failed on the first reproduced decimal false positive. GREEN: all Pocket Node suites now 35/35 pass, no skips; see segmentation-tests.txt. New regression covers all three negative controls, direct currency/ordinary-domain/abbreviation contrasts and same-line conservative suppression. Existing independent-live-request test now specifies a newline, making the new boundary explicit. Existing markup, cache, practice and main phone controller were untouched by this fix.

Skipped browser/model work. Remaining limitation: line-wide suppression misses some useful suggestions; absence remains visibly uninformative about safety and the user can still select topics manually.
