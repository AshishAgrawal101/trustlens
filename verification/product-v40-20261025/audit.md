# v39 bounded product audit

Highest-value reproduced issue: **the Source finder still cannot initialize against older valid Quote markup that lacks optional First/Last controls**. This is the same class as the resolved Claim upgrade defect, but a distinct remaining controller/control pair, not another report of the fixed Claim button.

## Exact reproduction

Read immutable `TrustLens-professional-20261024-endorsement-context-v32-review.zip` member `static/quote-context.html`; copied its exact bytes to `v32-quote.html.txt`, with SHA in `legacy-contract.json`. Loaded the current Quote/Source controllers through the established combined-controller harness, substituting only that frozen markup and native `getElementById` semantics returning real null for absent IDs. No fabricated jump buttons or private DOM state were used.

`legacy-repro.json`: old markup lacks `source-first` and `source-last` and has Find initially disabled. Current `static/source-context.js:58` throws on unconditional First/Last `addEventListener` registration, before its final `clear()`/enabling step. The older page’s otherwise-supported Previous/Next finder becomes unusable. Guarding only listener registration is insufficient: `invalidate()` and `renderPage()` also unconditionally access both new controls.

This establishes the exact old-markup/current-controller compatibility failure, **not an actual browser cache-timing race**. The existing service-worker asset-ordering possibility makes the pairing relevant; no browser settings, worker, cache or version was altered by this audit. Current complete v39 assets and full source/extracted suites passing are not contradicted.

## Smallest justified fix to propose

Bind the optional First/Last controls once and guard their listener, reset and render/disabled access consistently. Do not make essential preexisting finder/form/result/Previous/Next hooks optional. Older markup should retain explicit Find, all-page Previous/Next behavior, result/privacy invalidation and native validation; current markup retains endpoint jumps/focus exactly. Pure SourceContext function/export prefix must stay byte-identical. No matching, Unicode, schema, new storage or worker change is needed.

Add a portable immutable-v32-markup regression with real-null lookup and initially disabled state honoured. Prove startup enables Find; explicit literal finding and Previous/Next work; edit/native invalid/Clear/lifecycle reset output; no private exports/I/O; current First/Last tests remain green. Verify the pure hash and existing frozen oracle rather than changing historical expected output. Root owns refreshed asset/cache/export/browser receipts if selected.

## Other inspected paths

Read current Media and main request/error/Cancel/lifecycle logic and existing media caption/admission, main response/revocation/lifecycle/cancel tests. Did not reproduce another ordinary-flow privacy or stale-response defect in this bounded pass. Media preserves caption notes without changing file-only requests; file replacement/Cancel/exit invalidate generations; main review revocation and stale fetch/copy guards remain. Main shortcut explicitly checks disabled submit before requestSubmit. No unsupported synthetic eventless-state scenario was promoted to a user bug. The still-section-focused Media result may merit future geometry evidence, but it is not a newly reproduced defect here and does not justify an automatic polish edit.

No application files changed, no upload/file-access permission bypass, browser/native-phone check, model, external data, network or download was used. Only local immutable archive reads and constructed controller probes produced these artifacts.
