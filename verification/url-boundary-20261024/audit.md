# URL boundary audit

Read-only app audit with tiny constructed strings and local Node WHATWG URL comparisons. No navigation, DNS, HTTP fetch, private input, model, browser upload or app edits. Inspected parse_address/analyze_url callers in URL anatomy, email labels and text link extraction; existing IDNA/numeric/hidden-character tests reviewed. Constructed actual results are in constructed-results.json.

## P2: malformed explicit scheme becomes a false verified host

`analyze_url('https:/example.org/path')` returns low with verified url:host detail `https`. `http:/example.org` similarly reports `http`. The missing `://` causes the parser to prepend https:// to the whole string, treating the supplied protocol as a hostname. Node's actual WHATWG URL constructor canonicalizes these explicit schemes to host example.org. Unlike a legitimately omitted scheme, this is malformed explicit scheme syntax; reporting “The address points to this host” as verified is misleading. Recommend reject explicit HTTP(S) protocol spellings without a complete authority prefix before applying the scheme-omission convenience. Preserve ordinary scheme-less domains and explicit valid addresses. Add direct/helper/API/known-reference pairs; no network required.

## P2: noncanonical numeric host interpreted as ordinary domain

`https://0x7f000001/` and `https://0x7f.0.0.1/` return low with verified hosts `0x7f000001` and `0x7f.0.0.1`, omitting the numeric-IP clue. WHATWG URL canonicalizes both to127.0.0.1. `https://example.0x1/` is accepted locally but WHATWG rejects it as an invalid numeric-ending host. Existing all-decimal rejection prevents octal0177.0.0.1, but not hexadecimal forms. This affects exact reference comparisons and claimed-host evidence. Recommend conservatively reject noncanonical web numeric-host spellings rather than pretend these are verified DNS hosts; preserve canonical IPv4/IPv6 and accepted normal hostname policy. Implement any WHATWG-ending-number detection carefully, with hex/decimal/octal/invalidnumeric and ordinary IDNA-domain controls, without adding DNS.

QR dispatch does not fetch URLs: it extracts text for review, then submits to analyze_text only after explicit confirmation. Nevertheless, confirmed reviewed text containing https://0x7f000001/ produces the same verified `url:host:0` detail, so this shared parser issue propagates to QR, screenshot/message text and HTML link labels. Direct malformed single-slash links are outside the HTTP(S)literal extractor pattern; direct Link mode still accepts them as above. Origin scores and signed provenance do not participate.

## Other observations and limits

Current stdlib rejects bracket-junk IPv6 authorities (`[::1]suffix`) before host evidence; no500 found there. Cc/Cf/Cs and backslash/space controls are rejected, including bidi/ZWJ in paths, so they cannot silently disappear before validation. Scoped IPv6 `[fe80::1%25eth0]` is accepted as a Python IP literal but rejected by WHATWG; this is an additional compatibility limit worth rejecting for ordinary web-address input if root selects the numeric-host correction. It does not cause a network lookup here. Ports0/normalports remain literal, with ordinary invalid port handling.

The URL anatomy notice already says it is not browser validation, but the core report's verified destination-host title is stronger than these inputs support. No release/privacy/network threat claim is inferred from this offline diagnostic. Existing focused IDNA, URL anatomy and link-evidence tests pass; the new cases are not yet regressions in app source. Root selects fixes before edits.
