# -*- coding: utf-8 -*-
"""The organization's logo: its colors for the style, and the logo itself in the header or side rail.

  python -I logo.py check <logo.svg|png> [--on #RRGGBB]   -> dominant colors, brand + accent, fragment size,
                                                           plate needed on --on, style_check of the derived style.
                                                           Exit 1 on any failure.

pipeline.json
  "logo": {"path": "../brand/logo.svg", "height": 40, "alt": "Tidewell"}   (path relative to _build/)
  "style": {"logo": true, "preset": "mint"}     -> brand + accent from the logo, the preset's look and palette
  "style": {"logo": true, "mode": "dark"}       -> make_style() from the logo
  Official brand hex values win: {"logo": true, "brand": "#0B5D6B"} keeps the logo's accent and your brand.

In measures.py
  import logo
  LOGO = logo.html(40)                       # "" when pipeline.json has no "logo": the header just has no logo
  LOGO = logo.html(48, align="flex-start")   # in a flex column (side rail): a stretched <svg> centers its drawing
  LOGO = logo.html(40, on=P["surface"])      # `on` = the real color behind the logo (a hex, not a @@token@@):
                                             # a white plate is added when the logo would not read on it

What it does
1. extract(path)       dominant colors of the logo with weights. SVG: every painted shape (rect, circle, ellipse,
                       path, polygon, polyline, line, text) with its fill - an attribute, inline style, a <style> class
                       rule, a gradient (its stops), or inherited from a <g> - or its stroke when it has no fill,
                       weighted by rough area. Hex, rgb() and basic named colors. PNG/JPG (needs Pillow): opaque
                       pixels. Colors are grouped in 20deg hue bins (anti-aliasing shades merge; the bin's most
                       frequent exact color represents it); white / black / grays are the logo's ink, kept apart.
2. brand_accent(cols)  brand = the chromatic color with the largest area, accent = the largest one at least 35deg of
                       hue away (None for a one-hue logo). A logo with no chromatic color: brand = its darkest ink.
                       No color found at all is an error, never a made-up brand.
                       Extraction only proposes: show the two colors to the user, an official hex wins.
3. html(...)           the fragment for a measure. SVG inline (sanitized: no script, foreignObject, on*=, external
                       href, external url() or @import; attributes in single quotes so it sits in a DAX "..." string)
                       or PNG as <img src='data:image/png;base64,...'> at 2x the display height, palette-quantized.
                       Both measured in Desktop (Secure edition). Gate: <= 12 KB.
4. plate_needed(cols, bg)  the logo is never recolored; when any of its significant colors (a mark, the wordmark) is
                       under 3:1 on the background it sits on and a white plate fixes that, html(on=bg) puts it on a
                       white plate.

Rules: reference/design-system.md §4 (logos); when to redesign vs re-skin: skills/colorful-styles/SKILL.md."""
import base64
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # python -I drops the script folder from sys.path
from palette import _lum, contrast  # noqa: E402  (one WCAG implementation for the whole kit)
from styles import _hls  # noqa: E402

MAX_BYTES = 12_000
SIGNIFICANT = 0.05   # a color covering at least 5% of the logo counts for the plate decision (a wordmark does)
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
NAMED = {"black": "#000000", "white": "#FFFFFF", "red": "#FF0000", "green": "#008000", "blue": "#0000FF",
         "yellow": "#FFFF00", "orange": "#FFA500", "purple": "#800080", "gray": "#808080", "grey": "#808080",
         "navy": "#000080", "teal": "#008080", "maroon": "#800000"}


def _norm(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


# ---------------------------------------------------------------- 1. dominant colors
def _chromatic(c):
    _, l, s = _hls(c)   # chroma, not HSL saturation: a dark slate (#1F2937) is ink, not a brand hue
    return s * (1 - abs(2 * l - 1)) >= 0.12 and 0.10 <= l <= 0.92


def _area(tag, attrs):
    """rough painted area of one SVG element (logos are flat shapes: good enough to rank colors)"""
    def num(k, d=0.0):
        m = re.search(r"[-\d.]+", attrs.get(k, str(d)))
        return float(m.group()) if m else d
    if tag == "rect":
        return num("width") * num("height")
    if tag == "circle":
        return 3.1416 * num("r") ** 2
    if tag == "ellipse":
        return 3.1416 * num("rx") * num("ry")
    if tag == "text":
        return 1.2 * num("font-size", 16) ** 2   # a word of strokes, not its bounding box
    if tag == "line":
        return 4 * (abs(num("x2") - num("x1")) + abs(num("y2") - num("y1")))
    if tag in ("path", "polygon", "polyline"):
        v = [float(x) for x in re.findall(r"-?\d+\.?\d*", attrs.get("d", attrs.get("points", "")))]
        if len(v) >= 4:
            return 0.5 * (max(v[0::2]) - min(v[0::2])) * (max(v[1::2]) - min(v[1::2]))
    return 100.0


def _bin(pairs):
    bins, ink = {}, {}
    for c, w in pairs:
        b = bins.setdefault(int(_hls(c)[0] // 20), {}) if _chromatic(c) else \
            ink.setdefault("light" if _lum(c) > 0.5 else "dark", {})
        b[c] = b.get(c, 0) + w
    tot = sum(w for _, w in pairs) or 1
    out = [(max(b, key=b.get), sum(b.values()) / tot) for b in list(bins.values()) + list(ink.values())]
    return sorted(out, key=lambda t: -t[1])


def _paints(value, grads):
    """a fill/stroke value -> list of hex colors ([] for none / transparent / unknown)"""
    v = (value or "").strip()
    m = re.match(r"url\(\s*['\"]?#([\w-]+)", v)
    if m:
        return grads.get(m.group(1), [])
    if HEX.match(v):
        return [_norm(HEX.match(v).group())]
    m = re.match(r"rgba?\(\s*(\d+)\D+(\d+)\D+(\d+)", v)
    if m:
        return ["#%02X%02X%02X" % tuple(min(255, int(x)) for x in m.groups())]
    return [NAMED[v.lower()]] if v.lower() in NAMED else []


def _svg_pairs(txt):
    # <style> rules: .cls-1, .cls-2 { fill: #..; stroke: .. }  (Illustrator / Figma exports)
    css = {}
    for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", " ".join(re.findall(r"<style[^>]*>(.*?)</style>", txt, re.S))):
        props = dict((k.strip().lower(), v.strip()) for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", body))
        for s in sel.split(","):
            s = s.strip()
            if s.startswith("."):
                css.setdefault(s[1:], {}).update(props)
    # gradients: id -> stop colors
    grads = {}
    for gid, body in re.findall(r"<(?:linear|radial)Gradient\b[^>]*\bid=['\"]([\w-]+)['\"][^>]*>(.*?)</(?:linear|radial)Gradient>",
                                txt, re.S):
        stops = re.findall(r"stop-color\s*[=:]\s*['\"]?\s*([^'\";>]+)", body)
        grads[gid] = [c for s in stops for c in _paints(s, {})]
    pairs, stack, hidden = [], [{"fill": "#000000", "stroke": None}], 0   # SVG default fill is black
    for close, tag, body, selfclose in re.findall(r"<(/?)([a-zA-Z]+)\b([^>]*?)(/?)>", txt):
        if tag in ("defs", "clipPath", "mask", "symbol", "pattern", "marker"):   # shapes in here are not painted as such
            hidden += -1 if close else (0 if selfclose else 1)
            continue
        if hidden:   # opening and closing tags inside defs / clipPath / mask touch neither the paint stack nor the colors
            continue
        if close:
            if tag in ("g", "svg", "a") and len(stack) > 1:
                stack.pop()
            continue
        attrs = dict(re.findall(r"([\w:-]+)\s*=\s*['\"]([^'\"]*)['\"]", body))
        paint = dict(stack[-1])
        for cls in attrs.get("class", "").split():
            paint.update({k: v for k, v in css.get(cls, {}).items() if k in ("fill", "stroke")})
        for k in ("fill", "stroke"):
            if k in attrs:
                paint[k] = attrs[k]
        m = re.findall(r"(fill|stroke)\s*:\s*([^;]+)", attrs.get("style", ""))
        paint.update({k: v.strip() for k, v in m})
        if tag in ("g", "svg", "a"):
            if not selfclose:
                stack.append(paint)
            continue
        if tag not in ("rect", "circle", "ellipse", "path", "polygon", "polyline", "line", "text"):
            continue
        area = _area(tag, attrs)
        fills = _paints(paint.get("fill"), grads) if tag != "line" else []
        cols, w = (fills, area) if fills else (_paints(paint.get("stroke"), grads), area * 0.2)   # stroke-only line art
        for c in cols:
            pairs.append((c, w / len(cols)))
    return pairs


def extract(path):
    """[(hex, share)] largest first; [] when no color could be read"""
    if path.lower().endswith(".svg"):
        return _bin(_svg_pairs(open(path, encoding="utf-8").read()))
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("a PNG/JPG logo needs Pillow (pip install pillow) - or give an SVG")
    im = Image.open(path).convert("RGBA")
    im.thumbnail((240, 240))
    counts = {}
    for r, g, b, a in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()):
        if a >= 200:
            c = f"#{r:02X}{g:02X}{b:02X}"
            counts[c] = counts.get(c, 0) + 1
    return _bin(list(counts.items()))


# ---------------------------------------------------------------- 2. brand + accent
def _hue_gap(a, b):
    d = abs(_hls(a)[0] - _hls(b)[0]) % 360
    return min(d, 360 - d)


def brand_accent(cols):
    if not cols:
        raise SystemExit("no colors found in the logo (SVG paint as hex / rgb() / class / gradient, or an opaque "
                         "PNG): give the brand hex in pipeline.json \"style\" instead")
    chroma = [(c, w) for c, w in cols if _chromatic(c)]
    ink = [c for c, _ in cols if not _chromatic(c)]
    if not chroma:   # one-color / black-and-white logo: the darkest ink is the brand, no accent
        return {"brand": min(ink, key=_lum), "accent": None, "ink": ink, "mono": True}
    brand = max(chroma, key=lambda t: t[1])[0]
    rest = [(c, w) for c, w in chroma if _hue_gap(c, brand) >= 35]
    accent = max(rest, key=lambda t: t[1])[0] if rest else None
    return {"brand": brand, "accent": accent, "ink": ink, "mono": False}


def plate_needed(cols, bg):
    """True when a significant non-white color of the logo (its mark or its wordmark) is under 3:1 (WCAG non-text) on
    bg AND a white plate fixes it (a light logo color on a light page: a white plate would not help)"""
    if not HEX.match(bg or ""):
        return False
    return any(contrast(c, bg) < 3.0 and contrast(c, "#FFFFFF") >= 3.0
               for c, w in cols if w >= SIGNIFICANT and _lum(c) < 0.85)


# ---------------------------------------------------------------- 3. the fragment for a measure
def _sanitize_svg(txt):
    txt = re.sub(r"<\?xml.*?\?>|<!--.*?-->|<!DOCTYPE[^\[>]*(\[.*?\])?\s*>", "", txt, flags=re.S)
    if re.search(r"<script|<foreignObject|\son\w+\s*=|(?:xlink:)?href\s*=\s*['\"](?!#)"
                 r"|url\(\s*['\"]?\s*(?!#)|@import", txt, re.I):
        raise SystemExit("logo SVG has a script, foreignObject, an event handler or an external reference (href, "
                         "url(), @import) - export a clean SVG (the Secure edition strips them, and the whole element "
                         "can go with them)")
    txt = re.sub(r"\s+", " ", txt).strip()
    # the measures' add() rescales every 'font-size:NNpx' (FONT_SCALE); '.0px' keeps a wordmark's own size
    txt = re.sub(r"font-size\s*:\s*(\d+)px", r"font-size:\1.0px", txt)
    return txt.replace('"', "'")   # attributes in single quotes: the fragment sits in a DAX "..." string


def fragment(path, height, max_width=None, alt="logo", align="center", on=None, cols=None):
    """the logo as HTML for a measure; see the module doc. `cols` = extract(path) when the caller has it already"""
    mw = f"max-width:{max_width}px;" if max_width else ""
    st = f"height:{height}px;width:auto;{mw}display:block;flex:none"
    alt = alt.replace("'", "&#39;").replace('"', "&quot;")
    if path.lower().endswith(".svg"):
        svg = _sanitize_svg(open(path, encoding="utf-8").read())
        for _ in range(2):   # the root's own width / height go: the style sizes it, the viewBox keeps the ratio
            svg = re.sub(r"(<svg\b[^>]*?)\s(?:width|height)='[^']*'", r"\1", svg, count=1)
        if "viewBox" not in svg.split(">", 1)[0]:
            raise SystemExit("logo SVG needs a viewBox to scale")
        # a logo is an image: it never mirrors. Without direction:ltr an SVG <text> wordmark inherits the RTL card's
        # direction and runs from the wrong end over the mark (measured in an RTL build)
        frag = svg.replace("<svg", f"<svg role='img' aria-label='{alt}' style='{st};direction:ltr;unicode-bidi:isolate'", 1)
    else:
        try:
            from PIL import Image
        except ImportError:
            raise SystemExit("a PNG/JPG logo needs Pillow (pip install pillow) - or give an SVG")
        im = Image.open(path).convert("RGBA")
        im.thumbnail((10_000, height * 2), Image.LANCZOS)   # 2x the display height, no larger
        buf = io.BytesIO()
        im.quantize(64, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        frag = f"<img alt='{alt}' src='data:image/png;base64,{b64}' style='{st}'>"
    if on and plate_needed(cols if cols is not None else extract(path), on):   # never recolor a logo: plate it
        frag = f"<div style='flex:none;background:#FFFFFF;border-radius:8px;padding:6px 10px'>{frag}</div>"
    frag = f"<div style='flex:none;align-self:{align};display:flex'>{frag}</div>"
    if len(frag) > MAX_BYTES:
        raise SystemExit(f"logo fragment is {len(frag)} characters > {MAX_BYTES}: simplify the SVG or use a smaller "
                         "PNG (every card that shows the logo carries it)")
    return frag


def _config():
    try:
        cfg = json.load(open(os.path.join(HERE, "pipeline.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    lg = cfg.get("logo")
    if not lg:
        return None
    lg = {"path": lg} if isinstance(lg, str) else dict(lg)
    lg["path"] = os.path.normpath(os.path.join(HERE, lg["path"]))
    if not os.path.exists(lg["path"]):
        raise SystemExit(f"pipeline.json \"logo\": no file at {lg['path']} (the path is relative to _build/)")
    return lg


def path():
    """the configured logo file, or None"""
    lg = _config()
    return lg["path"] if lg else None


def html(height=None, **kw):
    """the configured logo as an HTML fragment, or "" when pipeline.json has no "logo" """
    lg = _config()
    if not lg:
        return ""
    kw.setdefault("alt", lg.get("alt", "logo"))
    return fragment(lg["path"], height or lg.get("height", 40), **kw)


def colors(p=None):
    """brand + accent of a logo file (default: the configured one)"""
    p = os.path.normpath(os.path.join(HERE, p)) if p else path()   # a path in "style": {"logo": "..."} is relative to _build/
    if not p:
        raise SystemExit('"style": {"logo": true} needs "logo" in pipeline.json')
    return brand_accent(extract(p))


# ---------------------------------------------------------------- check
def main(argv):
    if len(argv) < 2 or argv[0] != "check":
        print(__doc__.split("\n\n")[0])
        return 2
    p = argv[1]
    on = argv[argv.index("--on") + 1] if "--on" in argv else "#FFFFFF"
    cols = extract(p)
    if not cols:
        print("LOGO FAIL no colors found (SVG paint as hex / rgb() / class / gradient, or an opaque PNG)")
        return 1
    ba = brand_accent(cols)
    print("dominant:", ", ".join(f"{c} {w:.0%}" for c, w in cols[:6]))
    print(f"brand {ba['brand']}  accent {ba['accent']}  {'(one-color logo: accent from the preset)' if ba['mono'] else ''}")
    for h in (40, 48):
        print(f"fragment at {h}px: {len(fragment(p, h, on=on, cols=cols))} characters")
    print(f"on {on}: {'plate (a significant color under 3:1)' if plate_needed(cols, on) else 'no plate needed'}")
    import styles as S
    import style_check
    fails = [f"{mode}/{mech}: {e}" for mode in ("light", "dark") for mech in S.MECHANISMS
             if (e := style_check.check(S.make_style(ba["brand"], accent=ba["accent"], mode=mode, mechanism=mech)))]
    print("LOGO OK" if not fails else "LOGO FAIL " + "; ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
