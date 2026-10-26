// Integrated input-flow controller tests, including ordinary mode hooks and explicit review.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace('setAttribute(k,v){this.attributes[k]=v;}', 'setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k];}dispatchEvent(event){return this.fire(event.type,event);}');
harness=harness.replace('AbortController,AbortSignal,Blob,','AbortController,AbortSignal,Blob,Event,');
harness=harness.replace('vm.runInContext(source,context);', "vm.runInContext(source,context);for(const script of ['draft-transfer.js','primary-flow.js'])vm.runInContext(fs.readFileSync(path.join(root,'static',script),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob,Event};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
test('Message and Screenshot are primary while all seven unique modes remain reachable',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');
  const primary=html.slice(html.indexOf('class="communication-modes primary-modes"'),html.indexOf('<details id="visual-modes"'));
  assert.deepEqual([...primary.matchAll(/data-mode="([^"]+)"/g)].map(m=>m[1]),['text','screenshot']);
  const modes=[...html.matchAll(/data-mode="([^"]+)"/g)].map(m=>m[1]);assert.equal(modes.length,7);assert.equal(new Set(modes).size,7);
  assert.match(html,/More tools: link, email, call, QR &amp; image origin/);
  const x=fixture.setup();assert.equal(x.ids['visual-modes'].open,false);assert.equal(x.requests.length,0);
});
test('the screenshot path stays primary and requires read, edit/review, then a separate check',async()=>{
  const x=fixture.setup();await x.mode('screenshot');assert.equal(x.ids['visual-modes'].open,false);assert.equal(x.ids['screenshot-sample-help'].hidden,false);assert.match(x.ids['mode-guide'].textContent,/confirm before checking/);
  await x.file();assert.equal(x.requests.length,0);x.state.fetch=async()=>({ok:true,json:async()=>({text:'Send me your security code.',notice:'Review all recognized words.'})});await x.submit();
  assert.equal(x.requests[0].url,'/api/extract/screenshot');assert.equal(x.ids['ocr-review'].hidden,false);assert.equal(x.ids.result.hidden,true);
  await x.submit();assert.equal(x.requests.length,1);assert.match(x.ids.error.textContent,/confirm/);
  x.ids.content.value='Please send me your security code.';await x.ids.content.fire('input');assert.equal(x.ids.reviewed.checked,false);
  x.ids.reviewed.checked=true;x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.submit();assert.equal(x.requests[1].url,'/api/analyze/text');assert.equal(x.ids.result.hidden,false);assert.ok(x.ids.actions.textContent);
});
test('More tools follows selected modes without triggering a request or trapping the primary path',async()=>{
  const x=fixture.setup();for(const mode of ['url','email','call','qr','image']){await x.mode(mode);assert.equal(x.ids['visual-modes'].open,true);assert.equal(x.ids['screenshot-sample-help'].hidden,true);}
  await x.mode('text');assert.equal(x.ids['visual-modes'].open,false);assert.match(x.ids['mode-guide'].textContent,/review the evidence/);assert.equal(x.requests.length,0);
});
test('demo replacement and explicit draft transfer select the appropriate disclosure with no analysis',async()=>{
  const x=fixture.setup();await x.demo('link');assert.equal(x.ids['visual-modes'].open,true);await x.demo('ordinary');assert.equal(x.ids['visual-modes'].open,false);
  const text=x.ids.content.value;await x.ids['transfer-draft'].fire('click');assert.equal(x.ids['visual-modes'].open,true);assert.equal(x.ids['input-label'].textContent,'What did the caller say?');assert.equal(x.ids.content.value,text);
  await x.ids['transfer-draft'].fire('click');assert.equal(x.ids['visual-modes'].open,false);assert.equal(x.ids.content.value,text);assert.equal(x.requests.length,0);
});
test('constructed screenshot link is a passive download and cannot auto-select or extract a file',async()=>{
  const x=fixture.setup();await x.mode('screenshot');const anchor=x.ids['screenshot-sample-download'];
  assert.equal(anchor.attributes.href,'/static/demo-message.png');assert.equal(anchor.attributes.download,'trustlens-constructed-screenshot.png');
  await anchor.fire('click');assert.equal(x.ids.file.value,'');assert.equal(x.ids.file.files.length,0);assert.equal(x.requests.length,0);assert.equal(x.ids['ocr-review'].hidden,true);
  await x.mode('text');assert.equal(x.ids['screenshot-sample-help'].hidden,true);
});
test('QR remains in More tools and retains its separate review gate',async()=>{
  const x=fixture.setup();await x.mode('qr');await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'https://example.org',codes:['https://example.org'],review_required:true,notice:'Review the code.'})});
  await x.submit();assert.equal(x.requests[0].url,'/api/extract/qr');assert.equal(x.ids['visual-modes'].open,true);assert.equal(x.ids.reviewed.required,true);await x.submit();assert.equal(x.requests.length,1);
});
