'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const folder=__dirname,HASH='b09644736bd8bda0c8c7ed14469fd0b027a4174df7a430024f37e842b735e4bd';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function evaluate(){
 const bytes=fs.readFileSync(path.join(folder,'acceptance.json'));if(sha(bytes)!==HASH)throw Error('Frozen role contract changed');
 const contract=JSON.parse(bytes),source=fs.readFileSync(path.join(folder,'../../static/claim-review.js'));let networkCalls=0;
 const denied=()=>{networkCalls++;throw Error('Network prohibited');},scope={module:{exports:{}},URL,fetch:denied,XMLHttpRequest:denied};vm.runInNewContext(source.toString(),scope);const api=scope.module.exports;
 const rows=contract.cases.map(c=>{const original=JSON.stringify(c.input);let result=null,error=null;try{result=JSON.parse(JSON.stringify(api.review(c.input,contract.now)));}catch(e){error=e.message;}
  const failures=[],ids=result?result.questions.map(r=>r.id):[],labels=result?result.labels.map(r=>r.id):[];
  // Missing-account explanatory rows are not human role assignments. Assert exact active-role labels.
  const roles=labels.filter(id=>/^labels:[ab]:(unsure|supports|challenges|context)$/.test(id));
  if(c.expected_outcome==='worksheet'){
   if(error)failures.push('unexpected_error');if(JSON.stringify(roles.slice().sort())!==JSON.stringify(c.expected_label_ids.slice().sort()))failures.push('active_role_labels_mismatch');
   for(const id of c.required_question_ids)if(!ids.includes(id))failures.push('missing_question:'+id);
   for(const id of c.forbidden_question_ids)if(ids.includes(id))failures.push('forbidden_question:'+id);
  }else if(!error)failures.push('expected_validation_error');
  if(original!==JSON.stringify(c.input))failures.push('input_mutated');
  return {id:c.id,expected_outcome:c.expected_outcome,expected_label_ids:c.expected_label_ids,actual_label_ids:labels,active_role_ids:roles,result,error,failures};
 });return {label:'Frozen user-selected role structural acceptance; not factual correctness',contract_sha256:HASH,source_sha256:sha(source),network_calls:networkCalls,rows,failures:rows.filter(r=>r.failures.length).length,plan:api.PLAN};
}
module.exports={evaluate,HASH};if(require.main===module){const dest=path.join(folder,'results.json');if(fs.existsSync(dest))throw Error('Refusing to overwrite retained results');const r=evaluate();fs.writeFileSync(dest,JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify({cases:r.rows.length,failures:r.failures,network_calls:r.network_calls}));}
