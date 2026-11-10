# PBIP HTML pipeline - build, gate, version, write, apply

Measured end to end in Power BI Desktop (Oct 2026 release) on the kit's reference build, a project-portfolio dashboard (`measures_example_projects.py`). See `../../reference/design-system.md` and `../../reference/build-workflow.md` for why each step exists.

## Setup

1. Copy this folder next to your PBIP as `_build/` and make a clean backup copy of the PBIP (the writer rebuilds the TMDL from it on every run).
2. Copy `pipeline.example.json` to `pipeline.json` and fill it: `project` (the PBIP base name), `table` (the table that hosts the generated measures), `page_id` (folder under `definition/pages`), `page_display_name`, `backup_dir` (relative to the project folder), optional `partition_m` (a file in `_build` whose M replaces the table's partition) and `lineage_namespace` (keep it stable once measures exist).
3. Write your measures and `LAYOUT` in `measures.py`, starting from `measures_example_projects.py`; adapt the scenarios in `stress.py` to your columns.

## The loop (every iteration, in this order)

```
python -I gen_query.py q_all.dax                         # 1. DEFINE every measure + EVALUATE all HTML measures
powershell -File runq.ps1 -QueryFile q_all.dax -OutFile r_all.json   # 2. run it on the open Desktop model (port auto)
python -I regress.py r_all.json                          # 3. which cards changed vs the last version (byte compare)
python -I gen_preview.py r_all.json preview.html         # 4. exact-size preview of every card
node fitcheck.mjs preview.html --shot full.png           # 5. GATE: FIT OK + CONTRAST OK (headless Edge, no npm)
python -I stress.py                                      # 6. GATE: 6 filter scenarios (all, one status, one owner, blanks, empty)
python -I versions.py snapshot "what changed" --fit "FIT OK" --results r_all.json --shot full.png   # 7. version
python -I gen_pbip.py                                    # 8. write TMDL + visual.json (padding 0, palette slicers)
# 9. Desktop: Apply external changes -> Home > Refresh -> screenshot and compare with full.png
```

Never write the PBIP (8) unless 5 and 6 pass. Never skip 7: it is what makes revert possible.

## Build settings (environment variables)

| Variable | Values | Effect |
| --- | --- | --- |
| `DASH_DIR` | `rtl` (default) / `ltr` | Reading direction: card `dir`/`text-align`, number alignment, arrows; `LAYOUT` and `SLICERS` are mirrored for LTR (x' = page width - x - w) |
| `DASH_LANG` | `he` (default for rtl) / `en` (default for ltr) | UI language: `labels.py` translates display strings only (model refs and data literals are masked) and fails the build on any untranslated string; month names follow the locale |
| `DASH_PALETTE` | `ocean`, `midnight`, `berry`, `vivid`, presets `exec`, `trend`, `mono`, `night`, `warm`, `forest` | Color tokens, page background, slicer colors, gradient layer and filled KPI cards (`vivid`) |

Gate every combination you ship: e.g. `DASH_DIR=ltr DASH_PALETTE=ocean` and `DASH_DIR=rtl DASH_PALETTE=vivid` each through `fitcheck.mjs` and `stress.py`. Translated strings are usually longer - the fit gate catches it; shorten the wording, not the layout.

## Files

| File | Role |
| --- | --- |
| `measures.py` (start from `measures_example_projects.py`) | Single source of truth: measures, `LAYOUT`, `SLICERS`. Inline styles only; colors only as `@@token@@`; `FONT_SCALE` remaps sizes; `CARD` root carries `height:100vh;overflow:hidden;line-height:1.35;direction:rtl;text-align:right`. |
| `components.py` | Parameterized card builders: `waterfall`, `heat_matrix`, `lift_bars`, `small_multiples`, `scatter`, `treemap_rows`, `decomp_static`, `data_table` (column kinds text / number / percent / date / bar / pill, totals row, "and N more" tooltip). Charts take `colors="category"` (stable color per category value: alphabetical rank → `cat1..cat6`); `accent(expr, "cat2")` adds a colored top band. Each returns a DAX expression for `add(...)`; titles, empty text and `blank_label` are arguments, so they work in any language. Designed and gated at 520-640 × 320-400. |
| `component_lab_example.py` | Binds every builder to a model, evaluates them on the open Desktop model and renders a gate page (`node fitcheck.mjs lab.html`). Optional DAX filter argument for empty/filtered states; `LAB_COLORS=category` colors every chart per category; `LAB_FROM=results.json` renders saved (e.g. anonymized) results without querying. |
| `fitjs.py` | The shared `fitCheck()` script injected into preview and lab pages. |
| `labels.py` | UI string translation (Hebrew authored → English) with masking of DAX data literals and model references; status display names. |
| `palette.py` (brand + theme) | `DASH_PRIMARY` / `DASH_ACCENT` / `DASH_DARK` derive a palette named `brand` (text tokens pushed to WCAG 4.5:1, `strong` fill safe for white text). `python -I palette.py theme out.json` writes the active palette as a report theme (View → Themes → Browse). |
| `palette.py` | Color tokens for `ocean` (light), `midnight` (dark), `berry` (colorful). Every palette defines every token, including `*_text` variants chosen for WCAG 4.5:1 on their soft backgrounds. Switch: `DASH_PALETTE=midnight`. Page background, preview and slicer colors follow the palette. |
| `gen_query.py` / `runq.ps1` | Live DAX test against the open model through Desktop's own AdomdClient. Optional 2nd arg to `gen_query.py` = a DAX filter table (used by `stress.py`). |
| `gen_preview.py` | Places each measure's real HTML in an iframe of its exact visual size on the page background; defines `fitCheck()` (8px safe edge). |
| `fitcheck.mjs` | Headless Edge via DevTools protocol + Node's built-in WebSocket. Waits until every card has rendered, runs `fitCheck()` and a WCAG contrast check on every text element (4.5:1, large text 3:1); optional screenshot. Closes Edge over CDP and kills anything left on its temp profile (Edge's children outlive a plain kill). Exit 1 on failure. |
| `stress.py` | Re-renders all cards under filter scenarios and gates each with `fitcheck.mjs`. |
| `regress.py` | Byte-compares every measure's HTML with the last version: refactors must print IDENTICAL; intended changes list exactly which cards changed. |
| `versions.py` | `snapshot` / `list` / `diff vA vB` / `revert vN` (auto pre-revert snapshot). A version = zip of .pbip + report/model definitions + `_build` sources + the real HTML outputs + screenshot, in `<project>/_versions/`. After revert: Apply external changes -> Refresh. |
| `config.py` / `pipeline.json` | Project settings (PBIP name, host table, page, backup, optional partition M); no project names or paths are hardcoded in the scripts. |
| `gen_pbip.py` | Measures into TMDL (rebuilt from the backup copy each run), optional partition M swap, page background from palette, `visual.json` per visual with padding 0 / chrome off, slicer `items.fontColor`/`items.background` from palette, AppSource visual registered in `report.json`. |
