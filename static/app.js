'use strict';
const $ = id => document.getElementById(id);
const MODES = {
  text: {label:'Paste the message', help:'Texts, direct messages, or a request someone sent you. Remove details you don’t need to share. Wording rules cover English; other-language warning signs may be missed.', placeholder:'Paste the exact wording here…', max:30000, example:'This is your bank security team. Your account will be suspended. Send us the verification code immediately. Do not call your bank.'},
  url: {label:'Paste a web address', help:'We inspect the address without visiting it. HTTPS alone does not establish safety.', placeholder:'https://example.com', max:4096, example:'https://trusted-bank.example@account-review.example/verify'},
  email: {label:'Paste the email', help:'Include the body and, if available, full headers. Pasted authentication headers cannot independently verify a sender. Wording rules cover English; other-language warning signs may be missed.', placeholder:'From: …\nSubject: …\n\nEmail body…', max:250000, example:'From: Community Office <office@example.org>\nReply-To: claim@example.net\nAuthentication-Results: mail.example.org; spf=pass; dkim=pass\nSubject: Grant payment\n\nYou have won a community grant. Buy gift cards to pay the processing fee immediately.'},
  call: {label:'What did the caller say?', help:'Paste a transcript or write down the request. We check the wording, not the caller’s identity or voice. Wording rules cover English; other-language warning signs may be missed.', placeholder:'Caller: …\nMe: …', max:30000, example:'Caller: I am with technical support. Install AnyDesk so I can fix your account. Read me the login code. Keep this secret from your family.'},
  screenshot: {label:'Choose a message screenshot', help:'Read English text locally, correct recognition mistakes, then explicitly check the request. A screenshot cannot reveal a hidden link destination.', max:30000},
  qr: {label:'Choose an image with a QR code', help:'Decode QR text locally without opening any destination. Review every decoded code before checking the wording and links.', max:30000},
  image: {label:'Upload the original file', help:'Check Content Credentials and visual AI-origin patterns. Re-uploads and screenshots can lose credentials.', max:30000}
};
const DEMOS = {
  code: {mode:'text', text:MODES.text.example},
  link: {mode:'email', text:'From: Account Team <updates@bank.example>\nSubject: Review your account\nContent-Type: text/html; charset=utf-8\n\n<p>Please review your account:</p><a href="https://account-review.example/sign-in">https://bank.example</a>'},
  ordinary: {mode:'text', text:'Your one-time code is 123456. Do not share it with anyone. We will never ask you to read us a verification code.'}
};
let mode='text', controller, generation=0, currentReport=null, previewURL=null, ocrReady=false, emailFile=null, manualTopics=null, manualVersion=0;
function node(tag,text,className){const n=document.createElement(tag); if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function clearResult(){$('cross-checks').hidden=true;window.VerificationPlan?.reset();clearManualGuidance();generation++;controller?.abort();currentReport=null;$('result').hidden=true;$('result-recovery').hidden=true;$('loading').hidden=true;$('empty').hidden=false;$('error').hidden=true;$('submit').disabled=false;$('check-form').setAttribute('aria-busy','false');['verdict','result-summary','coverage-checked','coverage-unverified','cross-check-rows','cross-check-status','credentials','evidence','evidence-count','actions','limits','copy-status','print-summary','error','check-status'].forEach(id=>$(id).replaceChildren());}
function releasePreview(){if(previewURL)URL.revokeObjectURL(previewURL);previewURL=null;$('preview').removeAttribute('src');$('file-name').textContent='';$('preview-wrap').hidden=true;}
function updateInputCount(){ $('input-count').textContent=$('content').value.length.toLocaleString('en-US')+' / '+MODES[mode].max.toLocaleString('en-US')+' characters'; }
function inputState(){
  const upload=['image','screenshot','qr'].includes(mode), emailUpload=mode==='email'&&emailFile, editing=(!upload||ocrReady)&&!emailUpload;
  $('content').hidden=!editing;$('content').required=editing;$('input-meta').hidden=!editing;updateInputCount();
  $('image-input').hidden=!upload;$('file').required=upload&&!ocrReady;
  $('known-website-wrap').hidden=mode!=='url';$('qr-sample-help').hidden=mode!=='qr';
  $('email-upload').hidden=mode!=='email';$('email-file-name').textContent=emailFile?emailFile.name:'';$('email-file-clear').hidden=!emailFile;
  $('ocr-review').hidden=!ocrReady;$('reviewed').required=ocrReady;
  $('input-label').htmlFor=emailUpload?'email-file':editing?'content':'file';
  $('input-label').textContent=emailUpload?'Selected email file':ocrReady?(mode==='qr'?'Review every decoded QR code':'Review and edit the recognized text'):MODES[mode].label;
  $('submit').replaceChildren(document.createTextNode(emailUpload?'Analyze email file':mode==='image'?'Check image origin':mode==='qr'&&!ocrReady?'Read QR code':mode==='screenshot'&&!ocrReady?'Read screenshot':ocrReady?'Check reviewed text':'Check for warning signs'),node('span','→'));
}
function resetInput(){clearResult();ocrReady=false;$('reviewed').checked=false;$('content').value='';$('known-website').value='';$('file').value='';emailFile=null;$('email-file').value='';$('example-note').hidden=true;releasePreview();inputState();}
function setMode(next){resetInput();mode=next;$('visual-modes').open=['screenshot','image','qr'].includes(mode);const m=MODES[mode];document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));$('input-help').textContent=m.help;$('mode-guide').textContent=mode==='image'?'Image origin cannot tell you whether a seller or payment request is safe. Choose Screenshot to read a message instead.':mode==='qr'?'Two steps: decode the image, then review every code before checking. QR text is unverified; no destination is opened.':mode==='screenshot'?'Two steps: read the screenshot, then review and correct the text before checking. Hidden link destinations cannot be recovered.':'Choose Message for wording, Link for an address, or Email for headers and hidden HTML links. Call checks a transcript, not a voice.';$('content').placeholder=m.placeholder||'';$('content').maxLength=m.max;$('example').hidden=!m.example;inputState();}
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.mode!==mode)setMode(b.dataset.mode);}));
document.querySelectorAll('[data-demo]').forEach(b=>b.addEventListener('click',()=>{const demo=DEMOS[b.dataset.demo];setMode(demo.mode);$('content').value=demo.text;updateInputCount();$('example-note').hidden=false;$('content').focus();}));
$('clear').addEventListener('click',()=>{resetInput();(['image','screenshot','qr'].includes(mode)?$('file'):$('content')).focus();});
$('cancel').addEventListener('click',()=>{clearResult();$('check-status').textContent='Stopped waiting for this check. Your input is kept here. Local processing may continue.';($('content').hidden?(emailFile?$('email-file'):$('file')):$('content')).focus();});
$('check-form').addEventListener('keydown',async event=>{
  if(event.key!=='Enter'||(!event.ctrlKey&&!event.metaKey)||event.altKey||event.shiftKey||event.isComposing)return;
  event.preventDefault();const form=$('check-form');if(!$('submit').disabled&&form.reportValidity())await form.requestSubmit();
});
$('known-website').addEventListener('input',clearResult);
$('reviewed').addEventListener('change',clearResult);
$('content').addEventListener('input',()=>{clearResult();$('example-note').hidden=true;if(ocrReady)$('reviewed').checked=false;updateInputCount();});
$('example').addEventListener('click',()=>{clearResult();emailFile=null;$('email-file').value='';inputState();$('content').value=MODES[mode].example;updateInputCount();$('example-note').hidden=false;$('content').focus();});
$('file').addEventListener('change',()=>{clearResult();releasePreview();ocrReady=false;$('reviewed').checked=false;$('content').value='';inputState();const file=$('file').files[0];if(!file)return;if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size>64*1024*1024){$('error').textContent='Choose a PNG, JPEG or WebP no larger than 64 MiB.';$('error').hidden=false;$('file').value='';$('error').focus();return;}previewURL=URL.createObjectURL(file);$('preview').src=previewURL;$('file-name').textContent=file.name;$('preview-wrap').hidden=false;});
$('email-file').addEventListener('change',()=>{
  clearResult();emailFile=null;
  const file=$('email-file').files[0];
  if(file){
    if(!/\.eml$/i.test(file.name)||file.size>250000||!file.size){
      $('error').textContent='Choose an .eml email file between 1 and 250,000 bytes. For larger emails, paste the relevant message instead.';
      $('error').hidden=false;$('email-file').value='';$('error').focus();
    }else emailFile=file;
  }
  $('example-note').hidden=true;inputState();
});
$('email-file-clear').addEventListener('click',()=>{clearResult();emailFile=null;$('email-file').value='';inputState();$('content').focus();});
function validReport(report){
  const text=value=>typeof value==='string';
  const records=(value,check)=>Array.isArray(value)&&value.every(item=>item&&typeof item==='object'&&check(item));
  const credentials=report?.content_credentials;
  return report&&typeof report==='object'&&['text','url','email','call','image'].includes(report.kind)
    &&['low','guarded','high','critical'].includes(report.risk_level)&&text(report.summary)&&text(report.share_summary)
    &&records(report.evidence,item=>Number.isFinite(item.weight)&&item.weight>=-1&&item.weight<=1&&['verified','inferred','unknown'].includes(item.evidence_class)&&['title','detail','source'].every(key=>text(item[key])))
    &&records(report.actions,item=>text(item.title)&&text(item.detail))&&Array.isArray(report.limitations)&&report.limitations.every(text)
    &&(report.model_ran==null||typeof report.model_ran==='boolean')
    &&(credentials==null||(['verified','untrusted','invalid','absent','unavailable','external'].includes(credentials.status)&&text(credentials.detail)&&['signer','declaration'].every(key=>credentials[key]==null||text(credentials[key]))));
}
function showCrossChecks(report){
  const panel=$('cross-checks'),rows=$('cross-check-rows');rows.replaceChildren();$('cross-check-status').textContent='';panel.hidden=report.kind!=='image';if(panel.hidden)return;
  const add=(label,detail)=>rows.append(node('dt',label),node('dd',detail));
  const credentialLabels={verified:'Signature, file binding and signer trust validated under a local trust snapshot. This authenticates signed statements, not the scene.',untrusted:'Signature matches the file, but signer trust was not established. Declarations remain unverified.',invalid:'Credential validation failed. Signer and origin declarations cannot be relied on.',absent:'No embedded credentials found. This does not establish image origin.',unavailable:'No credential verification result is available.',external:'External credentials were not fetched or verified.'};
  add('Signed history',credentialLabels[report.content_credentials?.status]||'No signed-history result was reported.');
  const evidence=id=>report.evidence.some(item=>item.id===id);
  if(evidence('image:clip'))add('CLIP pattern classifier','Component output reported; see its score and limitations in the evidence below.');
  if(evidence('image:community'))add('CommunityForensics pattern classifier','Component output reported; see its score and limitations in the evidence below.');
  if(evidence('image:model'))add('Pattern-model decision',evidence('image:clip')&&evidence('image:community')?'Combined output derived from the reported pattern components. This is not a third independent model.':'Pattern-model output reported. A complete component breakdown was not reported.');
  $('cross-check-status').textContent=evidence('image:disagreement')?'Pattern components disagree. See the evidence and the reported decision rule; no new verdict is calculated here.':report.model_ran===false?'The detector did not return a model result. No pattern-model agreement is established.':'No component-disagreement finding was reported. This does not establish agreement between checks.';
}
function showReport(report){
  if(!validReport(report))throw new Error('The local server returned an incomplete report. Your input was kept. Retry with the launcher open.');
  showCrossChecks(report);currentReport=report;$('print-summary').textContent=report.share_summary;$('empty').hidden=true;$('loading').hidden=true;$('result').hidden=false;
  const image=report.kind==='image';$('manual-panel').hidden=image;
  const concerns=report.evidence.filter(e=>e.weight>0).length;
  const incompleteEmail=report.kind==='email'&&report.evidence.some(e=>e.id==='email:incomplete');
  const incompleteLinks=report.evidence.some(e=>e.id==='analysis:links_incomplete'||e.id==='email:links_incomplete'||e.id==='url:malformed'||(typeof e.id==='string'&&e.id.startsWith('url:malformed:')));
  const scope=report.kind==='image'?'image':report.kind==='text'&&ocrReady&&['screenshot','qr'].includes(mode)?mode:report.kind;
  const coverage={
    text:['The submitted wording and literal web addresses were checked for rule-based warning signs.','The sender, their story and hidden link destinations remain unverified. No address was visited; redirects were not followed.'],
    screenshot:['The text you reviewed after screenshot extraction was checked for wording and literal-address warning signs.','Recognition can miss text. The sender, image story and hidden link destinations remain unverified. No address was visited; redirects were not followed.'],
    qr:['The decoded text you reviewed was checked for wording and literal-address warning signs.','A readable QR code does not verify its publisher or destination. No address was visited; hidden targets and redirects remain unchecked.'],
    url:['The submitted address structure and any supplied known-site hostname were compared locally.','Ownership, sender identity, destination content and redirects remain unverified. Neither address was visited; a hostname match does not establish safety.'],
    email:['Available email wording, headers and extracted link addresses were checked locally.','Pasted or imported headers do not independently authenticate the sender. Attachments were not opened or scanned, and addresses and redirects were not visited.'],
    call:['The submitted transcript wording and literal web addresses were checked for warning signs.','The caller’s identity, voice and story remain unverified. No audio was checked, no address was visited and redirects were not followed.'],
    image:['This is an image-origin report. The evidence below states which components ran and which were unavailable.','No claim is made that every image component ran. Image origin cannot verify the depicted story, a sender, a seller or a payment request.']
  }[scope];
  $('coverage-checked').textContent=coverage[0];
  $('coverage-unverified').textContent=coverage[1]+(incompleteLinks?' Some links remain unchecked.':'');
  $('verdict-tag').textContent=image?(report.risk_level==='high'&&(report.model_ran||report.content_credentials?.status==='verified')?'LIKELY AI-GENERATED · NOT A SCAM VERDICT':report.risk_level==='guarded'?'INCONCLUSIVE · NOT A SCAM VERDICT':'IMAGE CHECK · NOT A SCAM VERDICT'):incompleteEmail||incompleteLinks?'CHECK INCOMPLETE':report.risk_level==='high'?'PAUSE & VERIFY':concerns?'TAKE A CLOSER LOOK':'STILL UNVERIFIED';
  $('verdict-tag').className='verdict-tag '+(image?(report.risk_level==='high'?'high':report.risk_level==='guarded'?'guarded':''):report.risk_level);
  if(image){
    $('verdict').textContent=report.risk_level==='high'&&(report.model_ran||report.content_credentials?.status==='verified')?'This image looks AI-generated':report.model_ran?(report.risk_level==='guarded'?'Can\'t tell if this image is real':'No AI patterns found')
      :report.content_credentials?.status==='verified'?'Signed provenance found'
      :report.content_credentials?.status==='unavailable'?'Image checks unavailable':'Credentials check complete';
  }else $('verdict').textContent=incompleteEmail?'This email needs a manual check.':incompleteLinks?(report.risk_level==='high'?'Pause; some links remain unchecked.':'Some links still need review.'):report.risk_level==='high'?'Don’t act on this request yet.':concerns?'There’s more to check.':'This request is still unverified.';
  $('result-summary').textContent=image?String(report.summary).replace(' (experimental)',''):report.summary;
  $('result-safety').hidden=image&&!report.model_ran;
  $('result-safety').textContent=image?''+(report.risk_level==='high'?'If this image is being used to sell something, ask for money, or announce a prize or emergency, treat that as a scam warning sign and verify through a source you already trust. ':'')+'AI image detection can be wrong, and this model has not passed release requirements yet, so check the evidence below and look for the original source before you share or act on an image. Image origin does not establish whether a message, sale or person is trustworthy.':'This reviews content, not a person’s honesty. A warning does not prove fraud; no warning does not prove safety.';
  $('credentials').replaceChildren();$('credentials').hidden=!report.content_credentials;
  if(report.content_credentials){const c=report.content_credentials;$('credentials').append(node('strong','Content Credentials: '+c.status),node('div',c.detail));if(c.signer)$('credentials').append(node('div','Signer: '+c.signer));if(c.declaration)$('credentials').append(node('div','Signed declaration: '+c.declaration));}
  $('evidence').replaceChildren();$('evidence-count').textContent=report.evidence.length+' observation'+(report.evidence.length===1?'':'s');
  const groups=image?[['Image and provenance evidence',report.evidence]]:[
    ['Warning signs to review',report.evidence.filter(e=>e.weight>0)],
    ['Observed facts',report.evidence.filter(e=>!(e.weight>0)&&e.evidence_class==='verified')],
    ['Still unknown',report.evidence.filter(e=>!(e.weight>0)&&e.evidence_class!=='verified')]
  ];
  groups.forEach(([title,items])=>{if(!items.length)return;const group=node('section',undefined,'evidence-group');group.append(node('h4',title,'evidence-group-title'));
    items.forEach(e=>{const item=node('article',undefined,'evidence-item');item.append(node('span',({verified:'Observed / verified',inferred:'Inference',unknown:'Not verified'})[e.evidence_class],'evidence-label '+e.evidence_class),node('h5',e.title),node('p',e.detail),node('p',e.source,'small'));group.append(item);});$('evidence').append(group);});
  $('actions').replaceChildren();report.actions.forEach(a=>{const li=node('li');li.append(node('strong',a.title),node('p',a.detail));$('actions').append(li);});
  $('result-recovery').hidden=image;
  $('limits').replaceChildren();report.limitations.forEach(t=>$('limits').append(node('li',t)));
  window.VerificationPlan?.show(!image);$('verdict').focus({preventScroll:true});if(window.innerWidth<681)$('result').scrollIntoView({behavior:'auto',block:'start'});
}
$('check-form').addEventListener('submit',async event=>{
  event.preventDefault();clearResult();const token=generation;const extracting=['screenshot','qr'].includes(mode)&&!ocrReady;const selectedMode=['screenshot','qr'].includes(mode)?'text':mode;controller=new AbortController();const activeController=controller;let timedOut=false;
  const timer=setTimeout(()=>{timedOut=true;activeController.abort();},mode==='image'?120000:extracting?45000:15000);
  $('empty').hidden=true;$('loading').hidden=false;$('submit').disabled=true;$('check-form').setAttribute('aria-busy','true');
  $('loading-text').textContent=mode==='image'?'Checking signed credentials, then local visual patterns when needed. The first image may take a minute while the model loads.':extracting&&mode==='qr'?'Decoding QR text on this computer. No destination is opened. Review every code before checking.':emailFile?'Reading the email file locally. Attachments are not opened or scanned.':extracting?'Reading the screenshot with Windows OCR on this computer. You will review the text before it is checked.':'Checking the wording and address structure on this computer.';
  try{
    let body,headers={};
    if(ocrReady&&!$('reviewed').checked)throw new Error('Review the recognized text and confirm it before checking.');
    if(emailFile){body=new FormData();body.append('file',emailFile);}
    else if(mode==='image'||extracting){if(!$('file').files[0])throw new Error('Choose an image first.');body=new FormData();body.append('file',$('file').files[0]);}
    else {const key=({text:'text',url:'url',email:'raw_email',call:'transcript'})[selectedMode];body=JSON.stringify({[key]:selectedMode==='url'?$('content').value:$('content').value.trim(),...(selectedMode==='url'&&!/^ *$/.test($('known-website').value)?{known_website:$('known-website').value}:{})});headers={'Content-Type':'application/json'};}
    const response=await fetch(emailFile?'/api/analyze/email-file':extracting?'/api/extract/'+mode:'/api/analyze/'+selectedMode,{method:'POST',headers,body,signal:controller.signal});
    const data=await response.json().catch(()=>{throw new Error('The local server returned an unreadable response. Your input was kept. Retry with the launcher open.');});if(!response.ok)throw new Error(typeof data?.detail==='string'?data.detail:'Please check the input length and format, then try again.');
    if(token===generation){
      if(extracting){if(!data||typeof data.text!=='string'||data.text.length>30000||typeof data.notice!=='string'||(mode==='qr'&&data.review_required!==true))throw new Error('The extracted text could not be reviewed. Try a clearer image or paste the message manually.');ocrReady=true;$('content').value=data.text;$('reviewed').checked=false;$('ocr-notice').textContent=data.text?data.notice:'No readable text was found. Type the message below or try a clearer crop.'+(mode==='screenshot'?' For a transparent image, use an opaque copy with a contrasting background. A white background can hide white text.':'')+' Review it before checking.';inputState();$('loading').hidden=true;$('empty').hidden=false;$('content').focus();}
      else showReport(data);
    }
  }catch(error){if((error.name!=='AbortError'||timedOut)&&token===generation){$('error').textContent=timedOut?'This check took too long. Keep the launcher open and try again; you can also paste the message manually.':error instanceof TypeError?'Could not reach the local server. Keep the TrustLens launcher running, then retry.':error.message;$('error').hidden=false;$('loading').hidden=true;$('empty').hidden=false;$('error').focus();}}
  finally{clearTimeout(timer);if(token===generation){$('submit').disabled=false;$('check-form').setAttribute('aria-busy','false');}}
});
async function copyText(text){
  let timer;
  try{await Promise.race([navigator.clipboard.writeText(text),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('Clipboard timed out')),3000);})]);}
  finally{clearTimeout(timer);}
}
$('copy').addEventListener('click',async()=>{if(!currentReport)return;const token=generation;try{await copyText(currentReport.share_summary);if(token===generation)$('copy-status').textContent='Copied. Original content and contact details are omitted.';}catch{if(token===generation)$('copy-status').textContent='Clipboard access is unavailable. Use Download instead.';}});
function downloadSummary(summary,filename){
  const url=URL.createObjectURL(new Blob([summary],{type:'text/plain;charset=utf-8'}));const a=node('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('download').addEventListener('click',()=>{if(currentReport)downloadSummary(currentReport.share_summary,'trustlens-safe-summary.txt');});
function clearManualSteps(){manualVersion++;manualTopics=null;$('manual-result').hidden=true;$('manual-steps').replaceChildren();$('manual-status').textContent='';}
function clearManualGuidance(){clearManualSteps();document.querySelectorAll('[data-topic]').forEach(input=>{input.checked=false;});$('manual-panel').hidden=true;$('manual-guidance').open=false;}
document.querySelectorAll('[data-topic]').forEach(input=>input.addEventListener('change',clearManualSteps));
$('manual-form').addEventListener('submit',event=>{
  event.preventDefault();clearManualSteps();if(!currentReport||currentReport.kind==='image')return;
  const topics=[...document.querySelectorAll('[data-topic]')].filter(input=>input.checked).map(input=>input.dataset.topic);
  if(!topics.length){$('manual-status').textContent='Choose at least one request, then show the selected steps.';return;}
  if(typeof PocketGuide==='undefined'){$('manual-status').textContent='The selected-step guide could not load. Keep the local launcher open and reload to try again.';return;}
  manualTopics=topics;
  PocketGuide.nextSteps(topics).forEach(([title,detail])=>{const li=node('li');li.append(node('strong',title),node('p',detail));$('manual-steps').append(li);});
  $('manual-result').hidden=false;$('manual-heading').focus();
});
$('manual-copy').addEventListener('click',async()=>{
  if(!manualTopics)return;const version=manualVersion,summary=PocketGuide.summary(manualTopics);
  try{await copyText(summary);if(version===manualVersion)$('manual-status').textContent='Copied user-selected steps. No original input is included.';}
  catch{if(version===manualVersion)$('manual-status').textContent='Clipboard unavailable. Use Download selected steps instead.';}
});
$('manual-download').addEventListener('click',()=>{if(manualTopics)downloadSummary(PocketGuide.summary(manualTopics),'trustlens-user-selected-steps.txt');});
$('print').addEventListener('click',()=>{if(!currentReport)return;$('print-summary').textContent=currentReport.share_summary;window.print();});
$('about-open').addEventListener('click',()=>$('about-dialog').showModal());
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>$(b.dataset.close).close()));
let recoveryPlans=null, recoverySelection=null, recoveryToken=0;
function validRecoveryPlans(plans){
  const text=(value,max)=>typeof value==='string'&&value.trim().length>0&&value.length<=max;
  return Array.isArray(plans)&&plans.length>0&&plans.length<=4&&new Set(plans.map(plan=>plan?.id)).size===plans.length
    &&plans.every(plan=>plan&&typeof plan==='object'&&!Array.isArray(plan)&&typeof plan.id==='string'&&/^[a-z][a-z0-9_-]{0,31}$/.test(plan.id)
      &&text(plan.label,80)&&text(plan.title,160)&&Array.isArray(plan.steps)&&plan.steps.length>0&&plan.steps.length<=8&&plan.steps.every(step=>text(step,1000)));
}

function chooseRecovery(plan){
  recoveryToken++;recoverySelection=plan;$('recovery-plan').hidden=false;$('recovery-heading').textContent=plan.title;$('recovery-steps').replaceChildren(...plan.steps.map(s=>node('li',s)));$('recovery-copy-status').textContent='';
  [...$('recovery-options').children].forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.plan===plan.id)));$('recovery-heading').focus();
}
async function openRecovery(){
  const token=++recoveryToken;recoverySelection=null;$('recovery-plan').hidden=true;$('recovery-options').replaceChildren();$('recovery-status').textContent='Loading the checklist…';$('recovery-dialog').showModal();
  try{
    if(!recoveryPlans){const response=await fetch('/api/recovery',{signal:AbortSignal.timeout(10000)});if(!response.ok)throw new Error();const plans=(await response.json())?.plans;if(!validRecoveryPlans(plans))throw new Error();if(token!==recoveryToken||!$('recovery-dialog').open)return;recoveryPlans=plans;}
    if(token!==recoveryToken||!$('recovery-dialog').open)return;
    $('recovery-status').textContent='';recoveryPlans.forEach(plan=>{const b=node('button',plan.label,'secondary');b.dataset.plan=plan.id;b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>chooseRecovery(plan));$('recovery-options').append(b);});
  }catch{if(token===recoveryToken)$('recovery-status').textContent='The checklist could not load. Use the FTC guide below, or reopen this panel to retry.';}
}
document.querySelectorAll('[data-recovery]').forEach(b=>b.addEventListener('click',openRecovery));
$('recovery-dialog').addEventListener('close',()=>{recoveryToken++;});
$('recovery-copy').addEventListener('click',async()=>{const plan=recoverySelection,token=recoveryToken;if(!plan)return;try{await copyText('TrustLens — recovery checklist\n'+plan.title+'\n\n'+plan.steps.join('\n\n')+'\n\nGeneral guidance: https://consumer.ftc.gov/articles/what-do-if-you-were-scammed\nRecovery is not guaranteed.');if(token===recoveryToken&&plan===recoverySelection)$('recovery-copy-status').textContent='Copied. No personal details are included.';}catch{if(token===recoveryToken&&plan===recoverySelection)$('recovery-copy-status').textContent='Clipboard unavailable. You can select and copy the checklist text.';}});
$('capability-refresh').addEventListener('click',async()=>{
  const button=$('capability-refresh'),hadFocus=document.activeElement===button;button.disabled=true;$('capability-status').textContent='Checking local configuration…';
  try{
    const response=await fetch('/api/capabilities',{signal:AbortSignal.timeout(10000)});
    if(!response.ok)throw new Error();
    const data=await response.json();
    const labels=[['screenshot_ocr','Screenshot text extraction'],['image_detector','Experimental image detector'],['content_credentials','Content Credentials']];
    if(typeof data.message_rules!=='boolean'||labels.some(([key])=>typeof data[key]?.configured!=='boolean'))throw new Error();
    $('capability-list').replaceChildren(node('li','Message, link, email and call rules: '+(data.message_rules?'available locally':'unavailable')));
    labels.forEach(([key,label])=>{const item=data[key];$('capability-list').append(node('li',label+': '+(item.configured?'configured; runtime not verified':'not configured')+(item.detail?' — '+item.detail:'')));});
    const qr=data.qr_reader;$('capability-list').append(node('li','QR code reader: '+(typeof qr?.configured==='boolean'?(qr.configured?'configured; runtime not verified':'not configured')+(qr.detail?' — '+qr.detail:''):'configuration unknown; refresh with the latest local server')));
    $('capability-status').textContent='Configuration checked. Availability can still change during a check.';
  }catch{
    $('capability-list').replaceChildren(node('li','Current availability is unknown. Keep the local launcher running and retry.'));
    $('capability-status').textContent='Could not read local configuration. You can still try a content check.';
  }finally{button.disabled=false;button.textContent='Refresh availability';if(hadFocus&&(document.activeElement===document.body||document.activeElement===button))button.focus();}
});

function clearPrivatePage(){
  resetInput();recoveryToken++;recoverySelection=null;
  $('ocr-notice').replaceChildren();$('recovery-plan').hidden=true;
  ['recovery-options','recovery-heading','recovery-steps','recovery-status','recovery-copy-status'].forEach(id=>$(id).replaceChildren());
  if($('recovery-dialog').open)$('recovery-dialog').close();
}
window.addEventListener('pagehide',clearPrivatePage);
window.addEventListener('pageshow',event=>{if(event.persisted)clearPrivatePage();});
// Enable only after the controller has installed every handler.
$('submit').disabled=false;
