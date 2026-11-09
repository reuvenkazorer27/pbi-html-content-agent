# Demand research: what Power BI users actually ask for and don't have

Review date: 09/11/2026. Goal: ground the library's differentiation layer in documented user demand, not in assumptions drawn from the catalog list. For each row: the exact demand evidence (quote + date + link), the status versus the built-in feature (the feature's owning feature page), feasibility in HTML Content, and the decision.

## Evidence types (and their weight)

1. **Direct user request** - a quote from reddit / Fabric Ideas. The strongest evidence of demand.
2. **Community expert wishlist** - Data Goblins; documents recurring requests from the field.
3. **AppSource downloads leaderboard** (DataChant, snapshot 24/07/2025) - **proxy only**: the popularity of third-party visuals suggests people are looking for something beyond the built-in, but it does not prove the feature is missing from the built-in, nor does it prove demand specifically for an HTML equivalent. Used only as supporting evidence, always alongside a built-in status check on the feature page.
4. **Built-in status** - determined only against the specific feature page on Microsoft Learn, as of the review date.

## The exact demand evidence

### Direct requests (reddit / Fabric Ideas)

- **Flat timeline with markers** - u/geophizx, r/PowerBI, 03/09/2022: "Would love to see a simple timeline that sits flat and has markers that stick up / down and then elevate with description. I've been pretty disappointed with the Gantt charts". https://www.reddit.com/r/PowerBI/comments/x46215/any_custom_visual_requests/
- **Roadmaps / milestones** - u/Nicodemus888, r/PowerBI, 23/11/2023: "Trying to visualise roadmaps, GANTT charts, milestones is execrable". https://www.reddit.com/r/PowerBI/comments/18280vs/missing_or_poorly_implemented_things/
- **Bullet and complex column charts** - u/FullllyPitted, r/PowerBI, 23/03/2026: "We use Deneb for visuals that PBI can't do. Detailed stacked bar charts, dual axis bar charts, bullet, etc." https://www.reddit.com/r/PowerBI/comments/1s1lf3m/how_often_do_you_find_that_outofthebox_viz_types/
- **Custom calendar** - u/Usual-Cat6451, r/PowerBI, 11/08/2023: "Can I use this to make a custom calendar?" (same thread x46215)
- **Org chart** - official Epic idea submitted by a Microsoft employee (Miguel_Myers), 07/10/2024; user comments: "I had requests from leadership to create our Org chart but I did not use Power BI to do it" (05/12/2024), "This would be amazing, especially when looking at workforce data" (28/01/2025). https://community.fabric.microsoft.com/t5/Fabric-Ideas/Epic-idea-Organization-chart/idi-p/4520633
- **Ishikawa** - u/iammarcmason, 02/09/2022: "If you can make a good ishikawa diagram it'll be the only one (that I've seen) out there" (thread x46215). A single request.

### Documented wishlist (Data Goblins, Kurt Buhler, 04/10/2022)

https://data-goblins.com/power-bi/visual-wishlist
- "This is essential for creating commonly-requested chart types like bullet charts, dumbbell plots" (section on markers/overlay on columns).
- "This unlocks additional visualization types, including lollipop charts, dumbbell plots and bullet charts. It would be trivially easy to create good visuals that compare actuals to target."
- On label positioning: "There is no way for me to fulfill this requirement today... we are forced to explore programmatic solutions with Deneb, R or Python."
- Wish for measure-driven labels: value + delta in the same label (8.4M ⬆0.3M ⬆4%).

### AppSource proxy (DataChant leaderboard, snapshot 24/07/2025)

https://github.com/DataChant/PowerBI-Visuals-AppSource - popularity score (not a raw download count), as of the snapshot date:
- Zebra BI Tables 0.998 (variance/IBCS tables, commercial), Apex Gantt 0.958, ChartExpo Sankey 0.988, Water Cup 0.986 (progress gauge), Multi Card KPIs 0.965, ZoomCharts Drill-Down Timeline 0.936, Counter Calendar 0.89 (certified).
- Careful reading: Zebra BI Tables being at the top means there is a market of paying customers for variance tables; it does not prove the built-in is lacking (that was checked separately), nor that HTML specifically is the answer.

## Built-in status (feature pages, checked 09/11/2026)

- **Gantt**: there is a **built-in Gantt visual in Power BI, in preview** - dedicated feature page: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-gantt - supports tasks, durations, progress, milestones (when End is empty), 3 category levels. This is a built-in Power BI visual, not a side Fabric feature. It is **not** the same thing as a lightweight milestone timeline: the Gantt is a heavy task scheduler, and the reddit requests talk about a light strip with markers.
- **Bullet / dumbbell / lollipop**: not built in; SQLBI shows that bullet charts are assembled manually from columns ("MacGyver"): https://www.sqlbi.com/articles/building-bullet-charts-in-power-bi-reports/
- **IBCS / variance tables**: not built in (the catalog + the tables page); Zebra BI fills the gap for a fee.
- **Waffle**: not built in.
- **Calendar heatmap**: built-in workaround - matrix + conditional formatting on cell background: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-conditional-formatting
- **Progress gauge**: workaround - built-in Gauge / hacked donut.
- **KPI card with sparkline**: the modern Card supports reference labels and images, without a sparkline: https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card ; sparkline in a table/matrix - built in (preview): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-sparklines-tables
- **Org chart**: not built in; official Epic idea open (above).

## The table: demand × built-in × feasibility × decision

| Component | Demand evidence | Built-in status | HTML Content feasibility | Decision |
| --- | --- | --- | --- | --- |
| Bullet chart | Deneb quote (2026) + wishlist "commonly-requested" | None | Full, Secure (static SVG) | **In the library** |
| Dumbbell | wishlist "commonly-requested" | None | Full, Secure | **In the library** |
| Lollipop | wishlist | None | Full, Secure | **In the library** |
| Variance/IBCS columns | Proxy: Zebra BI Tables 0.998 (paying customers) | None | Full, Secure | **In the library** |
| KPI trend (composite label + sparkline) | wishlist measure-driven labels + proxy Multi Card KPIs | Partial (Card without sparkline) | Full, Secure | **In the library** |
| Calendar heatmap | Direct request (2023) + proxy Counter Calendar 0.89 | Workaround (matrix+CF) | Full, Secure | **In the library** |
| Radial progress / waffle | Proxy: Water Cup 0.986 | Workaround (Gauge/donut) | Full, Secure | **In the library** |
| **Milestone timeline** (flat strip, markers up/down) | Two direct requests (2022, 2023) | Emerging workaround: the built-in Gantt in preview is a task scheduler, not a light strip | Full, Secure: dates → x coordinates in DAX, markers and labels above/below the axis, no JS | **In the library** (`milestone-timeline`) |
| **Org strip** (fixed hierarchy: root + direct reports) | Official Microsoft Epic (2024) + user comments | None | Full in the fixed format, Secure: cards and connectors are SVG with coordinates computed in DAX; automatic layout for dynamic depth does require JS (Regular) | **In the library** (`org-strip`, two levels, up to 6 direct reports, limitations labeled) |
| Sankey / flows | Proxy: ChartExpo 0.988 | None | Not implemented here: laying out flows over arbitrary data is a general layout problem; coordinates precomputed in DAX can cover fixed cases, and JS (Regular) the general one | **No** - beyond the library's scope for now |
| Ishikawa | Single request (2022) | None | Technically full, but niche | **No** - demand too weak |
| Histogram | reddit mention | Workaround (binning + columns) | Full | **No** - the built-in workaround is reasonable |

## Caveats from the research (anchored in the library)

- **Maintenance**: u/Tee_hops (24/03/2026): "We don't like to use too much that is not ootb so future folks can inherit it with ease." Conclusion: a few strong, documented components, not many primitives.
- **Licensing**: u/I_Pick_D (23/03/2026): "I can never justify either the expense or trouble involved in licensing something off the market place." Conclusion: a paste-in DAX library, with no licensing and no external dependency, answers exactly this.
- **Security**: all components work in the certified Secure edition (no JS, no external resources) - they pass organizational security review and are included in export.

## Working method for the agent (also anchored in AGENTS.md)

1. Demand first: evidence that people ask for the thing (ideas, reddit, community blogs; leaderboard only as a labeled proxy).
2. Verify the built-in: the specific feature page on Microsoft Learn, not the catalog list; classify as not built in / workaround / exists and HTML adds composition; date.
3. Feasibility: against HTML Content limitations (Secure: no JS; Regular: JS). Also check the static path (DAX → SVG coordinates / absolute positioning) before concluding "requires JS".
4. Decision documented in the table here.
