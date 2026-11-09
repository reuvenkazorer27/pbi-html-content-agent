# -*- coding: utf-8 -*-
"""Project settings for the pipeline, read from pipeline.json next to this file.
Copy pipeline.example.json to pipeline.json and fill it for your PBIP - no project
names, tables or paths are hardcoded in the scripts."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # the PBIP project folder (this folder lives in <project>/_build)
_PATH = os.path.join(HERE, "pipeline.json")
if not os.path.exists(_PATH):
    raise SystemExit("pipeline.json not found - copy pipeline.example.json to pipeline.json and fill it for your PBIP")
CFG = json.load(open(_PATH, encoding="utf-8"))
for key in ("project", "table", "page_id", "backup_dir"):
    if not CFG.get(key):
        raise SystemExit(f"pipeline.json: '{key}' is required")

PROJECT = CFG["project"]                                       # <project>.pbip / .Report / .SemanticModel
TABLE = CFG["table"]                                           # table that hosts the generated measures
PAGE_ID = CFG["page_id"]                                       # folder name under definition/pages
PAGE_DISPLAY_NAME = CFG.get("page_display_name")               # optional: page title shown in Desktop
BACKUP_DIR = os.path.normpath(os.path.join(ROOT, CFG["backup_dir"]))   # clean copy of the PBIP (rebuild source)
PARTITION_M = CFG.get("partition_m")                           # optional: file in _build whose M replaces the table partition
LINEAGE_NS = CFG.get("lineage_namespace", "pbi-html-dashboard")   # keep stable: measure lineage tags derive from it

REPORT_DIR = os.path.join(ROOT, f"{PROJECT}.Report")
MODEL_DIR = os.path.join(ROOT, f"{PROJECT}.SemanticModel")
TMDL = os.path.join(MODEL_DIR, "definition", "tables", f"{TABLE}.tmdl")
TMDL_BACKUP = os.path.join(BACKUP_DIR, f"{PROJECT}.SemanticModel", "definition", "tables", f"{TABLE}.tmdl")
