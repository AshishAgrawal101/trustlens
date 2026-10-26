# Factual invisible-format notice implementation

Added only static/unicode-notice.js and tests/unicode_notice.test.cjs, plus this new receipt. Root separately supplied two hidden polite status regions (quote-formatting, source-formatting) and loaded the helper after the existing quote/source controllers. No existing comparison/finder module, raw input, frozen contract or historical result was changed by this worker.

UnicodeNotice.inspect accepts a strict string of at most30,000 UTF-16 units and returns only total, fixed code-point/name/count rows and a directional-presence boolean. Its finite18-character set includes soft hyphen, zero-width space, word joiner/BOM, Arabic/left/right direction marks, embeddings/overrides/isolates and legitimate ZWJ/ZWNJ. It performs one bounded pass, no normalization, interpretation, network, storage or dependencies. Names/counts are deterministic, and no source text is returned by this helper.

The notice controller runs after explicit successful Compare/Find submissions, using the existing result's hidden state. It scans all admitted source text, including characters outside returned context windows. Absence leaves the notice empty/hidden and makes no safety claim. Presence says characters can affect display/exact matching and also occur in legitimate shaping/emoji, with no characters changed. Directional presence adds only a display-order fact. Fixed field labels, names and counts are rendered with textContent; no actual control character or private snippet is inserted into the notice.

Relevant inputs clear the corresponding notices; Original affects both, Revised only comparison, Source passage only finder. Main Clear/example, source Clear, pagehide and persisted pageshow are covered. Failed submissions clear old notices, and capturing native invalid listeners also clear notices when browser constraint validation prevents a submit event. Pure compare/find schemas and exact raw-string behavior remain unchanged.

Validation: nine new pure/controller/markup tests plus existing quote/source frozen contract suites total45 passes in126.9ms process duration. Cases cover all18 names/counts, legitimate joiners, ordinary Arabic/Hebrew text with no targeted controls,30k bound/nonstring errors, unchanged private input, hidden initial state, all-source scanning, absence/no reassurance, edit/example/clear/exit, failed/native-invalid submission and root markup/script ordering. The previous independent audit's frozen probes/results remain historical; no diagnostic was retuned.

No browser test was attempted: root reported the current Debugger unattached. Controller doubles/source assertions do not establish real screen-reader announcements, rendered glyph behavior, keyboard focus or device compatibility. The notice does not expose every invisible/ambiguous character, authenticate a quote, infer intent, repair visual order or decide that text is malicious. Existing literal/uncertainty caveats remain necessary.

Helper SHA256: a4a70808b5e88b22395144c774fc7fd0adddfade665dcfaf0bdf172e0c883c41.

## Integration closure

Root reviewed the helper and corrected the host notice regions from p to div, matching their appended paragraph/list children. The owned markup test accepts the corrected container and retains hidden/polite status semantics. Root reports the full JavaScript suite at382 passes; this is root's integration count, distinct from this worker's45 targeted passes. Native-browser verification is pending root execution. No further app edit was made by this worker.
