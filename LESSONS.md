# LESSONS.md - measured lessons (Power BI Desktop, not docs)

Every entry here was **measured in a real Power BI Desktop session**, not taken from documentation. Rules in this file override anything in `reference/` or a component that contradicts them.

**Standing rule (Ruby, 9 Nov 2026):** every lesson measured while building a dashboard - visualization (layout, fit, RTL, typography, color, visual chrome, HTML/SVG rendering, tooltips, slicer placement) and the build workflow (Desktop/PBIP iteration, testing measures, process safety) - is added here the same day, with: what broke, the root cause, the fix, how to verify it. Lessons about **data sources, APIs and credentials** do **not** go here - they go to Ruby's library only (Trove, book `powerbi-agentic`). Rules that change how something is built are also copied into the relevant `skills/*/SKILL.md`, `reference/*.md` or `checklists/validation.md`. Format: `L<n> · date · area`.

---

## L1 · 09.11.2026 · Theme padding eats the HTML viewport (the #1 cause of clipped cards)

- **Broke:** every HTML Content card was clipped at the bottom (KPI subtext, last list row, footer lines), and titles wrapped because cards were narrower than designed.
- **Root cause:** the Fluent 2 base theme (`Fluent2-CY26SU10`) pads **every** visual `16/14/16/16` (left/top/right/bottom) under `visualStyles.*.*.padding`. The HTML viewport is the frame minus padding: **30px shorter and 32px narrower** than the `position` in `visual.json`.
- **Fix:** every HTML Content visual (and every slicer that sits on an HTML panel) gets, in `visual.visualContainerObjects`:
  `"padding": [{"properties": {"top": 0D, "bottom": 0D, "left": 0D, "right": 0D}}]` (literal values `'0D'`), together with `background`, `border`, `title`, `dropShadow`, `visualHeader` → `show:false`.
- **Verify:** read the report's base theme `visualStyles["*"]["*"].padding` before designing; after Apply, a card's painted edge must coincide with the selection frame.
- An earlier wrong diagnosis ("Desktop renders text taller than the browser") was this padding. Do not add "extra line-height slack" for it; set padding to 0.

## L2 · 09.11.2026 · `dir="rtl"` alone does not right-align text in HTML Content

- **Broke:** titles and paragraphs in several cards rendered left-aligned in Desktop although the root had `dir='rtl'` (they were right-aligned in the browser preview).
- **Root cause:** the visual's *default body styling* injects an alignment (`text-align:left`) that is inherited; `start` resolves against it.
- **Fix:** the root of every card carries `direction:rtl;text-align:right` **inline** (plus `dir='rtl' lang='he'`). Numeric cells keep explicit `text-align:left;direction:ltr;unicode-bidi:isolate`.

## L3 · 09.11.2026 · Type scale for a 1920×1080 canvas

- **Broke:** 11-13px text was unreadable: Fit to page shows a 1920 canvas at ~0.70-0.75 on a laptop, so 12px renders ≈ 9px.
- **Fix (minimums on 1920×1080):** body / list labels 15px, secondary 14px, small captions 13px (never below), card title 20px, header title 26-28px, KPI value 48-50px, stage/donut number 26-36px. On 1280×720 divide by 1.25.
- **How:** write the measures with a base scale and remap in one place (the pipeline's `FONT_SCALE` map) - never hand-edit sizes per card.

## L4 · 09.11.2026 · Fit check before Desktop: every card at its exact size, 8px slack

- **Broke:** cards that looked fine in a full-page screenshot still overflowed by 2-30px.
- **Fix:** the preview renders each measure in an iframe of the exact visual size and runs `fitCheck()`: any descendant whose box ends past `edge - 8px`, or a root taller than the frame, fails. Nothing goes to the PBIP until it prints `FIT OK`. Tool: `tools/pbip-html-pipeline/gen_preview.py`.
- Rules that fell out of it: fixed-height rows (not content-driven); `flex:none` on every fixed-height child of a flex column (otherwise it shrinks to 0 - a status bar and slicer slots disappeared); `white-space:nowrap` on card titles/subtitles and legends; budget rows from the frame: `rows = floor((H - padding - header - footer - 8) / rowPitch)`.

## L5 · 09.11.2026 · Lists that do not fit: top N + "ועוד N" with a hover tooltip

- Show top N rows; the overflow line lists the rest in a manual tooltip: `class='tooltipEnabled'` + `data-tooltip-title-NN` / `data-tooltip-value-NN` (one pair per hidden item, NN zero-padded). Works in Secure (no script). A *click to expand* is not possible in Secure; it needs Regular + script, or a native drillthrough page.
- A blank category that dominates (e.g. 36% "no department") is not a bar: drop it from the list and state it in a note line; it compresses every real bar.
- Short categorical lists (≤12) fit in two columns (`display:grid; grid-auto-flow:column; grid-template-rows:repeat(n,28px)`) instead of being truncated.

## L6 · 09.11.2026 · Native slicers on an HTML panel

- Do not draw a box behind the slicer in HTML (double border). Draw only the label; the slicer (padding 0, header off, background off, `mode:'Dropdown'`) supplies its own box.
- Slicer y = panelTop + titleBlock + i × slotPitch + labelHeight, all from the same constants the HTML uses.

## L7 · 09.11.2026 · Iterating on a PBIP while Desktop is open

- Write the files, then click **Apply external changes** in the yellow banner - do not close Desktop between iterations. The banner can be hidden behind the canvas until the window repaints; take a screenshot to find it.
- After Apply the **model** is updated, but visuals keep showing **cached query results**: click Home → **Refresh** (or switch page) before judging the render. Judging without Refresh shows the previous version.
- If Desktop must be closed, close it **before** writing: it saves on close and can overwrite your files.
- A project whose folder was moved fails Apply with `ArtifactShortcut: Required artifact is missing`: the open window still points to the old path - reopen the `.pbip` from its new location.
- TMDL: a line starting with `///` is the **description** of the next object. Never use it as a BEGIN/END marker around generated measures; keep reruns idempotent by rebuilding from a backup copy.

## L8 · 09.11.2026 · Never force-close Desktop; one window per project

- Do not force-kill Power BI Desktop and do not stop a `PBIDesktop` process you did not start (one without a window may be the user's own reopen in progress). Ask first.
- Never leave two Desktop windows open on the same PBIP: each saves its own state and they overwrite each other. Before opening, check for a running instance on the same project.
- An invisible modal (a Desktop dialog that opens but does not render) blocks every click; find it in the accessibility tree (`FloatingDialog`) instead of closing the app.

## L9 · 09.11.2026 · Test every HTML measure against the open model before writing

- Desktop ships `Microsoft.PowerBI.AdomdClient.dll` next to `PBIDesktop.exe`; the model port is in `...\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt` (UTF-16, newest file). `tools/pbip-html-pipeline/runq.ps1` auto-detects it and runs a `DEFINE MEASURE ... EVALUATE ROW(...)` query with every HTML measure; the real HTML it returns feeds the exact-size preview and fit check (L4).
- DAX `VAR` names cannot contain Hebrew (`VAR _v_סטטוס` is a syntax error). Hebrew is fine in measure, table and column names.

## Correction · 09.11.2026

An earlier note said "HTML Content in Desktop renders text lines taller than the browser - add slack". **Wrong.** The clipping came from the theme's default visual padding (L1). Fix padding to 0; do not pad designs to compensate.

## L10 · 09.11.2026 · Versions + regression gate before any change

- Every iteration ends with `versions.py snapshot` (PBIP definitions + `_build` sources + the real HTML of every card + screenshot). A bad result is undone with `versions.py revert vN` → Apply external changes → Refresh; revert first snapshots the current state, so it is itself undoable.
- Refactors are proven safe by `regress.py`: the HTML of all cards must be byte-IDENTICAL to the last version. Tokenizing all colors was shipped this way (IDENTICAL), then the intended contrast fix showed exactly 2 changed cards.
- Gates before writing the PBIP: `fitcheck.mjs` (FIT OK + CONTRAST OK) and `stress.py` (all scenarios). Verify a scenario really filters (one owner → 5 projects) - a gate that tests nothing passes everything.

## L11 · 09.11.2026 · Contrast: fill colors are not text colors

- The automatic WCAG check found teal status text `#00A3AE` on `#E0F6F7` at 2.73:1 and purple `#8764B8` on its soft fill below 4.5:1. A status needs two tokens: a fill color (bars, borders, dots) and a darker `*_text` color for text on its soft background. Dark palettes need lighter `*_text` variants (the active pill failed at 4.30:1 in Midnight until it got its own `active_text`).
- Verifying a color change in Desktop: a JPEG zoom cannot tell close shades apart (`#00A3AE` vs `#00747C`). Save a PNG of the Desktop window and read pixels with `System.Drawing.Bitmap.GetPixel` (darkest pixel matching the hue in the element's box) - v002 was confirmed this way. If the model has the new measure (check with a DAX `SEARCH` on the measure text) but the canvas still shows the old look, it is the visual cache: Home → Refresh.

## L12 · 09.11.2026 · Colorful dashboard: gradient page + filled KPI cards (measured in Desktop, Secure)

- **Gradient page background without an image:** one full-page HTML Content visual (0,0,1920,1080), first in `LAYOUT` so it gets the lowest z, padding 0 / chrome off, content `<div style='height:100vh;background:linear-gradient(135deg,from,mid 55%,to)'>`. Renders in Desktop with the Secure edition. Cards keep a white `surface` so text stays readable on the gradient.
- **Filled KPI cards:** `background:linear-gradient(160deg,rgba(0,0,0,0),rgba(0,0,0,.24)),<accent>` - the overlay only darkens, so white text contrast only improves; swap icon roles (white glyph, accent details); progress track `rgba(255,255,255,.30)` with a white fill. White text needs **deep** accents (≥4.5:1): blue `#1D4ED8`, violet `#7C3AED`, teal `#0F766E`, green `#15803D`, red `#C81E1E` (`#DC2626` failed at 4.40:1 as text on a pale inset).
- **How it is switched:** palette flags (`kpi_filled`, `bg_layer`) and gradient tokens exist in every palette; off in light palettes, so `regress.py` proved the light dashboard byte-IDENTICAL while the colorful one was built. `DASH_PALETTE=vivid` builds the colorful version; the light one stays a version away (`versions.py revert`).

## L13 · 09.11.2026 · Git: versions as commits + tags, and a .gitignore that cannot leak

- Make the dashboard project a git repo; `versions.py snapshot` then also commits and tags `vNNN`, `revert` commits the restore. Zips in `_versions/` stay as a local backup (ignored by git).
- The project `.gitignore` must exclude: env/key files (`*.env`, `env*.txt`), pulled data (`data/`), `**/.pbi/cache.abf`, `**/.pbi/localSettings.json`, build scratch. Before the first commit run `git ls-files | grep -iE "env|data/|cache.abf|localSettings|\.csv"` - it must print nothing.
- Measured pitfall: a broad `*.dax` ignore (meant for scratch queries) silently dropped all 32 `library/components/*.dax` from the agent's first commit. Ignore by prefix (`q_*.dax`), and compare `git ls-files | wc -l` with the files on disk before pushing.
- The agent itself lives in a **private** GitHub repo (reuvenkazorer27/pbi-html-content-agent); run a secrets scan (keys, tokens, `crm_`, `Bearer`) before every push.
