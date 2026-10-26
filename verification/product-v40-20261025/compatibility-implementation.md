# Source finder optional jump controls

Changed only `static/source-context.js`, new `tests/source_legacy_dom.test.cjs` and exact immutable fixture `tests/fixtures/quote-context-v32.html`. No existing test guard/expectation, shared fixture, HTML, parser, cache, export or documentation edit.

First/Last buttons are bound once. Their reset/disabled rendering and listener setup are guarded when absent. The essential existing form/result/Previous/Next controls remain required; this is not a general missing-DOM fallback. Current markup retains identical endpoint jumps and range-focus behavior. `compatibility-preservation.json` confirms the entire pure SourceContext/module-export prefix is byte-identical.

The new portable fixture is exact frozen v32 archive markup, SHA-256 `c7fbfbfbca5cd874630b7f3f1280a9b4b7ef02904ad91dd0b03626efe9d30ae9`. Tests honour its disabled Find before controller execution, return real null for missing IDs and never fabricate First/Last. Three pre-fix failures remain in `compatibility-red.txt`; `compatibility-green.txt` records **38/38** focused legacy/current jump/paging/oracle tests. `compatibility-integration.txt` records **78/78** related source/Unicode tests passing, zero failures/skips.

Legacy regressions verify initialization enables Find, explicit eleven-match finding, Previous/Next ranges and disabled-edge focus, retained inputs/no I/O, edit/native-invalid/Clear/lifecycle erasure and inert stale navigation. Current max-30,000 jump, frozen two-argument outputs, independent paging oracle and Unicode regressions still pass. No timing race was demonstrated in a browser; this closes the exact structurally possible old-markup/current-controller pairing. Root owns actual cache/export/version/browser verification.
