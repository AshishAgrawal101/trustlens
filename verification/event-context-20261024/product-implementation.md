# Optional event-date implementation

## Delivered scope

Changed `static/claim-review.html` and `static/claim-review.js`; added `tests/claim_event_date.test.cjs`. Added only one optional unnamed date field (`claim-event-date`, pure key `eventDate`) in the existing worksheet. No CSS, phone, worker, cache, export packager or general docs changed. The field is a supplied claimed date, never inferred from wording or the computer clock; unknown/range dates should be left blank.

Pure review/analyze return shapes remain unchanged. When a nonblank event date is supplied, eligible source publication dates receive descriptive before/same/after rows and fixed unverified context. Eligibility requires source URL or quotation: date-only inputs remain zero accounts and produce no account chronology. UTC-midnight Date.parse subtraction measures calendar days without local DST or Date.UTC's 0–99 year remapping. Strict existing calendar validation applies, with a raw10-character cap and fixed private errors. Existing year0000 pure-validator behavior is retained rather than silently changing historical validation; a constructed0000 leap-boundary probe gave2days. Normal browser date entry remains browser-controlled with a four-digit upper bound.

The fixed PLAN string is untouched. Missing/empty event date review and analyze outputs match the three pre-edit frozen contracts exactly. Existing source counts, role semantics and next-step priority are unchanged. Date differences do not verify sources, establish independence, identify contradictions or settle truth; earlier publication may be an announcement or refer to another event.

All existing field invalidation and lifecycle erasure now include the event input. Both input/change invalidate result and exports. Clear/exit/persisted Back erase it. Loading examples replaces drafts; the constructed caption now explicitly supplies15June2024/event2024-06-15 beside the existing2020 source date, then waits for explicit Review. This root-approved adjustment is recorded in product-spec.md; no “today” interpretation occurs. Other examples clear the optional date.

## Evidence

- Spec/cases and `old-output-contract.json` / `plan-before.sha256` frozen before edits.
- Initial six tests: **4 failed,2 controls passed**, recorded in product-red.txt.
- Final seven new tests include calendar boundaries, absent compatibility, date-only/missing sources, invalid inputs, unnamed optional markup, fixed copy/download bytes, edit/Clear/example/lifecycle and late clipboard feedback.
- Combined current full Node: **496 passed,0 failed/skipped** (`product-node.txt`). No old test was edited.
- Independent13-branch Python-calendar oracle/evaluator was frozen by image_evaluation before implementation and handed the ready code for separate execution. Results were pending when this report was written.

This is constructed local source/controller evidence. Actual browser layout/date selection/printing and refreshed Pocket cache/export are root-owned follow-up; no physical-phone or source-verification claim follows. v23 and earlier archives remain untouched.

Independent follow-up: image_evaluation reports **13 frozen branches /24 inputs green** against its Python-calendar oracle and v23 archive compatibility baseline; **53 focused tests passed**. No concrete gap found. Its evaluator required a URL global in the isolated VM (harness-only, no application issue). See sibling independent results/review receipts. Browser/offline integration remains root-owned and pending at this checkpoint.
