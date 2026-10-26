# Minimal Pocket hostname boundary repair

Changed only static/phone/guide.js and new tests/pocket_host_boundaries.test.cjs. Root owns markup, generated landing source and cache version integration. No suggestion grammar, model, physical phone setup or frozen v16 archive changed. Original22-case frozen source/before outputs remain immutable; after-boundary-fix.json is a labelled regression replay. Current guide SHA256 a1848f7a28c64babd04fb50b494589356aee5435c8dc0f99aa4f8d9f8b3694bf.

Known references now reject raw Unicode Cc/Cf/Cs before trimming/URL construction, reject malformed explicit HTTP(S) prefixes before bare-domain fallback, and reject raw authority @ even with empty parsed username/password. Normal astral pairs are not Cs under Unicode-mode property matching and remain accepted in paths. Valid IDNA, bare domains, complete schemes and ordinary surrounding spaces remain supported. Fixed errors never echo input.

For message extraction, raw formatted/control/surrogate tokens use the existing unreadable row and null comparison path. The literal-token regex now explicitly retains Cf characters even when JavaScript also classifies them as whitespace, notably U+FEFF; without this, an embedded format character would truncate a token into a different hostname before validation. Ordinary whitespace/hard lines remain delimiters; no message lines are joined or stripped. Later normal URLs are still processed, all literal candidates are counted and only first12 inspected.

Browser numeric canonicalization deliberately remains unchanged: short/radix/octal spellings still resolve to their accurate browser destination and compare as before. This is a policy distinction from desktop canonical-only admission, not a failed fix. Root adds the explicit normalization disclosure. Escaped host spelling likewise remains browser normalization outside the selected scope. No hostname match authenticates identity or safety.

Fifteen dedicated tests: pre-fix8failed/7passed; final15pass. Combined dedicated, existing Pocket compare/coverage and desktop manual-guidance privacy tests:27passed in157.9ms (green-tests.txt). Cases cover malformed reference syntax, Cc/Cf/Cs raw rejection, empty/nonempty userinfo, hidden token unreadability/later normal URL, Unicode IDNA/astral pairs, unchanged numeric policy,30k/4096 bounds, bounded first12 coverage, message-userinfo destination and fixed topic-only exports. A test expansion added a second malformed FEFF token to the14-token coverage fixture; its remaining count was corrected to2, preserving the twelve inspected limit.

Main desktop manual rendering/copy/download still call only nextSteps/summary with selected topics; neither function was edited. Public API shapes items/remaining/known/rows and null/unreadable semantics remain unchanged. No source navigation/fetch or external content transfer is performed.

Tests establish local pure/controller behavior, not physical Android/iPhone operation, browser installation/cache readiness or overall URL/parser equivalence. URLs containing ordinary whitespace delimiters are still extracted as literal text tokens; this is not a browser hyperlink reconstruction engine. Root should preserve the v16 package, regenerate the live index and verify its v12 cache fixtures separately.

## Fresh read-only review after integration

Ran independent local probes without changing guide/tests/cache/archive. Null/object known references and null/array message inputs fail with fixed messages, without coercing user objects. Exact4,096-unit reference accepted;4,097 rejected. A30,000-unit literal URL remained bounded and returned hostname only. Private path/query markers in both message/reference were absent from returned comparison objects. Authority @ detection does not reject an @ occurring only in a path. Explicit port443 remains supported.

A valid astral path and case-mapped Deseret astral IDNA host remain accepted; Unicode-mode Cs checking does not reject valid surrogate pairs. Raw NUL and FEFF tokens become unreadable while a later normal URL is still inspected. Ordinary tab/newline delimiters still yield two separate normal addresses and are not joined. Cf retention in the token regex is necessary for FEFF specifically, because it is otherwise JavaScript whitespace; it does not authorize treating all whitespace as part of a URL. The checker remains literal-token extraction, not hyperlink reconstruction.

The regenerated static/index.html contains the exact current guide source (after line-ending normalization). Desktop manual selected-topic nextSteps/summary paths remain unchanged; they do not call the hostname comparator with private message content. No new regression was found in the authorized HTTP(S)/raw-character/userinfo slice.

One preexisting out-of-scope residual was reproduced: a malformed non-HTTP reference ftp:/example.com is still prefixed as a bare reference, producing known hostname ftp and matching https://ftp/. Proper ftp://example.com is rejected. The selected new prefix guard intentionally covers explicit HTTP(S) only; it did not introduce this older fallback behavior. Root was notified to decide whether a broader unsupported-scheme boundary belongs in a separate reviewed slice. No guide mutation was made during this review.

Root reports a native cached-offline v12 check rejected malformed https:/example and Clear erased both known/message fields. That is root's browser observation, separate from these worker pure probes. Root's next v13 package includes unrelated expanded Practice; this review does not claim that future cache/package has been tested. Frozen v16 archive and original22-case before outputs remain untouched.

## Malformed non-HTTP scheme residual closure

Root authorized one additional generic boundary guard after the existing explicit HTTP(S) guard. A scheme-shaped prefix without :// is rejected unless it has the admitted bare-host decimal-port shape. This closes ftp:/, file:/, foo:/ and empty ftp: fallback without a protocol-name blocklist or normalization. Proper unsupported protocols still fail the existing HTTP(S) check.

New tests/pocket_scheme_boundaries.test.cjs was written first:4failed/6passed before the guard. Final dedicated/boundary/compare/coverage/desktop-manual run:37passed in206.6ms (scheme-green-tests.txt). Bare example.com:8080 and intranet:8080, path/query/fragment suffixes, path-only colon, bracketed IPv6 and fixed topic-only exports remain supported. Errors use the existing fixed catch and omit input.

Ambiguous ftp:80 is deliberately interpreted as hostname ftp with decimal port80, not as an FTP URL; the explicit test records that policy. Existing reserved HTTP(S) prefix handling still rejects http:80/https:80 before the generic port exception. This is a bounded reference admission rule, not a claim to infer the user's intended URI scheme. No hostname match establishes ownership or safety.

Only guide.js and the new dedicated test changed as app/test source for this closure. Original22-case before outputs and v16 archive remain unchanged. The earlier root v12 cached browser observation remains historical; root owns regeneration and final v13 cache/browser verification. Current guide SHA256: c63d16fdd33179199e826daa20947592cf343286401d90baf87aa444ff2b2208.
