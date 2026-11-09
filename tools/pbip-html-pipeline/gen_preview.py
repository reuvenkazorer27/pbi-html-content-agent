# -*- coding: utf-8 -*-
"""Build a 1920x1080 browser preview from real measure output (r_*.json),
with an automatic FIT CHECK: every HTML card is rendered at its exact visual size
and any element that ends past the card edge (minus SAFE px) is reported.

  python gen_preview.py r_all.json preview.html
  bash fitcheck.sh preview.html        -> prints FIT OK or the list of overflows
"""
import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures import LAYOUT, SLICERS, DIR
from palette import P as PAL

SAFE = 8  # px of slack every card must keep at the bottom/sides (Desktop vs browser rounding)

res, out = sys.argv[1], sys.argv[2]
row = json.load(open(res, encoding="utf-8-sig"))
row = row[0] if isinstance(row, list) else row
val = {k.strip("[]"): v for k, v in row.items()}

parts = []
for name, meas, x, y, w, h in LAYOUT:
    doc = "<!doctype html><html><body style='margin:0'>" + val.get(meas, "") + "</body></html>"
    parts.append(f"<iframe data-name='{name}' title='{name}' style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:0' srcdoc=\"{html.escape(doc, quote=True)}\"></iframe>")
for name, lbl, x, y, w, h in SLICERS:
    parts.append(f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;box-sizing:border-box;padding:0 12px;border:1px solid {PAL['slicer_border']};border-radius:6px;background:{PAL['slicer_bg']};display:flex;align-items:center;justify-content:space-between;font:15px Segoe UI;color:{PAL['slicer_fg']}' dir='{DIR}'>{'הכל' if DIR == 'rtl' else 'All'} <span>&#9662;</span></div>")

FIT_JS = """
function fitCheck(){
  var SAFE=%d, out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){
    var d=f.contentDocument, root=d && d.body && d.body.firstElementChild; if(!root) {out.push(f.dataset.name+': EMPTY');return;}
    var W=f.clientWidth, H=f.clientHeight, worst=null;
    root.querySelectorAll('*').forEach(function(el){
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

page = ("<!doctype html><html><head><meta charset='utf-8'><title>Preview</title></head>"
        f"<body style='margin:0;background:#E5E7EB'><div style='position:relative;width:1920px;height:1080px;background:{PAL['page_bg']}'>"
        + "".join(parts) + "</div><pre id='fit' style='display:none'></pre>"
        "<script>var q=new URLSearchParams(location.search);if(q.get('x')!==null){document.body.firstChild.style.transform='translate(-'+q.get('x')+'px,-'+q.get('y')+'px)'}"
        + FIT_JS + "</script></body></html>")
open(out, "w", encoding="utf-8").write(page)
print("ok")
