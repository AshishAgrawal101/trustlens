'use strict';
const UnicodeNotice=(()=>{
  const names=new Map([
    [0x00AD,'SOFT HYPHEN'],[0x061C,'ARABIC LETTER MARK'],[0x200B,'ZERO WIDTH SPACE'],
    [0x200C,'ZERO WIDTH NON-JOINER'],[0x200D,'ZERO WIDTH JOINER'],[0x200E,'LEFT-TO-RIGHT MARK'],[0x200F,'RIGHT-TO-LEFT MARK'],
    [0x202A,'LEFT-TO-RIGHT EMBEDDING'],[0x202B,'RIGHT-TO-LEFT EMBEDDING'],[0x202C,'POP DIRECTIONAL FORMATTING'],
    [0x202D,'LEFT-TO-RIGHT OVERRIDE'],[0x202E,'RIGHT-TO-LEFT OVERRIDE'],[0x2060,'WORD JOINER'],
    [0x2066,'LEFT-TO-RIGHT ISOLATE'],[0x2067,'RIGHT-TO-LEFT ISOLATE'],[0x2068,'FIRST STRONG ISOLATE'],[0x2069,'POP DIRECTIONAL ISOLATE'],
    [0xFEFF,'ZERO WIDTH NO-BREAK SPACE / BYTE ORDER MARK']
  ]);
  const directional=point=>point===0x061C||point===0x200E||point===0x200F||(point>=0x202A&&point<=0x202E)||(point>=0x2066&&point<=0x2069);
  function inspect(text){
    if(typeof text!=='string'||text.length>30000)throw new Error('Formatting inspection supports text up to 30,000 characters.');
    const found=new Map();let total=0,hasDirection=false;
    for(const char of text){const point=char.codePointAt(0);if(names.has(point)){found.set(point,(found.get(point)||0)+1);total++;hasDirection=hasDirection||directional(point);}}
    return {total,counts:[...names].filter(([point])=>found.has(point)).map(([point,name])=>({codePoint:'U+'+point.toString(16).toUpperCase().padStart(4,'0'),name,count:found.get(point)})),directional:hasDirection};
  }
  return {inspect};
})();
if(typeof module==='object'&&module.exports)module.exports=UnicodeNotice;

if(typeof document!=='undefined'){
  const get=id=>document.getElementById(id);
  if(get('quote-formatting')&&get('source-formatting')){
    function clear(id){get(id).replaceChildren();get(id).hidden=true;}
    function clearBoth(){clear('quote-formatting');clear('source-formatting');}
    function show(id,resultId,fields){
      clear(id);if(get(resultId).hidden)return;
      let reports;
      try{reports=fields.map(([label,inputId])=>({label,...UnicodeNotice.inspect(get(inputId).value)}));}catch{return;}
      if(!reports.some(report=>report.total))return;
      const note=document.createElement('p');note.textContent='Invisible formatting characters are present. They can affect display or exact matching and are also used in legitimate text, including language shaping and emoji. No characters were changed.';get(id).append(note);
      if(reports.some(report=>report.directional)){const direction=document.createElement('p');direction.textContent='Directional formatting can change display order.';get(id).append(direction);}
      const list=document.createElement('ul');
      for(const report of reports)for(const row of report.counts){const item=document.createElement('li');item.textContent=report.label+': '+row.codePoint+' '+row.name+' — '+row.count;list.append(item);}
      get(id).append(list);get(id).hidden=false;
    }
    get('quote-form').addEventListener('invalid',()=>clear('quote-formatting'),true);
    get('source-form').addEventListener('invalid',()=>clear('source-formatting'),true);
    get('quote-form').addEventListener('submit',()=>show('quote-formatting','quote-result',[['Original version','quote-original'],['Revised version','quote-revised']]));
    get('source-form').addEventListener('submit',()=>show('source-formatting','source-result',[['Original version','quote-original'],['Source passage','source-passage']]));
    get('quote-original').addEventListener('input',clearBoth);
    get('quote-revised').addEventListener('input',()=>clear('quote-formatting'));
    get('source-passage').addEventListener('input',()=>clear('source-formatting'));
    get('quote-clear').addEventListener('click',clearBoth);
    get('quote-example').addEventListener('click',clearBoth);
    get('source-clear').addEventListener('click',()=>clear('source-formatting'));
    window.addEventListener('pagehide',clearBoth);window.addEventListener('pageshow',event=>{if(event.persisted)clearBoth();});clearBoth();
  }
}
