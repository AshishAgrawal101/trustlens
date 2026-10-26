# Bounded email href coverage design — not implementation

Inspected current VisibleText, anchor/body reconstruction, strict parse_address, text linkcoverage and guidance/frontend consumers. No app/tests edited, outputs scored or URLs fetched. The cases below are frozen as expectations before any future implementation/predictions; they are constructed parser contracts, not accuracy data.

## Smallest complete behavior

Retain every visible anchor's raw href category and label, rather than only HTTP(S)/mailto. Exclude anchors inside script/style as now. Keep current block/br label boundaries and inline concatenation. Do not use CSS visibility, basehref resolution, redirects or fetched content; state these limits. Count unsupported links without echoing href/label/query or treating them as fraud evidence.

For literal protocol-relative `//authority/path`, validate by passing `https:` plus the ORIGINAL href into existing strict parse_address solely inside a host-extraction helper. Require exactly two leading slashes and nonempty authority; `///`, empty authority, malformed ports/IDNA/numeric/scoped hosts are not accepted. Detect rawCc/Cf/Cs before any strip; current href.strip loses leadingtabs before validation, so retain raw input even if a separate classification value trims ordinary edge spaces. The synthetic prefix is an internal parser adapter, never appended to bodies/links, rendered, exported, or reported as an HTTPS/encrypted connection. Report only parsed host mismatch against an independently parseable contiguous displayedhost. Do not add an HTTPS/noHTTP claim. Paths/query/fragment are irrelevant to host equality and remain absent from comparison evidence.

Userinfo in a protocol-relative authority does not make the displayed prefix the destination. Strict parse_address supplies the actualhost; preserve existing caution: mismatch detail remains literal parsedhost comparison, not trustworthy ownership. Do not silently drop userinfo or normalize malformed/formatting characters into a trusted match. A valid //bank.example@evil.example target may compare destinationevil.example; no sourcevisit. A syntactically invalid //target counts as uninspected, not verifiedhost. Same-host protocol-relative targets need not generate fraud-weight evidence. Existing HTTP(S) links continue existing bounded localrules; do not rewrite them or change URLpolicy.

Continue primaryrecipient mailto comparison under existing limitations; do not infer that mailtoqueryrecipients, aliases, ownership or message delivery are checked. A malformed/noncomparable mailto target should contribute to partialhrefcoverage if the target could not be parsed, while an ordinary non-address label on a valid mailto is merely noncomparable displaytext. Avoid counting that label as a targetfailure.

Other nonempty hrefs—relativepaths, `?query`, unsupported/active schemes, malformed explicitwebschemes—are UNINSPECTED targets. Do not resolve them from a messagebase (untrusted, currentlyignored), inspect scriptdata, execute or stringify rawtarget into evidence. Relative targets may be legitimate; this is incompletecoverage, not risk evidence. Missinghref, empty/space-onlyhref and localfragmentonly `#section` are documented non-destination anchors: ignore for targetcoverage, neither verifiedsafe nor uninspectedexternaldestination. If rawhiddencontrols accompany apparentempty/fragment form, count unsupported rather than stripawayhiddencontent.

## Evidence/consumer coordination

Recommend a NEW stable `email:links_incomplete` Evidence, evidence_classunknown, severityinfo, weight0, fixed title and COUNT-ONLY detail: `N visible HTML link target(s) were not inspected because their address syntax or scheme is unsupported. No target was visited.` Aggregate across readableHTMLparts. Do not reuse `email:incomplete`, which currently means unreadable/ambiguous MIME/header/body and changes summary to couldnotfullyinterpretthroughtrustedmailapp. Do not reuse `analysis:links_incomplete` unchanged: its consumer hardcodes first8uniqueHTTP(S)cap and that would be false for unsupportedhrefs.

Root must coordinate guidance/app.js to recognize the newemailcoverageID: generic partiallinkreviewheadline, fixed inputfree export caveat, retain useful readablewarnings, no clean-safety headline, no increase in fraudweight/risk purelyfrom partialcoverage. Count omittedtargets separately from existing first8uniqueliteralHTTP(S)coverage and mismatchevidencecap; retain bothrecords ifbothapply. Ifconsumercoordinationcannotlandinthesameslice, do not silentlyshipnewIDwithoutvisiblecoverage. Existingemail limitations must explain host-onlyprotocolrelativehandling and unsupportedtargets, no impliedHTTPS. FullCSS/renderedvisibility and queryrecipientcoverage remain unimplemented.

## Frozen constructed contract

|ID|Constructed HTML/condition|Expected|
|---|---|---|
|pr-mismatch|labelhttps://bank.example;href//evil.example/path?PRIVATE=1|mismatchbank/evil;noHTTPS/HTTPtransportclaim/noPRIVATEdetail|
|pr-same|labelbank.example;href//BANK.EXAMPLE./path|nomismatch,noindependence/safetyclaim|
|pr-idna|labelstraße.example;href//xn--strae-oqa.example/|nomismatch,nontransitionalIDNApreserved|
|pr-userinfo|labelbank.example;href//bank.example@evil.example/|destinationevil,neverbank;noidentityclaim|
|pr-invalid|href///evil.example or//:443 or//0x7f000001|partialcount1each,novalidhost|
|pr-hidden|hrefcontainsleadingtab/ZWSP/bidi|partialcount,nostrippedtrustedcomparison|
|relative|href/login,../notice,?ticket=PRIVATE|partialcount3,noquery/path/PRIVATEecho|
|unsupported|hrefjavascript:...,data:...,ftp:/example|partialcount3,noexecution/fetch/fraudweight|
|non-destination|missinghref,emptyhref,spacesonly,#section|ignoreexternalcoverage,notverifiedsafe|
|hidden-fragment|rawcontrol+#section|partialcount1,notignoredthroughstrip|
|hidden-script|unsupportedhrefinside script/style|excluded,zeropartialcount|
|inline-vs-block|bank.<strong>example versusbank.<br>example|inlinecompares,blockdoesnotfabricatehost|
|valid-http-control|existingHTTPSmismatch/normalHTTPuserinfo|existingruleevidenceunchanged|
|mailto-control|validmismatch; malformedprimary; querycc|existingmismatch;malformedpartial;queryccstillunscannedlimitation|
|aggregate|2HTMLpartswithunsupportedhrefsplus9uniqueHTTPlinks|correctaggregatedunsupportedcountandseparateexistingcapcaveat|
|readablewarning|requestsharecodeplusunsupportedhref|requestwarningretained,partialcoverage0weight,inputfreeexports|

The implementation should distinguish invalid target from noncomparable label and cap detailedmismatches as now. Text/body-only pastes have no HTMLtargetcoverageclaim. .eml and pastedHTML must share the same semantic result; existing attachments/headerdefects remain separate. Futuretests should verify bothactualAPI shapes and frontendcoverage/exportconsumers with no URLsvisited. No authorization to editanotherowner's guidance/frontend follows from thisdesign.
