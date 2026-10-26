# v29 independent reliability audit

One reproduced narrow gap: Quote native-invalid events do not clear an old comparison. probes.json was frozen before inspection/execution. Reproducer quote-invalid-probe.cjs loads the actual Quote, Source and Unicode controllers in the existing DOM double, submits two valid versions containing a zero-width character, then changes the required original field without emitting input and delivers only invalid (native validation suppresses submit).

Actual result: comparisonStillVisible=true; oldPrivateDiffRetained=true; formattingNoticeHidden=true; requests=0. Quote only invalidates on input or submit; Unicode notice independently clears on captured invalid. Numbers, Claim and newly paged Source already have captured invalid cleanup. Thus the combined rendered state can retain an obsolete comparison while dropping its corresponding formatting notice. This is local stale presentation, not a network/privacy exfiltration claim.

Scope limit: ordinary keyboard editing emits input and already clears the result. The reproducible boundary is a native-invalid event after a value changes without that event (constructed programmatic/autofill-style mutation); no real browser/autofill behavior was demonstrated. Existing quote invalid test calls submit with reportValidity=false, which does not exercise native submit suppression. Root should decide whether the one-line consistent invalid handler merits inclusion.

Smallest recommendation: quote-form.addEventListener('invalid',invalidate,true), with a regression that delivers invalid without submit and checks old diff/status removed, result hidden, formatting notice hidden, drafts preserved, no exports/network. No pure comparison or other workflow changes needed.

Focused baseline: 21 Quote controller, Unicode notice and Numbers controller tests pass, zero failures/skips. Probe uses actual current producers/controllers; no invented malformed server response, file access/upload, model work or remote destination. No app/test-source edits. No further substantive gap established in this bounded review; no blanket correctness claim.

## Quote fix closure

Added tests/quote_invalid.test.cjs first: direct captured-native-invalid combined Quote/Source/Unicode regression failed because the previous comparison remained visible. Added only quote-form captured invalid listener reusing invalidate. Regression now passes; 40 relevant pure/controller/paging/Unicode tests pass, zero skips. It checks private drafts unchanged, old diff/status/error removed, result/formatting notice hidden, empty guidance restored and zero requests/clipboard/downloads.

Mechanical comparison to immutable v28 source ZIP confirms removing that single added handler restores the complete previous quote-context.js text (newline-normalized). Pure compare region remains byte-identical, SHA256 d09e00a682ab96ac1f290a2c71cef06c577230fbd6e9ddaa45d1d816c7791bfe. No math/alignment/schema changes.

Separate Media contract was frozen in media-invalid-contract.json before execution. DOM-only probe media-invalid-probe.cjs uses existing synthetic report/mock file metadata, no image payload/backend. After completed inspection then native-invalid without submit, oldResultVisible=true, oldFactsRetained=true, extraRequests=0. Initial harness failed module resolution; corrected only its require base to the existing tests directory, then reproduced. No Media source edits. Same narrow boundary caveat as above applies; proposed captured invalid cleanup awaits root approval.

## Media fix closure

Root authorized the separately reproduced Media boundary. New tests/media_invalid.test.cjs was run first: both completed-output and pending-request regressions failed before source change. Added exactly one captured invalid listener reusing existing invalidate. One subsequent assertion needed DOM-double adaptation from unsupported getAttribute to its existing attributes map; no production change was needed. Final 32 Media context/controller/cancel/semantic tests pass, zero skips.

The direct invalid event now removes completed facts and status, aborts the pending client signal, restores controls/aria-busy, and prevents both late success and late failure from restoring output or focusing errors. Selection, preview and caption remain intact; no extra request occurs. Mock metadata only; no image payload/backend/browser upload. No policy, metadata interpretation, endpoint, pure helper or model changes.
