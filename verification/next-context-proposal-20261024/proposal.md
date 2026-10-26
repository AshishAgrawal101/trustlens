# One bounded next capability: inspect later literal matches

**Proposal:** add explicit Previous five / Next five navigation to the existing Quote & context passage finder. Do not add a page, search service, matching mode or verdict.

Grounded gap: SourceContext.find already counts every exact non-overlapping occurrence in up to30,000supplied characters, but retains only the first5windows (static/source-context.js). The UI/docs explicitly say “Showing the first5”; tests/source_context.test.cjs and source_controller.test.cjs lock that cap, including30,000matches. A user inspecting a repeated quotation in a transcript/article can learn that17occurrences exist but cannot inspect occurrence6or17in this tool. Later surrounding qualifications may differ. This is a disclosed feature limit, not a current correctness/accuracy bug.

Not duplicate scope: Claim already supports two manuallylabelled accounts and supplied event/publication chronology; Numbers now supports counts or reported percentages without inventing sample sizes. Quote already compares versions and finds exact wording, so paging existing occurrences fills a narrower concrete workflow gap than another worksheet/input.

## Minimal contract for a later approved slice

Keep existing twoargument find API/schema/frozenoutputs unchanged. Add a separatelynamed bounded page accessor or internalsharedwindow routine, preserving exactcase/whitespace/nonoverlap/UTF16offset/surrogatewindow behavior. Explicit integer pageindex only; at most5windows perrender, source still30,000/quote4,000. Re-scan the bounded suppliedsource on explicit navigation if simplest; do not retain all contextwindows or fetch a source. Show “Matches6–10of17” with actualordinaltitles, not repeated1–5. Firstpage remains the default on explicitFind. Next/Previous are disabled when unavailable, and all edits/Clear/example/exit/persistedBack invalidate navigation and results. No autorun, storage, URLstate, clipboard/export or cross-tool transfer. Keep rawtext/textContent, context-edgeellipsis/Unicodepresence notices and the existing found/notfound authenticity/meaning caveats. A later occurrence is not independent evidence or a truth score.

## Acceptance cases to freeze before implementation

- PAGE-01:0/1/5matches keep existing firstpage output; navigation absent/disabled appropriately.
- PAGE-02:6distinctlysurrounded matches: firstpage1–5, explicitNext shows only6with correct originaloffset/before/text/after, Previous restores exactly1–5.
- PAGE-03:10and11matches test exactfull-lastpage vs partialthirdpage; no skip/duplicate and correctrange/total labels.
- PAGE-04:overlap `aa`in`aaa`, case/whitespace mismatch and HTMLliteral preserve current semantics on everypage.
- PAGE-05:contextwindow crossing astralsurrogate atpageboundary preserves pairs and originalsource reconstruction; no normalization.
- PAGE-06:30,000onecharacter matches still render atmost5atonce, first/lastpage reachable with boundedwork and no I/O; invalidpageindices reject fixederror without inputecho.
- PAGE-07:editing either sharedOriginal or passage, loadingexample, eitherClear and lifecycleexit/Back remove oldpage, counts/windows/formatnotice and disable stalebuttons; nextFind startsfirstpage.
- PAGE-08:keyboardnavigation announces/focuses visiblecurrentrange, buttonsremainusable320/390, no automaticFind; quotation/sourceunverified caveat remains with allpages.

No v27 changes. No implementation/evaluation or new performanceclaim. Root should prioritize this against other work before assigning ownership; frozenoldfirst5contracts remain historical/APIcompatibility checks.
