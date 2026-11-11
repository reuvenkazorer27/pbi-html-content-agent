# -*- coding: utf-8 -*-
"""fitCheck() injected into preview pages. FIT OK needs every card iframe to pass two checks:

1. Nothing clipped: SAFE px of slack at the bottom and sides. An element marked data-bleed (a full-bleed band that
   is meant to reach the card edge) is skipped; its children are still checked.
2. No large empty band: the space between the lowest visible "ink" (text, a filled or bordered box, an svg/img) and
   the card's bottom padding must stay under max(EMPTY_MIN px, EMPTY_SHARE x card height). A card that leaves half
   its height blank looks broken - fill it (stretch rows, more rows, a second element) or make the card smaller.
   Exempt: a card containing an element marked data-fill='free' (background layer, empty-state message).
3. No large void inside: the biggest vertical gap between ink boxes (from the first ink to the last) must stay under
   max(VOID_MIN px, EMPTY_SHARE x card height) - one tile at the top and a block at the bottom with nothing between
   them fails like an empty bottom band. Boxes taller than 85% of the card (the card's own surface) are not ink here.
   An element marked data-fill='slot' counts as ink: it reserves room for a native visual placed on top of the card
   (a slicer under its HTML label)."""
SAFE = 8            # px of slack every card keeps at the bottom/sides
EMPTY_SHARE = 0.15  # an empty band taller than 15% of the card fails ...
EMPTY_MIN = 40      # ... and never below 40px (small cards keep normal breathing room)
VOID_MIN = 60       # an internal gap fails above max(60px, 15% of the card height)
FIT_JS = """
function _ink(el){
  if(el.tagName==='svg'||el.tagName==='IMG'||el.getAttribute('data-fill')==='slot') return true;
  for(var i=0;i<el.childNodes.length;i++){var n=el.childNodes[i]; if(n.nodeType===3 && n.textContent.trim()) return true;}
  var cs=getComputedStyle(el);
  if(cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)' && cs.backgroundColor!=='transparent') return true;
  if(cs.backgroundImage && cs.backgroundImage!=='none') return true;
  return ['Top','Bottom','Left','Right'].some(function(s){return parseFloat(cs['border'+s+'Width'])>0 && cs['border'+s+'Style']!=='none';});
}
/* the vertical extent an ink element really paints: a box with only a top/bottom rule (a section divider around
   other content) paints those lines, not its whole height - otherwise it would hide a void inside it */
function _inkBoxes(el, r){
  var cs=getComputedStyle(el), filled=(cs.backgroundColor && cs.backgroundColor!=='rgba(0, 0, 0, 0)' && cs.backgroundColor!=='transparent')
      || (cs.backgroundImage && cs.backgroundImage!=='none');
  var text=false; for(var i=0;i<el.childNodes.length;i++){var n=el.childNodes[i]; if(n.nodeType===3 && n.textContent.trim()) text=true;}
  var sides=function(s){return parseFloat(cs['border'+s+'Width'])>0 && cs['border'+s+'Style']!=='none';};
  if(filled || text || el.tagName==='svg' || el.tagName==='IMG' || el.getAttribute('data-fill')==='slot' || sides('Left') || sides('Right'))
    return [[r.top, r.bottom]];
  var out=[]; if(sides('Top')) out.push([r.top, r.top+parseFloat(cs.borderTopWidth)]);
  if(sides('Bottom')) out.push([r.bottom-parseFloat(cs.borderBottomWidth), r.bottom]);
  return out;
}
function fitCheck(){
  var SAFE=%d, SHARE=%s, MINPX=%d, VOIDPX=%d, out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){ try{
    var d=f.contentDocument, root=d && d.body && d.body.firstElementChild; if(!root) {out.push(f.dataset.name+': EMPTY');return;}
    var W=f.clientWidth, H=f.clientHeight, worst=null, ink=0, boxes=[];
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
      if(!el.closest('svg') || el.tagName==='svg') { if(_ink(el)) { ink=Math.max(ink, r.bottom); if(el!==root && r.height<0.85*H) boxes.push.apply(boxes, _inkBoxes(el, r)); } }
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
      boxes.sort(function(a,b){return a[0]-b[0];});
      var reach=boxes.length?boxes[0][1]:0, vgap=0, vat=0;
      boxes.forEach(function(b){ if(b[0]-reach>vgap){vgap=b[0]-reach; vat=reach;} reach=Math.max(reach,b[1]); });
      var vlim=Math.max(VOIDPX, SHARE*H);
      if(vgap>vlim) out.push(f.dataset.name+': '+Math.round(vgap)+'px empty gap inside the card at y='+Math.round(vat)+' (limit '+Math.round(vlim)+'px) - let the content stretch or fill the gap');
    }
  }catch(e){ out.push(f.dataset.name+': fit check error '+e); } });
  var p=document.getElementById('fit'); p.textContent = out.length ? 'FIT FAIL\\n'+out.join('\\n') : 'FIT OK';
}
window.addEventListener('load', function(){ setTimeout(fitCheck, 300); });
""" % (SAFE, EMPTY_SHARE, EMPTY_MIN, VOID_MIN)
