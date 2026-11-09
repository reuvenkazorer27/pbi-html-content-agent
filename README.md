# PBI HTML Content Agent

An agent folder for working with the **HTML Content** custom visual in Power BI: building dashboards from DAX-generated HTML, either as a complete dashboard inside one full-canvas visual, or as a composite dashboard of several visuals working together over a regular Power BI page background.

## What the agent can do

- Produce visuals that Power BI does not ship built-in: a bullet chart with quality bands, IBCS variance columns (actual / plan / variance), a dumbbell chart for period comparison, lollipop, a GitHub-style calendar heatmap, waffle, a scorecard table with an in-cell sparkline, a conditional alert banner and a styled filter-state banner, a flat milestone timeline, and a fixed hierarchy chart (org strip) - plus foundation components (KPI cards, column/line/donut charts, tables) for fullscreen mode.
- Build a **complete dashboard inside one visual** that covers the whole canvas (a fullscreen shell with header, side menu and content area).
- Build a **composite dashboard** of several HTML Content visuals at exact sizes that blend with the page background and with native visuals.
- Wire **real slicers and filtering**: the visual responds to slicers and filters, and can also filter other visuals (cross-filter) when it is built correctly with the Context role.
- Build a side menu and header, including real page navigation (through native buttons layered over the HTML - no fake navigation).
- Work **fully in Hebrew with correct RTL**: mixed text with numbers, currency, dates and English names, charts that start from the right, a right-docked menu.
- Work with a **color palette library** and the theme color variables (`--pbi-theme-*`), so the content matches a background that is not drawn in HTML.
- Write HTML Content visuals directly into PBIR files (`visual.json`), including the GUIDs of both editions.
- Build, check and version a dashboard end to end with `tools/pbip-html-pipeline/`: live DAX test against the open model, exact-size preview, automatic fit / WCAG contrast / filter-stress gates, a byte-level regression gate, palettes (light, dark, colorful), and snapshots with diff and revert (git commit + tag per snapshot).

## What the agent will not do (and will not pretend to do)

- It will not build "HTML buttons" that look clickable but do nothing. Page navigation happens only through native Power BI buttons or through a real cross-filter.
- It will not promise that scripts work in the Secure (certified) edition. There, the sanitizer removes them.
- It will not use localStorage, cookies, pop-up windows or external scripts. The Power BI sandbox blocks them in every edition.
- It will not present anything as "tested" unless it was run. Every component states what is based on official documentation and what still needs validation in Desktop.

## Folder structure

| Path | What is there |
| --- | --- |
| `AGENTS.md` | The agent's main brief - the file the agent reads first, including the fit-to-canvas contract. |
| `LESSONS.md` | Lessons measured in real Power BI Desktop sessions. They override the docs. |
| `ROADMAP.md` | The 20-step plan with built / researched status. |
| `reference/` | Verified knowledge about the visual: capabilities, limits, canvas sizes, PBIR. With links to sources. |
| `research/` | Demand research: what users actually ask for and do not have, and how each library component was decided against demand and the built-in visuals. |
| `skills/` | Five skills: dashboard-shell, composite-dashboard, html-slicers-filters, navigation-header-menu, rtl-hebrew. |
| `library/` | Ready-to-paste components: `.dax` files with CSS, color palettes, and a shell for a fullscreen dashboard. |
| `examples/` | A complete working example: a Hebrew RTL sales dashboard on a 720p canvas, with exact coordinates. |
| `tools/pbip-html-pipeline/` | The build / gate / version / write pipeline (see its README). |
| `checklists/` | Validation checklist: what to check in Desktop, in the Service, on mobile and in export before a dashboard is handed over. |
| `SOURCES.md` | Every factual claim in the folder linked to its live source, with the check date. |

## What is in the component library (`library/components/`)

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

## How to work with it

1. Copy the folder into the project (next to the PBIP, or into a general working folder).
2. Point the agent (Claude Code, Cursor or any other agent) to read `AGENTS.md` and `LESSONS.md` at the start of the session.
3. Ask for a dashboard in natural language, for example: "Build me an RTL sales dashboard with a KPI row, a right side menu and a working year slicer". The agent picks the matching pattern, uses the component library and the pipeline, and states explicitly what was verified and what still needs your validation.

## Visual editions (important before you start)

The HTML Content visual (by Daniel Marsh-Patrick, free and open source) ships as two separate editions on AppSource:

- **HTML Content (Regular)** - the most flexible: all the HTML/CSS/SVG the sandbox allows, external images, and from version 2.0 also `<script>` execution and inline event handlers. Uncertified, so it is not included in export to PDF/PowerPoint or in email subscriptions.
- **HTML Content Secure 🛡️** (formerly HTML Content (lite)) - certified by Microsoft: sanitized, no external resources, no scripts. Suitable for organizations restricted to certified visuals, and included in export.

Every library component is marked with the edition it suits. The agent's default is Secure, unless the need requires Regular (for example scripts or external content).

## Verification status

- **Measured in Power BI Desktop (Oct 2026 release, 9 Nov 2026):** the fit-to-canvas contract, the pipeline (`tools/pbip-html-pipeline/`) and the lessons in `LESSONS.md`, on a real 1920×1080 Hebrew RTL dashboard with the Secure edition - including padding 0, RTL alignment, the type scale, palette-driven slicers, the gradient background layer and filled KPI cards.
- **Documentation-based, not yet run in Desktop:** the components in `library/components/` and the example in `examples/` (written from the HTML Content 2.0 docs, the PBIR Implementation Guide and Microsoft Learn, 9 Nov 2026), and the items marked 📋 in `ROADMAP.md`. Before production use, run `checklists/validation.md`. Every component that needs checking is marked `not run in Power BI`.
