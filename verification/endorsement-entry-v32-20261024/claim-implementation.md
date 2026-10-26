# Constructed endorsement entry

Changed only `static/claim-review.js`, `static/claim-review.html` and new `tests/claim_endorsement_example.test.cjs`. No shared fixture or existing-test change was needed. Root owns guide links, renderer, cache, export and packaging.

The existing example controls now include **An endorsement**. Adjacent fixed help explains that examples replace the entire worksheet and require Review separately. The example supplies only `These headphones last twice as long.` and clearly constructed sponsored-post context identifying missing comparison model/settings and independent results. It invents no source accounts, dates or evidence labels. Existing clear/populate logic erases previous private fields/results/export state, leaves empty Sources closed and focuses Claim.

The exact consumed fragment allowlist adds only literal `endorsement`; routing still invokes the normal example button and removes the fragment without putting fields in history. Existing caption/headline definitions and pure review/PLAN code remain unchanged (`claim-preservation.json`). Explicit Review still yields the existing no-source observation and generic next step, not an automatic endorsement finding.

TDD evidence: `claim-red.txt` captured missing-button/routing/replacement failures before edits; `claim-green.txt` has 9/9 route/new regression passes. `claim-integration.txt` has 103/103 Claim tests passing, zero failures/skips. Coverage includes button/startup/hashchange replacement, all private source/date/role resets, pending clipboard generation guard, strict malformed/private fragment rejection, explicit Review, consumed Pocket path, Clear/reload and lifecycle erasure. No new network, storage or export behavior.

Actual guide-link browser navigation and refreshed offline export are integration-owner evidence, not established by these controller tests. Physical-phone use and real endorsement conclusions remain unverified.
