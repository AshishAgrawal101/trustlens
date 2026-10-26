const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../static/numbers-context.html'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'../static/numbers-context.css'),'utf8');
const tag=id=>html.match(new RegExp('<[a-z][a-z0-9]*\\b[^>]*\\bid="'+id+'"[^>]*>'))?.[0];
test('method choice is labelled unnamed disabled and defaults explicitly to counts inside the form',()=>{
  const form=html.match(/<form\b[^>]*id="numbers-form"[^>]*>([\s\S]*?)<\/form>/)?.[1];assert.ok(form);
  assert.match(form,/<label\b[^>]*for="numbers-method"/);assert.match(tag('numbers-method')||'',/^<select\b[^>]*\sdisabled(?:\s|>)/);assert.doesNotMatch(tag('numbers-method'),/\sname=/);
  assert.match(form,/<option\b[^>]*value="counts"[^>]*\sselected(?:\s|>)/);assert.match(form,/<option\b[^>]*value="percentages"/);
  assert.match(form,/Changing method keeps each method.s separate entries/);assert.match(form,/No values are converted/);assert.match(form,/Clear, loading an example or leaving this page removes both drafts/);assert.match(form,/autocomplete|<noscript>/);
});
test('inactive percentage controls are disabled in static markup and describe reported rates without denominators',()=>{
  assert.match(tag('numbers-counts')||'',/^<div\b/);
  const fieldset=html.match(/<fieldset\b[^>]*id="numbers-percentages"[^>]*>([\s\S]*?)<\/fieldset>/);assert.ok(fieldset);
  for(const attribute of ['hidden','disabled'])assert.match(fieldset[0].slice(0,fieldset[0].indexOf('>')+1),new RegExp('\\s'+attribute+'(?:\\s|>)'));
  for(const id of ['percentage-a','percentage-b']){
    const input=tag(id);assert.ok(input);for(const attribute of ['disabled','required'])assert.match(input,new RegExp('\\s'+attribute+'(?:\\s|>)'));
    for(const [key,value]of Object.entries({type:'text',inputmode:'decimal',maxlength:'64','aria-describedby':'percentage-help'}))assert.ok(input.includes(key+'="'+value+'"'));
    assert.doesNotMatch(input,/\sname=/);assert.match(fieldset[1],new RegExp('<label\\b[^>]*for="'+id+'"'));
  }
  assert.match(fieldset[1],/without a percent sign/);assert.match(fieldset[1],/totals.*not.*inferred/i);
});
test('count contracts result-first caveat and private fallback remain while select is mobile sized',()=>{
  for(const id of ['count-a','total-a','count-b','total-b']){assert.ok(tag(id));assert.doesNotMatch(tag(id),/\sdisabled(?:\s|>)/);assert.match(tag(id),/max="9007199254740991"/);}
  assert.match(html,/<p\b[^>]*id="numbers-result-caveat"[^>]*>Supplied counts only; no significance or causal conclusion\.<\/p>/);
  assert.ok(html.indexOf('id="numbers-result"')<html.indexOf('class="limits"'));assert.match(tag('numbers-result-title'),/tabindex="-1"/);assert.match(tag('numbers-submit'),/\sdisabled(?:\s|>)/);
  assert.doesNotMatch(html,/<(?:input|select|textarea)\b[^>]*\sname=/);assert.match(html,/<noscript>/);assert.match(html,/reported percentages/i);
  assert.match(css,/#numbers-method[^}]*font-size:16px/);assert.match(css,/#numbers-method[^}]*min-height:48px/);assert.match(css,/#numbers-method[^}]*width:100%/);assert.match(css,/#numbers-method:focus-visible/);assert.match(css,/@media print/);
});
