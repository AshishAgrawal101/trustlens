/* Presentation-only effects: pointer glow and tilt. Reads no user input, no network, no storage. */
(function(){
  if(typeof document==='undefined'||(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))return;
  var glow='.primary,.secondary,.modes button,.hero-facts span,.evidence-item,.next-step,.what-checked';
  document.addEventListener('pointermove',function(e){
    var t=e.target.closest&&e.target.closest(glow);
    if(t){var r=t.getBoundingClientRect();t.style.setProperty('--mx',(e.clientX-r.left)+'px');t.style.setProperty('--my',(e.clientY-r.top)+'px');}
    var s=e.target.closest&&e.target.closest('.lens-stage');
    if(s){var b=s.getBoundingClientRect(),x=(e.clientX-b.left)/b.width-.5,y=(e.clientY-b.top)/b.height-.5;
      s.style.transform='perspective(900px) rotateY('+(x*10)+'deg) rotateX('+(-y*10)+'deg)';}
  },{passive:true});
  document.addEventListener('pointerout',function(e){var s=e.target.closest&&e.target.closest('.lens-stage');if(s&&!s.contains(e.relatedTarget))s.style.transform='';},{passive:true});
  var seen=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');seen.unobserve(x.target);}});},{threshold:.12});
  document.querySelectorAll('.principles>div,.support-row>*,.demo-bar,footer').forEach(function(n){n.classList.add('reveal');seen.observe(n);});
})();
