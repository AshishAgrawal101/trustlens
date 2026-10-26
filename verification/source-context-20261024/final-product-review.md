# Final product review: source finder and shared quote workspace

Read-only source review of current quote-context.html/CSS/controller, source-context.js and main dialog styles/markup. No application edits, browser uploads, profile/permission changes or user-tab inspection. Root reports browser hit/no-hit/example-clear/native-anchor/Tab+Enter-back verification; those are attributed root evidence, not repeated here.

## P3: shared field instructions do not scope comparison-only requirements

Original version and Revised version labels both say unqualified Required. Original's aria-describedby also includes quote-limits, whose 'Each version ...800segments' statement sounds applicable to every use of the field. Finder intentionally requires only Original plus the separate source passage, and has no800segment cap. Although current nearby helper says Revised not needed, the label/description contract is contradictory.

Concrete source experiment: Original='x '.repeat(401) has802characters/802segments. SourceContext.find(original,original) returns one match; QuoteContext.compare(original,original) rejects the800segment limit. Neither implementation is wrong; the visible/screen-reader-facing scope description is incomplete.

Minimal suggested fix: Original required for comparison and finding; Revised required for comparison. Start quote-limits 'For version comparison only...' and explicitly state finder uses the Original4000character cap without the comparison segment limit. Keep existing native required flags (separate forms) and validation behavior. Acceptance: static label/description assertions clarify both actions, comparison still rejects >800segments, finder still accepts within4000characters with Revised blank. No semantic, factual or authenticity conclusion should be added.

## Reviewed without further concrete defect

- Original/finder jump links are passive native fragments; root has verified keyboard navigation. The source-form is separate, so native Revised required does not block finder submission. Missing Original is rejected by the finder with a fixed message; source error is focused. Quote-example clears pasted source/result through the added hook.
- Source Clear removes source only; main Clear and example replacement wipe full source/finder state. Original edits invalidate results; Revised changes need not invalidate finder because they are not its input. Exit/Back clearing remains covered by each module.
- Exact-match result uses text nodes/mark, bounded first five context windows with a total non-overlapping count. Conditional edge ellipses and context-window note prevent a window from being presented as the whole passage. No match explicitly does not prove fabrication; a hit does not authenticate source or meaning.
- Summary is at least58px high, buttons at least44/48px under shared CSS, textarea inputs16px and long source snippets pre-wrap/anywhere. Source disclosure has a dark green focus outline against the light card. No source-driven anchors exist.
- Main dialog close controls use width44px and shared min-height44px. At320 viewport, dialog width calc(100%-32px) gives288px; mobile padding22px leaves a244px content area. The upper-right close button is positioned right20/top10 and is not CSS-shrunk below its target width. Eyebrows are short and headings begin below the top-row space; no specific overlap can be established from source. Native layout/text zoom/pointer hit testing is not certified by this calculation.
- Diff scroll region is focusable/labelled, added/removed text has visible words as well as decoration, and snippet focus/output errors have explicit destinations. Screen-reader reading order and live-announcement duplication still require actual assistive-technology testing.

No new privacy or state blocker found. Primary suggested change is truthful scoping of already-existing input requirements, not another feature.
