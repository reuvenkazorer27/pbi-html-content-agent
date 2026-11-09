# Kubai Icons - icons for KPIs and side menus

Source: https://github.com/kubai087/kubai-icons (the icon collection: https://icons.kubai.design/)
Icon license: **MIT** (see LICENSE-MIT-kubai in this folder). Checked 09/11/2026.
Commercial use allowed, attribution not required (the copyright notice must be kept with the files - kept in LICENSE-MIT-kubai).

## What's here
12 static SVG icons (`kubai-icons-static` package, default palette #5393FF), selected for dashboard use:
banknote (revenue), hand-coins (profit), coins, users (customers/employees), chart-line (trend), chart-funnel (funnel), gauge (utilization), circle-alert (alerts), calendar, filter, target (targets), clipboard-check (tasks).

## Embedding in HTML Content
- The SVG is fully self-contained: no script, no external dependency, no fonts. Suitable in principle for the Secure edition too (inline SVG). **Not tested in actual Power BI** - declarative SVG filters (feDropShadow etc.) may be blocked/ignored in some editions; in that case the icon will look flat but correct.
- Embedding: paste the file contents inline into the component's HTML, and double the double quotes (`"` -> `""`) in DAX. Full example: `snippets/kpi-with-icon.dax`.
- Internal ids are namespaced by icon name (`-ki-<name>`) to prevent collisions between different icons on the same page. The same icon twice in the same visual = duplicate id; browsers render this correctly (the definitions are identical), but for full safety - add a unique suffix to the ids when embedding.
- Changing color: all shades are derived from #5393FF. You can download a different shade from the site (icons.kubai.design) or edit the `stop-color`/`stroke` in the file.
- RTL: the icons are mostly symmetric/neutral. Directional icons (arrows) were not included in this set; if you add them - consider horizontal mirroring in a Hebrew context.

## Size
The viewBox includes padding for the shadow: 24px in the file ≈ a "live" icon of ~20px. For a KPI card, width/height 20-28 is recommended.
