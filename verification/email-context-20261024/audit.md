# Read-only email boundary audit

Tiny constructed strings/bytes only. No remote/private files, attachments executed/decoded, downloads, models or app edits. Process-local ASGI requests used the real current app with raise_app_exceptions=False to observe actual status codes.

## Confirmed P2: malformed address headers cause500

`From: "\r\n\r\nOrdinary meeting notes.` causes IndexError from stdlib lazy header parsing in message.get_all during analyze_message. `Reply-To: a@[\r\n\r\nOrdinary meeting notes.` causes AttributeError involving InvalidHeaderDefect.all_defects. Both failure families also reproduce with the other address header name. These are not simply unavailable source material: `/api/analyze/email` and `/api/analyze/email-file` both returned500 Internal Server Error for each of the two representative inputs. Existing wrappers catch RecursionError/HeaderParseError, but not these parser failures. Source bytes are well below all limits and contain no NUL or attachment.

Recommendation: root-select a narrow parser-boundary normalization for these known stdlib failure classes in both shared entrypoints, returning the existing fixed actionable ValueError/400 without raw input/exception echo. Do not blindly suppress arbitrary analyzer errors into clean reports. Preserve readable-body warnings only if an explicit guarded/incomplete fallback is designed; fixed400 is the smaller fail-closed correction. Paired regressions should use string andbyte entrypoints and both actual routes, retain normal From/Reply-To behavior and malformed/deepMIME tests. No change made before root approval.

## Lower priority literal-label scope issue

HTML `<a href="https://evil.example">https://bank.<br>example</a>` and the same label split by `<div>example</div>` produce verified email:link_mismatch evidence stating displayed host bank.example. VisibleText inserts hard boundaries in body text for these tags, but its anchor-label accumulator concatenates only handle_data, reconstructing a URL across those boundaries. The host comparison is therefore not strictly a comparison of one literal rendered address. This does not visit a link and the warning caveat remains useful, but the verified displayed-host detail is stronger than the parser observed. Recommend preserve hard boundaries in anchor-label text as well, so only actual contiguous address-like labels yield a host claim. Adjacent inline emphasis should remain joinable. No claim is made about full browser CSS rendering or malicious intent.

## Other reviewed limits

Body parsing skips explicit attached-message subtrees; unscanned-part inventory reads MIME metadata only and reports incomplete when no readable body exists. Copied authentication headers stay unknown, notverified; link destinations are never fetched. Byte input is capped250000 and NUL-rejected, declared encoding errors produce incomplete context, and filenames/attachment bodies are not evidence. Mailto scope explicitly limits primary recipient domains and excludes query recipients/ownership; these limitations must remain. Unsupported content and missing metadata are not fraud evidence.

A small header matrix covered7headernames×17malformed/specialvalues and identified the two exception families above. This is a targeted diagnostic, not a parser fuzzing completeness or security guarantee. Existing focused email suites were run separately; their pass does not cover the newly reproduced negative cases. Root prioritizes any app changes; this audit owns only this note.

Additional same-family reproduction: HTML mailto comparison with label `a@[` and valid href `mailto:a@example.org`, or valid displayed mailbox and href `mailto:a@[`, raises the same AttributeError from Address parsing. Shared entrypoint fail-closed normalization must cover lazy header parsing and link-label parsing, or narrower local catches must cover both. Existing5focused email suites passed86tests,zero skips; these new cases remain failing and unpatched.
