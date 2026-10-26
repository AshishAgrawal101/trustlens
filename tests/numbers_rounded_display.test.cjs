// Display acceptance frozen before the presentation-only change.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const prefix=fs.readFileSync(path.join(__dirname,'numbers_controller.test.cjs'),'utf8').split("test('numbers require")[0];
const fixture={require,__dirname,AbortController,AbortSignal,Blob};vm.runInNewContext(prefix+'\nthis.setup=fixture.setup;',fixture);
const cases=[
 {id:'near-total-reported',method:'percentages',values:['1','0.000000000001'],nonzero:'0.000000000001%'},
 {id:'smallest-reported',method:'percentages',values:['1','.'+'0'.repeat(62)+'1'],nonzero:'0.'+'0'.repeat(62)+'1%'},
 {id:'near-total-counts',method:'counts',values:['1','100','1','100000000000000'],nonzero:'0.000000000001%'},
 {id:'conventional-counts',method:'counts',values:['20','100','30','200'],rawCounts:['20 of 100','30 of 200']}
];
async function submit(x,row){x.ids['numbers-method'].value=row.method;await x.ids['numbers-method'].fire('change');const fields=row.method==='percentages'?['percentage-a','percentage-b']:['count-a','total-a','count-b','total-b'];fields.forEach((id,i)=>x.ids[id].value=row.values[i]);await x.ids['numbers-form'].fire('submit');}
for(const row of cases)test('qualified rounded calculated facts: '+row.id,async()=>{
 const x=fixture.setup();await submit(x,row);assert.equal(x.ids['numbers-result'].hidden,false);
 const children=x.ids['numbers-facts'].children,details=children.filter(n=>n.tagName==='dd');
 assert.equal(details.length,row.method==='percentages'?5:4);
 for(const value of details.slice(0,4))assert.match(value.textContent,/^About /);
 if(row.nonzero){assert.ok(details[1].textContent.includes(row.nonzero),'positive B remains displayed');assert.equal(details[3].textContent,'About -100%','rounded total decline is qualified');}
 if(row.rawCounts)row.rawCounts.forEach((value,i)=>assert.ok(details[i].textContent.endsWith('('+value+')')));
});
test('undefined baseline is unchanged and rounding note is adjacent to calculated facts',async()=>{
 const x=fixture.setup();await submit(x,{method:'percentages',values:['0','1']});
 const details=x.ids['numbers-facts'].children.filter(n=>n.tagName==='dd');assert.equal(details[3].textContent,'Undefined: Group A’s rate is zero. A percent increase from zero cannot be calculated.');
 const html=fs.readFileSync(path.join(__dirname,'../static/numbers-context.html'),'utf8');assert.match(html,/id="numbers-format-note"[^>]*>[\s\S]*?six significant digits[\s\S]*?not confidence[\s\S]*?<\/p>\s*<dl id="numbers-facts"/);
});
test('both pure calculation function bodies remain byte-identical',()=>{
 const source=fs.readFileSync(path.join(__dirname,'../static/numbers-context.js'),'utf8');
 for(const [start,end,expected]of [['  function compare(input){','  function comparePercentages(input){','2a9d755f7cc70e97ffa8e277918ed238ec2d773e6b21ab14699807590533ceb1'],['  function comparePercentages(input){','  return {compare,comparePercentages};','f4e6f05e0b14b4d9ab3ef0dcc739d236f5a8876b6fccbe55542c644c8e23538a']])assert.equal(crypto.createHash('sha256').update(source.slice(source.indexOf(start),source.indexOf(end))).digest('hex'),expected);
});
