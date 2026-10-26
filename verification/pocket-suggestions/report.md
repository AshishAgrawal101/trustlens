# Pocket opt-in topic suggestions — 2026-10-23

Implemented only new static/phone/suggestions.js, new tests/pocket_suggestions.test.cjs and this verification folder. Existing Pocket markup/scripts/styles/cache/version, desktop rules and all model files were left to their owners. No dependencies, storage, remote calls, automatic inbox access, training or model downloads were added.

## Integration contract

Root adds button #suggest-topics (type button), live region #suggestion-status and list/container #suggestion-results, then includes /phone/suggestions.js after the existing Pocket scripts/DOM and updates its offline shell version/cache assets. The widget reads existing #message and input[name=request] money/code/device/secret. It also listens to #guide submit, #clear and #example. The pure CommonJS/helper interface is PocketSuggestions.suggest(text), returning topic/label/snippet rows.

The Suggest click is opt-in. It produces up to four topic suggestions using short English literal request patterns and matched on-page excerpts of at most 120 characters each. It never changes selections. Each separate Apply topic action selects only that topic and dispatches the existing checkbox change event, invalidating old guide results through the existing controller. Focus moves to the selected checkbox. Existing selections display Topic already selected, and manual checkbox changes refresh those buttons. Live status changes after Apply so it no longer claims no topics changed.

Message edits, Clear, example replacement, guide submission, pagehide and persisted pageshow remove all suggestion text/result nodes. Dynamic content uses textContent, never HTML. Suggestions and private excerpts do not enter PocketGuide.summary or existing exports; this file adds no export, network, URL, cache, logging or persistence path. Source text remains in the existing textarea until the existing Clear/lifecycle behavior removes it.

## Conservative scope

Money: gift-card purchases, literal currency transfers/payments, sending money/bitcoin/crypto. Code: a finite set of explicit code/password/account-number requests. Device: AnyDesk/TeamViewer installation/download or enabling/allowing remote access. Pressure: keep this/it secret or act now. These identify possible checklist topics, not fraud or sender identity.

Entire sentences containing quotations, negation, advice/condition markers or finite history/training markers are skipped. This deliberately misses mixed-context current requests rather than pretending to resolve intent. The implementation has a shortcut comment specifying this boundary. No suggestions does not establish safety and the visible empty state says to select topics manually. Legitimate sensitive requests can suggest the same topic as a scam.

## Frozen diagnostic and residuals

Before implementation/evaluation, froze 24 constructed cases in frozen-cases.json. SHA-256 remains 4A8BA3528381CE7CE5117FDA5714DCF3807F0E66A59DE71FF9AF07064B2F5AC7. No real public scam, private user message, spam corpus, dataset image or final input was used in this new diagnostic. Cases include expected useful direct requests, ordinary/advice/history/quotation controls, a legitimate payment request and deliberately harder paraphrase/mixed-context requests. This is examined development material, not an independent evaluation or accuracy claim.

results.json records 18/24 exact topic sets. Nine ordinary/advice/context controls produce no suggestions; nine supported sensitive requests, including the legitimate lunch transfer, produce their expected topic. Six misses remain unchanged: implicit code reference, indirect balance wording, negation with a later live request in the same sentence, history with a later live request, quoted live caller wording, and secrecy expressed as do-not-tell-family. These outcomes were retained rather than expanding rules to chase every constructed case. No unsupported topic was emitted on this frozen set; that does not establish real-world precision.

Reproduce: node verification/pocket-suggestions/evaluate.cjs. Results contain case identifiers and topic sets, not message contents or private snippets.

## Verification

RED: tests were written first and initially failed because suggestions.js did not exist. Focused tests passed after implementation; the final paired run with existing comparison tests is 8/8 passed, no skips. See tests.txt. The five new tests cover bounded/deduplicated snippets and topics, input limit, direct negation/advice/history, independent live sentence, opt-in initial behavior, explicit per-topic Apply/change/focus, selected-control refresh, no-match uncertainty, private snippet clearing and page lifecycle invalidation. DOM tests use the existing project's small offline-double pattern, not a real browser. No actual model/runtime work occurs.

Skipped physical Android, browser accessibility and integrated service-worker checks; root owns markup/cache/browser integration. Risks: English literal suggestions can miss current requests or suggest topics for legitimate requests; the user must review and explicitly apply each one. This adds assistance to the manual checklist, not automatic scam detection.
