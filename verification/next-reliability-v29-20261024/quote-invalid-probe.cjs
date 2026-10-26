const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=process.cwd(),testDir=path.join(root,'tests');
let harness=fs.readFileSync(path.join(testDir,'frontend_state.test.cjs'),'utf8').split("test('screenshot requires")[0].replace('static/index.template.html','static/quote-context.html').replace('static/app.js','static/quote-context.js');
harness=harness.replace('vm.runInContext(source,context);',"vm.runInContext(source,context);vm.runInContext(fs.readFileSync(path.join(root,'static/source-context.js'),'utf8'),context);vm.runInContext(fs.readFileSync(path.join(root,'static/unicode-notice.js'),'utf8'),context);");
const fixture={require,__dirname:testDir,AbortController,AbortSignal,Blob};vm.runInNewContext(harness+'\nthis.setup=setup;',fixture);
(async()=>{const x=fixture.setup();x.ids['quote-original'].value='PRIVATE\u200b wording';x.ids['quote-revised'].value='PRIVATE wording';await x.ids['quote-form'].fire('submit');assert.equal(x.ids['quote-result'].hidden,false);assert.equal(x.ids['quote-formatting'].hidden,false);
// Native validation delivers invalid and suppresses submit. No synthetic submit follows.
x.ids['quote-original'].value='';await x.ids['quote-form'].fire('invalid');
const result={comparisonStillVisible:!x.ids['quote-result'].hidden,oldPrivateDiffRetained:x.ids['quote-diff'].textContent.includes('PRIVATE'),formattingNoticeHidden:x.ids['quote-formatting'].hidden,requests:x.requests.length};console.log(JSON.stringify(result));assert.equal(result.comparisonStillVisible,true);assert.equal(result.formattingNoticeHidden,true);})();
