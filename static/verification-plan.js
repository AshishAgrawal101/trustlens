'use strict';
(() => {
  const get=id=>document.getElementById(id), panel=get('verification-plan');
  const routes=[...document.querySelectorAll('[data-route]')];
  const plans={
    app:{title:'Open an app or website you already trust',steps:['Leave the supplied link alone. Open the official app or type an address you already know independently.','Check the request there, or use that service’s established support route. Do not enter a password or security code into the supplied link.','If you cannot confirm the request, pause before responding or paying.']},
    number:{title:'Start a new call using a known number',steps:['End the unexpected call or leave the message. Do not use its phone number or caller ID.','Use a number on your bank card, a previous trusted record, or an independently known official source.','Describe the request without giving a password or one-time code. If you cannot confirm it, pause.']},
    person:{title:'Talk privately with someone you trust',steps:['Pause the request and speak with a trusted friend, family member or other person you know.','Explain what was requested. Use an existing contact record or speak in person; do not rely on the request’s new number or a familiar-sounding voice.','If you still cannot independently confirm the story, do not rush into payment or sharing account access.']}
  };
  let selected=null, version=0;
  function reset(){version++;selected=null;panel.hidden=true;get('verification-choice').hidden=true;get('verification-steps').replaceChildren();get('verification-heading').textContent='';get('verification-status').textContent='';routes.forEach(button=>button.setAttribute('aria-pressed','false'));}
  function show(visible){reset();panel.hidden=!visible;}
  function summary(){const plan=plans[selected];return 'TrustLens — user-selected verification plan\n'+plan.title+'\n\n'+plan.steps.join('\n\n')+'\n\nThis is a plan, not completed verification or proof of safety. Original input and its contact details are omitted.';}
  routes.forEach(button=>button.addEventListener('click',()=>{
    const key=button.dataset.route;if(panel.hidden||!Object.hasOwn(plans,key))return;
    version++;selected=key;routes.forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    get('verification-heading').textContent=plans[key].title;get('verification-steps').replaceChildren();
    plans[key].steps.forEach(text=>{const item=document.createElement('li');item.textContent=text;get('verification-steps').append(item);});
    get('verification-status').textContent='';get('verification-choice').hidden=false;get('verification-heading').focus();
  }));
  get('verification-copy').addEventListener('click',async()=>{
    if(panel.hidden||!selected)return;const token=version,text=summary();
    try{await copyText(text);if(token===version&&!panel.hidden)get('verification-status').textContent='Copied your fixed plan. Original content and contact details are omitted.';}
    catch{if(token===version&&!panel.hidden)get('verification-status').textContent='Clipboard unavailable. Use Download plan instead.';}
  });
  get('verification-download').addEventListener('click',()=>{if(!panel.hidden&&selected)downloadSummary(summary(),'trustlens-verification-plan.txt');});
  window.VerificationPlan={reset,show};reset();
})();
