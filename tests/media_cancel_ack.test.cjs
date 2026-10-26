// Constructed controller only; no browser, uploads or backend processing.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const prefix=fs.readFileSync(path.join(__dirname,'media_context.test.cjs'),'utf8').split("test('metadata yields")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};
vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;this.file=file;this.report=report;',fixture);
const ACK='Stopped waiting for this inspection. Your selection and caption are kept here. Local processing may continue.';
async function pending(x){await fixture.file(x);x.ids['media-caption'].value='PRIVATE CAPTION';let resolve,reject;x.state.fetch=()=>new Promise((a,b)=>{resolve=a;reject=b;});const task=x.ids['media-form'].fire('submit');await x.ids['media-cancel'].fire('click');return {task,resolve,reject};}

test('Cancel acknowledges stopped waiting while preserving file preview caption and focus',async()=>{
 const x=fixture.setup(),operation=await pending(x);
 assert.equal(x.ids['media-status'].textContent,ACK);assert.doesNotMatch(ACK,/PRIVATE/);
 assert.equal(x.ids['media-caption'].value,'PRIVATE CAPTION');assert.equal(x.ids['media-file'].files[0].name,'PRIVATE_FILENAME.png');assert.equal(x.ids['media-preview'].src,'blob:fixture');assert.equal(x.revoked.length,0);
 assert.equal(x.document.activeElement,x.ids['media-file']);assert.equal(x.requests[0].options.signal.aborted,true);assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-submit'].disabled,false);
 operation.resolve({ok:true,json:async()=>fixture.report()});await operation.task;assert.equal(x.ids['media-status'].textContent,ACK);assert.equal(x.ids['media-result'].hidden,true);
});

test('late cancelled failure cannot replace acknowledgment or focus an error',async()=>{
 const x=fixture.setup(),operation=await pending(x);const active=x.document.activeElement;operation.reject(new Error('PRIVATE failure'));await operation.task;
 assert.equal(x.ids['media-status'].textContent,ACK);assert.equal(x.ids['media-error'].hidden,true);assert.equal(x.document.activeElement,active);
});

test('edit replacement Clear retry exit and persisted Back erase the old acknowledgment',async()=>{
 for(const reset of ['edit','replace','clear','retry','pagehide','pageshow']){
  const x=fixture.setup(),operation=await pending(x);assert.equal(x.ids['media-status'].textContent,ACK);
  if(reset==='edit')await x.ids['media-caption'].fire('input');
  else if(reset==='replace')await fixture.file(x);
  else if(reset==='clear')await x.ids['media-clear'].fire('click');
  else if(reset==='retry'){x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.ids['media-form'].fire('submit');}
  else for(const fn of x.windowEvents[reset])fn({persisted:true});
  assert.notEqual(x.ids['media-status'].textContent,ACK,reset);
  const status=x.ids['media-status'].textContent;operation.resolve({ok:true,json:async()=>fixture.report()});await operation.task;assert.equal(x.ids['media-status'].textContent,status,reset+' stale completion');
 }
});
