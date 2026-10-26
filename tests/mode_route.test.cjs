// Entry routes reuse the actual mode buttons; no content travels through the fragment.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const base=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
function setup(hash){let harness=base.replace('setAttribute(k,v){this.attributes[k]=v;}', 'setAttribute(k,v){this.attributes[k]=v;}getAttribute(k){return this.attributes[k];}');
 harness=harness.replace('window:{innerWidth:1200,',`window:{location:{hash:${JSON.stringify(hash)}},innerWidth:1200,`);
 harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);for(const script of ['primary-flow.js','mode-route.js'])vm.runInContext(fs.readFileSync(path.join(root,'static',script),'utf8'),context);");
 const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);return fixture.setup();
}
for(const mode of ['text','url','email','call','screenshot','qr','image'])test('directory entry selects '+mode+' without submitting or importing text',()=>{
 const x=setup('#check='+mode);assert.equal(x.requests.length,0);assert.equal(x.ids.content.value,'');assert.equal(x.ids.file.value,'');assert.equal(x.document.activeElement,x.ids.workspace);assert.equal(x.ids['visual-modes'].open,['url','email','call','qr','image'].includes(mode));
 const label={text:'Paste the message',url:'Paste a web address',email:'Paste the email',call:'What did the caller say?',screenshot:'Choose a message screenshot',qr:'Choose an image with a QR code',image:'Upload the original file'}[mode];if(mode!=='text')assert.equal(x.ids['input-label'].textContent,label);else assert.equal(x.document.querySelectorAll('[data-mode]').find(b=>b.dataset.mode==='text').getAttribute('aria-pressed'),'true');
 assert.equal(x.ids.file.required,['screenshot','qr','image'].includes(mode));assert.equal(x.ids.reviewed.checked,false);assert.equal(x.ids.result.hidden,true);
});
test('unknown, partial, encoded or content-bearing fragments are ignored',()=>{
 for(const hash of ['', '#workspace','#check=admin','#check=email&text=PRIVATE','#check=%65mail','#check=Email','#check=image?file=PRIVATE']){const x=setup(hash);assert.equal(x.document.querySelectorAll('[data-mode]').find(b=>b.dataset.mode==='text').getAttribute('aria-pressed'),'true');assert.equal(x.document.activeElement,null);assert.equal(x.requests.length,0);assert.equal(x.ids.content.value,'');}
});
test('repeating the selected route retains the edited draft without another mode click',()=>{const x=setup('#check=email');x.ids.content.value='PRIVATE';let clicks=0;x.document.querySelectorAll('[data-mode]').find(button=>button.dataset.mode==='email').addEventListener('click',()=>clicks++);for(const fn of x.windowEvents.hashchange)fn({});assert.equal(clicks,0);assert.equal(x.ids.content.value,'PRIVATE');assert.equal(x.requests.length,0);});
