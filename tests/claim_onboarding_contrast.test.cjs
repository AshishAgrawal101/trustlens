const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const css=fs.readFileSync(path.join(__dirname,'../static/styles.css'),'utf8');
function rule(selector){const escaped=selector.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');const matches=[...css.matchAll(new RegExp(escaped+'\\{([^}]+)\\}','g'))];assert.ok(matches.length,'Missing scoped rule '+selector);return Object.fromEntries(matches.at(-1)[1].split(';').filter(Boolean).map(row=>row.split(':').map(x=>x.trim())));}
function luminance(hex){assert.match(hex,/^#[0-9a-f]{6}$/i);const rgb=hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;}
function contrast(a,b){const [lo,hi]=[luminance(a),luminance(b)].sort((a,b)=>a-b);return (hi+.05)/(lo+.05);}
test('hero scope notice remains readable on the dark page',()=>{
  for(const background of ['#09191f','#0d282c'])assert.ok(contrast(rule('.intro .hint').color,background)>=4.5);
});
// Actual matching normal-state selectors for the direct paragraph in details.demo-bar > div.demo-content.
function paragraphColor(){
  const matching=new Set(['p','.demo-bar>div>p','.demo-content>p','.demo-bar>.demo-content>p']),candidates=[];
  for(const [order,match]of [...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)].entries())for(const selector of match[1].trim().split(',')){
    const normalized=selector.trim().replace(/\s*>\s*/g,'>');if(!matching.has(normalized))continue;
    const color=match[2].match(/(?:^|;)\s*color:([^;]+)/)?.[1];if(!color)continue;
    const classes=(selector.match(/\.[\w-]+/g)||[]).length,tags=(selector.replace(/\.[\w-]+/g,'').match(/[a-z]+/g)||[]).length;candidates.push({color,specificity:classes*100+tags,order});
  }
  candidates.sort((a,b)=>b.specificity-a.specificity||b.order-a.order);return candidates[0].color;
}
test('demo link and direct explanatory paragraphs explicitly use light text on both dark background endpoints',()=>{
  const link=rule('.demo-content #claim-example-link'),text={color:paragraphColor()};assert.equal(link['min-height'],'44px');
  for(const style of [link,text])for(const background of ['#09191f','#0d282c'])assert.ok(contrast(style.color,background)>=4.5);
});
test('dark hero secondary links have opaque contrast-safe normal and hover surfaces',()=>{
  const base=rule('.quick-start a.secondary'),hover=rule('.quick-start a.secondary:hover');
  assert.equal(base.display,'inline-flex');assert.equal(base['align-items'],'center');assert.ok(parseFloat(base['min-height'])>=44);
  assert.ok(contrast(base.color,base.background)>=4.5);assert.ok(contrast(base.color,hover.background)>=4.5);
  for(const background of ['#09191f','#0d282c'])assert.ok(contrast(base['border-color'],background)>=3);
});
test('existing light focus color stays visible against normal and hovered hero buttons',()=>{
  const focus='#b5ee96';assert.match(css,/\.quick-start :focus-visible[^}]*outline-color:#b5ee96/);
  for(const selector of ['.quick-start a.secondary','.quick-start a.secondary:hover'])assert.ok(contrast(focus,rule(selector).background)>=3);
});
