# Hidden Unicode formatting: literal tools interpretability audit

Read-only audit. No app, frozen contract or historical result changed. Ten fresh constructed probes were saved before pure API execution: constructed-probes.json SHA256 0326724840912864a65bdd5413baa958df2066acd33582679a49e5697d90542b. results.json retains current compare/find output and both source hashes. No browser, private input, model or external content API was used. General Unicode documentation was opened separately; no probe text was submitted to it.

## Concrete observed gap

Six formatting-only changes returned compare.identical=false and find.total=0: inserted U+200B ZERO WIDTH SPACE, U+00AD SOFT HYPHEN, U+2060 WORD JOINER, U+202E/U+202C directional override pair, U+2066/U+2069 directional isolate pair, and U+200F RIGHT-TO-LEFT MARK. An identical soft-hyphen pair returned identical=true and one source match. Legitimate emoji ZWJ, Persian ZWNJ and ordinary controls also remained exactly identical with one match.

Those are correct literal outcomes under the existing contracts. The gap is explanation/display: the comparison and finder render raw control characters as text, but their fixed statuses mention only wording/whitespace differences. There is no formatting-character presence notice. A reader can be shown removed/added segments whose distinguishing character has no ordinary visible glyph, or a no-match outcome without a visible reason for literal mismatch. Directional controls can also influence the order of displayed text; textContent prevents HTML execution but does not remove Unicode rendering behavior. Current stylesheet has no special control disclosure or bidi isolation.

This audit did not compare browser pixels. It does not claim these probes always look identical, reproduce a particular cross-span visual exploit, or defeat a browser's actual bidi handling. Font, line break and directionality matter. The independently reproduced fact is the exact output difference/no-match plus absent character disclosure; the visual-order risk is grounded in Unicode's rendering specification and needs browser testing before a specific exploit claim.

## Legitimate uses and authoritative grounding

[Unicode UAX #14](https://www.unicode.org/reports/tr14/) describes discretionary hyphenation and line-break controls. Soft hyphens and zero-width break opportunities can be introduced by ordinary publishing/copying; word joiner intentionally inhibits a break. Treating their presence as fraud would confuse typesetting with intent.

[Unicode UAX #9](https://www.unicode.org/reports/tr9/) defines directional marks, embeddings, overrides and isolates for mixed-direction text. They may be necessary for legible Arabic/Hebrew mixed with Latin text or numbers. U+200D ZERO WIDTH JOINER and U+200C ZERO WIDTH NON-JOINER also have legitimate shaping uses; the probes include emoji and Persian examples. Do not strip all format characters, call the text malicious, or infer an author tried to deceive. These raw-code-unit tools intentionally retain exact input rather than performing a linguistic equivalence comparison.

## Smallest fact-only notice proposal

Preserve QuoteContext.compare and SourceContext.find schemas/results exactly. Add a separate bounded formatting-inspection helper used by controllers after an explicit successful Compare/Find, without rewriting input or rerunning matching on a transformed string. First scope: U+00AD, U+200B, U+2060, U+FEFF, U+061C, U+200E/U+200F, U+202A–U+202E and U+2066–U+2069. Report only fixed code-point names and per-input counts, including controls anywhere in the admitted source, not only returned windows. No original snippets, automatic removals, fuzzy matches, intent/credibility score or truth conclusion.

Suggested fixed notice: “Invisible formatting characters are present. They can affect display or exact matching and are also used in legitimate text. No characters were changed.” If directional controls occur, add: “Directional formatting can change display order.” A disclosure can list names/counts such as U+202E RIGHT-TO-LEFT OVERRIDE without embedding the actual control character in the warning. No notice for absence should say text is safe or free of all visual ambiguity.

Avoid blanket category-Cf warnings in this minimal slice: ZWJ/ZWNJ are common legitimate orthography/emoji, while variation selectors are not all Cf. Excluding those from the first notice does not establish they cannot affect display. A future visible-code-point view or bidi containment would be a separate UI design requiring browser/accessibility tests, not a silent normalization patch.

Use a dedicated fixed-text notice region outside raw text containers. Clear it on every relevant edit, main Clear, source Clear, programmatic example replacement, pagehide and persisted pageshow. Keep source/query text local, no storage/export/network; shared raw input must remain intact. Preserve all old frozen contracts; add new helper/controller regressions for each admitted character, ordinary multilingual text, legitimate joiners, copied soft hyphens, counts, private-string omission and stale resets. Root should authorize exact helper/UI ownership before implementation.

## Scope limits

This is an interpretability improvement, not a literal matching bug or evidence of attacker intent. It does not resolve homoglyphs, normalization, OCR errors, malformed surrogate strings, semantic quotation changes or authenticity. No auto-repair is proposed. Existing exact-match and not-fake/not-truth caveats remain necessary even with a presence notice.
