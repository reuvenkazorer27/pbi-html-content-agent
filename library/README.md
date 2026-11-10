# Component library

Static, paste-ready DAX components. They are doc-based unless a row says otherwise; the gated builders in `tools/pbip-html-pipeline/components.py` come first (see the main README).

## What is in it

Each component is one `.dax` file: a ready-to-paste measure + a CSS block for the Stylesheet property + binding and sizing notes. All of them are RTL-clean (numbers, currency and dates are isolated correctly), and all work in both editions unless stated otherwise.

The library has three layers. Its core is the differentiation layer: components that give value the built-in visuals do not. What to build was decided from documented demand research (what users actually ask for on reddit, Microsoft Ideas and AppSource downloads - see `research/user-demand.md`), and every "no built-in equivalent" claim was checked against the specific feature page on Microsoft Learn (not only the catalog list) on 9 Nov 2026 and classified honestly: no built-in / built-in workaround exists / built-in exists and HTML adds composition - see `SOURCES.md`.

### Differentiation layer - the value HTML adds beyond the built-ins

Every "no built-in" claim here was checked against the official feature page on Microsoft Learn on 9 Nov 2026 (links in `SOURCES.md`) and is classified in one of three ways: **no built-in at all**, **built-in workaround exists** (works, but not in this form), or **built-in exists and HTML adds composition**.

| Component | What it gives | Status versus the built-ins |
| --- | --- | --- |
| `insight-narrative` | An insight sentence computed entirely in DAX: values, colored up/down tokens and a sparkline inside the sentence | **Built-in exists**: the Narrative visual (smart narrative, custom mode) writes text with dynamic values - without a chart inside the sentence, without styled tokens and without precise bidi isolation |
| `exception-cards` | An operational exception queue: only categories below target are drawn (empty rows drop out), each row with gap, severity and a recommended action | **No built-in**: a table with conditional formatting gives data, not a designed action queue |
| `stage-tracker` | A sequence of connected process stages: status per stage, a counter, and conversion % on the connectors | **No built-in**: Funnel shows falling values as bars, not a status flow with conversions |
| `variance-columns` | A filled actual column + an outlined plan column + a green/red variance bridge + signed % (IBCS) | **No built-in**; the common commercial solution (Zebra BI) is paid |
| `bullet-chart` | Actual versus target on quality bands (65/85/100%) with a target marker | **No built-in**; [SQLBI](https://www.sqlbi.com/articles/building-bullet-charts-in-power-bi-reports/): assembled "MacGyver" style from columns. AppSource: OKVIZ, xViz |
| `dumbbell-chart` | Two periods as connected dots + a signed delta per category | **No built-in**; AppSource: MAQ and others |
| `lollipop-chart` | A stem + a value dot in a status color versus target; lighter than columns | **No built-in** |
| `waffle-chart` | A 10×10 grid where each cell is one percent of the target | **No built-in**; AppSource: Waffle Chart and others |
| `calendar-heatmap` | A GitHub-style daily density floor for a year, 365 Context rows | **Built-in workaround exists**: a matrix with background conditional formatting gives a heat grid, not GitHub's week-columns shape; AppSource: OKVIZ ProCalendar |
| `kpi-trend` | A rich KPI card: value + sparkline + YoY pill + target-attainment pill + status edge | **Partly built-in**: the modern Card gives value + reference labels + images, but no sparkline inside the card (built-in sparklines exist only in table/matrix) |
| `scorecard-table` | A metric row with a wide sparkline + value + completion pill + status dot | **Built-in exists**: sparklines in table/matrix exist (in preview); here the full composition is one row with exact styling |
| `alert-banner` | A conditional exceptions banner: how many categories are below target, and which | **Complements built-in**: data alerts exist (Service, and Activator in preview) but they are notifications; there is no designed in-canvas banner |
| `filter-banner` | The active filter state as styled chips inside the canvas itself | **Built-in workaround exists**: a Card with a dynamic text measure prints the state as plain text; the filter pane is outside the canvas |
| `radial-progress` | A thin progress ring with the KPI in the center | **Built-in workaround exists**: the Gauge is a dial with a needle, and a donut coerced into a ring - not a thin ring with designed center content |
| `milestone-timeline` | A flat timeline: milestone markers alternating above/below the axis, with name + date, status color (done/current/planned) | **No built-in**: the built-in Gantt (preview) is a task scheduler with durations - not a light milestone strip; direct demand on reddit (2022, 2023). Documented limit: a single axis; milestones that are too dense collide |
| `org-strip` | A fixed hierarchy chart: root + up to 6 subordinate cards with connectors, all positioned by DAX | **No built-in**: [an official Microsoft Epic idea](https://community.fabric.microsoft.com/t5/Fabric-Ideas/Epic-idea-Organization-chart/idi-p/4520633) (10/2024) with user requests. Documented limit: exactly two levels, no expand/collapse and no dynamic depth |

### Skeleton layer

`header-bar` · `side-menu` · `slicer-chips` · and a full shell in `library/shell/`

Paste instructions for each component are at the top of its file, including its layer and rationale. Full color palettes are in `library/palettes.md`.

## Interactivity: what each component can do (verified against the official docs, 9 Nov 2026)

Source: https://html-content.com/docs/interactivity. The rule: Power BI resolves a clicked element to a data row only if the visual is built with rows in the Context role. A complete practical example (including a manual tooltip, hover, unselected, `data-hc-suppress`): `examples/context-interaction.dax`.

| Class | Components | What works |
| --- | --- | --- |
| **Row-bound (Context), 12 components** - a click filters other visuals, contextual tooltip, right-click drillthrough | bar-chart-svg, bullet-chart, calendar-heatmap, data-table, data-table-databars, donut-legend, dumbbell-chart, exception-cards, lollipop-chart, scorecard-table, slicer-chips, variance-columns | Everything - after turning on Cross-filtering > Enable in the format pane |
| **Optional Context, 4 components** - a single measure by default; adding a column to Context makes it per-row | badge-status, donut-svg, progress-bar, kpi-card | Without Context: display only. With Context: like row-bound |
| **Single aggregated measure, 16 components** - no row resolution; manual tooltip possible (`tooltipEnabled` + `data-tooltip-*`) | alert-banner, filter-banner, gauge-svg, header-bar, insight-narrative, kpi-card-icon, kpi-card-sparkline, kpi-trend, line-chart-area, line-chart-svg, milestone-timeline, org-strip, radial-progress, side-menu, stage-tracker, waffle-chart | Manual tooltip only; no cross-filter |

Hard limits (every edition): no writeback to the model, no triggering export, no live hover sync between two separate visuals, no control over other slicers. Page navigation = native buttons over the HTML only.

**Custom icons (Kubai, MIT):** `library/icons/` - 12 static SVGs for inline embedding in KPI cards and the side menu, with embedding instructions and license. Example: `examples/kpi-with-icon.dax`.
