# -*- coding: utf-8 -*-
"""Write the measures into the TMDL and the visuals into the PBIR page. Idempotent."""
import sys, os, json, uuid, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measures import M, LAYOUT, SLICERS
from config import TMDL, TMDL_BACKUP, REPORT_DIR, PAGE_ID, TABLE as ENTITY, PAGE_DISPLAY_NAME, PARTITION_M, LINEAGE_NS

REPORT = os.path.join(REPORT_DIR, "definition")
PAGE_DIR = os.path.join(REPORT, "pages", PAGE_ID)
HTML_GUID = "htmlContent443BE3AD55E043BF878BED274D3A6865"  # HTML Content Secure (certified)
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"
from palette import P as PAL
BG = PAL["page_bg"]


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


# ---------------------------------------------------------------- TMDL
# always rebuild from the untouched backup copy so reruns stay idempotent
src = open(TMDL_BACKUP, encoding="utf-8").read()
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

for j, (name, col, x, y, w, h) in enumerate(SLICERS):
    write_visual(name, {
        "$schema": VC_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": 5000 + j, "width": w, "height": h, "tabOrder": 100 + j},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [{
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": ENTITY}}, "Property": col}},
                "queryRef": f"{ENTITY}.{col}",
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
