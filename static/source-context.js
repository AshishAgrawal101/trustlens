'use strict';
const SourceContext=(()=>{
  function find(quote,source,pageIndex=0){
    if(typeof quote!=='string'||!quote.trim()||quote.length>4000)throw new Error('Enter wording in Original version above, up to 4,000 characters.');
    if(typeof source!=='string'||!source.trim()||source.length>30000)throw new Error('Paste a nonblank source passage of up to 30,000 characters.');
    const pageError='Choose an available group of matches, then find again.';
    if(!Number.isInteger(pageIndex)||pageIndex<0||pageIndex>5999)throw new Error(pageError);
    const matches=[];let total=0,from=0,start;
    while((start=source.indexOf(quote,from))!==-1){
      total++;const end=start+quote.length;
      if(total>pageIndex*5&&matches.length<5){
        let left=Math.max(0,start-160),right=Math.min(source.length,end+160);
        // Keep a context window from cutting a valid UTF-16 surrogate pair.
        if(left>0&&/[\uDC00-\uDFFF]/.test(source[left])&&/[\uD800-\uDBFF]/.test(source[left-1]))left--;
        if(right<source.length&&/[\uD800-\uDBFF]/.test(source[right-1])&&/[\uDC00-\uDFFF]/.test(source[right]))right++;
        matches.push({start,end,before:source.slice(left,start),text:source.slice(start,end),after:source.slice(end,right)});
      }
      from=end;
    }
    if(pageIndex>0&&pageIndex*5>=total)throw new Error(pageError);
    return {total,matches,truncated:total>matches.length};
  }
  return {find};
})();
if(typeof module==='object'&&module.exports)module.exports=SourceContext;
if(typeof document!=='undefined'){
  const get=id=>document.getElementById(id),firstButton=get('source-first'),lastButton=get('source-last');
  let pageIndex=0,lastPage=0;
  function invalidate(){pageIndex=0;lastPage=0;get('source-paging').hidden=true;if(firstButton)firstButton.disabled=true;get('source-prev').disabled=true;get('source-next').disabled=true;if(lastButton)lastButton.disabled=true;get('source-formatting').hidden=true;get('source-formatting').replaceChildren();get('source-window-note').hidden=true;get('source-result').hidden=true;get('source-error').hidden=true;['source-page-status','source-status','source-matches','source-error'].forEach(id=>get(id).replaceChildren());}
  function clear(){invalidate();get('source-passage').value='';}
  ['quote-original','source-passage'].forEach(id=>get(id).addEventListener('input',invalidate));
  get('quote-clear').addEventListener('click',clear);
  get('quote-example').addEventListener('click',clear);
  get('source-clear').addEventListener('click',()=>{clear();get('source-passage').focus();});
  function renderPage(nextPage,trigger){
    try{
      const source=get('source-passage').value,result=SourceContext.find(get('quote-original').value,source,nextPage);
      get('source-matches').replaceChildren();pageIndex=nextPage;lastPage=Math.max(0,Math.ceil(result.total/5)-1);
      get('source-status').textContent=result.total===0?'No exact match was found in this supplied passage. Case, spacing, punctuation, excerpts or revisions can differ; this does not prove a quotation is fabricated.'
        :result.total+' non-overlapping exact '+(result.total===1?'match':'matches')+' found in the supplied passage. A wording match does not authenticate the source or establish meaning or truth.';
      get('source-page-status').textContent=result.total?'Matches '+(pageIndex*5+1)+'–'+(pageIndex*5+result.matches.length)+' of '+result.total:'';
      get('source-paging').hidden=result.total<=5;if(firstButton)firstButton.disabled=pageIndex===0;get('source-prev').disabled=pageIndex===0;get('source-next').disabled=pageIndex===lastPage;if(lastButton)lastButton.disabled=pageIndex===lastPage;
      for(const [index,row]of result.matches.entries()){
        const item=document.createElement('article'),title=document.createElement('h4'),context=document.createElement('p'),mark=document.createElement('mark');
        title.textContent='Match '+(pageIndex*5+index+1)+' of '+result.total;context.className='source-window';mark.textContent=row.text;
        context.append(document.createTextNode((row.start>row.before.length?'…':'')+row.before),mark,document.createTextNode(row.after+(row.end+row.after.length<source.length?'…':'')));item.append(title,context);get('source-matches').append(item);
      }
      get('source-window-note').hidden=result.matches.length===0;get('source-result').hidden=false;
      if(trigger){if(trigger.disabled)get('source-page-status').focus();get('source-page-status').scrollIntoView({block:'start'});}else get('source-result').focus();
    }catch(error){invalidate();get('source-error').textContent=error.message;get('source-error').hidden=false;get('source-error').focus();}
  }
  get('source-form').addEventListener('invalid',invalidate,true);
  get('quote-form').addEventListener('invalid',event=>{if(event.target===get('quote-original'))invalidate();},true);
  get('source-form').addEventListener('submit',event=>{
    event.preventDefault();invalidate();if(!get('source-form').reportValidity())return;renderPage(0);
  });
  for(const [id,direction]of [['source-prev',-1],['source-next',1]])get(id).addEventListener('click',()=>{if(get('source-result').hidden||get(id).disabled)return;renderPage(pageIndex+direction,get(id));});
  firstButton?.addEventListener('click',()=>{if(get('source-result').hidden||firstButton.disabled)return;renderPage(0,firstButton);});
  lastButton?.addEventListener('click',()=>{if(get('source-result').hidden||lastButton.disabled)return;renderPage(lastPage,lastButton);});
  window.addEventListener('pagehide',clear);window.addEventListener('pageshow',event=>{if(event.persisted)clear();});clear();get('source-submit').disabled=false;
}
