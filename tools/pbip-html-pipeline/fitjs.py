# -*- coding: utf-8 -*-
"""fitCheck() injected into preview pages. FIT OK needs every card iframe to pass two checks:

1. Nothing clipped: SAFE px of slack at the bottom and sides. An element marked data-bleed (a full-bleed band that
   is meant to reach the card edge) is skipped; its children are still checked.
2. No large empty band: the space between the lowest visible "ink" (text, a filled or bordered box, an svg/img) and
   the card's bottom padding must stay under max(EMPTY_MIN px, EMPTY_SHARE x card height). A card that leaves half
   its height blank looks broken - fill it (stretch rows, more rows, a second element) or make the card smaller.
   Exempt: a card containing an element marked data-fill='free' (background layer, empty-state message)."""
SAFE = 8            # px of slack every card keeps at the bottom/sides
EMPTY_SHARE = 0.15  # an empty band taller than 15% of the card fails ...
EMPTY_MIN = 40      # ... and never below 40px (small cards keep normal breathing room)
FIT_JS = """
function _ink(el){
  if(el.tagName==='svg'||el.tagName==='IMG') return true;
  for(var i=0;i<el.childNodes.length;i++){var n=el.childNodes[i]; if(n.nodeType===3 && n.textContent.trim()) return true;}
  var cs=getComputedStyle(el);
  if(cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)' && cs.backgroundColor!=='transparent') return true;
  if(cs.backgroundImage && cs.backgroundImage!=='none') return true;
  return ['Top','Bottom','Left','Right'].some(function(s){return parseFloat(cs['border'+s+'Width'])>0 && cs['border'+s+'Style']!=='none';});
}
function fitCheck(){
  var SAFE=%d, SHARE=%s, MINPX=%d, out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){ try{
    var d=f.contentDocument, root=d && d.body && d.body.firstElementChild; if(!root) {out.push(f.dataset.name+': EMPTY');return;}
    var W=f.clientWidth, H=f.clientHeight, worst=null, ink=0;
    /* motion: measure the resting layout - entrances at their end, endless loops at their start - then put every
       animation back where it was (finish() would end a fill:none animation for good and change the page) */
    var saved=[];
    try{ (d.getAnimations ? d.getAnimations() : []).forEach(function(a){ try{
      saved.push([a, a.currentTime, a.playState]);
      var tm=a.effect.getComputedTiming(); a.pause(); a.currentTime = tm.iterations===Infinity ? 0 : tm.endTime;
    }catch(e){} }); }catch(e){}
    root.querySelectorAll('*').forEach(function(el){
      /* .fit-clip = clipped on purpose (odometer digit strips, sweeping sheens) */
      if(el.closest && el.closest('.fit-clip')) return;
      var r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
      if(!el.closest('svg') || el.tagName==='svg') { if(_ink(el)) ink=Math.max(ink, r.bottom); }
      if(el.hasAttribute('data-bleed')) return;   // full-bleed decoration (card band); its children are still checked
      var over=Math.max(r.bottom-(H-SAFE), r.right-(W-SAFE), SAFE-r.left);
      if(over>0.5 && (!worst||over>worst.over)) worst={over:over,tag:el.tagName,txt:(el.textContent||'').trim().slice(0,40)};
    });
    if(root.scrollHeight>H+0.5) out.push(f.dataset.name+': content '+(root.scrollHeight-H)+'px taller than the visual');
    saved.forEach(function(s){ try{ s[0].currentTime=s[1]; if(s[2]==='running') s[0].play(); }catch(e){} });
    if(worst) out.push(f.dataset.name+': '+Math.round(worst.over)+'px past the safe edge at <'+worst.tag+'> "'+worst.txt+'"');
    var free=root.matches('[data-fill=free]') || root.querySelector('[data-fill=free]');
    if(!free && root.children.length){
      var pad=parseFloat(getComputedStyle(root).paddingBottom)||0, gap=Math.round(H-pad-ink), lim=Math.max(MINPX, SHARE*H);
      if(gap>lim) out.push(f.dataset.name+': '+gap+'px empty band at the bottom (limit '+Math.round(lim)+'px) - fill the card or make it smaller');
    }
  }catch(e){ out.push(f.dataset.name+': fit check error '+e); } });
  var p=document.getElementById('fit'); p.textContent = out.length ? 'FIT FAIL\\n'+out.join('\\n') : 'FIT OK';
}
window.addEventListener('load', function(){ setTimeout(fitCheck, 300); });
""" % (SAFE, EMPTY_SHARE, EMPTY_MIN)
