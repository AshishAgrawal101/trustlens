'use strict';
const QuoteContext=(()=>{
  function compare(original,revised){
    if([original,revised].some(text=>typeof text!=='string'||!text.trim()||text.length>4000))throw new Error('Enter two nonblank versions, each up to 4,000 characters.');
    const a=original.match(/\s+|[^\s]+/gu),b=revised.match(/\s+|[^\s]+/gu);
    if(a.length>800||b.length>800)throw new Error('Use shorter excerpts: each version supports up to 800 whitespace or nonwhitespace segments.');
    const width=b.length+1,table=new Uint16Array((a.length+1)*width);
    for(let i=a.length-1;i>=0;i--)for(let j=b.length-1;j>=0;j--)table[i*width+j]=a[i]===b[j]?1+table[(i+1)*width+j+1]:Math.max(table[(i+1)*width+j],table[i*width+j+1]);
    const parts=[];let i=0,j=0;
    function add(type,text){if(parts.at(-1)?.type===type)parts.at(-1).text+=text;else parts.push({type,text});}
    while(i<a.length||j<b.length){
      if(i<a.length&&j<b.length&&a[i]===b[j]){add('same',a[i++]);j++;}
      else if(i<a.length&&(j===b.length||table[(i+1)*width+j]>=table[i*width+j+1]))add('removed',a[i++]);
      else add('added',b[j++]);
    }
    return {parts,identical:original===revised};
  }
  return {compare};
})();
if(typeof module==='object'&&module.exports)module.exports=QuoteContext;

if(typeof document!=='undefined'){
  const get=id=>document.getElementById(id),fields=['quote-original','quote-revised'];
  function invalidate(){get('quote-result').hidden=true;get('quote-error').hidden=true;get('quote-empty').hidden=false;['quote-diff','quote-status','quote-error'].forEach(id=>get(id).replaceChildren());}
  function clear(){invalidate();fields.forEach(id=>get(id).value='');}
  fields.forEach(id=>get(id).addEventListener('input',invalidate));
  get('quote-form').addEventListener('invalid',invalidate,true);
  get('quote-form').addEventListener('submit',event=>{
    event.preventDefault();invalidate();if(!get('quote-form').reportValidity())return;
    try{
      const result=QuoteContext.compare(...fields.map(id=>get(id).value));
      for(const part of result.parts){const span=document.createElement('span');span.className=part.type;
        if(part.type!=='same'){const label=document.createElement('span');label.className='change-label';label.textContent=part.type==='removed'?'[Removed] ':'[Added] ';span.append(label);}
        span.append(document.createTextNode(part.text));get('quote-diff').append(span);
      }
      get('quote-status').textContent=result.identical?'The supplied versions are exactly identical, including whitespace. This does not verify their source or accuracy.':'Literal wording or whitespace differs. Removed text belongs to the first version; added text belongs to the second. Alignment is one possible comparison, not a judgment about meaning.';
      get('quote-empty').hidden=true;get('quote-result').hidden=false;get('quote-result-title').focus();get('quote-result-title').scrollIntoView({block:'start'});
    }catch(error){get('quote-error').textContent=error.message;get('quote-error').hidden=false;get('quote-error').focus();}
  });
  get('quote-clear').addEventListener('click',()=>{clear();get('quote-original').focus();});
  get('quote-example').addEventListener('click',()=>{clear();get('quote-original').value='The park will close for repairs on Monday. Most paths remain open.';get('quote-revised').value='The park will close on Monday.';get('quote-original').focus();});
  window.addEventListener('pagehide',clear);window.addEventListener('pageshow',event=>{if(event.persisted)clear();});clear();get('quote-submit').disabled=false;
}
