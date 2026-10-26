# Explicit coverage for unscanned email parts

The original attachment-only baseline was reproduced: a multipart mail containing only an application/pdf attachment returned the generic low-risk “No strong warning signs matched” headline with only a generic attachment limitation. This overstated the readable content checked.

The shared email analyzer now adds metadata-only `email:unscanned` evidence with an unscanned-part count. It iterates MIME structure without decoding unsupported/attachment content or recording filenames. Each explicitly attached multipart or forwarded-message subtree counts once and is not descended into. Nontext inline parts also count. Supported non-attachment text/plain and text/html alternatives do not count. The existing body_parts traversal is unchanged.

The evidence is unknown/info with zero fraud weight. When readable text exists, the headline explicitly limits coverage to readable subject/body and retains the existing warning result. When no readable body exists and unscanned parts remain, the result is explicitly incomplete and at least guarded; a subject alone does not establish attachment content or safety. Existing readable high-risk signs remain high. Existing incomplete-email guidance provides manual review actions and an input-free incomplete share summary.

Ten new tests cover attachment-only and nontext-only mail, subject-only mail with an attachment, normal multipart alternatives, inline images, attached forwarded messages and attached multipart subtrees, zero fraud weight, no filename/body echo, no calls to attachment content decoding, route guidance and paste/file parity. Existing malformed/deep MIME behavior and email/link/intake/upload regressions also passed: 154 targeted tests in 5.57 seconds, with no failures. Root owns restart and final integrated verification.

Skipped: attachment decoding, execution, malware scanning, content-type inference from attachment bytes and filenames in reports.
Risk: the inventory describes only unscanned coverage; it cannot establish whether an attachment or its declared MIME type is safe or truthful.
