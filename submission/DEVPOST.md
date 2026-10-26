# TrustLens

**Elevator pitch:** A private second look at suspicious messages, calls, links and images—showing the evidence and a safer next step before someone sends money or shares access.

## What is the specific problem, and how do you know it is real?

People face a practical decision when an unexpected caller or message asks them to act: send money, read out a code, install an app, or trust an image. Warning signs can be unclear, and an overconfident accusation can also cause harm. TrustLens helps users pause, understand the request and verify it through a separate route.

**Intended community:** families who help one another assess unexpected payment and account-access requests. The entrant selected this focus. No interviews, usability study or prevented-loss outcomes have been established. Before submission, add consented, non-identifying community observations if available; personal family details are deliberately excluded from this draft.

The FTC's [consumer scam guidance](https://consumer.ftc.gov/scams) covers impersonation, gift-card requests, phone scams and other relevant patterns. This supports the broader problem; it does not establish prevalence in our specific community.

## What it does

Users choose Message, Screenshot, Link, Email, Call or Image. Screenshots pass through local Windows OCR and an editable, explicitly confirmed review step before analysis. Results show observed facts, possible concerns, unresolved questions and specific next actions. A security-code request is treated differently from a normal code notification or a request for source code. Pasted email authentication headers remain unverified. Call checking works on a transcript; no voice-clone claim is made.

Results lead with a next step and group the supporting evidence. HTML email checks compare a displayed web address with the underlying link host, while acknowledging legitimate tracking differences. Constructed practice-check buttons demonstrate a risky request, a disguised link and ordinary advice without a user having to paste private material.

Images use two separate signals: a frozen local visual detector and C2PA Content Credentials. Signed provenance does not authenticate a sale or prove a scene true. The interface explicitly keeps image origin separate from scam intent.

Users can copy or download an input-free summary to discuss with someone they trust. It excludes the original message, contact details and suspicious URLs. A short practice mode teaches why a particular next step is safer, including a benign example and a provenance misconception.

If someone already acted, a recovery checklist addresses money sent, exposed credentials, remote-device access or a clicked link. It asks for no personal incident details and links to FTC guidance. It does not promise recovered funds.

## How it was built

Python, FastAPI and Pydantic handle bounded inputs and structured evidence. Standard-library parsing handles URLs and MIME emails. The interface is plain HTML/CSS/JavaScript with keyboard controls, responsive layout and visible error/unknown states. Existing frozen CLIP/CommunityForensics inference and an isolated native C2PA worker supply the optional image path. Checks run locally, without a remote LLM or URL fetch.

AI-assisted coding and earlier components are disclosed in `DISCLOSURE.md`. This prototype is an extension of an existing project, not a wholly new model trained during the hackathon. Organizer eligibility has not been established.

## What makes the approach useful

The emphasis is on a defensible decision process: show the evidence, disclose the uncertainty, then suggest an independent action. Input-free sharing and a practice mode support conversations among family members or neighbors without forwarding sensitive content. This is a product-design contribution; it is not a claim that multimodal scam checking is new.

## What was tested

The professional development build passed 486 Python tests with zero skips, including native OCR and C2PA signing/tampering, and 51 controller/share tests. Browser checks cover the communication flow, configuration panel and Pocket's local workflow; Pocket also received a real browser form POST into its review step, produced user-selected guidance, and cleared/reloaded without retained text while the local server was stopped. Physical Android share-sheet behavior is still unverified. Android installation/share-sheet behavior, screenshot/image browser uploads and full assistive-technology conformance remain unverified. Two short published scam excerpts plus constructed controls formed a frozen diagnostic: one excerpt gained a warning, the other remains a miss. Four actual admitted images returned no embedded credentials through native C2PA; the visual-model attempt stopped at RAM admission and produced no scores. These checks establish no population accuracy or user-study outcome. See `docs/PROFESSIONAL-UPGRADE-20261023.md` for exact scope.

## Challenges and limitations

Rules can misread context and miss new scams. An image model cannot decide whether an offer is honest. C2PA is often absent, and copied authentication headers cannot be trusted as proof. The prototype is English-only and supports call transcripts, not live phone interception. A local setup is heavier than a production consumer app.

## Next steps

Run consent-based usability sessions with the specific community, document false reassurance and confusing warnings, then prioritize improvements from those observations. Any public deployment requires security and operational work beyond this local build.

## Submission checklist

- [ ] Add consented community usability observations if collected; do not disclose a relative's experience without their permission.
- [ ] Resolve prior-component eligibility with the organizers; disclose reuse accurately.
- [ ] Upload a public repository containing source, README, tests and disclosures; exclude local paths, private data and large weights.
- [ ] Record and link the 2–6 minute demo using `DEMO.md`.
- [ ] Review every claim against the saved verification and evaluation files.
- [ ] Submit the complete entry before the published deadline.

Sources: [official rules](https://neighborhoodhacks.org/rules/), [judging rubric](https://neighborhoodhacks.org/judging/), [Devpost](https://neighborhood-hacks-2026.devpost.com/). Checked October 21, 2026 in America/Chicago.

The later usefulness version adds exact-hostname comparison against a user-supplied known website (no site visits or authenticity claim), selectable fixed Pocket recovery checklists, and explicit incomplete reporting/exports for inputs beyond the eight-link inspection limit. See docs/USEFULNESS-20261023.md.
