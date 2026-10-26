const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../static/tools.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'../static/tools.css'),'utf8');
test('directory uses only known local destinations and supported mode-only fragments',()=>{
 const targets=[...html.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 const allowed=['#tools','/','/#check=text','/#check=screenshot','/#check=url','/#check=email','/#check=call','/#check=qr','/#check=image','/static/claim-review.css','/static/tools.css','/static/claim-review.html','/static/media-context.html','/static/numbers-context.html','/static/quote-context.html','/context-guide.html#ads'];
 assert.ok(targets.every(x=>allowed.includes(x)));
 for(const target of allowed)assert.ok(targets.includes(target),target);
 assert.doesNotMatch(html,/<script\b|https?:\/\/|\?mode=|data-mode=/i);
});
test('scope separates request checks, context and origin without verification claims',()=>{
 for(const id of ['communication-title','context-title','origin-title'])assert.match(html,new RegExp('aria-labelledby="'+id+'"'));
 assert.match(html,/More tools/);assert.match(html,/not met release requirements/);assert.match(html,/Missing credentials do not identify AI generation/);assert.match(html,/none supplies a truth verdict/);assert.match(html,/attachments unscanned/);assert.match(html,/No account/);
});
test('directory supports narrow layout and keyboard navigation without active input surfaces',()=>{
 assert.match(html,/class="skip" href="#tools"/);assert.match(html,/id="tools"[^>]*tabindex="-1"/);assert.match(css,/@media\(max-width:600px\)/);assert.match(css,/grid-template-columns:1fr/);assert.doesNotMatch(html,/<form\b|<input\b|<iframe\b|<img\b|\son\w+=/i);
});
test('light cards explicitly restore dark text and readable article links',()=>{
 assert.match(css,/\.tool-group\{color:var\(--ink\)\}/);
 assert.match(css,/\.tool-group \.eyebrow\{color:#125c50\}/);
 assert.match(css,/\.tool-group \.hint\{color:#40594d\}/);
 assert.match(css,/\.context-tools h3 a\{color:#125c50\}/);
});

test('home discovers the directory while all seven checker modes remain available',()=>{const home=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');assert.equal((home.match(/href="\/static\/tools.html"/g)||[]).length,2);const modes=[...home.matchAll(/data-mode="([^"]+)"/g)].map(m=>m[1]).sort();assert.deepEqual(modes,['call','email','image','qr','screenshot','text','url']);});
