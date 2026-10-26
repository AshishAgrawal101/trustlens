# Useful local improvements — historical wave

Superseded by [the intake/reliability handoff](INTAKE-RELIABILITY-20261023.md). Counts below describe this earlier archive.

This version adds an exact-hostname comparison, selectable Pocket recovery checklists, and honest reporting when communication inputs exceed the link-inspection bound. Two reused subagents implemented/reviewed bounded parts; root integrated, tested and verified the browser behavior. Earlier archives and the frozen entry remain unchanged.

## What changed for users

**Known-site comparison:** after showing Pocket next steps, expand “Compare with a website you already know.” Enter a known official website or hostname. Up to twelve literal HTTP(S) addresses are compared on-device by exact parsed hostname. Subdomains and suffix/lookalike hosts do not inherit a match. Text before @ does not become the destination. A same-host result explicitly does not establish safety; a difference can have legitimate explanations. No supplied site is visited or authenticated. Paths, ports and query parameters are not compared. Invalid reference schemes, credentials/@, backslashes and spaces are rejected. The typed reference and comparison are excluded from action exports and erased by Clear/page exit.

**Selectable recovery:** Pocket now offers money, code/password, device-access and opened-link choices. Only the chosen two-step checklist is shown and its heading receives focus. Copy/download contain fixed existing guidance and the FTC source, not the message, hostname comparison or incident details. Pending clipboard operations are tied to the selected checklist; Clear/page exit invalidate them. This is general U.S. English guidance, not a recovery service, and recovery is not guaranteed.

**Incomplete link coverage:** Message, Call and Email still inspect only the first eight unique literal HTTP(S) matches. Larger inputs now receive count-only unknown evidence, an explicit summary/limitation, a “CHECK INCOMPLETE” tag and a link-review action. The input-free share summary preserves the incomplete notice. No warning is fabricated about an unexamined ninth link. When an actual high warning is present among inspected links, the heading remains urgent: “Pause; some links remain unchecked.” The literal-uniqueness rule is before trailing punctuation trimming, not a count of canonical destination websites.

## Evidence

486 Python tests passed, zero skips, including native OCR and C2PA cryptographic fixtures. 51 JavaScript tests passed, including exact-host/suffix/IDN/userinfo behavior, invalidation, fixed recovery exports, stale completion and bounded-link presentation. A final eight-case targeted link/export rerun passed after count wording was clarified. These are implementation checks, not real-world accuracy or a new detector benchmark.

Ordinary Edge browser control verified nine-link incomplete reporting, then Pocket mismatch and same-host output with explicit limits. With the local server deliberately stopped, exact-host comparison and the selected payment recovery checklist worked. Clear removed the message/topics/result/recovery selection, and offline reload returned an empty guide. At 320 pixels there was no document horizontal overflow; selecting account recovery focused its heading. The viewport was restored and the server restarted afterward. Screenshot: `verification/pocket-recovery/browser-recovery.png`. It contains only a constructed example. Final independent review identified the high-warning/overflow precedence issue, which root corrected and covered with a controller regression.

## Limits and preserved boundaries

Pocket is a human-guided checklist; its reference domain is supplied by the user and not independently verified. Exact hostname equality cannot establish authenticity, ownership, reputation or transaction safety. The twelve-address display/comparison bound and eight-link desktop inspection bound remain visible. Hidden links, redirects and omitted content remain unresolved.

No new model, image inference retry, payload download, GPU job, final/Arena access, cloud content analysis, automation resume or publication occurred. The previous real-image C2PA results and visual-model RAM stop remain historical evidence under their pinned versions. Physical Android installation/share sheet, browser file uploads, full assistive-technology testing and clean-machine installation remain unverified.

The current source runs at http://127.0.0.1:8766/ and Pocket at `/phone/` while its launcher is running. The new review ZIP has its own manifest/checksum receipt and is not an entry replacement. All earlier archives, original live source, trained runtime, cryptographic behavior and trust store are preserved.
