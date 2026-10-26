'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),folder=path.join(root,'verification/public-examples-20261024');
const manifestBytes=fs.readFileSync(path.join(folder,'frozen-manifest.json')),manifest=JSON.parse(manifestBytes),results=JSON.parse(fs.readFileSync(path.join(folder,'results.json'))),html=fs.readFileSync(path.join(root,'static/public-examples.html'),'utf8');
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#x27;');
test('page retains frozen manifest and all seven record IDs',()=>{
 assert.equal(crypto.createHash('sha256').update(manifestBytes).digest('hex'),'1a20943215977476f11c71df256abd210ceb98ea68ce78828226e82256f9da17');
 assert.equal((html.match(/<article /g)||[]).length,7);for(const r of manifest.records)assert.equal((html.match(new RegExp('id="'+r.id+'"','g'))||[]).length,1);
 assert.ok(html.includes(results.source_sha256));assert.ok(html.includes(results.manifest_sha256));
});
test('every exact snippet is escaped and source-attributed to opened primary HTTPS pages',()=>{
 for(const record of manifest.records){assert.ok(html.includes('<blockquote>'+escape(record.snippet)+'</blockquote>'));
  const url=new URL(record.source_url);assert.equal(url.protocol,'https:');assert.ok(['consumer.ftc.gov','www.microsoft.com','www.uspis.gov','support.microsoft.com'].includes(url.hostname));
  assert.ok(html.includes('href="'+escape(record.source_url)+'" target="_blank" rel="noopener noreferrer"'));assert.ok(html.includes(escape(record.source_title)));
 }
});
test('source quotation scope remains within 25 words per page and no snippet has a live URL',()=>{
 const totals=new Map();for(const r of manifest.records){totals.set(r.source_url,(totals.get(r.source_url)||0)+r.snippet.trim().split(/\s+/u).length);assert.doesNotMatch(r.snippet,/https?:|www\./i);}
 for(const count of totals.values())assert.ok(count<=25);
});
test('warning/advice/ambiguity and retained misses remain explicit without accuracy claims',()=>{
 const warning=results.rows.filter(r=>r.expected_warning===true),advice=results.rows.filter(r=>r.expected_warning===false),ambiguous=results.rows.filter(r=>r.expected_warning===null);
 assert.equal(warning.length,3);assert.equal(warning.filter(r=>r.actual_warning).length,1);assert.equal(warning.filter(r=>!r.actual_warning).length,2);assert.equal(advice.length,3);assert.ok(advice.every(r=>!r.actual_warning));assert.equal(ambiguous.length,1);
 assert.equal((html.match(/Retained miss:/g)||[]).length,2);assert.equal((html.match(/AUTHOR-ASSIGNED LABEL:/g)||[]).length,7);
 assert.match(html,/not victim logs or a representative benchmark/);assert.match(html,/No accuracy, safety or source-verification claim/);assert.match(html,/not a complete message/);assert.match(html,/Only request_evidence was evaluated/);
});
test('static page has no scripts, active inputs, source prefetches, handlers or content APIs',()=>{
 assert.doesNotMatch(html,/<(?:script|iframe|form|input|textarea|button)\b/i);assert.doesNotMatch(html,/\son[a-z]+\s*=/i);assert.doesNotMatch(html,/(?:fetch|localStorage|sessionStorage|XMLHttpRequest)\s*[(.]/);
 assert.doesNotMatch(html,/<link[^>]+(?:preconnect|prefetch|prerender|https?:)/i);assert.match(html,/href="\/static\/claim-review.css"/);assert.match(html,/Source links open only when you choose them/);
 const generator=fs.readFileSync(path.join(folder,'render_page.py'),'utf8');assert.doesNotMatch(generator,/from app|import app|request_evidence\(/);assert.match(generator,/html.escape/);
});
