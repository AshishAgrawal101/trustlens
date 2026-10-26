'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),vm=require('node:vm');
const folder=__dirname,sourcePath=path.resolve(folder,'../../static/claim-review.js');
const hash=text=>crypto.createHash('sha256').update(text).digest('hex');
const CONTRACT_SHA='36f3edc43e31e6e476ee6e13d5e4d420ceb1e546c42879da09fea5b166b18e65';
function evaluate(){
 const contractBytes=fs.readFileSync(path.join(folder,'acceptance.json'));
 if(hash(contractBytes)!==CONTRACT_SHA)throw new Error('Frozen contract changed');
 const contract=JSON.parse(contractBytes),source=fs.readFileSync(sourcePath,'utf8');let networkCalls=0;
 const denied=()=>{networkCalls++;throw new Error('Network forbidden in worksheet diagnostic');};
 const sandbox={module:{exports:{}},URL,fetch:denied,XMLHttpRequest:denied};vm.runInNewContext(source,sandbox,{filename:sourcePath});
 const api=sandbox.module.exports;
 const rows=contract.cases.map(c=>{
  const input={claim:c.input.claim,context:c.input.context};
  c.input.sources.forEach((s,i)=>{const k=i?'b':'a';input[k+'Url']=s.url;input[k+'Quote']=s.quote;input[k+'Date']=s.date;});
  const snapshot=JSON.stringify(input);let result=null,error=null;try{result=JSON.parse(JSON.stringify(api.analyze(input,contract.now)));}catch(e){error=e.message;}
  const ids=result?[...result.observations,...result.questions].map(x=>x.id):[];
  const failures=[];
  if(c.expected_outcome==='worksheet'){
   if(error)failures.push('unexpected_validation_error');
   for(const id of c.required_ids||[])if(!ids.includes(id))failures.push('missing_id:'+id);
  }else if(!error)failures.push('expected_validation_error');
  if(JSON.stringify(input)!==snapshot)failures.push('input_mutated');
  const output=JSON.stringify(result)+String(error)+api.PLAN;
  for(const marker of ['PRIVATE_CLAIM','PRIVATE_CONTEXT','PRIVATE_PASSWORD','PRIVATE_TOKEN','PRIVATE_QUOTE','<script>','<img '])if(output.includes(marker))failures.push('private_or_markup_echo:'+marker);
  if(result&&JSON.stringify(Object.keys(result).sort())!==JSON.stringify(['observations','questions','steps']))failures.push('unexpected_result_schema');
  return {id:c.id,expected_outcome:c.expected_outcome,required_ids:c.required_ids||[],actual_ids:ids,result,error,failures};
 });
 return {label:'Frozen authored structural acceptance, not truth-detection accuracy',contract_sha256:CONTRACT_SHA,source_sha256:hash(fs.readFileSync(sourcePath)),network_calls:networkCalls,rows,failures:rows.filter(r=>r.failures.length).length,plan:sandbox.module.exports.PLAN};
}
module.exports={evaluate,CONTRACT_SHA};
if(require.main===module){const dest=path.join(folder,'results.json');if(fs.existsSync(dest))throw new Error('Refusing to overwrite retained results');const result=evaluate();fs.writeFileSync(dest,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({cases:result.rows.length,failures:result.failures,network_calls:result.network_calls}));}
