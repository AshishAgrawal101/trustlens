# Pocket hostname boundary audit — read-only

Twenty-two fresh cases frozen before current execution: frozen-cases.json SHA256 31d805f9c310e3c625e7573825ea980ef9b3a393f3743deabf3aa1a4500f3693. pocket-before.json retains compareHosts and hostCoverage outputs; desktop-before.json retains current parse_address behavior and known-reference userinfo rejection. Both source hashes are recorded. No app file or frozen v16 archive changed; no navigation, URL fetch, DNS resolution, phone setup or uploads occurred.

## P2: malformed explicit known schemes become a different reference

Known https:/example.com is accepted as hostname “https” because compareHosts only looks for :// before deciding to prepend https://. Against a normal example.com message it reports a different host; against a literal https://https/page it reports a matching host. This is a constructed reference created from malformed input, not the intended example.com. Extra-slash https:///example.com and https:////example.com are also accepted and normalized to example.com. Current desktop rejects all these explicit malformed HTTP(S) forms before parsing.

Smallest candidate: before bare-host fallback, reject explicit http:/https: prefixes unless they match the existing desktop complete-authority boundary (two slashes followed by an actual non-slash/non-query/non-fragment authority character). Do not silently repair or prefix a malformed explicit HTTP(S) URL. Pair bare domain, valid scheme, port, case and IPv6 controls. This is the highest-value direct correctness gap; no new host identity verification should be claimed.

## P2: raw hidden formatting and userinfo boundaries are not preserved

Known exa<U+00AD>mple.com and exa<U+200B>mple.com compare as example.com, as do the same literal message hosts. A U+202E character in a path is accepted for both known/message addresses. A leading tab in known is removed before the check; desktop checks raw Cc/Cf/Cs before stripping and rejects each case. Pocket raw URL processing currently normalizes away or accepts formatting without showing a notice. The existing IDN note does not cover these discarded controls.

Known https://@example.com also passes because username/password strings are empty; desktop's reference check rejects the presence of userinfo syntax even when empty. A percent-escaped host is normalized to a match in Pocket while desktop rejects escaped host syntax. Browser normalization is not intrinsically a malicious destination change, but these differences defeat a promise that the supplied literal spelling was checked under the desktop boundary policy.

Candidate scope: validate raw known/reference and each extracted literal URL for hidden control/format/surrogate categories before trimming or URL construction. Invalid reference should produce a fixed error; invalid extracted address should remain an unreadable/null-comparison row so coverage is not silently lost. Reject userinfo syntax in known authority even when parsed credentials are empty. Keep message userinfo's actual destination/notes control working. Do not normalize the private text or strip controls to obtain a matching hostname.

## P2 policy difference: numeric canonicalization is implicit

Known 127.1,0x7f000001 and0177.0.0.1 all become127.0.0.1 and compare true against canonical127.0.0.1; a message containing127.1 does likewise. Desktop intentionally rejects these noncanonical/radix spellings. The browser's canonical destination here is accurate, so this is not evidence that WHATWG sends to the wrong host. The issue is an undisclosed spelling transformation and cross-tool inconsistency, especially if results are described as exact parsed hostname comparison.

If root selects parity, require canonical literal IP spelling or mark shorthand unreadable before giving a match. Keep ordinary canonical IPv4, bracketed IPv6 and valid nontransitional IDNA controls. Do not implement a broad numeric/DNS rewriter or claim matching an IP authenticates an organization. Deriving the original authority must account for userinfo, brackets and ports; this needs paired tests rather than comparing the whole URL to url.hostname.

## Working controls and bounded coverage

Canonical example.com, canonical127.0.0.1 and faß.de/nontransitional punycode controls compare true. Userinfo in a message correctly resolves to the host after @ and compares false against the bait domain. A legitimate subdomain compares different, as documented. hostCoverage still counts all literal regex matches and parses only the first12, preserving remaining counts; this audit does not propose fetching additional links or changing those limits. No ownership, fraud or safety conclusion follows from either match or mismatch.

## Shared desktop manual-guidance callers

Inspected app.js manual-form rendering, manual-copy and manual-download: they call only PocketGuide.nextSteps(selected topics) and fixed PocketGuide.summary(selected topics). They do not pass message text or known-host values into compareHosts/hostCoverage. Thus these Pocket host-boundary gaps do not alter the main desktop automatic URL parser or its user-selected guidance/actions/exports. Pocket's own phone.js uses hostCoverage; phone/compare.js uses compareHosts and renders fixed match caveats. A future shared-guide fix must leave nextSteps/summary byte behavior intact and rerun manual-guidance privacy tests. The generated static/index.html embeds the shared guide; root should regenerate it if source guide changes, rather than editing the frozen archive.

## Limits and priorities

No source edit is proposed without root choosing exact scope. Prioritize explicit malformed known schemes and raw formatting/reference-boundary validation; numeric spelling policy is a separate explicit choice. Full JS URL/IDNA and Python policy equivalence is not established by these22 probes. Existing safety caveats reduce interpretation risk but do not fix incorrect reference parsing. These are targeted constructed comparisons, not real-user prevalence or accuracy measurements.
