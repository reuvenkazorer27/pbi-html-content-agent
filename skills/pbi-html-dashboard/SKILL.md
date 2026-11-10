---
name: pbi-html-dashboard
description: Start here for any Power BI dashboard built on the HTML Content visual - KPI cards, charts, tables and panels in a PBIP/PBIR report, in LTR or RTL, plain, colorful or with motion. Use when the user asks to build, redesign or extend a Power BI dashboard or report page, to set this kit up next to their report, or mentions HTML Content, PBIP, PBIR or DAX measures that return HTML.
---

# Power BI HTML Content dashboards: start here

This skill is the entry point of the **PBI HTML Content Agent** kit. The kit's root is `${CLAUDE_PLUGIN_ROOT}` (installed as a Claude Code plugin) or the folder that contains `AGENTS.md` (cloned). Every path below is relative to that root. Read the files with your file tools; the variable is not set inside shell commands, so write out the full path there.

## 1. Read before producing anything

1. `${CLAUDE_PLUGIN_ROOT}/AGENTS.md` - what the agent is built on, the contract, the honesty rules, the working method.
2. `reference/design-system.md` and `reference/build-workflow.md`.
3. The skill that matches the request: `composite-dashboard` (the default for team dashboards), `dashboard-shell`, `html-slicers-filters`, `navigation-header-menu`, `rtl-hebrew`, `colorful-styles`, `motion`.

## 2. Set the kit up next to the user's report (once per project)

The pipeline runs next to the PBIP, not inside the installed plugin.

1. Find the user's `<project>.pbip`. The project folder holds `<project>.Report/` and `<project>.SemanticModel/`. If the report is not saved as a PBIP yet, ask the user to save it as a Power BI Project (File → Save as → .pbip).
2. Copy `${CLAUDE_PLUGIN_ROOT}/tools/pbip-html-pipeline/` to `<project folder>/_build/`. Do not overwrite an existing `_build/` without asking.
3. Make a clean backup copy of the PBIP (for example `../<project>_backup/`). The writer rebuilds the model's TMDL from it on every run.
4. Copy `_build/pipeline.example.json` to `_build/pipeline.json` and fill it in:
   - `project`: the PBIP base name.
   - `table`: the table that hosts the generated measures. List `<project>.SemanticModel/definition/tables/*.tmdl` and ask which one.
   - `page_id`: a folder under `<project>.Report/definition/pages/`.
   - `page_display_name`.
   - `backup_dir`: relative to the project folder.
   - `style`: ask for brand colors and light/dark (see `colorful-styles`). The default is `"accent"`.
5. Start `_build/measures.py` from `measures_example_projects.py` (or `measures_example_sales.py`). Replace its tables, columns, texts and `LAYOUT` with the user's model. Never invent measures without naming the tables and columns you assumed.
6. Requirements: Windows, Power BI Desktop with the project open, Python 3, Node 22+ and Microsoft Edge. No pip or npm packages are needed.

## 3. The loop (every iteration)

Run the loop in `${CLAUDE_PLUGIN_ROOT}/tools/pbip-html-pipeline/README.md`:
1. Live DAX test.
2. Exact-size preview.
3. `fitcheck.mjs` (fit + contrast).
4. `stress.py` (filter states).
5. `versions.py snapshot`.
6. `gen_pbip.py`.
7. In Desktop: Apply external changes → Refresh → screenshot.

Nothing is done without the Desktop screenshot. Report what was measured, what is only gated and what is doc-based, and hand over `checklists/validation.md`.
