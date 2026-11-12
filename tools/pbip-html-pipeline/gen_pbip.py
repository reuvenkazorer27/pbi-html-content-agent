# -*- coding: utf-8 -*-
"""Write the measures into the TMDL and the visuals into the PBIR page. Idempotent."""
import sys, os, json, uuid, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measures import M, LAYOUT, SLICERS
from config import TMDL, TMDL_BACKUP, REPORT_DIR, PAGE_DIR, PAGE_ID, TABLE as ENTITY, PAGE_DISPLAY_NAME, PARTITION_M, LINEAGE_NS, require_paths

require_paths()
import measures as _ms
from layout_check import check as _layout_check
# Several pages (optional): measures.PAGES = [{"id": folder, "name": display name, "LAYOUT": [...], "SLICERS": [...],
#   "NAV": [(visual name, target page id, x, y, w, h), ...]}, ...]; the first page is pipeline.json's page_id.
# Without PAGES: one page from LAYOUT / SLICERS (+ optional measures.NAV), exactly as before.
PAGES = getattr(_ms, "PAGES", None) or [{"id": PAGE_ID, "name": PAGE_DISPLAY_NAME, "LAYOUT": LAYOUT, "SLICERS": SLICERS,
                                         "NAV": getattr(_ms, "NAV", [])}]
_ids = {p["id"] for p in PAGES}
for _p in PAGES:
    for _n, _t, *_r in _p.get("NAV", []):
        if _t not in _ids:
            raise SystemExit(f"nav button {_n} on page {_p['id']} points to page {_t!r}, which is not in PAGES (nothing written)")
    _problems = _layout_check(_p["LAYOUT"], list(_p.get("SLICERS", [])) + [(n, t, *r) for n, t, *r in _p.get("NAV", [])],
                              getattr(_ms, "PAGE_W", 1920), getattr(_ms, "PAGE_H", 1080))
    if _problems:   # never place a visual on top of another - fix LAYOUT / SLICERS / NAV first
        raise SystemExit(f"layout check failed on page {_p['id']}, nothing written:\n  " + "\n  ".join(_problems))
REPORT = os.path.join(REPORT_DIR, "definition")
HTML_GUID = "htmlContent443BE3AD55E043BF878BED274D3A6865"  # HTML Content Secure (certified)
VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"
from palette import P as PAL
BG = PAL["page_bg"]


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


# ---------------------------------------------------------------- before writing
# Desktop with unsaved changes may not offer "Apply external changes" and a later save overwrites these files
# (bridge.instances() never contacts a Desktop that is still opening, and every bridge request has a timeout)
try:
    import bridge as _br
    from config import PROJECT as _PROJECT
    _all = _br.instances(_PROJECT)   # [] when no Desktop has the bridge: nothing to check, nothing to say
    _mine = [i for i in _all if os.path.basename(i.get("currentFilePath") or "").lower() == f"{_PROJECT}.pbip".lower()]
    for _i in _mine:
        if _i.get("hasUnsavedChanges"):
            print(f"WARNING: Desktop (pid {_i['pid']}) has unsaved changes in {_PROJECT}.pbip - the Apply banner may not show, "
                  "and saving in Desktop now would overwrite what is written here. See reference/build-workflow.md §1.")
    _unknown = [i for i in _all if i.get("error")]
    if _unknown and not _mine:   # a window we could not ask may be this project's: say so once, not per window
        print(f"note: unsaved-changes check incomplete - {len(_unknown)} Desktop window(s) did not answer the bridge "
              f"({_unknown[0]['error']})")
except (Exception, SystemExit) as _e:   # never block the write on the bridge - but say that the check did not run
    print(f"note: unsaved-changes check skipped - the Desktop Bridge failed: {_e}")


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

# ---------------------------------------------------------------- optional: the style as the report's theme
# pipeline.json "report_theme": true -> native visuals (slicers, any built-in chart) and the --pbi-theme-* variables
# follow the style. A report that already has another custom theme keeps it unless "report_theme": "replace" (it may be
# the organization's own theme - ask before replacing it).
from config import CFG as _CFG
_rt = _CFG.get("report_theme")
if _rt:
    import palette as _pal
    _theme = _pal.theme_json()
    _fname = f"{_theme['name']}.json"
    # powerbi-report-author validate: customTheme.name, the resource item name/path AND the theme file's own "name"
    # must all be the same string with ".json" (a bare name mis-applies the theme in the Service)
    _theme["name"] = _fname
    _tc = rep.get("themeCollection") or {}
    _cur = _tc.get("customTheme")
    _curname = (_cur or {}).get("name") or ""
    _base = _tc.get("baseTheme") or {}
    if not _base.get("reportVersionAtImport"):   # nothing to copy the version from: skip, never crash mid-write
        print("report theme: skipped - report.json has no baseTheme to take reportVersionAtImport from "
              "(apply the theme in Desktop: View > Themes > Browse, `python -I palette.py theme out.json`)")
    elif _cur and _curname != _fname and not _curname.startswith("pbi-html-") and _rt != "replace":
        print(f"report theme: kept the report's own custom theme {_curname} (\"report_theme\": \"replace\" overrides it)")
    else:
        _dst = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
        os.makedirs(_dst, exist_ok=True)
        if _curname != _fname and _curname.startswith("pbi-html-"):
            try:
                os.remove(os.path.join(_dst, os.path.basename(_curname)))   # our previous theme file, superseded
            except OSError:
                pass
        json.dump(_theme, open(os.path.join(_dst, _fname), "w", encoding="utf-8"), indent=2)
        rep["themeCollection"]["customTheme"] = {"name": _fname, "reportVersionAtImport": _base["reportVersionAtImport"],
                                                 "type": "RegisteredResources"}
        _pk = [x for x in rep.get("resourcePackages", []) if x.get("name") != "RegisteredResources"]
        _old = next((x for x in rep.get("resourcePackages", []) if x.get("name") == "RegisteredResources"), None)
        _items = [i for i in (_old or {}).get("items", []) if i.get("type") != "CustomTheme"]
        _items.append({"name": _fname, "path": _fname, "type": "CustomTheme"})
        _pk.append({"name": "RegisteredResources", "type": "RegisteredResources", "items": _items})
        rep["resourcePackages"] = _pk
        print(f"report theme: {_fname}")
json.dump(rep, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- pages and visuals
NO_CHROME = {
    "background": [{"properties": {"show": lit("false")}}],
    "border": [{"properties": {"show": lit("false")}}],
    "title": [{"properties": {"show": lit("false")}}],
    "dropShadow": [{"properties": {"show": lit("false")}}],
    "visualHeader": [{"properties": {"show": lit("false")}}],
    # the Fluent 2 theme pads every visual 16/14/16/16 -> the HTML viewport would be 30px shorter than the frame
    "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"), "left": lit("0D"), "right": lit("0D")}}],
}
import shutil
PAGES_DIR = os.path.join(REPORT, "pages")
_template = json.load(open(os.path.join(PAGE_DIR, "page.json"), encoding="utf-8"))


def _slicer_field(col):
    """slicer column: a column of the host table, or any table's column written 'Table'[Column] / Table[Column]"""
    mm = re.match(r"^'?(.+?)'?\[(.+)\]$", col)
    return (mm.group(1), mm.group(2)) if mm else (ENTITY, col)


def write_page(pg):
    pdir = os.path.join(PAGES_DIR, pg["id"])
    os.makedirs(pdir, exist_ok=True)
    pp = os.path.join(pdir, "page.json")
    page = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else {"$schema": _template.get("$schema")}
    page["name"] = pg["id"]
    if pg.get("name"):
        page["displayName"] = pg["name"]
    page.setdefault("displayName", pg["id"])
    # the layout is authored for a fixed canvas: write it, or a new (scaffolded) page stays 1280x720 and clips everything
    page["width"], page["height"] = getattr(_ms, "PAGE_W", 1920), getattr(_ms, "PAGE_H", 1080)
    page["displayOption"] = "FitToPage"
    color = {"solid": {"color": lit(f"'{BG}'")}}
    page["objects"] = {
        "background": [{"properties": {"color": color, "transparency": lit("0D")}}],
        "outspace": [{"properties": {"color": color, "transparency": lit("0D")}}],
    }
    json.dump(page, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    vdir = os.path.join(pdir, "visuals")

    def write_visual(name, body):
        d = os.path.join(vdir, name)
        os.makedirs(d, exist_ok=True)
        json.dump(body, open(os.path.join(d, "visual.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    layout, slicers, nav = pg["LAYOUT"], pg.get("SLICERS", []), pg.get("NAV", [])
    # generated visuals (hc*/sl*/nv*) that the current layout no longer has would point at a removed measure
    keep = {n for n, *_ in layout} | {n for n, *_ in slicers} | {n for n, *_ in nav}
    for _d in sorted(os.listdir(vdir)) if os.path.isdir(vdir) else []:
        if _d[:2] in ("hc", "sl", "nv") and _d not in keep:
            shutil.rmtree(os.path.join(vdir, _d))
            print("removed stale generated visual:", pg["id"], _d)
    for i, (name, meas, x, y, w, h) in enumerate(layout):
        write_visual(name, {
            "$schema": VC_SCHEMA,
            "name": name,
            "position": {"x": x, "y": y, "z": 1000 + i, "width": w, "height": h, "tabOrder": i},
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
    for j, (name, col, x, y, w, h) in enumerate(slicers):
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
    # native page-navigation buttons over the HTML menu items (skills/navigation-header-menu): blank and invisible,
    # the action in visualContainerObjects.visualLink (names from `powerbi-report-author formatting describe-object`)
    off = {"properties": {"show": lit("false")}}
    for k, (name, target, x, y, w, h) in enumerate(nav):
        write_visual(name, {
            "$schema": VC_SCHEMA,
            "name": name,
            "position": {"x": x, "y": y, "z": 6000 + k, "width": w, "height": h, "tabOrder": 200 + k},
            "visual": {
                "visualType": "actionButton",
                "objects": {
                    "icon": [{"properties": {"shapeType": lit("'blank'")}, "selector": {"id": "default"}}],
                    "text": [off], "outline": [off],
                    "fill": [{"properties": {"show": lit("false"), "transparency": lit("100D")}, "selector": {"id": st}}
                             for st in ("default", "hover", "selected", "disabled")],
                },
                "visualContainerObjects": {
                    **{kk: vv for kk, vv in NO_CHROME.items() if kk != "padding"},
                    "visualLink": [{"properties": {"show": lit("true"), "type": lit("'PageNavigation'"),
                                                   "navigationSection": lit(f"'{target}'")}}],
                },
            },
            "howCreated": "InsertVisualButton",
        })
    return len(layout) + len(slicers) + len(nav)


_count = sum(write_page(pg) for pg in PAGES)
# pages.json: every generated page in order, the first one opens
_pj = os.path.join(PAGES_DIR, "pages.json")
_pages = json.load(open(_pj, encoding="utf-8"))
_order = [p["id"] for p in PAGES]
_pages["pageOrder"] = _order + [p for p in _pages.get("pageOrder", []) if p not in _order]
_pages["activePageName"] = _order[0]
json.dump(_pages, open(_pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("pages:", len(PAGES), "| visuals:", _count)

# Microsoft's PBIR validator, when installed (doc: reference/build-workflow.md §1b) - e.g. an unregistered custom visual
import shutil as _sh, subprocess as _sp
_KNOWN_FALSE = {"PBIR_SLICER_HEIGHT_BELOW_FLOOR"}   # a 40px slicer with padding 0 renders fine in Desktop (measured)


def _findings(node, out):
    """every finding in the validator's JSON as {code, severity, message, file}. The CLI keys findings by code:
    data.diagnostics = {CODE: {"severity": ..., "items": [{"message", "file"}, ...]}}; objects that carry their own
    "code" field are taken as they are."""
    if isinstance(node, dict):
        diag = node.get("diagnostics")
        if isinstance(diag, dict):
            for code, d in diag.items():
                d = d if isinstance(d, dict) else {}
                for it in (d.get("items") or [{}]):
                    out.append({"code": code, "severity": d.get("severity"),
                                "message": (it or {}).get("message"), "file": (it or {}).get("file")})
        elif "code" in node:
            out.append(node)
        for k, v in node.items():
            if not (k == "diagnostics" and isinstance(diag, dict)):
                _findings(v, out)
    elif isinstance(node, list):
        for v in node:
            _findings(v, out)
    return out


_cli = _sh.which("powerbi-report-author")
if _cli:
    from config import ROOT as _ROOT, PROJECT as _P
    _r = _sp.run([_cli, "validate", os.path.join(_ROOT, f"{_P}.pbip")], capture_output=True, text=True, encoding="utf-8", errors="replace")
    _raw = (_r.stdout or "") + (_r.stderr or "")
    try:
        _doc = json.loads(_r.stdout[_r.stdout.index("{"):] if "{" in _r.stdout else _r.stdout)
        _all = _findings(_doc, [])
        _failed = '"result": "failed"' in json.dumps(_doc) or '"result":"failed"' in _r.stdout
    except ValueError:
        _all, _failed = None, False
    if _all is None:
        print("powerbi-report-author validate (unparsed):", _raw.strip()[-800:] or f"exit {_r.returncode}")
    else:
        _real = [f for f in _all if f.get("code") not in _KNOWN_FALSE]
        _sev = lambda f: str(f.get("severity") or f.get("level") or "").lower()
        _err = [f for f in _real if _sev(f) in ("error", "fatal")]
        _known = len(_all) - len(_real)
        if _failed and not _all:   # the validator failed but nothing was parsed: never report OK on a format we cannot read
            print("powerbi-report-author validate: WARNING - the validator reports 'failed' but no finding could be read:",
                  _raw.strip()[-800:])
        print(f"powerbi-report-author validate: {'OK' if not _err else 'ERRORS'} - {len(_err)} error(s), "
              f"{len(_real) - len(_err)} other finding(s), {_known} known false positive(s) ignored")
        for f in _real[:12]:
            print(f"  {_sev(f) or 'info'}: {f.get('code')} - {str(f.get('message') or '')[:160]}")
        if any("VISUAL_TYPE_UNKNOWN" in str(f.get("code")) for f in _all):
            print("  -> a visual type is not registered: the HTML Content visual will show 'add it to this report first'")
