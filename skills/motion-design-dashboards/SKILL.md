---
name: motion-design-dashboards
description: Design and build striking, motion-designed Power BI dashboards in HTML Content - a full design language (materials, type, colour, one hero data device, page choreography) on top of a real, dense dashboard, not a pretty landing page or a data story. CSS keyframes only (Secure edition), real numbers, gated. Optional textures and surfaces from Uiverse.io (MIT). Use when the user asks for an impressive / wow / premium / "go wild" dashboard, a new visual identity for a dashboard, or motion beyond the kit's standard entrances.
---

# Motion-design dashboards

This skill raises the ceiling of what the kit builds: a page that looks designed, moves with intent, and still works as a dashboard a manager scans in ten seconds. It sits on top of `skills/motion` (meaning-carrying motion), `skills/dashboard-shell` (one fullscreen visual, Pattern A) and `skills/composite-dashboard` (Pattern B). Everything here runs in the **Secure** edition: one inline `<style>` per measure, `@keyframes`, inline SVG, CSS gradients. No script.

Verification status: the rules marked *(measured)* were measured in Power BI Desktop (Secure edition, Nov 2026) on full-page examples built with this skill; the design languages and the procedure are gated in headless Edge (`page_check.py`); the Uiverse step is doc-based plus one adapted element checked by `uiverse.py`.

## 1. The contract: a dashboard, never a story

Reviewers rejected beautiful pages that read like a landing page or an essay. Every page must pass all of these:

1. **A KPI row** across the top: 4-6 numbers, each with its basis (period) and its change against a stated comparison (vs previous month / same period last year), arrow + colour + value.
2. **6-9 panels**, each answering one question, each with a short title and a unit ("Revenue by region, K"). Panels have clear boundaries; the page is dense, no decorative empty areas.
3. **The standard instruments are present**: a time series (the hero chart or a strong secondary), a ranked breakdown, a two-dimensional view (matrix / heat grid), a composition (segments, payment, mix), and the exceptions of the latest period.
4. **No prose.** No paragraph, no manifesto, no sentence headline ("Revenue fell 45% in October"). Labels and short captions only (one line, under ~8 words). A flag on the exception carries the sentence-length message.
5. **No fake controls.** No buttons, tabs, toggles, active chips or "filters" that are not real. A static index or legend is fine and must look static. Real filtering = native slicers placed in slots (see `html-slicers-filters`), or the Context role.
6. **Every number is real and every claim is computed** ("lowest since …", "peak", "3rd weakest month"): assert it in the generator or compute it in DAX. No currency symbol the data does not state.
7. **Small selections still work**: one region, one month, empty selection - the layout degrades to empty slots / a "last month only" panel / an empty state, never to errors, `vs BLANK`, or overlapping labels.

Signs of a story page (fix before you ship): a big sentence in the hero, a paragraph anywhere, fewer than 5 panels, a single giant visual without a KPI row, scroll-like vertical narrative, decorative illustration that encodes nothing.

## 2. Choose one design language (mix at most two motifs)

A design language = material + type + colour logic + **one hero data device** + a motion signature. The hero device is where the data becomes the image; everything else is a disciplined dashboard grid around it. Pick by audience and data, not by taste of the moment.

| # | Language | Look | Hero data device | Motion signature | Good for |
|---|---|---|---|---|---|
| 1 | **Instrument HUD** | pale technical ground, blueprint grid, monospace readouts, one hot accent, part numbers, dimension lines | the total as a core assembly that explodes into segment modules (leader lines, plates sized by value), a spec sheet beside it | assembly flies apart from the core; dimension lines draw; a playhead sweeps the periods once and stops on the exception | operations, engineering, product mix |
| 2 | **Cylinder shelf** | deep cool stage, period cards in a 3D ring, glossy cards with a fill "tank" | each period is a card on a ring, fill = value / peak, the latest card faces the viewer | the ring assembles small and tilted, then opens around the viewer; a counter reaches 100 % | monthly performance, seasonality |
| 3 | **Depth line-up** | white / ice stage, wide tracked caps, soft floor shadows | ranked entities as tall figures at depths (x, height, blur, opacity interpolated by rank); each figure is stacked from its components | figures walk in from one step further back; a scan line reveals the leader; rank counter rolls | rankings of regions, teams, stores |
| 4 | **Orb command center** | near-black, a coloured light from the top, frosted panels, gradient hairline on the hero only | a glass sphere holding the total, rings around it = shares, an outer ring = margin | rail and header rise, the orb opens with a circular clip, numbers rise out of masks, panels settle | executive overview, dark rooms, TV walls |
| 5 | **Atmosphere glass** | one atmospheric gradient stage; panels repaint the same stage at their own position under a white veil = seamless glass | a smooth wave chart with the values row above it, the active period in bold | panels slide in from the side one by one; the wave draws with the fill following the pen | trend-led pages, public screens |
| 6 | **Calm bento** | warm neutral page, off-white cards, hairlines, soft shadows, one accent colour | tick gauges per entity (ticks gained vs lost), odometer tiles, a route with milestone pins | ticks sweep, gained ticks arrive last, lost ticks fade out; pins land as the pen passes | balanced KPI pages, management packs |
| 7 | **Night grid ops** | near-black with a faint grid, violet / teal glow, gradient hairline borders | glowing columns per period (exceptions in a warning hue), tick gauges | columns grow from the axis, labels rise, the exception pulses twice | monitoring, SLA, operations |
| 8 | **Contact sheet** | paper + one ink colour, dot screens, print marks | a grid of period frames cut from ONE shared image, each frame "developed" to its value; a hand-drawn circle around the exception | frames develop in sequence; the circle draws itself | monthly reviews, marketing |
| 9 | **Monochrome editorial** | strict black / white / greys, giant numerals, heavy condensed type | an oversized number system: KPI numerals as the main graphic, discs sized by value | numerals rise out of masks, discs pop by rank | board packs, investor style |
| 10 | **Topographic** | misty neutral, one ink colour, one lime accent, mono labels | contour rings = cumulative thresholds; entities as pins on the terrain | contours draw from the edge inward; pins drop | cumulative goals - use as ONE panel, it pulls toward story |

Rules for every language: the palette has one hero accent plus semantic up / down / warning; text contrast WCAG AA on the real background; at most one hero device; the grid around it follows section 1.

## 3. Motion grammar

- **Meaning first** (`skills/motion`): animate the change (roll from the previous value, bars move from the previous value, gained / lost ticks), the exception (a flag, a ring that pulses at most twice), the rank (walk-in order), the freshness. Decoration (sheen, drift) only once and only on the hero.
- **One clock for the page.** Every delay = beat + offset. Order: frame/grid -> header -> KPI row -> hero device -> panels (reading order) -> data marks -> exception flag -> optional coda. Each element enters once.
- **Three curves**: settle `cubic-bezier(.16,1,.3,1)` (things arriving), pen `cubic-bezier(.45,0,.25,1)` (lines and wipes), soft `cubic-bezier(.25,.46,.45,.94)` (fades). Overshoot (`cubic-bezier(.34,1.56,.64,1)`) only on chips and dots, never on data lengths.
- **Budget**: the page settles by ~6 s; data entrances under ~1.6 s per element; alerts at most 2 cycles; no `infinite`, ever. The entrance replays on every filter change and refresh - keep it short enough to live with.
- **Devices** (all CSS): mask rise (overflow box + translate), odometer (0-9 digit strips, start at the previous value's digit), pen draw (clip wipe on a wrapper for time series; `pathLength` dash only on a non-distorted SVG), fill follows the pen ~0.2 s behind, tick sweep, rank walk-in (translate + scale + blur from the next depth), ring assembly (3D transforms), develop (a fill or veil revealing a value level), stamp/flag wipe.

## 4. Materials from Uiverse.io (optional, MIT)

Uiverse.io is an open-source library of HTML/CSS elements (github.com/uiverse-io/galaxy, MIT License, Copyright (c) 2023 Uiverse.io). Use it to complete the imagery of a page - textures, backgrounds, card surfaces, badges - not for behaviour.

- **Use**: `Patterns` (backgrounds, textures, grids, dot screens), `Cards` (surfaces and frames), `Notifications` (alert-chip shapes).
- **Never**: `loaders` (endless loops), `Buttons`, `Toggle-switches`, `Checkboxes`, `Radio-buttons`, `Inputs`, `Forms` (fake controls in a dashboard).
- **Procedure**: `python -I tools/pbip-html-pipeline/uiverse.py list Patterns` -> pick -> `python -I tools/pbip-html-pipeline/uiverse.py get Patterns/<file>.html --prefix bg1 --out el.html`. The tool scopes every class to the prefix, keeps the author comment, and reports what must be removed (`:hover`-only effects, `infinite`, external `url()`, script). Merge its CSS into your single `<style>`, recolour it to your palette, and keep the attribution comment. List every element used (path, author, MIT) in the deliverable.
- A texture under text needs a solid `background-color` fallback that the contrast gate can check.

## 5. Build procedure

1. **Data**: aggregate in the generator (Python stdlib) for a static design study, or write the DAX directly. Real data only; assert totals.
2. **Page**: ONE root `<div>` with ONE `<style>` inside. Root: `box-sizing:border-box;height:100vh;width:100%;overflow:hidden` and an explicit `background-color` = the honest worst case behind the text. Content 8 px inside the edges. Size everything in `calc(N*var(--u))` (or write px and let `page_kit.fluid()` convert): the page then scales with the visual.
3. **Gate**: `python -I tools/pbip-html-pipeline/page_check.py page.html` -> SECURE LINT OK, FIT OK, CONTRAST OK, frozen frames. Read the PNG and the frame montage every iteration; check the section-1 contract by eye.
4. **Into Power BI** (Pattern A, one fullscreen visual):
   - *Static study*: `page_kit.dax_literal(page_kit.fluid(html))` as the measure - renders exactly as gated, does not react to slicers. Say so.
   - *Live*: port the generator to DAX (CONCATENATEX over ranked VALUES / month series, every number via FORMAT). Acceptance: the unfiltered DAX output is byte-identical to the gated HTML; then the stress scenarios (one value per slicer column, one month, a narrow combination, empty) each pass `page_check.py`.
   - Then the normal loop: `gen_pbip.py`, reload, Calculate, Desktop screenshot (`reference/build-workflow.md`).

## 6. Traps (measured unless marked)

- **Desktop injects its own line-height / font-size into the visual** *(measured)*: a page that fit in the browser was clipped at the bottom in Desktop. Pin `line-height` and `font-size` on the root (`page_kit.fluid` does it).
- **Fixed px vs the visual size** *(measured)*: use `--u = min(100vw/W, 100vh/H)`; at the design size it is exactly 1 px (pixel-identical render).
- **clip-path from `inset()` to `none` does not interpolate** - it flips at 50 %. Always give an explicit `to{clip-path:inset(0 0 0 0)}`.
- **Stroke-dash draw with `vector-effect:non-scaling-stroke`**: Chromium ignores `pathLength` (dash computed in px) - the line never looks drawn. For time series use a clip wipe on a wrapper; use `pathLength='1'` only on SVGs that keep their aspect.
- **`animation` shorthand without `both`**: the element shows its end state before its delay - always `both` for entrances.
- **Never translate / scale the visual's root** *(measured)*: Desktop kept a horizontal scrollbar at the bottom of the card. Animate the root's opacity and its children's position.
- **A 1px line of the fallback `background-color` at the visual edge** *(measured)* when the page is scaled: clip the colour with a final transparent layer `background-clip:content-box`.
- **Native slicers cannot join an HTML entrance** *(measured)*: a panel that slides in leaves its slicers floating - keep slicer panels still.
- **The contrast gate reads `background-color` only, and samples mid-animation**: give translucent / gradient surfaces an honest solid colour (opacity >= 0.5), animate an overlay's opacity instead of the background under text, and keep "dim" start colours >= 3:1.
- **`fit-clip` elements are skipped by the fit gate** - a number made only of odometer strips can read as a void; keep gaps tight. Mark clipped-on-purpose items `fit-clip`, full-bleed bands `data-bleed`, intentional empty decoration `data-fill='free'`.
- **3D**: an overlay that overflows a `backface-visibility:hidden` face inside a `preserve-3d` ring is cut off - make overlays siblings with a small `translateZ`. `-webkit-box-reflect` is unreliable - use a gradient reflection.
- **Fonts**: only Windows fonts (Segoe UI family, Bahnschrift, Consolas, Georgia, Cambria, Sitka, Segoe Script/Print, Ink Free). Bahnschrift and Consolas have no Hebrew glyphs.
- **No `prefers-reduced-motion` query** *(measured)*: Desktop reports `reduce` when Windows animation effects are off and the query hid all motion. Keep motion short and finite instead; say so in the deliverable.
- **Measure names must not equal a column name** of the host table *(measured)*: Desktop refuses to load the model; a DAX query with `DEFINE MEASURE` does not catch it.
- **Untested in Desktop so far** (render may degrade, text stays readable): `backdrop-filter`, SVG `feTurbulence`, `mask-image`, blend modes, animated `filter:blur()`.

## 7. Hebrew / RTL

Root `dir='rtl' lang='he'`, layout mirrored, every number / percent / id isolated (`direction:ltr;unicode-bidi:isolate` or `<bdi>`), Hebrew month abbreviations with geresh, time axis direction labelled. See `skills/rtl-hebrew`.

## 8. Deliverable

State per page: the design language and hero device, how each data field maps to a visual, the gate lines, the Uiverse elements used (path, author, MIT), what is static vs live DAX, what was checked in Desktop vs only in the headless gate, and the motion budget (settles by N s, loops: none).
