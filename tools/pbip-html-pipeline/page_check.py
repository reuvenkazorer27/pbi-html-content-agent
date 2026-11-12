# -*- coding: utf-8 -*-
"""Gate full-page HTML Content visuals (the HTML a fullscreen measure returns) without a model or PBIP.

  python -I page_check.py page.html [more.html ...] [--size 1920x1080] [--frames 0.3,0.8,1.4,2.2,2.9,3.5,6] [--no-fluid]

Several pages = the base page plus its stress variants (one region, one month, empty ...) written by the same
generator; every page must pass. Per page:
1. Secure lint (page_kit.lint): no script/handlers/external files/fake controls/loops/reduced-motion query
2. fluid(): the page as it will ship (scales with the visual, pinned root line-height)
3. exact-size preview + fitcheck.mjs: the kit's FIT (safe edge, empty band, inner void, cut text) + WCAG CONTRAST,
   PLUS panel checks on every element marked data-panel (animations parked at their end):
     - content clipped by its panel (a row cut off by overflow:hidden)
     - an empty band at the bottom of a panel > max(40px, 15% of its height) (a hero 80% blank in a stress variant)
4. motion_frames.mjs: frozen frames -> <page>_frames/ (+ montage <page>_frames.png with Pillow); a crash or a frame
   with 0 animations while others have some is retried once, then fails the page
Writes <page>.png (rest state). Exit 1 on any failure."""
import sys, os, re, html as H, subprocess, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import page_kit
from fitjs import FIT_JS

PANEL_JS = r"""
function panelCheck(){
  var out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){
    var d=f.contentDocument, w=f.contentWindow; if(!d) return;
    var anims=d.getAnimations(), saved=anims.map(function(a){return a.currentTime});
    anims.forEach(function(a){try{var t=a.effect.getComputedTiming(); a.pause(); a.currentTime=t.endTime-1;}catch(e){}});
    d.querySelectorAll('[data-panel]').forEach(function(p){
      var pr=p.getBoundingClientRect(), name=p.getAttribute('data-panel')||p.className||'panel', cs=w.getComputedStyle(p);
      if(pr.height<20) return;
      var low=pr.top+parseFloat(cs.paddingTop), clip=null;
      p.querySelectorAll('*').forEach(function(el){
        if(el.closest('.fit-clip')||el.closest('[data-bleed]')||el.tagName==='STYLE') return;
        var r=el.getBoundingClientRect(), s=w.getComputedStyle(el);
        if(r.width<1||r.height<1||s.visibility==='hidden'||parseFloat(s.opacity)<0.05) return;
        var own=[].some.call(el.childNodes,function(n){return n.nodeType===3&&n.textContent.trim().length>0});
        var bg=s.backgroundColor, filled=(bg&&bg!=='rgba(0, 0, 0, 0)'&&bg!=='transparent')||s.backgroundImage!=='none';
        if(own||filled||el.tagName==='svg'||el.tagName==='IMG') low=Math.max(low,r.bottom);
        if(clip===null&&own&&(r.bottom>pr.bottom+1||r.right>pr.right+1||r.left<pr.left-1||r.top<pr.top-1))
          clip=(el.textContent||'').trim().slice(0,30);
      });
      if(clip!==null) out.push(f.dataset.name+': panel "'+name+'" clips its content at "'+clip+'" - give it room or show fewer rows');
      var free=p.querySelector('[data-fill=free]')||p.matches('[data-fill=free]');
      var band=pr.bottom-parseFloat(cs.paddingBottom)-low, lim=Math.max(40,0.15*pr.height);
      if(!free&&band>lim) out.push(f.dataset.name+': panel "'+name+'" has '+Math.round(band)+'px empty at the bottom (limit '+Math.round(lim)+'px)');
    });
    anims.forEach(function(a,i){try{a.currentTime=saved[i]; a.play();}catch(e){}});
  });
  return out;
}
var _kitFit=fitCheck;
fitCheck=function(){
  _kitFit(); var t=document.getElementById('fit'), extra=panelCheck();
  if(extra.length){ var cur=t.textContent; t.textContent=(cur.indexOf('FIT OK')===0?'FIT FAIL':cur)+'\n'+extra.join('\n'); }
};
"""


def gate(src, W, Hh, frames, use_fluid):
    page = open(src, encoding="utf-8").read(); base = os.path.splitext(src)[0]; ok = True
    bad = page_kit.lint(page)
    print("SECURE LINT", "OK" if not bad else "FAIL: " + "; ".join(bad), f"| {len(page):,} chars")
    ok &= not bad
    if use_fluid:
        page = page_kit.fluid(page, W, Hh)
    doc = "<!doctype html><html><body style='margin:0'>" + page + "</body></html>"
    prev = base + "_preview.html"
    open(prev, "w", encoding="utf-8").write(
        "<!doctype html><html><head><meta charset='utf-8'><title>Page check</title></head><body style='margin:0;background:#E5E7EB'>"
        f"<div style='position:relative;width:{W}px;height:{Hh}px'><iframe data-name='page' title='page' "
        f"style='position:absolute;left:0;top:0;width:{W}px;height:{Hh}px;border:0' srcdoc=\"{H.escape(doc, quote=True)}\"></iframe></div>"
        "<pre id='fit' style='display:none'></pre><script>" + FIT_JS + PANEL_JS + "</script></body></html>")
    for attempt in (1, 2):   # a cold headless Edge occasionally answers 'FIT CHECK ERROR Uncaught' - retry once
        r = subprocess.run(["node", os.path.join(HERE, "fitcheck.mjs"), prev, "--shot", base + ".png"], capture_output=True, text=True)
        out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("screenshot"))
        if "CHECK ERROR" not in out:
            break
    print(out)
    ok &= "FIT OK" in out and "CONTRAST OK" in out
    if frames:
        fdir = base + "_frames"; os.makedirs(fdir, exist_ok=True); fr_ok = False
        for attempt in (1, 2):
            f = subprocess.run(["node", os.path.join(HERE, "motion_frames.mjs"), prev, os.path.join(fdir, "f"), frames, f"0,0,{W},{Hh}"],
                               capture_output=True, text=True)
            m = re.search(r"animations found per frame: ([\d,]+)", f.stdout)
            counts = [int(c) for c in m.group(1).split(",")] if m else []
            fr_ok = bool(counts) and not (max(counts) > 0 and min(counts) == 0)
            if fr_ok:
                break
        print("FRAMES", "OK" if fr_ok else "FAIL (frame capture crashed or a frame came back empty)", counts or f.stderr[-200:].strip())
        ok &= fr_ok
        try:
            from PIL import Image, ImageDraw
            ims = []
            for t in frames.split(","):
                p = os.path.join(fdir, f"f_{float(t):g}s.png")
                if os.path.exists(p):
                    ims.append((t, Image.open(p).resize((960, int(960 * Hh / W)))))
            if ims:
                ch = ims[0][1].height + 18
                mt = Image.new("RGB", (960 * 2, ch * ((len(ims) + 1) // 2)), "white"); d = ImageDraw.Draw(mt)
                for i, (t, im) in enumerate(ims):
                    x, y = (i % 2) * 960, (i // 2) * ch; d.text((x + 4, y + 3), f"t={t}s", fill="black"); mt.paste(im, (x, y + 18))
                mt.save(base + "_frames.png")
        except ImportError:
            pass
    os.remove(prev)
    print(("PAGE OK " if ok else "PAGE FAIL ") + os.path.basename(src))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="+"); ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--frames", default="0.3,0.8,1.4,2.2,2.9,3.5,6"); ap.add_argument("--no-fluid", action="store_true")
    a = ap.parse_args()
    W, Hh = (int(v) for v in a.size.lower().split("x"))
    results = [gate(os.path.abspath(p), W, Hh, a.frames, not a.no_fluid) for p in a.pages]
    if len(results) > 1:
        print(f"ALL PAGES {'OK' if all(results) else 'FAIL'} ({sum(results)}/{len(results)})")
    sys.exit(0 if all(results) else 1)
