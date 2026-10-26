// Reuse the existing phone DOM double; no browser or platform installation claim.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'../static/phone');
const guide=require('../static/phone/guide.js');
const harness=fs.readFileSync(path.join(__dirname,'phone_companion.test.cjs'),'utf8');
const setupSource=harness.slice(harness.indexOf('function phonePage('),harness.indexOf("test('phone edits"));
function setup(writeText=async()=>{}){
  const blobs=[],revoked=[],downloads=[];
  const fixture={fs,path,vm,root,guide,Blob,URL:{createObjectURL(blob){blobs.push(blob);return 'blob:recovery';},revokeObjectURL(url){revoked.push(url);}}};
  vm.runInNewContext(setupSource+';this.setup=phonePage;',fixture);
  const p=fixture.setup(writeText);
  Object.getPrototypeOf(p.ids.message).click=function(){downloads.push(this.download);};
  return {...p,blobs,revoked,downloads};
}
test('four offline recovery choices show only selected fixed steps and focus their heading',()=>{
  const p=setup();
  const cases=[['money',/payment provider/,/stopped or reversed/],['account',/affected account/,/trusted device/],['device',/remote-access/,/Disconnect/],['link',/entering information/,/account checklist/]];
  for(const [key,title,step] of cases){
    p.ids['recovery-'+key].fire('click');
    assert.equal(p.ids['recovery-result'].hidden,false);assert.match(p.ids['recovery-title'].textContent,title);assert.match(p.ids['recovery-steps'].textContent,step);
    assert.equal(p.ids['recovery-steps'].children.length,2);assert.equal(p.document.activeElement,p.ids['recovery-title']);
    for(const [other] of cases)assert.equal(p.ids['recovery-'+other].ariaPressed,String(other===key));
  }
});
test('recovery exports fixed input-free guidance and releases its download URL',async()=>{
  const copied=[],p=setup(async text=>copied.push(text));p.ids.message.value='PRIVATE account https://private.test TOKEN';
  p.ids['recovery-money'].fire('click');await p.ids['recovery-copy'].fire('click');p.ids['recovery-download'].fire('click');
  const summary=await p.blobs[0].text();assert.equal(summary,copied[0]);assert.doesNotMatch(summary,/PRIVATE|private.test|TOKEN/);
  assert.match(summary,/General U.S./);assert.match(summary,/Recovery is not guaranteed/);assert.match(summary,/consumer.ftc.gov/);
  assert.deepEqual(p.downloads,['trustlens-pocket-recovery.txt']);[...p.timers.values()][0]();assert.deepEqual(p.revoked,['blob:recovery']);
});
test('recovery clipboard timeout is actionable and stale completion cannot label a new selection',async()=>{
  const p=setup(()=>new Promise(()=>{}));p.ids['recovery-account'].fire('click');const pending=p.ids['recovery-copy'].fire('click');
  [...p.timers.values()][0]();await pending;assert.match(p.ids['recovery-status'].textContent,/Download checklist/);
  let resolve;const q=setup(()=>new Promise(r=>resolve=r));q.ids['recovery-money'].fire('click');const copying=q.ids['recovery-copy'].fire('click');
  q.ids['recovery-device'].fire('click');resolve();await copying;assert.equal(q.ids['recovery-status'].textContent,'');
});
test('Clear and page exit erase recovery selection and invalidate pending status and exports',async()=>{
  let reject;const p=setup(()=>new Promise((resolve,r)=>reject=r));p.ids['recovery-link'].fire('click');const pending=p.ids['recovery-copy'].fire('click');
  p.ids.clear.fire('click');reject(new Error('denied'));await pending;
  assert.equal(p.ids['recovery-result'].hidden,true);assert.equal(p.ids['recovery-title'].textContent,'');assert.equal(p.ids['recovery-status'].textContent,'');
  p.ids['recovery-download'].fire('click');assert.equal(p.blobs.length,0);
  p.ids['recovery-device'].fire('click');p.windowEvents.pagehide();assert.equal(p.ids['recovery-steps'].textContent,'');assert.equal(p.ids['recovery-device'].ariaPressed,'false');
});
test('recovery markup keeps limits and explicit external FTC guide visible',()=>{
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  assert.match(html,/General U.S. guidance in English/);assert.match(html,/Recovery is not guaranteed/);assert.match(html,/This external guide uses the internet/);
  for(const id of ['money','account','device','link'])assert.match(html,new RegExp('id="recovery-'+id+'" type="button"'));
});
