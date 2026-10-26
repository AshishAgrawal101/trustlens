'use strict';
const ClaimReview=(()=>{
  const steps=[
    'Find the earliest original account and read its full context, including qualifications and corrections.',
    'Trace each account to its underlying evidence. Different websites may repeat one press release, witness or image.',
    'Check publication and event dates separately. For images, check the original caption, place and date; this worksheet does not inspect pixels.',
    'Look for evidence that challenges the claim. Keep it unresolved when you cannot establish the context before sharing or acting.'
  ];
  const PLAN='TrustLens — independent claim-checking plan\nThis is not a truth verdict. No source was visited or verified.\n\n'+steps.map((step,index)=>(index+1)+'. '+step).join('\n\n')+'\n\nYour claim, context, source addresses, quotations and dates are omitted.';
  function sourceUrlError(message,field){const error=new Error(message);error.field=field;return error;}
  function validDate(value){return /^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value+'T00:00:00Z'))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;}
  function review(input,today){
    const fields={};
    for(const key of ['claim','context','aUrl','aQuote','aDate','bUrl','bQuote','bDate']){
      const value=input[key]??'';
      if(typeof value!=='string'||value.length>(key.endsWith('Url')?4096:key.endsWith('Date')?10:4000))throw new Error('Check the field lengths and formats, then review again.');
      fields[key]=value.trim();
    }
    if(!fields.claim)throw new Error('Enter one specific claim before reviewing its context.');
    if(!validDate(today))throw new Error('A valid calendar date is needed for this review.');
    const suppliedEvent=input.eventDate===undefined?'':input.eventDate;
    if(typeof suppliedEvent!=='string'||suppliedEvent.length>10)throw new Error('Use a valid calendar date for the supplied event date, or leave it blank.');
    const eventDate=suppliedEvent.trim();
    if(eventDate&&!validDate(eventDate))throw new Error('Use a valid calendar date for the supplied event date, or leave it blank.');
    for(const key of ['aRole','bRole']){
      const role=input[key]===undefined?'unsure':input[key];
      if(!['unsure','supports','challenges','context'].includes(role))throw new Error('Choose one of the available source labels, then review again.');
      fields[key]=role;
    }
    const observations=[],questions=[],labels=[],activeRoles=[];
    const add=(list,id,text)=>list.push({id,text});
    const hosts=[];
    for(const key of ['a','b']){
      const label=key==='a'?'Source A':'Source B',url=fields[key+'Url'],quote=fields[key+'Quote'],date=fields[key+'Date'];
      if(url||quote){
        const role=fields[key+'Role'];activeRoles.push(role);
        add(labels,'labels:'+key+':'+role,label+': you labelled this account as '+({unsure:'unsure',supports:'supporting the claim',challenges:'challenging the claim',context:'adding context'})[role]+'. This records your interpretation, not a detected finding.');
      }else add(labels,'labels:'+key+':missing',label+': no address or quotation was supplied. Its selected role is not counted as an account.');
      if(url){
        if(!/^https?:\/\/[^/\\?#\s]/i.test(url))throw sourceUrlError('Use a complete HTTP or HTTPS source address. No source was opened.',key+'Url');
        let parsed;
        try{parsed=new URL(url);}catch{throw sourceUrlError('Use a complete HTTP or HTTPS source address. No source was opened.',key+'Url');}
        if(!['http:','https:'].includes(parsed.protocol)||!parsed.hostname||parsed.username||parsed.password||/[\u0000-\u0020\u007f\\]/.test(url))throw sourceUrlError('Use an HTTP or HTTPS address without embedded login details or control characters. No source was opened.',key+'Url');
        hosts.push(parsed.hostname);
      }else add(questions,'source:'+key+':missing_url',label+': find the original source address or record where this account came from.');
      if(url&&!quote)add(questions,'source:'+key+':missing_quote',label+': inspect the full account and record the words or evidence relevant to this specific claim.');
      if(quote&&!url)add(questions,'source:'+key+':quote_unattributed',label+': a supplied quotation without an address cannot be traced here.');
      if(!date&&(url||quote))add(questions,'source:'+key+':missing_date',label+': publication date is missing. Check it against the date of the event or image.');
      if(date){
        if(!validDate(date))throw new Error('Use a valid calendar date for each supplied publication date.');
        if(date>today)add(questions,'source:'+key+':future_date',label+': the supplied publication date is later than today. Check for a typo, scheduled publication or missing context; this does not disprove the claim.');
        if(eventDate&&(url||quote)){
          const days=(Date.parse(date+'T00:00:00Z')-Date.parse(eventDate+'T00:00:00Z'))/86400000;
          const relation=days<0?'before':days>0?'after':'same',gap=Math.abs(days);
          const timing=days===0?'on the same calendar date as':gap.toLocaleString('en-US')+' calendar '+(gap===1?'day':'days')+' '+relation;
          add(observations,'dates:'+key+':'+relation,label+': its supplied publication date is '+timing+' the supplied event date. Both dates remain unverified.'+(days<0?' Earlier publication may describe an announcement or a different event; it is not a contradiction finding.':' This ordering does not establish what happened or whether the claim is true.'));
        }
      }
    }
    const count=hosts.length;
    add(observations,'sources:'+['zero','one','two'][count],['No source addresses were supplied.','One source address was supplied; its content was not checked.','Two source addresses were supplied; neither source content was checked.'][count]);
    if(count===2){
      const same=hosts[0]===hosts[1];
      add(observations,'hosts:'+(same?'same':'different'),same?'The supplied addresses have the same parsed hostname. This does not establish independent reporting.':'The supplied addresses have different parsed hostnames. This does not establish independent reporting.');
      add(questions,'sources:independence','Trace whether both accounts rely on the same original report, witness, press release or image. Website count is not independent evidence.');
    }
    if(!fields.context)add(questions,'context:missing','Record where the claim appeared and what came before or after it. The setting and original context remain unresolved.');
    if(fields.aQuote&&fields.bQuote){
      add(questions,'quotes:compare','Compare each supplied quotation with its full source. Agreement, contradiction and factual meaning have not been checked here.');
      if(fields.aQuote===fields.bQuote)add(observations,'quotes:identical','The two quotations are identical after trimming surrounding whitespace. Repeated wording does not corroborate truth or establish independent evidence.');
    }
    if(fields.aDate||fields.bDate)add(questions,'dates:context','These are supplied publication dates, not verified event dates. Earlier, later or recent publication does not establish whether the claim is true.');
    if(eventDate){
      add(observations,'dates:event_supplied','An event date was supplied by you; it was not independently verified.');
      add(questions,'dates:event_context','Check what the supplied event and publication dates each describe, using the original accounts. A calendar-day difference does not authenticate a source, establish independence or settle the claim.');
    }
    const support=activeRoles.includes('supports'),challenge=activeRoles.includes('challenges');
    const opposedSameQuote=support&&challenge&&fields.aQuote&&fields.aQuote===fields.bQuote;
    if(opposedSameQuote)add(questions,'labels:opposed_same_quote','You assigned support and challenge labels to identical supplied quotations. Compare the surrounding context and explain your interpretations; this is not a detected factual contradiction.');
    if(support&&!challenge)add(questions,'coverage:no_challenge','You labelled accounts as supporting the claim, but none as challenging it. Look for relevant contrary evidence; different positions do not require equal weight.');
    if(challenge&&!support)add(questions,'coverage:no_support','You labelled accounts as challenging the claim, but none as supporting it. Inspect the original claim and its stated evidence; different positions do not require equal weight.');
    if(!support&&!challenge)add(questions,'labels:unresolved','The supplied accounts have no support/challenge labels yet. They may add context or remain uncertain; no conclusion about the claim follows.');
    add(questions,'labels:human_judgment','Source roles are your judgments. The app has not checked relevance, reliability, factual support or source independence.');
    const nextStep=count===0?'Next: locate an original source account before interpreting the claim.'
      :questions.some(row=>row.id.endsWith(':future_date'))?'Next: clarify the supplied future publication date and the actual event date.'
      :questions.some(row=>row.id.endsWith(':missing_quote'))?'Next: read the full source and record the evidence relevant to the claim.'
      :opposedSameQuote?'Next: compare the surrounding context of the identical quotations and explain your different labels.'
      :support&&!challenge?'Next: look for relevant evidence that could challenge your interpretation.'
      :challenge&&!support?'Next: inspect the original claim and the evidence offered for it.'
      :'Next: compare what the accounts actually establish, keeping the claim unresolved.';
    return {observations,questions,labels,nextStep,steps:[...steps]};
  }
  // Preserve the original worksheet result contract for existing callers.
  function analyze(input,today){const {observations,questions,steps}=review(input,today);return {observations,questions,steps};}
  return {analyze,review,PLAN};
})();
if(typeof module==='object'&&module.exports)module.exports=ClaimReview;

if(typeof document!=='undefined'){
  const get=id=>document.getElementById(id),form=get('claim-form'),correctionButton=get('claim-correct-source');
  const fieldIds={claim:'claim-text',context:'claim-context',eventDate:'claim-event-date',aUrl:'source-a-url',aQuote:'source-a-quote',aDate:'source-a-date',bUrl:'source-b-url',bQuote:'source-b-quote',bDate:'source-b-date',aRole:'source-a-role',bRole:'source-b-role'};
  const sourceIds=['source-a-url','source-a-quote','source-a-date','source-a-role','source-b-url','source-b-quote','source-b-date','source-b-role'];
  const sourceErrors={aUrl:{id:'source-a-url',label:'Source A address'},bUrl:{id:'source-b-url',label:'Source B address'}};
  let generation=0,correction=null;
  function hasSourceEntries(){return sourceIds.some(id=>id.endsWith('-role')?get(id).value!=='unsure'&&get(id).value!=='':Boolean(get(id).value.trim()));}
  function syncSources(){const present=hasSourceEntries();get('claim-sources-state').hidden=!present;get('claim-sources-state').textContent=present?'Entries present · included in Review':'';}
  function clearCorrection(){correction=null;if(correctionButton){correctionButton.hidden=true;correctionButton.textContent='';}for(const field of Object.values(sourceErrors)){get(field.id).removeAttribute('aria-invalid');get(field.id).setAttribute('aria-describedby','source-url-help');}}
  function invalidate(){generation++;clearCorrection();get('claim-result').hidden=true;get('claim-error').hidden=true;['claim-observations','claim-questions','claim-labels','claim-review-status','claim-next-steps','claim-copy-status','claim-error'].forEach(id=>get(id).replaceChildren());get('claim-copy-plan').disabled=true;get('claim-download-plan').disabled=true;syncSources();}
  function clear(){invalidate();Object.values(fieldIds).forEach(id=>get(id).value='');get('source-a-role').value='unsure';get('source-b-role').value='unsure';syncSources();get('claim-sources').open=false;}
  function items(id,rows){const list=get(id);for(const row of rows){const item=document.createElement('li');item.textContent=typeof row==='string'?row:row.text;list.append(item);}}
  Object.values(fieldIds).forEach(id=>get(id).addEventListener('input',invalidate));
  get('claim-event-date').addEventListener('change',invalidate);
  ['source-a-role','source-b-role'].forEach(id=>get(id).addEventListener('change',invalidate));
  form.addEventListener('invalid',event=>{invalidate();if(sourceIds.some(id=>get(id)===event.target))get('claim-sources').open=true;},true);
  form.addEventListener('submit',event=>{
    event.preventDefault();invalidate();if(!form.reportValidity())return;
    try{
      const date=new Date(),today=[date.getFullYear(),String(date.getMonth()+1).padStart(2,'0'),String(date.getDate()).padStart(2,'0')].join('-');
      const input=Object.fromEntries(Object.entries(fieldIds).map(([key,id])=>[key,get(id).value]));
      const result=ClaimReview.review(input,today);
      items('claim-observations',result.observations);items('claim-questions',result.questions);items('claim-labels',result.labels);get('claim-review-status').textContent=result.nextStep;items('claim-next-steps',result.steps);
      get('claim-result').hidden=false;get('claim-copy-plan').disabled=false;get('claim-download-plan').disabled=false;get('claim-result-title').focus();get('claim-result-title').scrollIntoView({block:'start'});
    }catch(error){if(hasSourceEntries())get('claim-sources').open=true;const field=Object.hasOwn(sourceErrors,error.field)?sourceErrors[error.field]:null;get('claim-error').textContent=(field?field.label+': ':'')+error.message;if(field){correction=field;get(field.id).setAttribute('aria-invalid','true');get(field.id).setAttribute('aria-describedby','source-url-help claim-error');if(correctionButton){correctionButton.textContent='Correct '+field.label;correctionButton.hidden=false;}}get('claim-error').hidden=false;get('claim-error').focus();}
  });
  correctionButton?.addEventListener('click',()=>{if(!correction||correctionButton.hidden||get('claim-error').hidden)return;get('claim-sources').open=true;get(correction.id).focus();});
  get('claim-clear').addEventListener('click',()=>{clear();get('claim-text').focus();});
  const examples={
    caption:{claim:'This photo shows the town square after the storm on 15 June 2024.',context:'Constructed example: a cropped image was reposted without its original caption. The event date below is supplied for this example, not inferred or verified.',eventDate:'2024-06-15',aUrl:'https://archive.example/photo',aQuote:'Town square following a storm.',aDate:'2020-06-15',bUrl:'https://repost.example/post',bQuote:'Town square following a storm.'},
    headline:{claim:'The library is permanently closing next month.',context:'Constructed example: a forwarded headline omits the article body.',aUrl:'https://news.example/library',aQuote:'The library building will close for renovation.',bUrl:'https://library.example/notice',bQuote:'Services continue at the temporary branch.'},
    endorsement:{claim:'These headphones last twice as long.',context:'Constructed sponsored headphone post. No comparison model or test settings are supplied, and no independent results are provided. Identify the comparison models, test conditions and relevant independent results before interpreting the claim. Sponsorship alone does not establish whether it is true or false.'}
  };
  document.querySelectorAll('[data-claim-example]').forEach(button=>button.addEventListener('click',()=>{clear();const example=examples[button.getAttribute('data-claim-example')];if(example)for(const [key,value]of Object.entries(example))get(fieldIds[key]).value=value;syncSources();get('claim-sources').open=hasSourceEntries();get('claim-text').focus();}));
  function routeExample(){
    const hash=window.location?.hash||'',match=/^#example=(caption|headline|endorsement)$/.exec(hash);
    if(!match||match[0]!==hash)return;
    const button=[...document.querySelectorAll('[data-claim-example]')].find(button=>button.getAttribute('data-claim-example')===match[1]);
    if(!button)return;
    button.click();
    history.replaceState(null,'',window.location.pathname+window.location.search);
  }
  window.addEventListener('hashchange',routeExample);
  get('claim-copy-plan').addEventListener('click',async()=>{
    if(get('claim-result').hidden)return;const token=generation;let timer;get('claim-copy-plan').disabled=true;
    try{await Promise.race([navigator.clipboard.writeText(ClaimReview.PLAN),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('timeout')),1500);})]);if(token===generation)get('claim-copy-status').textContent='Input-free checking plan copied.';}
    catch{if(token===generation)get('claim-copy-status').textContent='Could not copy. Download the plan instead.';}
    finally{clearTimeout(timer);if(token===generation)get('claim-copy-plan').disabled=false;}
  });
  get('claim-download-plan').addEventListener('click',()=>{
    if(get('claim-result').hidden)return;
    const url=URL.createObjectURL(new Blob([ClaimReview.PLAN],{type:'text/plain;charset=utf-8'})),link=document.createElement('a');link.href=url;link.download='TrustLens-checking-plan.txt';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);get('claim-copy-status').textContent='Input-free plan download requested.';
  });
  window.addEventListener('pagehide',clear);window.addEventListener('pageshow',event=>{if(event.persisted)clear();});
  clear();get('claim-review-submit').disabled=false;routeExample();
}
