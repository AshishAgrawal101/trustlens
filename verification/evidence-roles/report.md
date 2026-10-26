# Independent human-role acceptance result

Frozen contract unchanged: SHA256 b09644736bd8bda0c8c7ed14469fd0b027a4174df7a430024f37e842b735e4bd. Reviewed source SHA256 9de2cef081935a830719ca0dc09424bc10ae9dffd466f36e747a05102c5dfcaf. evaluate.cjs calls ClaimReview.review with original frozen inputs; the original 25-case worksheet contract still calls the compatible analyze adapter.

All 18 cases pass: 16 worksheet results and two fixed invalid-role errors. Active role IDs and required/forbidden gap questions match. Inactive URL/quote, date-only and whitespace-only accounts cannot close gaps. Missing-account explanatory label rows are recorded separately; they are explicitly not counted as role assignments. The evaluator checks exact active-role IDs, allowing these informative :missing rows rather than misrepresenting them as meaningful accounts. No contract expectation was changed.

No concrete actionable semantic defect found. Every active label calls itself the user's interpretation, not a detected finding. Every valid result includes labels:human_judgment denying checked relevance/reliability/factual support/independence. Quote-only accounts stay unattributed. Opposed support/challenge labels remove only the corresponding gap prompts and leave the next step unresolved; they do not establish balance or truth. Gap wording explicitly says different positions do not require equal weight.

No network attempt or input mutation occurred in the isolated pure-function run. Invalid role strings/types yield a fixed message, without echoing the value. No app edits. The evaluator refuses to overwrite retained results; source and contract digests are saved alongside all actual outputs/errors in results.json.

New tests/claim_roles_contract.test.cjs: 21 pass, including 18 frozen rows plus lineage, interpretation/exclusion and false-balance checks. Combined with previous frozen worksheet/pure tests, 54 pass in 131.2 ms process duration. These are authored acceptance checks, not evidence of factual accuracy or model performance.

Interaction scenarios remain controller/browser scope. Source review confirms role controls have both input/change invalidation and Clear/page lifecycle resets to unsure. This pure test does not establish actual browser focus, clipboard permissions, complete erasure or accessibility. Root's separate controller/browser receipts should describe those observations. Fixed PLAN exports contain no selected role findings or private input.
