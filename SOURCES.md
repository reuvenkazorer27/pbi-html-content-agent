# Sources

Every factual claim in this folder traces to one of these sources, all accessed 9 Nov 2026. The folder's code and layout conventions were authored from these docs and were not executed in Power BI.

## HTML Content official documentation (html-content.com, Daniel Marsh-Patrick)

- Visual Editions (Regular vs Secure, min versions, edition choice): https://html-content.com/docs/visual-editions
- Interactivity (Context role, cross-filtering, tooltips, context menu, `data-hc-suppress`): https://html-content.com/docs/interactivity
- Limitations (sandbox, iframes, blocked features, CORS): https://html-content.com/docs/limitations
- Scripting, Regular edition (execution model, recommended pattern, gotchas): https://html-content.com/docs/scripting
- Sanitization (Secure): https://html-content.com/docs/sanitization
- Accepted Tags (Secure): https://html-content.com/docs/accepted-tags
- Data Roles (Values / Context / Tooltips; Context renamed from Granularity in 2.0): https://html-content.com/docs/data-roles
- Templates (Body/Row, `{{content}}` / `{{row}}`, render order, blank-row drop): https://html-content.com/docs/properties-templates
- Stylesheet property (DOM overview: `#htmlContent`, `.htmlViewerEntry`; overrides simple formatting): https://html-content.com/docs/properties-stylesheet
- Content Formatting (renderer, Show raw HTML caps, Allow opening URLs, No Data message, body styling, override inline styles): https://html-content.com/docs/properties-content-formatting
- Theme Colors (`--pbi-theme-*` variables, high contrast): https://html-content.com/docs/theme-colors
- Diagnostics (Raw HTML / Sanitizer / Console / Events tabs): https://html-content.com/docs/diagnostics
- FAQ (free/MIT, certification, JavaScript in content): https://html-content.com/docs/faq
- PBIR Implementation Guide (visualType GUIDs, `queryState.content` projections, `objects.templates`, literal escaping rules): https://html-content.com/docs/pbir-guide
- Simple Worked Example (templates walkthrough): https://html-content.com/docs/simple-example
- 2.0 release notes (29 Sep 2026; lite renamed Secure; templates, diagnostics, theme colors, render modes, suppression): https://html-content.com/blog/v2-release
- Enterprise and Security FAQ (declared privileges per edition, certification detail): https://html-content.com/enterprise
- Source (MIT): https://github.com/dm-p/powerbi-visuals-html-content
- AppSource listing (Secure/certified, formerly "HTML Content (lite)"): https://marketplace.microsoft.com/en-us/product/power-bi-visuals/coacervolimited1596856650797.htmlcontent_certified

## Microsoft Learn

- Canvas settings and page size presets (16:9 with 1280×720 / 1920×1080 / QHD / 4K; 4:3; Letter; Tooltip; Custom; theme-set defaults): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-report-display-settings
- Report page tooltips (Tooltip page size 320×240; design at Actual Size): https://learn.microsoft.com/en-us/power-bi/guidance/report-page-tooltips
- Mobile layout view (interactive canvas, auto-create, slicer-state behavior): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-create-mobile-optimized-report-mobile-layout-view
- Mobile best practices (323pt max width; minimum visual sizes incl. custom visual = L 323×180pt): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-create-mobile-optimized-report-best-practices
- Mobile formatting (size/position disconnected from desktop layout): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-create-mobile-optimized-report-format-visuals
- Mobile app interaction settings (multi-select not supported for custom visuals): https://learn.microsoft.com/en-us/power-bi/explore-reports/mobile/mobile-app-interaction-settings
- Certified visuals (certification benefits: export to PowerPoint, subscription emails; requirements): https://learn.microsoft.com/en-us/power-bi/developer/visuals/power-bi-custom-visuals-certified
- Tenant policy for certified-only visuals and organizational store: https://learn.microsoft.com/en-us/fabric/admin/organizational-visuals


## Differentiation benchmarks (checked 9 Nov 2026)

Basis for the library's native-comparison claims in README.md and in each component header. Rule: claims are verified against the feature-owning page, not inferred from the overview catalog.

- Built-in visuals catalog (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualizations-overview - the overview list: bar/column, line, area, combo, ribbon, waterfall, pie/donut, treemap, funnel, scatter/bubble/dot plot, Gantt (preview), tables/matrix, maps, card/KPI/gauge/goals, AI visuals, slicers, text/buttons/navigators.
- Sparklines in a table or matrix (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-sparklines-tables - NATIVE (marked in preview on the page): add a sparkline column to any table/matrix; formatting limited to line and marker options. Grounds the scorecard-table "native exists, HTML composes richer" classification.
- Card visual (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card - the modern card supports callout values, reference labels, images and multi-card layouts; no embedded sparkline. Grounds the kpi-trend classification.
- Smart narrative (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-smart-narrative - NATIVE: custom mode writes narrative text with dynamic values tied to fields/measures, basic text formatting only; no inline charts. Grounds the insight-narrative classification.
- Data alerts (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/create-reports/service-set-data-alerts - NATIVE notifications on dashboard tiles (gauges, KPIs, cards) in the service, plus Fabric Activator alerts on report visuals (preview); notifications, not in-canvas visuals. Grounds the alert-banner classification.
- Conditional formatting in visuals (Microsoft Learn): https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-conditional-formatting - background color rules on matrix cells are the native calendar-heatmap workaround. Grounds the calendar-heatmap classification.
- SQLBI, "Building bullet charts in Power BI reports": https://www.sqlbi.com/articles/building-bullet-charts-in-power-bi-reports/ - bullet charts must be hand-assembled ("MacGyvered") from core bar charts; no native bullet.
- AppSource listings (commercial/community fills for the same gaps): Bullet Chart by OKVIZ (wa104380953), Bullet Chart by xViz (WA200000933), Dumbbell Chart by MAQ Software, Waffle Chart, calendar heatmaps (OKVIZ ProCalendar Heatmap, Zentrix Calendar Heatmap).

## User demand evidence (checked 9 Nov 2026)

Basis for the build/skip decisions in `research/user-demand.md`. Rule: a component enters the library because people demonstrably ask for it, not because the catalog lacks it. Direct user requests are the strongest evidence; the AppSource leaderboard is a labeled proxy only (popularity of third-party visuals, not proof of unmet native capability).

- r/PowerBI, "Any custom visual requests?" (2 Sep 2022): u/geophizx (3 Sep 2022) - "a simple timeline that sits flat and has markers that stick up / down... I've been pretty disappointed with the Gantt charts"; u/Usual-Cat6451 (11 Aug 2023) - "Can I use this to make a custom calendar?"; u/iammarcmason - ishikawa. https://www.reddit.com/r/PowerBI/comments/x46215/any_custom_visual_requests/
- r/PowerBI, "Missing or poorly implemented things?" (23 Nov 2023): u/Nicodemus888 - "Trying to visualise roadmaps, GANTT charts, milestones is execrable". https://www.reddit.com/r/PowerBI/comments/18280vs/missing_or_poorly_implemented_things/
- r/PowerBI, "How often do you find that out-of-the-box viz types are insufficient?" (23 Mar 2026): u/FullllyPitted - "We use Deneb for visuals that PBI can't do. Detailed stacked bar charts, dual axis bar charts, bullet, etc."; u/Tee_hops - maintainability ("not ootb so future folks can inherit it with ease"); u/I_Pick_D - marketplace licensing aversion. https://www.reddit.com/r/PowerBI/comments/1s1lf3m/how_often_do_you_find_that_outofthebox_viz_types/
- Microsoft Fabric Ideas, "Epic idea: Organization chart" (submitted by Microsoft employee Miguel_Myers, 7 Oct 2024): user comments Dec 2024 - Feb 2025 asking for a native org chart ("requests from leadership to create our Org chart"). https://community.fabric.microsoft.com/t5/Fabric-Ideas/Epic-idea-Organization-chart/idi-p/4520633
- Data Goblins, "Power BI Data Visualization - Ideas & Wishlist" (Kurt Buhler, 4 Oct 2022): markers/overlay on bars are "essential for creating commonly-requested chart types like bullet charts, dumbbell plots" and "unlocks... lollipop charts, dumbbell plots and bullet charts"; data-label placement "forced to explore programmatic solutions with Deneb, R or Python"; measure-driven data labels (8.4M with inline delta). https://data-goblins.com/power-bi/visual-wishlist
- DataChant Power BI AppSource leaderboard (snapshot 24 Jul 2025) - PROXY ONLY: Zebra BI Tables 0.998, Sankey (ChartExpo) 0.988, Water Cup 0.986, Multi Card KPIs 0.965, Apex Gantt 0.958, ZoomCharts Drill-Down Timeline 0.936, Counter Calendar 0.89. Popularity of third-party visuals; says nothing by itself about native capability. https://github.com/DataChant/PowerBI-Visuals-AppSource
- Native status check, Gantt (Microsoft Learn, feature-owning page, fetched 9 Nov 2026): the Gantt visual IS a native Power BI visual, in preview - tasks, durations, progress, milestones (blank End), 3 category levels. https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-gantt

## Third-party (flagged; conventions, not Microsoft specs)

- VizForge, "Power BI Page Size & Canvas Presets in Pixels" (4 Nov 2026): pixel values for 4:3 (960×720) and Letter (816×1056), the note that new Fluent 2 reports default to 1920×1080, and the 24px-margin/16px-gutter pixel-math convention used in `reference/canvas-and-layout.md`: https://vizforge.ai/blog/power-bi-page-size-canvas
