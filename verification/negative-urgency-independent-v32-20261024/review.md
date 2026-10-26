# Independent negative-urgency review

No concrete issue found. Eight probes frozen in probes.json before new implementation/tests inspection; actual Evidence outputs preserved in results.json. Only complete sentence-leading declarative 'This is not urgent' becomes unknown/info/weight0 context. Question punctuation, embedded quoted/history framing, double negation and hard-line interruption retain old urgency behavior. Horizontal whitespace and soft-hyphen normalization use existing policy; original soft hyphen remains in the evidence excerpt. Later same-family urgency and a live code request remain positive independently.

Compared actual source diff to immutable v31 ZIP (diff.txt): change is confined to the narrow guard/context branch. RULES exact equality verified; no report construction, weight, model, parser or language-scope edits. New detail explicitly says the supplied clause describes urgency and does not verify sender or safety, rather than declaring a safe message.

139 targeted negative-urgency/passive-refusal/remember-not-to tests passed, zero failures/skips. Five additional independent controls retained urgency: quoted entire declaration, ?!, comma question, semicolon later urgent request and comma later act-now request. These extra probes were exploratory after code inspection and are not relabeled frozen acceptance. No app edits or historical final-data access; code/constructed strings only. This remains a narrow English wording exception, not general negation/quote understanding.

## Final guard simplification supplemental review

Current text.py SHA256 a24fedbb87efdcd60c56e82287ec88cf826caa8258052152acdba9b69d720dd0. Question punctuation now reads normalized text at sentence_match.end() directly; existing wording_view removes only intra-letter soft hyphens, preserving punctuation and sentence boundaries. Original evidence excerpts still use the original offset helper. This removes unnecessary source-boundary mapping without broadening recognized clauses. All 24 new negative-urgency tests pass, zero skips. Initial frozen probes/results remain unchanged.
