# Actual device and voluntary usability protocol

**Status: protocol only. No physical-phone session or human usability session is claimed.** The user confirms Illinois District 11 and an iPhone; model/iOS version and actual residence/school eligibility are unverified. Android hardware availability is unknown. Desktop browser/controller tests, including an emulated narrow viewport, are not substitutes for either device. Keep this blank until someone actually performs a step.

## Preparation and privacy

Record build/archive digest, date, device model, OS/browser version, network condition and the exact approved origin. Use only constructed text, `static/demo-message.png`, `static/demo-qr.png` and `static/demo-email.eml`; do not collect passwords, live codes, account details, personal messages or real incidents. If a participant volunteers private material, stop and replace it with a constructed example. Disable unrelated notification previews for any separately consented recording. Do not record by default.

For U5, prepare a separate synthetic attachment-only `.eml` in a normal mail composer with a benign text attachment and no message body, then observe the actual desktop result before the session. If that fixture or the optional image-component result is unavailable, mark the relevant part not run; do not fabricate a screenshot or verdict. Do not use an actual inbox message.

Pocket needs a trusted reachable secure origin for phone/offline installation work. `[APPROVED HTTPS POCKET URL]` is not yet supplied. A separate static Pocket device bundle is being prepared by root; it has not been deployed and supplies no phone-execution evidence. A phone's `127.0.0.1` is the phone, not this computer. Do not expose the Windows backend to the LAN or publicly deploy it to manufacture a pass. If no separately approved setup exists, mark phone install/offline/share tasks **BLOCKED**; test only the already accessible desktop workflow. This document authorizes no hosting, publication, contact or permission bypass.

For clipboard/share tests, ask the device owner first and use synthetic content. Inspect preview only; cancel external sending. Clear Pocket afterward and remove the synthetic clipboard value using the device owner's normal controls. Pocket cannot erase system clipboard, Photos, other apps, cloud synchronization or external copies. Test notes must not imply otherwise.

## Device tasks and expected observations

Run one iPhone session first. Repeat applicable tasks on an actual Android device if one is later available; leave Android untested otherwise. A fallback is recorded separately and cannot be counted as success of an unavailable platform capability.

| ID | Device task | Pass criterion / failure record |
|---|---|---|
| D1 | On iPhone Safari, open the approved static Pocket origin; record whether installation/Home Screen controls are actually offered | Page readable, usable controls; record real install option and launch behavior. No option or origin: blocked/unsupported, not a fabricated install |
| D2 | Paste a constructed code request manually; select the matching checklist topic, then explicitly choose **Show safer next steps** | No automatic analysis, no destination opens; guidance appears only after explicit choices; explain manual checklist scope |
| D3 | Try the optional explicit Paste control; deny permission or observe a real unavailable state | Manual paste remains possible, error is understandable, draft is not replaced by stale clipboard completion |
| D4 | If using the optional manually built iOS Shortcut, record each actual action and whether it opens Safari or Home Screen view | Fixed trusted URL only; no message in URL/query/fragment. If unsupported, record that and retain manual copy/paste. No native Share Extension claim |
| D5 | Prepare the actual view online using its offline-preparation control, then use airplane mode/offline and reload | Static checklist, practice and Clear work in the prepared view. Record whether external help fails gracefully; a successful desktop test is not a phone pass |
| D6 | With synthetic content/results present, Clear; close/reopen and reload prepared view offline | Draft, selected topics and result are empty. Record remaining OS clipboard separately, not as Pocket storage |
| D7 | On actual Android Chrome, if available, test install and the OS's offered text-sharing path | Record offered behavior and actual receiver result; explicit review required, no automatic content analysis or URL persistence. Unsupported/no hardware stays untested |
| D8 | Actual phone portrait/landscape, enlarged text, keyboard, VoiceOver or TalkBack if available | No clipped essential controls, focus remains understandable, labels/readout meaningful; record exact failures and assistance, not “accessible” from viewport screenshots |
| D9 | On desktop with installed components, manually choose the provided image/QR/email fixtures using the ordinary file picker | Screenshot/QR extraction remains review-first; email states attachment limits. Selection denial is a limitation, never bypassed. No visual-model retry required |
| D10 | Stop/unavailable-server rehearsal with a synthetic draft; retry after restoring it | Honest error, no stale result/export, draft retained, controls recover. Do not interrupt unrelated work or leave server stopped |

Do not enable notification/SMS monitoring, automatic calls, background message access or financial transactions. They are outside the app's implemented scope.

Pocket's main submit action is **Show safer next steps**. Apply controls belong only to its separate optional topic-suggestion helper. Record those as distinct actions rather than conflating topic suggestions with the checklist submission.

For the desktop verification-plan check, run a constructed Message example, choose **A number I already trust**, and inspect **Copy plan** / **Download plan** only with the device owner's permission. Pass means fixed input-free steps and a clear user-selected/not-completed-verification label; no call, contact, original wording or contact detail is sent. Clear/change input and confirm that an old plan cannot be exported. This is not Pocket's main submit action and is not actual verification.

The browser screenshot file-selection clip remains **Not recorded** after an automated-review permission block. The user may perform ordinary manual selection later; an API fixture pass or pasted fallback is not a successful browser upload. Record this distinction in D9.

## Voluntary human session — 10–15 minutes

Aim for 3–5 consenting adults with varied comfort using phones; this is a practical target, not completed recruitment or a representative sample. Obtain permission before approaching any school/minor participant and follow the responsible adult/institution's consent requirements; do not recruit minors by default. Use P01/P02-style codes, not names, in notes. No compensation or benefit is promised here.

Recruitment wording for the user to deliver; **not sent**:

> Would you volunteer about fifteen minutes to try a local safety prototype using made-up messages? I am testing the app, not you. You can skip a question or stop at any time. Please do not share private messages, passwords or financial information. With your permission I will keep anonymous task notes, without recording audio/video or your identity. The app can be wrong and is not a professional fraud service. Would you like to participate?

Before starting, separately ask permission for anonymous notes and any optional recording; declining recording does not prevent participation. Offer a no-notes walkthrough. Keep consent records apart from task notes if needed. Allow withdrawal by participant code until the stated review date: [DATE]. Planned raw-note deletion date: [DATE, preferably within seven days after review]; retain only necessary anonymous aggregate counts after that. Do not publish a quote or image without separate consent.

Use the same five tasks, alternating the first two tasks' order between participants. Ask what they would do before showing advice; then let them use the app without coaching. After a first attempt, assistance is allowed but recorded separately. Do not count assisted recovery as an unassisted pass.

| Task | Constructed input / instruction | Observable success |
|---|---|---|
| U1 | “Send us the verification code immediately. Do not call your bank.” | Identifies the requested code and chooses an independently known contact; does not send a code |
| U2 | “Your one-time code is 123456. Do not share it with anyone.” | Distinguishes a notification/advice from a request; explains that no warning does not prove the sender safe |
| U3 | `https://bank.example@actual.example/confirm` | Identifies actual.example as the host; does not open it; does not treat exact-host equality or HTTPS as ownership proof |
| U4 | Pocket: paste text, choose a relevant topic, **Show safer next steps**; then Clear | Understands this is a manual guide; completes the steps, sees fixed advice and clears input/results |
| U5 | Show an attachment-only email incomplete result and an image “credentials absent/unavailable” example | Explains the unanswered question without calling the attachment/image safe or fraudulent; chooses an independent review step |

Predeclared product-readiness criteria: no private-content persistence/URL exposure or stale export during these tasks; no critical false reassurance left unexplained; each participant can identify an independent verification step by the end; target at least four of five tasks completed unassisted, with actual task/participant denominators reported. A single critical privacy failure pauses the affected workflow until fixed and retested. A comprehension failure is recorded as a UX failure, not blamed on the participant. These criteria do not establish detector accuracy or prove real-world harm reduction.

Ask afterward: What did you think the app checked? What remained unknown? Which next step would you take? Was any label confusing or alarming? What did you expect Clear to erase? What one thing should change? Do not suggest the desired answer before recording the first response.

The [36-case communication diagnostic](../verification/cac-evaluation/report.md) retained 6/9 adapted scam-pattern misses and 5/9 ordinary extra concerns; all 9 ambiguous cases were unscored. Those selected authored cases are not human participants or a device benchmark, and do not justify a detector-accuracy claim. Preserve those limits when explaining the prototype to volunteers.

## Blank observations — no results entered

Build/archive SHA256: ______  Approved origin: ______  Observer: ______  Session date: ______

| Device code | Model / OS / browser / view | Online/offline preparation state | Task ID | Pass / fail / blocked / unsupported / not run | Exact observed behavior and error | Assistance / time | Reproduction / follow-up |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |

| Participant code | Voluntary/notes consent | Task ID and order | First choice/explanation (non-identifying) | Unassisted completion | Time / assistance | False reassurance or misunderstanding | Follow-up |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |

Actual participants: ____  Unassisted tasks completed / attempted: ____ / ____  Critical failures: ____
Blocked device tasks and reasons: ____  Changes made after these observations: ____
New build/retest date, recorded separately from original failures: ____  Notes deleted on: ____

Report observed counts and misses with version/date/device. Say “small voluntary usability pilot” if completed; do not convert software passes into participants, report planned work as completed, relabel a failed first attempt as a pass, or claim prevented losses. Current completed v6 software counts are 728 Python/121 JavaScript; this blank protocol adds zero participants and zero physical-device evidence.
