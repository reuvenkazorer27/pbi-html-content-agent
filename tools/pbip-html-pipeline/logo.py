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
1. extract(path)       dominant colors of the logo with weights. SVG (parsed as XML): every painted shape (rect,
                       circle, ellipse, path, polygon, polyline, line, text) with its paint after the cascade -
                       presentation attribute < <style> rule (tag / .class / #id, matched on the selector's last
                       compound) < inline style, inherited from <g>; gradients by their stops, following href chains;
                       its stroke when it has no fill; shapes in defs / clipPath / mask skipped; weighted by rough
                       area. Hex, rgb() and basic named colors. PNG/JPG (needs Pillow): opaque pixels. Colors are
                       grouped in 20deg hue bins (anti-aliasing shades merge; the bin's most frequent exact color
                       represents it); white / black / grays are the logo's ink, kept apart.
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
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)   # python -I drops the script folder from sys.path


# one WCAG implementation for the whole kit - imported when first used, not at import time: palette imports styles,
# whose "style": {"logo": true} imports this module, so a top-level import here would be circular (a measures.py
# that imports logo first crashed with "module 'logo' has no attribute 'colors'")
_F = {}


def _fn(mod, name):
    """the kit's own color function, imported once on first use"""
    if name not in _F:
        _F[name] = getattr(__import__(mod), name)
    return _F[name]


def _lum(c):
    return _fn("palette", "_lum")(c)


def contrast(a, b):
    return _fn("palette", "contrast")(a, b)


def _hls(c):
    return _fn("styles", "_hls")(c)


MAX_BYTES = 12_000
SIGNIFICANT = 0.05   # a color covering at least 5% of the logo counts for the plate decision (a wordmark does)
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
NAMED = {"black": "#000000", "white": "#FFFFFF", "red": "#FF0000", "green": "#008000", "blue": "#0000FF",
         "yellow": "#FFFF00", "orange": "#FFA500", "purple": "#800080", "gray": "#808080", "grey": "#808080",
         "navy": "#000080", "teal": "#008080", "maroon": "#800000"}
PAINT = ("fill", "stroke", "font-size")   # the cascaded properties that weigh a color (font-size: a wordmark's area)
SHAPES = ("rect", "circle", "ellipse", "path", "polygon", "polyline", "line", "text")
HIDDEN = ("defs", "clipPath", "mask", "symbol", "pattern", "marker", "style", "title", "desc", "metadata")
XLINK = "{http://www.w3.org/1999/xlink}href"


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
    v = (value or "").replace("!important", "").strip()
    m = re.match(r"url\(\s*['\"]?#([\w.-]+)", v)
    if m:
        return grads.get(m.group(1), [])
    if HEX.match(v):
        return [_norm(HEX.match(v).group())]
    m = re.match(r"rgba?\(\s*(\d+)\D+(\d+)\D+(\d+)", v)
    if m:
        return ["#%02X%02X%02X" % tuple(min(255, int(x)) for x in m.groups())]
    return [NAMED[v.lower()]] if v.lower() in NAMED else []


_SIZES = {"xx-small": 9, "x-small": 10, "small": 13, "medium": 16, "large": 18, "x-large": 24, "xx-large": 32}


def _px(value, parent):
    """a CSS font-size -> px: px / unitless (user units) / pt / em / rem / % / keywords; anything else = the parent's"""
    v = str(value).replace("!important", "").strip().lower()
    if v in _SIZES:
        return float(_SIZES[v])
    if v in ("smaller", "larger"):
        return parent / 1.2 if v == "smaller" else parent * 1.2
    m = re.fullmatch(r"(\d+(?:\.\d*)?|\.\d+)\s*(px|pt|em|rem|%)?", v)   # '1.2.3' -> no match -> parent
    if not m:
        return parent   # 'inherit', calc(), var(): keep the inherited size
    n, unit = float(m.group(1)), m.group(2) or "px"
    return {"px": n, "pt": n * 4 / 3, "em": n * parent, "rem": n * 16.0, "%": n / 100 * parent}[unit]


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _css_rules(root):
    """[(compound selector, {fill / stroke / font-size})] in source order. A selector is matched on its last compound
    (tag, .class, #id, combined): `svg path`, `g .cls-1`, `path.cls-1`, `#a`, `*` - an approximation that covers
    logo exports; specificity is not modeled, the later rule wins."""
    css = " ".join(el.text or "" for el in root.iter() if _local(el.tag) == "style")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    for sel, body in re.findall(r"([^{}@]+)\{([^{}]*)\}", css):
        props = {k.strip().lower(): v.strip() for k, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", body)
                 if k.strip().lower() in PAINT}
        for s in sel.split(","):
            last = re.split(r"[\s>+~]+", s.strip())[-1]
            if props and re.fullmatch(r"[a-zA-Z*]*(?:[.#][\w-]+)*", last or "-"):
                rules.append((last, props))
    return rules


def _css_for(el, rules):
    tag, classes, eid, out = _local(el.tag), set(el.get("class", "").split()), el.get("id"), {}
    for sel, props in rules:
        t = re.match(r"[a-zA-Z*]*", sel).group()
        if t not in ("", "*", tag):
            continue
        if all((n in classes) if k == "." else (n == eid) for k, n in re.findall(r"([.#])([\w-]+)", sel)):
            out.update(props)
    return out


def _gradients(root):
    """gradient id -> stop colors, following href chains (Illustrator: a stops gradient + gradients that reuse it)"""
    raw = {}
    for el in root.iter():
        if _local(el.tag) in ("linearGradient", "radialGradient") and el.get("id"):
            stops = []
            for st in el:
                if _local(st.tag) == "stop":
                    m = re.search(r"stop-color\s*:\s*([^;]+)", st.get("style", ""))
                    stops += _paints(m.group(1) if m else st.get("stop-color"), {})
            ref = (el.get("href") or el.get(XLINK) or "").lstrip("#")
            raw[el.get("id")] = (stops, ref)

    def resolve(gid, seen=()):
        stops, ref = raw.get(gid, ([], ""))
        if stops or not ref or ref in seen:
            return stops
        return resolve(ref, seen + (gid,))
    return {gid: resolve(gid) for gid in raw}


def _svg_pairs(txt):
    try:
        root = ET.fromstring(txt)
    except ET.ParseError as e:
        raise SystemExit(f"logo SVG is not well-formed XML ({e}) - export it again")
    rules, grads, pairs = _css_rules(root), _gradients(root), []
    ids = {el.get("id"): el for el in root.iter() if el.get("id")}

    def cascade(el, inherited):
        paint = dict(inherited)
        for k in PAINT:                       # presentation attribute < CSS rule < inline style
            if el.get(k) is not None:
                paint[k] = el.get(k)
        paint.update(_css_for(el, rules))
        paint.update({k: v.strip() for k, v in re.findall(r"(fill|stroke|font-size)\s*:\s*([^;]+)", el.get("style", ""))})
        for k in ("fill", "stroke"):
            if (paint.get(k) or "").strip() == "inherit":
                paint[k] = inherited.get(k)
        if isinstance(paint.get("font-size"), str):   # set on this element: to px against the inherited size
            paint["font-size"] = _px(paint["font-size"], inherited.get("font-size") or 16.0)
        return paint

    def add(paint, area, line=False):
        fills = [] if line else _paints(paint.get("fill"), grads)
        cols, w = (fills, area) if fills else (_paints(paint.get("stroke"), grads), area * 0.2)   # line art
        for c in cols:
            pairs.append((c, w / len(cols)))

    def walk(el, inherited, depth=0):
        tag = _local(el.tag)
        if tag in HIDDEN or depth > 20:   # shapes in defs / clipPath / mask are not painted as such
            return
        paint = cascade(el, inherited)
        if tag == "use":   # <use href='#m'> paints a symbol / element defined elsewhere (sprite-style exports)
            target = ids.get((el.get("href") or el.get(XLINK) or "").lstrip("#"))
            if target is None:
                return
            if _local(target.tag) == "symbol":   # a symbol is HIDDEN where it is defined: paint its children here
                for ch in target:
                    walk(ch, cascade(target, paint), depth + 1)
            else:                                # a <g> or a shape keeps its own paint (cascaded over the <use>'s)
                walk(target, paint, depth + 1)
            return
        if tag == "text":   # a wordmark: weighted by its font size, split over its runs by their share of letters
            runs = []

            def collect(node, p):   # the node's own text, its <tspan>/<a> children (nested), and each child's tail
                runs.append(((node.text or "").strip(), p))
                for ch in node:
                    if _local(ch.tag) in ("tspan", "a", "textPath"):
                        collect(ch, cascade(ch, p))
                    runs.append(((ch.tail or "").strip(), p))   # text after </tspan> is painted like its parent
            collect(el, paint)
            letters = sum(len(t) for t, _ in runs)
            for t, p in runs:   # each run by its own size: 1.2 * size^2 for the whole word, shared by letters
                if t:
                    add(p, 1.2 * (p.get("font-size") or 16.0) ** 2 * len(t) / letters)
            if not letters:
                add(paint, 1.2 * (paint.get("font-size") or 16.0) ** 2)
            return
        if tag in SHAPES:
            add(paint, _area(tag, el.attrib), line=tag == "line")
        for ch in el:
            walk(ch, paint, depth)

    walk(root, {"fill": "#000000", "stroke": None, "font-size": None})   # SVG default fill is black
    return pairs


def extract(path):
    """[(hex, share)] largest first; [] when no color could be read"""
    if path.lower().endswith(".svg"):
        return _bin(_svg_pairs(open(path, encoding="utf-8-sig").read()))   # -sig: a BOM is not part of the SVG
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
                 r"|url\(\s*['\"]?\s*[^\s'\"#)]|@import", txt, re.I):
        raise SystemExit("logo SVG has a script, foreignObject, an event handler, or an href / url() / @import that "
                         "points outside the SVG (another file, a web address or an embedded data: image) - export a "
                         "clean vector SVG, or give the logo as a PNG (the Secure edition strips such parts, and the "
                         "whole element can go with them)")
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
        svg = _sanitize_svg(open(path, encoding="utf-8-sig").read())
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
def selftest():
    """the cases the code reviews found (12 Nov 2026), no model or Desktop needed: python -I logo.py selftest"""
    import tempfile
    with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as tmp:   # nothing left in %TEMP%
        return _selftest(d, tmp)


def _selftest(d, tmp):
    import subprocess
    fails = []

    def svg(name, body, vb="0 0 200 60", head=""):
        p = os.path.join(d, name + ".svg")
        open(p, "w", encoding="utf-8").write(head + "<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/"
                                             f"xlink' viewBox='{vb}'>{body}</svg>")
        return p

    def expect(label, cond):
        print(("ok   " if cond else "FAIL ") + label)
        if not cond:
            fails.append(label)

    def rejects(body):
        try:
            fragment(svg("r", body, "0 0 9 9"), 40)
            return False
        except SystemExit:
            return True

    tw = svg("tw", "<rect width='56' height='56' fill='#0B5D6B'/><circle cx='34' cy='20' r='9' fill='#F28C38'/>"
                   "<text x='68' y='37' font-size='26' fill='#12343B'>Tidewell</text>")
    cases = [
        ("attributes", tw, "#0B5D6B", "#F28C38"),
        ("class rules", svg("c", "<style>.a{fill:#0B5D6B}.b{fill:#F28C38}</style><rect class='a' width='56' height='56'/>"
                                 "<circle class='b' cx='30' cy='20' r='9'/>"), "#0B5D6B", "#F28C38"),
        ("element / descendant / id rules", svg("e", "<style>svg path{fill:#0B5D6B} g .b{fill:#F28C38}</style>"
                                                     "<path d='M0 0 L100 0 L100 60 Z'/><g><circle class='b' cx='150' cy='30' r='12'/></g>"),
         "#0B5D6B", "#F28C38"),
        ("CSS rule beats fill attribute", svg("p", "<style>.t{fill:#0B5D6B}</style><rect class='t' fill='#000' width='99' height='60'/>"),
         "#0B5D6B", None),
        ("href-chained gradient", svg("g", "<defs><linearGradient id='b'><stop offset='0' stop-color='#1D4ED8'/></linearGradient>"
                                           "<linearGradient id='a' xlink:href='#b'/></defs><rect width='99' height='60' fill='url(#a)'/>"
                                           "<circle cx='150' cy='30' r='12' fill='rgb(234,88,12)'/>"), "#1D4ED8", "#EA580C"),
        ("stroke-only line art", svg("s", "<path d='M10 10 L190 50' fill='none' stroke='#9333EA'/>"), "#9333EA", None),
        ("<use> of a <symbol>", svg("u", "<symbol id='m'><rect width='60' height='60' fill='#0B5D6B'/></symbol><use href='#m'/>"),
         "#0B5D6B", None),
        ("<use> of a painted <g>", svg("ug", "<defs><g id='k' fill='#DC2626'><rect width='60' height='60'/></g></defs>"
                                            "<use xlink:href='#k'/>"), "#DC2626", None),
        ("two-color <tspan> wordmark", svg("t", "<rect width='20' height='20' fill='#0B5D6B'/><text font-size='40'><tspan fill='#0B5D6B'>Tide"
                                                "</tspan><tspan fill='#F28C38'>well</tspan></text>"), "#0B5D6B", "#F28C38"),
        ("text after </tspan> keeps the parent's color", svg("tail", "<text font-size='40' fill='#12343B'><tspan fill='#F28C38'>T"
                                                              "</tspan>idewell Group</text>"), "#12343B", None),
        ("nested <tspan> colors", svg("nest", "<rect width='9' height='9' fill='#0B5D6B'/><text font-size='40'><tspan fill='#0B5D6B'>Tide"
                                            "<tspan fill='#F28C38'>well</tspan></tspan></text>"), "#0B5D6B", "#F28C38"),
        ("BOM + XML declaration", svg("bom", "<rect width='9' height='9' fill='#0B5D6B'/>", "0 0 9 9",
                                      "\ufeff<?xml version='1.0' encoding='UTF-8'?>"), "#0B5D6B", None),
    ]
    for label, p, brand, accent in cases:
        try:
            ba = colors(p)
            expect(f"{label}: {ba['brand']} / {ba['accent']}", ba["brand"] == brand and (accent is None or ba["accent"] == accent))
        except SystemExit as e:
            expect(f"{label}: {e}", False)
    try:
        colors(svg("none", "<rect width='9' height='9' fill='none'/>"))
        expect("no colors is an error", False)
    except SystemExit:
        expect("no colors is an error", True)
    expect("quoted local url('#g') accepted", not rejects("<rect width='9' height='9' style=\"fill:url('#g')\"/>"))
    expect("external url() rejected", rejects("<rect width='9' height='9' style='fill:url(\"https://x.org/a#g\")'/>"))
    expect("@import rejected", rejects("<style>@import url(https://x.org/a.css);</style><rect width='9' height='9'/>"))
    expect("event handler rejected", rejects("<rect width='9' height='9' onclick='x()'/>"))
    expect("plate for a dark wordmark on navy", plate_needed([("#F97316", .6), ("#000000", .3)], "#0D2140"))
    expect("no useless plate on white", not plate_needed([("#FACC15", .7), ("#1F2937", .3)], "#FFFFFF"))
    frag = fragment(svg("fs", "<rect width='9' height='9' fill='#000'/><text style='font-size:22px'>A</text>"), 40)
    expect("font-size survives FONT_SCALE", "font-size:22.0px" in frag)
    expect("a logo never mirrors", "direction:ltr" in fragment(tw, 40))
    expect("no BOM in the fragment", "\ufeff" not in fragment(os.path.join(d, "bom.svg"), 40))
    # `import logo` before palette, with "style": {"logo": true}: was a circular-import crash
    for f in os.listdir(HERE):
        if f.endswith(".py"):
            open(os.path.join(tmp, f), "w", encoding="utf-8").write(open(os.path.join(HERE, f), encoding="utf-8").read())
    json.dump({"project": "x", "table": "T", "page_id": "p", "backup_dir": "_b", "logo": {"path": tw},
               "style": {"logo": True, "preset": "mint"}}, open(os.path.join(tmp, "pipeline.json"), "w"))
    env = {k: v for k, v in os.environ.items() if k not in ("DASH_STYLE", "DASH_PALETTE")}
    r = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {tmp!r}); import logo, palette; "
                        "print(palette.P['primary'])"], capture_output=True, text=True, env=env, cwd=tmp)
    expect("`import logo` first with a logo style", r.returncode == 0 and "#0B5D6B" in r.stdout.upper())
    if r.returncode or "#0B5D6B" not in r.stdout.upper():
        print("     " + (r.stdout + r.stderr).strip()[-1500:].replace("\n", "\n     "))
    import bridge
    expect("bridge: report title vs opening title",
           bridge.is_report_title("sales-demo") and not bridge.is_report_title("Untitled - Power BI Desktop")
           and not bridge.is_report_title("ללא שם - Power BI Desktop"))
    expect("bridge: '<project> - Power BI Desktop' is the project's report",
           bridge.is_report_title("sales-demo - Power BI Desktop", "sales-demo")
           and not bridge.is_report_title("Untitled - Power BI Desktop", "sales-demo"))
    # a wordmark sized by CSS weighs by that size: the 48px dark word outweighs the small mark
    big = svg("fsz", "<style>.w{font-size:48px;fill:#12343B}</style><rect width='30' height='30' fill='#F28C38'/>"
                     "<text class='w'>Tidewell</text>")
    cols = extract(big)
    expect("CSS font-size weighs the wordmark", cols[0][0] == "#12343B")
    rel = extract(svg("rel", "<rect width='40' height='40' fill='#F28C38'/><g font-size='20'>"
                             "<text font-size='50%' fill='#12343B'>Tidewell</text></g>"))
    expect("relative font-size (50% of 20px = 10px) is not read as 50px", rel[0][0] == "#F28C38")
    per = colors(svg("per", "<text font-size='14'><tspan font-size='48' fill='#0B5D6B'>TIDE</tspan>"
                            "<tspan fill='#F28C38'>well</tspan></text>"))
    expect("a <tspan>'s own font-size weighs its run", per["brand"] == "#0B5D6B")
    expect("bridge: another report that starts with the project's name is not this project's",
           not bridge.is_report_title("sales-archive - Power BI Desktop", "sales"))
    print("SELFTEST OK" if not fails else f"SELFTEST FAIL ({len(fails)})")
    return 0 if not fails else 1


def main(argv):
    if argv[:1] == ["selftest"]:
        return selftest()
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
