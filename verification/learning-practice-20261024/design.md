# One coherent Practice journey: choose the next check

Design proposal only. Extend the existing Practice dialog and SCENARIOS/controller; no new page, worksheet, source fetching, analysis endpoint, model or persistent profile. Six authored constructed situations teach a bounded review action, not whether a real message or story is true. All content below is original practice material.

## Journey

Entry stays Practice in the main header. Intro: **Six constructed situations. Practice choosing what to check next—not deciding who or what is true.**

Each item displays a topic, a short scenario/question and three plain-language actions. Exactly one is the best bounded review action given the supplied situation. After selection, keep the selected state visible, disable all choices, focus explanatory feedback and reveal Next. Feedback says **A useful next check:** followed by the correct action and its explanation. If distinguishing the chosen action is useful, use existing 'That is the safer next step' wording, but do not produce a running right/wrong tally.

Progress: **Situation 2 of 6 · 1 reviewed** before answering; **Situation 2 of 6 · 2 reviewed** afterward. A determinate progress element may use reviewed/6 with an accessible label 'Practice situations reviewed'; omit animation and do not label it accuracy, safety ability, confidence or protection. Do not show a score or imply the reviewer learned the skill from clicking an answer.

After the last explanation, **Finish practice** reveals a compact completion state in the same dialog. Heading: **Six situations reviewed.** Fixed recap: 'Keep a request private. Trace the original account. Compare counts with their totals. Inspect exact wording. Separate file history from the story.' Limits: 'These constructed examples are not an independent benchmark or an assessment of your ability. Real situations can remain unresolved.' Actions: **Restart practice**, **Back to the checker**, and optionally a normal **Explore local tools** link. Do not auto-navigate or prefill another tool.

## Proposed six items

### 1. Communication · keep the code private

Scenario/question: **An unexpected caller says: “Read me the security code we just sent so I can cancel a payment.” What is the best next check?**

Choices:

1. Read the code once the caller supplies an employee number.
2. End the call and contact the provider through an app or number you already know. **Best**
3. Ask the caller to repeat the request more slowly.

Explanation: **Keep the code private and verify through a separate route. An employee number supplied by the caller does not authenticate them. The wording is a reason to pause; this practice item does not identify an actual caller or prove fraud.**

Optional tool signpost after feedback: Message / Call wording check, never voice authentication.

### 2. Claim context · trace shared evidence

Scenario/question: **Two websites repeat the same press release about a new local policy. A post calls this “two independent confirmations.” What should you check next?**

Choices:

1. Count the websites as two independent sources because their addresses differ.
2. Treat the claim as false because both websites quote the same release.
3. Trace the original release and look for evidence independent of that account. **Best**

Explanation: **Different websites can repeat one underlying source. That observation does not make the policy claim true or false. Read the original account and check what evidence each report adds. Labels such as supporting or challenging are your interpretation, not automatically detected reliability.**

Optional tool signpost: Claim & context.

### 3. Image caption · separate clocks and events

Scenario/question: **A reposted image is captioned “today’s storm.” An editable file field contains an older date. What is the best next check?**

Choices:

1. Find the earliest original account and compare its caption, publication date and event context. **Best**
2. Declare the caption false from the file date alone.
3. Declare the caption accurate if no location metadata is present.

Explanation: **An embedded clock, publication date and event date can describe different things. Metadata can be edited, copied or removed. Neither an old-looking date nor missing location metadata resolves the caption. This item does not inspect an image or establish where or when a scene occurred.**

Optional tool signpost: Media & context for limited file details, Claim & context for source accounts. No file selected or uploaded by practice.

### 4. Numbers · compare the denominator

Scenario/question: **A report lists 20 cases among 100 people in Group A and 30 cases among 200 in Group B. It says the larger count means Group B has a higher rate. What is the best next check?**

Choices:

1. Accept a higher rate because 30 is larger than 20.
2. Compare 20% with 15%, then check whether the groups and measurements are comparable. **Best**
3. Conclude that being in Group B causes fewer cases.

Explanation: **The supplied rates are 20/100 = 20% and 30/200 = 15%. Group B has the larger count but the smaller proportion in these supplied numbers. That descriptive comparison does not establish data quality, statistical significance, comparability or cause.**

Optional tool signpost: Numbers & context. No estimate of real-world prevalence or research finding is being made.

### 5. Literal quotations · inspect what was changed

Scenario/question: **One supplied version says “The site may close for repairs.” A repost says “The site will close permanently.” What is the best next check?**

Choices:

1. Prefer the shorter repost because it is easier to understand.
2. Use the changed wording alone to decide which author is dishonest.
3. Compare the exact words, then read the full original account and surrounding context. **Best**

Explanation: **The supplied versions differ in wording. A literal comparison can show those changes; it cannot authenticate either version, determine intent or settle factual meaning. Check the fuller source before interpreting the revision.**

Optional tool signpost: Quote & context. Both versions explicitly remain supplied/unverified; do not call either an authenticated original.

### 6. Provenance versus story · verify the transaction separately

Scenario/question: **A seller offers an image with a validated, asset-bound Content Credentials signature and asks for a deposit. What is the best next check?**

Choices:

1. Verify the seller, item and payment protections through independent routes before paying. **Best**
2. Treat the signature as proof that the item exists and the deposit is safe.
3. Treat an image-pattern score as another independent vote that the seller can be trusted.

Explanation: **Validated provenance concerns signed statements bound to a file under a trust policy. It does not verify a seller, the existence of an item or a payment request. Pattern-model outputs answer another limited question and can share biases; a combined score is not an independent third model. Check the story and transaction separately.**

Optional tool signpost: Image origin for limited evidence; Message for payment-request wording. No origin model or signature verification runs in practice.

## State, privacy and keyboard acceptance

- Each open starts a fresh session. Restart resets index, reviewed count, selected choices, explanation, progress, completion state and any signpost. No answer history, timestamps, analytics, local/session storage or URL payloads.
- Retain only current item choice and simple in-memory reviewed count, or derive reviewed count from sequential index/answered flag. Do not retain a detailed answer log or calculate correctness percentage. Restart cannot accidentally add to a prior session.
- Practice reads none of the checker's private input, report, file, source accounts or caption. Opening/closing it does not overwrite an existing checker draft or run any analysis. Item text and recap are fixed authored content rendered with textContent.
- On answer, move focus to feedback before disabled choices leave a keyboard user without a focus destination. Next focuses the new question/first enabled choice. Completion focuses its heading. Restart focuses the first question. Back to checker/Escape closes the native modal and restores the invoking button; avoid auto-moving focus to an unrelated input.
- Escape and both close buttons work during an item, explanation and completion. Closing cancels no unrelated checker request and cannot leave a hidden modal completion button tabbable. Reopening resets the session, not checker content.
- Pagehide/persisted pageshow reset practice state so Back cannot restore an answer summary unexpectedly; use existing private-page lifecycle without erasing private checker data merely because practice resets. No claim that browser process snapshots can be forcibly erased.
- No programmatic file selection, upload, source fetch, model run, clipboard/export or automatic navigation. Tool links are passive internal links, if included, and carry only a whitelisted tool choice; they transfer no scenario or user text. Leaving the page uses normal private-input pageexit clearing.
- Mobile: 44px minimum answer/Next/Restart targets, readable body text, visible focus and no horizontally scrolling question/choice cards. Progress has a text equivalent; color is not the sole feedback signal. Reduced motion respected.

## Meaningful regression plan

1. All six scenarios have one valid answer index and fixed nonempty feedback. Assert selected subjects/actions in each case, not a snapshot of decorative copy.
2. Opening does not read/overwrite checker values, create fetch requests, allocate previews or submit. Every example remains visibly constructed.
3. Answer feedback and focus move correctly; double-click/repeated activation cannot increment reviewed count twice. Next before answer does nothing; one Next advances one item.
4. Last item goes to a bounded completion state rather than an index past SCENARIOS. Completion has reviewed6/6 but no accuracy score and no retained correctness log.
5. Restart from completion and from a partially answered session resets to zero reviewed; close/reopen also resets. Disabled old answers cannot reappear or receive focus.
6. Native keyboard Escape/focus restoration, narrow widths and screen-reader progress announcements require root browser checks. DOM tests alone do not establish these or demonstrate learning.

This is a proposal awaiting implementation assignment. It adds one coherent review habit journey to the existing feature rather than another page. It does not change scam rules, model reliability or factual-verification capabilities.
