# ROADMAP - 20 steps forward

Rule for every step: **the dashboard and the fit between its parts come first.** A step ships only if the regression gate shows no unintended change and the fit, contrast and stress gates pass. Status: ✅ built and measured · 🧪 built, waiting on a Desktop check · 📋 researched, not built yet.

## A. Safety net - never lose a good version

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 1 | Versions: snapshot / list / diff / revert, each version keeps the real HTML of every card + screenshot | ✅ | `tools/pbip-html-pipeline/versions.py` |
| 2 | Regression gate: byte-compare every card's HTML with the last version; refactors must be IDENTICAL | ✅ | `regress.py` |
| 3 | Automatic pre-revert snapshot (a revert is itself revertible) | ✅ | `versions.py revert` |

## B. Quality gates - catch problems before Desktop

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 4 | Headless fit check (no browser pane, no npm): Edge + DevTools protocol | ✅ | `fitcheck.mjs` |
| 5 | WCAG contrast gate on every text element (4.5:1, large 3:1) | ✅ | `fitcheck.mjs` |
| 6 | Stress scenarios: all / one status / one owner / blanks / empty selection / every column filtered | ✅ | `stress.py` |
| 7 | Microsoft PBIR validator as a gate (`powerbi-report-author validate`) + Desktop screenshots via its `preview --host desktop --screenshot` | 📋 CLI not installed (`npm i -g @microsoft/powerbi-report-authoring-cli`) | reference/pbir-visual-json.md |
| 8 | Rule linter over visual.json (padding 0, altText, crossFilter when Context, slicer item colors) - PBI Inspector V2 or a small Python rule set | 📋 | - |

## C. Color and background - "colorful dashboard"

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 9 | Color tokens: no hex in measures; palettes ocean / midnight / berry, all passing fit + contrast | ✅ | `palette.py` |
| 10 | Text-safe status colors (`*_text`) separate from fill colors | ✅ | `palette.py`, measures `_txt()` |
| 11 | Page background + slicer colors from the palette (no white dropdown on a dark page) | ✅ measured in Desktop | `gen_pbip.py` |
| 12 | Colorful page: gradient background layer (full-page HTML visual) + filled KPI cards, palette `vivid` | ✅ measured in Desktop; wallpaper *image* via RegisteredResources still 📋 | `palette.py`, `reference/design-system.md` §4 |
| 13 | Generated custom theme from the palette, so `--pbi-theme-*` and native visuals match | 📋 structure verified | reference/pbir-visual-json.md |
| 13b | Direction (LTR/RTL, mirrored layout) and UI language (display-string translation with protected data literals) | ✅ | `measures_example_projects.py`, `labels.py` |
| 14 | High-contrast mode fallbacks (`#htmlContent.pbi-theme-hc`) in every card | 📋 | capabilities.md |

## D. Interactivity and reach

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 15 | Cross-filter cards written in PBIR (`crossFilter.enabled` + `sampling` Context) - e.g. click an owner bar filters the page | 📋 property names verified | reference/pbir-visual-json.md |
| 16 | No-data message per visual (`contentFormatting.noDataMessage`) | 📋 | same |
| 17 | Alt text per visual bound to a summary measure + `role/aria-label` in SVG | 📋 placement to diff once | same |
| 18 | Mobile layout (`mobile.json` per visual, ≥323×180pt) | 📋 | same |

## E. Scale and reuse

| # | Step | Status | Where |
| --- | --- | --- | --- |
| 19 | Layout engine: compute `LAYOUT` from a grid spec (rows, columns, gutters) with overlap / multiple-of-8 asserts, so a new dashboard starts from intent, not coordinates | 📋 | - |
| 20 | Component kit: the reference build's cards (KPI, lifecycle, segmented bars, 2-column list, donut, timeline, filter panel) extracted as parameterized builders on top of the token + fit system | 📋 the reference build `measures_example_projects.py` is the reference implementation | `measures_example_projects.py` |

Next recommended order: 11 (confirm in Desktop) → 7 → 15 → 12/13 → 19 → 20.
