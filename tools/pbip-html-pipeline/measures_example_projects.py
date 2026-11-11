# -*- coding: utf-8 -*-
"""Single source of truth for the Hebrew RTL HTML Content dashboard measures.
All measures live on table 'פרויקטים'. HTML is fully inline-styled (no Stylesheet
property, no <style>, no script) so it renders the same in HTML Content Secure and Regular.
"""

import config   # first: pipeline.json "dir" / "lang" (the data's language) set the defaults below
from palette import P, resolve, ACTIVE
import os as _os

# Reading direction of the whole dashboard: "rtl" (Hebrew/Arabic) or "ltr" (English...). Env: DASH_DIR.
DIR = _os.environ.get("DASH_DIR", "rtl")
assert DIR in ("rtl", "ltr"), "DASH_DIR must be rtl or ltr"
DIR_TOKENS = {
    "rtl": {"dir": "rtl", "lang": "he", "start": "right", "end": "left", "fwd_arrow": "&#9664;"},
    "ltr": {"dir": "ltr", "lang": "en", "start": "left", "end": "right", "fwd_arrow": "&#9654;"},
}[DIR]
DIR_TOKENS["lang"] = _os.environ.get("DASH_LANG", DIR_TOKENS["lang"])   # UI language: he (authored) or en
LANG = DIR_TOKENS["lang"]
DIR_TOKENS["locale"] = {"he": "he-IL", "en": "en-US"}.get(LANG, "en-US")   # month names in the timeline
from labels import translate, STATUS_EN


def _resolve_dir(text):
    for k, v in DIR_TOKENS.items():
        text = text.replace(f"@@{k}@@", v)
    return text

from config import TABLE   # host table from pipeline.json (the reference build uses 'פרויקטים')
T = f"'{TABLE}'"
C = lambda c: f"{T}[{c}]"

FONT = "font-family:Segoe UI,Arial,sans-serif"
CARD = ("box-sizing:border-box;height:100vh;overflow:hidden;background:@@surface@@;"
        "border-radius:12px;box-shadow:0 1px 3px @@shadow@@;line-height:1.35;"
        "direction:@@dir@@;text-align:@@start@@;" + FONT + ";color:@@fg@@")
FG2 = "@@fg2@@"
TRACK = "@@track@@"

# ---------------------------------------------------------------- colorful styles (styles.py)
# Every card - KPI and analysis - is the same material; each card has a ROLE that picks its hue, and the
# active style decides how that hue shows (bar / tint / chip) and computes every in-card color for contrast.
import styles as S
STYLE = S.NAME if S.ACTIVE else ""
CARD_ROLE = {   # this dashboard's cards -> roles (a KPI and the chart about the same thing share a role)
    "HTML Header": "neutral", "HTML Filter Panel": "neutral",
    "HTML KPI סהכ": "hero", "HTML KPI פעילים": "c1", "HTML KPI באפיון": "c2",
    "HTML KPI בתחזוקה": "c3", "HTML KPI מועדים": "bad",
    "HTML Status Flow": "c2", "HTML Owners": "c1", "HTML Departments": "c3",
    "HTML Timeline": "warn", "HTML Type Donut": "c4",
}
if S.ACTIVE:
    CARD = S.CARD


def _apply_card_tokens(name, expr):
    return S.apply(expr, CARD_ROLE.get(name, "neutral"))


# status -> (display, color, light bg)
STATUSES = [
    ("באפיון", "באפיון", "@@design@@", "@@design_soft@@"),
    ("פעיל", "פעיל", "@@primary@@", "@@primary_soft@@"),
    ("בתחזוקה שוטפת", "בתחזוקה שוטפת", "@@maint@@", "@@maint_soft@@"),
    ("הושלם/פרויקט חד פעמי", "הושלם", "@@done@@", "@@done_soft@@"),
]

ISO = "VAR LRI = UNICHAR ( 8294 )\nVAR PDI = UNICHAR ( 8297 )\n"


def status_color_switch(var):
    parts = ", ".join(f'"{s}", "{c}"' for s, _, c, _ in STATUSES)
    return f"SWITCH ( {var}, {parts}, \"@@muted@@\" )"


def _txt(tok):  # status fill token -> its text-safe variant (WCAG 4.5:1 on the soft background)
    return tok.replace("@@primary@@", "@@active_text@@").replace("@@design@@", "@@design_text@@").replace("@@maint@@", "@@maint_text@@").replace("@@done@@", "@@done_text@@")


def status_text_switch(var):
    parts = ", ".join(f'"{s}", "{_txt(c)}"' for s, _, c, _ in STATUSES)
    return f"SWITCH ( {var}, {parts}, \"@@fg2@@\" )"


def status_bg_switch(var):
    parts = ", ".join(f'"{s}", "{bg}"' for s, _, _, bg in STATUSES)
    return f"SWITCH ( {var}, {parts}, \"@@neutral_soft@@\" )"


def status_name_switch(var):
    if LANG == "en":   # data values stay Hebrew in the model; only their display is English
        pairs = ", ".join(f'"{k}", "{v}"' for k, v in STATUS_EN.items())
        return f'SWITCH ( {var}, {pairs}, "", "No status", {var} )'
    return f'SWITCH ( {var}, "הושלם/פרויקט חד פעמי", "הושלם", "", "ללא סטטוס", {var} )'


def legend_html():
    return "".join(
        f"<span style='display:inline-flex;align-items:center;gap:4px'>"
        f"<span style='width:10px;height:10px;border-radius:3px;background:{c}'></span>{d}</span>"
        for _, d, c, _ in STATUSES)


M = {}  # name -> dict(expr, folder, fmt)


import re as _re
FONT_SCALE = {10: 13, 11: 14, 12: 15, 13: 16, 14: 17, 16: 20, 18: 22, 22: 26, 24: 30, 30: 36, 40: 50}


def _scale_fonts(expr):
    return _re.sub(r"font-size:(\d+)px", lambda m: f"font-size:{FONT_SCALE.get(int(m.group(1)), int(m.group(1)))}px", expr)


def add(name, expr, folder, fmt=None):
    M[name] = dict(expr=translate(resolve(_apply_card_tokens(name, _resolve_dir(_scale_fonts(expr.strip())))), LANG), folder=folder, fmt=fmt)


# ---------------------------------------------------------------- base measures
add("# פרויקטים", f"COUNTROWS ( {T} )", "מדדים", "0")
for key, nm in [("פעיל", "# פעילים"), ("באפיון", "# באפיון"),
                ("בתחזוקה שוטפת", "# בתחזוקה"), ("הושלם/פרויקט חד פעמי", "# הושלמו")]:
    add(nm, f'CALCULATE ( [# פרויקטים], KEEPFILTERS ( {C("סטטוס")} = "{key}" ) )', "מדדים", "0")
add("# חלף מועד יעד", f"""
COUNTROWS (
    FILTER (
        {T},
        NOT ISBLANK ( {C("מועד יעד")} )
            && {C("מועד יעד")} < TODAY ()
            && {C("סטטוס")} IN {{ "פעיל", "באפיון" }}
    )
)""", "מדדים", "0")
add("# יעד ב-30 יום", f"""
COUNTROWS (
    FILTER (
        {T},
        NOT ISBLANK ( {C("מועד יעד")} )
            && {C("מועד יעד")} >= TODAY ()
            && {C("מועד יעד")} <= TODAY () + 30
            && {C("סטטוס")} IN {{ "פעיל", "באפיון" }}
    )
)""", "מדדים", "0")

# ---------------------------------------------------------------- header
def chip_block(col, label, k):
    return f"""
VAR _v{k} = FILTER ( VALUES ( {C(col)} ), TRUE () )
VAR _c{k} =
    IF (
        ISFILTERED ( {C(col)} ),
        "<span style='display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;background:@@primary_soft@@;color:@@primary_text@@;font-size:12px;white-space:nowrap'><b>{label}:</b> "
            & IF (
                COUNTROWS ( _v{k} ) > 2,
                LRI & COUNTROWS ( _v{k} ) & PDI & " נבחרו",
                CONCATENATEX ( _v{k}, IF ( {C(col)} = "", "לא שויך", {status_name_switch(C(col)) if col == "סטטוס" else C(col)} ), ", " )
            ) & "</span>"
    )"""


_header_expr = (ISO + "".join(chip_block(c, l, k) for k, (c, l) in enumerate(
    [("סטטוס", "סטטוס"), ("מחלקה", "מחלקה"), ("בעלים", "בעלים"), ("סוג", "סוג")])) + f"""
VAR _chips = _c0 & _c1 & _c2 & _c3
VAR _state =
    IF (
        _chips = "",
        "<span style='font-size:12px;color:{FG2}'>מוצגים כל הפרויקטים</span>",
        "<span style='font-size:12px;color:{FG2}'>סינון פעיל:</span>" & _chips
    )
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};display:flex;align-items:center;justify-content:space-between;gap:24px;padding:0 24px'>"
        & "<div style='display:flex;align-items:center;gap:16px;min-width:0'>"
            & "<div style='width:48px;height:48px;flex:none;border-radius:12px;background:@@primary@@;display:flex;align-items:center;justify-content:center'>"
                & "<svg width='26' height='26' viewBox='0 0 26 26'><rect x='2' y='2' width='9' height='9' rx='2' fill='@@on_accent@@'/><rect x='15' y='2' width='9' height='9' rx='2' fill='@@on_accent@@' opacity='.6'/><rect x='2' y='15' width='9' height='9' rx='2' fill='@@on_accent@@' opacity='.6'/><rect x='15' y='15' width='9' height='9' rx='2' fill='@@on_accent@@'/></svg>"
            & "</div>"
            & "<div style='min-width:0'>"
                & "<div style='font-size:22px;font-weight:700;line-height:1.2'>תיק הפרויקטים</div>"
                & "<div style='font-size:13px;color:{FG2};line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>מערכות, מסכי ניהול " & LRI & "BI" & PDI & " וסוכנים · מעקב לפי סטטוס, בעלים, מחלקה ומועדי יעד</div>"
            & "</div>"
        & "</div>"
        & "<div style='display:flex;align-items:center;gap:8px;flex-wrap:nowrap;justify-content:flex-end;flex:0 1 auto;min-width:0;overflow:hidden'>"
            & _state
            & "<span style='padding:4px 12px;border-radius:999px;background:@@neutral_soft@@;font-size:12px;color:@@fg@@;white-space:nowrap'>"
                & LRI & [# פרויקטים] & PDI & " פרויקטים בתצוגה</span>"
            & "<span style='padding:4px 12px;border-radius:999px;border:1px solid @@border@@;font-size:12px;color:{FG2};white-space:nowrap'>נכון ל-"
                & LRI & FORMAT ( TODAY (), "dd/MM/yyyy" ) & PDI & "</span>"
        & "</div>"
    & "</div>\"""")
add("HTML Header", _header_expr, "HTML")


# ---------------------------------------------------------------- KPI cards
ICONS = {
    "all": "<svg width='22' height='22' viewBox='0 0 18 18'><rect x='1' y='2' width='16' height='4' rx='1.5' fill='{c}'/><rect x='1' y='8' width='16' height='4' rx='1.5' fill='{c}' opacity='.6'/><rect x='1' y='14' width='10' height='3' rx='1.5' fill='{c}' opacity='.35'/></svg>",
    "play": "<svg width='22' height='22' viewBox='0 0 18 18'><circle cx='9' cy='9' r='8' fill='{c}'/><path d='M7 5.5v7l5.5-3.5z' fill='@@on_accent@@'/></svg>",
    "pen": "<svg width='22' height='22' viewBox='0 0 18 18'><rect x='2' y='2' width='14' height='14' rx='3' fill='{c}'/><path d='M5.5 12.5l1-3 5-5 2 2-5 5z' fill='@@on_accent@@'/></svg>",
    "gear": "<svg width='22' height='22' viewBox='0 0 18 18'><circle cx='9' cy='9' r='7' fill='none' stroke='{c}' stroke-width='3' stroke-dasharray='3.2 2'/><circle cx='9' cy='9' r='3' fill='{c}'/></svg>",
    "clock": "<svg width='22' height='22' viewBox='0 0 18 18'><circle cx='9' cy='9' r='8' fill='{c}'/><path d='M9 4.5V9l3 2' stroke='@@on_accent@@' stroke-width='1.8' fill='none' stroke-linecap='round'/></svg>",
}


FILLED = P["kpi_filled"] == "1"   # colorful palettes: KPI cards filled with their accent, white text


def kpi(name, title, value_expr, accent, light, icon, sub_expr, value_color=None):
    vc = value_color or '"@@fg@@"'
    if STYLE:   # same material as every other card; the hero role turns this one solid (styles.py)
        root = f"{CARD};padding:16px 20px;display:flex;flex-direction:column;justify-content:space-between"
        title_c, chip_bg = FG2, "@@c_chip@@"
        glyph = ICONS[icon].replace("@@on_accent@@", "@@c_icon_in@@").format(c="@@c_icon@@")
        sub_expr = sub_expr.replace(f"background:{accent};border-radius:3px", "background:@@c_icon@@;border-radius:3px")
    elif FILLED:
        # card = accent with a darkening overlay (text contrast only improves toward the bottom)
        root = f"{CARD};background:linear-gradient(160deg,rgba(0,0,0,0),rgba(0,0,0,.24)),{accent};padding:16px 20px;display:flex;flex-direction:column;justify-content:space-between"
        title_c, chip_bg = "@@on_accent@@", "rgba(255,255,255,.22)"
        glyph = ICONS[icon].replace("@@on_accent@@", "§ACC§").format(c="@@on_accent@@").replace("§ACC§", accent)
        vc = '"@@on_accent@@"'
        sub_expr = (sub_expr.replace("color:@@fg2@@", "color:@@on_accent@@")
                    .replace("background:@@track@@", "background:rgba(255,255,255,.30)")
                    .replace(f"background:{accent};border-radius:3px", "background:@@on_accent@@;border-radius:3px"))
    else:
        root = f"{CARD};border-inline-start:4px solid {accent};padding:16px 20px;display:flex;flex-direction:column;justify-content:space-between"
        title_c, chip_bg, glyph = FG2, light, ICONS[icon].format(c=accent)
    add(name, ISO + f"""
VAR _val = {value_expr}
VAR _vc = {vc}
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{root}'>"
        & "<div style='display:flex;align-items:center;justify-content:space-between'>"
            & "<span style='font-size:14px;font-weight:600;color:{title_c}'>{title}</span>"
            & "<span style='width:40px;height:40px;flex:none;border-radius:10px;background:{chip_bg};display:flex;align-items:center;justify-content:center'>{glyph}</span>"
        & "</div>"
        & "<div style='font-size:40px;font-weight:700;line-height:1;color:" & _vc & ";direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>" & FORMAT ( _val + 0, "#,##0" ) & "</div>"
        & {sub_expr}
    & "</div>\"""", "HTML")


def share_sub(measure, accent, extra='""'):
    return f"""VAR _sh = DIVIDE ( {measure}, [# פרויקטים] )
    RETURN
        "<div style='display:flex;flex-direction:column;gap:6px'>"
            & "<div style='height:6px;border-radius:3px;background:{TRACK};overflow:hidden'><div style='height:100%;width:" & FORMAT ( _sh * 100, "0.0" ) & "%;background:{accent};border-radius:3px'></div></div>"
            & "<div style='font-size:12px;color:{FG2}'>" & LRI & FORMAT ( _sh, "0%" ) & PDI & " מהתיק" & {extra} & "</div>"
        & "</div>\""""


def wrap(sub):  # turn "VAR..RETURN.." snippet into a parenthesised expression
    return "(\n    " + sub + "\n)"


kpi("HTML KPI סהכ", "סה״כ פרויקטים", "[# פרויקטים]", "@@fg@@", "@@neutral_soft@@", "all",
    f"""(
    VAR _d = COUNTROWS ( FILTER ( VALUES ( {C("מחלקה")} ), {C("מחלקה")} <> "" ) )
    VAR _o = COUNTROWS ( FILTER ( VALUES ( {C("בעלים")} ), {C("בעלים")} <> "" ) )
    RETURN
        "<div style='font-size:12px;color:{FG2}'>ב-" & LRI & _d & PDI & " מחלקות · " & LRI & _o & PDI & " בעלי פרויקטים</div>"
)""")
kpi("HTML KPI פעילים", "פעילים", "[# פעילים]", "@@primary@@", "@@primary_soft@@", "play",
    wrap(share_sub("[# פעילים]", "@@primary@@")))
kpi("HTML KPI באפיון", "באפיון", "[# באפיון]", "@@design@@", "@@design_soft@@", "pen",
    wrap(share_sub("[# באפיון]", "@@design@@")))
kpi("HTML KPI בתחזוקה", "בתחזוקה שוטפת", "[# בתחזוקה]", "@@maint@@", "@@maint_soft@@", "gear",
    wrap(share_sub("[# בתחזוקה]", "@@maint@@",
                   '" · " & LRI & ( [# הושלמו] + 0 ) & PDI & " הושלמו"')))
kpi("HTML KPI מועדים", "חלף מועד היעד", "[# חלף מועד יעד]", "@@bad@@", "@@bad_soft@@", "clock",
    f"""(
    VAR _up = [# יעד ב-30 יום] + 0
    RETURN
        "<div style='font-size:12px;color:{FG2}'>עוד " & LRI & _up & PDI & " מגיעים למועד ב-30 יום</div>"
)""",
    value_color='IF ( [# חלף מועד יעד] > 0, "@@bad@@", "@@done@@" )')


# ---------------------------------------------------------------- status lifecycle
stage_html = []
for i, (key, disp, col, bg) in enumerate(STATUSES):
    m = {"באפיון": "[# באפיון]", "פעיל": "[# פעילים]", "בתחזוקה שוטפת": "[# בתחזוקה]",
         "הושלם/פרויקט חד פעמי": "[# הושלמו]"}[key]
    stage_html.append((m, disp, col, bg))

stage_parts = []
bar_parts = []
legend_parts = []
for i, (m, disp, col, bg) in enumerate(stage_html):
    if i > 0:
        stage_parts.append(f'"<div style=\'flex:1;height:2px;background:@@connector@@;margin-top:28px;position:relative\'><span style=\'position:absolute;inset-inline-end:-4px;top:-9px;font-size:12px;color:@@arrow@@\'>@@fwd_arrow@@</span></div>"')
    stage_parts.append(
        f'"<div style=\'display:flex;flex-direction:column;align-items:center;gap:4px;width:104px;flex:none\'>'
        f'<div style=\'width:56px;height:56px;border-radius:50%;background:{bg};border:3px solid {col};display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:{_txt(col)}\'>" & ( {m} + 0 ) & "</div>'
        f'<div style=\'font-size:12px;font-weight:600;text-align:center;white-space:nowrap\'>{disp}</div>'
        f'<div style=\'font-size:11px;color:{FG2};direction:ltr;unicode-bidi:isolate\'>" & FORMAT ( DIVIDE ( {m}, _n ) + 0, "0%" ) & "</div></div>"')
    bar_parts.append(
        f'IF ( {m} > 0, "<div style=\'width:" & FORMAT ( DIVIDE ( {m}, _n ) * 100, "0.0" ) & "%;background:{col}\'></div>" )')
    legend_parts.append(
        f'"<div style=\'display:flex;align-items:center;gap:8px;font-size:13px\'><span style=\'width:10px;height:10px;border-radius:3px;background:{col};flex:none\'></span><span style=\'flex:1\'>{disp}</span>'
        f'<span style=\'font-weight:600;direction:ltr;unicode-bidi:isolate\'>" & ( {m} + 0 ) & "</span>'
        f'<span style=\'width:44px;text-align:@@end@@;color:{FG2};direction:ltr;unicode-bidi:isolate\'>" & FORMAT ( DIVIDE ( {m}, _n ) + 0, "0%" ) & "</span></div>"')

_sf_vars = ISO + f"""
VAR _n = [# פרויקטים]
VAR _own = FILTER ( ADDCOLUMNS ( VALUES ( {C("בעלים")} ), "@n", [# פרויקטים] ), {C("בעלים")} <> "" )
VAR _top1 = TOPN ( 1, _own, [@n], DESC, {C("בעלים")}, ASC )
VAR _topOwner = MAXX ( _top1, {C("בעלים")} )
VAR _topN = MAXX ( _top1, [@n] ) + 0
VAR _late = [# חלף מועד יעד] + 0
VAR _noDept = COUNTROWS ( FILTER ( {T}, {C("מחלקה")} = "" ) ) + 0
VAR _noDate = COUNTROWS ( FILTER ( {T}, ISBLANK ( {C("מועד יעד")} ) ) ) + 0
RETURN
"""
_sf_body = f"""        & "<div style='display:flex;align-items:flex-start;gap:4px'>"
            & {" & ".join(stage_parts)}
        & "</div>"
        & "<div style='display:flex;flex:none;height:14px;border-radius:7px;overflow:hidden;background:{TRACK}'>"
            & {" & ".join(bar_parts)}
        & "</div>"
        & "<div style='margin-top:auto;background:@@inset@@;border-radius:10px;padding:12px 16px;display:flex;flex-direction:column;gap:4px;font-size:12px;line-height:1.45'>"
            & "<div style='font-weight:700;font-size:13px'>תובנות</div>"
            & "<div>&#8226; " & IF ( _topN > 0, "<b>" & _topOwner & "</b> מוביל/ה " & LRI & _topN & PDI & " פרויקטים (" & LRI & FORMAT ( DIVIDE ( _topN, _n ), "0%" ) & PDI & " מהתיק)", "אין בעלים בבחירה" ) & "</div>"
            & "<div>&#8226; " & IF ( _late > 0, "<span style='color:@@bad@@;font-weight:600'>" & LRI & _late & PDI & " פרויקטים</span> פעילים או באפיון כבר עברו את מועד היעד", "אין פרויקטים פעילים שעברו את מועד היעד" ) & "</div>"
            & "<div>&#8226; ל-" & LRI & FORMAT ( DIVIDE ( _noDept, _n ) + 0, "0%" ) & PDI & " מהפרויקטים לא שויכה מחלקה, ול-" & LRI & FORMAT ( DIVIDE ( _noDate, _n ) + 0, "0%" ) & PDI & " אין מועד יעד</div>"
        & "</div>\""""
SF_TITLE, SF_SUB = "מחזור חיי הפרויקט", "כמה פרויקטים נמצאים בכל שלב, מאפיון ועד סיום"
add("HTML Status Flow", _sf_vars + f"""    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:16px 24px;display:flex;flex-direction:column;gap:14px'>"
        & "<div><div style='font-size:16px;font-weight:700'>{SF_TITLE}</div>"
        & "<div style='font-size:12px;color:{FG2}'>{SF_SUB}</div></div>"
""" + _sf_body + """
    & "</div>\"""", "HTML")


# ---------------------------------------------------------------- segmented bar lists
BLANK_NOTE = ""  # filled per call below


STATUS_MEASURE = {"באפיון": "[# באפיון]", "פעיל": "[# פעילים]", "בתחזוקה שוטפת": "[# בתחזוקה]",
                  "הושלם/פרויקט חד פעמי": "[# הושלמו]"}


def mix_block(cond):
    """DAX line: when `cond` holds (the list above is short), a status-mix block of the current selection
    sits at the bottom of the card (margin-top:auto) - real content instead of an empty band"""
    bars = " & ".join(
        f'''IF ( {STATUS_MEASURE[k]} > 0, "<div style='width:" & FORMAT ( DIVIDE ( {STATUS_MEASURE[k]}, [# פרויקטים] ) * 100, "0.0" ) & "%;background:{c}'></div>" )'''
        for k, _, c, _ in STATUSES)
    legend = " & ".join(
        f'''"<span style='display:inline-flex;align-items:center;gap:6px'><span style='width:10px;height:10px;border-radius:3px;background:{c}'></span>{d} <b style='color:@@fg@@;direction:ltr;unicode-bidi:isolate'>" & ( {STATUS_MEASURE[k]} + 0 ) & "</b></span>"'''
        for k, d, c, _ in STATUSES)
    return (f'''        & IF ( {cond}, "<div style='margin-top:auto;flex:none;background:@@inset@@;border-radius:10px;padding:10px 14px;display:flex;flex-direction:column;gap:8px'>"'''
            f''' & "<div style='font-size:13px;font-weight:700'>תמהיל הסטטוסים בבחירה</div>"'''
            f''' & "<div style='display:flex;flex:none;height:10px;border-radius:5px;overflow:hidden;background:@@track@@'>" & {bars} & "</div>"'''
            f''' & "<div style='display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:@@fg2@@'>" & {legend} & "</div></div>" )''')


def _seg_return(title, subtitle, top, cols, blank_note):
    grid = ("<div style='display:flex;flex-direction:column;gap:4px;flex:1 1 auto;min-height:0'>" if cols == 1 else
            "<div style='display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(\" & MAX ( 1, ROUNDUP ( COUNTROWS ( _top ) / 2, 0 ) ) & \",28px);gap:4px 24px'>")   # as many grid rows as items
    body = f"""        & "{grid}" & _body & "</div>"
        & IF ( _rest > 0, "<div class='tooltipEnabled'" & _tip & " style='font-size:12px;color:@@primary@@;cursor:help'>ועוד " & LRI & _rest & PDI & " נוספים · העבירו את העכבר לפירוט &#9432;</div>" )
        {BLANK_NOTE if blank_note else ""}
""" + mix_block(f"COUNTROWS ( _top ) <= {4 if cols == 1 else 8}")
    return f"""    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:20px 24px;display:flex;flex-direction:column;gap:12px'>"
        & "<div><div style='font-size:16px;font-weight:700;white-space:nowrap'>{title}</div><div style='font-size:12px;color:{FG2};white-space:nowrap'>{subtitle}</div></div>"
        & "<div style='display:flex;gap:14px;font-size:11px;color:{FG2};white-space:nowrap'>{legend_html()}</div>"
{body}
    & "</div>\""""


def seg_bars(name, col, title, subtitle, top, cols=1, skip_blank=False, blank_note=""):
    rowh = "flex:1 1 0;min-height:28px;max-height:40px" if cols == 1 else "height:28px"   # one-column rows stretch
    segs = " & ".join(
        f"""IF ( _s{i} > 0, "<div style='flex:none;width:" & FORMAT ( DIVIDE ( _s{i}, _max ) * 100, "0.00" ) & "%;background:{c}'></div>" )"""
        for i, (_, _, c, _) in enumerate(STATUSES))
    svars = "\n            ".join(
        f'VAR _s{i} = CALCULATE ( [# פרויקטים], KEEPFILTERS ( {C("סטטוס")} = "{k}" ) ) + 0'
        for i, (k, _, _, _) in enumerate(STATUSES))
    add(name, ISO + f"""
VAR _rows = FILTER ( ADDCOLUMNS ( VALUES ( {C(col)} ), "@n", [# פרויקטים] ), {"" if not skip_blank else C(col) + " <> " + chr(34) + chr(34) + " && "}TRUE () )
VAR _max = MAXX ( _rows, [@n] )
VAR _top = TOPN ( {top}, _rows, [@n], DESC, {C(col)}, ASC )
VAR _rest = COUNTROWS ( _rows ) - COUNTROWS ( _top )
VAR _restT = EXCEPT ( _rows, _top )
VAR _restR =
    ADDCOLUMNS (
        _restT,
        "@i",
            VAR _cn = [@n]
            VAR _cm = {C(col)}
            RETURN COUNTROWS ( FILTER ( _restT, [@n] > _cn || ( [@n] = _cn && {C(col)} < _cm ) ) ) + 1
    )
VAR _tip =
    CONCATENATEX (
        _restR,
        VAR _k = FORMAT ( [@i], "00" )
        RETURN
            " data-tooltip-title-" & _k & "='" & IF ( {C(col)} = "", "לא שויך", SUBSTITUTE ( {C(col)}, "'", "’" ) ) & "'"
                & " data-tooltip-value-" & _k & "='" & [@n] & "'",
        "", [@i], ASC
    )
VAR _body =
    CONCATENATEX (
        _top,
        VAR _nm = {C(col)}
        VAR _lbl = IF ( _nm = "", "לא שויך", SUBSTITUTE ( _nm, "'", "’" ) )
        VAR _lc = IF ( _nm = "", "{FG2}", "@@fg@@" )
        VAR _n = [@n]
        {svars}
        RETURN
            "<div style='display:flex;align-items:center;gap:12px;{rowh}'>"
                & "<div title='" & _lbl & "' style='width:{150 if cols == 1 else 96}px;flex:none;font-size:12px;color:" & _lc & ";white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & _lbl & "</div>"
                & "<div style='flex:1;display:flex;height:14px;border-radius:7px;overflow:hidden;background:{TRACK}'>" & {segs} & "</div>"
                & "<div style='width:32px;flex:none;font-size:13px;font-weight:700;text-align:@@end@@;direction:ltr;unicode-bidi:isolate'>" & _n & "</div>"
            & "</div>",
        "",
        [@n], DESC,
        {C(col)}, ASC
    )
RETURN
§RET§""".replace("§RET§", _seg_return(title, subtitle, top, cols, blank_note)), "HTML")


seg_bars("HTML Owners", "בעלים", "פרויקטים לפי בעלים", "פרויקטים לכל בעלים, לפי סטטוס", 6)
BLANK_NOTE = """& VAR _bl = CALCULATE ( [# פרויקטים], KEEPFILTERS ( 'פרויקטים'[מחלקה] = "" ) ) + 0
          RETURN IF ( _bl > 0, "<div style='font-size:12px;color:@@fg2@@;margin-top:auto'>" & LRI & _bl & PDI & " פרויקטים (" & LRI & FORMAT ( DIVIDE ( _bl, [# פרויקטים] ), "0%" ) & PDI & ") עדיין לא שויכו למחלקה</div>" )"""
seg_bars("HTML Departments", "מחלקה", "פרויקטים לפי מחלקה", "המחלקה המזמינה, לפי סטטוס", 12, cols=2, skip_blank=True, blank_note="y")


# ---------------------------------------------------------------- type donut
TYPE_COLORS = ["@@primary@@", "@@maint@@", "@@series3@@", "@@series4@@", "@@muted@@", "@@done@@"]
color_sw = "SWITCH ( _rk, " + ", ".join(f'{i+1}, "{c}"' for i, c in enumerate(TYPE_COLORS)) + ', "@@muted@@" )'
_DONUT_BODY = f"""        & "<div style='display:flex;align-items:center;gap:28px;flex:1;min-height:0'>"
            & "<svg viewBox='0 0 180 180' style='flex:none;height:100%;max-height:260px;aspect-ratio:1/1'>"
                & "<circle cx='90' cy='90' r='" & _R & "' fill='none' stroke='{TRACK}' stroke-width='24'/>" & _segs
                & "<text x='90' y='92' text-anchor='middle' style='font-size:30px;font-weight:700;fill:@@fg@@;{FONT}'>" & _tot & "</text>"
                & "<text x='90' y='114' text-anchor='middle' style='font-size:12px;fill:{FG2};{FONT}'>פרויקטים</text>"
            & "</svg>"
            & "<div style='flex:1;display:flex;flex-direction:column'>" & _legend & "</div>"
        & "</div>\""""
DONUT_TITLE = "פרויקטים לפי סוג"
DONUT_SUB = 'מערכות, מסכי ניהול ו-" & LRI & "BI" & PDI & ", סוכנים'


def _donut_return():
    return f"""    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:20px 24px;display:flex;flex-direction:column;gap:12px'>"
        & "<div><div style='font-size:16px;font-weight:700'>{DONUT_TITLE}</div><div style='font-size:12px;color:{FG2}'>{DONUT_SUB}</div></div>"
""" + _DONUT_BODY + """
    & "</div>\""""


add("HTML Type Donut", ISO + f"""
VAR _cats = ADDCOLUMNS ( VALUES ( {C("סוג")} ), "@n", [# פרויקטים] )
VAR _cats2 =
    ADDCOLUMNS (
        _cats,
        "@rk",
            VAR _cn = [@n]
            VAR _nm = {C("סוג")}
            RETURN COUNTROWS ( FILTER ( _cats, [@n] > _cn || ( [@n] = _cn && {C("סוג")} < _nm ) ) ) + 1
    )
VAR _tot = SUMX ( _cats, [@n] )
VAR _R = 62
VAR _Cf = 2 * PI () * _R
VAR _segs =
    CONCATENATEX (
        _cats2,
        VAR _rk = [@rk]
        VAR _before = SUMX ( FILTER ( _cats2, [@rk] < _rk ), [@n] )
        VAR _len = _Cf * DIVIDE ( [@n], _tot )
        RETURN
            "<circle cx='90' cy='90' r='" & _R & "' fill='none' stroke-width='24' stroke='" & {color_sw} & "' "
                & "stroke-dasharray='" & FORMAT ( _len, "0.00" ) & " " & FORMAT ( _Cf - _len, "0.00" ) & "' "
                & "stroke-dashoffset='" & FORMAT ( - _Cf * DIVIDE ( _before, _tot ), "0.00" ) & "' transform='rotate(-90 90 90)'/>",
        "", [@rk], ASC
    )
VAR _legend =
    CONCATENATEX (
        _cats2,
        VAR _rk = [@rk]
        VAR _nm = {C("סוג")}
        RETURN
            "<div style='display:flex;align-items:center;gap:10px;font-size:13px;height:36px;border-bottom:1px solid @@divider2@@'>"
                & "<span style='width:10px;height:10px;border-radius:3px;flex:none;background:" & {color_sw} & "'></span>"
                & "<span style='flex:1;color:" & IF ( _nm = "", "{FG2}", "@@fg@@" ) & "'>" & IF ( _nm = "", "לא הוגדר", _nm ) & "</span>"
                & "<span style='font-weight:600;direction:ltr;unicode-bidi:isolate'>" & [@n] & "</span>"
                & "<span style='width:44px;text-align:@@end@@;color:{FG2};direction:ltr;unicode-bidi:isolate'>" & FORMAT ( DIVIDE ( [@n], _tot ), "0%" ) & "</span>"
            & "</div>",
        "", [@rk], ASC
    )
RETURN
§RET§""".replace("§RET§", _donut_return()), "HTML")
# ---------------------------------------------------------------- timeline (gantt strip)
_TL_BODY = f"""        & IF (
            _cnt = 0,
            "<div style='flex:1;display:flex;align-items:center;justify-content:center;font-size:13px;color:{FG2}'>אין פרויקטים עם מועד יעד בבחירה הנוכחית</div>",
            "<div style='display:flex;gap:12px;height:22px'><div style='width:270px;flex:none'></div><div style='width:116px;flex:none'></div>"
                & "<div style='flex:1;position:relative;direction:ltr'>" & _axis & "</div><div style='width:100px;flex:none;font-size:11px;color:{FG2};text-align:@@end@@;line-height:22px'>מועד יעד</div></div>"
                & "<div style='display:flex;flex-direction:column;gap:2px'>" & _body & "</div>"
                & IF ( _cnt > 7, "<div class='tooltipEnabled'" & _tip & " style='font-size:12px;color:@@primary@@;cursor:help'>ועוד " & LRI & ( _cnt - 7 ) & PDI & " פרויקטים עם מועד מאוחר יותר · העבירו את העכבר לפירוט &#9432;</div>" )
        )"""
_TL_BODY += "\n" + mix_block("_cnt > 0 && _cnt <= 4")   # few dated rows: the mix fills the card
TL_TITLE = "לוח זמנים · פרויקטים עם מועד יעד"
TL_SUB = '" & LRI & _cnt & PDI & " מתוך " & LRI & [# פרויקטים] & PDI & " פרויקטים הוגדרו עם תאריכים · ציר הזמן נקרא משמאל לימין'


def _tl_return():
    return f"""    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:16px 24px;display:flex;flex-direction:column;gap:8px'>"
        & _head
""" + _TL_BODY + """
    & "</div>\""""


add("HTML Timeline", ISO + f"""
VAR _dated = FILTER ( {T}, NOT ISBLANK ( {C("מועד יעד")} ) )
VAR _cnt = COUNTROWS ( _dated ) + 0
VAR _rows = TOPN ( 7, _dated, {C("מועד יעד")}, ASC, {C("מזהה")}, ASC )
VAR _restT = EXCEPT ( _dated, _rows )
VAR _tip =
    CONCATENATEX (
        _restT,
        VAR _k = FORMAT ( COUNTROWS ( FILTER ( _restT, {C("מועד יעד")} < EARLIER ( {C("מועד יעד")} ) || ( {C("מועד יעד")} = EARLIER ( {C("מועד יעד")} ) && {C("מזהה")} < EARLIER ( {C("מזהה")} ) ) ) ) + 1, "00" )
        RETURN
            " data-tooltip-title-" & _k & "='" & SUBSTITUTE ( {C("כותרת")}, "'", "’" ) & "'"
                & " data-tooltip-value-" & _k & "='" & FORMAT ( {C("מועד יעד")}, "dd/MM/yyyy" ) & "'",
        "", {C("מועד יעד")}, ASC, {C("מזהה")}, ASC
    )
VAR _today = TODAY ()
VAR _minD = MIN ( MINX ( _rows, COALESCE ( {C("תאריך התחלה")}, {C("מועד יעד")} - 14 ) ), _today )
VAR _maxD = MAX ( MAXX ( _rows, {C("מועד יעד")} ), _today )
VAR _rs = DATE ( YEAR ( _minD ), MONTH ( _minD ), 1 )
VAR _re = EOMONTH ( _maxD, 0 ) + 1
VAR _span = INT ( _re - _rs )
VAR _months = DATEDIFF ( _rs, _re, MONTH )
VAR _todayPct = FORMAT ( DIVIDE ( INT ( _today - _rs ), _span ) * 100, "0.00" )
VAR _grid =
    CONCATENATEX (
        GENERATESERIES ( 1, _months - 1, 1 ),
        "<div style='position:absolute;top:0;bottom:0;left:" & FORMAT ( DIVIDE ( INT ( EDATE ( _rs, [Value] ) - _rs ), _span ) * 100, "0.00" ) & "%;width:1px;background:@@grid@@'></div>"
    )
    & "<div style='position:absolute;top:0;bottom:0;left:" & _todayPct & "%;width:2px;background:@@bad@@;opacity:.7'></div>"
VAR _axis =
    CONCATENATEX (
        GENERATESERIES ( 0, _months - 1, 1 ),
        VAR _m0 = EDATE ( _rs, [Value] )
        VAR _w = DIVIDE ( INT ( EDATE ( _rs, [Value] + 1 ) - _m0 ), _span ) * 100
        RETURN
            "<div style='position:absolute;top:0;height:22px;left:" & FORMAT ( DIVIDE ( INT ( _m0 - _rs ), _span ) * 100, "0.00" ) & "%;width:" & FORMAT ( _w, "0.00" ) & "%;text-align:center;font-size:11px;color:{FG2};line-height:22px;direction:@@dir@@'>"
                & FORMAT ( _m0, "mmmm", "@@locale@@" ) & " " & LRI & YEAR ( _m0 ) & PDI & "</div>",
        "", [Value], ASC
    )
VAR _body =
    CONCATENATEX (
        _rows,
        VAR _st = {C("סטטוס")}
        VAR _due = {C("מועד יעד")}
        VAR _s = COALESCE ( {C("תאריך התחלה")}, _due - 14 )
        VAR _late = _due < _today && _st IN {{ "פעיל", "באפיון" }}
        VAR _col = {status_color_switch("_st")}
        VAR _l = DIVIDE ( INT ( _s - _rs ), _span ) * 100
        VAR _w = MAX ( DIVIDE ( INT ( _due - _s ), _span ) * 100, 0.8 )
        VAR _ttl = SUBSTITUTE ( {C("כותרת")}, "'", "’" )
        VAR _own = IF ( {C("בעלים")} = "", "לא שויך", {C("בעלים")} )
        RETURN
            "<div style='display:flex;align-items:center;gap:12px;height:28px'>"
                & "<div title='" & _ttl & "' style='width:270px;flex:none;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & _ttl & "</div>"
                & "<div style='width:116px;flex:none;font-size:11px;color:{FG2};white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & _own & "</div>"
                & "<div style='flex:1;position:relative;height:28px;direction:ltr'>" & _grid
                    & "<div style='position:absolute;top:7px;height:14px;border-radius:7px;left:" & FORMAT ( _l, "0.00" ) & "%;width:" & FORMAT ( _w, "0.00" ) & "%;background:" & _col
                    & IF ( _late, ";box-shadow:0 0 0 2px @@bad@@", "" ) & "'></div>"
                & "</div>"
                & "<div style='width:100px;flex:none;font-size:12px;text-align:@@end@@;direction:ltr;unicode-bidi:isolate;"
                    & IF ( _late, "color:@@bad@@;font-weight:700", "color:@@fg@@" ) & "'>" & FORMAT ( _due, "dd/MM/yyyy" ) & "</div>"
            & "</div>",
        "",
        {C("מועד יעד")}, ASC,
        {C("מזהה")}, ASC
    )
VAR _head =
    "<div style='display:flex;align-items:flex-start;justify-content:space-between;gap:12px'>"
        & "<div><div style='font-size:16px;font-weight:700'>לוח זמנים · פרויקטים עם מועד יעד</div>"
        & "<div style='font-size:12px;color:{FG2}'>" & LRI & _cnt & PDI & " מתוך " & LRI & [# פרויקטים] & PDI & " פרויקטים הוגדרו עם תאריכים · ציר הזמן נקרא משמאל לימין</div></div>"
        & "<div style='display:flex;flex-wrap:wrap;gap:4px 10px;font-size:11px;color:{FG2};justify-content:flex-end;align-items:center'>{legend_html()}"
        & "<span style='display:inline-flex;align-items:center;gap:4px'><span style='width:2px;height:10px;background:@@bad@@'></span>היום</span>"
        & "<span style='display:inline-flex;align-items:center;gap:4px'><span style='width:12px;height:8px;border-radius:4px;box-shadow:0 0 0 2px @@bad@@'></span>חלף המועד</span></div>"
    & "</div>"
RETURN
§TL§""".replace("§TL§", _tl_return()), "HTML")
# ---------------------------------------------------------------- right filter panel
slots = "".join(
    f"<div style='height:80px;flex:none;box-sizing:border-box'>"
    f"<div style='height:24px;font-size:13px;font-weight:700;line-height:22px'>{lbl}</div>"
    f"<div style='height:40px'></div></div>"
    for lbl in ["סטטוס", "מחלקה", "בעלים", "סוג פרויקט"])

FP_HEAD = f"""<div style='height:64px;flex:none;box-sizing:border-box;padding-top:16px'>"
            & "<div style='font-size:18px;font-weight:700;line-height:24px'>סינון</div>"
            & "<div style='font-size:12px;color:{FG2};line-height:18px'>הבחירה מסננת את כל הדף</div>"
        & "</div>"""
FP_MIX = mix_block("TRUE ()")   # the tall panel shows what the selection is made of
add("HTML Filter Panel", ISO + f"""
VAR _recent = TOPN ( 3, {T}, {C("מזהה")}, DESC )   -- 3 recent + the selection mix fill the tall panel
VAR _items =
    CONCATENATEX (
        _recent,
        VAR _st = {C("סטטוס")}
        VAR _d = {C("תיאור")}
        VAR _dd = IF ( LEN ( _d ) > 72, LEFT ( _d, 70 ) & "…", _d )
        RETURN
            "<div style='padding:10px 0;border-bottom:1px solid @@divider@@'>"
                & "<div style='display:flex;align-items:center;justify-content:space-between;gap:8px'>"
                    & "<span style='font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {C("כותרת")} & "</span>"
                    & "<span style='flex:none;padding:1px 8px;border-radius:999px;font-size:11px;background:" & {status_bg_switch("_st")} & ";color:" & {status_text_switch("_st")} & "'>" & {status_name_switch("_st")} & "</span>"
                & "</div>"
                & "<div style='font-size:11px;color:{FG2};margin-top:2px'>" & IF ( {C("בעלים")} = "", "לא שויך", {C("בעלים")} ) & "</div>"
                & IF ( _dd <> "", "<div style='font-size:11px;color:@@fg3@@;line-height:1.45;margin-top:4px'>" & _dd & "</div>" )
            & "</div>",
        "",
        {C("מזהה")}, DESC
    )
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:0 16px 16px 16px;display:flex;flex-direction:column'>"
        & "{FP_HEAD}"
        & "{slots}"
        & "<div style='margin-top:8px;border-top:1px solid @@border@@;padding-top:14px'>"
            & "<div style='font-size:14px;font-weight:700'>נוספו לאחרונה</div>"
            & _items
        & "</div>"
{FP_MIX}
    & "</div>\"""", "HTML")


# ---------------------------------------------------------------- layout (canvas px, RTL reading order)
# page 1920x1080, margin 32, gutter 16, panel 296 docked right (x=1592), content 32..1576
# header 24-96 | KPI 112-272 | middle 288-672 | bottom 688-1048 (=1080-32)
LAYOUT = [
    # name,               measure,              x,    y,   w,    h
    ("hcHeader",          "HTML Header",        32,   24,  1856, 72),
    ("hcFilterPanel",     "HTML Filter Panel",  1592, 112, 296,  936),
    ("hcKpiTotal",        "HTML KPI סהכ",       1280, 112, 296,  160),
    ("hcKpiActive",       "HTML KPI פעילים",    968,  112, 296,  160),
    ("hcKpiSpec",         "HTML KPI באפיון",    656,  112, 296,  160),
    ("hcKpiMaint",        "HTML KPI בתחזוקה",   344,  112, 296,  160),
    ("hcKpiDue",          "HTML KPI מועדים",    32,   112, 296,  160),
    ("hcStatusFlow",      "HTML Status Flow",   1080, 288, 496,  384),
    ("hcOwners",          "HTML Owners",        544,  288, 520,  384),
    ("hcDepartments",     "HTML Departments",   32,   288, 496,  384),
    ("hcTimeline",        "HTML Timeline",      560,  688, 1016, 360),
    ("hcTypeDonut",       "HTML Type Donut",    32,   688, 512,  360),
]

# colorful palettes: one full-page HTML layer under everything paints the gradient
# (Secure-safe CSS, no image resource); it is first in LAYOUT so it gets the lowest z.
if P["bg_layer"] == "1":
    add("HTML Background", '''"<div style='height:100vh;background:linear-gradient(135deg,@@bg_from@@ 0%,@@bg_mid@@ 55%,@@bg_to@@ 100%)'></div>"''', "HTML")
    LAYOUT.insert(0, ("hcBackground", "HTML Background", 0, 0, 1920, 1080))
# native dropdown slicers sit under the panel's labels: y = 112 + 64 + 24 + 80*i
SLICERS = [
    ("slStatus", "סטטוס", 1608, 200, 264, 40),
    ("slDept",   "מחלקה", 1608, 280, 264, 40),
    ("slOwner",  "בעלים", 1608, 360, 264, 40),
    ("slType",   "סוג",   1608, 440, 264, 40),
]


# LTR: mirror every visual horizontally (filter panel docks left, reading flow starts left).
# Coordinates are authored for RTL; x' = page width - x - w keeps every gap and alignment.
PAGE_W = 1920
if DIR == "ltr":
    LAYOUT[:] = [(n, m, PAGE_W - x - w, y, w, h) for n, m, x, y, w, h in LAYOUT]
    SLICERS[:] = [(n, c, PAGE_W - x - w, y, w, h) for n, c, x, y, w, h in SLICERS]
