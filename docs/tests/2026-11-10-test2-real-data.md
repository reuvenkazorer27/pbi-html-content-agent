# PBI HTML Content Agent 1.0.0: second test, on real data

> Verifies the first independent test ("REPORT.md", P1-P11, not in this repo; each finding is summarized in §1). Screenshots referenced below stay with the test project, not in the repo. The fixes are in the PR that added this file; §8 lists them, and "Left as follow-ups" what is not fixed yet.

Tester: a Claude Code session (Opus 5.5). Dates: 10-11 Nov 2026.
Kit: `npx pbi-html-content-agent@1.0.0` (npm). Data: the owner's Hebrew demo workbook `דאטה_דמו_BI_בעברית.xlsx` (fictional office-equipment and electronics retailer): 1,200 sales, 10 products, 150 customers, 6 branches and a 730-day calendar (2025-2026). No data was invented.

Two projects, each in its own folder with its own git repo, created **before** the kit ran:

| Project | Model | Route | Verified where |
| --- | --- | --- | --- |
| `kit-test-2/RetailHe` | Built by me: a blank report saved as PBIP (GUI), then everything else with the **Power BI Modeling MCP** | Kit + Trove + cua (Desktop GUI) | Headless gates; written to Desktop was not finished (see §4) |
| `BI/new_demo` | Built by the owner in Desktop: the same workbook, already loaded and saved as PBIP | **Kit only**, at the owner's request (no Trove, no cua) | Headless gates + **Power BI Desktop** (bridge screenshot) |

At the owner's direction I stopped after **one version** per project (no fix loops), and the colorful-styles previews were limited to the 3 already rendered.

## 1. Verdict on REPORT.md

| # | Finding (REPORT.md) | Verdict | Evidence |
| --- | --- | --- | --- |
| P1 | `versions.py` commits/tags an enclosing repo | **CONDITIONAL**: the unrelated-work damage happens only when the project sits inside a parent repo. `tag -f` and the over-broad `add -A` are **CONFIRMED** in any repo. | **Own repo** (`kit-test-2`, `new_demo`): commits stayed inside the project. **Nested** (scratch: parent repo + project subfolder): the commit `v001: nested test` included the parent's `unrelated_wip.txt`. **`tag -f`**: a pre-existing `v001` tag (on the baseline) was silently moved to the snapshot commit. **`add -A`** in the own repo committed `_build/__pycache__/*.pyc`, the scratch files (`q_all.dax`, `r_all.json`, `preview.html`, PNGs) and `_versions/*.zip`, although build-workflow §5 says the zips are "ignored by git". Nothing writes that ignore rule. |
| P2 | Builders fail the fill gate under one-value filters | **CONFIRMED** (both projects) | **RetailHe** stress, 3/9 scenarios fail: `heat_matrix` 198px band, `data_table` 170px, `treemap_rows` 147px, `lift_bars` 208px. **new_demo**: fails even **unfiltered** on short fact columns (3 channels: heat matrix 64px; 4 payment methods: lift 112px). Fixed with a `_stretch()` string patch (outside the API, like the first tester), and stress still failed 4/8 (one row, one tile). Causes: `lift_bars` rows `height:28px`, `heat_matrix` rows `max-height:64px`, `data_table` 30px rows, a single treemap tile. |
| P3 | No "Apply external changes" banner | **NOT REPRODUCED** when Desktop had no unsaved changes: after `gen_pbip.py` on new_demo (`hasUnsavedChanges: false`), the owner saw the banner. **CONDITIONAL**: the flag can stay `true`. | **RetailHe** after MCP edits: `hasUnsavedChanges: true` survived three Ctrl+S presses ("Last saved" kept updating). A freshly opened `new_demo.pbip` also reports `true`. That is exactly the state in which REPORT.md saw no banner. **MCP route**: `measure_operations Update` → `bridge.py reload` took 17s with no click and no Apply. The capture grew 14 KB → 99 KB, so the page rendered. |
| P4 | `stress.py` scenarios hardcoded | **CONFIRMED** | Unmodified on RetailHe: 6/7 scenarios `DAX ERROR … Column 'סטטוס' … cannot be found`. Edited by hand in both projects. Side effect: on a DAX error the script `continue`s before cleanup and leaves `q_s_*.dax` behind. |
| P5 | Middle voids pass the fill gate | **CONFIRMED** | **Synthetic**: a 504×380 card with a title, a 60px block and a `margin-top:auto` footer (≈230px void in the middle) → `FIT OK`. **Real**: the new_demo filter panel has ≈150px of nothing between the two mix blocks (`screenshots/04`, `05`) → `FIT OK`. |
| P6 | 72px header clips under `accent` | **CONFIRMED** | Same layout, `HEADER_H=72` → `FIT FAIL hcHeader: 1px past the safe edge`; 80 → `FIT OK`. |
| P7 | `bridge.py shot` PrintMetadataUnavailable after a fresh open | **NOT REPRODUCED** | `new_demo.pbip` opened from the shell. The bridge was ready after 56s, and `bridge.py shot` 70s after the open returned the rendered page (99 KB) on the first try, with nobody looking at the window. |
| P8 | dark + tint gives light cards | **CONFIRMED** | `make_style(brand="#0F766E", accent="#E11D48", mode="dark", mechanism="tint")` → card tokens `c_bg` `#F4F7F6` (neutral), `#EEFDFC` (c1), `#FEF1F1` (bad). |
| P9 | RTL details | **Truncation CONFIRMED** (on mixed Hebrew + Latin text), **slicer "All" CONFIRMED**, **mid-motion NOT TESTED** (no motion in this build) | `כונן SSD חיצוני` renders as "כונן D…" in the treemap, in the preview and in Desktop. The native slicers show "All" in English on the Hebrew page (`screenshots/05`). |
| P10 | Doc contradictions | **CONFIRMED** (all 3) | `design-system.md:60` "`a1`..`a5` for analysis cards" vs `styles.ROLES` `c1..c6`. `skills/composite-dashboard/SKILL.md:35,41,52`: `var(--pbi-theme-bg-light)`, one `_HTML` table, `library/palettes.md`. `design-system.md:75` and colorful-styles: the sales example is "not ported to roles". |
| P11 | 30-40s blank canvas after opening | **NOT TESTED** | No GUI observation in the kit-only run. The bridge needed 56s to come up, so a blank canvas for that long is plausible. |
| Gap | Creating the model / PBIP from scratch | **Mostly bridged by the Modeling MCP** | See §2. |

## 2. Does the Power BI Modeling MCP bridge the "no model yet" gap?

**Yes, for the whole model. One GUI step remains, plus a save.**

- **GUI (2 steps):**
  - Home → Blank report → File → Save as → type *Power BI project files (\*.pbip)*. This took ~4 min with automation (the Save-as click needed foreground input).
  - **Ctrl+S after the MCP edits**: until Desktop saves, the TMDL on disk is still the empty model.
- **MCP, zero clicks (~2 min):**
  - `table_operations Create` × 5 (Excel M partition + typed columns in one batch);
  - `relationship_operations Create` × 4;
  - `model_operations RefreshWithXMLA Full`: 1,200 / 10 / 150 / 6 / 730 rows, verified with DAX;
  - `MarkAsDateTable`;
  - `column_operations Create` × 6 calculated columns + a `Calculate` refresh.
  - Desktop's Data pane showed all 5 tables at once, with no Apply.
- **Caveats:**
  - The MCP does not infer columns from M: every column must be declared, with `sourceColumn` and `dataType`.
  - The M path is absolute (a moved folder breaks refresh).
  - Results come back inline: one `SUMMARIZECOLUMNS` of 18 Hebrew rows cost ~3K tokens.
  - `hasUnsavedChanges` stayed `true` afterwards (P3).

## 3. New findings (not in REPORT.md)

| # | Severity | Finding | Evidence / impact |
| --- | --- | --- | --- |
| N1 | **High** | **The kit assumes one flat host table.** It fits a star schema only partly, and quietly. | **Slicers**: `gen_pbip.py` binds every slicer to `pipeline.json` `table`, so there is no filter on a dimension (branch, category, year). **Builders**: `heat_matrix`, `small_multiples` and `lift_bars` take every column from one `table`. `lift_bars` uses `COUNTROWS(table)`, so on a dimension table it counts dimension rows. **On a dimension table**: `data_table` and `treemap_rows` run `VALUES(dim[col])`, which is not filtered by fact-side slicers, so `data_table` always lists all 6 branches and its empty state never shows. **In practice**: RetailHe needed 6 RELATED calculated columns (added with the MCP). new_demo (kit only) ended with **2 slicers** (channel, payment method) instead of the year / branch / category a user expects. |
| N2 | **High** | **`gen_pbip.py` rebuilds the host table's TMDL from the init-time `_backup`.** Any model change after `init` (here: calculated columns on `מכירות`) is **silently dropped** on the next write, and Apply would then delete those columns from the live model. | I had to copy the new `מכירות.tmdl` into `_backup` by hand. Not documented. |
| N3 | Medium | **`runq.ps1` falls back to any open model.** With two Desktops on the same schema (RetailHe + new_demo), a query that fails on the intended model silently runs on the other one. `stress.py` cannot pass `-Port`. | Here the newest model happened to be the right one. I pinned `-Port 53766` (found with the MCP's `ListLocalInstances`). |
| N4 | Medium | `small_multiples` prints raw panel totals: "194701.5", "842701.5". | `screenshots/04`, `05`. The other builders use `_fmt()`. |
| N5 | Medium (owner) | **The agent builds the whole template in one go.** Nothing in AGENTS.md / pbi-html-dashboard makes it stop for a direction check on one card / one version. The first ask round (AGENTS.md §3.2, colorful-styles) covers brand and light/dark but **not the page background** (clean vs. a colored page, and which color). | the owner's review, 10 Nov 2026. In this run the background question was asked by hand (answer: clean light gray, preset colors, no hero). |
| N6 | Low | `pipeline.json` `style` cannot say "preset `accent` with `hero: false`". It needs the preset's full `make_style()` dict (11 colors copied out of `styles.py`). | new_demo `pipeline.json`. |

## 4. What was not done

- **Contract deviation (on purpose, the owner: "stop at one"):** new_demo was written to the PBIP with `FIT OK` + `CONTRAST OK` but **stress failing 4/8** (P2). AGENTS.md §0.4 says never write before stress passes. RetailHe was gated and versioned but **not written** to Desktop.
- **Not run:** `checklists/validation.md` in full, `powerbi-report-author validate`, a slicer click in Desktop, LTR/English, motion.
- **P7 retry and P11:** no reproduction, so no fix (a retry on `PrintMetadataUnavailable` stays a cheap optional hardening).

## 5. Time per phase

Day 1 (10 Nov, UTC+2), 15:36 → 16:06; day 2, 07:51 → 07:55.

| Phase | Time |
| --- | --- |
| Data read + copy | 1 min |
| Blank report → Save as PBIP (GUI, cua) | 4 min |
| Model with the Modeling MCP (5 tables, relationships, refresh, date table) + Ctrl+S | 2 min |
| `init` + reading AGENTS.md, design-system, build-workflow, pipeline README, 2 skills, components | 4 min |
| RetailHe `measures.py` → first FIT OK (2 gate runs: 72px fail, 80px pass) + 2 style previews | 3 min |
| RetailHe stress (unmodified: P4; adapted: P2) | 6 min |
| P1 git tests (own repo, `tag -f`, nested) | 2 min |
| CUA save attempts / bridge status on RetailHe (P3 condition) | 3 min |
| new_demo: `git init` + `init` + questions + `measures.py` + 3 gate runs + stress + snapshot + `gen_pbip` | 6 min |
| new_demo in Desktop: open → bridge shot (P7) → MCP update + `bridge.py reload` (P3 route) | 4 min |
| **Kit-only, new_demo: folder → PBIP written** | **≈ 6 min of agent time** (16:00 → 16:06) |

## 6. Token usage

- **Context window at the time of writing** (`get_usage`, measured): **339,587 tokens** (34% of 1M):
  - messages 259K;
  - MCP tools 36K;
  - system tools 24K;
  - system prompt 11K;
  - skills 7.9K.
  - Plan: 5-hour window at 4% (a new window on day 2).
- **The MCP route's cost is inline text:**
  - A full measure push for this dashboard is **35.6K characters** of DAX (38.4 KB, `q_all.dax`). That is an *estimated* 12-18K input tokens per full push, plus the same again if the call is echoed.
  - A single-measure Update cost a few hundred tokens.
  - Keep the gates on files (`runq.ps1`). Push only the changed measures with the MCP.
- **Largest avoidable costs this run:**
  - full-resolution screenshots (≈10);
  - one MCP DAX result returned inline (18 rows of Hebrew, ≈3K tokens);
  - reading `components.py` in 3 slices instead of the README.

## 7. Screenshots (`kit-test-2/screenshots/`)

| File | What |
| --- | --- |
| `01_retailhe_preview_accent_rtl.png` | RetailHe v1, `accent`, RTL Hebrew, headless preview (FIT OK, CONTRAST OK) |
| `02_retailhe_preview_tonal.png`, `03_retailhe_preview_sunset.png` | the 2 alternative style previews (colorful-styles step 2) |
| `04_newdemo_preview_v1.png` | new_demo v1 headless preview (accent, no hero, clean page) |
| `05_newdemo_desktop_v1_bridge.png` | **new_demo v1 in Power BI Desktop** (`bridge.py shot`, after a fresh open) |

## 8. Final fix list (confirmed → fixed in the kit PR)

| Fix | For |
| --- | --- |
| `versions.py`: git only when `show-toplevel == ROOT`, otherwise print a "zip-only" note; `add -A -- .` excluding `_versions/*.zip` and `__pycache__`; never `tag -f` (an existing tag → warn and skip the tag) | P1 |
| `stress.py`: scenarios from `pipeline.json` `"stress"` (fallback: the built-in reference scenarios); `-Port` from `pipeline.json` `"port"` / `DASH_PORT`; temp files removed on DAX error too | P4, N3 |
| `components.py`: `stretch=True` option on `lift_bars`, `heat_matrix` and `data_table` (rows `flex:1 1 0` with min/max); off by default, so existing builds stay byte-identical | P2 (partial) |
| `small_multiples`: panel totals through `_fmt()` | N4 |
| `measures_example_sales.py`: 80px header | P6 |
| Docs (build-workflow): creating the model with the Modeling MCP; the banner condition (`hasUnsavedChanges`) + close/reopen fallback; refresh `_backup` after model changes; star-schema limits and the RELATED workaround; `-Port` with several models | Gap, P3, N1, N2, N3 |
| Docs: `a1..a5` → `c1..c6`; composite-dashboard aligned with styles/design-system; dark + tint note; RTL mixed-text truncation + slicer locale note | P10, P8, P9 |
| AGENTS.md §3: ask about the page background (clean / colored + color); stop after one version for a direction check before building every card | N5 |

**Left as follow-ups** (confirmed, but not a minimal change):
- P5 (internal-void gate);
- N1 in code (slicers and builders on dimension tables);
- N6 (preset + overrides);
- P2 in full (a status-mix fill block and `short_when` driven by `_n`).
