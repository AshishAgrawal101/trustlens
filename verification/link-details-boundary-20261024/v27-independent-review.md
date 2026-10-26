# Independent v27 scope and raw-reference review

Read-only comparison against immutable v26 source ZIP, normalizing CRLF for inspection, found exactly two intended changes: communication_report always prepends its existing English wording limitation even with custom limitations; add_guidance appends one fixed English-coverage sentence to text/call/email exports. No rule, weight, evidence, risk, action or model change exists in these two diffs.

Independent old-module/current-module exercises covered German password wording, risky English code request, ordinary meeting reminder, and custom-limit email. Reports were identical outside intended limitations; action objects were identical, and removing the one new fixed scope sentence made each export byte-identical to v26. German remained low (a disclosed language miss), risky remained high, ordinary low and custom email high. This is compatibility evidence, not accuracy measurement.

Optional-reference policy is aligned with strict producer validation: only empty/ASCII-space-only fields are omitted. All other supplied reference bytes are forwarded unchanged. Ordinary URL edge spaces are accepted by the producer; TAB/BOM-only and prefixed references are rejected. Broader trim() would discard invalid controls and is intentionally avoided. Raw required URL is always forwarded. Producer errors are fixed and contain no supplied address.

Actual in-process API probes with wrong-type URL, oversized private URL and wrong-type reference all returned HTTP 422 with exactly the same fixed private detail, without input echo. No external URL was contacted.

Validation: 70 focused Python tests (communication scope + URL details), 6 controller tests, all pass, zero skips. No source changes in this review. This does not establish general German coverage or model readiness.
