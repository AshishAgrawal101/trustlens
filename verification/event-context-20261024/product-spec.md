# Optional event date: pre-implementation contract

Add one optional unnamed date input to the existing Claim worksheet. Pure API input key `eventDate`: omitted or empty means no event comparison; otherwise a trimmed YYYY-MM-DD strict valid calendar date, string <=10 characters before trimming. Reuse existing date validator; no inferred date/range/timezone or source visit. Old return shapes, outputs when omitted/empty, source counting, roles and fixed PLAN bytes remain unchanged.

Only a source with URL or quotation counts as an account and qualifies for comparison with its supplied publication date. Date-only fields do not become source accounts. For each eligible dated account append observation ID `dates:a:before|same|after` or `dates:b:before|same|after`; compare publication date against event date using UTC calendar midnights. Describe absolute calendar-day difference, supplied/unverified status, and no truth/independence conclusion. Earlier publication may be an announcement, not a contradiction. Present event date adds fixed unverified context notice/question; no new truth score or automatic source relevance finding. No raw date or field content is added to fixed exports.

UI: claim-event-date optional type=date, no name, bounded to years supported by current strict four-digit pure validator, associated hint. Existing explicit Review only; date edits invalidate result and exports. Clear/pagehide/persisted Back erase date and rows. Examples replace private drafts and leave optional event date blank. Private print omission unchanged. Result uses existing observations/questions lists; no new panel/chart/controller/module.

Cases frozen before implementation:
1. Absent/empty eventDate exact original review/analyze output and unchanged PLAN hash.
2. 2024-03-01 event, Source A 2024-02-28 publication =>2days before (leap day).
3. 2024-01-01 event, Source A 2023-12-31 publication =>1day before.
4. Same date =>same calendar date, no automatic truth claim.
5. Source B publication 2024-03-03 vs2024-03-01 =>2days after.
6. Missing source publication =>no invented comparison; existing missing-date question retained.
7. Date alone without URL/quote =>not counted as account/no source comparison.
8. Invalid leap day, nonstring/oversized input/partial date =>fixed private error.
9. Event field input invalidates output/export; Clear/examples/exit/Back erase field and result; no network.
10. PLAN byte hash matches before/after and copy/download omit supplied event/source fields.

Root-approved example adjustment before implementation: the existing constructed caption example will explicitly state 15 June 2024 in the claim and eventDate=2024-06-15, beside its existing2020 publication date. Loading the example replaces prior drafts and still requires explicit Review; no date is inferred from “today” or the computer clock. Other examples leave eventDate blank. This replaces only the earlier example-blank assumption for that one constructed example.
