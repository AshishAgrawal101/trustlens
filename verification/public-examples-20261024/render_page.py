"""Render retained public diagnostic only; no analyzer imports or predictions."""
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[1]
MANIFEST_SHA="1a20943215977476f11c71df256abd210ceb98ea68ce78828226e82256f9da17"

def render():
    manifest_bytes=(FOLDER/"frozen-manifest.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest()!=MANIFEST_SHA:
        raise ValueError("Frozen manifest changed")
    manifest=json.loads(manifest_bytes)
    results=json.loads((FOLDER/"results.json").read_text(encoding="utf-8"))
    if results["manifest_sha256"]!=MANIFEST_SHA:
        raise ValueError("Results do not belong to this manifest")
    records=manifest["records"]; rows=results["rows"]
    if [r["id"] for r in records]!=[r["id"] for r in rows]:
        raise ValueError("Retained rows differ from frozen records")
    esc=html.escape
    cards=[]
    for record,row in zip(records,rows):
        url=record["source_url"];parsed=urlsplit(url)
        if parsed.scheme!="https" or parsed.hostname not in {"consumer.ftc.gov","www.microsoft.com","www.uspis.gov","support.microsoft.com"}:
            raise ValueError("Non-primary source URL")
        label=record["hand_label"]
        if label=="ambiguous":
            outcome="No pattern matched. This fragment is ambiguous and unscored."
        elif row["actual_warning"]:
            outcome="Pattern concern reported: "+", ".join(item["id"]+" ("+item["severity"]+")" for item in row["request_evidence"] if item["weight"]>0)+". This does not prove fraud."
        elif row["expected_warning"]:
            outcome="Retained miss: no pattern matched the author-assigned warning expectation."
        else:
            outcome="No pattern matched this advice excerpt. This is not a safety verdict."
        kind="Official message illustration" if record["kind"]=="official_message_illustration" else "Official advice / policy, verbatim"
        date=record["publication_or_update_date"] or "Not displayed in the opened source"
        cards.append('<article class="public-card" id="'+esc(record["id"])+'" aria-labelledby="'+esc(record["id"])+ '-title"><p class="public-type">'+esc(kind)+'</p><h3 id="'+esc(record["id"])+ '-title">'+esc(record["id"].replace('-',' ').capitalize().replace('Ftc ', 'FTC ').replace('Uspis ', 'USPIS '))+'</h3><p class="public-label">AUTHOR-ASSIGNED LABEL: '+esc(label.upper())+'</p><blockquote>'+esc(record["snippet"])+'</blockquote><p class="public-outcome">'+esc(outcome)+'</p><p>'+esc(record["rationale"])+'</p><details><summary>Source and excerpt scope</summary><p><a href="'+esc(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+esc(record["source_title"])+' (opens in a new tab)</a></p><p>'+esc(record["excerpt_selection"])+'</p><p>Publication / update: '+esc(date)+'; date precision: '+esc(record["date_precision"])+'. Retrieved: '+esc(record["retrieved_date_utc"])+ ' UTC.</p></details></article>')
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Seven retained public educational excerpts and their literal-pattern outcomes, including misses."><title>Public examples and retained misses — TrustLens</title><link rel="stylesheet" href="/static/claim-review.css"><style>
.public-examples .public-body{padding:28px;display:grid;gap:22px}.public-examples .public-card{min-width:0;border:1px solid #b8c9bd;border-radius:14px;background:#fffef9;color:#143c38;padding:24px;overflow-wrap:anywhere}.public-examples .public-card h3{font-size:22px;line-height:1.3;margin:0 0 12px}.public-examples .public-type,.public-examples .public-label{font-size:14px;font-weight:700;color:#245c50}.public-examples blockquote{margin:18px 0;padding:15px 18px;border-left:4px solid #397c61;background:#edf2eb;font-size:19px;white-space:pre-wrap}.public-examples .public-outcome{font-weight:700}.public-examples summary{cursor:pointer;font-weight:650;min-height:44px}.public-examples .public-summary{padding:24px 28px;color:#143c38;background:#edf2eb;border-bottom:1px solid #b8c9bd}.public-examples .public-summary ul{padding-left:22px}.public-examples .public-provenance{padding:0 28px 28px;overflow-wrap:anywhere}.public-examples .public-provenance code{font-size:14px}.public-examples .public-card details p{margin-top:12px}@media(max-width:540px){.public-examples .public-body,.public-examples .public-summary{padding:20px 16px}.public-examples .public-card{padding:20px 16px}.public-examples .public-provenance{padding:0 16px 22px}.public-examples blockquote{padding:12px;font-size:18px}}@media print{body.public-examples>*{display:block!important}body.public-examples:after{display:none!important}.public-examples details{display:block}.public-examples .public-card{break-inside:avoid}body.public-examples{background:#fff;color:#143c38}}
</style></head><body class="public-examples"><a class="skip" href="#public-results">Skip to retained examples</a><header class="wrap header"><a class="brand" href="/" aria-label="TrustLens home"><span class="lens" aria-hidden="true"></span>TrustLens</a><a class="back" href="/">← Back to the checker</a></header><main class="wrap"><section class="intro"><p class="eyebrow">TRANSPARENCY · RETAINED RESULTS</p><h1>Public examples.<br><em>Misses included.</em></h1><p class="lede">Seven short excerpts from opened official pages, compared with the unchanged local request-pattern rules. These are public educational illustrations and advice, not victim logs or a representative benchmark.</p></section><section class="workspace" id="public-results" tabindex="-1" aria-labelledby="public-title"><div class="workspace-bar"><h2 id="public-title">What the pattern check actually returned</h2></div><div class="public-summary"><ul><li>3 author-assigned warnings → 1 pattern concern and 2 retained misses.</li><li>3 advice excerpts → no pattern concerns.</li><li>1 ambiguous fragment → unscored; no pattern matched.</li></ul><p>Labels reflect the author’s interpretation of the published context. No accuracy, safety or source-verification claim is made. Excerpts omit surrounding cues; a subject or fragment is not a complete message. Nothing is checked when this page opens.</p><p>This page has no inputs or scripts. Source links open only when you choose them.</p></div><div class="public-body">"""+"\n".join(cards)+"""</div><section class="public-provenance" aria-labelledby="provenance-title"><h3 id="provenance-title">Frozen source and limits</h3><p>The manifest and labels were frozen before predictions on 2026-10-24 UTC. This page renders retained results; it does not rerun the analyzer. Only request_evidence was evaluated, not email headers, links, guidance or the end-to-end interface.</p><p>Short contiguous excerpts are attributed to their publishers. No live message destinations are included. No source was visited by the analyzer; opening an attribution link is your separate choice.</p><p>Manifest SHA-256: <code>"""+esc(MANIFEST_SHA)+"""</code></p><p>Evaluated request-pattern source SHA-256: <code>"""+esc(results["source_sha256"])+"""</code></p><p>These historical outcomes describe that exact source and these excerpts. They do not measure performance on future messages. Misses remain visible; no tuning followed this diagnostic.</p></section></section></main><footer class="wrap"><span>TrustLens · A second look, before you act.</span><a href="/">Return home</a></footer></body></html>
"""

if __name__=="__main__":
    (ROOT/"static/public-examples.html").write_text(render(),encoding="utf-8")
