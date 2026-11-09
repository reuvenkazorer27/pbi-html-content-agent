---
name: html-slicers-filters
description: Make HTML Content visuals work with filters, slicers and cross-filtering, in both directions. Use whenever the user asks for working slicers, filter-responsive HTML visuals, clickable filter chips, or HTML that filters other visuals.
---

# Slicers and filters that actually work

## The two directions

**Incoming (HTML visual reacts to filters): always works, zero setup.** Slicers, the filter pane, and cross-filtering from other visuals change the filter context, Power BI re-queries, the measure recomputes, the HTML re-renders. Design implication: never cache values inside markup assuming a fixed context; always compute from measures.

**Outgoing (click in HTML filters other visuals): works only with the Context role.** Recipe:

1. Put at least one **column** in the Context data role (e.g. `Sales[Category]`).
2. Values holds the per-row HTML measure.
3. Format pane → *Cross-filtering* card (appears only when row context exists) → **Enable = on**.
4. Clicks on a row element now select that data point and filter the page like clicking a bar in a native chart. Ctrl+click multi-selects (desktop). Unselected rows dim (70% default; property-configurable or CSS on `.htmlViewerEntry.unselected`).

Right-click on a row gives the data-point context menu, including drillthrough when a drillthrough page exists. Context fields also reconcile report-page tooltips.

## What "an HTML slicer" really is

A chip/list/button column built in HTML Content with the recipe above behaves like clicking data points in a chart: it **cross-filters**. It is not a slicer visual:

- No persistent "slicer state", no Select-all, no search box, no single-select mode, no sync-slicers participation as a slicer.
- Selection highlight must be designed: dimmed `.unselected` rows are the built-in affordance.

When the user needs true slicer behavior (state, select-all, hierarchy, search), use a native slicer and style it into the design (see `skills/composite-dashboard/SKILL.md`). Offer both and say the difference plainly.

Reference implementation: `library/components/slicer-chips.dax`.

## Inner elements that must not filter

A row's root element is the selectable node; a click anywhere inside it cross-filters. For nested controls (links, expand buttons, modals, icon actions) that must not filter:

- `data-hc-suppress="filter"` (plus `context-menu` / `tooltip` / `all` as needed) - declarative, both editions, no script.
- Regular edition scripting alternative: `event.stopPropagation()` in the handler.

## Tooltips

- Rows (Context present): fields in Context and Tooltips roles appear in the standard tooltip; report-page tooltips work through Context reconciliation.
- One-giant-measure visuals: manual binding with `class="tooltipEnabled"` and `data-tooltip-title-XX` / `data-tooltip-value-XX` (matching XX keys).

## Mobile caveat

Multi-select of data points is not supported for custom visuals in the Power BI mobile apps; single-tap selection follows the app's interaction settings. Validate chip slicers on a device before promising them.

## Filter-dependent design rules

- Compute "is filtered / show all" states in DAX (`ISFILTERED`, `ISCROSSFILTERED`, `SELECTEDVALUE`) and render the right markup, including empty-state HTML; also use the visual's "No Data" message property.
- Keep per-row measures returning `BLANK()` for rows that should disappear; the visual drops blank rows.
- Numbers, deltas and charts must degrade gracefully when a filter leaves one row or one period: guard `DIVIDE`, `MIN/MAX` and axis scaling.
