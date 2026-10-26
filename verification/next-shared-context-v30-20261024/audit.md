# Shared Original native-validation dependency audit

contract.json froze the target-aware expectation before execution. Actual controllers were loaded together in the existing DOM double. Source finder was submitted successfully for shared Original containing a zero-width character; then a required Quote field was set empty without an input event. Captured invalid handlers on quote-form were invoked with the actual field as event.target, and no submit followed.

Observed for Original invalid: Source result remains visible, private context remains, Source formatting notice remains visible, Quote result hidden, zero requests. The Source finder depends on Original, so that output no longer represents the current supplied Original. Observed for Revised invalid: Source result and notice remain visible, correctly preserving the independent lookup. Source handler listens to input on Original/source passage and invalid on source-form only; Original belongs to quote-form, so native invalid for that field never reaches source-form. V29 Quote/Media handlers remain correct within their own scope.

This is a concrete constructed event dependency gap, not a demonstrated keyboard or autofill defect. Normal editing dispatches input and already invalidates both dependencies. Reproduction requires a value change without input plus native constraint validation of Quote; browsers suppress submit on invalid, so submit cleanup cannot solve cross-form state.

Smallest closure: within Source controller, capture quote-form invalid and call existing invalidate only when event.target is quote-original. That clears source windows, range/page state and formatting notice consistently. Do not clear Source for quote-revised invalid. Add paired direct-event tests with actual targets and no submit; retain passage/version drafts, prove zero I/O and next Find page0. No change to pure finder, Quote comparison or broad validation framework required. No source edits performed.

## Authorized closure

New tests/source_shared_invalid.test.cjs added first: Original cleanup failed, Revised independence control passed. Implemented exactly one captured quote-form invalid handler gated by event.target === quote-original and reusing Source invalidate. No Unicode controller changes.

Final 68 focused source pure/controller/paging/oracle, Unicode and Quote invalid tests pass, zero skips. Direct page-two regression removes private windows/range/status, hides notice and pager, disables both controls, retains all drafts and performs no I/O; next explicit Find starts page zero. Revised invalid retains independent page-two Source windows and notice.

Mechanical comparison against immutable v29 source ZIP: removing the one added handler restores the entire source-context.js normalized text exactly. Pure prefix SHA256 unchanged: 5316502ee7da8675caeee9435ea0edb9724951d2c027fe83a5a666d6145a582c. No finder arithmetic/offsets/schema/parser/model changes. Browser native focus/event propagation remains root's separate acceptance; constructed direct-event scope is unchanged.
