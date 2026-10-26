# Native OCR line-wrap failure — read-only reproduction

Two constructed 900×200 PNGs contain exactly the same request, rendered with Arial 44. One has “Send us the verification code.” on one line; the other places a line break after the word “the”. The fixtures, desired request-warning expectation, source pins and two-call native-OCR budget were frozen before outputs in line-wrap-protocol.json, SHA256 534638307c824bbbe11be3af8e84877d6de9f6e3a51906543fc1fe19f8815dba. No source images, user/private content, finals or Arena data were read.

Actual production extract_screenshot invoked the installed Windows English OCR. Both returned the intended words correctly, with review_required=true. Single-line OCR took 0.653 seconds and the ordinary downstream text analyzer emitted request:code/high. Wrapped OCR took 0.578 seconds, retained its newline and emitted text:none/low with the generic no-warning headline. No OCR recognition error explains the difference: the shared request matcher treats newline as a sentence boundary, splitting the verb from its object.

line-wrap-results.json retains exact constructed outputs and both outcomes. This is one paired software-layout reproduction, not a scam-accuracy benchmark. The runtime-loading function was replaced with an assertion guard in the audit process; no image-model inference, GPU, download or application-source edit occurred. Native OCR was the only native extraction work performed, under the existing 30-second per-call timeout.

Proposed scope sent to root before editing: review layout-whitespace handling at the shared request-evidence boundary, retaining original editable OCR line breaks and adding wrapped request, wrapped negation/advice and unrelated-line controls. A blanket newline join can change clause scope, so that choice needs its own paired regressions. No change is approved or applied in this audit. Do not change model runtime, weights or thresholds, or tune on sealed/final data.

Separate preservation.json rehashes all nine immutable source review archives, including v7 e9c6cfc857e78fba5971ec54e9300fbaf442eb6aabe873870662a643b1aadb61, plus 104 original-source entries and all 34 protected files relative to the current v7 manifest. All matched. The approved earlier input-decoder fix is part of that v7 baseline; this audit makes no new protected-source exception.

Skipped: phone work, publication, screenshot browser file selection, visual inference, broader fuzzing and source edits.
Risk: an accurately recognized wrapped request can currently miss a warning; mandatory review remains necessary and does not automatically repair layout-sensitive matching.

