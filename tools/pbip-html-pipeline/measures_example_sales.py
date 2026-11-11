# -*- coding: utf-8 -*-
"""Example 2 - Sales overview on invented data (make_sales_data.py), English, left-to-right.
A whole dashboard from the kit's builders only: kpi_card (icons), treemap_rows, heat_matrix, small_multiples,
data_table, lift_bars + an HTML filter panel over native slicers - everything except the slicers is HTML Content.
Model: one table (pipeline.json "table") with OrderID, OrderDate, Region, Category, Product, Channel, Rep, Units,
Amount, Discount, Status. Copy to measures.py to use it."""
import os as _os, re as _re
_os.environ.setdefault("DASH_DIR", "ltr")
_os.environ.setdefault("DASH_LANG", "en")
if not _os.environ.get("DASH_STYLE"):   # not ported to styles.py roles yet: legacy palettes unless a style is asked for
    _os.environ.setdefault("DASH_PALETTE", "vivid")
from palette import P, resolve
import components as K
from config import TABLE

DIR, LANG = _os.environ["DASH_DIR"], _os.environ["DASH_LANG"]
assert DIR in ("ltr", "rtl"), "DASH_DIR must be ltr or rtl"
DIR_TOKENS = {"dir": DIR, "lang": LANG, "locale": {"he": "he-IL"}.get(LANG, "en-US"),
              **({"start": "left", "end": "right", "fwd_arrow": "&#9654;"} if DIR == "ltr" else
                 {"start": "right", "end": "left", "fwd_arrow": "&#9664;"})}
T = f"'{TABLE}'"
C = lambda c: f"{T}[{c}]"
CARD, FG2, ISO = K.CARD, "@@fg2@@", K.ISO

M = {}
FONT_SCALE = {10: 13, 11: 14, 12: 15, 13: 16, 14: 17, 16: 20, 18: 22, 22: 26, 24: 30, 30: 36, 40: 50}


def _resolve_dir(text):
    for k, v in DIR_TOKENS.items():
        text = text.replace(f"@@{k}@@", v)
    return text


def add(name, expr, folder, fmt=None):
    expr = _re.sub(r"font-size:(\d+)px", lambda m: f"font-size:{FONT_SCALE.get(int(m.group(1)), int(m.group(1)))}px", expr.strip())
    M[name] = dict(expr=resolve(_resolve_dir(expr)), folder=folder, fmt=fmt)


# ---------------------------------------------------------------- base measures
add("Revenue", f"SUM ( {C('Amount')} )", "Measures", "#,0")
add("Orders", f"COUNTROWS ( {T} )", "Measures", "#,0")
add("Total units", f"SUM ( {C('Units')} )", "Measures", "#,0")
add("Avg order value", "DIVIDE ( [Revenue], [Orders] )", "Measures", "#,0")
add("Returns", f'CALCULATE ( [Orders], KEEPFILTERS ( {C("Status")} = "Returned" ) )', "Measures", "#,0")
add("Return rate", "DIVIDE ( [Returns], [Orders] )", "Measures", "0.0%")
add("Revenue 30d", f"""
VAR _end = CALCULATE ( MAX ( {C('OrderDate')} ), ALLSELECTED ( {T} ) )
RETURN CALCULATE ( [Revenue], KEEPFILTERS ( {C('OrderDate')} > _end - 30 ) )""", "Measures", "#,0")
add("Revenue prev 30d", f"""
VAR _end = CALCULATE ( MAX ( {C('OrderDate')} ), ALLSELECTED ( {T} ) )
RETURN CALCULATE ( [Revenue], KEEPFILTERS ( {C('OrderDate')} > _end - 60 && {C('OrderDate')} <= _end - 30 ) )""", "Measures", "#,0")

# ---------------------------------------------------------------- header
add("HTML Header", ISO + f"""
VAR _n = [Orders] + 0
VAR _from = MIN ( {C('OrderDate')} )
VAR _to = MAX ( {C('OrderDate')} )
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:0 24px;display:flex;align-items:center;justify-content:space-between;gap:16px'>"
        & "<div style='min-width:0'><div style='font-size:22px;font-weight:700;white-space:nowrap'>Sales overview</div>"
        & "<div style='font-size:12px;color:{FG2};white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>Invented sample data · "
        & IF ( _n = 0, "no orders in the selection", FORMAT ( _from, "mmm yyyy" ) & " – " & FORMAT ( _to, "mmm yyyy" ) & " · " & FORMAT ( _n, "#,0" ) & " orders" ) & "</div></div>"
    & "</div>\"""", "HTML")


# ---------------------------------------------------------------- KPI cards (filled with a categorical color)
FILLED = P.get("kpi_filled") == "1"   # colorful palettes: deep filled cards; light palettes: light cards


def kpi(name, title, value, fmt, icon, cat, sub):
    add(name, K.kpi_card(title, value, fmt, icon, sub, cat=cat, filled=FILLED), "HTML")


kpi("HTML KPI Revenue", "Revenue", "[Revenue]", "$#,0", "money", "cat1",
    '''VAR _c = [Revenue 30d] VAR _p = [Revenue prev 30d] RETURN IF ( ISBLANK ( _p ), "No prior 30 days", "Last 30 days " & FORMAT ( DIVIDE ( _c - _p, _p ), "+0%;-0%;0%" ) & " vs prior 30" )''')
kpi("HTML KPI Orders", "Orders", "[Orders]", "#,0", "cart", "cat2", '"Units " & FORMAT ( [Total units] + 0, "#,0" )')
kpi("HTML KPI AOV", "Avg order value", "[Avg order value]", "$#,0", "tag", "cat3",
    f'LRI & FORMAT ( DISTINCTCOUNT ( {C("Product")} ) + 0, "0" ) & PDI & " products · " & LRI & FORMAT ( DISTINCTCOUNT ( {C("Region")} ) + 0, "0" ) & PDI & " regions"')
kpi("HTML KPI Returns", "Return rate", "[Return rate]", "0.0%", "return", "cat4", '"Returned orders " & FORMAT ( [Returns] + 0, "#,0" )')

# ---------------------------------------------------------------- filter panel (labels only; native slicers sit under them)
FILTERS = ["Region", "Category", "Channel"]
slots = "".join(f"<div style='height:80px;flex:none;box-sizing:border-box'><div style='height:24px;font-size:13px;font-weight:600'>{f}</div></div>" for f in FILTERS)


def _mix(col, title):
    """share of orders per value of `col` in the current selection: label, share bar, %; rows stretch to fill"""
    color = K._catcolor(T, col, C(col))
    return (f'"<div style=\'flex:1;min-height:0;display:flex;flex-direction:column;gap:4px\'>'
            f'<div style=\'flex:none;font-size:13px;font-weight:700;margin-top:6px\'>{title}</div>" & '
            f'CONCATENATEX ( VALUES ( {C(col)} ), VAR _s = DIVIDE ( [Orders], CALCULATE ( [Orders], ALLSELECTED ( {C(col)} ) ) ) RETURN '
            f'"<div style=\'flex:1 1 0;min-height:24px;max-height:52px;display:flex;align-items:center;gap:8px\'>'
            f'<div style=\'width:92px;flex:none;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis\'>" & {C(col)} & "</div>'
            f'<div style=\'flex:1;height:10px;border-radius:5px;background:@@track@@;overflow:hidden;display:flex\'>'
            f'<div style=\'flex:none;width:" & FORMAT ( _s * 100, "0.0" ) & "%;background:" & {color} & "\'></div></div>'
            f'<div style=\'width:44px;flex:none;font-size:12px;font-weight:700;text-align:@@end@@;direction:ltr;unicode-bidi:isolate\'>" & FORMAT ( _s, "0%" ) & "</div></div>", '
            f'"", [Orders], DESC, {C(col)}, ASC ) & "</div>"')


# below the slicers the panel shows what the selection is made of, so the tall panel is not an empty column
add("HTML Filter Panel", f"""
"<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:16px;display:flex;flex-direction:column'>"
    & "<div style='height:64px;flex:none'><div style='font-size:16px;font-weight:700'>Filters</div>"
    & "<div style='font-size:12px;color:{FG2}'>Every selection filters the page</div></div>"
    & "{slots}"
    & "<div style='flex:1;min-height:0;display:flex;flex-direction:column;gap:8px;border-top:1px solid @@border@@;padding-top:8px'>"
        & "<div style='flex:none;font-size:14px;font-weight:700'>In this selection</div>"
        & {_mix("Status", "Order status")}
        & {_mix("Channel", "Channel")}
    & "</div>"
& "</div>\"""", "HTML")

# ---------------------------------------------------------------- charts and table from the kit's builders
add("HTML Products", K.treemap_rows(T, "Product", "[Revenue]", "Revenue by product", "Top 6 products, tile area proportional to revenue",
                                   top=6, colors="category"), "HTML")
add("HTML Region Mix", K.heat_matrix(T, "Region", "Category", "[Orders]", "Orders: region × category",
                                     "Darker = more orders"), "HTML")
add("HTML Reps", K.accent(K.data_table(
    T, "Rep",
    [{"label": "Revenue", "value": "[Revenue]", "kind": "bar", "width": "1.5fr", "color": "cat1", "fmt": "$#,0", "total": "[Revenue]"},
     {"label": "Orders", "value": "[Orders]", "kind": "number", "width": "64px", "total": "[Orders]"},
     {"label": "AOV", "value": "[Avg order value]", "kind": "number", "width": "72px", "fmt": "$#,0", "total": "[Avg order value]"},
     {"label": "Returns", "value": "[Return rate]", "kind": "percent", "width": "72px", "fmt": "0.0%", "total": "[Return rate]"}],
    "Sales reps", "Sorted by revenue", sort_by="[Revenue]", top=6, key_label="Rep", totals="Total",
    header_accent="cat1", more_label="and {n} more reps", blank_label="Unassigned",
    tip_value='FORMAT ( [@s], "$#,0" )'), "cat1"), "HTML")
add("HTML Returns Lift", K.lift_bars(T, "Product", f'{C("Status")} = "Returned"', "Where returns concentrate",
                                     "Return share vs. the overall rate", top=7, colors="category"), "HTML")
add("HTML Region Trend", K.small_multiples(T, "Region", "OrderDate", "[Orders]", "Orders by region",
                                           "Last 6 months, shared scale", top=6, colors="category"), "HTML")
add("HTML Background", '''"<div style='height:100vh;background:linear-gradient(135deg,@@bg_from@@ 0%,@@bg_mid@@ 55%,@@bg_to@@ 100%)'></div>"''', "HTML")

# ---------------------------------------------------------------- layout (LTR authored; 1920x1080, margin 32, gutter 16)
# header 80px: at 72 the accent style's top bar pushes the title 1px past the safe edge (FIT FAIL)
# filter panel docked left (32..328); content 344..1888 = 1544 wide
LAYOUT = [
    ("hcBackground",   "HTML Background",    0,    0,   1920, 1080),
    ("hcHeader",       "HTML Header",        32,   24,  1856, 80),
    ("hcFilterPanel",  "HTML Filter Panel",  32,   120, 296,  928),
    ("hcKpiRevenue",   "HTML KPI Revenue",   344,  120, 374,  160),
    ("hcKpiOrders",    "HTML KPI Orders",    734,  120, 374,  160),
    ("hcKpiAov",       "HTML KPI AOV",       1124, 120, 374,  160),
    ("hcKpiReturns",   "HTML KPI Returns",   1514, 120, 374,  160),
    ("hcProducts",     "HTML Products",      344,  296, 504,  380),
    ("hcRegionMix",    "HTML Region Mix",    864,  296, 504,  380),
    ("hcRegionTrend",  "HTML Region Trend",  1384, 296, 504,  380),
    ("hcReps",         "HTML Reps",          344,  692, 764,  356),
    ("hcReturnsLift",  "HTML Returns Lift",   1124, 692, 764,  356),
]
if P.get("bg_layer") != "1":
    LAYOUT.pop(0)
    M.pop("HTML Background")
# slicer y = panel top 120 + title 64 + i*80 + label 24 (+16 panel padding)
SLICERS = [(f"sl{f}", f, 48, 120 + 16 + 64 + 24 + 80 * i, 264, 40) for i, f in enumerate(FILTERS)]

# RTL: mirror the LTR-authored layout (x' = page width - x - w); the filter panel docks right
PAGE_W, PAGE_H = 1920, 1080
if DIR == "rtl":
    LAYOUT[:] = [(n, m, PAGE_W - x - w, y, w, h) for n, m, x, y, w, h in LAYOUT]
    SLICERS[:] = [(n, c, PAGE_W - x - w, y, w, h) for n, c, x, y, w, h in SLICERS]
