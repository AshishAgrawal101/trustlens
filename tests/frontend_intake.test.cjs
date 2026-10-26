// Controller regressions reuse the existing offline DOM double, with print/FormData observability.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
let harness=fs.readFileSync(path.join(__dirname,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0];
harness=harness.replace('FormData:class{append(){}}','FormData:class{constructor(){this.entries=[];}append(...args){this.entries.push(args);}}');
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(harness+'\nthis.setup=setup;this.report=report;',fixture);
async function email(x,name='message.eml',size=100){x.ids['email-file'].files=[{name,size,type:'message/rfc822'}];await x.ids['email-file'].fire('change');}
test('QR extraction requires separate review and checks all edited text without opening destinations',async()=>{
  const x=fixture.setup();await x.mode('qr');await x.file();
  x.state.fetch=async()=>({ok:true,json:async()=>({text:'https://first.test\nSend a code',codes:['https://first.test','Send a code'],review_required:true,notice:'Review every code.'})});
  await x.submit();assert.equal(x.requests[0].url,'/api/extract/qr');assert.equal(x.ids.content.value,'https://first.test\nSend a code');
  assert.equal(x.ids.reviewed.required,true);assert.equal(x.ids.result.hidden,true);await x.submit();assert.equal(x.requests.length,1);
  x.ids.reviewed.checked=true;x.ids.content.value='https://corrected.test\nSend a code';await x.ids.content.fire('input');assert.equal(x.ids.reviewed.checked,false);
  x.ids.reviewed.checked=true;x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.submit();
  assert.equal(x.requests[1].url,'/api/analyze/text');assert.deepEqual(JSON.parse(x.requests[1].options.body),{text:'https://corrected.test\nSend a code'});
  assert.equal(x.requests.length,2);
});
test('QR clear or mode change rejects stale extraction and malformed success cannot bypass review',async()=>{
  const x=fixture.setup();await x.mode('qr');await x.file();let resolve;
  x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();await x.ids.clear.fire('click');
  resolve({ok:true,json:async()=>({text:'PRIVATE QR',review_required:true})});await pending;
  assert.equal(x.ids.content.value,'');assert.equal(x.ids['ocr-review'].hidden,true);assert.equal(x.ids['file-name'].textContent,'');
  await x.file();x.state.fetch=async()=>({ok:true,json:async()=>({text:'https://not-reviewed.test',review_required:false})});await x.submit();
  assert.match(x.ids.error.textContent,/could not be reviewed/);assert.equal(x.ids['ocr-review'].hidden,true);
  await x.mode('email');assert.equal(x.ids.reviewed.required,false);assert.equal(x.ids.file.required,false);
});
test('email file selection waits for explicit analysis, preserves paste alternative, and uses multipart',async()=>{
  const x=fixture.setup();await x.mode('email');x.ids.content.value='Existing pasted draft';await email(x,'<img onerror=alert(1)>.EML');
  assert.equal(x.requests.length,0);assert.equal(x.ids.content.hidden,true);assert.equal(x.ids.content.required,false);
  assert.equal(x.ids['email-file-name'].textContent,'<img onerror=alert(1)>.EML');assert.equal(x.ids['email-file-name'].children.length,0);
  assert.match(x.ids.submit.textContent,/Analyze email file/);x.state.fetch=async()=>({ok:true,json:async()=>({...fixture.report(),kind:'email'})});await x.submit();
  assert.equal(x.requests[0].url,'/api/analyze/email-file');assert.equal(x.requests[0].options.body.entries[0][0],'file');assert.equal(x.requests[0].options.headers['Content-Type'],undefined);
  await x.ids['email-file-clear'].fire('click');assert.equal(x.ids.content.hidden,false);assert.equal(x.ids.content.required,true);assert.equal(x.ids.content.value,'Existing pasted draft');
  assert.equal(x.ids['email-file-name'].textContent,'');await x.submit();assert.equal(x.requests[1].url,'/api/analyze/email');
});
test('invalid email files fail locally and file clear or mode replacement rejects stale reports',async()=>{
  const x=fixture.setup();await x.mode('email');
  for(const [name,size] of [['message.html',10],['message.eml',250001],['empty.eml',0]]){
    await email(x,name,size);assert.match(x.ids.error.textContent,/250,000/);assert.equal(x.ids['email-file-name'].textContent,'');assert.equal(x.ids.content.hidden,false);
  }
  assert.equal(x.requests.length,0);await email(x);let resolve;x.state.fetch=()=>new Promise(r=>resolve=r);const pending=x.submit();
  await x.mode('text');resolve({ok:true,json:async()=>({...fixture.report(),summary:'PRIVATE FILE RESULT'})});await pending;
  assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['email-file-name'].textContent,'');assert.equal(x.ids['print-summary'].textContent,'');
  await x.mode('email');await email(x);await x.ids.example.fire('click');assert.equal(x.ids['email-file-name'].textContent,'');assert.equal(x.ids.content.hidden,false);
  await email(x);await x.ids.clear.fire('click');assert.equal(x.ids['email-file'].value,'');assert.equal(x.ids['email-file-name'].textContent,'');assert.equal(x.ids.content.value,'');
});
test('print checklist uses only safe summary, clears on edits, and cannot print a stale report',async()=>{
  const x=fixture.setup();await x.ids.print.fire('click');assert.equal(x.state.prints,undefined);
  const data=fixture.report();data.summary='PRIVATE SUMMARY';data.evidence[0].detail='PRIVATE EVIDENCE';data.share_summary='Fixed input-free next steps';
  x.ids.content.value='PRIVATE MESSAGE';x.state.fetch=async()=>({ok:true,json:async()=>data});await x.submit();
  assert.equal(x.ids['print-summary'].textContent,'Fixed input-free next steps');await x.ids.print.fire('click');assert.equal(x.state.prints,1);
  assert.doesNotMatch(x.ids['print-summary'].textContent,/PRIVATE/);await x.ids.content.fire('input');assert.equal(x.ids['print-summary'].textContent,'');
  await x.ids.print.fire('click');assert.equal(x.state.prints,1);
});
test('print stylesheet hides every body child except the dedicated input-free checklist',()=>{
  const css=fs.readFileSync(path.join(__dirname,'../static/styles.css'),'utf8');
  assert.match(css,/@media print\{body>\*\{display:none!important\}body>#print-checklist\{display:block!important/);
  const html=fs.readFileSync(path.join(__dirname,'../static/index.template.html'),'utf8');
  const print=html.slice(html.indexOf('<section id="print-checklist"'),html.indexOf('<script src="/static/app.js"'));
  assert.match(print,/id="print-summary"/);assert.doesNotMatch(print,/id="content"|id="evidence"|id="file-name"/);
});
test('optional known website stays scoped to Link and clears private comparison drafts',async()=>{
  const x=fixture.setup();await x.mode('url');assert.equal(x.ids['known-website-wrap'].hidden,false);
  x.ids.content.value='https://bank.example/pay';x.ids['known-website'].value='bank.example';await x.submit();
  assert.deepEqual(JSON.parse(x.requests[0].options.body),{url:'https://bank.example/pay',known_website:'bank.example'});
  x.ids['known-website'].value='changed.example';await x.ids['known-website'].fire('input');assert.equal(x.ids.result.hidden,true);assert.equal(x.ids['print-summary'].textContent,'');
  await x.mode('text');assert.equal(x.ids['known-website-wrap'].hidden,true);assert.equal(x.ids['known-website'].value,'');await x.submit();
  assert.equal(Object.hasOwn(JSON.parse(x.requests[1].options.body),'known_website'),false);
});
test('QR capability shows configuration only and treats older responses as unknown',async()=>{
  const x=fixture.setup();const data={message_rules:true,screenshot_ocr:{configured:true},image_detector:{configured:false},content_credentials:{configured:true},qr_reader:{configured:true,detail:'Native decoder configuration only.'}};
  x.state.fetch=async()=>({ok:true,json:async()=>data});await x.ids['capability-refresh'].fire('click');
  assert.match(x.ids['capability-list'].textContent,/QR code reader: configured; runtime not verified/);
  delete data.qr_reader;await x.ids['capability-refresh'].fire('click');assert.match(x.ids['capability-list'].textContent,/QR code reader: configuration unknown/);
});
test('constructed fixture links remain passive downloads scoped to their intake modes',async()=>{
  const x=fixture.setup();await x.mode('qr');assert.equal(x.ids['qr-sample-help'].hidden,false);assert.equal(x.ids['email-upload'].hidden,true);
  await x.ids['qr-sample-download'].fire('click');assert.equal(x.requests.length,0);assert.equal(x.ids.file.value,'');assert.equal(x.ids['ocr-review'].hidden,true);
  assert.equal(x.ids['qr-sample-download'].attributes.href,'/static/demo-qr.png');assert.equal(x.ids['qr-sample-download'].attributes.download,'trustlens-constructed-qr.png');
  await x.mode('email');assert.equal(x.ids['qr-sample-help'].hidden,true);assert.equal(x.ids['email-upload'].hidden,false);
  await x.ids['email-sample-download'].fire('click');assert.equal(x.requests.length,0);assert.equal(x.ids['email-file'].value,'');assert.equal(x.ids.result.hidden,true);
  assert.equal(x.ids['email-sample-download'].attributes.href,'/static/demo-email.eml');assert.equal(x.ids['email-sample-download'].attributes.download,'trustlens-constructed-email.eml');
  await x.mode('text');assert.equal(x.ids['qr-sample-help'].hidden,true);assert.equal(x.ids['email-upload'].hidden,true);
});
