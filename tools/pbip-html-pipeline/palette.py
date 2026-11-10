# -*- coding: utf-8 -*-
"""Color tokens for the dashboard. measures.py writes @@token@@ placeholders; add() resolves them
with the ACTIVE palette. 'ocean' reproduces the original hand-tuned colors exactly (regression baseline).

Switch:  set environment variable DASH_PALETTE=midnight (or edit ACTIVE) and rebuild.
Every palette defines every token; text-on-soft tokens (*_text) are chosen for WCAG >= 4.5:1;
"strong" is a fill that carries white (on_accent) text at >= 4.5:1 in that palette.
"""
import os

PALETTES = {
    "ocean": {  # light, enterprise-calm (original)
        "page_bg": "#F4F7FA", "outspace_bg": "#F4F7FA",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#F4F7FA", "bg_mid": "#F4F7FA", "bg_to": "#F4F7FA", "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#1F2937", "fg2": "#605E5C", "fg3": "#4B5563", "muted": "#8A8886",
        "primary": "#0F6CBD", "primary_text": "#0F4C8A", "strong": "#0F6CBD", "active_text": "#0F6CBD", "primary_soft": "#E6F0FA",
        "design": "#8764B8", "design_text": "#6B4C9A", "design_soft": "#F1ECF8",   # v002: text darkened for WCAG 4.5:1
        "maint": "#00A3AE", "maint_text": "#00747C", "maint_soft": "#E0F6F7",
        "done": "#107C10", "done_text": "#107C10", "done_soft": "#E5F2E5",
        "bad": "#D13438", "bad_soft": "#FBE7E7", "neutral_soft": "#F3F2F1",
        "track": "#EEF2F6", "border": "#E1E5EA", "divider": "#EEF1F4", "divider2": "#F0F2F5",
        "grid": "#E8ECF1", "connector": "#D6DCE3", "arrow": "#A0A8B3", "inset": "#F6F8FB",
        "series3": "#5B5FC7", "series4": "#CA5010", "shadow": "rgba(16,24,40,.10)",
        "slicer_fg": "#1F2937", "slicer_bg": "#FFFFFF", "slicer_border": "#C8CED6",
    },
    "midnight": {  # dark, full system (bg + surface + fg), from library/palettes.md #5
        "page_bg": "#141A22", "outspace_bg": "#141A22",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#141A22", "bg_mid": "#141A22", "bg_to": "#141A22", "surface": "#1D2632", "on_accent": "#FFFFFF",
        "fg": "#E8EDF2", "fg2": "#A9B4C0", "fg3": "#C3CCD6", "muted": "#7A8794",
        "primary": "#4EA3F1", "primary_text": "#9CCBF7", "strong": "#1F6FB8", "active_text": "#9CCBF7", "primary_soft": "#1F3B57",
        "design": "#9B8AFB", "design_text": "#C4B9FD", "design_soft": "#2E2A4F",
        "maint": "#34D3BE", "maint_text": "#7FE6D8", "maint_soft": "#163A3A",
        "done": "#4CC38A", "done_text": "#8EDDB6", "done_soft": "#173826",
        "bad": "#F16B6B", "bad_soft": "#3D2024", "neutral_soft": "#2A3646",
        "track": "#2A3646", "border": "#33404F", "divider": "#2A3646", "divider2": "#2A3646",
        "grid": "#2E3A49", "connector": "#3E4C5C", "arrow": "#6E7C8B", "inset": "#18212C",
        "series3": "#9B8AFB", "series4": "#F0B35E", "shadow": "rgba(0,0,0,.35)",
        "slicer_fg": "#E8EDF2", "slicer_bg": "#1D2632", "slicer_border": "#3E4C5C",
    },
    "berry": {  # light, colorful (marketing/product), from library/palettes.md #4
        "page_bg": "#FAF5F8", "outspace_bg": "#FAF5F8",
        "kpi_filled": "0", "bg_layer": "0", "bg_from": "#FAF5F8", "bg_mid": "#FAF5F8", "bg_to": "#FAF5F8", "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#2B1F29", "fg2": "#6B5A68", "fg3": "#4A3B47", "muted": "#A79AA4",
        "primary": "#7C2D5E", "primary_text": "#6A2550", "strong": "#7C2D5E", "active_text": "#7C2D5E", "primary_soft": "#F4E6EF",
        "design": "#4A3B76", "design_text": "#4A3B76", "design_soft": "#ECE8F5",
        "maint": "#E56BA0", "maint_text": "#A8336A", "maint_soft": "#FBE7F0",
        "done": "#3E7D4E", "done_text": "#2F6A3E", "done_soft": "#E6F2E9",
        "bad": "#D13438", "bad_soft": "#FBE7E7", "neutral_soft": "#F1E4EC",
        "track": "#F1E4EC", "border": "#E8D8E2", "divider": "#F3EAF0", "divider2": "#F3EAF0",
        "grid": "#EEE2EA", "connector": "#DCCAD6", "arrow": "#B3A2AE", "inset": "#FBF7FA",
        "series3": "#D9A441", "series4": "#4A3B76", "shadow": "rgba(43,31,41,.10)",
        "slicer_fg": "#2B1F29", "slicer_bg": "#FFFFFF", "slicer_border": "#DCCAD6",
    },
    "vivid": {  # colorful: gradient page (indigo -> violet -> pink), filled KPI cards, saturated status colors
        "page_bg": "#4C1D95", "outspace_bg": "#312E81",
        "kpi_filled": "1", "bg_layer": "1", "bg_from": "#312E81", "bg_mid": "#6D28D9", "bg_to": "#BE185D",
        "surface": "#FFFFFF", "on_accent": "#FFFFFF",
        "fg": "#1E1B4B", "fg2": "#475569", "fg3": "#334155", "muted": "#94A3B8",
        "primary": "#1D4ED8", "primary_text": "#1E3A8A", "strong": "#1D4ED8", "active_text": "#1D4ED8", "primary_soft": "#DBEAFE",
        "design": "#7C3AED", "design_text": "#5B21B6", "design_soft": "#EDE9FE",
        "maint": "#0F766E", "maint_text": "#115E59", "maint_soft": "#CCFBF1",
        "done": "#15803D", "done_text": "#166534", "done_soft": "#DCFCE7",
        "bad": "#C81E1E", "bad_soft": "#FEE2E2", "neutral_soft": "#EEF2FF",
        "track": "#EEF2FF", "border": "#E0E7FF", "divider": "#EEF2FF", "divider2": "#EEF2FF",
        "grid": "#E0E7FF", "connector": "#C7D2FE", "arrow": "#A5B4FC", "inset": "#F5F3FF",
        "series3": "#DB2777", "series4": "#F59E0B", "shadow": "rgba(30,27,75,.30)",
        "slicer_fg": "#1E1B4B", "slicer_bg": "#FFFFFF", "slicer_border": "#C7D2FE",
    },
}

# ---------------------------------------------------------------- derive a palette from brand colors
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in c)


def _lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _mix(a, b, t):
    """t=0 -> a, t=1 -> b"""
    ca, cb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ca, cb)))


def _readable(color, bg, target=4.5, toward="#000000"):
    """the closest mix of color toward black (light bg) or white (dark bg) that reads on bg at `target`"""
    if contrast(color, bg) >= target:
        return color
    lo, hi = 0.0, 1.0
    if contrast(_mix(color, toward, 1.0), bg) < target:
        raise ValueError(f"no shade of {color} toward {toward} reaches {target}:1 on {bg}")
    for _ in range(30):
        mid = (lo + hi) / 2
        if contrast(_mix(color, toward, mid), bg) >= target:
            hi = mid
        else:
            lo = mid
    return _mix(color, toward, hi)


# ---------------------------------------------------------------- categorical colors (non-status series)
# Six categorical colors per palette for charts colored by category (bars, tiles, bubbles, panels).
# Each catN gets catN_soft (tile/pill background) and catN_text (text on catN_soft, >= 4.5:1).
# Light sets follow the reference HTML catalog's palettes; they never replace status colors.
CATS = {
    "ocean":    ["#0F6CBD", "#00A3AE", "#8764B8", "#CA5010", "#107C10", "#5B5FC7"],
    "midnight": ["#4EA3F1", "#34D3BE", "#9B8AFB", "#F0B35E", "#4CC38A", "#F16B6B"],
    "berry":    ["#7C2D5E", "#E56BA0", "#4A3B76", "#D9A441", "#3E7D4E", "#D13438"],
    "vivid":    ["#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4", "#EC4899"],   # catalog "vivid"
}


def _is_dark(p):
    return _lum(p["surface"]) < 0.2


def add_cats(p, cats):
    """write cat1..cat6 (+ _soft, _text) into palette p; text tokens pushed to WCAG 4.5:1"""
    dark = _is_dark(p)
    away = "#FFFFFF" if dark else "#000000"
    for i, c in enumerate(cats, 1):
        soft = _mix(c, p["surface"], 0.80) if dark else _mix(c, "#FFFFFF", 0.86)
        p[f"cat{i}"], p[f"cat{i}_soft"] = c, soft
        p[f"cat{i}_text"] = _readable(c, soft, toward=away)
    return p


for _name, _cats in CATS.items():
    add_cats(PALETTES[_name], _cats)


def _derived_cats(a, b):
    """the catalog's 'derived' set: two colors expanded into six without muddy midpoints"""
    return [a, b, _mix(a, "#000000", 0.30), _mix(a, "#FFFFFF", 0.42), _mix(b, "#000000", 0.26), _mix(b, "#FFFFFF", 0.44)]


def derive(primary, accent=None, dark=False, cats=None):
    """A full palette (every token) from one or two brand colors. Text tokens are pushed until they
    pass WCAG 4.5:1 on their backgrounds; 'strong' is pushed until white text passes on it.
    cats: optional six categorical colors (default: the catalog's 'derived' expansion of primary/accent)."""
    accent = accent or _mix(primary, "#00A3AE", 0.6)
    base = dict(PALETTES["midnight" if dark else "ocean"])
    surface, page, fg = base["surface"], base["page_bg"], base["fg"]
    soft = (lambda c: _mix(c, surface, 0.78)) if dark else (lambda c: _mix(c, "#FFFFFF", 0.88))
    away = "#FFFFFF" if dark else "#000000"
    out = dict(base)
    out.update({
        "primary": primary, "primary_soft": soft(primary),
        "primary_text": _readable(primary, soft(primary), toward=away),
        "active_text": _readable(primary, soft(primary), toward=away),
        "strong": _readable(primary, "#FFFFFF", toward="#000000"),
        "maint": accent, "maint_soft": soft(accent), "maint_text": _readable(accent, soft(accent), toward=away),
        "series3": _mix(primary, accent, 0.5),
        "bg_from": page, "bg_mid": page, "bg_to": page,
    })
    for k in ("primary_text", "active_text", "maint_text", "design_text", "done_text"):
        bgk = k.replace("_text", "_soft").replace("active_soft", "primary_soft")
        assert contrast(out[k], out[bgk]) >= 4.5, (k, out[k], out[bgk])
    assert contrast("#FFFFFF", out["strong"]) >= 4.5 and contrast(fg, surface) >= 4.5
    add_cats(out, cats or _derived_cats(primary, accent))
    return out


# The reference HTML catalog's six presets as ready palettes (accent / accent2 / categorical set).
_MONO = lambda c: [c] + [_mix(c, "#FFFFFF", t) for t in (0.22, 0.42, 0.60, 0.75)] + ["#94A3B8"]
PRESETS = {
    "exec":  dict(primary="#2563EB", accent="#F59E0B"),                       # blue-gold, executive
    "trend": dict(primary="#06B6D4", accent="#F59E0B"),                       # teal, trend focus
    "mono":  dict(primary="#334155", accent="#94A3B8", cats=_MONO("#334155")),  # one hue, no noise
    "night": dict(primary="#818CF8", accent="#FBBF24", dark=True),            # dark, light violet
    "warm":  dict(primary="#F43F5E", accent="#EC4899",
                  cats=["#F43F5E", "#F59E0B", "#EC4899", "#8B5CF6", "#FBBF24", "#94A3B8"]),   # catalog "sunset"
    "forest": dict(primary="#10B981", accent="#84CC16",
                   cats=["#10B981", "#84CC16", "#EAB308", "#14B8A6", "#22C55E", "#94A3B8"]),  # catalog "forest"
}
for _name, _spec in PRESETS.items():
    PALETTES[_name] = derive(**_spec)

# brand palettes from the environment: DASH_PRIMARY=#hex [DASH_ACCENT=#hex] [DASH_DARK=1] -> palette "brand"
if os.environ.get("DASH_PRIMARY"):
    PALETTES["brand"] = derive(os.environ["DASH_PRIMARY"], os.environ.get("DASH_ACCENT"), os.environ.get("DASH_DARK") == "1")

# ---------------------------------------------------------------- legacy palette choice
ACTIVE = os.environ.get("DASH_PALETTE", "brand" if "brand" in PALETTES else "ocean")
P = PALETTES[ACTIVE]
STYLE = ""
assert all(set(v) == set(PALETTES["ocean"]) for v in PALETTES.values()), "every palette must define every token"
# a colorful style (styles.py: DASH_STYLE / pipeline.json "style", default "accent") replaces the choice above:
# styles.py registers PALETTES["style"] and sets ACTIVE, P and STYLE here. Works in either import order.
import styles as _styles  # noqa: E402


def theme_json(palette=None, name=None):
    """A Power BI report theme (import via View > Themes > Browse) so native visuals and the
    --pbi-theme-* variables match the palette."""
    p = PALETTES[palette] if palette else P
    return {
        "name": name or f"pbi-html-{palette or ACTIVE}",
        "dataColors": [p["primary"], p["maint"], p["design"], p["series4"], p["done"], p["series3"], p["bad"], p["muted"]],
        "background": p["surface"], "foreground": p["fg"], "tableAccent": p["primary"],
        "good": p["done"], "bad": p["bad"], "neutral": p["muted"],
    }   # padding 0 is set per HTML Content visual by gen_pbip.py - never theme-wide (native visuals need theirs)


if __name__ == "__main__":      # python -I palette.py theme out.json  -> write the active palette as a report theme
    import json, sys
    if len(sys.argv) > 2 and sys.argv[1] == "theme":
        json.dump(theme_json(), open(sys.argv[2], "w", encoding="utf-8"), indent=2)
        print(f"theme written: {sys.argv[2]} ({ACTIVE})")


def resolve(text, palette=None):
    pal = PALETTES[palette] if palette else P
    for k, v in pal.items():
        text = text.replace(f"@@{k}@@", v)
    assert "@@" not in text, "unresolved color token"
    return text
