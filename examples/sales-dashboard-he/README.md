# Working example: an RTL composite sales dashboard on a 1280×720 canvas

A complete example of pattern B (composite) with a top KPI row, a dense, orderly layout with no dead space, and components that use what HTML can do beyond the built-ins: IBCS variance columns, a dumbbell chart, exception cards with a recommended action, a process stage tracker, a computed narrative with a sparkline inside the sentence, a scorecard and a filter-state banner - next to a native slicer and a right-docked side menu with transparent native navigation buttons.

**Edition:** HTML Content Secure is enough for everything here (no scripts and no external resources), so the dashboard is also included in export to PDF/PowerPoint.
**Verification status:** not run in Power BI. Based on the 2.0 documentation only. Run `../../checklists/validation.md` before use. Note: this example predates the measured fit contract - before building it, apply `../../AGENTS.md` section 0 and `../../LESSONS.md` (container padding 0, inline `text-align:right`, the type scale).

## Page layout (all numbers in pixels, multiples of 8)

Page background: `#F4F7FA` (Ocean BI `bg`). For every HTML visual: Effects > Background/Border/Shadow off. Usable width 1232 (24 margins), a 200-wide menu on the right (x=1056), content area 24..1040 at a width of 1016, gutters of 8 only - that keeps the layout dense.

| # | Role | Type | x | y | w | h | z |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Header | HTML Content: `HTML Header` | 24 | 16 | 1232 | 56 | 1 |
| 2 | Side menu | HTML Content: `HTML Side Menu` | 1056 | 80 | 200 | 624 | 1 |
| 3 | Navigation button: Sales | Native blank button (transparent) | over the first menu item | | | | 3 |
| 4 | Navigation button: Products | Native blank button (transparent) | over the second menu item | | | | 3 |
| 5 | KPI: Revenue | HTML Content: `HTML KPI Trend - Revenue` | 24 | 80 | 248 | 120 | 1 |
| 6 | KPI: Orders | HTML Content: `HTML KPI Trend - Orders` | 280 | 80 | 248 | 120 | 1 |
| 7 | KPI: Average basket | HTML Content: `HTML KPI Trend - Avg Basket` | 536 | 80 | 248 | 120 | 1 |
| 8 | KPI: Gross profit | HTML Content: `HTML KPI Trend - Gross Profit` | 792 | 80 | 248 | 120 | 1 |
| 9 | Filter-state banner | HTML Content: `HTML Filter Banner` | 24 | 208 | 688 | 40 | 1 |
| 10 | Year slicer | Native slicer on `Date[Year]` (tile style) | 728 | 208 | 312 | 40 | 1 |
| 11 | IBCS variance | HTML Content: `HTML Variance Row` + Context=`Sales[Category]` | 24 | 256 | 496 | 256 | 1 |
| 12 | Exception cards | HTML Content: `HTML Exception Row` + Context=`Sales[Category]` | 536 | 256 | 504 | 160 | 1 |
| 13 | Stage tracker | HTML Content: `HTML Stage Tracker` | 536 | 424 | 504 | 88 | 1 |
| 14 | Narrative | HTML Content: `HTML Narrative - Revenue` | 24 | 520 | 1016 | 48 | 1 |
| 15 | Scorecard: categories | HTML Content: `HTML Scorecard Row` + Context=`Sales[Category]` | 24 | 576 | 496 | 128 | 1 |
| 16 | Dumbbell: this year versus last year | HTML Content: `HTML Dumbbell Row` + Context=`Sales[Category]` | 536 | 576 | 504 | 128 | 1 |

Width arithmetic: 4 KPI cards of 248 + 3 gutters of 8 = 1016. Each row: 496 + 8 + 504 = 1008, plus an 8 gutter to the menu. Height arithmetic: the KPI row ends at 200, filters 208-248, middle 256-512, narrative 520-568, bottom row 576-704. The KPIs are always the first row under the header, and no empty area is larger than one gutter.

## What "works" in this dashboard (precisely)

- The year slicer (native) filters every HTML visual. Always works, no setup. The filter-state banner reflects it through `SELECTEDVALUE`/`ISFILTERED`.
- The visuals with Context (11, 14, 15, 16) respond to every filter on the page, and right-click opens a context menu including drillthrough if a drillthrough page exists. If Cross-filtering > Enable is turned on in one of them, clicking a row also filters the others.
- The alert banner is computed in DAX: how many categories are below target, and which, with a status color.
- The menu items navigate between pages through transparent native buttons placed over them (rows 3-4 in the table). The HTML itself does not navigate.
- Export to PDF: works because all visuals are Secure.

## Build steps in Desktop

1. Make sure the page is 16:9 at 1280×720 (Format page > Canvas settings).
2. Install HTML Content Secure from AppSource (search for "HTML Content Secure").
3. Create a measure table named `_HTML` and paste the measures from `measures.dax` into it (adapt table/column names to your model).
4. For each row of the layout table: add an HTML Content visual, bind the measure to Values (and the Context column where noted), and set position and size from the table.
5. Paste each component's CSS into that visual's Stylesheet (or one shared stylesheet through fx on a measure).
6. Place the transparent navigation buttons over the menu items (Insert > Buttons > Blank > Action > Page navigation), and record the rectangles in the table.
7. Run `../../checklists/validation.md`.

## Files

- `measures.dax` - all of the dashboard's measures (copied from the library, adapted to the example model's names).
- The original components: `../../library/components/`.
