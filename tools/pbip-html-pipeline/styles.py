# -*- coding: utf-8 -*-
"""Colorful dashboard styles: one card material for every card, one color mechanism, contrast computed.

A style is generated from a few design inputs, so an agent can fit it to the user's brand, data and
context. It is not a fixed theme. The rules behind it are in reference/design-system.md §4:
  - KPI cards and analysis cards are ONE material (surface, border, radius, title, icon chip)
  - color reaches every card through ONE mechanism: an accent bar, a tint, or the icon chip
  - saturation stays on small areas (data marks, icons, the bar) plus at most one hero card
  - every in-card text / mark color is computed for contrast on the card it sits on (4.5:1 / 3:1)

Use
  1. Pick or build a style:
       style = make_style(brand="#0E7490", mode="light", mechanism="bar")   # from the user's brand
       style = PRESETS["accent"]                                            # or a ready preset
     The project default goes in pipeline.json, e.g. "style": "accent", or
     "style": {"brand": "#0E7490", "accent": "#F59E0B", "mode": "dark", "mechanism": "tint", "hero": false}.
     Override per build with DASH_STYLE=<preset> or DASH_STYLE=none (legacy palettes).
  2. Give each card a ROLE: "neutral" (header, filter panel), "hero" (the one headline KPI),
     "brand", the semantic roles "good" / "bad" / "warn", or "c1".."c6" (categories). The role picks the
     card's hue, so a KPI about a category, and the chart about that same category, share one color.
  3. In your measures' add(): expr = apply(expr, role). Build card roots with CARD and use the
     tokens @@c_chip@@ / @@c_icon@@ / @@c_icon_in@@ for icon chips.
Roles map to data tokens too: c1..c3 -> primary / design / maint, good -> done, bad -> bad,
c4 -> series3, warn -> series4 and warn, c1..c6 -> cat1..cat6, so data and cards share one set of colors.
"""
import colorsys
import json
import os

from palette import PALETTES, _mix, _lum, contrast

ROLES = ("neutral", "brand", "hero", "good", "bad", "warn", "c1", "c2", "c3", "c4", "c5", "c6")
MECHANISMS = ("bar", "start-bar", "tint", "tint-strong", "chip")
MARK, TEXT = 3.0, 4.5   # WCAG 1.4.11 non-text / 1.4.3 text


# ---------------------------------------------------------------- color helpers
def _hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return "#" + "".join(f"{round(v * 255):02X}" for v in (r, g, b))


def _hls(c):
    c = c.lstrip("#")
    h, l, s = colorsys.rgb_to_hls(*(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)))
    return h * 360, l, s


def readable(color, bgs, target, toward):
    """the closest mix of color toward black/white that reads at `target` on EVERY background"""
    if min(contrast(color, b) for b in bgs) >= target:
        return color
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if min(contrast(_mix(color, toward, mid), b) for b in bgs) >= target:
            hi = mid
        else:
            lo = mid
    out = _mix(color, toward, hi)
    assert min(contrast(out, b) for b in bgs) >= target, ("no readable color", color, bgs, target)
    return out


def _best(color, bgs, targets, toward):
    """as high a target as the backgrounds allow (e.g. 10 -> 7 -> 4.5), never below the last"""
    for t in targets:
        try:
            return readable(color, bgs, t, toward)
        except AssertionError:
            continue
    raise AssertionError(("no readable color", color, bgs, targets[-1]))


def tone(hue, card):
    """the role scale of `hue` on a light or dark card (Radix-like steps, contrast-checked):
    s2 card tint, s3 tint, s5 chip/track, s6 border, s9 solid marks, s11 secondary text, s12 text"""
    dark = _lum(card) < 0.2
    to = "#FFFFFF" if dark else "#000000"
    if dark:
        s2, s3, s5, s6 = card, _mix(hue, card, .84), _mix(hue, card, .74), _mix(hue, card, .62)
    else:
        s2, s3, s5, s6 = (_mix(hue, "#FFFFFF", t) for t in (.955, .90, .82, .62))
    return {"s2": s2, "s3": s3, "s5": s5, "s6": s6,
            "s9": readable(hue, [s2, s3, s5], MARK, to),
            "s11": readable(_mix(hue, to, .30), [s2, s3, s5], TEXT, to),
            "s12": _best(_mix(hue, to, .72), [s2, s3, s5], (10.0, 7.0, TEXT), to)}


# ---------------------------------------------------------------- building a style from design inputs
def make_style(brand, accent=None, mode="light", mechanism="bar", bar=4, hero=True, page=None, card=None,
               border=None, radius=12, shadow=None, colors=None):
    """A complete style from a brand color (and optionally a second color).

    mode       "light" | "dark"
    mechanism  how color reaches every card: "bar" (top accent bar), "start-bar" (bar on the reading-start
               side), "tint" (card tinted in its role hue), "tint-strong" (deeper tint, borderless), "chip"
               (neutral card, color only in the icon chip and the data)
    hero       True: the card with role "hero" is a solid brand fill with white text (use it once)
    colors     optional overrides for any role: {"c1": "#..", "bad": "#..", ...}
    Everything not given is derived: the categorical set rotates around the brand hue, the semantic
    colors are the usual green / red / amber, neutral is a gray leaning toward the brand."""
    assert mode in ("light", "dark") and mechanism in MECHANISMS
    dark = mode == "dark"
    h, l, s = _hls(brand)
    acc_h = _hls(accent)[0] if accent else h + 150
    sat, lig = (min(max(s, .55), .85), .62) if dark else (min(max(s, .55), .80), .42)
    cats = [brand if not dark else _hsl(h, sat, lig), _hsl(acc_h, sat, lig), _hsl(h + 60, sat, lig),
            _hsl(acc_h + 60, sat, lig), _hsl(h - 60, sat, lig), _hsl(acc_h - 60, sat, lig)]
    base = {"neutral": _hsl(h, .14, .62 if dark else .44), "brand": brand,
            "good": "#4ADE80" if dark else "#15803D", "bad": "#F87171" if dark else "#C81E1E",
            "warn": "#FBBF24" if dark else "#B45309"}
    base.update({f"c{i + 1}": c for i, c in enumerate(cats)})
    base.update(colors or {})
    tinted = mechanism in ("tint", "tint-strong")
    return {
        "mode": mode, "mechanism": mechanism, "bar": 0 if mechanism in ("chip",) or tinted else bar,
        "hero": hero, "radius": radius,
        "page": page or (_mix(brand, "#0B0D12", .93) if dark else _mix(brand, "#F3F4F6", .94)),
        "card": None if tinted else (card or (_mix(brand, "#16181D", .92) if dark else "#FFFFFF")),
        # tinted cards are computed from this base: dark mode tints dark surfaces (not light pastels on a dark page)
        "tint_base": (card or _mix(brand, "#16181D", .92)) if (tinted and dark) else None,
        "border": border or (_mix(brand, "#2A2E35", .85) if dark else _mix(brand, "#E5E7EB", .88)),
        "shadow": shadow or ("none" if dark else "0 1px 2px rgba(16,24,40,.06)"),
        "colors": base,
    }


def _preset(colors, **kw):
    """a preset keeps its make_style() inputs, so pipeline.json can say {"preset": "accent", "hero": false}"""
    args = dict(brand=colors["brand"], colors=colors, **kw)
    st = make_style(**args)
    st["inputs"] = args
    return st


_LIGHT = {"neutral": "#64748B", "brand": "#4F46E5", "c1": "#1D4ED8", "c2": "#7C3AED", "c3": "#0F766E",
          "c4": "#DB2777", "c5": "#0891B2", "c6": "#65A30D", "good": "#15803D", "bad": "#C81E1E", "warn": "#B45309"}
PRESETS = {   # worked examples of the inputs above - not the limit of what make_style() can produce
    "accent":   _preset(_LIGHT, mechanism="bar", bar=4, hero=True, page="#F3F4F6", border="#E5E7EB"),
    "tonal":    _preset(_LIGHT, mechanism="tint", hero=False, page="#F6F7F9"),
    "midnight": _preset({"neutral": "#94A3B8", "brand": "#818CF8", "c1": "#60A5FA", "c2": "#A78BFA",
                         "c3": "#2DD4BF", "c4": "#F472B6", "c5": "#22D3EE", "c6": "#A3E635", "good": "#4ADE80",
                         "bad": "#F87171", "warn": "#FBBF24"},
                        mode="dark", bar=3, hero=False, page="#0E1015", card="#16181D", border="#2A2E35"),
    "sand":     _preset({"neutral": "#7A6F62", "brand": "#B4532A", "c1": "#2F5D8A", "c2": "#7A4E8C",
                         "c3": "#4E7D5B", "c4": "#B4532A", "c5": "#5B7A8C", "c6": "#8A7A3C", "good": "#3F6B3A",
                         "bad": "#B42318", "warn": "#B7791F"},
                        bar=3, radius=10, hero=True, page="#EFE9DF", card="#FBF8F3", border="#E2D8C8", shadow="none"),
    "ocean":    _preset({"neutral": "#7DA3C9", "brand": "#22D3EE", "c1": "#38BDF8", "c2": "#A78BFA",
                         "c3": "#2DD4BF", "c4": "#F472B6", "c5": "#818CF8", "c6": "#A3E635", "good": "#34D399",
                         "bad": "#FB7185", "warn": "#FBBF24"},
                        mode="dark", bar=3, radius=14, hero=False, page="#071426", card="#0D2140", border="#1C365C"),
    "duotone":  _preset({"neutral": "#4F46E5", "brand": "#4338CA", "c1": "#4F46E5", "c2": "#8B5CF6",
                         "c3": "#312E81", "c4": "#A5B4FC", "c5": "#6366F1", "c6": "#C7D2FE", "good": "#818CF8",
                         "bad": "#D97706", "warn": "#D97706"},
                        mechanism="chip", hero=True, page="#F4F5FB", border="#E1E4F2"),
    "sunset":   _preset({"neutral": "#9A6B55", "brand": "#E11D48", "c1": "#EA580C", "c2": "#9333EA",
                         "c3": "#0F766E", "c4": "#E11D48", "c5": "#D97706", "c6": "#BE185D", "good": "#15803D",
                         "bad": "#DC2626", "warn": "#D97706"},
                        mechanism="start-bar", bar=6, hero=False, page="#FFF4EC", border="#F5DCCB"),
    "mint":     _preset({"neutral": "#4B7F6F", "brand": "#059669", "c1": "#0369A1", "c2": "#6D28D9",
                         "c3": "#0F766E", "c4": "#0891B2", "c5": "#65A30D", "c6": "#0D9488", "good": "#15803D",
                         "bad": "#B91C1C", "warn": "#65A30D"},
                        mechanism="tint-strong", radius=18, hero=False, page="#F2F7F5"),
}
DEFAULT = "accent"


# ---------------------------------------------------------------- the palette a style implies
DATA_TOKENS = {"primary": "c1", "design": "c2", "maint": "c3", "done": "good", "bad": "bad",
               "series3": "c4", "series4": "warn", "warn": "warn"}


def style_palette(st):
    """a full token palette for style `st`: page, neutral in-card tokens from the card color, data colors
    pushed to 3:1 (marks) / 4.5:1 (text) on the card, soft pills with text-safe text"""
    card = st["card"] or st.get("tint_base") or "#FFFFFF"
    dark = _lum(card) < 0.2
    away = "#FFFFFF" if dark else "#000000"
    p = dict(PALETTES["midnight" if dark else "ocean"])
    p.update(kpi_filled="0", bg_layer="0", page_bg=st["page"], outspace_bg=st["page"], bg_from=st["page"],
             bg_mid=st["page"], bg_to=st["page"], surface=card, inset=_mix(card, away, .05),
             track=_mix(card, away, .09), divider=_mix(card, away, .08), divider2=_mix(card, away, .07),
             grid=_mix(card, away, .09), neutral_soft=_mix(card, away, .07), border=st["border"],
             connector=_mix(card, away, .22), slicer_bg=card, slicer_border=_mix(card, away, .25),
             shadow="rgba(0,0,0,.35)" if dark else "rgba(16,24,40,.06)")
    p["fg"] = _best("#F1F5F9" if dark else "#111827", [card, p["inset"]], (7.0, TEXT), away)
    p["fg2"] = readable("#B0B8C4" if dark else "#4B5563", [card, p["inset"]], TEXT, away)
    p["fg3"] = readable("#CBD5E1" if dark else "#374151", [card, p["inset"]], TEXT, away)
    p["muted"] = readable("#7A8794" if dark else "#8A8886", [card], MARK, away)
    p["arrow"] = readable(p["arrow"], [card], MARK, away)
    p["slicer_fg"] = p["fg"]
    c = st["colors"]
    for tok, role in DATA_TOKENS.items():   # marks 3:1 on the track; builders also use them as text: 4.5:1 on the card
        p[tok] = readable(readable(c[role], [card, p["track"]], MARK, away), [card, p["inset"]], TEXT, away)
    for k, soft, txt in (("primary", "primary_soft", "primary_text"), ("design", "design_soft", "design_text"),
                         ("maint", "maint_soft", "maint_text"), ("done", "done_soft", "done_text"),
                         ("warn", "warn_soft", "warn_text"), ("bad", "bad_soft", None)):
        p[soft] = _mix(p[k], card, .80)
        if txt:
            p[txt] = readable(p[k], [p[soft]], TEXT, "#FFFFFF" if _lum(p[soft]) < 0.2 else "#000000")
    p["active_text"] = p["primary_text"]
    p["strong"] = readable(c["brand"], ["#FFFFFF"], TEXT, "#000000")
    for i in range(1, 7):                   # categorical colors = the style's c1..c6
        col = readable(c[f"c{i}"], [card], MARK, away)
        soft = _mix(col, card, .80)
        p[f"cat{i}"], p[f"cat{i}_soft"] = col, soft
        p[f"cat{i}_text"] = readable(col, [soft], TEXT, "#FFFFFF" if _lum(soft) < 0.2 else "#000000")
    return p


# ---------------------------------------------------------------- per-card tokens
def card_css(st):
    """root style of every card in this style (KPI and analysis alike); per-card values are @@c_*@@ tokens"""
    side = "border-inline-start" if st["mechanism"] == "start-bar" else "border-top"
    return ("box-sizing:border-box;height:100vh;overflow:hidden;background:@@c_bg@@;"
            f"border:1px solid @@c_border@@;{side}:@@c_barw@@ solid @@c_bar@@;"
            f"border-radius:{st['radius']}px;box-shadow:@@c_shadow@@;line-height:1.35;"
            "direction:@@dir@@;text-align:@@start@@;font-family:Segoe UI,Arial,sans-serif;color:@@fg@@")


def card_tokens(st, role):
    """token values for one card of `role` (applied before the palette resolves the rest)"""
    assert role in ROLES, f"unknown role {role!r} - use one of {ROLES}"
    hero = role == "hero" and st["hero"]
    hue = st["colors"]["brand" if role == "hero" else role]
    t = tone(hue, st["card"] or st.get("tint_base") or "#FFFFFF")
    out = {"c_barw": f"{st['bar'] or 1}px", "c_shadow": st["shadow"], "c_chip": t["s3"], "c_icon": t["s9"],
           "c_icon_in": "@@on_accent@@"}
    if hero:                 # the one solid card: brand fill, white text, same shape
        solid = readable(hue, ["#FFFFFF"], TEXT, "#000000")
        soft_w = readable(_mix("#FFFFFF", solid, .18), [solid], TEXT, "#FFFFFF")
        out.update({"c_bg": solid, "c_border": solid, "c_bar": solid, "fg": "#FFFFFF", "fg2": soft_w,
                    "fg3": soft_w, "c_chip": "rgba(255,255,255,.20)", "c_icon": "#FFFFFF", "c_icon_in": solid,
                    "track": "rgba(255,255,255,.30)"})
    elif st["mechanism"] in ("tint", "tint-strong"):   # tinted card; text in the card's own hue, not gray
        strong = st["mechanism"] == "tint-strong"
        bg, edge = (t["s5"], t["s5"]) if strong else (t["s3"], t["s6"])
        out.update({"c_bg": bg, "c_border": edge, "c_bar": edge, "fg": t["s12"], "fg2": t["s11"],
                    "fg3": t["s11"], "c_chip": t["s2"] if strong else t["s5"],
                    "track": t["s2"] if strong else t["s5"], "divider": t["s6"] if strong else t["s5"],
                    "divider2": t["s6"] if strong else t["s5"], "inset": t["s3"] if strong else t["s2"],
                    "grid": t["s6"] if strong else t["s5"], "neutral_soft": t["s3"] if strong else t["s5"],
                    "border": t["s6"]})
        to = "#FFFFFF" if _lum(bg) < 0.2 else "#000000"   # data on a tint: re-check against THIS card
        for tok, r in DATA_TOKENS.items():                # marks 3:1 on the track, and 4.5:1 as text
            out[tok] = readable(readable(st["colors"][r], [bg, out["track"]], MARK, to), [bg, out["inset"]], TEXT, to)
    else:                    # one neutral card material; the hue is the bar (if any), the chip and the icon
        out.update({"c_bg": st["card"], "c_border": st["border"],
                    "c_bar": t["s9"] if st["bar"] else st["border"]})
    return out


def apply(expr, role):
    """resolve the per-card tokens of `role` in a card's expression (no-op when no style is active)"""
    if not ACTIVE:
        return expr
    for k, v in card_tokens(ACTIVE, role).items():
        expr = expr.replace(f"@@{k}@@", v)
    return expr


# ---------------------------------------------------------------- which style is active
def _from_config():
    try:
        return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline.json"),
                              encoding="utf-8")).get("style")
    except (OSError, ValueError):
        return None


def resolve_style(spec):
    """a preset name, a make_style() argument dict, {"preset": name, ...changed inputs}, {"logo": true, ...} (brand and
    accent from the logo in pipeline.json, with or without a preset), or None/"none" -> a style dict"""
    if spec in (None, "", "none"):
        return None
    if isinstance(spec, str) and spec.lstrip().startswith("{"):   # DASH_STYLE='{"brand": "#0E7490", "mode": "dark"}'
        spec = json.loads(spec)
    if isinstance(spec, dict) and spec.get("logo"):   # brand + accent from pipeline.json "logo" (logo.py)
        import logo as _logo
        ba = _logo.colors(spec["logo"] if isinstance(spec["logo"], str) else None)
        spec = {k: v for k, v in spec.items() if k != "logo"}
        spec.setdefault("brand", ba["brand"])          # an official brand hex given here wins over the extracted one
        if ba["accent"] and "accent" not in spec:
            spec["accent"] = ba["accent"]
    if isinstance(spec, dict) and "preset" in spec:   # a preset with some inputs changed
        name = spec["preset"]
        assert name in PRESETS, f"unknown preset {name!r}: use one of {', '.join(PRESETS)}"
        args = dict(PRESETS[name]["inputs"])
        args.update({k: v for k, v in spec.items() if k != "preset"})
        if ("brand" in spec or "accent" in spec) and "colors" not in spec:
            # a preset's colors pin every role, so a new brand alone used to change nothing: a given brand takes the
            # brand and c1 roles, a given accent c2; every role not given keeps the preset's hue (its curated palette)
            pin = {"brand": spec["brand"], "c1": spec["brand"]} if spec.get("brand") else {}
            if spec.get("accent"):
                pin["c2"] = spec["accent"]
            args["colors"] = dict(args["colors"], **pin)
        return make_style(**args)
    if isinstance(spec, dict):
        return make_style(**spec)
    assert spec in PRESETS, f"unknown style {spec!r}: use a preset ({', '.join(PRESETS)}) or a make_style() dict"
    return PRESETS[spec]


# DASH_STYLE > pipeline.json "style" > DEFAULT. An explicit DASH_PALETTE selects the legacy palettes.
_spec = os.environ.get("DASH_STYLE") or (None if os.environ.get("DASH_PALETTE") else (_from_config() or DEFAULT))
ACTIVE = resolve_style(_spec)
NAME = _spec if isinstance(_spec, str) and _spec in PRESETS else "custom"
CARD = card_css(ACTIVE) if ACTIVE else None

if ACTIVE:   # register in palette.py (it imports this module last, or this module imported it first)
    import palette as _palette
    _palette.PALETTES["style"] = style_palette(ACTIVE)
    assert set(_palette.PALETTES["style"]) == set(_palette.PALETTES["ocean"]), "style palette must define every token"
    _palette.ACTIVE, _palette.STYLE = "style", NAME
    _palette.P = _palette.PALETTES["style"]
