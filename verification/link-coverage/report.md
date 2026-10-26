# Bounded link coverage — 2026-10-23

Fixed silent truncation of literal HTTP(S) links in the development candidate. Only app/analyzers/text.py and new tests/test_link_coverage.py were edited; this report is the verification output. No URL was fetched, extra address analyzed, fraud rule changed, model run or protected original edited.

Caller audit before editing: main.py text and call endpoints; email.py shared analyze_text over subject/decoded bodies and final communication_report with custom limitations; app/guidance.py input-free export generation; text/context/link/guidance test callers. Email reconstructs its report, so coverage explanation is keyed from evidence inside shared communication_report rather than attached only to analyze_text's first report.

## Behavior

The first eight unique literal URL matches still receive exactly the existing local address checks, in appearance order. Deduplication remains exact matching text before trailing punctuation trimming, preserving existing behavior. No normalization, additional parsing, link fetch, redirect following or ownership check was added.

At more than eight matches, evidence id analysis:links_incomplete reports only unique count, eight inspected and remaining uninspected count. It is unknown, info, weight zero: incomplete coverage is not an inferred fraud warning. Shared communication_report prefixes “Link review is incomplete” and adds the precise limit to its normal or email-specific limitations. Existing summaries and limitations are unchanged below the limit. Strong warnings among the first eight remain intact; ignored links never create address findings. If MIME/header interpretation is independently incomplete, email's existing more-general incomplete summary can supersede the prefix, while coverage evidence and limitation remain present.

The ordinary safe summary remains input-free. Its existing matched-sign count does not include the zero-weight coverage notice; root owns corresponding incomplete UI/export presentation and can recognize the evidence id explicitly.

## Checks

RED: 4 failed, 3 passed before editing: no evidence existed for text/call/email overflow, or overflow alongside a real first-eight warning.

GREEN: 289 passed in 1.39s:

`python -m pytest tests/test_link_coverage.py tests/test_link_evidence.py tests/test_community.py tests/test_professional_requests.py tests/test_reference_context.py tests/test_context_history.py tests/test_guidance_context.py -q`

Seven new regressions cover eight links, duplicated eight links, many repeats, nine unique links with duplicate ninth across text/call/email, exact parser call list, an ignored suspicious ninth link, preserved strong first-eight findings, null risk index/low confidence and input-free summary. Tests use constructed example addresses. A tracking wrapper proves the suspicious ninth destination was never passed to analyze_url and no url:userinfo finding is fabricated from it.

Skipped browser and full-suite integration, owned by root. Remaining limit: links after the first eight remain unexamined, hidden HTML label comparisons have their own separate bounds, and unmatched content is never a safety guarantee.
