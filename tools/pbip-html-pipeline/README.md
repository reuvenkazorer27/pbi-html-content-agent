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
node fitcheck.mjs preview.html --shot full.png           # 5. GATE: FIT OK (no clipping, no empty band) + CONTRAST OK (headless Edge, no npm)
python -I stress.py                                      # 6. GATE: 6 filter scenarios (all, one status, one owner, blanks, empty)
python -I versions.py snapshot "what changed" --fit "FIT OK" --results r_all.json --shot full.png   # 7. version
python -I gen_pbip.py                                    # 8. write TMDL + visual.json (padding 0, palette slicers)
# 9. Desktop: Apply external changes -> Home > Refresh -> screenshot and compare with full.png
```

Never write the PBIP (8) unless 5 and 6 pass. Never skip 7: it is what makes revert possible.

**With Power BI's own tools** (see `../../reference/build-workflow.md` §1b): push the changed measures with the Power BI Modeling MCP (`measure_operations` Update - live, no Apply), run 8 to keep the files in sync, then

```
powerbi-report-author validate <project>.pbip                     # optional PBIR validation (Node CLI)
python -I bridge.py reload                                       # report files into Desktop (not the model), waits for render
python -I bridge.py shot <page-id> desktop.png                   # real Desktop screenshot, compare with full.png
```

Without the bridge (`bridge.py` exits 2) or the MCP: Apply external changes → Home ▸ Refresh → screenshot by hand.

## Build settings (environment variables)

| Variable | Values | Effect |
| --- | --- | --- |
| `DASH_DIR` | `rtl` (default) / `ltr` | Reading direction: card `dir`/`text-align`, number alignment, arrows; `LAYOUT` and `SLICERS` are mirrored for LTR (x' = page width - x - w) |
| `DASH_LANG` | `he` (default for rtl) / `en` (default for ltr) | UI language: `labels.py` translates display strings only (model refs and data literals are masked) and fails the build on any untranslated string; month names follow the locale |
| `DASH_STYLE` | a preset (`accent` default, `tonal`, `midnight`, `sand`, `ocean`, `duotone`, `sunset`, `mint`), a JSON `make_style()` dict (`'{"brand":"#0E7490","mode":"dark"}'`), or `none` | Colorful styles from `styles.py`: one card material for KPI and analysis cards, one color mechanism (bar / tint / chip), at most one hero card, every in-card color computed for contrast. Project default: `"style"` in `pipeline.json`. See `skills/colorful-styles/SKILL.md` |
| `DASH_PALETTE` | `ocean`, `midnight`, `berry`, `vivid`, presets `exec`, `trend`, `mono`, `night`, `warm`, `forest` | Legacy palettes (setting it turns styles off): color tokens, page background, slicer colors, gradient layer and filled KPI cards (`vivid`) |

Gate every combination you ship: e.g. `DASH_DIR=ltr DASH_STYLE=accent` and `DASH_DIR=rtl DASH_STYLE=sand` each through `fitcheck.mjs` and `stress.py`. Translated strings are usually longer - the fit gate catches it; shorten the wording, not the layout.

## Files

| File | Role |
| --- | --- |
| `measures.py` (start from `measures_example_projects.py`) | Single source of truth: measures, `LAYOUT`, `SLICERS`. Inline styles only; colors only as `@@token@@`; `FONT_SCALE` remaps sizes; `CARD` root carries `height:100vh;overflow:hidden;line-height:1.35;direction:rtl;text-align:right`. |
| `layout_check.py` | Layout gate: visuals on the page, no HTML visual on top of another (full-page background layer excepted), each slicer inside exactly one HTML panel. `gen_pbip.py` runs it and writes nothing on failure; `python -I layout_check.py` runs it alone. |
| `bridge.py` | Power BI Desktop Bridge in plain Python (named pipe, JSON-RPC): `status`, `reload` (report only, then waits for render), `shot <page-id> out.png`. Exit 2 when no bridge - fall back to Apply external changes. |
| `measures_example_sales.py` + `make_sales_data.py` | Example 2: an English LTR sales dashboard on invented data, built only from the builders (icon KPIs, treemap, heat matrix, small multiples, table, lift bars) + HTML filter panel over native slicers. |
| `components.py` | Parameterized card builders: `kpi_card` (icon required),  `waterfall`, `heat_matrix`, `lift_bars`, `small_multiples`, `scatter`, `treemap_rows`, `decomp_static`, `data_table` (column kinds text / number / percent / date / bar / pill, totals row, "and N more" tooltip). Charts take `colors="category"` (stable color per category value: alphabetical rank → `cat1..cat6`); `accent(expr, "cat2")` adds a colored top band. Each returns a DAX expression for `add(...)`; titles, empty text and `blank_label` are arguments, so they work in any language. Designed and gated at 520-640 × 320-400. |
| `component_lab_example.py` | Binds every builder to a model, evaluates them on the open Desktop model and renders a gate page (`node fitcheck.mjs lab.html`). Optional DAX filter argument for empty/filtered states; `LAB_COLORS=category` colors every chart per category; `LAB_FROM=results.json` renders saved (e.g. anonymized) results without querying. |
| `fitjs.py` | The shared `fitCheck()` script injected into preview and lab pages: nothing past the 8px safe edge (`data-bleed` bands excepted) and **no empty band** at the bottom of a card larger than max(40px, 15% of its height) (`data-fill='free'` excepted). |
| `labels.py` | UI string translation (Hebrew authored → English) with masking of DAX data literals and model references; status display names. |
| `palette.py` (brand + theme) | `DASH_PRIMARY` / `DASH_ACCENT` / `DASH_DARK` derive a palette named `brand` (text tokens pushed to WCAG 4.5:1, `strong` fill safe for white text). `python -I palette.py theme out.json` writes the active palette as a report theme (View → Themes → Browse). |
| `style_check.py` | Contrast check for styles without a model: every preset plus 800 generated styles, or one style (`python -I style_check.py sand` or a JSON dict). Run it on any style you build for a user. |
| `styles.py` | The colorful-style engine: `make_style()` from brand / mode / mechanism / hero, `PRESETS`, `ROLES`, `apply(expr, role)` for per-card tokens, `CARD` (the shared card root), `readable()` for contrast-safe colors. Registers the active style's palette in `palette.py`. |
| `palette.py` | Color tokens for `ocean` (light), `midnight` (dark), `berry` (colorful). Every palette defines every token, including `*_text` variants chosen for WCAG 4.5:1 on their soft backgrounds. Switch: `DASH_PALETTE=midnight`. Page background, preview and slicer colors follow the palette. |
| `gen_query.py` / `runq.ps1` | Live DAX test against the open model through Desktop's own AdomdClient. Optional 2nd arg to `gen_query.py` = a DAX filter table (used by `stress.py`). |
| `gen_preview.py` | Places each measure's real HTML in an iframe of its exact visual size on the page background; defines `fitCheck()` (8px safe edge). |
| `fitcheck.mjs` | Headless Edge via DevTools protocol + Node's built-in WebSocket. Waits until every card has rendered, runs `fitCheck()` and a WCAG contrast check on every text element (4.5:1, large text 3:1); optional screenshot. Closes Edge over CDP and kills anything left on its temp profile (Edge's children outlive a plain kill). Exit 1 on failure. |
| `stress.py` | Re-renders all cards under filter scenarios and gates each with `fitcheck.mjs`. |
| `regress.py` | Byte-compares every measure's HTML with the last version: refactors must print IDENTICAL; intended changes list exactly which cards changed. |
| `versions.py` | `snapshot` / `list` / `diff vA vB` / `revert vN` (auto pre-revert snapshot). A version = zip of .pbip + report/model definitions + `_build` sources + the real HTML outputs + screenshot, in `<project>/_versions/`. After revert: Apply external changes -> Refresh. |
| `config.py` / `pipeline.json` | Project settings (PBIP name, host table, page, backup, optional partition M); no project names or paths are hardcoded in the scripts. |
| `gen_pbip.py` | Measures into TMDL (rebuilt from the backup copy each run), optional partition M swap, page background from palette, `visual.json` per visual with padding 0 / chrome off, page canvas size from `PAGE_W`/`PAGE_H` (default 1920×1080), slicer `items.fontColor`/`items.background` from palette, AppSource visual registered in `report.json`. |
