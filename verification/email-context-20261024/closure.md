# Email parser and label-boundary closure

Root authorized the minimal email.py fix after the read-only audit. Inspected production callers in main.py/intake.py and existing email/header/link/MIME tests first. No endpoint, MIME-role, attachment, byte-limit, authentication, URL-policy or model changes.

Both public string/byte parsing entrypoints now normalize known stdlib IndexError/AttributeError parser failures alongside existing HeaderParseError/RecursionError into their existing fixed actionable ValueError. Actual routes therefore return400 without raw exception/input echo. Local mailto label parsing also skips those malformed Address failures, preserving readable-body warnings rather than rejecting an otherwise usable message. No malformed label becomes evidence of fraud.

VisibleText now mirrors its existing block/br newline boundaries into anchor-label text. It no longer creates a contiguous displayed hostname from bank.<br>example or block-split labels. Inline spans/strong labels remain contiguous and still compare. Body text handling, URL destinations and existing declared link limitations remain unchanged.

Eighteen new tests ran before implementation:17failed,1passed. They now all pass, covering both header names/failurefamilies, string/byte entrypoints, both real ASGI routes, malformed mailto/readablewarning pairs, block/br labels and valid inline/normal sender controls. Combined meaningful email/file-intake/community suites:166passed,zero skips in6.35seconds. No native model, remote/private data, attachment execution or downloads occurred. Only email.py and the dedicated regression test were changed in app/test scope; this audit closure records results.
