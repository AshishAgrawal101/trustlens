// Independent frozen Python Fraction oracle; no application math copied here.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const directory=path.join(__dirname,'../verification/reported-percentages-20261024');
const bytes=fs.readFileSync(path.join(directory,'acceptance.json'));
const digest=fs.readFileSync(path.join(directory,'acceptance.sha256'),'utf8').trim().split(/\s+/)[0];
const frozen=JSON.parse(bytes),numbers=require('../static/numbers-context.js');
function compare(input){assert.equal(typeof numbers.comparePercentages,'function','reported-percentage API must exist');return numbers.comparePercentages(input);}
function exactExpected(rational){return Number(rational.numerator)/Number(rational.denominator);}
function close(actual,expected,name){
 assert.equal(typeof actual,'number',name);assert.ok(Number.isFinite(actual),name+' finite');
 if(expected===0){assert.equal(actual,0,name+' zero');assert.ok(!Object.is(actual,-0),name+' no negative zero');return;}
 assert.equal(Math.sign(actual),Math.sign(expected),name+' sign');
 // No absolute epsilon floor: a 1e-62 change must not be hidden by 1e-12.
 assert.ok(Math.abs((actual-expected)/expected)<=1e-12,name+' relative error');
}
test('unchanged 16-branch Fraction oracle and digest are intact',()=>{
 assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),digest);
 assert.equal(digest,'c2b357b4a089d9180530467d7883a6443965578429b05cecd80f3a2e409fbfdc');
 assert.equal(frozen.cases.length,16);
});
for(const row of frozen.cases){
 test('reported-percentages frozen acceptance: '+row.id,()=>{
  if(row.expected&&typeof row.expected==='object'){
   const result=compare(row.input);
   for(const key of ['rateA','rateB','percentagePoints','relativePercent']){
    if(row.expected[key]===null)assert.equal(result[key],null,key+' undefined baseline');
    else close(result[key],exactExpected(row.expected[key]),row.id+' '+key);
   }
   if(row.paired_swap_property){const swapped=compare({percentageA:row.input.percentageB,percentageB:row.input.percentageA});close(swapped.percentagePoints,-exactExpected(row.expected.percentagePoints),'near-equal swapped points');}
  }else{
   assert.equal(typeof numbers.comparePercentages,'function');
   for(const value of row.values)for(const key of ['percentageA','percentageB']){
    const input={percentageA:'1',percentageB:'1',[key]:value};
    assert.throws(()=>compare(input),error=>error instanceof Error&&typeof error.message==='string'&&error.message.length>0,row.id+' '+key);
   }
  }
 });
}
