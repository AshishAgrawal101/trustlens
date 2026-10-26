# Independent reported-percentages math/API review

Read-only review of spec.md, current static/numbers-context.js and frozen-count/numerical tests. No implementation, tests, historical contracts or outputs changed. The proposed extension is useful: comparing supplied rates without inventing counts preserves an important distinction the existing counts-only workflow cannot express. No blocking arithmetic issue if exact decimal coefficients are used.

## Recommended minimal API

Keep current compare(input) function body unchanged and add comparePercentages({percentageA,percentageB}) alongside it. Return the same four numeric keys: rateA, rateB, percentagePoints, relativePercent (null for zero A). Strict string inputs only; no Number coercion, valueOf callbacks or inferred denominators. A published decimal coefficient/exponent is an arithmetic representation, not a supplied sample size, so never expose it as an observed count/total. No helper rewrite of counts is necessary. Reusing one generic helper risks changing count rateA/countA/totalA*100 rounding order or accidentally multiplying percentage-point differences by100 twice.

For each admitted trimmed string, parse coefficient c and fractional digit count d with denominator t=10**d using BigInt. Syntax can be the explicit ASCII grammar /^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/ and then exact bound 0<=c<=100*t. This accepts .5 and1., rejects lone dot/sign/exponent/%/comma/hex/nonfinite values, and handles all zero spellings consistently. Do not first convert to Number to perform the0..100 check:100.00000000000000000000000000000000001 must be rejected even though Number rounds it to100.

Set D=cB*tA-cA*tB. Percentage inputs are already in percent units:

- rateA=Number(cA)/Number(tA), rateB analogously; **no multiplication by100**.
- percentagePoints=Number(D)/Number(tA*tB); **no multiplication by100**.
- relativePercent=cA===0n?null:Number(D)/Number(cA*tB)*100.

1.2 vs1.8 therefore yields0.6points and50%relative. A100 vsB100 yields0points/0relative; A0 vsB0 still yields null relative. For nonzeroA to zeroB the relative result is-100%, not undefined. Swapping groups reverses points but generally does not negate relative change. These formulas retain a nonzero signed difference when separately converted rates round to the same Number. Return mathematical positive zero for exact D=0; a negative zero must not become a reported change.

## Bounded arithmetic and parsing points to settle explicitly

With at most64 normalized ASCII characters and no exponent, an admitted fractional decimal has at most63 fractional digits (the leading-dot spelling). The smallest positive admitted value is1e-63. Decimal coefficients/denominators and their cross-products stay well below Number overflow, and a nonzero percentage-point difference cannot underflow to zero in this domain. The largest relative change is below roughly1e67, finite. Each BigInt argument must be converted to Number only after bounded parsing and exact subtraction; converting separate rates before subtracting loses the intended precision. A defensive finite-output check can fail with a fixed input-free error, but must not silently replace a valid nonzero difference with0.

The only contract ambiguity is “ordinary surrounding whitespace” versus “hidden-formatting input.” JS trim() silently removes U+FEFF, a format character the spec says to reject. Specify allowed surrounding whitespace and check raw forbidden controls/format characters before trimming; do not let trim turn forbidden input into accepted numeric text. Smallest unambiguous option: allow surrounding ASCII U+0020 spaces only, reject Cc/Cf/Cs anywhere, then trim those spaces. If tabs/newlines are intentionally accepted around numbers, document the exact permitted set rather than also claiming all controls rejected. Non-ASCII digit forms and embedded whitespace should remain invalid.

The64 cap is stated after trimming and safely bounds BigInt work. It does not bound raw whitespace scanning; if the pure API is intended to impose a total resource bound too, explicitly define a modest raw-string cap before trim (or change the contract to64 raw characters). Browser maxlength64 already bounds ordinary user entry, but is not pure-API validation. This is a specification clarification, not a demonstrated performance defect or reason to add a dependency.

Use fixed errors for missing object/fields, wrong types, syntax, size and exact range. No raw string/object interpolation in errors. Extra object keys can follow existing compare compatibility rather than introducing an unrelated strict-schema policy. Validation must precede coefficient construction.

## Acceptance worth freezing before implementation

The existing proposed cases cover the main formulas. Add exact-bound rounding pair100.00000000000000000000000000000000001 reject vs100.00000000000000000000000000000000000 accept, leading zero spellings, lone dot, all admitted zero forms, and U+FEFF prefix/suffix rejection before trim. Use a long pair differing at the final fractional digit, e.g1.00000000000000000000000000000000000000000000000000000000000001 vs1.00000000000000000000000000000000000000000000000000000000000002 when within64 characters; assert signed nonzero difference and reconstruction against exact integer oracle, not merely different rendered rates. Programmatically construct length64 smallest-positive and length65 rejection to avoid counting typos in a fixture. Confirm finite rate/points/relative outputs across both extreme orders, null only when exact cA=0, and Object.is(value,-0) false for exact equal rates.

Preserve old compare outputs on all frozen12 cases and safe-max near-equal regression, not just approximate display strings. Keeping its body unchanged makes the compatibility claim strongest. Existing count example, native validity, first result heading focus+scroll, edits/Clear/exit/persisted-back privacy and static Pocket rendering/cache checks remain necessary controller/integration work. Six significant digits are display rounding only: a tiny difference can still be shown in scientific notation even if the two rounded displayed rates coincide. Percentage-mode questions should explicitly say supplied rates may already be rounded and sample sizes were not supplied; never imply precision/statistical significance/causation or reverse-engineer counts.

Recommendation: proceed after selecting the exact whitespace/raw-length policy. No second arithmetic library, new models, source visits or significance test is warranted.
