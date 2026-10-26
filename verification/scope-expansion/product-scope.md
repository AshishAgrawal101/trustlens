# Content and context: landing integration

TrustLens now presents two distinct paths: check a message/request for existing rule-based warning signs, or manually review a claim and its context. The hero and a link above the existing mode controls point to `/static/claim-review.html` using “Review a claim & its context.” This is a local worksheet for organizing user-supplied evidence, sources, missing context and alternative explanations. It does not browse, establish truth, authenticate sources or provide an accuracy claim.

The broader introduction includes messages, claims, image context and sources without expanding the existing analyzers' contracts. All seven data-mode hooks and checker element IDs remain intact. Message/Screenshot still check reviewed wording; other tools keep their existing address, email, transcript, QR and image-origin scopes. An image-origin signal cannot establish a depicted event or accompanying claim. A worksheet entry is a user's observation, not an independently verified finding.

Implementation scope for this slice is only `static/index.template.html` and this note. The worksheet itself is owned and integrated separately by root/the assigned worker; linking to its path does not establish that its validation, lifecycle behavior or browser rendering has passed. No model, online fact-checking, deployment, publishing or source-fetch capability was added by this landing change.

Validation: 25 existing frontend professional/dashboard/scope/original-preview tests passed, zero skips, after the copy change. A static check confirmed all seven mode hooks and two claim-review links. This slice does not claim phone execution, human usability or claim-verification accuracy.
