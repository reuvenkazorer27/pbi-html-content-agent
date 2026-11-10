# -*- coding: utf-8 -*-
"""Layout gate: no visual placed on top of another ("never create on top").

Rules checked on LAYOUT (HTML visuals) and SLICERS (native slicers):
- every visual lies inside the page canvas
- HTML visuals do not overlap each other - except a full-page background layer (it is meant to be under everything)
- a slicer sits entirely inside exactly one HTML visual (the filter panel that draws its label) and overlaps
  nothing else; slicers do not overlap each other

  python -I layout_check.py        -> checks measures.py; exit 1 with the list of problems
gen_pbip.py runs the same check and refuses to write the PBIP when it fails."""
import os, sys


def _overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _inside(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return bx <= ax and by <= ay and ax + aw <= bx + bw and ay + ah <= by + bh


def check(layout, slicers, page_w=1920, page_h=1080):
    """returns a list of problems (empty = OK)"""
    bad = []
    page = (0, 0, page_w, page_h)
    html = [(n, (x, y, w, h)) for n, _m, x, y, w, h in layout]
    sl = [(n, (x, y, w, h)) for n, _c, x, y, w, h in slicers]
    for n, r in html + sl:
        if not _inside(r, page):
            bad.append(f"{n} {r} is outside the {page_w}x{page_h} page")
    layers = {n for n, r in html if r == page}            # full-page background layer(s)
    body = [(n, r) for n, r in html if n not in layers]
    for i, (n1, r1) in enumerate(body):
        for n2, r2 in body[i + 1:]:
            if _overlap(r1, r2):
                bad.append(f"{n1} {r1} overlaps {n2} {r2}")
    for i, (n, r) in enumerate(sl):
        hosts = [hn for hn, hr in body if _inside(r, hr)]
        hits = [hn for hn, hr in body if _overlap(r, hr) and hn not in hosts]
        if len(hosts) != 1:
            bad.append(f"slicer {n} {r} must sit inside exactly one HTML panel (found {hosts or 'none'})")
        if hits:
            bad.append(f"slicer {n} {r} also overlaps {hits}")
        for n2, r2 in sl[i + 1:]:
            if _overlap(r, r2):
                bad.append(f"slicer {n} {r} overlaps slicer {n2} {r2}")
    return bad


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import measures as ms
    problems = check(ms.LAYOUT, ms.SLICERS, getattr(ms, "PAGE_W", 1920), getattr(ms, "PAGE_H", 1080))
    print("\n".join(problems) or "LAYOUT OK")
    sys.exit(1 if problems else 0)
