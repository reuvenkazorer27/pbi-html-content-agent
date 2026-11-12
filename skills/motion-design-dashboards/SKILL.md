---
name: motion-design-dashboards
description: Design and build striking, motion-designed Power BI dashboards in HTML Content - a full design language (materials, type, colour, one hero data device, page choreography) on top of a real, dense dashboard, not a pretty landing page or a data story. CSS keyframes only (Secure edition), real numbers, gated with stress variants. Optional textures and surfaces from Uiverse.io (MIT). Use when the user asks for an impressive / wow / premium / "go wild" dashboard, a new visual identity for a dashboard, or motion beyond the kit's standard entrances.
---

# Motion-design dashboards

This skill raises the ceiling of what the kit builds: a page that looks designed, moves with intent, and still works as a dashboard a manager scans in ten seconds. It sits on top of `skills/motion` (meaning-carrying motion), `skills/dashboard-shell` (one fullscreen visual, Pattern A) and `skills/composite-dashboard` (Pattern B). Everything here runs in the **Secure** edition: one inline `<style>` per measure, `@keyframes`, inline SVG, CSS gradients. No script.

**Reading order.** This file and `skills/motion/SKILL.md` for the design study (sections 1-6). `reference/design-system.md` and `reference/build-workflow.md` (versions, Desktop loop) apply from section 6 step 4 on, when the page goes into a PBIP. `skills/rtl-hebrew/SKILL.md` for Hebrew pages.

Verification status: rules marked *(measured)* were measured in Power BI Desktop (Secure edition, Nov 2026) on full-page examples; the design languages, the procedure and the gate were exercised on ten example pages by builders who had only this skill (headless Edge, `page_check.py`); everything else is doc-based.

## 1. The contract: a dashboard, never a story

Reviewers rejected beautiful pages that read like a landing page or an essay. Every page passes all of these:

1. **A KPI row** across the top: 4-6 numbers, each with its basis (period) and its change against a stated comparison (vs previous month / same period last year), arrow + colour + value. Full-page languages may use type-only KPIs (no icon chip); the icon rule in `AGENTS.md` is for the `kpi_card` builder.
2. **6-9 panels**, each answering one question, each with a short title and a unit ("Revenue by region, K"). Mark every panel `data-panel='<name>'` - the gate checks each panel for clipped rows and empty space. Clear boundaries, dense, no decorative empty areas.
3. **The standard instruments are present**: a time series, a ranked breakdown, a two-dimensional view (matrix / heat grid), a composition (segments, payment, mix), and the exceptions of the latest period.
4. **No prose.** No paragraph, no manifesto, no sentence headline. Labels and one-line captions (under ~8 words). A flag on the exception carries the sentence-length message.
5. **No fake controls.** No buttons, tabs, toggles, active chips or "filters" that are not real. A static index or legend is fine and must look static. Real filtering = native slicers in slots (`html-slicers-filters`) or the Context role.
6. **Every number is real and every claim is computed** ("lowest since …", "peak", "3rd weakest"): assert it in the generator or compute it in DAX. A currency symbol only when the data or the user states the currency. **No target in the data** = no attainment unless you state the stand-in in the header ("target = 2025 actual").
7. **Small selections still work - and are tested.** The generator takes a filter argument and writes stress variants next to the page: one region, one month, a narrow combination, empty. `page_check.py page.html page_region.html page_month.html page_empty.html` must pass them all. The layout degrades to empty slots / a "last month only" panel / an empty state, never to errors, `vs BLANK`, a blank hero, or overlapping labels.

**Exceptions need enough data.** A month of ~20 orders makes most region-month changes look like -60 %. Flag an exception only when the latest period has at least 5 orders for that item **and** it breaks two conditions (e.g. below 60 % of its own 3-month average and below last year's same month); show the order count next to the flag; when the latest month is thin (under ~30 orders) give the KPI row a year-to-date basis as well and label each panel's period.

Signs of a story page (fix before you ship): a big sentence in the hero, a paragraph anywhere, fewer than 5 panels, one giant visual without a KPI row, a scroll-like vertical narrative, an illustration that encodes nothing (a decorative "photo" in the hero is the classic failure - see language 8).

## 2. Choose one design language

A design language = material + type + colour logic + **one hero data device** + a motion signature. The hero device is where the data becomes the image; everything else is a disciplined grid around it. "Mix at most two motifs" = you may borrow ONE device from a second language for a secondary panel (e.g. tick gauges inside a HUD page); never two hero devices.

| # | Language | Look | Hero data device (exact encoding) | Motion signature | Good for |
|---|---|---|---|---|---|
| 1 | **Instrument HUD** | pale technical ground, blueprint grid, monospace readouts, one hot accent, part numbers, dimension lines | the total as a core ring (arc = share per segment) that explodes into segment modules; each module splits into plates whose length = value on one shared scale; dimension lines show the gaps between modules; a spec sheet table beside it | modules fly out of the core; leader and dimension lines draw; a playhead sweeps the periods once and stops on the exception flag | operations, engineering, product mix |
| 2 | **Cylinder shelf** | deep cool stage, period cards in a 3D ring, glossy cards with a fill "tank" | one card per period; tank fill = value / best period; the latest card faces the viewer | the ring assembles small and tilted, then opens; a counter reaches 100 % | monthly performance, seasonality |
| 3 | **Depth line-up** | white / ice stage, wide tracked caps (Latin only), soft floor shadows | ranked entities as tall figures; **height = value** (one shared floor and scale); rank is shown ONLY by depth cues - x position, width, blur (<= 1.5 px), opacity, z-order; each figure is stacked from its components (one accent in a light-to-dark ramp) | figures walk in from one depth further back, back ones first; a scan line reveals the leader; rank chips roll as odometers | rankings of regions, teams, stores |
| 4 | **Orb command center** | near-black, coloured light from the top, frosted panels, gradient hairline on the hero only | a glass sphere holding the total; CONCENTRIC rings around it, one per entity, arc = share; an outer ring = margin with a tick at the comparison value. The side rail is a static index (labels, period, source), never navigation | rail and header rise, the orb opens with a circular clip, numbers rise out of masks, rings draw, panels settle | executive overview, wall screens |
| 5 | **Atmosphere glass** | one atmospheric gradient stage; panels repaint the stage under a white veil = seamless glass (recipe in section 3) | a smooth wave chart with the values row above it, the active period in bold, a dashed average line | panels slide in from the side one by one; the wave draws with the fill following the pen | trend-led pages, public screens |
| 6 | **Calm bento** | warm neutral page, off-white cards, hairlines, soft shadows, one accent colour | tick gauges per entity: N ticks (e.g. 40) on a half circle, **one tick = scale / N** (state it), filled from the reading start (right in RTL); ticks kept from the comparison sweep in first, ticks gained arrive last in the good colour, ticks lost are drawn at the comparison level then fade to the track colour | ticks sweep; odometer tiles roll from the previous value; a cumulative route draws with milestone pins landing as the pen passes | balanced KPI pages, management packs |
| 7 | **Night grid ops** | near-black, faint grid, violet / teal glow, gradient hairline borders | glowing columns per period; an exception column (rule stated on the panel) turns warning-hued; a threshold tick on each column | columns grow from the axis, labels rise, the exception pulses twice | monitoring, SLA, operations |
| 8 | **Halftone contact sheet** | paper + one ink colour, dot screens (Uiverse patterns fit here), print marks, script annotation | a grid of period frames cut from ONE shared print; each frame **develops to its value** (the developed part = value / peak, the rest stays undeveloped paper) so the image itself is the bar chart; a hand-drawn circle around the exception | frames develop in sequence; the circle draws itself; numerals rise | monthly reviews, marketing |
| 9 | **Monochrome editorial** | black / white / greys + semantic red / green for change only, heavy condensed type (`Bahnschrift` with `font-stretch:condensed`) | the KPI row IS the numeral system (huge numerals); the hero is a separate ranked device (discs with area = value, a dashed ring at the comparison size) - do not repeat a KPI as the hero | numerals rise out of masks, discs pop by rank | board packs, investor style |
| 10 | **Topographic** | misty neutral, one ink colour, one lime accent, mono labels | contour rings = attainment thresholds (25/50/75/100/125 % of a STATED target); entity pins sit at their own attainment. Use it as the hero panel of a full dashboard, never as the page | contours fill from the edge inward; pins drop by rank | target tracking |

**Approved directions (12 Nov 2026, reviewed by the kit owner).** Liked: the exploded-assembly HUD (1), the depth line-up (3), the halftone contact sheet with the hand-drawn circle (8), night grid ops with glowing columns and tick gauges (7), and all builder pages in languages 1-7, 9, 10. Rejected: a contact sheet whose shared image was a decorative landscape that encoded nothing - the reason language 8 now requires the develop-to-value encoding. Rejected earlier: every page that read as a story (big sentence, paragraph, one giant visual).

Every language: one hero accent plus semantic up / down / warning; WCAG AA text contrast on the real background; one hero device; the grid follows section 1.

## 3. Recipes

- **Seamless glass (language 5).** One stage gradient sized to the page (e.g. 1920 x 1080). Each panel paints the same layers with `background-size:` the page size and `background-position: -x -y` (its own page position), under a white veil gradient, plus `background-color` = the lightest blend for the contrast gate. Do not use `background-attachment:fixed` (breaks under transforms). In a fluid page write the sizes in `var(--u)`.
- **Heat grids.** A continuous colour scale has mid-tones where neither white nor dark text reaches 4.5:1. Use 4-5 discrete bins with a text colour per bin (and a legend), or labels >= 19 px bold (the 3:1 large-text threshold).
- **Labels in charts** are HTML overlays (or SVG `<text>` with an explicit `fill`), with a solid chip behind them when they sit on a gradient.
- **Odometer digits** need `font-variant-numeric:tabular-nums`.
- **Develop / fill animations**: animate `height` / `clip-path`, not `scale` with a CSS variable (it scaled the element's border to hundreds of px).
- **Entrances on the bottom row** slide up or scale in - a downward slide pushes the last row past the page edge in some frames.

## 4. Motion grammar

- **Meaning first** (`skills/motion`): animate the change (roll from the previous value, bars grow from the comparison value, gained / lost ticks), the exception (a flag, a ring that pulses at most twice), the rank (walk-in order), the freshness. Decoration (sheen, drift) once and only on the hero.
- **One clock for the page.** Every delay = beat + offset. Order: frame/grid -> header -> KPI row -> hero device -> panels (reading order) -> data marks -> exception flag -> optional coda. Each element enters once.
- **Three curves**: settle `cubic-bezier(.16,1,.3,1)` (arriving), pen `cubic-bezier(.45,0,.25,1)` (lines and wipes), soft `cubic-bezier(.25,.46,.45,.94)` (fades). Overshoot (`cubic-bezier(.34,1.56,.64,1)`) only on chips and dots, never on data lengths.
- **Budget**: the page settles by ~6 s; data entrances under ~1.6 s per element; alerts at most 2 cycles; no `infinite`. The entrance replays on every filter change and refresh.
- **Devices**: mask rise, odometer (start at the previous value's digit), pen draw (clip wipe on a wrapper for time series; `pathLength` dash only on a non-distorted SVG), fill follows the pen ~0.2 s behind, tick sweep, rank walk-in, ring assembly (3D), develop, flag wipe. Animated `filter:blur()` is untested in Desktop - keep blur static at rest and small.

## 5. Materials from Uiverse.io (optional, MIT)

Uiverse.io is an open-source library of HTML/CSS elements (github.com/uiverse-io/galaxy, MIT License, Copyright (c) 2023 Uiverse.io). Use it to complete the imagery of a page - textures, backgrounds, card surfaces, alert-chip shapes - never for behaviour.

- **Use**: `Patterns` (dot screens, grids, ruled paper, hatching), `Cards` (surfaces, frames), `Notifications` (alert-chip shapes). **Never**: `loaders` (loops), `Buttons`, `Toggle-switches`, `Checkboxes`, `Radio-buttons`, `Inputs`, `Forms` (fake controls).
- **Find**: `python -I tools/pbip-html-pipeline/uiverse.py search Patterns dots` (matches the author/tags comment; files are cached).
- **Get**: `python -I tools/pbip-html-pipeline/uiverse.py get Patterns/<file>.html --prefix bg1 --split` prints the CSS ready to merge into your page's ONE `<style>` (classes scoped to the prefix, rem/em turned into px) and the markup separately, and reports what to remove (`:hover`-only effects, `infinite`, external `url()`, script). Elements with `::before`/`::after` need a positioned parent.
- **Adapt**: recolour to your palette and rescale freely - it is still the element (keep the attribution comment). List every element used (path, author, MIT) in the deliverable.
- A texture under text needs a solid `background-color` fallback the contrast gate can check. A decorative layer that extends past the page (a perspective floor, a full-bleed texture) is marked `fit-clip` - allowed for decoration only, never on data.

## 6. Build procedure

1. **Data**: aggregate in the generator (Python stdlib) for a design study, or write the DAX directly. Real data only; assert totals. The generator takes a filter argument for the stress variants (section 1.7).
2. **Page**: ONE root `<div>` with ONE `<style>` inside. Root: `box-sizing:border-box;height:100vh;width:100%;overflow:hidden`, an explicit `background-color` = the honest worst case behind the text, and a text `color` that reads on it (the gate measures text against the nearest opaque background). Content 8 px inside the edges. Sizes in `calc(N*var(--u))`, or px that `page_kit.fluid()` converts.
3. **Gate**: `python -I tools/pbip-html-pipeline/page_check.py page.html page_<variant>.html ...` -> SECURE LINT OK, FIT OK (page + every `data-panel`), CONTRAST OK, FRAMES OK for every page. Read `page.png` and `page_frames.png` each iteration and check section 1 by eye. The default frames include 2.9 s (where flags usually enter); pass `--frames` for your own beats.
4. **Into Power BI** (Pattern A, one fullscreen visual):
   - *Static study*: `page_kit.dax_literal(page_kit.fluid(html))` as the measure - renders exactly as gated, does not react to slicers. Say so.
   - *Live*: port the generator to DAX (CONCATENATEX over ranked VALUES / month series, every number via FORMAT). Acceptance: the unfiltered DAX output is byte-identical to the gated HTML; the stress scenarios each pass `page_check.py`.
   - Then the normal loop (`reference/build-workflow.md`): `gen_pbip.py`, `versions.py snapshot`, reload, Calculate, Desktop screenshot.

## 7. Traps (measured unless marked)

- **Desktop injects its own line-height / font-size into the visual** *(measured)*: a page that fit in the browser was clipped at the bottom in Desktop. `page_kit.fluid` pins both on the root.
- **Fixed px vs the visual size** *(measured)*: `--u = min(100vw/W, 100vh/H)` is exactly 1 px at the design size (pixel-identical render) and scales the page with the visual.
- **clip-path from `inset()` to `none` does not interpolate** - it flips at 50 %. Always an explicit `to{clip-path:inset(0 0 0 0)}`.
- **Stroke-dash draw with `vector-effect:non-scaling-stroke`**: Chromium ignores `pathLength` - the line never looks drawn. Clip wipe on a wrapper for time series.
- **`animation` shorthand without `both`** shows the end state before the delay.
- **Never translate / scale the visual's root** *(measured)*: Desktop kept a horizontal scrollbar. Animate the root's opacity and its children's position.
- **A 1 px line of the fallback `background-color` at the visual edge** *(measured)* when the page is scaled: clip the colour with a final transparent layer, `background-clip:content-box`.
- **Native slicers cannot join an HTML entrance** *(measured)*: keep slicer panels still.
- **The contrast gate reads `background-color` only, and samples mid-animation**: honest solid colours under translucent / gradient surfaces (opacity >= 0.5), animate an overlay's opacity instead of the background under text, keep "dim" start colours >= 3:1.
- **`fit-clip` elements are skipped by the fit gate** - a number made only of odometer strips can read as a void; keep gaps tight.
- **3D**: an overlay that overflows a `backface-visibility:hidden` face inside a `preserve-3d` ring is cut off - make overlays siblings with a small `translateZ`. `-webkit-box-reflect` is unreliable - use a gradient reflection.
- **Fonts**: only Windows fonts (Segoe UI family, Bahnschrift, Consolas, Georgia, Cambria, Sitka, Segoe Script/Print, Ink Free). Bahnschrift and Consolas have no Hebrew glyphs.
- **No `prefers-reduced-motion` query** *(measured)*: Desktop reports `reduce` when Windows animation effects are off and the query hid all motion.
- **Measure names must not equal a column name** of the host table *(measured)*: Desktop refuses to load the model; a DAX query with `DEFINE MEASURE` does not catch it.
- **Untested in Desktop so far** (may degrade, text stays readable): `backdrop-filter`, SVG `feTurbulence`, `mask-image`, blend modes, animated `filter:blur()`, `font-stretch` on Bahnschrift.

## 8. Hebrew / RTL

Root `dir='rtl' lang='he'`, layout mirrored with logical properties, every number / percent / id isolated (`<bdi>` or `direction:ltr;unicode-bidi:isolate`), Hebrew month abbreviations with geresh. **Time axes run left to right** (as `skills/rtl-hebrew` says) and carry a label ("ציר הזמן: משמאל לימין"); a grid of period frames counts as a time axis. **No letter-spacing on Hebrew text**: in languages with tracked caps (3, 9) the tracking applies to Latin and digits only; Hebrew labels stay untracked, weight carries the emphasis.

## 9. Deliverable

Per page: the design language and hero device, how each data field maps to a visual, the gate lines for the page and every stress variant, the Uiverse elements used (path, author, MIT), static vs live DAX, what was checked in Desktop vs only in the headless gate, and the motion budget (settles by N s, loops: none).
