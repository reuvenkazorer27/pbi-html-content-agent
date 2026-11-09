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

Card sizes the builders are designed for (fit-checked): 520-640 wide x 320-400 high.
"""

FONT = "font-family:Segoe UI,Arial,sans-serif"
CARD = ("box-sizing:border-box;height:100vh;overflow:hidden;background:@@surface@@;"
        "border-radius:12px;box-shadow:0 1px 3px @@shadow@@;line-height:1.35;"
        "direction:@@dir@@;text-align:@@start@@;" + FONT + ";color:@@fg@@")
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


def _wrap(title, subtitle, body, empty_text, is_empty="_n = 0"):
    empty_text = _t(empty_text)
    return f"""
RETURN
    "<div dir='@@dir@@' lang='@@lang@@' style='{CARD};padding:16px 20px;display:flex;flex-direction:column;gap:10px'>"
        & {_head(title, subtitle)}
        & IF ( {is_empty},
            "<div style='flex:1;display:flex;align-items:center;justify-content:center;font-size:13px;color:{FG2}'>{empty_text}</div>",
            {body} )
    & "</div>\""""


def _cat(ref, blank_label):
    """category value for display: blank -> blank_label, apostrophes made safe for attributes"""
    return f'IF ( {ref} = "", "{_t(blank_label)}", SUBSTITUTE ( {ref}, "\'", "’" ) )'


def _fmt(expr):
    """compact number: 1.2M / 3.4K / 120, isolated for bidi"""
    return (f"LRI & IF ( ABS ( {expr} ) >= 1000000, FORMAT ( {expr} / 1000000, \"0.0\" ) & \"M\", "
            f"IF ( ABS ( {expr} ) >= 1000, FORMAT ( {expr} / 1000, \"0.0\" ) & \"K\", FORMAT ( {expr}, \"#,0\" ) ) ) & PDI")


# 1 --------------------------------------------------------------- waterfall
def waterfall(table, category, delta, title, subtitle, order=None, start=None, start_label="Start", end_label="End",
              empty_text="No data", blank_label="-"):
    """Start bar, one floating bar per category (positive / negative), end bar. Reads in the page's direction.
    order: optional sort column (one value per category); default = category name."""
    s0 = start or "0"
    start_label, end_label = _t(start_label), _t(end_label)
    okey = f"CALCULATE ( MIN ( {table}[{order}] ) )" if order else f"RANKX ( ALL ( {table}[{category}] ), {table}[{category}], , ASC )"
    return ISO + f"""
VAR _start = {s0} + 0
VAR _steps = FILTER ( ADDCOLUMNS ( VALUES ( {table}[{category}] ), "@d", {delta} + 0, "@o", {okey} ), [@d] <> 0 )
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
            & "<div style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:" & _col
            & ";bottom:" & FORMAT ( DIVIDE ( _bot - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _v ), _rng ) * _H, 2 ), "0.0" ) & "px'></div>"
            & "<div style='position:absolute;inset-inline-start:0;width:100%;text-align:center;font-size:11px;font-weight:700;color:" & _col
            & ";bottom:" & FORMAT ( MIN ( DIVIDE ( _top - _lo, _rng ) * _H + 2, _H - 16 ), "0.0" ) & "px'>" & LRI & IF ( _v >= 0, "+", "" ) & FORMAT ( _v, "#,0" ) & PDI & "</div></div>"
            & "<div style='height:18px;font-size:11px;color:{FG2};text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{table}[{category}]", blank_label)} & "</div></div>",
        "", [@o], ASC )
VAR _total = ( lbl, v ) => BLANK ()
VAR _openBar =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:4px'><div style='position:relative;height:" & _H & "px'>"
    & "<div style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:@@muted@@;bottom:" & FORMAT ( DIVIDE ( MIN ( _start, 0 ) - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _start ), _rng ) * _H, 2 ), "0.0" ) & "px'></div></div>"
    & "<div style='height:18px;font-size:11px;font-weight:700;text-align:center'>{start_label} " & {_fmt('_start')} & "</div></div>"
VAR _closeBar =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:4px'><div style='position:relative;height:" & _H & "px'>"
    & "<div style='position:absolute;inset-inline-start:15%;width:70%;border-radius:3px;background:@@primary@@;bottom:" & FORMAT ( DIVIDE ( MIN ( _end, 0 ) - _lo, _rng ) * _H, "0.0" ) & "px;height:" & FORMAT ( MAX ( DIVIDE ( ABS ( _end ), _rng ) * _H, 2 ), "0.0" ) & "px'></div></div>"
    & "<div style='height:18px;font-size:11px;font-weight:700;text-align:center'>{end_label} " & {_fmt('_end')} & "</div></div>"
""".replace("VAR _bar = ( lbl, v, b, col, sgn ) => BLANK ()\n", "").replace("VAR _total = ( lbl, v ) => BLANK ()\n", "") + _wrap(
        title, subtitle, "\"<div style='flex:1;display:flex;align-items:flex-end;gap:6px'>\" & _openBar & _bars & _closeBar & \"</div>\"", empty_text)


# 2 --------------------------------------------------------------- heat matrix
def heat_matrix(table, row_col, col_col, value, title, subtitle, max_rows=6, max_cols=6, empty_text="No data", blank_label="-"):
    """Category x category grid; cell color intensity = value / max. Top rows/cols by total."""
    return ISO + f"""
VAR _rows = TOPN ( {max_rows}, ADDCOLUMNS ( VALUES ( {table}[{row_col}] ), "@t", {value} + 0 ), [@t], DESC, {table}[{row_col}], ASC )
VAR _cols = TOPN ( {max_cols}, ADDCOLUMNS ( VALUES ( {table}[{col_col}] ), "@t", {value} + 0 ), [@t], DESC, {table}[{col_col}], ASC )
VAR _n = COUNTROWS ( FILTER ( _rows, [@t] > 0 ) ) + 0
VAR _max = MAXX ( CROSSJOIN ( SELECTCOLUMNS ( _rows, "r", {table}[{row_col}] ), SELECTCOLUMNS ( _cols, "c", {table}[{col_col}] ) ),
    VAR _r = [r] VAR _c = [c] RETURN CALCULATE ( {value}, {table}[{row_col}] = _r, {table}[{col_col}] = _c ) + 0 )
VAR _hdr =
    "<div style='display:flex;gap:4px;height:22px;flex:none'><div style='width:120px;flex:none'></div>"
    & CONCATENATEX ( _cols, "<div style='flex:1 1 0;min-width:0;font-size:11px;color:{FG2};text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
        & {_cat(f"{table}[{col_col}]", blank_label)} & "</div>", "", [@t], DESC ) & "</div>"
VAR _grid =
    CONCATENATEX ( _rows,
        VAR _r = {table}[{row_col}]
        RETURN "<div style='display:flex;gap:3px;height:26px;flex:none'>"
            & "<div style='width:120px;flex:none;font-size:12px;line-height:26px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat("_r", blank_label)} & "</div>"
            & CONCATENATEX ( _cols,
                VAR _c = {table}[{col_col}]
                VAR _v = CALCULATE ( {value}, {table}[{row_col}] = _r, {table}[{col_col}] = _c ) + 0
                VAR _a = DIVIDE ( _v, _max )
                RETURN "<div style='flex:1 1 0;min-width:0;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;"
                    & IF ( _v = 0, "background:@@track@@;color:@@fg2@@", IF ( _a > 0.5, "background:@@strong@@;color:@@on_accent@@", "background:@@primary_soft@@;color:@@primary_text@@" ) )
                    & "'>" & IF ( _v = 0, "", LRI & _v & PDI ) & "</div>",
                "", [@t], DESC )
            & "</div>",
        "", [@t], DESC )
""" + _wrap(title, subtitle, "\"<div style='display:flex;flex-direction:column;gap:3px'>\" & _hdr & _grid & \"</div>\"", empty_text)


# 3 --------------------------------------------------------------- lift bars (key influencers, static)
def lift_bars(table, category, target_filter, title, subtitle, top=6, min_support=2, empty_text="No data", blank_label="-"):
    """For each category: share of rows meeting target_filter vs. the overall share (lift = x times).
    Categories with fewer than min_support rows and blank categories are left out (a 1-row category has a
    meaningless lift)."""
    return ISO + f"""
VAR _all = COUNTROWS ( {table} ) + 0
VAR _hit = CALCULATE ( COUNTROWS ( {table} ), {target_filter} ) + 0
VAR _base = DIVIDE ( _hit, _all )
VAR _cats = FILTER ( ADDCOLUMNS ( VALUES ( {table}[{category}] ),
    "@n", CALCULATE ( COUNTROWS ( {table} ) ) + 0,
    "@h", CALCULATE ( COUNTROWS ( {table} ), {target_filter} ) + 0 ), [@n] >= {min_support} && {table}[{category}] <> "" )
VAR _lifted = ADDCOLUMNS ( _cats, "@l", DIVIDE ( DIVIDE ( [@h], [@n] ), _base ) )
VAR _top = TOPN ( {top}, _lifted, [@l], DESC, [@n], DESC, {table}[{category}], ASC )
VAR _n = COUNTROWS ( _top ) + 0
VAR _maxL = MAXX ( _top, [@l] )
VAR _body =
    CONCATENATEX ( _top,
        VAR _l = [@l]
        RETURN "<div style='display:flex;align-items:center;gap:10px;height:28px'>"
            & "<div style='width:130px;flex:none;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {table}[{category}] & "</div>"
            & "<div style='flex:1;height:14px;border-radius:7px;background:@@track@@;overflow:hidden;display:flex'>"
            & "<div style='flex:none;width:" & FORMAT ( DIVIDE ( _l, _maxL ) * 100, "0.0" ) & "%;background:" & IF ( _l >= 1, "@@primary@@", "@@muted@@" ) & "'></div></div>"
            & "<div style='width:64px;flex:none;font-size:13px;font-weight:700;text-align:@@end@@;direction:ltr;unicode-bidi:isolate'>" & FORMAT ( _l, "0.0" ) & "x</div>"
            & "</div>",
        "", [@l], DESC, [@n], DESC )
""" + _wrap(title, subtitle,
            f"\"<div style='font-size:12px;color:{FG2}'>\" & LRI & FORMAT ( _base, \"0%\" ) & PDI & \" = 1.0x</div><div style='display:flex;flex-direction:column;gap:4px'>\" & _body & \"</div>\"",
            empty_text)


# 4 --------------------------------------------------------------- small multiples
def small_multiples(table, category, date_col, value, title, subtitle, top=6, months=6, cols=3, empty_text="No data",
                    blank_label="-"):   # blank categories are skipped here; blank_label kept for a uniform signature
    """One mini column chart per category over the last `months` months (by date_col), shared scale."""
    return ISO + f"""
VAR _endM = EOMONTH ( MAX ( {table}[{date_col}] ), 0 )
VAR _cats = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {table}[{category}] ), "@t", {value} + 0 ), {table}[{category}] <> "" && [@t] > 0 ), [@t], DESC, {table}[{category}], ASC )
VAR _n = IF ( ISBLANK ( _endM ), 0, COUNTROWS ( _cats ) + 0 )
VAR _grid = GENERATE ( SELECTCOLUMNS ( _cats, "cat", {table}[{category}] ), GENERATESERIES ( 0, {months} - 1, 1 ) )
VAR _vals = ADDCOLUMNS ( _grid, "@v",
    VAR _c = [cat] VAR _m0 = EOMONTH ( _endM, -[Value] - 1 ) + 1 VAR _m1 = EOMONTH ( _endM, -[Value] )
    RETURN CALCULATE ( {value}, {table}[{category}] = _c, {table}[{date_col}] >= _m0, {table}[{date_col}] <= _m1 ) + 0 )
VAR _max = MAX ( MAXX ( _vals, [@v] ), 1 )
VAR _panels =
    CONCATENATEX ( _cats,
        VAR _c = {table}[{category}]
        RETURN "<div style='box-sizing:border-box;border:1px solid @@border@@;border-radius:8px;padding:5px 8px;display:flex;flex-direction:column;gap:2px;min-width:0'>"
            & "<div style='display:flex;justify-content:space-between;gap:6px;font-size:12px'><span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & _c & "</span>"
            & "<b style='direction:ltr;unicode-bidi:isolate'>" & [@t] & "</b></div>"
            & "<div style='display:flex;align-items:flex-end;gap:3px;height:34px;direction:ltr'>"
            & CONCATENATEX ( FILTER ( _vals, [cat] = _c ),
                "<div style='flex:1 1 0;border-radius:2px 2px 0 0;background:@@primary@@;height:" & FORMAT ( MAX ( DIVIDE ( [@v], _max ) * 34, 2 ), "0" ) & "px;opacity:" & IF ( [@v] = 0, "0.25", "1" ) & "'></div>",
                "", [Value], DESC )
            & "</div></div>",
        "", [@t], DESC )
""" + _wrap(title, subtitle,
            f"\"<div style='display:grid;grid-template-columns:repeat({cols},1fr);gap:8px'>\" & _panels & \"</div><div style='font-size:12px;color:{FG2}'>\" & FORMAT ( EOMONTH ( _endM, -{months} ) + 1, \"MMM yyyy\", \"@@locale@@\" ) & \" - \" & FORMAT ( _endM, \"MMM yyyy\", \"@@locale@@\" ) & \"</div>\"",
            empty_text)


# 5 --------------------------------------------------------------- scatter / bubble
def scatter(table, category, x, y, size, title, subtitle, x_label, y_label, top=12, empty_text="No data", blank_label="-"):
    """Bubble per category: position x/y, area by size. x grows left-to-right in both directions (axis)."""
    x_label, y_label = _t(x_label), _t(y_label)
    return ISO + f"""
VAR _pts = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {table}[{category}] ), "@x", {x} + 0, "@y", {y} + 0, "@s", {size} + 0 ),
    {table}[{category}] <> "" && [@s] > 0 ), [@s], DESC, {table}[{category}], ASC )
VAR _n = COUNTROWS ( _pts ) + 0
VAR _x0 = MIN ( MINX ( _pts, [@x] ), 0 ) VAR _x1 = MAX ( MAXX ( _pts, [@x] ), 0 ) VAR _xr = IF ( _x1 - _x0 = 0, 1, _x1 - _x0 )
VAR _y0 = MIN ( MINX ( _pts, [@y] ), 0 ) VAR _y1 = MAX ( MAXX ( _pts, [@y] ), 0 ) VAR _yr = IF ( _y1 - _y0 = 0, 1, _y1 - _y0 )
VAR _ms = MAXX ( _pts, [@s] )
VAR _dots =
    CONCATENATEX ( _pts,
        VAR _r = 4 + 9 * SQRT ( DIVIDE ( [@s], _ms ) )
        VAR _cx = 8 + 84 * DIVIDE ( [@x] - _x0, _xr )
        VAR _cy = 86 - 74 * DIVIDE ( [@y] - _y0, _yr )
        VAR _rk = RANKX ( _pts, [@s] + DIVIDE ( RANKX ( _pts, {table}[{category}], , DESC ), 1000 ), , DESC )
        VAR _lbl = _rk <= 5
        RETURN "<div title='" & SUBSTITUTE ( {table}[{category}], "'", "’" ) & "' style='position:absolute;transform:translate(-50%,-50%);border-radius:50%;background:@@primary@@;opacity:.75;"
            & "left:" & FORMAT ( _cx, "0.0" ) & "%;top:" & FORMAT ( _cy, "0.0" ) & "%;width:" & FORMAT ( 2 * _r, "0" ) & "px;height:" & FORMAT ( 2 * _r, "0" ) & "px'></div>"
            & IF ( _lbl, "<div style='position:absolute;font-size:11px;color:{FG2};white-space:nowrap;transform:translate(-50%,0);left:" & FORMAT ( _cx, "0.0" ) & "%;top:calc(" & FORMAT ( _cy, "0.0" ) & "% " & IF ( MOD ( _rk, 2 ) = 0, "- " & FORMAT ( _r + 18, "0" ), "+ " & FORMAT ( _r + 1, "0" ) ) & "px)'>"
            & LEFT ( {_cat(f"{table}[{category}]", blank_label)}, 14 ) & "</div>" ),
        "" )
""" + _wrap(title, subtitle,
            f"\"<div style='flex:1;display:flex;flex-direction:column;gap:4px;min-height:0'>"
            f"<div style='flex:1;position:relative;border-inline-start:1px solid @@border@@;border-bottom:1px solid @@border@@;direction:ltr;min-height:0'>\" & _dots & \"</div>"
            f"<div style='display:flex;justify-content:space-between;font-size:11px;color:{FG2};flex:none'><span>{y_label} ↑</span><span>{x_label} →</span></div></div>\"",
            empty_text)


# 6 --------------------------------------------------------------- treemap (two rows, proportional)
def treemap_rows(table, category, value, title, subtitle, top=8, empty_text="No data", blank_label="-"):
    """Approximate treemap: largest categories split over two rows, tile width proportional to value."""
    return ISO + f"""
VAR _c = TOPN ( {top}, FILTER ( ADDCOLUMNS ( VALUES ( {table}[{category}] ), "@v", {value} + 0 ), [@v] > 0 ), [@v], DESC, {table}[{category}], ASC )
VAR _n = COUNTROWS ( _c ) + 0
VAR _tot = SUMX ( _c, [@v] )
VAR _ranked = ADDCOLUMNS ( _c, "@k", RANKX ( _c, [@v], , DESC, Dense ) + DIVIDE ( RANKX ( _c, {table}[{category}], , ASC ), 1000 ) )
VAR _half = DIVIDE ( SUMX ( _c, [@v] ), 2 )
VAR _row1 = FILTER ( _ranked, SUMX ( FILTER ( _ranked, [@k] < EARLIER ( [@k] ) ), [@v] ) < _half )
VAR _row2 = EXCEPT ( _ranked, _row1 )
VAR _tiles = ( t ) => BLANK ()
VAR _r1 = CONCATENATEX ( _row1,
    VAR _i = MOD ( INT ( [@k] ) - 1, 6 )
    RETURN "<div style='flex:" & FORMAT ( MAX ( DIVIDE ( [@v], _tot ) * 1000, 1 ), "0" ) & " 1 0;min-width:0;border-radius:6px;padding:8px;box-sizing:border-box;overflow:hidden;"
        & SWITCH ( _i, 0, "background:@@primary_soft@@;color:@@primary_text@@;border-top:3px solid @@primary@@", 1, "background:@@maint_soft@@;color:@@maint_text@@;border-top:3px solid @@maint@@", 2, "background:@@design_soft@@;color:@@design_text@@;border-top:3px solid @@design@@", 3, "background:@@done_soft@@;color:@@done_text@@;border-top:3px solid @@done@@", 4, "background:@@bad_soft@@;color:@@fg@@;border-top:3px solid @@bad@@", "background:@@neutral_soft@@;color:@@fg@@;border-top:3px solid @@muted@@" ) & "'>"
        & "<div style='font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{table}[{category}]", blank_label)} & "</div>"
        & "<div style='font-size:16px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>" & {_fmt('[@v]')} & "</div></div>", "", [@k], ASC )
VAR _r2 = CONCATENATEX ( _row2,
    VAR _i = MOD ( INT ( [@k] ) - 1, 6 )
    RETURN "<div style='flex:" & FORMAT ( MAX ( DIVIDE ( [@v], _tot ) * 1000, 1 ), "0" ) & " 1 0;min-width:0;border-radius:6px;padding:8px;box-sizing:border-box;overflow:hidden;"
        & SWITCH ( _i, 0, "background:@@primary_soft@@;color:@@primary_text@@;border-top:3px solid @@primary@@", 1, "background:@@maint_soft@@;color:@@maint_text@@;border-top:3px solid @@maint@@", 2, "background:@@design_soft@@;color:@@design_text@@;border-top:3px solid @@design@@", 3, "background:@@done_soft@@;color:@@done_text@@;border-top:3px solid @@done@@", 4, "background:@@bad_soft@@;color:@@fg@@;border-top:3px solid @@bad@@", "background:@@neutral_soft@@;color:@@fg@@;border-top:3px solid @@muted@@" ) & "'>"
        & "<div style='font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{table}[{category}]", blank_label)} & "</div>"
        & "<div style='font-size:16px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>" & {_fmt('[@v]')} & "</div></div>", "", [@k], ASC )
""".replace("VAR _tiles = ( t ) => BLANK ()\n", "") + _wrap(title, subtitle,
            "\"<div style='flex:1;display:flex;flex-direction:column;gap:6px;min-height:0'><div style='flex:1;display:flex;gap:6px;min-height:0'>\" & _r1 & \"</div><div style='flex:1;display:flex;gap:6px;min-height:0'>\" & _r2 & \"</div></div>\"",
            empty_text)


# 7 --------------------------------------------------------------- decomposition (static, largest branch)
def decomp_static(table, levels, value, title, subtitle, level_names, total_label="Total", empty_text="No data", blank_label="-"):
    """Total -> split by each level in turn, always following the largest branch (no drill interaction)."""
    assert len(levels) == len(level_names) and 1 <= len(levels) <= 3
    level_names, total_label = [_t(n) for n in level_names], _t(total_label)
    parts, filt = [], []
    for i, col in enumerate(levels):
        f = ", ".join(filt)
        parts.append(f"""
VAR _l{i} = TOPN ( 4, FILTER ( ADDCOLUMNS ( CALCULATETABLE ( VALUES ( {table}[{col}] ){', ' + f if f else ''} ), "@v", CALCULATE ( {value}{', ' + f if f else ''} ) + 0 ), [@v] > 0 ), [@v], DESC )
VAR _k{i} = MAXX ( TOPN ( 1, _l{i}, [@v], DESC ), {table}[{col}] )
VAR _h{i} =
    "<div style='flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:6px'><div style='font-size:11px;color:{FG2};white-space:nowrap'>{level_names[i]}</div>"
    & CONCATENATEX ( _l{i},
        VAR _top = {table}[{col}] = _k{i}
        RETURN "<div style='box-sizing:border-box;border-radius:6px;padding:4px 8px;font-size:12px;display:flex;justify-content:space-between;gap:6px;"
            & IF ( _top, "background:@@strong@@;color:@@on_accent@@;font-weight:700", "background:@@track@@" ) & "'>"
            & "<span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>" & {_cat(f"{table}[{col}]", blank_label)} & "</span>"
            & "<span style='direction:ltr;unicode-bidi:isolate'>" & [@v] & "</span></div>",
        "", [@v], DESC ) & "</div>\"""")
        filt.append(f"{table}[{col}] = _k{i}")
    cols = " & \"<div style='flex:none;align-self:center;color:@@arrow@@'>@@fwd_arrow@@</div>\" & ".join(f"_h{i}" for i in range(len(levels)))
    return ISO + f"""
VAR _tot = {value} + 0
VAR _n = IF ( _tot > 0, 1, 0 )""" + "".join(parts) + "\n" + _wrap(title, subtitle,
        f"\"<div style='flex:1;display:flex;align-items:flex-start;gap:8px;min-height:0'>"
        f"<div style='flex:none;width:90px;border-radius:8px;background:@@fg@@;color:@@surface@@;padding:8px;box-sizing:border-box'>"
        f"<div style='font-size:11px'>{total_label}</div><div style='font-size:22px;font-weight:700;direction:ltr;unicode-bidi:isolate;text-align:@@start@@'>\" & {_fmt('_tot')} & \"</div></div>"
        f"<div style='flex:none;align-self:center;color:@@arrow@@'>@@fwd_arrow@@</div>\" & {cols} & \"</div>\"",
        empty_text)
