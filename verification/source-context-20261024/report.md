# Independent exact source-context acceptance

All twelve frozen cases pass. Frozen contract SHA256 7554de40b53410337188c9deb769303dbce0ea99e1d8299fef721ccee72c274a is unchanged and predates module creation. The retained one-time evaluation source SHA256 is 17c53f0b09f6c8dc338dd25780e63a1fcaceeeb430a0829258fbdca03b4e11a9. results.json contains all actual output spans/context and errors; the evaluator refuses to overwrite it. Subsequent tests reevaluate in memory without replacing historical results.

Exact totals, first-five offsets and truncation match every case, including nonoverlapping aa in aaa, case/whitespace/punctuation sensitivity, literal ellipsis/HTML, Unicode UTF-16 offsets and source-edge windows. Both surrogate-boundary cases extend context to161 units rather than cut a pair. All contexts reconstruct exact adjacent source slices. No normalization, trimming of matched content, source authentication or semantic interpretation occurs.

Eighteen tests pass in126.9ms process duration. Additional bounds cover strict strings/nonblank checks with fixed no-private-echo errors, 4,000/30,000 UTF-16 units including emoji, preserved surrounding whitespace, all30,000 single-character occurrences counted while returning five, and exact160/161-unit contexts. A loose1second bound on the30k one-character test guards against unbounded work, not a deployment latency claim; that combined counting/bound test took3.0ms in this run. The isolated evaluator attempted no fetch/XHR.

No pure matching defect found. The module uses indexOf and advances by the exact quote length, so overlap is deliberately not counted. It stores at most five windows while counting every match. Output preserves source text and offsets, and no network/storage is required.

## Controller finding sent to root

Source review found a stale-result trigger outside pure arithmetic: after locating a quotation, clicking the existing quote example button programmatically changes Original version without dispatching input. The first locator controller listened to original/source input and quote-clear but not quote-example. The old locator result can therefore remain visible for the old query. Recommended minimal fix: invalidate locator output on quote-example click, with a controller regression; no matching algorithm change. Root owns this controller and is working on it. This report records the initial finding; closure requires root's later receipt rather than rewriting frozen results.

The UI uses createTextNode/mark.textContent for context and explicitly says no match does not prove fabrication and a match does not authenticate source/meaning/truth. That source review does not replace browser tests for actual display, focus, erasure or stale programmatic edits. Original quote comparison, old results and app code were not edited by this worker.

These are constructed literal-location checks, not quotation authenticity, contextual completeness, factual accuracy or a user study. The user-supplied passage may itself be partial or fabricated. Matching supplied text does not establish an independently verified source.
