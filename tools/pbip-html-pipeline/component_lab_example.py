# -*- coding: utf-8 -*-
"""Component lab (example): bind every builder in components.py to the reference build's model (Hebrew
columns: סוג = type, מחלקה = department, סטטוס = status, בעלים = owner) - adapt the bindings to yours - evaluate on the open
Desktop model, render at card size and gate (fit + contrast). Usage:
  python -I component_lab.py            -> writes q_lab.dax, then run runq + preview + fitcheck (see main)
Env: DASH_DIR / DASH_LANG / DASH_PALETTE as for the dashboard; LAB_COLORS=category (one color per category value);
LAB_FROM=<results.json> renders saved results without querying (e.g. anonymized data for a public screenshot)."""
import html, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measures as MS                      # reference build: add(), M, T, C, LANG, DIR, tokens
import components as K
from palette import P as PAL

T, C, LANG = MS.T, MS.C, MS.LANG
L = (lambda he, en: en if LANG == "en" else he)
CL = os.environ.get("LAB_COLORS", "single")          # "category": one color per category value
TM = "status" if CL == "single" else "category"

LAB = [
    ("labWaterfall", K.waterfall(T, "סוג", "[# פעילים] - [# באפיון]", L("פעילים פחות באפיון לפי סוג", "Active minus in-design, by type"),
                                 L("מצטבר לפי סוג פרויקט", "Cumulative by project type"),
                                 start_label=L("התחלה", "Start"), end_label=L("סוף", "End"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"))),
    ("labHeat", K.heat_matrix(T, "מחלקה", "סטטוס", "[# פרויקטים]", L("מחלקה × סטטוס", "Department × status"),
                              L("מספר פרויקטים בכל צירוף", "Projects per combination"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"))),
    ("labLift", K.lift_bars(T, "מחלקה", f"{C('סטטוס')} = \"פעיל\"", L("איפה יש יותר פרויקטים פעילים", "Where active projects concentrate"),
                            L("פי כמה מהממוצע", "Times the overall share"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"), colors=CL)),
    ("labSmall", K.small_multiples(T, "בעלים", "תאריך התחלה", "[# פרויקטים]", L("פרויקטים חדשים לפי בעלים", "New projects by owner"),
                                   L("6 החודשים האחרונים", "Last 6 months"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"), colors=CL)),
    ("labScatter", K.scatter(T, "מחלקה", "[# פרויקטים]", "DIVIDE ( [# פעילים], [# פרויקטים] )", "[# פרויקטים]",
                             L("גודל מול שיעור פעילים", "Size vs. share active"), L("לפי מחלקה", "By department"),
                             L("פרויקטים", "Projects"), L("פעילים %", "Active %"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"), colors=CL)),
    ("labTreemap", K.treemap_rows(T, "מחלקה", "[# פרויקטים]", L("פרויקטים לפי מחלקה", "Projects by department"),
                                  L("השטח יחסי לכמות", "Area proportional to count"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"), colors=TM)),
    ("labDecomp", K.decomp_static(T, ["סוג", "מחלקה", "בעלים"], "[# פרויקטים]", L("פירוק לפי הענף הגדול", "Breakdown along the largest branch"),
                                  L("סוג ← מחלקה ← בעלים", "Type → department → owner"), [L("סוג", "Type"), L("מחלקה", "Department"), L("בעלים", "Owner")],
                                  total_label=L("סה״כ", "Total"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned"))),
    ("labTable", K.accent(K.data_table(
        T, "בעלים",
        [{"label": L("פרויקטים", "Projects"), "value": "[# פרויקטים]", "kind": "bar", "width": "1.4fr", "color": "cat1", "total": "[# פרויקטים]"},
         {"label": L("פעילים", "Active"), "value": "[# פעילים]", "kind": "number", "width": "64px", "total": "[# פעילים]"},
         {"label": L("באיחור", "Overdue"), "value": "[# חלף מועד יעד]", "kind": "number", "width": "72px", "total": "[# חלף מועד יעד]"},
         {"label": L("% פעילים", "Active %"), "value": "DIVIDE ( [# פעילים], [# פרויקטים] )", "kind": "percent", "width": "72px",
          "total": "DIVIDE ( [# פעילים], [# פרויקטים] )"}],
        L("עומס לפי בעלים", "Workload by owner"), L("ממוין לפי מספר פרויקטים", "Sorted by number of projects"),
        sort_by="[# פרויקטים]", top=5, key_label=L("בעלים", "Owner"), totals=L("סה״כ", "Total"), header_accent="cat1",
        more_label=L("ועוד {n} בעלים", "and {n} more owners"), empty_text=L("אין נתונים", "No data"), blank_label=L("לא שויך", "Unassigned")), "cat1")),
    ("labTable2", K.data_table(
        T, "כותרת",
        [{"label": L("סוג", "Type"), "value": f"CALCULATE ( MAX ( {C('סוג')} ) )", "kind": "pill", "pill_col": "סוג", "width": "1fr", "blank": L("לא שויך", "Unassigned")},
         {"label": L("סטטוס", "Status"), "value": f"CALCULATE ( MAX ( {C('סטטוס')} ) )", "kind": "pill", "pill_col": "סטטוס", "width": "1fr", "blank": L("לא שויך", "Unassigned")},
         {"label": L("מועד יעד", "Due"), "value": f"CALCULATE ( MIN ( {C('מועד יעד')} ) )", "kind": "date", "width": "92px"}],
        L("המועדים הקרובים", "Next due dates"), L("פרויקטים לפי מועד יעד", "Projects by due date"),
        sort_by=f"IF ( ISBLANK ( CALCULATE ( MIN ( {C('מועד יעד')} ) ) ), -999999, - CALCULATE ( MIN ( {C('מועד יעד')} ) ) )",
        top=6, key_label=L("פרויקט", "Project"), tip_value=f"FORMAT ( CALCULATE ( MIN ( {C('מועד יעד')} ) ), \"dd/MM/yyyy\" )",
        more_label=L("ועוד {n} פרויקטים", "and {n} more projects"), empty_text=L("אין נתונים", "No data"), blank_label=L("ללא שם", "Untitled"))),
]
for name, expr in LAB:
    MS.add("LAB " + name, expr, "LAB")

# 3 x 3 grid of 608 x 328 cards on 1920 x 1080
POS = [(32 + c * 624, 32 + r * 344, 608, 328) for r in range(3) for c in range(3)]

defs = "\n".join(f"MEASURE {T}[{n}] =\n{d['expr']}" for n, d in MS.M.items())
cols = ",\n".join(f'"{n}", [LAB {n}]' for n, _ in LAB)
flt = sys.argv[1] if len(sys.argv) > 1 else None
body = f"ROW (\n{cols}\n)"
if flt:
    body = f"CALCULATETABLE ( {body}, {flt} )"
open(os.path.join(HERE, "q_lab.dax"), "w", encoding="utf-8").write(f"DEFINE\n{defs}\nEVALUATE\n{body}\n")
src = os.environ.get("LAB_FROM")     # render-only from saved results (e.g. anonymized for a screenshot)
if not src:
    r = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "runq.ps1",
                        "-QueryFile", "q_lab.dax", "-OutFile", "r_lab.json"], cwd=HERE, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit("DAX ERROR:\n" + (r.stderr or r.stdout)[-1500:])
row = json.load(open(os.path.join(HERE, src or "r_lab.json"), encoding="utf-8-sig"))[0]

import fitjs as FJ   # FIT_JS shared with gen_preview
parts = []
for (name, _), (x, y, w, h) in zip(LAB, POS):
    doc = "<!doctype html><html><body style='margin:0'>" + row.get(name, row.get(f"[{name}]", "")) + "</body></html>"
    parts.append(f"<iframe data-name='{name}' style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:0' srcdoc=\"{html.escape(doc, quote=True)}\"></iframe>")
page = ("<!doctype html><html><head><meta charset='utf-8'></head><body style='margin:0'>"
        f"<div style='position:relative;width:1920px;height:1080px;background:{PAL['page_bg']}'>" + "".join(parts)
        + "</div><pre id='fit' style='display:none'></pre><script>" + FJ.FIT_JS + "</script></body></html>")
out = sys.argv[2] if len(sys.argv) > 2 else "lab.html"
open(os.path.join(HERE, out), "w", encoding="utf-8").write(page)
print(f"lab page: {out}")
