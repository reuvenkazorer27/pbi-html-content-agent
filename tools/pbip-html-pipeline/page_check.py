# -*- coding: utf-8 -*-
"""Gate ONE full-page HTML Content visual (the HTML a fullscreen measure returns) without a model or PBIP.

  python -I page_check.py page.html [--size 1920x1080] [--frames 0.3,0.8,1.4,2.2,3.5,6] [--no-fluid]

1. Secure lint (page_kit.lint): no script/handlers/external files/fake controls/loops/reduced-motion query
2. fluid(): the page as it will ship (scales with the visual, pinned root line-height)
3. exact-size preview + fitcheck.mjs: FIT (safe edge, empty band, inner void, cut text) + WCAG CONTRAST
4. motion_frames.mjs: frozen frames -> <page>_frames/<t>s.png (+ a montage <page>_frames.png when Pillow is present)
Writes <page>.png (rest state). Exit 1 on any failure. Same gates as the card pipeline (fitjs.py, fitcheck.mjs)."""
import sys, os, html as H, subprocess, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import page_kit
from fitjs import FIT_JS

ap = argparse.ArgumentParser()
ap.add_argument("page"); ap.add_argument("--size", default="1920x1080")
ap.add_argument("--frames", default="0.3,0.8,1.4,2.2,3.5,6"); ap.add_argument("--no-fluid", action="store_true")
a = ap.parse_args()
W, Hh = (int(v) for v in a.size.lower().split("x"))
src = os.path.abspath(a.page); base = os.path.splitext(src)[0]
page = open(src, encoding="utf-8").read()
ok = True
bad = page_kit.lint(page)
print("SECURE LINT", "OK" if not bad else "FAIL: " + "; ".join(bad), f"| {len(page):,} chars")
ok &= not bad
if not a.no_fluid:
    page = page_kit.fluid(page, W, Hh)
doc = "<!doctype html><html><body style='margin:0'>" + page + "</body></html>"
prev = base + "_preview.html"
open(prev, "w", encoding="utf-8").write(
    "<!doctype html><html><head><meta charset='utf-8'><title>Page check</title></head><body style='margin:0;background:#E5E7EB'>"
    f"<div style='position:relative;width:{W}px;height:{Hh}px'><iframe data-name='page' title='page' "
    f"style='position:absolute;left:0;top:0;width:{W}px;height:{Hh}px;border:0' srcdoc=\"{H.escape(doc, quote=True)}\"></iframe></div>"
    "<pre id='fit' style='display:none'></pre><script>" + FIT_JS + "</script></body></html>")
r = subprocess.run(["node", os.path.join(HERE, "fitcheck.mjs"), prev, "--shot", base + ".png"], capture_output=True, text=True)
out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("screenshot"))
print(out)
ok &= "FIT OK" in out and "CONTRAST OK" in out
if a.frames:
    fdir = base + "_frames"; os.makedirs(fdir, exist_ok=True)
    f = subprocess.run(["node", os.path.join(HERE, "motion_frames.mjs"), prev, os.path.join(fdir, "f"), a.frames, f"0,0,{W},{Hh}"],
                       capture_output=True, text=True)
    print((f.stdout.strip().splitlines() or [f.stderr[-300:]])[-1])
    try:
        from PIL import Image, ImageDraw
        ts = a.frames.split(","); ims = []
        for t in ts:
            p = os.path.join(fdir, f"f_{float(t):g}s.png")
            if os.path.exists(p):
                ims.append((t, Image.open(p).resize((640, int(640 * Hh / W)))))
        if ims:
            ch = ims[0][1].height + 18
            m = Image.new("RGB", (640 * 3, ch * ((len(ims) + 2) // 3)), "white"); d = ImageDraw.Draw(m)
            for i, (t, im) in enumerate(ims):
                x, y = (i % 3) * 640, (i // 3) * ch; d.text((x + 4, y + 3), f"t={t}s", fill="black"); m.paste(im, (x, y + 18))
            m.save(base + "_frames.png")
    except ImportError:
        pass
os.remove(prev)
print("PAGE OK" if ok else "PAGE FAIL")
sys.exit(0 if ok else 1)
