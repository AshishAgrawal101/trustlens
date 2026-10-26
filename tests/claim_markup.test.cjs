const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../static/claim-review.html'),'utf8');const css=fs.readFileSync(path.join(__dirname,'../static/claim-review.css'),'utf8');
test('claim workspace exposes unique labelled constrained fields and initially hidden accessible output',()=>{
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);assert.equal(new Set(ids).size,ids.length);
 for(const id of ['claim-text','claim-context','source-a-url','source-b-url','source-a-quote','source-b-quote','source-a-date','source-b-date']){assert.ok(ids.includes(id),id);assert.ok(html.includes('for="'+id+'"'),id);}
 assert.match(html,/<textarea id="claim-text"[^>]*required maxlength="4000"/);for(const source of ['a','b']){assert.match(html,new RegExp('<input id="source-'+source+'-url"[^>]*type="url" maxlength="4096"'));assert.match(html,new RegExp('<input id="source-'+source+'-date"[^>]*type="date"'));}
 assert.match(html,/<section id="claim-result" tabindex="-1" hidden/);assert.match(html,/id="claim-error"[^>]*role="alert" tabindex="-1" hidden/);
 for(const id of ['claim-form','claim-review-submit','claim-clear','claim-observations','claim-questions','claim-next-steps','claim-copy-plan','claim-download-plan','claim-copy-status'])assert.ok(ids.includes(id),id);
});
test('page states no verdict or source verification and export omission, with local script only',()=>{
 assert.match(html,/No truth score is produced/);assert.match(html,/Sources are not visited/);assert.match(html,/not independently verified/);assert.match(html,/input-free steps only/);assert.match(html,/source addresses, quotes and dates are omitted/);
 assert.match(html,/data-claim-example="caption"/);assert.match(html,/data-claim-example="headline"/);assert.match(html,/<script src="\/static\/claim-review.js"><\/script>/);assert.doesNotMatch(html,/<script>|type="file"|<img|<iframe|action="https?:/);
});
test('print cannot expose private workspace and sizing supports narrow layouts',()=>{assert.match(css,/@media print\{body>\*\{display:none!important\}/);assert.match(css,/font-size:16px/);assert.match(css,/min-height:44px/);assert.match(css,/prefers-reduced-motion:reduce/);assert.match(css,/grid-template-columns:1fr/);});

test('script failure cannot submit named private fields through native GET fallback',()=>{
 const form=html.slice(html.indexOf('<form id="claim-form"'),html.indexOf('</form>'));
 assert.match(form,/<form id="claim-form" autocomplete="off">/);assert.doesNotMatch(form,/\bname="/);assert.match(form,/id="claim-review-submit" type="submit" disabled/);assert.match(form,/<noscript>.*requires JavaScript.*Review is disabled.*No sources are fetched.*<\/noscript>/);
});
