# -*- coding: utf-8 -*-
"""Stress test: render every HTML measure under several filter scenarios and fit/contrast-check each.

  python -I stress.py            (needs the Desktop model open; uses runq.ps1 and node fitcheck.mjs)

A dashboard that fits only the unfiltered view is not done: empty selections, a single owner,
one status, many long titles all change row counts and text lengths.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import TABLE, CFG
# Your model's scenarios go in pipeline.json, so this file never needs editing:
#   "stress": [{"name": "one-status", "filter": "{T}[Status] = \"Done\""}, ...]   ({T} = the host table)
# Each filter is a DAX filter table/expression; an "all" (unfiltered) scenario is always run first.
# Without "stress", the built-in scenarios below run - they use the reference build's columns (Hebrew: סטטוס = status, בעלים = owner,
# מחלקה = department, מזהה = id). For your model, put the same shapes in pipeline.json:
# one value per slicer-like column, a blank, an empty selection, and an all-columns-filtered worst case.
# Scenario values are data-driven or generic - never hardcode a real person's name here.
T = f"'{TABLE}'"
SCENARIOS = [
    ("all", None),
    ("status-done", f"{T}[סטטוס] = \"הושלם/פרויקט חד פעמי\""),
    ("status-design", f"{T}[סטטוס] = \"באפיון\""),
    ("one-owner", f"TOPN ( 1, FILTER ( VALUES ( {T}[בעלים] ), {T}[בעלים] <> \"\" ), CALCULATE ( COUNTROWS ( {T} ) ) )"),   # busiest owner, whoever it is
    ("no-department", f"{T}[מחלקה] = \"\""),
    ("empty", f"{T}[מזהה] = -1"),
    ("all-chips", f"FILTER ( ALL ( {T} ), {T}[סטטוס] = \"באפיון\" )"),   # marks every column filtered: header shows 4 chips
]
if CFG.get("stress"):
    SCENARIOS = [("all", None)] + [(sc["name"], sc["filter"].replace("{T}", T)) for sc in CFG["stress"] if sc.get("name") != "all"]
# several Desktop models open: pin the one to test ("port" in pipeline.json or DASH_PORT; 0 = newest that answers)
PORT = str(os.environ.get("DASH_PORT") or CFG.get("port") or 0)


def run(cmd):
    return subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding="utf-8", errors="replace")


fails = 0
for name, flt in SCENARIOS:
    q, r, h = f"q_s_{name}.dax", f"r_s_{name}.json", f"p_s_{name}.html"
    try:
        run([sys.executable, "-I", "gen_query.py", q] + ([flt] if flt else []))
        rq = run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "runq.ps1", "-QueryFile", q, "-OutFile", r, "-Port", PORT])
        if "rows: 1" not in rq.stdout:
            print(f"{name:14} DAX ERROR {rq.stderr.strip()[:200]}"); fails += 1; continue
        run([sys.executable, "-I", "gen_preview.py", r, h])
        fc = run(["node", "fitcheck.mjs", h])
        ok = fc.returncode == 0
        fails += not ok
        print(f"{name:14} {'PASS' if ok else 'FAIL'}" + ("" if ok else "\n    " + fc.stdout.strip().replace("\n", "\n    ")))
    finally:   # also on a DAX error
        for f in (q, r, h):
            try: os.remove(os.path.join(HERE, f))
            except OSError: pass
print("STRESS OK" if not fails else f"STRESS FAIL ({fails} scenario(s))")
sys.exit(1 if fails else 0)
