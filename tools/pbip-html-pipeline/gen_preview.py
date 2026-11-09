# -*- coding: utf-8 -*-
"""Build a 1920x1080 browser preview from real measure output (r_*.json),
with an automatic FIT CHECK: every HTML card is rendered at its exact visual size
and any element that ends past the card edge (minus SAFE px) is reported.

  python gen_preview.py r_all.json preview.html
  bash fitcheck.sh preview.html        -> prints FIT OK or the list of overflows
"""
import sys, os, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures import LAYOUT, SLICERS, DIR, LANG
from palette import P as PAL


res, out = sys.argv[1], sys.argv[2]
row = json.load(open(res, encoding="utf-8-sig"))
row = row[0] if isinstance(row, list) else row
val = {k.strip("[]"): v for k, v in row.items()}

parts = []
for name, meas, x, y, w, h in LAYOUT:
    doc = "<!doctype html><html><body style='margin:0'>" + val.get(meas, "") + "</body></html>"
    parts.append(f"<iframe data-name='{name}' title='{name}' style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:0' srcdoc=\"{html.escape(doc, quote=True)}\"></iframe>")
for name, lbl, x, y, w, h in SLICERS:
    parts.append(f"<div style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;box-sizing:border-box;padding:0 12px;border:1px solid {PAL['slicer_border']};border-radius:6px;background:{PAL['slicer_bg']};display:flex;align-items:center;justify-content:space-between;font:15px Segoe UI;color:{PAL['slicer_fg']}' dir='{DIR}'>{'הכל' if LANG == 'he' else 'All'} <span>&#9662;</span></div>")  # mock dropdown text: Hebrew 'הכל' = 'All'

from fitjs import FIT_JS   # shared with component_lab_example.py

page = ("<!doctype html><html><head><meta charset='utf-8'><title>Preview</title></head>"
        f"<body style='margin:0;background:#E5E7EB'><div style='position:relative;width:1920px;height:1080px;background:{PAL['page_bg']}'>"
        + "".join(parts) + "</div><pre id='fit' style='display:none'></pre>"
        "<script>var q=new URLSearchParams(location.search);if(q.get('x')!==null){document.body.firstChild.style.transform='translate(-'+q.get('x')+'px,-'+q.get('y')+'px)'}"
        + FIT_JS + "</script></body></html>")
open(out, "w", encoding="utf-8").write(page)
print("ok")
