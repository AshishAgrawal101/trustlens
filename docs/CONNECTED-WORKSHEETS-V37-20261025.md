# Connected worksheets without saved drafts v37

The suggested next tool now opens separately when that preserves useful work. Quote, Numbers and Media each offer **Open Claim & context (new tab)**. Claim offers **Open other tools (new tab)** near its introduction. The current worksheet remains open rather than navigating away and triggering its intentional privacy reset.

These are ordinary fixed internal links with visible new-tab labels and `noopener`. No input is copied between pages, put into an address, saved, sent to a server or made available through an opener channel. Unrelated Home/Back/footer navigation stays unchanged. Return through the browser's tab controls and clear each worksheet when finished. Closing, reloading or leaving a worksheet clears its entries; an open background tab can also be discarded by the browser. This is not recoverable saved work or a guarantee of preservation.

Pocket uses its canonical cached Claim page and context guide, with the appropriate **Open context guide (new tab)** label. Media remains desktop-only. No controller, detector, validator, model or stylesheet changed in this slice.

## Verification

- Source: **1,594 Python and 596 JavaScript tests passed, zero failures or skips**, including configured native Windows OCR and local signing checks. Seven focused markup/render checks were added before implementation; existing assertions needed no changes.
- Independent review verified four fixed, labelled separate-tab actions, unchanged ordinary navigation, exact Pocket rewriting and all five relevant controllers byte-identical to v36.
- Actual desktop browser at 320 pixels: keyboard-opening Claim from Numbers preserved the original values and comparison; the child Claim was blank. Opening Tools from a populated/reviewed Claim kept that worksheet intact. Opening Claim from a completed quotation comparison preserved both versions and the diff, with a blank child. Clear/reload removed inputs and results. Client and scroll widths matched at 305 pixels.
- Standalone Pocket v37/cache v31: all 29 shell paths returned HTTP 200 with matching hashes; all 31 manifest files matched. After the owned server stopped, keyboard-opening cached Numbers → Claim → guide in separate tabs worked, original worksheets remained intact and the child Claim had no transferred input. Each worksheet cleared/reloaded empty at 320 pixels. This is desktop-browser offline evidence, not a physical phone test.

Evidence: `verification/connected-workflow-v37-20261025/`, `verification/v37-independent-connected-20261025/` and `verification/v37-root-browser-20261025/`. The initial root quotation harness compared JSON property order; comparing the actual fields confirmed no data changed. No product fix was needed for that harness assertion. Foreground-tab selection, browser discard and physical-phone behavior were not established by these observations. Media's file workflow was not browser-uploaded.

Preservation checks verified 55 earlier source/phone artifacts, 104 original files and 34 protected files relative to v33 unchanged. The matching external source receipt records current archive/extracted hashes and tests after completion. No new model release, real-world accuracy, user-study outcome, recording, publication or challenge submission is claimed.
