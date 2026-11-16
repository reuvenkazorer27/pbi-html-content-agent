# Interactive operations mode

An extension of `SKILL.md` for dashboards that feel like an operations product: one **twin** of the thing being managed as the hero, motion driven by what the user does (pick a date, switch a view, select an item) rather than by an autoplay entrance, and dense operational instruments around it. Everything stays inside the Secure edition: the interaction is always a **native** visual (slicer, button, page navigation) and the HTML only redraws from DAX.

Status: the three languages and the page rules below were gated with `page_check.py` on full-page builds (every language, five states each: latest, an earlier as-of month, another view, a drill or filter, empty). The slicer recipes are doc-based until a build in this mode is measured in Desktop with the selection changed.

## When to use it

The user asks for an impressive dashboard **and** the subject is something that is operated: a site, a fleet, a store network, a process with steps, a portfolio with a target. Use the plain design languages of `SKILL.md` section 2 for board packs, public screens and one-off reviews.

## Three more design languages

Same rules as `SKILL.md` section 2 (one hero device, exact encoding, a dashboard around it).

| # | Language | Look | Hero data device (exact encoding) | Motion | Good for |
|---|---|---|---|---|---|
| 11 | **Digital twin** | calm grey or warm-neutral app shell, one hot accent, soft cards, small-caps labels | an isometric map of the managed thing: zones (one per top-level entity, e.g. region) holding blocks (one per sub-entity, e.g. category); **block height = the measure on one shared scale**, block colour = the active View (status, vs comparison, margin band); pins mark the latest-period exceptions. A long, linear thing (a line, a train, a conveyor) is drawn side-on with depth instead - see "Isometric drawing" | blocks grow from the previous as-of step (see "Motion from the previous state"); pins drop last; one highlight on what changed most | operations, store networks, portfolios |
| 12 | **Operations console** | light or dark, dense, monospace numbers, status pills | a target-line distribution (histogram; the bars on the BAD side of the target hatched - in the warning colour when past the target is bad, e.g. lead time; when past the target is good, e.g. order value, hatch the side below it) plus an hour/weekday x entity rhythm matrix (dot area = count) and a timeline or status list of recent events | bars grow from their previous height; the hatching comes in last; the "now" line of the timeline wipes in | SLAs, dwell / lead times, queues, month-close checks |
| 13 | **Mix map** | warm paper, rich category colours, round shapes | circle packing: circle area = value, one dashed ring per circle at its comparison value (same period last year); when ONE parent is selected, the parent fills the panel and its children are drawn inside it | the children open out of the parent's position in the overview (DAX knows that position - see "Drill on select") | spend / revenue mix, category portfolios |

**Thin periods.** When one month holds few rows (under ~30), the hero shows a longer window that ends at the as-of month (year to date, or the last 3-6 months) and says so; the KPI rail keeps the month and adds the longer basis.

## The four interaction recipes

Each recipe = a native visual that changes the filter context + DAX that redraws. Never a control drawn in the HTML.

1. **As-of replay.** A disconnected table of periods (`'As Of'[Month]`, a calculated table of the fact's month starts) in a native single-select slicer. A single-select slicer selects its FIRST item when nothing is selected (`strictSingleSelect`: "the first available will be automatically chosen"), so sort the months latest first: add a key column (e.g. `Recent = -INT ( [Month] )`) and set `sortByColumn: Recent` on `Month`. Measures compute "as of" the selected period:
   `VAR _asof = MAX ( 'As Of'[Month] )` and filter the fact with `KEEPFILTERS ( 'T'[Date] < EDATE ( _asof, 1 ) )`. Every window ends at the as-of month (the twin's last column, the trend's "now" line). Compute the previous step too (`EDATE ( _asof, -1 )`) for the motion. Label the page "as of <month>" - the twin, the KPIs and the charts all follow. A step before the data starts has no comparison: say "no previous year" instead of a change.
2. **View toggle.** A disconnected table of views (`'View'[View]`: Revenue / Margin / vs LY, with an order column) in a native single-select slicer (or a field parameter). `VAR _view = SELECTEDVALUE ( 'View'[View], "Revenue" )` and `SWITCH ( _view, ... )` for the encoding and the legend. A view changes what is encoded (colour, the measure shown in labels), not the layout - keep sizes and positions stable so the motion compares like with like. Show the active view in the header.
3. **Drill on select.** `IF ( ISFILTERED ( 'T'[Region] ) && HASONEVALUE ( 'T'[Region] ), <children view>, <overview> )` - `HASONEVALUE` alone is also true when other filters happen to leave one region, and the page would drill although nobody selected it. The drill follows the selection whatever the View is. The overview layout is deterministic (the generator / DAX computes every parent's rectangle), so the children view can START at the selected parent's rectangle and grow to the panel: put the parent's rect in CSS variables and animate `translate` plus a `scale` that ends at 1 (into the element's final size, thin borders only - section 3 of `SKILL.md`: a CSS-variable scale ABOVE 1 blows up the border). The reader sees the parent open, not a page swap; mark where it came from with a dashed outline.
4. **Rich tooltips.** HTML Content's manual tooltips: `class='tooltipEnabled'` with `data-tooltip-title-01` / `data-tooltip-value-01` pairs (numbered per element, 01, 02 ...) on each block, bubble, pin, bar and row. Put the detail there (value, comparison, rank, order count) instead of crowding the hero. Tooltips are an addition: every number the page claims is also visible somewhere without hovering.

## Motion from the previous state

In this mode the meaningful motion is the CHANGE between two states the DAX can compute: the previous as-of step, the comparison period, the parent before the drill. Write both values into the element (`--h0` previous height, `--h` current height; `--x0/--y0/--s0` parent rect) and animate from the first to the second on every render. Rules:
- Everything is visible from the first frame (`SKILL.md` section 4): blocks start at their PREVIOUS height, never at zero or transparent. No previous value (the first period, a new member) - start from the comparison value, or show the final state without motion; never invent a start.
- Marks without a length: a status pill or a categorical cell tints its background from the previous status colour to the current one; a rank row slides from its previous position.
- A rolling window (the last 13 weeks, 12 months): the columns both states share did not change, so animate the new column(s) from the comparison value and put the highlight there.
- **One highlight**: one treatment (a ring that pulses twice) on up to 3 items with the largest absolute change against the previous step - never on everything, never a second highlight style.
- A re-render after a slicer change settles in ~1.5 s (the user will scrub again); the first render follows the page budget of `SKILL.md` section 4.

## Insight rail

Up to 5 computed lines in a side panel, each with its number and its basis ("October -45% vs Sep · lowest since Nov 25 · 18 orders (thin)"). Same rules as exceptions (`SKILL.md` section 1): minimum orders, two conditions, computed claims; do not repeat a line the exceptions panel already shows. With no rows in the selection it shows one line that says so. No input box, no "ask" field, no avatar pretending to be an assistant.

## Work queues

A review queue (orders to check, items over a rule) is a status list: each row with its status pill (review / watch / clear) and the rule that put it there, the rules stated in the panel footer. No accept / approve / assign buttons - the queue says what needs a human, the work happens elsewhere.

## Product-grade finish

- A KPI rail: value with a superscript unit, a one-line basis, a micro gauge or sparkline, the change pill.
- Small-caps section labels, status pills with a dot, one accent colour plus semantic up / down / warning.
- Soft cards (1 px hairline, large radius), generous inner spacing, monospace for numbers in tables.
- Header: the title, a context line built from the filter state ("as of Oct 2026 · view Revenue · Region: Europe"), and the as-of and view slicer slots. Page tabs only when the report has those pages - each tab with a native button over it (`SKILL.md` section 7); a one-page report has no tabs.

## What stays out

Drag and drop, accept / approve buttons, toggles drawn in HTML, chat inputs, live-moving vehicles, anything that writes back. They need script or write-back, which the Secure edition does not have; drawn without them they are fake controls.

## Isometric drawing (for language 11)

Project a zone/block grid with `x' = (gx - gy) * cos30 * s`, `y' = (gx + gy) * sin30 * s - z`: each block is three SVG polygons (top rhombus, left face, right face) shaded from one colour (top = colour, left = 15 % darker, right = 30 % darker). Draw back to front (larger `gx + gy` last). Height `z` = value / max * the available height. Labels and pins are HTML positioned at the projected coordinates (so they can carry tooltips and stay crisp). Keep the SVG's aspect ratio (no `preserveAspectRatio='none'`).

A long, linear object does not fit: at 30 degrees an 800 px long run needs about 460 px of height. Draw it side-on with depth (front face plus a skewed top and side, same shading rule), with the same one shared height scale. To grow a block inside a skewed group, scale it about its base (`transform-origin` at the bottom edge), not its height attribute.
