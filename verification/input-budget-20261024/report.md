# Bounded local input-budget audit

No application/validation changes. Six workloads were written and SHA256-frozen in contract.json before predictions, with exact payload files. Each child ran sequentially with a hard10second subprocess timeout. No models, network, private inputs, attachment execution or browser activity. Existing archives/frozen results unchanged. Source identities recorded separately in source-identities.json.

## Initial traced run

One analysis per fresh imported child; imports/file reads excluded from analysis wall/peak region. Peak is Python tracemalloc allocations, **not** process RSS, native allocation/RAM/VRAM containment or a system memory bound. Tracemalloc changes execution cost substantially.

| Workload | Bytes | Analysis wall, tracing enabled | Python traced peak |
| --- | ---: | ---: | ---: |
| Plain email |239996|0.083s|2522790bytes |
|1000small readable MIMEparts |32049|1.495s|1151557bytes |
|6000small readable MIMEparts |192049|10s process timeout|Not available: child terminated |
|5000ordinary headers |200040|0.138s|2374005bytes |
|120nested multipart containers |227245|0.517s|2849691bytes |
|Repeated bounded negative advice |30811bytes/30000characters|0.223s|435133bytes |

All completed children returned reports without exceptions. Nested workload returns an incomplete report because its constructed headerless inner body has a parser separator defect; this is workload characterization, not a measured classification regression. The timed-out child receipt remains results.json and was not overwritten by later methods. No peak was guessed for it.

## Bounded repeats of the existing two part-count payloads

To distinguish tracing overhead from real parser cost, repeated only the already-frozen1000/6000part inputs with the same10s process timeouts. Separate immutable receipts:

- baseline-results.json, perf_counter only:0.425s and2.615s respectively (~6.15times for6times as many parts).
- profile-results.json, cProfile without tracemalloc:0.991s and7.375s.
- profile-focus-results.json, same cProfile method collecting specific application functions:0.970s and7.338s. These two profile observations are close, but are not a multi-run statistical performance claim.

Focused6000part cumulative times: parsebytes2.568s; analyze_message4.767s; body_parts1.070s; unscanned_parts_count0.972s; analyze_text0.215s. These intervals overlap due to nesting and **must not be added as independent costs**. Repeated typed header parsing is dominant:84009Content-Type header parses; the header-construction stack accounts for much of both parsing and later analysis traversals.

body_parts own time grows from0.0058s to0.139s, consistent with the growing checked_parts membership scan contributing superlinear work. But the full own interval (including other local work) is only about1.9%of the6000part profiled run, so it is an upper bound on membership cost—not a direct stopwatch of contains. A membership-only rewrite cannot be justified as the main measured bottleneck from this audit. The uninstrumented6000part run completes in2.615s, below the supplied45sinspection UI budget. This does not prove a worst-case bound for every250k input.

## Recommendation and limits

Do not optimize membership alone based on its theoretical complexity. If root pursues speed, first target the demonstrated repeated header-interpretation work with a measured before/after on identical synthetic inputs and unchanged malformed/duplicate/MIME/attachment contracts. Do not drop validation, retain private-message caches or add real-user telemetry. No optimization was applied here.

A max-byte cap alone is not a part-count bound, and this is a modest six-case audit, not fuzz coverage, concurrent load, cold-launch readiness, platform portability or a denial-of-service proof. The10s timeout belonged to the benchmark subprocess, not the application. No application timeout/worker isolation/RAM containment guarantee follows. All files/cases contain constructed local material only.
