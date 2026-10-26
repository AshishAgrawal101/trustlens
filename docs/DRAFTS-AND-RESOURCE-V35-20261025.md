# Separate number drafts and bounded Media processing v35

Switching Numbers input methods now keeps separate raw counts and reported-percentage entries on the current page. It clears the previous result, disables the inactive fields, does not convert values and requires an explicit comparison. Clear, a constructed example and leaving/restoring the page still wipe both drafts. There is no history or persistent storage. The pure arithmetic and active-method Swap code are unchanged.

Media file inspection now admits one operation at a time in this server process, before decoding and through metadata inspection. Another operation receives a fixed busy response and retry guidance while its draft remains available. The lock releases on success and failure. Existing validation, decoder, metadata schema and image models remain unchanged. This guard bounds concurrent Media processing only; it does not cap aggregate multipart upload buffers, serialize other tools or terminate work when the browser stops waiting.

## Verification

- Source: **1,560 Python and 593 JavaScript tests passed, zero failures or skips**, with configured native Windows OCR and local signing environment.
- Independent reviews checked both changes against immutable v34. Numbers arithmetic/Swap are byte-identical; Media's prior inspection body is unchanged behind the admission guard.
- Actual desktop browser: constructed counts and precise percentage strings survive both method round trips; prior results disappear; explicit comparisons remain correct. Clear/reload wipes all six fields. At 320 pixels client and scroll widths were both 305 pixels.
- Actual standalone Pocket v35/cache v30: all 29 shell paths returned HTTP 200 with matching hashes; all 31 manifest files matched. After the owned server was stopped, the cached guide and Numbers worksheet supported both methods, retained separate drafts, compared explicitly and cleared/reloaded to empty fields at 320 pixels. This is desktop-browser offline evidence, not a physical iPhone test.
- Tiny constructed image concurrency tests confirmed the second Media operation is rejected before decoding, retry works, failure releases the lock and the upload closes before a busy response. No large-image stress, OOM, browser upload or model inference result is claimed.

Evidence: `verification/next-workflow-v35-20261025/`, `verification/next-resource-v35-20261025/`, `verification/v35-independent-numbers-20261025/`, `verification/v35-independent-media-20261025/` and `verification/v35-root-browser-20261025/`. The fresh input-parser audit in `verification/next-input-audit-v35-20261025/` found no new defect in its eight predeclared cases; it made no rule changes.

Preservation checks verified all 52 prior source/phone artifacts, 104 original files and 34 protected files relative to v33 unchanged. The matching external source receipt records current archive hashes and fresh extracted-suite results when completed. Earlier measured limitations remain preserved. Physical phone work is deferred; browser file upload remains unperformed. No new model release, real-world accuracy, human-study outcome, recording, publication or challenge submission is established.
