# -*- coding: utf-8 -*-
"""Parameterized HTML Content card builders on top of the pipeline's token / font-scale / direction system.

Each builder returns a DAX expression (string) for one card. Pass it to `add(name, expr, folder)` from
your measures.py so colors (@@tokens@@), font sizes, direction and language are resolved like every
other card. Builders take model names as arguments - nothing about a specific model is hardcoded.

Conventions (see reference/design-system.md):
- root = CARD (height:100vh, overflow hidden, direction tokens), fonts authored on the base scale
  (11/12/13/16 -> 14/15/16/20 after FONT_SCALE), numbers isolated with LRI/PDI, colors only as tokens
- every card has an empty state and fixed row heights; lists are capped by top/max_* arguments (pick the
  cap from the card height; the cards do not add an "and N more" line - add one in your layout if needed)

Card sizes the builders are designed for (fit-checked): 520-640 wide x 320-400 high (KPI cards: 280-400 x 140-180).
"""
import re

FONT = "font-family:Segoe UI,Arial,sans-serif"
CARD = ("box-sizing:border-box;height:100vh;overflow:hidden;background:@@surface@@;"
        "border-radius:12px;box-shadow:0 1px 3px @@shadow@@;line-height:1.35;"
        "direction:@@dir@@;text-align:@@start@@;" + FONT + ";color:@@fg@@")
try:   # a colorful style (styles.py) gives every builder the same card material as the KPI cards
    import styles as _S
    if _S.ACTIVE:
        CARD = _S.CARD
except ImportError:
    _S = None
FG2 = "@@fg2@@"
ISO = "VAR LRI = UNICHAR ( 8294 )\nVAR PDI = UNICHAR ( 8297 )\n"
SERIES = ["@@primary@@", "@@maint@@", "@@design@@", "@@series4@@", "@@done@@", "@@series3@@"]


def _t(text):
    """caller text -> safe inside a DAX string literal and HTML: & < > escaped, " doubled"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', '""')


def _head(title, subtitle):
    title, subtitle = _t(title), _t(subtitle)
    return (f"\"<div style='flex:none'><div style='font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{title}</div>"
            f"<div style='font-size:12px;color:{FG2};white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{subtitle}</div></div>\"")


def _wrap(title, subtitle, body, empty_text, is_empty="_n = 0", motion=False):
    empty_text = _t(empty_text)
    return f"""
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:16px 20px;display:flex;flex-direction:column;gap:10px'>{_mstyle(motion)}"
        & {_head(title, subtitle)}
        & IF ( {is_empty},
            "<div data-fill='free' style='flex:1;display:flex;align-items:center;justify-content:center;font-size:13px;color:{FG2}'>{empty_text}</div>",
            {body} )
    & "</div>\""""


def _c(table, col):
    """column reference: `col` of `table`, or `col` itself when it is already a full reference such as 'Products'[Name].
    So a builder can break a fact table's measure down by a dimension column (star schema) - see build-workflow §0."""
    return col if "[" in col else f"{table}[{col}]"


def _cat(ref, blank_label):
    """category value for display: blank -> blank_label, apostrophes made safe for attributes"""
    return f'IF ( {ref} = "", "{_t(blank_label)}", SUBSTITUTE ( {ref}, "\'", "’" ) )'


def _catcolor(table, col, ref, suffix=""):
    """Stable color per category value: alphabetical rank over ALL values of the column -> cat1..cat6.
    The same value gets the same color in every card and under any filter. suffix: "", "_soft", "_text"."""
    opts = ", ".join(f'{i}, "@@cat{i + 1}{suffix}@@"' for i in range(5))
    return f'SWITCH ( MOD ( RANKX ( ALL ( {_c(table, col)} ), {_c(table, col)}, {ref}, ASC, Dense ) - 1, 6 ), {opts}, "@@cat6{suffix}@@" )'


def _catstyle(table, col, ref, tmpl):
    """One RANKX, several tokens: tmpl uses {c} for the color base (cat1..cat6),
    e.g. "background:@@{c}_soft@@;color:@@{c}_text@@". Returns a parenthesized DAX text expression."""
    opts = ", ".join(f'{i}, "{tmpl.format(c=f"cat{i + 1}")}"' for i in range(5))
    return (f'( VAR _ci = MOD ( RANKX ( ALL ( {_c(table, col)} ), {_c(table, col)}, {ref}, ASC, Dense ) - 1, 6 ) '
            f'RETURN SWITCH ( _ci, {opts}, "{tmpl.format(c="cat6")}" ) )')


def _mode(colors, default):
    """color modes: the builder's default ("single" or "status") or "category"; anything else is an error"""
    if colors not in (default, "category"):
        raise ValueError(f"colors must be {default!r} or 'category', got {colors!r}")
    return colors == "category"


def accent(expr, cat="cat1"):   # legacy palettes; with a style the card's role draws its accent
    """Give any builder's card a colored top band (cat1..cat6 or any color token name)."""
    if _S is not None and _S.ACTIVE:
        return expr   # the style already colors every card through its role (bar / tint / chip)
    a = f"style='{CARD};padding:16px 20px;"
    assert expr.count(a) == 1, "accent(): card root not found"
    return expr.replace(a, f"style='{CARD};border-top:5px solid @@{cat}@@;padding:13px 20px 16px;")


def _fmt(expr):
    """compact number: 1.2M / 3.4K / 120, isolated for bidi"""
    return (f"LRI & IF ( ABS ( {expr} ) >= 1000000, FORMAT ( {expr} / 1000000, \"0.0\" ) & \"M\", "
            f"IF ( ABS ( {expr} ) >= 1000, FORMAT ( {expr} / 1000, \"0.0\" ) & \"K\", FORMAT ( {expr}, \"#,0\" ) ) ) & PDI")


# ---------------------------------------------------------------- motion (opt-in, see skills/motion/SKILL.md)
# Every builder takes motion = False | True | k, and alert = None | "<DAX condition>".
#   motion=True  an entrance on every render (page open, filter change, Refresh): bars grow from the axis (no overshoot -
#                it would misstate values), tiles/cells pop, rows slide in, KPI digits roll (from prev= when given, so
#                the roll shows the change).
#   alert="..."  a DAX condition in the builder's row context; items that break it pulse a red ring twice (4.8 s, then
#                stop - WCAG 2.2.2 needs a pause control for motion longer than 5 s) on every render. Nothing else
#                loops: decorative motion (sheens, "breathing", grow-in for its own sake) is left out on purpose.
#   k > 1        slows every animation k times (only to check frames in Desktop). False: output byte-identical.
# CSS keyframes only (Secure edition). Rules and sources: skills/motion/SKILL.md.
# Individual transform properties (scale, translate) are used, so an element's own inline transform keeps working.
_STAGGER = "".join(f".mo-st>:nth-child({i}){{--mo-i:{i - 1}}}" for i in range(2, 25))
MOTION_CSS = (
    _STAGGER
    + ".mo-gy,.mo-gx,.mo-pop,.mo-in{animation-duration:calc(var(--mo-k,1)*.55s);animation-fill-mode:both;"
      "animation-timing-function:cubic-bezier(.2,.8,.2,1);animation-delay:calc(var(--mo-k,1)*var(--mo-i,0)*55ms)}"
    + ".mo-gy{transform-origin:50% 100%;animation-name:mo-gy}"
    + ".mo-gx{transform-origin:0 50%;animation-name:mo-gx}[dir=rtl] .mo-gx{transform-origin:100% 50%}"
    + ".mo-pop{animation-name:mo-pop;animation-timing-function:cubic-bezier(.34,1.56,.64,1)}"
    + ".mo-in{animation-name:mo-in}"
    + ".mo-late{animation-delay:calc(var(--mo-k,1)*.65s)}"
    + ".mo-od{display:inline-block;height:1em;overflow:hidden;vertical-align:top}"
    + ".mo-os{display:block;animation:mo-roll calc(var(--mo-k,1)*.9s) cubic-bezier(.2,.8,.2,1) both}"
    + ".mo-os i{display:block;height:1em;font-style:normal}"
    + "@keyframes mo-gy{from{scale:1 0}}@keyframes mo-gx{from{scale:0 1}}"
    + "@keyframes mo-pop{from{opacity:0;scale:.6}}@keyframes mo-in{from{opacity:0;translate:0 8px}}"
    + "@keyframes mo-roll{from{translate:0 var(--mo-from,0em)}}"
    + ".mo-gw{animation:mo-gw calc(var(--mo-k,1)*.8s) cubic-bezier(.2,.8,.2,1) both;animation-delay:calc(var(--mo-k,1)*var(--mo-i,0)*55ms)}"
    + "@keyframes mo-gw{from{width:var(--mo-w0)}}"
)


_K = "var(--mo-k,1)"
ALERT_CSS = (
    # an alerted element keeps its entrance and adds the ring: two animations in one list, the ring runs twice
    "".join(
        f".{e}.mo-focus{{animation-name:{e},{ring};animation-duration:calc({_K}*.55s),calc({_K}*2.4s);"
        f"animation-iteration-count:1,2;animation-timing-function:{tf},ease-out;animation-fill-mode:both,none;"
        f"animation-delay:calc({_K}*var(--mo-i,0)*55ms),calc({_K}*.8s)}}"
        for e, ring, tf in (("mo-pop", "mo-ring", "cubic-bezier(.34,1.56,.64,1)"), ("mo-in", "mo-ring", "cubic-bezier(.2,.8,.2,1)"),
                            ("mo-gy", "mo-ringin", "cubic-bezier(.2,.8,.2,1)"), ("mo-gx", "mo-ringin", "cubic-bezier(.2,.8,.2,1)"),
                            ("mo-gw", "mo-ringin", "cubic-bezier(.2,.8,.2,1)")))
    + f".mo-late.mo-focus{{animation-delay:calc({_K}*.65s),calc({_K}*1.2s)}}"
    # outer ring for chips, cells, rows; inner ring for bars (their track clips anything outside)
    "@keyframes mo-ring{0%{box-shadow:0 0 0 0 color-mix(in srgb,@@bad@@ 55%,transparent)}70%,100%{box-shadow:0 0 0 9px color-mix(in srgb,@@bad@@ 0%,transparent)}}"
    "@keyframes mo-ringin{0%,100%{box-shadow:inset 0 0 0 0 color-mix(in srgb,@@bad@@ 0%,transparent)}40%{box-shadow:inset 0 0 0 3px @@bad@@}}"
    # data freshness: a fresh dot pulses twice; a stale one stays still
    f".mo-fd{{animation:mo-fd calc({_K}*1.2s) ease-in-out 2}}@keyframes mo-fd{{50%{{opacity:.3;scale:.6}}}}"
)


def _m(motion, cls):
    """class attribute for a motion hook - empty when motion is off (byte-identical output)"""
    return f" class='{cls}'" if motion else ""


def _mf(motion, cls, alert):
    """like _m, plus 'mo-focus' (the alert ring) where the caller's DAX condition holds"""
    if not motion:
        return ""
    if not alert:
        return f" class='{cls}'"
    cond = alert
    return f" class='{cls}\" & IF ( {cond}, \" mo-focus\", \"\" ) & \"'"


def _mstyle(motion):
    """the motion <style> block for a card root - empty when motion is off"""
    if not motion:
        return ""
    k = 1 if motion is True else float(motion)
    return ("<style>" + MOTION_CSS + ALERT_CSS
            + ("" if k == 1 else f":root{{--mo-k:{k:g}}}") + "</style>")



def mix(table, col, value, title, top=6):
    """A 'what the selection is made of' block for a builder's fill=: share of `value` per value of `col` in the
    current selection - label, share bar, %. Rows stretch (flex:1 1 0) so the block fills whatever the list leaves."""
    ref = _c(table, col)
    color = _catcolor(table, col, ref)
    return (f'"<div style=\'flex:none;font-size:12px;font-weight:700\'>{_t(title)}</div>" & '
            f'CONCATENATEX ( TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {ref} ), "@mx", {value} + 0 ), [@mx] > 0 ), [@mx], DESC, {ref}, ASC ), '
            f'VAR _mxs = DIVIDE ( [@mx], CALCULATE ( {value}, ALLSELECTED ( {ref} ) ) ) RETURN '
            f'"<div style=\'flex:1 1 0;min-height:20px;display:flex;align-items:center;gap:8px\'>'
            f'<div style=\'width:96px;flex:none;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis\'>" & {_cat(ref, "-")} & "</div>'
            f'<div style=\'flex:1;height:8px;border-radius:4px;background:@@track@@;overflow:hidden;display:flex\'>'
            f'<div style=\'flex:none;width:" & FORMAT ( _mxs * 100, "0.0" ) & "%;background:" & {color} & "\'></div></div>'
            f'<div style=\'width:44px;flex:none;font-size:12px;font-weight:700;text-align:@@end@@;direction:ltr;unicode-bidi:isolate\'>" & FORMAT ( _mxs, "0%" ) & "</div></div>", '
            f'"", [@mx], DESC, {ref}, ASC )')


def _fill(fill, short):
    """the fill block, shown when the list is short (`short`: a DAX condition on _n); empty when fill is None"""
    if not fill:
        return ""
    return (f' & IF ( {short}, "<div style=\'flex:1 1 0;min-height:0;display:flex;flex-direction:column;gap:2px;'
            f'border-top:1px solid @@border@@;padding-top:6px\'>" & {fill} & "</div>" )')


def _stretched(expr, swaps):
    """stretch=True: apply the (old, new) swaps that turn fixed-height list rows into rows that grow to fill the
    card (design-system §2: flex:1 1 0 with a min and a max height). Each swap must match - a builder change that
    breaks one fails loudly instead of silently shipping fixed rows."""
    for old, new in swaps:
        assert old in expr, f"stretch: pattern not found: {old[:60]}"
        expr = expr.replace(old, new)
    return expr

# 1 --------------------------------------------------------------- waterfall
def waterfall(table, category, delta, title, subtitle, order=None, start=None, start_label="Start", end_label="End",
              empty_text="No data", blank_label="-", motion=False, alert=None):
    """Start bar, one floating bar per category (positive / negative), end bar. Reads in the page's direction.
    order: optional sort column (one value per category); default = category name."""
    s0 = start or "0"
    start_label, end_label = _t(start_label), _t(end_label)
    okey = f"CALCULATE ( MIN ( {_c(table, order)} ) )" if order else f"RANKX ( ALL ( {_c(table, category)} ), {_c(table, category)}, , ASC )"
    return ISO + f"""
VAR _start = {s0} + 0
VAR _steps = FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, category)} ), "@d", {delta} + 0, "@o", {okey} ), [@d] <> 0 )
VAR _cum = ADDCOLUMNS ( _steps, "@b", _start + SUMX ( FILTER ( _steps, [@o] < EARLIER ( [@o] ) ), [@d] ) )
VAR _n = COUNTROWS ( _steps ) + 0
VAR _end = _start + SUMX ( _steps, [@d] )
VAR _hi = MAX ( MAX ( MAXX ( _cum, [@b] + MAX ( [@d], 0 ) ), _end ), _start )
VAR _lo = MIN ( MIN ( MINX ( _cum, [@b] + MIN ( [@d], 0 ) ), 0 ), _end )
VAR _rng = MAX ( _hi - _lo, 1 ) * 1.15   // headroom for value labels
VAR _H = 170
VAR _bar = ( lbl, v, b, col, sgn ) => BLANK ()
VAR _bars =
    CONCATENATEX ( _cum,
        VAR _v = [@d] VAR _b = [@b]
        VAR _top = MAX ( _b, _b + _v ) VAR _bot = MIN ( _b, _b + _v )
        VAR _col = IF ( _v >= 0, "@@done@@", "@@bad@@" )
        RETURN
            "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:stretch;gap:4px'>"
            & "<div style='position:relative;height:" & _H & "px'>"
            & "<div{_mf(motion, 'mo-gy', alert)} style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:" & _col
            & ";bottom:" & FORMAT ( DIVIDE ( _bot - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _v ), _rng ) * _H, 2 ), "0.0" ) & "px'></div>"
            & "<div{_m(motion, 'mo-in')} style='position:absolute;inset-inline-start:0;width:100%;text-align:center;font-size:11px;font-weight:700;color:" & _col
            & ";bottom:" & FORMAT ( MIN ( DIVIDE ( _top - _lo, _rng ) * _H + 2, _H - 16 ), "0.0" ) & "px'>" & LRI & IF ( _v >= 0, "+", "" ) & FORMAT ( _v, "#,0" ) & PDI & "</div></div>"
            & "<div style='height:18px;font-size:11px;color:{FG2};text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{_c(table, category)}", blank_label)} & "</div></div>",
        "", [@o], ASC )
VAR _total = ( lbl, v ) => BLANK ()
VAR _openBar =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:4px'><div style='position:relative;height:" & _H & "px'>"
    & "<div{_m(motion, 'mo-gy')} style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:@@muted@@;bottom:" & FORMAT ( DIVIDE ( MIN ( _start, 0 ) - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _start ), _rng ) * _H, 2 ), "0.0" ) & "px'></div></div>"
    & "<div style='height:18px;font-size:11px;font-weight:700;text-align:center'>{start_label} " & {_fmt('_start')} & "</div></div>"
VAR _closeBar =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:4px'><div style='position:relative;height:" & _H & "px'>"
    & "<div{_m(motion, 'mo-gy')} style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:@@primary@@;bottom:" & FORMAT ( DIVIDE ( MIN ( _end, 0 ) - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _end ), _rng ) * _H, 2 ), "0.0" ) & "px'></div></div>"
    & "<div style='height:18px;font-size:11px;font-weight:700;text-align:center'>{end_label} " & {_fmt('_end')} & "</div></div>"
""".replace("VAR _bar = ( lbl, v, b, col, sgn ) => BLANK ()\n", "").replace("VAR _total = ( lbl, v ) => BLANK ()\n", "") + _wrap(
        title, subtitle, f"\"<div{_m(motion, 'mo-st')} style='flex:1;display:flex;align-items:flex-end;gap:6px'>\" & _openBar & _bars & _closeBar & \"</div>\"", empty_text,
        motion=motion)


# 2 --------------------------------------------------------------- heat matrix
def heat_matrix(table, row_col, col_col, value, title, subtitle, max_rows=6, max_cols=6, empty_text="No data", blank_label="-",
                motion=False, alert=None, stretch=True, fill=None, short_when=2):
    """Category x category grid; cell color intensity = value / max. Top rows/cols by total.
    stretch  True (default): rows grow to fill the card (max 120px instead of 64px); False: the 1.0 fixed rows.
    fill     DAX text (e.g. mix(...)) shown under the grid when at most short_when rows have data."""
    out = ISO + f"""
VAR _rows = TOPN ( {max_rows}, ADDCOLUMNS ( VALUES ( {_c(table, row_col)} ), "@t", {value} + 0 ), [@t], DESC, {_c(table, row_col)}, ASC )
VAR _cols = TOPN ( {max_cols}, ADDCOLUMNS ( VALUES ( {_c(table, col_col)} ), "@t", {value} + 0 ), [@t], DESC, {_c(table, col_col)}, ASC )
VAR _n = COUNTROWS ( FILTER ( _rows, [@t] > 0 ) ) + 0
VAR _max = MAXX ( CROSSJOIN ( SELECTCOLUMNS ( _rows, "r", {_c(table, row_col)} ), SELECTCOLUMNS ( _cols, "c", {_c(table, col_col)} ) ),
    VAR _r = [r] VAR _c = [c] RETURN CALCULATE ( {value}, {_c(table, row_col)} = _r, {_c(table, col_col)} = _c ) + 0 )
VAR _hdr =
    "<div style='display:flex;gap:4px;height:22px;flex:none'><div style='width:120px;flex:none'></div>"
    & CONCATENATEX ( _cols, "<div style='flex:1 1 0;min-width:0;font-size:11px;color:{FG2};text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
        & {_cat(f"{_c(table, col_col)}", blank_label)} & "</div>", "", [@t], DESC ) & "</div>"
VAR _grid =
    CONCATENATEX ( _rows,
        VAR _r = {_c(table, row_col)}
        RETURN "<div style='display:flex;gap:3px;flex:1 1 0;min-height:26px;max-height:64px'>"
            & "<div style='width:120px;flex:none;align-self:center;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat("_r", blank_label)} & "</div>"
            & CONCATENATEX ( _cols,
                VAR _c = {_c(table, col_col)}
                VAR _v = CALCULATE ( {value}, {_c(table, row_col)} = _r, {_c(table, col_col)} = _c ) + 0
                VAR _a = DIVIDE ( _v, _max )
                RETURN "<div{_mf(motion, 'mo-pop', alert)} style='flex:1 1 0;min-width:0;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;"
                    & IF ( _v = 0, "background:@@track@@;color:@@fg2@@", IF ( _a > 0.5, "background:@@strong@@;color:@@on_accent@@", "background:@@primary_soft@@;color:@@primary_text@@" ) )
                    & "'>" & IF ( _v = 0, "", LRI & _v & PDI ) & "</div>",
                "", [@t], DESC )
            & "</div>",
        "", [@t], DESC )
""" + _wrap(title, subtitle, f"\"<div{_m(motion, 'mo-st')} style='flex:1;min-height:0;display:flex;flex-direction:column;gap:3px'>\" & _hdr & _grid{_fill(fill, f"_n <= {short_when}")} & \"</div>\"", empty_text,
             motion=motion)
    return _stretched(out, [("flex:1 1 0;min-height:26px;max-height:64px", "flex:1 1 0;min-height:26px;max-height:120px")]) if stretch else out


# 3 --------------------------------------------------------------- lift bars (key influencers, static)
def lift_bars(table, category, target_filter, title, subtitle, top=6, min_support=2, empty_text="No data", blank_label="-",
              colors="single", motion=False, alert=None, stretch=True, fill=None, short_when=3, fact=None):
    """For each category: share of rows meeting target_filter vs. the overall share (lift = x times).
    Categories with fewer than min_support rows and blank categories are left out (a 1-row category has a
    meaningless lift).
    stretch  True (default): rows grow to fill the card (28-56px instead of a fixed 28px); False: the 1.0 fixed rows.
    fill     DAX text (e.g. mix(...)) shown under the bars when at most short_when categories are listed.
    fact     the table whose rows are counted (default `table`); pass the fact table when `category` is a dimension column."""
    out = ISO + f"""
VAR _all = COUNTROWS ( {fact or table} ) + 0
VAR _hit = CALCULATE ( COUNTROWS ( {fact or table} ), {target_filter} ) + 0
VAR _base = DIVIDE ( _hit, _all )
VAR _cats = FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, category)} ),
    "@n", CALCULATE ( COUNTROWS ( {fact or table} ) ) + 0,
    "@h", CALCULATE ( COUNTROWS ( {fact or table} ), {target_filter} ) + 0 ), [@n] >= {min_support} && {_c(table, category)} <> "" )
VAR _lifted = ADDCOLUMNS ( _cats, "@l", DIVIDE ( DIVIDE ( [@h], [@n] ), _base ) )
VAR _top = TOPN ( {top}, _lifted, [@l], DESC, [@n], DESC, {_c(table, category)}, ASC )
VAR _n = COUNTROWS ( _top ) + 0
VAR _maxL = MAXX ( _top, [@l] )
VAR _body =
    CONCATENATEX ( _top,
        VAR _l = [@l]
        RETURN "<div style='display:flex;align-items:center;gap:10px;height:28px'>"
            & "<div style='width:130px;flex:none;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_c(table, category)} & "</div>"
            & "<div style='flex:1;height:14px;border-radius:7px;background:@@track@@;overflow:hidden;display:flex'>"
            & "<div{_mf(motion, 'mo-gx', alert)} style='flex:none;width:" & FORMAT ( DIVIDE ( _l, _maxL ) * 100, "0.0" ) & "%;background:" & {"IF ( _l >= 1, \"@@primary@@\", \"@@muted@@\" )" if not _mode(colors, "single") else _catcolor(table, category, f"{_c(table, category)}")} & "'></div></div>"
            & "<div style='width:64px;flex:none;font-size:13px;font-weight:700;text-align:@@end@@;direction:ltr;unicode-bidi:isolate'>" & FORMAT ( _l, "0.0" ) & "x</div>"
            & "</div>",
        "", [@l], DESC, [@n], DESC )
""" + _wrap(title, subtitle,
            f"\"<div style='font-size:12px;color:{FG2}'>\" & LRI & FORMAT ( _base, \"0%\" ) & PDI & \" = 1.0x</div><div{_m(motion, 'mo-st')} style='display:flex;flex-direction:column;gap:4px'>\" & _body{_fill(fill, f"_n <= {short_when}")} & \"</div>\"",
            empty_text, motion=motion)
    return _stretched(out, [("gap:10px;height:28px'", "gap:10px;flex:1 1 0;min-height:28px;max-height:56px'"),
                            ("style='display:flex;flex-direction:column;gap:4px'>\" & _body", "style='flex:1;min-height:0;display:flex;flex-direction:column;gap:4px'>\" & _body")]) if stretch else out


# 4 --------------------------------------------------------------- small multiples
def small_multiples(table, category, date_col, value, title, subtitle, top=6, months=6, cols=3, empty_text="No data",
                    blank_label="-", colors="single", motion=False, alert=None):   # blank categories are skipped here; blank_label kept for a uniform signature
    """One mini column chart per category over the last `months` months (by date_col), shared scale."""
    return ISO + f"""
VAR _endM = EOMONTH ( MAX ( {_c(table, date_col)} ), 0 )
VAR _cats = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, category)} ), "@t", {value} + 0 ), {_c(table, category)} <> "" && [@t] > 0 ), [@t], DESC, {_c(table, category)}, ASC )
VAR _n = IF ( ISBLANK ( _endM ), 0, COUNTROWS ( _cats ) + 0 )
VAR _grid = GENERATE ( SELECTCOLUMNS ( _cats, "cat", {_c(table, category)} ), GENERATESERIES ( 0, {months} - 1, 1 ) )
VAR _vals = ADDCOLUMNS ( _grid, "@v",
    VAR _c = [cat] VAR _m0 = EOMONTH ( _endM, -[Value] - 1 ) + 1 VAR _m1 = EOMONTH ( _endM, -[Value] )
    RETURN CALCULATE ( {value}, {_c(table, category)} = _c, {_c(table, date_col)} >= _m0, {_c(table, date_col)} <= _m1 ) + 0 )
VAR _max = MAX ( MAXX ( _vals, [@v] ), 1 )
VAR _panels =
    CONCATENATEX ( _cats,
        VAR _c = {_c(table, category)}
        RETURN "<div style='box-sizing:border-box;border:1px solid @@border@@;border-radius:8px;padding:5px 8px;display:flex;flex-direction:column;gap:2px;min-width:0;min-height:0;flex:1 1 calc(100% / {cols} - 8px)'>"
            & "<div style='display:flex;justify-content:space-between;gap:6px;font-size:12px'><span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & _c & "</span>"
            & "<b style='direction:ltr;unicode-bidi:isolate'>" & {_fmt('[@t]')} & "</b></div>"
            & "<div style='display:flex;align-items:flex-end;gap:3px;flex:1;min-height:34px;direction:ltr'>"
            & CONCATENATEX ( FILTER ( _vals, [cat] = _c ),
                "<div{_mf(motion, 'mo-gy', alert)} style='flex:1 1 0;border-radius:2px 2px 0 0;background:" & {"\"@@primary@@\"" if not _mode(colors, "single") else _catcolor(table, category, "_c")} & ";height:" & FORMAT ( MAX ( DIVIDE ( [@v], _max ) * 100, 5 ), "0" ) & "%;opacity:" & IF ( [@v] = 0, "0.25", "1" ) & "'></div>",
                "", [Value], DESC )
            & "</div></div>",
        "", [@t], DESC )
""" + _wrap(title, subtitle,
            f"\"<div{_m(motion, 'mo-st')} style='flex:1;min-height:0;display:flex;flex-wrap:wrap;align-content:stretch;gap:8px'>\" & _panels & \"</div><div style='font-size:12px;color:{FG2}'>\" & FORMAT ( EOMONTH ( _endM, -{months} ) + 1, \"MMM yyyy\", \"@@locale@@\" ) & \" - \" & FORMAT ( _endM, \"MMM yyyy\", \"@@locale@@\" ) & \"</div>\"",
            empty_text, motion=motion)


# 5 --------------------------------------------------------------- scatter / bubble
def scatter(table, category, x, y, size, title, subtitle, x_label, y_label, top=12, empty_text="No data", blank_label="-",
            colors="single", motion=False, alert=None):
    """Bubble per category: position x/y, area by size. x grows left-to-right in both directions (axis)."""
    x_label, y_label = _t(x_label), _t(y_label)
    return ISO + f"""
VAR _pts = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, category)} ), "@x", {x} + 0, "@y", {y} + 0, "@s", {size} + 0 ),
    {_c(table, category)} <> "" && [@s] > 0 ), [@s], DESC, {_c(table, category)}, ASC )
VAR _n = COUNTROWS ( _pts ) + 0
VAR _x0 = MIN ( MINX ( _pts, [@x] ), 0 ) VAR _x1 = MAX ( MAXX ( _pts, [@x] ), 0 ) VAR _xr = IF ( _x1 - _x0 = 0, 1, _x1 - _x0 )
VAR _y0 = MIN ( MINX ( _pts, [@y] ), 0 ) VAR _y1 = MAX ( MAXX ( _pts, [@y] ), 0 ) VAR _yr = IF ( _y1 - _y0 = 0, 1, _y1 - _y0 )
VAR _ms = MAXX ( _pts, [@s] )
VAR _dots =
    CONCATENATEX ( _pts,
        VAR _r = 4 + 9 * SQRT ( DIVIDE ( [@s], _ms ) )
        VAR _cx = 8 + 84 * DIVIDE ( [@x] - _x0, _xr )
        VAR _cy = 86 - 74 * DIVIDE ( [@y] - _y0, _yr )
        VAR _rk = RANKX ( _pts, [@s] + DIVIDE ( RANKX ( _pts, {_c(table, category)}, , DESC ), 1000 ), , DESC )
        VAR _lbl = _rk <= 5
        RETURN "<div{_mf(motion, 'mo-pop', alert)} title='" & SUBSTITUTE ( {_c(table, category)}, "'", "’" ) & "' style='position:absolute;transform:translate(-50%,-50%);border-radius:50%;opacity:.8;background:" & {"\"@@primary@@\"" if not _mode(colors, "single") else _catcolor(table, category, f"{_c(table, category)}")} & ";"
            & "left:" & FORMAT ( _cx, "0.0" ) & "%;top:" & FORMAT ( _cy, "0.0" ) & "%;width:" & FORMAT ( 2 * _r, "0" ) & "px;height:" & FORMAT ( 2 * _r, "0" ) & "px'></div>"
            & IF ( _lbl, "<div{_m(motion, 'mo-in')} style='position:absolute;font-size:11px;color:{FG2};white-space:nowrap;transform:translate(-50%,0);left:" & FORMAT ( _cx, "0.0" ) & "%;top:calc(" & FORMAT ( _cy, "0.0" ) & "% " & IF ( MOD ( _rk, 2 ) = 0, "- " & FORMAT ( _r + 18, "0" ), "+ " & FORMAT ( _r + 1, "0" ) ) & "px)'>"
            & LEFT ( {_cat(f"{_c(table, category)}", blank_label)}, 14 ) & "</div>" ),
        "" )
""" + _wrap(title, subtitle,
            f"\"<div style='flex:1;display:flex;flex-direction:column;gap:4px;min-height:0'>"
            f"<div{_m(motion, 'mo-st')} style='flex:1;position:relative;border-inline-start:1px solid @@border@@;border-bottom:1px solid @@border@@;direction:ltr;min-height:0'>\" & _dots & \"</div>"
            f"<div style='display:flex;justify-content:space-between;font-size:11px;color:{FG2};flex:none'><span>{y_label} ↑</span><span>{x_label} →</span></div></div>\"",
            empty_text, motion=motion)


# 6 --------------------------------------------------------------- treemap (two rows, proportional)
def treemap_rows(table, category, value, title, subtitle, top=8, empty_text="No data", blank_label="-", colors="status", motion=False, alert=None,
                 fill=None, short_when=2):
    """Approximate treemap: largest categories split over two rows, tile width proportional to value.
    colors: "status" (default, status-token cycle) or "category" (stable color per category value).
    One tile takes the whole area; fill (DAX text, e.g. mix(...)) is shown under the tiles when there are at most short_when."""
    TILE = 'SWITCH ( _i, 0, "background:@@primary_soft@@;color:@@primary_text@@;border-top:3px solid @@primary@@", 1, "background:@@maint_soft@@;color:@@maint_text@@;border-top:3px solid @@maint@@", 2, "background:@@design_soft@@;color:@@design_text@@;border-top:3px solid @@design@@", 3, "background:@@done_soft@@;color:@@done_text@@;border-top:3px solid @@done@@", 4, "background:@@bad_soft@@;color:@@fg@@;border-top:3px solid @@bad@@", "background:@@neutral_soft@@;color:@@fg@@;border-top:3px solid @@muted@@" )'
    tile = (_catstyle(table, category, f"{_c(table, category)}", "background:@@{c}_soft@@;color:@@{c}_text@@;border-top:3px solid @@{c}@@")
            if _mode(colors, "status") else TILE)
    return ISO + f"""
VAR _c = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, category)} ), "@v", {value} + 0 ), [@v] > 0 ), [@v], DESC, {_c(table, category)}, ASC )
VAR _n = COUNTROWS ( _c ) + 0
VAR _tot = SUMX ( _c, [@v] )
VAR _ranked = ADDCOLUMNS ( _c, "@k", RANKX ( _c, [@v], , DESC, Dense ) + DIVIDE ( RANKX ( _c, {_c(table, category)}, , ASC ), 1000 ) )
VAR _half = DIVIDE ( SUMX ( _c, [@v] ), 2 )
VAR _row1 = FILTER ( _ranked, SUMX ( FILTER ( _ranked, [@k] < EARLIER ( [@k] ) ), [@v] ) < _half )
VAR _row2 = EXCEPT ( _ranked, _row1 )
VAR _tiles = ( t ) => BLANK ()
VAR _r1 = CONCATENATEX ( _row1,
    VAR _i = MOD ( INT ( [@k] ) - 1, 6 )
    RETURN "<div{_mf(motion, 'mo-pop', alert)} style='flex:" & FORMAT ( MAX ( DIVIDE ( [@v], _tot ) * 1000, 1 ), "0" ) & " 1 0;min-width:0;border-radius:6px;padding:8px;box-sizing:border-box;overflow:hidden;"
        & {tile} & "'>"
        & "<div style='font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{_c(table, category)}", blank_label)} & "</div>"
        & "<div style='font-size:16px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>" & {_fmt('[@v]')} & "</div></div>", "", [@k], ASC )
VAR _r2 = CONCATENATEX ( _row2,
    VAR _i = MOD ( INT ( [@k] ) - 1, 6 )
    RETURN "<div{_mf(motion, 'mo-pop', alert)} style='flex:" & FORMAT ( MAX ( DIVIDE ( [@v], _tot ) * 1000, 1 ), "0" ) & " 1 0;min-width:0;border-radius:6px;padding:8px;box-sizing:border-box;overflow:hidden;"
        & {tile} & "'>"
        & "<div style='font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{_c(table, category)}", blank_label)} & "</div>"
        & "<div style='font-size:16px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>" & {_fmt('[@v]')} & "</div></div>", "", [@k], ASC )
""".replace("VAR _tiles = ( t ) => BLANK ()\n", "") + _wrap(title, subtitle,
            f"\"<div style='flex:1;display:flex;flex-direction:column;gap:6px;min-height:0'><div{_m(motion, 'mo-st')} style='flex:1;display:flex;gap:6px;min-height:0'>\" & _r1 & \"</div>\" & IF ( _r2 = \"\", \"\", \"<div{_m(motion, 'mo-st')} style='flex:1;display:flex;gap:6px;min-height:0'>\" & _r2 & \"</div>\" ){_fill(fill, f"_n <= {short_when}")} & \"</div>\"",
            empty_text, motion=motion)


# 7 --------------------------------------------------------------- decomposition (static, largest branch)
def decomp_static(table, levels, value, title, subtitle, level_names, total_label="Total", empty_text="No data", blank_label="-",
                  motion=False, alert=None):
    """Total -> split by each level in turn, always following the largest branch (no drill interaction)."""
    assert len(levels) == len(level_names) and 1 <= len(levels) <= 3
    level_names, total_label = [_t(n) for n in level_names], _t(total_label)
    parts, filt = [], []
    for i, col in enumerate(levels):
        f = ", ".join(filt)
        parts.append(f"""
VAR _l{i} = TOPN ( 4, FILTER ( ADDCOLUMNS ( CALCULATETABLE ( VALUES ( {_c(table, col)} ){', ' + f if f else ''} ), "@v", CALCULATE ( {value}{', ' + f if f else ''} ) + 0 ), [@v] > 0 ), [@v], DESC )
VAR _k{i} = MAXX ( TOPN ( 1, _l{i}, [@v], DESC ), {_c(table, col)} )
VAR _h{i} =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:6px'><div style='font-size:11px;color:{FG2};white-space:nowrap'>{level_names[i]}</div>"
    & CONCATENATEX ( _l{i},
        VAR _top = {_c(table, col)} = _k{i}
        RETURN "<div{_mf(motion, 'mo-in', alert)} style='box-sizing:border-box;border-radius:6px;padding:4px 8px;font-size:12px;display:flex;justify-content:space-between;gap:6px;"
            & IF ( _top, "background:@@strong@@;color:@@on_accent@@;font-weight:700", "background:@@track@@" ) & "'>"
            & "<span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{_c(table, col)}", blank_label)} & "</span>"
            & "<span style='direction:ltr;unicode-bidi:isolate'>" & [@v] & "</span></div>",
        "", [@v], DESC ) & "</div>\"""")
        filt.append(f"{_c(table, col)} = _k{i}")
    cols = " & \"<div style='flex:none;align-self:center;color:@@arrow@@'>@@fwd_arrow@@</div>\" & ".join(f"_h{i}" for i in range(len(levels)))
    return ISO + f"""
VAR _tot = {value} + 0
VAR _n = IF ( _tot > 0, 1, 0 )""" + "".join(parts) + "\n" + _wrap(title, subtitle,
        f"\"<div{_m(motion, 'mo-st')} style='flex:1;display:flex;align-items:flex-start;gap:8px;min-height:0'>"
        f"<div{_m(motion, 'mo-pop')} style='flex:none;width:90px;border-radius:8px;background:@@fg@@;color:@@surface@@;padding:8px;box-sizing:border-box'>"
        f"<div style='font-size:11px'>{total_label}</div><div style='font-size:22px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>\" & {_fmt('_tot')} & \"</div></div>"
        f"<div style='flex:none;align-self:center;color:@@arrow@@'>@@fwd_arrow@@</div>\" & {cols} & \"</div>\"",
        empty_text, motion=motion)


# 8 --------------------------------------------------------------- data table
def data_table(table, key, columns, title, subtitle, sort_by, top=5, key_label=None, totals=None,
               empty_text="No data", blank_label="-", more_label="and {n} more", header_accent=None, zebra=True, tip_value='FORMAT ( [@s], "#,0" )',
               motion=False, alert=None, stretch=True, fill=None, short_when=3):
    """A real table card (header row, aligned columns, zebra rows, optional totals, "and N more" + tooltip).

    key      column whose values are the rows (shown first unless key_label is None and you list it yourself)
    columns  list of dicts: {"label", "value" (DAX evaluated per row: a measure or CALCULATE(...) - a bare SUM gives
             every row the grand total), "kind": text|number|percent|date|bar|pill,
             "width": CSS grid width (e.g. "1.4fr", "90px"), optional "fmt" (number format), optional "total" (DAX)}
             pill: colored by value (stable category colors) - pass "pill_col": a column name of `table`
             optional "blank": label for an empty value in this column (default: blank_label)
             bar + motion: optional "prev" (DAX, same row context) - the bar moves from the previous value to the current one
    sort_by  DAX sort expression (DESC), ties broken by the key (a measure or CALCULATE(...), like values)
    top      rows shown, 30px each - from the fit budget, not the data: at 328px card height 5 rows with totals,
             6 without: rows = (H - 32 padding - 58 title - 30 header - 30 totals - 22 more line - 8 slack) / 30
    totals   label for a totals row (each column's "total" DAX, if any), or None
    header_accent  None (neutral header) or a color token base such as "cat1" (tinted header row)
    stretch  True (default): data rows grow to fill the card (30-44px instead of a fixed 30px); False: the 1.0 fixed rows
    fill     DAX text (e.g. mix(...)) shown under the table when it has at most short_when rows
    Rows whose sort_by is BLANK are left out, so a key from a dimension table follows a filter on the fact table.
    tip_value  DAX text shown next to each hidden row in the "and N more" tooltip (row context of the key; [@s] = sort value)
    Numbers align to the end side and use tabular figures; text is clipped with an ellipsis, never wrapped."""
    if totals and not key_label:
        raise ValueError("totals needs key_label: the totals label is written in the key column")
    cols = ([{"label": key_label, "value": f"{_c(table, key)}", "kind": "key", "width": "1.6fr"}] if key_label else []) + list(columns)
    # one grid per row: "1fr" means minmax(auto,1fr), so a wide value would widen its column in that row only and break
    # the line-up with the header -> every fr track is minmax(0,fr) and every cell can shrink (min-width:0)
    widths = " ".join(re.sub(r"^([\d.]+)fr$", r"minmax(0,\1fr)", c.get("width", "1fr")) for c in cols)
    grid = f"display:grid;grid-template-columns:{widths};column-gap:12px;align-items:center"
    num_style = ("text-align:@@end@@;direction:ltr;unicode-bidi:isolate;font-variant-numeric:tabular-nums;white-space:nowrap;"
                 "min-width:0;overflow:hidden;text-overflow:ellipsis")
    clip = "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0"
    hdr_bg = (f"background:@@{header_accent}_soft@@;color:@@{header_accent}_text@@" if header_accent
              else f"background:@@inset@@;color:{FG2}")
    bar_vars, cells, tcells = [], [], []
    for j, c in enumerate(cols):
        kind, v = c.get("kind", "text"), c["value"]
        if kind == "bar":
            bar_vars.append(f"VAR _mx{j} = MAX ( MAXX ( _top, {v} ), 0.000001 )")
        if kind == "key":
            cell = f'"<div style=\'{clip};font-weight:600\'>" & {_cat(v, blank_label)} & "</div>"'
        elif kind == "text":
            cell = f'"<div style=\'{clip}\'>" & {_cat(v, c.get("blank", blank_label))} & "</div>"'
        elif kind in ("number", "percent", "date"):
            fmt = c.get("fmt") or {"number": "#,0", "percent": "0%", "date": "dd/MM/yyyy"}[kind]
            cell = f'"<div style=\'{num_style}\'>" & IF ( ISBLANK ( {v} ), "-", FORMAT ( {v}, "{fmt}" ) ) & "</div>"'
        elif kind == "bar":
            fmt = c.get("fmt") or "#,0"
            color = f"@@{c.get('color', 'primary')}@@"
            pv = c.get("prev") if motion else None   # previous value: the bar moves from it to the current one
            fill = (f'<div{_mf(motion, "mo-gw", alert)} style=\'--mo-w0:" & FORMAT ( MIN ( MAX ( DIVIDE ( {pv}, _mx{j} ), 0 ), 1 ) * 100, "0.0" ) & "%;'
                    if pv else f'<div{_mf(motion, "mo-gx", alert)} style=\'')
            cell = (f'"<div style=\'display:flex;align-items:center;gap:8px;min-width:0\'><div style=\'flex:1;min-width:16px;height:10px;border-radius:5px;background:@@track@@;overflow:hidden;display:flex\'>'
                    f'{fill}flex:none;width:" & FORMAT ( MAX ( DIVIDE ( {v}, _mx{j} ), 0 ) * 100, "0.0" ) & "%;background:{color}\'></div></div>'
                    f'<div style=\'{num_style};flex:none;min-width:auto;overflow:visible\'>" & IF ( ISBLANK ( {v} ), "-", FORMAT ( {v}, "{fmt}" ) ) & "</div></div>"')
        elif kind == "pill":
            pc = c["pill_col"]
            ref = v
            cell = (f'"<div style=\'min-width:0\'><span style=\'display:inline-block;max-width:100%;padding:1px 10px;border-radius:999px;font-size:11px;{clip};background:" & '
                    f'{_catstyle(table, pc, ref, "@@{c}_soft@@;color:@@{c}_text@@")} & "\'>" & {_cat(ref, c.get("blank", blank_label))} & "</span></div>"')
        else:
            raise ValueError(f"unknown column kind {kind}")
        cells.append(cell)
        t = c.get("total")
        if j == 0:
            tcells.append(f'"<div style=\'{clip};font-weight:700\'>{_t(totals or "")}</div>"')
        elif t and kind in ("number", "percent", "bar"):
            fmt = c.get("fmt") or {"number": "#,0", "percent": "0%", "bar": "#,0"}[kind]
            tcells.append(f'"<div style=\'{num_style};font-weight:700\'>" & IF ( ISBLANK ( {t} ), "-", FORMAT ( {t}, "{fmt}" ) ) & "</div>"')
        else:
            tcells.append('"<div></div>"')
    head_cells = " & ".join(
        f'"<div style=\'{clip};{num_style if c.get("kind") in ("number", "percent", "date", "bar") else ""}\'>{_t(c["label"] or "")}</div>"' for c in cols)
    row_cells = " & ".join(cells)
    more = _t(more_label).replace("{n}", '" & LRI & _rest & PDI & "')
    out = ISO + f"""
VAR _rows = ADDCOLUMNS ( FILTER ( ADDCOLUMNS ( VALUES ( {_c(table, key)} ), "@s0", {sort_by} ), NOT ISBLANK ( [@s0] ) ), "@s", [@s0] + 0 )
VAR _n = COUNTROWS ( _rows ) + 0
VAR _top = TOPN ( {top}, _rows, [@s], DESC, {_c(table, key)}, ASC )
VAR _rest = _n - COUNTROWS ( _top )
""" + "\n".join(bar_vars) + f"""
VAR _restT = TOPN ( 30, EXCEPT ( _rows, _top ), [@s], DESC, {_c(table, key)}, ASC )
VAR _tip =
    CONCATENATEX ( _restT,
        VAR _cur = [@s] VAR _ck = {_c(table, key)}
        VAR _k = FORMAT ( COUNTROWS ( FILTER ( _restT, [@s] > _cur || ( [@s] = _cur && {_c(table, key)} < _ck ) ) ) + 1, "00" )
        RETURN " data-tooltip-title-" & _k & "='" & {_cat(f"{_c(table, key)}", blank_label)} & "' data-tooltip-value-" & _k & "='" & SUBSTITUTE ( {tip_value}, "'", "’" ) & "'",
        "", [@s], DESC, {_c(table, key)}, ASC )
VAR _body =
    CONCATENATEX ( _top,
        VAR _cur = [@s] VAR _ck = {_c(table, key)}
        VAR _i = COUNTROWS ( FILTER ( _top, [@s] > _cur || ( [@s] = _cur && {_c(table, key)} < _ck ) ) ) + 1
        RETURN "<div{_mf(motion, 'mo-in', alert)} style='{grid};height:30px;padding:0 8px;border-bottom:1px solid @@divider@@;font-size:12px;"
            {'& IF ( MOD ( _i, 2 ) = 0, "background:@@inset@@", "" ) ' if zebra else ""}& "'>"
            & {row_cells} & "</div>",
        "", [@s], DESC, {_c(table, key)}, ASC )
VAR _totals = {f'"<div style=\'{grid};height:30px;padding:0 8px;border-top:2px solid @@border@@;font-size:12px\'>" & ' + " & ".join(tcells) + ' & "</div>"' if totals else '""'}
""" + _wrap(title, subtitle,
            f"\"<div{_m(motion, 'mo-st')} style='display:flex;flex-direction:column;min-height:0'>"
            f"<div style='{grid};height:30px;padding:0 8px;border-radius:6px;font-size:11px;font-weight:700;{hdr_bg}'>\" & {head_cells} & \"</div>\" & _body & _totals{_fill(fill, f"_n <= {short_when}")} & \"</div>\""
            f" & IF ( _rest > 0, \"<div class='tooltipEnabled'\" & _tip & \" style='font-size:12px;color:@@primary_text@@;margin-top:4px;flex:none'>{more}</div>\" )",
            empty_text, motion=motion)
    return _stretched(out, [("style='{grid};height:30px;padding:0 8px;border-bottom".format(grid=grid), "style='{grid};flex:1 1 0;min-height:30px;max-height:44px;padding:0 8px;border-bottom".format(grid=grid)),
                            ("style='{grid};height:30px;padding:0 8px;border-radius".format(grid=grid), "style='{grid};height:30px;flex:none;padding:0 8px;border-radius".format(grid=grid)),
                            ("style='display:flex;flex-direction:column;min-height:0'>", "style='flex:1;display:flex;flex-direction:column;min-height:0'>")]
                      + ([("style='{grid};height:30px;padding:0 8px;border-top".format(grid=grid), "style='{grid};height:30px;flex:none;padding:0 8px;border-top".format(grid=grid))]
                         if totals else [])) if stretch else out


# 9 --------------------------------------------------------------- KPI card (an icon is required)
# 22px glyphs on a 24-unit grid, drawn with {c} (glyph color) and {k} (detail color). Generic shapes, no brand marks.
KPI_ICONS = {
    "money":  "<svg width='22' height='22' viewBox='0 0 24 24'><rect x='2' y='6' width='20' height='12' rx='2.5' fill='{c}'/><circle cx='12' cy='12' r='3.2' fill='{k}'/></svg>",
    "cart":   "<svg width='22' height='22' viewBox='0 0 24 24'><path d='M3 4h3l2.2 10.2h10.3L21 7H7.2' fill='none' stroke='{c}' stroke-width='2.4' stroke-linejoin='round'/><circle cx='9.5' cy='19' r='1.9' fill='{c}'/><circle cx='17' cy='19' r='1.9' fill='{c}'/></svg>",
    "tag":    "<svg width='22' height='22' viewBox='0 0 24 24'><path d='M3 12.5V4h8.5L21 13.5 12.5 22z' fill='{c}'/><circle cx='7.5' cy='8.5' r='1.8' fill='{k}'/></svg>",
    "return": "<svg width='22' height='22' viewBox='0 0 24 24'><path d='M9 5L4 10l5 5' fill='none' stroke='{c}' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/><path d='M5 10h9a6 6 0 0 1 0 12h-3' fill='none' stroke='{c}' stroke-width='2.6' stroke-linecap='round'/></svg>",
    "people": "<svg width='22' height='22' viewBox='0 0 24 24'><circle cx='9' cy='8' r='4' fill='{c}'/><path d='M1.5 21a7.5 7.5 0 0 1 15 0z' fill='{c}'/><circle cx='17.5' cy='9' r='3' fill='{c}' opacity='.6'/></svg>",
    "clock":  "<svg width='22' height='22' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10' fill='{c}'/><path d='M12 6.5V12l3.5 2.5' stroke='{k}' stroke-width='2.2' fill='none' stroke-linecap='round'/></svg>",
    "check":  "<svg width='22' height='22' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10' fill='{c}'/><path d='M7 12.5l3.2 3.2L17 9' stroke='{k}' stroke-width='2.4' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "chart":  "<svg width='22' height='22' viewBox='0 0 24 24'><rect x='3' y='12' width='4' height='9' rx='1' fill='{c}'/><rect x='10' y='7' width='4' height='14' rx='1' fill='{c}'/><rect x='17' y='3' width='4' height='18' rx='1' fill='{c}'/></svg>",
    "list":   "<svg width='22' height='22' viewBox='0 0 24 24'><rect x='2' y='3' width='20' height='5' rx='1.5' fill='{c}'/><rect x='2' y='10' width='20' height='5' rx='1.5' fill='{c}' opacity='.6'/><rect x='2' y='17' width='12' height='4' rx='1.5' fill='{c}' opacity='.35'/></svg>",
    "alert":  "<svg width='22' height='22' viewBox='0 0 24 24'><path d='M12 2.5L23 21H1z' fill='{c}'/><rect x='11' y='9' width='2' height='6' fill='{k}'/><rect x='11' y='17' width='2' height='2' fill='{k}'/></svg>",
}


def kpi_card(title, value, fmt, icon, sub='""', cat="cat1", filled=False, motion=False, alert=None, prev=None,
             updated=None, stale_after=60):
    """KPI card: title + icon chip on one line, one big number, one single-line caption.

    value  DAX for the number; BLANK shows "-"     fmt  FORMAT string ("#,0", "$#,0", "0.0%")
    icon   a KPI_ICONS key - required: a KPI without an icon is rejected
    sub    DAX text expression for the caption line (single line, clipped)
    cat    color token base for the accent (cat1..cat6, or primary/done/bad/...)
    filled True: deep fill (@@strong@@ + darkening overlay), white text, colored top band;
           False: light card with a colored start border and a tinted icon chip.
    motion True: the number rolls in digit by digit - from prev (DAX, the previous period's value) when given, so the
           roll shows the change; the icon chip pops last.
    alert  DAX condition on _v (the value): when it holds, the icon chip pulses a red ring twice (needs motion).
    updated  DAX datetime of the data's last refresh, in UTC (compared with UTCNOW()): adds "Updated N ago" to the
           caption line; older than stale_after minutes -> an amber "Stale" state. With motion, a fresh dot pulses twice."""
    if icon not in KPI_ICONS:
        raise ValueError(f"kpi_card needs an icon from KPI_ICONS ({', '.join(KPI_ICONS)}), got {icon!r}")
    title = _t(title)
    if _S is not None and _S.ACTIVE:   # style: one material; color via the card's role tokens (c_chip / c_icon)
        root = f"{CARD};padding:12px 20px 14px"
        chip, title_c = "@@c_chip@@", FG2
        glyph = KPI_ICONS[icon].format(c="@@c_icon@@", k="@@c_icon_in@@")
    elif filled:
        root = (f"{CARD};background:linear-gradient(160deg,rgba(0,0,0,0),rgba(0,0,0,.24)),@@strong@@;color:@@on_accent@@;"
                f"border-top:6px solid @@{cat}@@;padding:12px 20px 14px")
        chip, title_c = "rgba(255,255,255,.22)", "@@on_accent@@"
        glyph = KPI_ICONS[icon].format(c="@@on_accent@@", k="@@strong@@")
    else:
        root = f"{CARD};border-inline-start:5px solid @@{cat}@@;padding:12px 20px 14px"
        chip, title_c = f"@@{cat}_soft@@", FG2
        glyph = KPI_ICONS[icon].format(c=f"@@{cat}@@", k="@@surface@@")
    odo = ("" if not motion else
           '\nVAR _txt = IF ( ISBLANK ( _v ), "-", FORMAT ( _v, "' + fmt + '" ) )'
           '\nVAR _dg = "<i>0</i><i>1</i><i>2</i><i>3</i><i>4</i><i>5</i><i>6</i><i>7</i><i>8</i><i>9</i>"'
           '\nVAR _odo = CONCATENATEX ( GENERATESERIES ( 1, LEN ( _txt ), 1 ), VAR _ch = MID ( _txt, [Value], 1 ) RETURN'
           ' IF ( CONTAINSSTRINGEXACT ( "0123456789", _ch ), "<span class=\'mo-od fit-clip\'><span class=\'mo-os\' style=\'translate:0 -" & _ch'
           ' & "em;animation-delay:calc(var(--mo-k,1)*" & FORMAT ( 0.06 * [Value], "0.00" ) & "s)\'>" & _dg & "</span></span>",'
           ' "<span>" & _ch & "</span>" ), "", [Value], ASC )')
    if motion and prev:
        odo = odo.replace("VAR _odo", '\nVAR _ptxt = IF ( ISBLANK ( ' + prev + ' ), "", FORMAT ( ' + prev + ', "' + fmt + '" ) )'
                          '\nVAR _off = LEN ( _txt ) - LEN ( _ptxt )\nVAR _odo').replace(
            "\"em;animation-delay", "\"em;--mo-from:-\" & VAR _pc = IF ( [Value] - _off >= 1, MID ( _ptxt, [Value] - _off, 1 ), \"0\" ) "
            "RETURN IF ( CONTAINSSTRINGEXACT ( \"0123456789\", _pc ), _pc, \"0\" ) & \"em;animation-delay")
    fresh = ""
    if updated:
        fresh = (f'\nVAR _age = DATEDIFF ( {updated}, UTCNOW (), MINUTE )'
                 '\nVAR _ago = IF ( ISBLANK ( _age ), "", IF ( _age < 1, "just now", IF ( _age < 60, _age & " min ago", IF ( _age < 1440, INT ( _age / 60 ) & " h ago", INT ( _age / 1440 ) & " d ago" ) ) ) )'
                 f'\nVAR _stale = _age > {int(stale_after)}'
                 '\nVAR _fresh = IF ( _ago = "", "", "<span style=\'flex:none;white-space:nowrap;color:" & IF ( _stale, "@@warn_text@@", "@@done_text@@" ) & "\'>"'
                 f' & "<i{_m(motion, "mo-fd")}" & IF ( _stale, "", "" ) & " style=\'display:inline-block;width:7px;height:7px;border-radius:50%;margin-inline-end:5px;vertical-align:middle;background:currentColor\'></i>"'
                 ' & IF ( _stale, "Stale · " & _ago, "Updated " & _ago ) & "</span>" )')
        if motion:   # a stale dot does not pulse
            fresh = fresh.replace('"<i class=\'mo-fd\'" & IF ( _stale, "", "" ) & "', '"<i class=\'" & IF ( _stale, "", "mo-fd" ) & "\'')
        else:
            fresh = fresh.replace(' & IF ( _stale, "", "" ) & "', "")
    number = "_odo" if motion else f'IF ( ISBLANK ( _v ), "-", FORMAT ( _v, "{fmt}" ) )'
    return ISO + f"""
VAR _v = {value}{odo}{fresh}
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{root};display:flex;flex-direction:column;justify-content:space-between'>{_mstyle(motion)}"
        & "<div style='display:flex;align-items:center;justify-content:space-between;gap:8px;flex:none'>"
            & "<span style='font-size:14px;font-weight:600;color:{title_c};white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{title}</span>"
            & "<span{_mf(motion, 'mo-pop mo-late', alert)} style='width:40px;height:40px;flex:none;border-radius:10px;background:{chip};display:flex;align-items:center;justify-content:center'>{glyph}</span>"
        & "</div>"
        & "<div style='font-size:40px;font-weight:700;line-height:1;direction:ltr;unicode-bidi:isolate;text-align:@@start@@;white-space:nowrap{';font-variant-numeric:tabular-nums' if motion else ''}'>" & {number} & "</div>"
        & {('"<div style=' + "'" + 'font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:none' + "'" + '>" & ' + sub + ' & "</div>"') if not updated else
           ('"<div style=' + "'" + 'display:flex;justify-content:space-between;gap:8px;font-size:12px;flex:none;min-width:0' + "'" + '><span style=' + "'" + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0' + "'" + '>" & ' + sub + ' & "</span>" & _fresh & "</div>"')}
    & "</div>\""""
