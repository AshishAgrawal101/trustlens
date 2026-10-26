# One proposed v29 workflow: reverse a Numbers comparison without retyping

Read-only proposal. No app/tests changed and no v28 archive/source receipt altered.

## Concrete gap and priority

Numbers already reports B-minus-A points and relative change “compared with A” (static/numbers-context.js calculated-fact rendering). The final guidance correctly says A is only the baseline. Yet the controller exposes only Compare, Clear and a constructed example; there is no way to exchange the groups except re-entering four count/total fields or two percentage strings. The two methods and disabled-field sync are in the same controller. Retyping is unnecessary and risks pairing a count with the wrong total or losing a long supplied decimal.

This is an actual missing interaction, not a correctness bug in the existing arithmetic. The learning value is already supported by frozen tests: tests/numbers_context.test.cjs has “swapping groups reverses points but relative percent has its own denominator”; reported_percentages_math.test.cjs explicitly tests20/15=-25% and15/20=+33.333…%. Current UI cannot expose this comparison cheaply. One action in the existing worksheet is preferable to another calculator/page/method or more static advice.

## Bounded proposal

Add one `type=button` action “Swap A/B inputs” near existing input actions, initially disabled until controller setup. Exchange only active-method raw input strings: count with count AND total with total, or percentageA/B. No parse/rounding/conversion, validation weakening, input history, source transfer or hidden-method mutation. Keep current method. Existing pure functions and their hashes stay unchanged.

Invalidate the old result/error first, swap atomically, announce fixed status “Group inputs swapped. Group A is now the other comparison baseline. Select Compare proportions to calculate again.” Keep the action focused for a second swap; do not submit or focus a disappearing result. Disable only when all active inputs are empty, preserving incomplete/invalid drafts if the user explicitly swaps them. Clear status on any edit/new comparison/method change/example/Clear/exit/Back. Clear and lifecycle behavior remains as currently implemented. The action is optional and causes no work until chosen.

## Acceptance to freeze if selected

- Counts20/100vs30/200: initial rates20/15, points-5, relative-25; swap exact pairs to30/200vs20/100, old result hidden, no new calculation until Compare; then points+5/relativeAbout33.3333. Swap twice restores byte-identical field strings.
- Percentage1.2/1.8 and two long nearby decimals: exact raw string exchange, unchanged hidden counts, current method retained, no invented denominator/normalization. Explicit Compare uses existing frozen math.
- Zero baseline swapped either direction preserves existing Undefined policy; partial/invalid drafts are moved rather than silently repaired or lost. No stale result/export remains.
- Keyboard action remains focused and announces fixed status; minimum44px target/no overflow320/390. Initial disabled/no-JS unnamed form and private print omission remain.
- Method switch, example, Clear, pagehide and persisted Back remove the status; ordinary edits invalidate and restore readiness. No request, clipboard, storage, URL state or automatic Compare.

Affected scope if approved: static/numbers-context.html/js, small numbers-context.css adjustment only if needed, new controller/markup tests. No tools-directory entry, new dependency, model or new pure arithmetic needed. Existing Pocket alias uses this same template/controller, so root would advance the prepared cache/export in a new version; frozen v28 stays unchanged. No physical-phone or human-learning benefit claim is established by this audit.

Priority: a medium-sized usability improvement with a clear end-to-end demonstration, after any observed accessibility/data-loss regressions. I found no new comparably concrete source-proved critical UI defect in the inspected current Tools, Quote paging, Claim disclosure or Pocket context links. Do not infer a new bug merely because a feature could be added.
