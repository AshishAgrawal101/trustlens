# Independent Numbers swap review

swap-review-acceptance.json frozen before reading implementation/tests. No new bug found. Compared current pure module prefix against immutable v28 ZIP: exact normalized bytes, SHA256 e312090ebb047a26eae20adebdb495f0757db350ee6c06c248cc094de021c828. Both mathematical methods and their contracts remain unchanged.

Swap preserves active raw string pairs only, including reported-percentage precision/edge spaces and count leading zeroes. Hidden inactive drafts are not swapped. It invalidates facts and clears previous errors before changing inputs, never calculates automatically, and requires explicit Compare. Baseline reversal is honestly described: 20/100 versus 30/200 yields -25%; swapping and explicitly comparing yields about 33.3333%. Zero baseline policy is preserved. Double swap restores exact strings.

Native badInput is checked before assigning any value, so browser-retained incomplete number buffers are not erased by assignment. If every active value is empty, Swap is disabled; this also avoids touching an unreadable incomplete buffer. Normal edits, Clear, method change, examples and lifecycle boundaries reset status/readiness consistently. Status is fixed, input-free text; no new requests, storage, clipboard or downloads.

Independent focused execution: 31 Numbers controller/swap and frozen reported-percentage oracle tests pass, zero failures/skips. Root separately owns real browser badInput/mobile evidence; this audit used code, DOM doubles and immutable ZIP comparison only. No source changes by reviewer.
