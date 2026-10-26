# Numbers cross-field error recovery

Recommend the small native-validity improvement. `before.json` reproduces ordinary input/Compare for A-only, B-only and dual `count > total`: every case focuses the same generic four-field error, preserves the drafts and hides results. The user must locate which group is wrong. The inputs themselves are within required/min/max/step constraints, so native validation currently cannot identify this cross-field issue.

`contract.json` freezes the three cases, proposed precedence/reset boundaries and the unchanged pure-prefix SHA. This is recovery usability, not a wrong arithmetic result: the pure comparator correctly rejects all three today. No new field, button, parser or calculation is justified.

## Smallest complete controller change

Keep the initial `form.reportValidity()` for native required/min/max/step failures. Retain the existing digits-only conversion unchanged; exponent/decimal wording rejected by that check must keep priority over a relationship error. Immediately after that existing count input object is built, set fixed native custom validity on each offending count using the already-parsed `input.countA/totalA` and `input.countB/totalB`. Suggested text: **Group A count cannot be larger than Group A total.** and equivalent B. Mark both if both fail; call `form.reportValidity()` and return, allowing browser focus on the first invalid count in DOM order. Only then call unchanged `NumbersContext.compare(input)`. Percentage mode is unaffected.

Do not duplicate the pure integer/range parser or math, derive a new denominator, change input values or automatically Compare. Both pure functions/module prefix must remain byte-exact. Swap continues swapping raw active pairs only; retained inactive-method drafts remain independent.

## Important event-order trap

Current form has captured `invalid → invalidate`. **Do not put custom-validity clearing inside `invalidate()`**, because native `reportValidity()` dispatches `invalid`; that would remove the very message being reported. Keep result invalidation and custom-message reset separate. Clear count messages on any input edit (including either total), method change, Swap, Clear, example and lifecycle reset. Starting an actual submit may clear/recompute old custom messages, but unchanged resubmission blocked by the browser should still report them normally. No new custom-validity state should prevent switching to percentage mode.

## Scope and acceptance

Scope: `static/numbers-context.js` controller only, dedicated regression and minimal DOM-double support for standard `setCustomValidity`/reporting if necessary; no HTML/parser/API/CSS/Pocket fork needed. Existing number min/max/step markup already gives native single-field priority. Root owns real-browser and shared Pocket cache/export integration.

- A-only targets count-a, B-only count-b; dual sets both and browser reports A first. Fix A while B remains wrong, then Compare reports B. No source values in custom messages.
- A total input edit clears the old count-a error before another Compare; a B edit clears stale relationship messages likewise. Drafts stay exact and results remain hidden until explicit Compare.
- Required/overflow/underflow/step native failures take priority, and existing digits-only parse failures get their existing fixed error before cross-field messages. Include an overflow plus relationship case and an exponent/digits-invalid plus relationship case.
- Method change clears custom messages while retaining separate raw drafts and disabling inactive fields; valid percentages compare even with invalid retained count drafts. Swap clears old custom associations without changing its raw-data semantics. Clear/example/exit wipe/reset exactly as before.
- Preserve old counts/percentage math/oracle outputs, no autorun/network/storage, and do not make expected historical hashes self-referential. Tests must exercise native invalid-event ordering rather than treating submit alone as browser validation. Native focus/validation-bubble behavior needs a real browser check; the existing generic controller double alone cannot establish it.

Main harm to avoid is sticky or prematurely cleared native validity: it could block every later submit or hide feedback. The event-order separation above and explicit total/method/reset cases bound that risk. The benefit is concrete correction at the existing count field without another UI layer. No application files were changed for this review.
