# Interactive operations mode

An extension of `SKILL.md` for dashboards that feel like an operations product: one **twin** of the thing being managed as the hero, motion driven by what the user does (pick a date, switch a view, select an item) rather than by an autoplay entrance, and dense operational instruments around it. Everything stays inside the Secure edition: the interaction is always a **native** visual (slicer, button, page navigation) and the HTML only redraws from DAX.

Status: written from studying interactive product concepts (Nov 2026) and the kit's measured rules; the recipes below are doc-based until a build in this mode is checked in Desktop (the Sales Operations study is the first).

## When to use it

The user asks for an impressive dashboard **and** the subject is something that is operated: a site, a fleet, a store network, a process with steps, a portfolio with a target. Use the plain design languages of `SKILL.md` section 2 for board packs, public screens and one-off reviews.

## Three more design languages

Same rules as `SKILL.md` section 2 (one hero device, exact encoding, a dashboard around it).

| # | Language | Look | Hero data device (exact encoding) | Motion | Good for |
|---|---|---|---|---|---|
| 11 | **Digital twin** | calm grey or warm-neutral app shell, one hot accent, soft cards, small-caps labels | an isometric map of the managed thing: zones (one per top-level entity, e.g. region) holding blocks (one per sub-entity, e.g. category); **block height = the measure on one shared scale**, block colour = the active View (status, vs comparison, margin band); pins mark the latest-period exceptions | blocks grow from the previous as-of step (see "Motion from the previous state"); pins drop last; a short highlight on the blocks that changed most | operations, store networks, portfolios |
| 12 | **Operations console** | light or dark, dense, monospace numbers, status pills | a target-line distribution (histogram; bars past the target hatched in the warning colour) plus an hour/weekday x entity rhythm matrix (dot area = count) and a timeline of upcoming or recent events | bars grow from the axis; the over-target bars hatch in last; the "now" line of the timeline wipes in | SLAs, dwell / lead times, queues |
| 13 | **Mix map** | warm paper, rich category colours, round shapes | circle packing: circle area = value, one ring per comparison size; when ONE parent is selected (slicer / Context), the parent fills the panel and its children are drawn inside it | the children zoom out of the parent's position in the overview (DAX knows that position - see "Drill on select") | spend / revenue mix, category portfolios |

## The four interaction recipes

Each recipe = a native visual that changes the filter context + DAX that redraws. Never a control drawn in the HTML.

1. **As-of replay.** A disconnected table of periods (`'As Of'[Month]`, a calculated table of the fact's month starts) in a native single-select slicer. Measures compute "as of" the selected period:
   `VAR _asof = MAX ( 'As Of'[Month] )` (no selection = the latest month) and filter the fact with `KEEPFILTERS ( 'T'[Date] < EDATE ( _asof, 1 ) )`. Compute the previous step too (`EDATE ( _asof, -1 )`) for the motion. Label the page "as of <month>" - the twin, the KPIs and the charts all follow.
2. **View toggle.** A disconnected table of views (`'View'[View]`: Revenue / Margin / vs LY, with an order column) in a native single-select slicer (or a field parameter). `VAR _view = SELECTEDVALUE ( 'View'[View], "Revenue" )` and `SWITCH ( _view, ... )` for the encoding and the legend. Show the active view in the header.
3. **Drill on select.** `IF ( HASONEVALUE ( 'T'[Region] ), <children view>, <overview> )`. The overview layout is deterministic (the generator / DAX computes every parent's rectangle), so the children view can START at the selected parent's rectangle and grow to the panel: put the parent's rect in CSS variables and animate `translate` / `scale` from it. The reader sees the parent open, not a page swap.
4. **Rich tooltips.** HTML Content's manual tooltips: `class='tooltipEnabled'` with `data-tooltip-title-01` / `data-tooltip-value-01` pairs on each block, bubble, pin and bar. Put the detail there (value, comparison, rank, order count) instead of crowding the hero. Tooltips are an addition: every number the page claims is also visible somewhere without hovering.

## Motion from the previous state

In this mode the meaningful motion is the CHANGE between two states the DAX can compute: the previous as-of step, the comparison period, the parent before the drill. Write both values into the element (`--h0` previous height, `--h` current height; `--x0/--y0/--s0` parent rect) and animate from the first to the second on every render. Rules:
- Everything is visible from the first frame (`SKILL.md` section 4): blocks start at their PREVIOUS height, never at zero or transparent.
- At most one highlight on what changed most (top 3 changes), never on everything.
- The whole change settles in ~1 s - the user will scrub again.

## Insight rail

Up to 5 computed lines in a side panel, each with its number and its basis ("October -45% vs Sep · lowest since Nov 25 · 18 orders (thin)"). Same rules as exceptions (`SKILL.md` section 1): minimum orders, two conditions, computed claims. No input box, no "ask" field, no avatar pretending to be an assistant.

## Product-grade finish

- A KPI rail: value with a superscript unit, a one-line basis, a micro gauge or sparkline, the change pill.
- Small-caps section labels, status pills with a dot, one accent colour plus semantic up / down / warning.
- Soft cards (1 px hairline, large radius), generous inner spacing, monospace for numbers in tables.
- Header with the native page tabs, the as-of selector and the view selector - all native, all in slots.

## What stays out

Drag and drop, accept / approve buttons, toggles drawn in HTML, chat inputs, live-moving vehicles, anything that writes back. They need script or write-back, which the Secure edition does not have; drawn without them they are fake controls.

## Isometric drawing (for language 11)

Project a zone/block grid with `x' = (gx - gy) * cos30 * s`, `y' = (gx + gy) * sin30 * s - z`: each block is three SVG polygons (top rhombus, left face, right face) shaded from one colour (top = colour, left = 15 % darker, right = 30 % darker). Draw back to front (larger `gx + gy` last). Height `z` = value / max * the available height. Labels and pins are HTML positioned at the projected coordinates (so they can carry tooltips and stay crisp). Keep the SVG's aspect ratio (no `preserveAspectRatio='none'`).
