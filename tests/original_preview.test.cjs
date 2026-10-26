// Actual controller plus viewer; DOM double does not certify rendering or native scrolling.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace("this.tagName=tag;", "this.tagName=tag;this.style={};");
harness=harness.replace('setAttribute(k,v){this.attributes[k]=v;}', 'setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return k===\'src\'?this.src:this.attributes[k];}');
harness=harness.replace('vm.runInContext(source,context);', "vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/original-preview.js'),'utf8'),context);");
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
async function open(x){x.ids['original-preview'].open=true;await x.ids['original-200'].fire('click');}
test('viewer reuses one existing image and URL; explicit sizes never analyze or change review',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();assert.equal(x.blobs.length,1);assert.equal(x.ids.preview.src,'blob:fixture');
  assert.equal(x.ids['original-preview'].open,false);await open(x);assert.equal(x.ids.preview.style.width,'200%');assert.equal(x.document.activeElement,x.ids['original-frame']);
  assert.equal(x.ids['original-200'].getAttribute('aria-pressed'),'true');assert.equal(x.requests.length,0);assert.equal(x.blobs.length,1);assert.equal(x.ids.reviewed.checked,false);
  for(const [id,width] of [['original-150','150%'],['original-fit','100%']]){x.ids['original-frame'].scrollTop=100;await x.ids[id].fire('click');assert.equal(x.ids.preview.style.width,width);assert.equal(x.ids['original-frame'].scrollTop,0);}
});
test('Clear, mode, demo, exit and Back remove original source and reset disclosure and size',async()=>{
  for(const reset of ['clear','mode','demo','pagehide','pageshow']){
    const x=fixture.setup();await x.mode('screenshot');await x.file();await open(x);
    if(reset==='clear')await x.ids.clear.fire('click');else if(reset==='mode')await x.mode('text');else if(reset==='demo')await x.demo('code');else for(const fn of x.windowEvents[reset])fn({persisted:true});
    assert.equal(x.ids.preview.src,undefined,reset);assert.equal(x.ids['preview-wrap'].hidden,true);assert.equal(x.ids['original-preview'].open,false);assert.equal(x.ids.preview.style.width,'100%');assert.equal(x.revoked.length,1);assert.equal(x.revoked[0],'blob:fixture');
    await x.ids['original-200'].fire('click');assert.equal(x.ids.preview.style.width,'100%');
  }
});
test('file replacement resets expanded viewer and invalid selection cannot retain previous pixels',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();await open(x);await x.file();assert.equal(x.ids['original-preview'].open,false);assert.equal(x.ids.preview.style.width,'100%');assert.equal(x.revoked.length,1);
  await open(x);x.ids.file.files=[{type:'text/html',size:10}];await x.ids.file.fire('change');assert.equal(x.ids.preview.src,undefined);assert.equal(x.ids['preview-wrap'].hidden,true);assert.equal(x.ids['original-preview'].open,false);assert.equal(x.ids.error.hidden,false);assert.equal(x.requests.length,0);
});
test('late OCR after Clear cannot restore source or review and comparison never bypasses review gate',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();await open(x);await x.ids.clear.fire('click');
  resolve({ok:true,json:async()=>({text:'PRIVATE LATE OCR',notice:'Review first.'})});await pending;assert.equal(x.ids.content.value,'');assert.equal(x.ids.preview.src,undefined);assert.equal(x.ids['ocr-review'].hidden,true);
  await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'Send a code',notice:'Review first.'})});await x.submit();await open(x);const count=x.requests.length;await x.submit();assert.equal(x.requests.length,count);assert.match(x.ids.error.textContent,/confirm/);
  x.ids.reviewed.checked=true;x.ids.content.value='Corrected';await x.ids.content.fire('input');assert.equal(x.ids.reviewed.checked,false);
});
test('image display failure is actionable without fetching another resource or analyzing',async()=>{
  const x=fixture.setup();await x.mode('screenshot');await x.file();await x.ids.preview.fire('error');assert.match(x.ids['original-status'].textContent,/could not display/);assert.equal(x.requests.length,0);assert.equal(x.blobs.length,1);
  await x.ids.clear.fire('click');await x.ids.preview.fire('error');assert.equal(x.ids['original-status'].textContent,'Fit to frame width.');
});
test('markup and styles retain one original, uncropped width sizing, keyboard region and private print exclusion',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8'),css=fs.readFileSync(path.join(__dirname,'../static/styles.css'),'utf8');
  assert.equal((html.match(/id="preview"/g)||[]).length,1);assert.match(html,/id="original-frame"[^>]*tabindex="0"/);assert.match(css,/#preview\{display:block;width:100%;max-width:none;height:auto;object-fit:contain/);
  assert.match(css,/@media print\{body>\*\{display:none!important\}body>#print-checklist\{display:block!important/);
  const helper=fs.readFileSync(path.join(__dirname,'../static/original-preview.js'),'utf8');assert.doesNotMatch(helper,/fetch\(|createObjectURL|localStorage|sessionStorage|\.src\s*=/);
});
