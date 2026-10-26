# Independent v40 optional source-navigation compatibility review

Read-only source/test review. Pure SourceContext prefix is raw-byte-identical to immutable v39; legacy fixtures/quote-context-v32.html is raw-byte-identical to immutable v32 ZIP, SHAc7fbfbfbca5cd874630b7f3f1280a9b4b7ef02904ad91dd0b03626efe9d30ae9. Receipts/source diff adjacent. No app/test edits by reviewer.

No concrete gap found. New controller caches optional First/Last nodes and guards their disabled assignments/listener registration. Required Previous/Next/Find and existing fields stay required; no catch-all startup swallowing or fake missing element creation. New full markup retains direct First/Last behavior. Pure count/matching/windows/pagevalidation unchanged.

Legacy test harness truly returns null for absent IDs, imports exact old HTML without injecting modern First/Last, parses initially disabled controls, and records disabled Find before source controller runs. Independently counted every harness substitution target: all four occur exactly once, including HTML source, strict getElementById replacement, disabled-attribute parsing and source-run checkpoint. None silently misses or multiplies. getElementById now null is native semantics, not a fabricated DOM element. Current shared fixture otherwise remains unchanged by this repair.

Legacy setup proves initially disabled Find enables, explicit Find works with 11matches, Previous/Next ranges1–5/6–10/11–11 correct, endpoint focus moves to page status, input strings remain, no I/O. Edit/nativeinvalid/bothclear/lifecycle reset pager/results and stale navigation inert. Modern jump and existing sharedOriginal/Revised invalidation tests also pass; no change to privacy/reset/inputfree behavior inferred beyond tested boundaries.

Focused Node receipt includes legacy/paging/currentjump/sharedinvalid suites,zero skips. These DOM doubles do not prove physicaldevice, browsercacheasset update or visual focus. Root browser/version verification remains separate. Fix supports deliberately absent additive controls on older markup, not arbitrary incompatible HTML or a service-worker cache migration guarantee.
