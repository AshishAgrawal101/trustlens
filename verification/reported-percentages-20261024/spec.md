# Reported percentages — bounded product extension

Problem: Numbers & context accepts only whole-number counts and totals. A user with two published percentages, but no sample sizes, cannot compare them without inventing denominators. Add one explicit input method to this existing tool, not another calculator. Existing counts math and its frozen regressions remain unchanged in behavior.

## Contract before implementation

- Select counts/totals (default) or reported percentages. No inference, automatic conversion, sample-size reconstruction or cross-tool transfer. Each method uses its own labelled unnamed fields. Changing method clears entered numbers and the prior result; no automatic comparison.
- Percentages are ordinary nonnegative decimal strings from0to100, optional decimal point, at most 64 raw characters including surrounding ASCII spaces. No sign/exponent/comma/%/hex/nonfinite/hidden-formatting input. Accept0,100,1.2,.5,1.; rejectempty,negative,100.01,NaN,Infinity,1e2 andoversizeddata. Numeric bounds and syntax are separate. Strict string parsing preserves decimal values for rational cross-product arithmetic.
- Export new pure NumbersContext.comparePercentages({percentageA:string,percentageB:string}); existing compare({countA,totalA,countB,totalB}) stays compatible. A small shared rational helper is allowed only if all existing frozen counts/numerical tests remain exactly valid. Use integer decimal coefficients and powers of10, not independently rounded percentages to find differences. The64char cap bounds BigInt work and Number conversion; outputs remain finite. No dependency.
- Output GroupA/B rates, B-minus-A percentage points and relative rate change compared withA. IfAiszero, relative change is null/undefined with fixed explanation. Zero-to-zero is also undefined. No time ordering, significance, causality, truth or data-quality conclusion. Display remains six significant digits; explain that supplied percentages may already be rounded.
- Reported-percentages results explicitly say underlying counts/totals were not supplied. Never display invented counts such as1of100. Retain original-data/comparability/denominator questions.
- Percentage fields text/inputmode decimal/maxlength64/required, initially hidden+disabled. Input-method select initiallydisabled until handlers ready. Hidden method fields stay disabled so native required validation does not block the active method. No field names, submissions, network, storage, history or new exports. Existing no-script guard persists.
- Shared Clear wipes all numbers/results and focuses the active method’s first field. Method stays selected on Clear. Lifecycle exit/persistedBack clears values/results and resets default counts. Input edits invalidate result. Existing count example unchanged; percentage example1.2vs1.8 explicitloadonly.
- Fixed current count-mode caveat remains initially unchanged; percent result caveat states supplied percentages/unknown totals/no significance or causal conclusion. Preserve result-first order, h3focus+nativeblockstart scrolling, full expanded limits, all old DOMIDs and privacy-print omission.
- Reuse desktop source templates/controllers for Pocket aliases. After stable edits advance Pocket cache fromv18 and synchronize readiness fixtures, regenerate a unique phone export and test actual prepared/exported offline calculations. Preserve all prior archives.

## Acceptance examples frozen before outputs

1. 1.2vs1.8: rates1.2/1.8, +0.6points, +50%relative.
2. 20vs15: -5points,-25%relative; reversing groups yields+5points,+33.333…%relative.
3. 0vs0 and0vs1: relative undefined;1vs0: -1point,-100%relative.
4. 100vs100:0points/0relative; .5vs1.:+.5point,+100%relative.
5. Nearby long decimal strings retain signed difference even if independently rendered rates coincide.
6. Smallest admitted positive decimal and100producefinite outputs; no infinity, negativezero-as-findings or fabricateddenominator.
7. Invalid syntax/range/length/types fail fixed private errors, not HTML/JS echo.
8. Controller defaults/counts/example/validation remain; select/change/edit/Clear/exit/Back reset correctly; disabled hidden fields; percentage-specific facts/unknowns; no I/O.
9. Actual local browser at320/390: both methods via keyboard; percentage success/zero baseline/error/recovery/Clear, heading/firstfact visible/no overflow. Prepared static Pocket export repeats disconnected calculation. No physical-phone claim.

Ownership assigned only after independent math/UX review. No new model, public source, hosting, phone setup or claimed learning/accuracy result.

## Accepted review clarifications (before implementation)

Keep the existing compare(counts) function body unchanged; the new percentages API uses decimal rational coefficients directly in percentage units, so its point difference has no extra factor of100. Avoid a count-function refactor merely to share three arithmetic expressions.

The64-character cap applies to each raw string including any surrounding spaces, matching theHTMLmaxlength. Trim only ordinaryASCIIU+0020 edge spaces. Reject rawCc/Cf/Cs and any non-ASCII whitespace before trimming. No generic trim() which removesFEFF. This bounds work before BigInt conversion and prevents precision loss from Number-based range checks. Literal100.000…001 must be rejected even when Number would round it to100.

Reviewers froze16independent Fraction-based branches inacceptance.json before implementation. Preserve their digest/cases; if rawcap differs from a frozen edge case, resolve before code ratherthan silentlyweakening. Verify finite large relative-change output wraps at320/390. Root will preserve a v22 reliability checkpoint before assigning implementation files for this extension.
