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
1. extract(path)       dominant colors of the logo with weights. SVG: each shape's fill weighted by its rough area
                       (rect, circle, ellipse, path / polygon bounding box, text). PNG/JPG (needs Pillow): opaque
                       pixels. Colors are grouped in 20deg hue bins (anti-aliasing shades merge; the bin's most
                       frequent exact color represents it); white / black / grays are the logo's ink, kept apart.
2. brand_accent(cols)  brand = the chromatic color with the largest area, accent = the largest one at least 35deg of
                       hue away (None for a one-hue logo). A logo with no chromatic color: brand = its darkest ink.
                       Extraction only proposes: show the two colors to the user, an official hex wins.
3. html(...)           the fragment for a measure. SVG inline (sanitized: no script, foreignObject, on*= or external
                       href; attributes in single quotes so it sits in a DAX "..." string) or PNG as
                       <img src='data:image/png;base64,...'> at 2x the display height, palette-quantized. Both measured
                       in Desktop (Secure edition). Gate: <= 12 KB.
4. plate_needed(cols, bg)  the logo is never recolored; when its main color is under 3:1 on the background it sits on,
                       html(on=bg) puts it on a white plate.

Rules: reference/design-system.md §4 (logos); when to redesign vs re-skin: skills/colorful-styles/SKILL.md."""
import base64
import colorsys
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BYTES = 12_000
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def _norm(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def _hls(c):
    c = c.lstrip("#")
    h, l, s = colorsys.rgb_to_hls(*(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)))
    return h * 360, l, s


def _lum(c):
    c = c.lstrip("#")
    ch = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


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


def extract(path):
    """[(hex, share)] largest first"""
    if path.lower().endswith(".svg"):
        txt = open(path, encoding="utf-8").read()
        pairs = []
        for tag, body in re.findall(r"<(rect|circle|ellipse|path|polygon|polyline|text)\b([^>]*)>", txt):
            attrs = dict(re.findall(r"([\w-]+)\s*=\s*['\"]([^'\"]*)['\"]", body))
            m = re.search(r"fill\s*:\s*(#[0-9a-fA-F]{3,6})", attrs.get("style", ""))
            fill = attrs.get("fill") or (m.group(1) if m else None)
            if fill and HEX.match(fill):
                pairs.append((_norm(fill), _area(tag, attrs)))
        return _bin(pairs)
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
    chroma = [(c, w) for c, w in cols if _chromatic(c)]
    ink = [c for c, _ in cols if not _chromatic(c)]
    if not chroma:   # one-color / black-and-white logo: the darkest ink is the brand, no accent
        dark = sorted(ink, key=_lum)
        return {"brand": dark[0] if dark else "#334155", "accent": None, "ink": ink, "mono": True}
    brand = max(chroma, key=lambda t: t[1])[0]
    rest = [(c, w) for c, w in chroma if _hue_gap(c, brand) >= 35]
    accent = max(rest, key=lambda t: t[1])[0] if rest else None
    return {"brand": brand, "accent": accent, "ink": ink, "mono": False}


def plate_needed(cols, bg):
    """True when the logo's main non-white color is under 3:1 (WCAG non-text) on bg AND a white plate fixes that
    (a light logo color on a light page: a white plate would not help - the logo's own dark ink carries it)"""
    vis = [(c, w) for c, w in cols if _lum(c) < 0.85]
    if not vis or not HEX.match(bg or ""):
        return False
    main = max(vis, key=lambda t: t[1])[0]
    return contrast(main, bg) < 3.0 and contrast(main, "#FFFFFF") >= 3.0


# ---------------------------------------------------------------- 3. the fragment for a measure
def _sanitize_svg(txt):
    txt = re.sub(r"<\?xml.*?\?>|<!--.*?-->|<!DOCTYPE.*?>", "", txt, flags=re.S)
    if re.search(r"<script|<foreignObject|\son\w+\s*=|(?:xlink:)?href\s*=\s*['\"](?!#)", txt, re.I):
        raise SystemExit("logo SVG has a script, foreignObject, an event handler or an external reference - "
                         "export a clean SVG (the Secure edition strips them, and the whole element can go with them)")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt.replace('"', "'")   # attributes in single quotes: the fragment sits in a DAX "..." string


def fragment(path, height, max_width=None, alt="logo", align="center", on=None):
    """the logo as HTML for a measure; see the module doc"""
    mw = f"max-width:{max_width}px;" if max_width else ""
    st = f"height:{height}px;width:auto;{mw}display:block;flex:none"
    alt = alt.replace("'", "&#39;").replace('"', "&quot;")
    if path.lower().endswith(".svg"):
        svg = _sanitize_svg(open(path, encoding="utf-8").read())
        svg = re.sub(r"(<svg\b[^>]*?)\s(?:width|height)='[^']*'", r"\1", svg, count=1)
        svg = re.sub(r"(<svg\b[^>]*?)\s(?:width|height)='[^']*'", r"\1", svg, count=1)
        if "viewBox" not in svg.split(">", 1)[0]:
            raise SystemExit("logo SVG needs a viewBox to scale")
        frag = svg.replace("<svg", f"<svg role='img' aria-label='{alt}' style='{st}'", 1)
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
    if on and plate_needed(extract(path), on):   # never recolor a logo: give it a light plate instead
        frag = f"<div style='flex:none;background:#FFFFFF;border-radius:8px;padding:6px 10px'>{frag}</div>"
    frag = f"<div style='flex:none;align-self:{align};display:flex'>{frag}</div>"
    if len(frag) > MAX_BYTES:
        raise SystemExit(f"logo fragment is {len(frag)} bytes > {MAX_BYTES}: simplify the SVG or use a smaller PNG "
                         "(every card that shows the logo carries it)")
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


def report_theme_colors(report_dir):
    """an existing report's custom-theme dataColors ([] when it has none) - the colors the report already uses"""
    rj = json.load(open(os.path.join(report_dir, "definition", "report.json"), encoding="utf-8"))
    custom = (rj.get("themeCollection") or {}).get("customTheme")
    if not custom:
        return []
    f = os.path.join(report_dir, "StaticResources", "RegisteredResources", custom["name"])
    if not os.path.exists(f):
        return []
    return [_norm(c) for c in json.load(open(f, encoding="utf-8")).get("dataColors", []) if HEX.match(c)]


# ---------------------------------------------------------------- check
def main(argv):
    if len(argv) < 2 or argv[0] != "check":
        print(__doc__.split("\n\n")[0])
        return 2
    p = argv[1]
    on = argv[argv.index("--on") + 1] if "--on" in argv else "#FFFFFF"
    cols = extract(p)
    if not cols:
        print("LOGO FAIL no colors found (SVG fills as hex literals, or an opaque PNG)")
        return 1
    ba = brand_accent(cols)
    print("dominant:", ", ".join(f"{c} {w:.0%}" for c, w in cols[:6]))
    print(f"brand {ba['brand']}  accent {ba['accent']}  {'(one-color logo: accent from the preset)' if ba['mono'] else ''}")
    for h in (40, 48):
        print(f"fragment at {h}px: {len(fragment(p, h, on=on))} bytes")
    print(f"on {on}: {'plate (main color under 3:1)' if plate_needed(cols, on) else 'no plate needed'}")
    sys.path.insert(0, HERE)
    import palette  # noqa: F401  (loads styles)
    import styles as S
    import style_check
    fails = [f"{mode}/{mech}: {e}" for mode in ("light", "dark") for mech in S.MECHANISMS
             if (e := style_check.check(S.make_style(ba["brand"], accent=ba["accent"], mode=mode, mechanism=mech)))]
    print("LOGO OK" if not fails else "LOGO FAIL " + "; ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
