const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const prefix=fs.readFileSync(path.join(__dirname,'media_context.test.cjs'),'utf8').split("test('metadata yields")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;this.file=file;this.report=report;',fixture);
test('native invalid without submit clears completed media output and keeps selection/caption',async()=>{
 const x=fixture.setup();await fixture.file(x);x.ids['media-caption'].value='PRIVATE caption';x.state.fetch=async()=>({ok:true,json:async()=>fixture.report()});await x.ids['media-form'].fire('submit');assert.equal(x.ids['media-result'].hidden,false);
 const requests=x.requests.length;await x.ids['media-form'].fire('invalid');
 assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-facts'].textContent,'');assert.equal(x.ids['media-questions'].textContent,'');assert.equal(x.ids['media-status'].textContent,'');assert.equal(x.ids['media-caption'].value,'PRIVATE caption');assert.equal(x.ids['media-file'].files[0].name,'PRIVATE_FILENAME.png');assert.equal(x.ids['media-preview'].src,'blob:fixture');assert.equal(x.revoked.length,0);assert.equal(x.requests.length,requests);
});
test('native invalid aborts pending client wait and stale completion cannot restore output',async()=>{
 for(const fail of [false,true]){
 const x=fixture.setup();await fixture.file(x);x.ids['media-caption'].value='PRIVATE caption';let resolve,reject;x.state.fetch=()=>new Promise((a,b)=>{resolve=a;reject=b;});const pending=x.ids['media-form'].fire('submit');
 await x.ids['media-form'].fire('invalid');assert.equal(x.requests[0].options.signal.aborted,true);assert.equal(x.ids['media-submit'].disabled,false);assert.equal(x.ids['media-cancel'].hidden,true);assert.equal(x.ids['media-form'].attributes['aria-busy'],'false');
 if(fail)reject(new Error('PRIVATE failure'));else resolve({ok:true,json:async()=>fixture.report()});await pending;
 assert.equal(x.ids['media-result'].hidden,true);assert.equal(x.ids['media-error'].hidden,true);assert.equal(x.ids['media-status'].textContent,'');assert.equal(x.ids['media-caption'].value,'PRIVATE caption');assert.equal(x.ids['media-file'].files[0].name,'PRIVATE_FILENAME.png');assert.equal(x.requests.length,1);
 }
});

