'use strict';
const NumbersContext=(()=>{
  function compare(input){
    if(!input||!['countA','totalA','countB','totalB'].every(key=>Number.isSafeInteger(input[key])&&input[key]>=0)
      ||input.totalA<1||input.totalB<1||input.countA>input.totalA||input.countB>input.totalB)
      throw new Error('Use whole-number counts from 0 to their group total, with totals from 1 to 9,007,199,254,740,991.');
    const a=BigInt(input.countA),ta=BigInt(input.totalA),b=BigInt(input.countB),tb=BigInt(input.totalB),difference=b*ta-a*tb;
    // Cross-products retain small rate differences near the safe-integer boundary.
    return {rateA:input.countA/input.totalA*100,rateB:input.countB/input.totalB*100,
      percentagePoints:Number(difference)/Number(ta*tb)*100,
      relativePercent:a===0n?null:Number(difference)/Number(a*tb)*100};
  }
  function comparePercentages(input){
    const message='Enter percentages from 0 to 100 using decimal digits and a point only, with at most 64 characters including surrounding spaces.';
    function decimal(value){
      if(typeof value!=='string'||value.length>64)throw new Error(message);
      const text=value.replace(/^ +| +$/g,'');
      if(!/^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(text))throw new Error(message);
      const [whole,fraction='']=text.split('.'),coefficient=BigInt((whole||'0')+fraction),denominator=10n**BigInt(fraction.length);
      if(coefficient>100n*denominator)throw new Error(message);
      return {coefficient,denominator};
    }
    if(!input||typeof input!=='object')throw new Error(message);
    const a=decimal(input.percentageA),b=decimal(input.percentageB),difference=b.coefficient*a.denominator-a.coefficient*b.denominator;
    return {rateA:Number(a.coefficient)/Number(a.denominator),rateB:Number(b.coefficient)/Number(b.denominator),
      percentagePoints:Number(difference)/Number(a.denominator*b.denominator),
      relativePercent:a.coefficient===0n?null:Number(difference)/Number(a.coefficient*b.denominator)*100};
  }
  return {compare,comparePercentages};
})();
if(typeof module==='object'&&module.exports)module.exports=NumbersContext;

if(typeof document!=='undefined'){
  const get=id=>document.getElementById(id),fields={countA:'count-a',totalA:'total-a',countB:'count-b',totalB:'total-b'},percentageFields={percentageA:'percentage-a',percentageB:'percentage-b'},allFields=[...Object.values(fields),...Object.values(percentageFields)];
  const format=value=>'About '+value.toLocaleString('en-US',{maximumSignificantDigits:6});
  const percentages=()=>get('numbers-method').value==='percentages';
  const firstField=()=>percentages()?'percentage-a':'count-a';
  const activeFields=()=>Object.values(percentages()?percentageFields:fields).map(get);
  function syncSwap(){get('numbers-swap').disabled=activeFields().every(input=>input.value==='');}
  const copy={counts:{title:'Two counts, two totals',help:'Use whole-number counts and totals from the same definition within each group. Count is the part being measured; total is the full group it comes from. Group A and Group B do not imply before and after.',empty:'Enter the count and total for both groups, then select Compare proportions. A larger count can represent a smaller share when the totals differ.',result:'Your descriptive comparison',caveat:'Supplied counts only; no significance or causal conclusion.'},percentages:{title:'Two reported percentages',help:'Compare two reported percentages without inventing sample sizes. Underlying counts and totals were not supplied and will not be inferred. Group A and Group B do not imply before and after.',empty:'Enter both reported percentages, then select Compare proportions. Underlying counts and totals remain unknown.',result:'Your reported-percentage comparison',caveat:'Supplied percentages only; counts and totals were not supplied. No significance or causal conclusion.'}};
  function syncMethod(){
    const active=percentages(),text=copy[active?'percentages':'counts'];
    get('numbers-counts').hidden=active;Object.values(fields).forEach(id=>get(id).disabled=active);
    get('numbers-percentages').hidden=!active;get('numbers-percentages').disabled=!active;Object.values(percentageFields).forEach(id=>get(id).disabled=!active);
    get('input-title').textContent=text.title;get('numbers-help').textContent=text.help;get('numbers-empty').textContent=text.empty;get('numbers-result-title').textContent=text.result;get('numbers-result-caveat').textContent=text.caveat;
    syncSwap();
  }
  function invalidate(){get('numbers-empty').hidden=false;get('numbers-result').hidden=true;get('numbers-error').hidden=true;['numbers-facts','numbers-questions','numbers-error','numbers-input-status'].forEach(id=>get(id).replaceChildren());syncSwap();}
  function clearCountValidity(){get('count-a').setCustomValidity('');get('count-b').setCustomValidity('');}
  function clear(){clearCountValidity();invalidate();allFields.forEach(id=>get(id).value='');syncMethod();}
  function reset(){get('numbers-method').value='counts';clear();}
  function fact(label,value){const term=document.createElement('dt'),detail=document.createElement('dd');term.textContent=label;detail.textContent=value;get('numbers-facts').append(term,detail);}
  allFields.forEach(id=>get(id).addEventListener('input',()=>{clearCountValidity();invalidate();}));
  get('numbers-method').addEventListener('change',()=>{clearCountValidity();invalidate();syncMethod();});
  get('numbers-form').addEventListener('invalid',invalidate,true);
  get('numbers-form').addEventListener('submit',event=>{
    event.preventDefault();clearCountValidity();invalidate();syncMethod();if(!get('numbers-form').reportValidity())return;
    try{
      const percent=percentages();let input,result;
      if(percent){input=Object.fromEntries(Object.entries(percentageFields).map(([key,id])=>[key,get(id).value]));result=NumbersContext.comparePercentages(input);}
      else{
        input=Object.fromEntries(Object.entries(fields).map(([key,id])=>{
          const raw=get(id).value.trim();if(!/^\d+$/.test(raw))throw new Error('Enter counts and totals using whole-number digits only.');return [key,Number(raw)];
        }));
        let invalidCounts=false;
        for(const [count,total,group]of [['countA','totalA','A'],['countB','totalB','B']])if(input[count]>input[total]){get(fields[count]).setCustomValidity('Group '+group+' count cannot be larger than Group '+group+' total.');invalidCounts=true;}
        if(invalidCounts){get('numbers-form').reportValidity();return;}
        result=NumbersContext.compare(input);
      }
      fact('Group A rate',format(result.rateA)+'%'+(percent?'':' ('+input.countA.toLocaleString('en-US')+' of '+input.totalA.toLocaleString('en-US')+')'));
      fact('Group B rate',format(result.rateB)+'%'+(percent?'':' ('+input.countB.toLocaleString('en-US')+' of '+input.totalB.toLocaleString('en-US')+')'));
      fact('Rate difference · B minus A',format(result.percentagePoints)+' percentage points');
      fact('Relative rate change · compared with A',result.relativePercent===null?'Undefined: Group A’s rate is zero. A percent increase from zero cannot be calculated.':format(result.relativePercent)+'%');
      if(percent)fact('Underlying counts and totals','Not supplied; not inferred from reported percentages.');
      const questions=[
        percent?'Are both reported percentages measuring the same outcome, using the same definitions and collection method?':'Are both counts measuring the same outcome, using the same definitions and collection method?',
        'Who is included in each group, and over what period? Different denominators or selection can change the story.',
        'Find the original data and check missing values, uncertainty, sample size and whether the comparison was selected after seeing the results.',
        percent?'These calculations describe supplied percentages only. They do not establish statistical significance, causation, data quality or whether a claim is true.':'These calculations describe supplied counts only. They do not establish statistical significance, causation, data quality or whether a claim is true.',
        'Rates and changes are rounded to six significant digits. Group A is only the comparison baseline; no time order or causal relationship is assumed.'
      ];
      if(percent)questions.unshift('Reported percentages may already be rounded. Obtain the underlying counts and totals; exact arithmetic cannot recover reporting precision or sample sizes.');
      else if(input.totalA!==input.totalB)questions.unshift('The group totals differ. Compare rates as well as raw counts; a larger count can have a lower rate.');
      if(result.relativePercent===null)questions.unshift(percent?'With a zero baseline, use reported rates and the percentage-point difference instead of a relative percent increase; obtain the underlying counts and totals.':'With a zero baseline, use the actual counts, rates and percentage-point difference instead of a relative percent increase.');
      for(const text of questions){const item=document.createElement('li');item.textContent=text;get('numbers-questions').append(item);}
      get('numbers-empty').hidden=true;get('numbers-result').hidden=false;get('numbers-result-title').focus();get('numbers-result-title').scrollIntoView({block:'start'});
    }catch(error){get('numbers-error').textContent=error.message;get('numbers-error').hidden=false;get('numbers-error').focus();}
  });
  get('numbers-clear').addEventListener('click',()=>{clear();get(firstField()).focus();});
  get('numbers-swap').addEventListener('click',()=>{
    if(get('numbers-swap').disabled)return;
    clearCountValidity();invalidate();
    if(activeFields().some(input=>input.validity.badInput)){get('numbers-input-status').textContent='Finish the number entries before swapping. Your inputs were kept.';return;}
    const pairs=percentages()?[['percentage-a','percentage-b']]:[['count-a','count-b'],['total-a','total-b']];
    for(const [a,b]of pairs)[get(a).value,get(b).value]=[get(b).value,get(a).value];
    syncSwap();get('numbers-input-status').textContent='Group A and B inputs swapped. Group A is now the other comparison baseline. Select Compare proportions to calculate again.';
  });
  get('numbers-example').addEventListener('click',()=>{
    clear();const example=percentages()?{percentageA:'1.2',percentageB:'1.8'}:{countA:1,totalA:1000,countB:2,totalB:1000},active=percentages()?percentageFields:fields;
    for(const[key,value]of Object.entries(example))get(active[key]).value=String(value);syncSwap();get(firstField()).focus();
  });
  window.addEventListener('pagehide',reset);window.addEventListener('pageshow',event=>{if(event.persisted)reset();});
  reset();get('numbers-method').disabled=false;get('numbers-submit').disabled=false;
}
