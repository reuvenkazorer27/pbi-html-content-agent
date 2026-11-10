# -*- coding: utf-8 -*-
"""fitCheck() injected into preview pages: every card iframe must keep SAFE px of slack (gates FIT OK)."""
SAFE = 8  # px of slack every card keeps at the bottom/sides
FIT_JS = """
function fitCheck(){
  var SAFE=%d, out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){
    var d=f.contentDocument, root=d && d.body && d.body.firstElementChild; if(!root) {out.push(f.dataset.name+': EMPTY');return;}
    var W=f.clientWidth, H=f.clientHeight, worst=null;
    /* motion: measure the resting layout - finish entrances, park endless loops at their start */
    if(d.getAnimations) d.getAnimations().forEach(function(a){ try{
      if(a.effect && a.effect.getComputedTiming().iterations===Infinity){ a.pause(); a.currentTime=0; } else { a.finish(); }
    }catch(e){} });
    root.querySelectorAll('*').forEach(function(el){
      /* .fit-clip = clipped on purpose (odometer digit strips, sweeping sheens) */
      if(el.closest && el.closest('.fit-clip')) return;
      var r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
      var over=Math.max(r.bottom-(H-SAFE), r.right-(W-SAFE), SAFE-r.left);
      if(over>0.5 && (!worst||over>worst.over)) worst={over:over,tag:el.tagName,txt:(el.textContent||'').trim().slice(0,40)};
      if(el.scrollWidth>el.clientWidth+1 && getComputedStyle(el).whiteSpace!=='nowrap' && getComputedStyle(el).overflow==='visible'){}
    });
    if(root.scrollHeight>H+0.5) out.push(f.dataset.name+': content '+(root.scrollHeight-H)+'px taller than the visual');
    if(worst) out.push(f.dataset.name+': '+Math.round(worst.over)+'px past the safe edge at <'+worst.tag+'> "'+worst.txt+'"');
  });
  var p=document.getElementById('fit'); p.textContent = out.length ? 'FIT FAIL\\n'+out.join('\\n') : 'FIT OK';
}
window.addEventListener('load', function(){ setTimeout(fitCheck, 300); });
""" % SAFE
