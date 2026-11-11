# -*- coding: utf-8 -*-
"""Write the measures into the TMDL and the visuals into the PBIR page. Idempotent."""
import sys, os, json, uuid, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measures import M, LAYOUT, SLICERS
from config import TMDL, TMDL_BACKUP, REPORT_DIR, PAGE_DIR, TABLE as ENTITY, PAGE_DISPLAY_NAME, PARTITION_M, LINEAGE_NS, require_paths

require_paths()
import measures as _ms
from layout_check import check as _layout_check
_problems = _layout_check(LAYOUT, SLICERS, getattr(_ms, "PAGE_W", 1920), getattr(_ms, "PAGE_H", 1080))
if _problems:   # never place a visual on top of another - fix LAYOUT / SLICERS first
    raise SystemExit("layout check failed, nothing written:\n  " + "\n  ".join(_problems))
REPORT = os.path.join(REPORT_DIR, "definition")
HTML_GUID = "htmlContent443BE3AD55E043BF878BED274D3A6865"  # HTML Content Secure (certified)
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"
from palette import P as PAL
BG = PAL["page_bg"]


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


# ---------------------------------------------------------------- before writing
# Desktop with unsaved changes may not offer "Apply external changes" and a later save overwrites these files
try:
    import bridge as _br
    from config import PROJECT as _PROJECT
    for _i in _br.instances():
        if os.path.basename(_i.get("currentFilePath") or "").lower() == f"{_PROJECT}.pbip".lower() and _i.get("hasUnsavedChanges"):
            print(f"WARNING: Desktop (pid {_i['pid']}) has unsaved changes in {_PROJECT}.pbip - the Apply banner may not show, "
                  "and saving in Desktop now would overwrite what is written here. See reference/build-workflow.md §1.")
except Exception:
    pass   # no bridge: nothing to check


def _strip_generated(text):
    """the host table's TMDL without the measures this pipeline generates (they are rebuilt from measures.py)"""
    out, skip = [], False
    for line in text.splitlines(keepends=True):
        mm = re.match(r"\tmeasure '?(.*?)'? =", line)
        if mm:
            skip = mm.group(1) in M
        elif re.match(r"\t\S", line):
            skip = False
        if not skip:
            out.append(line)
    return "".join(out)


def _objects(text):
    return set(re.findall(r"^\t(?:column|partition|hierarchy|calculationGroup) .*$", text, flags=re.M))


# ---------------------------------------------------------------- TMDL
# always rebuild from the untouched backup copy so reruns stay idempotent
src = open(TMDL_BACKUP, encoding="utf-8").read()
_live = open(TMDL, encoding="utf-8").read()
_new = sorted(_objects(_live) - _objects(src))
if "--refresh-backup" in sys.argv:
    open(TMDL_BACKUP, "w", encoding="utf-8", newline="\n").write(_strip_generated(_live))
    src = open(TMDL_BACKUP, encoding="utf-8").read()
    print("backup refreshed from the live TMDL (generated measures removed)")
elif _new:
    raise SystemExit("the model changed after the backup was made - these objects of the host table are not in the backup and "
                     "would be dropped:\n  " + "\n  ".join(o.strip() for o in _new) +
                     "\nSave in Desktop, then run: python -I gen_pbip.py --refresh-backup   (nothing was written)")
# optional: replace the table's partition M with a file from _build (pipeline.json "partition_m")
if PARTITION_M:
    mcode = open(os.path.join(HERE, PARTITION_M), encoding="utf-8").read().strip("\n")
    body = "".join("\t\t\t\t" + l + "\n" for l in mcode.splitlines())
    src, n = re.subn(r"(\tpartition [^\n]*= m\n\t\tmode: import\n\t\tsource =\n)(.*?)(\n\tannotation PBI_ResultType)",
                     lambda mm: mm.group(1) + body + mm.group(3), src, flags=re.S)
    assert n == 1, "partition block not found"
    print(f"partition source: {PARTITION_M}")
blocks = []
for name, d in M.items():
    tag = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{LINEAGE_NS}/" + name))
    lines = [l for l in d["expr"].splitlines() if l.strip()]
    b = f"\tmeasure '{name}' =\n" + "".join("\t\t\t" + l + "\n" for l in lines)
    if d["fmt"]:
        b += f"\t\tformatString: {d['fmt']}\n"
    b += f"\t\tdisplayFolder: {d['folder']}\n\t\tlineageTag: {tag}\n\n"
    blocks.append(b)
gen = "".join(blocks)
# insert right after the table header + lineageTag
m = re.search(r"^table .*\n\tlineageTag: .*\n\n", src, flags=re.M)
src = src[:m.end()] + gen + src[m.end():]
open(TMDL, "w", encoding="utf-8", newline="\n").write(src)
print("tmdl measures:", len(M))

# ---------------------------------------------------------------- report.json: register the AppSource visual
rp = os.path.join(REPORT, "report.json")
rep = json.load(open(rp, encoding="utf-8"))
pcv = rep.setdefault("publicCustomVisuals", [])
if HTML_GUID not in pcv:
    pcv.append(HTML_GUID)
json.dump(rep, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- page.json
pp = os.path.join(PAGE_DIR, "page.json")
page = json.load(open(pp, encoding="utf-8"))
if PAGE_DISPLAY_NAME:
    page["displayName"] = PAGE_DISPLAY_NAME
# the layout is authored for a fixed canvas: write it, or a new (scaffolded) page stays 1280x720 and clips everything
page["width"], page["height"] = getattr(_ms, "PAGE_W", 1920), getattr(_ms, "PAGE_H", 1080)
page["displayOption"] = "FitToPage"
color = {"solid": {"color": lit(f"'{BG}'")}}
page["objects"] = {
    "background": [{"properties": {"color": color, "transparency": lit("0D")}}],
    "outspace": [{"properties": {"color": color, "transparency": lit("0D")}}],
}
json.dump(page, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- visuals
NO_CHROME = {
    "background": [{"properties": {"show": lit("false")}}],
    "border": [{"properties": {"show": lit("false")}}],
    "title": [{"properties": {"show": lit("false")}}],
    "dropShadow": [{"properties": {"show": lit("false")}}],
    "visualHeader": [{"properties": {"show": lit("false")}}],
    # the Fluent 2 theme pads every visual 16/14/16/16 -> the HTML viewport would be 30px shorter than the frame
    "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"), "left": lit("0D"), "right": lit("0D")}}],
}


def write_visual(name, body):
    d = os.path.join(PAGE_DIR, "visuals", name)
    os.makedirs(d, exist_ok=True)
    json.dump(body, open(os.path.join(d, "visual.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# generated visuals (hc*/sl*) that the current layout no longer has would point at a removed measure
import shutil
_keep = {n for n, *_ in LAYOUT} | {n for n, *_ in SLICERS}
_vdir = os.path.join(PAGE_DIR, "visuals")
for _d in sorted(os.listdir(_vdir)) if os.path.isdir(_vdir) else []:
    if _d[:2] in ("hc", "sl") and _d not in _keep:
        shutil.rmtree(os.path.join(_vdir, _d))
        print("removed stale generated visual:", _d)

z = 1000
for i, (name, meas, x, y, w, h) in enumerate(LAYOUT):
    write_visual(name, {
        "$schema": VC_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": z + i, "width": w, "height": h, "tabOrder": i},
        "visual": {
            "visualType": HTML_GUID,
            "query": {"queryState": {"content": {"projections": [{
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": ENTITY}}, "Property": meas}},
                "queryRef": f"{ENTITY}.{meas}",
                "nativeQueryRef": meas,
            }]}}},
            "visualContainerObjects": NO_CHROME,
            "drillFilterOtherVisuals": True,
        },
    })

def _slicer_field(col):
    """slicer column: a column of the host table, or any table's column written 'Table'[Column] / Table[Column]"""
    mm = re.match(r"^'?(.+?)'?\[(.+)\]$", col)
    return (mm.group(1), mm.group(2)) if mm else (ENTITY, col)


for j, (name, col, x, y, w, h) in enumerate(SLICERS):
    ent, col = _slicer_field(col)
    write_visual(name, {
        "$schema": VC_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": 5000 + j, "width": w, "height": h, "tabOrder": 100 + j},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [{
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": col}},
                "queryRef": f"{ent}.{col}",
                "nativeQueryRef": col,
                "active": True,
            }]}}},
            "objects": {
                "data": [{"properties": {"mode": lit("'Dropdown'")}}],
                "header": [{"properties": {"show": lit("false")}}],
                # palette-driven so a dark page never gets a white dropdown (verified names: items.fontColor / items.background)
                "items": [{"properties": {
                    "fontColor": {"solid": {"color": lit(f"'{PAL['slicer_fg']}'")}},
                    "background": {"solid": {"color": lit(f"'{PAL['slicer_bg']}'")}},
                }}],
            },
            "visualContainerObjects": NO_CHROME,
            "drillFilterOtherVisuals": True,
        },
    })
print("visuals:", len(LAYOUT) + len(SLICERS))
