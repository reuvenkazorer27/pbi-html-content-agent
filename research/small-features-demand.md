# Supplementary research: small features and everyday frustrations (pulled live 09/11/2026)

User request (10:18): "תבדוק עוד דברים אפילו אם זה פיצ׳רים קטנים.. מחקר עוד יותר מעמיק" (check more things even if they're small features.. even deeper research).
Method: locate frustration/request threads, pull the full content, extract concrete requests with quote, date and audience score (points), and check status: what the native status is (if verified against Microsoft documentation - noted; otherwise "per user reports, not verified in the docs"), and whether HTML Content solves it (Secure static / Regular JS / no).

## Sources (exact URLs pulled)
- S1: https://www.reddit.com/r/PowerBI/comments/1fzxi0c/whats_annoying_about_powerbi/ (thread 09/10/2024, 45 pts, 187 comments)
- S2: https://www.reddit.com/r/PowerBI/comments/1kl0dy0/what_frustrates_you_about_power_bi/ (12/05/2025, 135 pts, 151 comments)
- S3: https://www.reddit.com/r/PowerBI/comments/1k0moxt/what_is_a_brand_new_functionality_you_want_to_see/ (16/04/2025, 54 pts, 189 comments)
- S4: https://spilledgraphics.com/powerbi/011-my-power-bi-wishlist/ (blog, 6 detailed wishes with examples from the Economist/Washington Post)
- S5: https://community.fabric.microsoft.com/idea/fbc_ideas/enable-text-style-formatting-inside-dax-for-more-power/4884694 (Fabric Ideas, posted ~11 months before the review)

## A. Gaps the existing library already answers (with evidence)

| # | Request (quote, source, date, pts) | Native status | Library solution |
|---|---|---|---|
| 1 | "A MATRIX VISUAL THAT DOESN'T SUCK" (S3, anxiouscrimp, 16/04/2025, 105 pts); "The matrix visual SUCKS. It should have the same formatting options as a pivot table on excel" (S1, Accomplished-Fee6953, 10/10/2024); "The matrix visual" (S2, pvnptl123, 46 pts) | **Verified against the owning doc** (https://learn.microsoft.com/en-us/power-bi/visuals/desktop-matrix-visual, 09/11/2026): the matrix has improved significantly - per-column width in pixels, conditional width (fx), custom totals, freeze headers. The complaint about column widths (79 pts in 2024) **has been addressed natively**. What is still missing: full styling freedom at the individual cell level (arbitrary CSS) | `data-table` / `scorecard-table` - the remaining value: full CSS control, sparklines in cells, icons |
| 2 | "pie charts where it cuts off the words on the legend instead of wrapping them" (S1, Problemilyyy, 09/10/2024, 15 pts) | Per report | `donut-legend` - HTML legend with line wrapping |
| 2b | See #2: verified against the owning doc (https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-customize-title-background-and-legend, 09/11/2026): legend settings = on/off, title, position, color, font - **no text wrap for legend items**. The complaint stands |
| 3 | "the data labels in a chart cannot be moved like in Excel" (S2, Salt_Bug4223, 12/05/2025, 15 pts) | Per report | Freely positioned HTML labels in all components (see milestone-timeline: 6 non-overlapping labels in 360px) |
| 4 | "make a column header or certain cells bold - 2 clicks in excel but 3 hours of trial and error in PBI" (S2, Prestigious-Deer-103, 12/05/2025, 10 pts) | Per report | `data-table` - free CSS on every cell |
| 5 | "we cannot do conditional formatting on a series in a bar chart (happens weekly)" (S2, casperseve, 13/05/2025, 8 pts) | Per report | `condition-bar` / `progress-bar` - conditional color in DAX |
| 6 | "Cards are very limited" (S2, crasspy, 12/05/2025) | Per report | The whole KPI line + Kubai icons (new) |
| 7 | "Slicers can't be vertical... And those big bubbles on slicers are driving me mad" (S1, Cornokz, 09/10/2024, 4 pts) | Per report | `slicer-chips` (display only, does not control other slicers) |
| 8 | "Ability to specify Custom CSS for every element - for each table column separately, row/column headers, titles, subtitles" (S3, Ok-Boysenberry3950, 16/04/2025, 14 pts) | Open feature request | This is exactly the essence of HTML Content - CSS on every element |
| 9 | "conditional formatting affects the whole cell... you cannot highlight or emphasize separate parts of the text" (S5, Fabric Idea) | Official: open idea in Fabric Ideas. **Important:** the top comment on the page (Joe_Barry, ~11 months) states: "It is possible at the moment using HTML. You can use the HTML Content visual by Daniel Marsh-Patrick" | Pattern of styled spans within a single string - exists in the KPI components |

## B. Gaps the library does not yet answer - possible in HTML Content (Secure static)

| # | Request (quote, source, date, pts) | Native status | Proposed implementation |
|---|---|---|---|
| 10 | "Histograms." (S3, ThomasMarkov, 16/04/2025, 19 pts); "Lack of histograms+box and whisker plots in core visuals" (S1, GossipGirlX0X0, 09/10/2024, 5 pts) | **Verified against the official types catalog** (https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a, 09/11/2026): there is no histogram type (there are column/bar/ribbon/waterfall/funnel/Gantt-preview etc.). Native workaround: manual binning + column chart. HTML: bins in DAX + SVG columns with clean bin labels |
| 11 | "Native pareto chart." (S3, CaptCurmudgeon, 16/04/2025, 10 pts) | Per report | Sorted columns + cumulative % line, same pattern as bullet-with-trend |
| 12 | box plot (S1, same as above, 5 pts) | Per report | Five-number summary in DAX + static SVG drawing |
| 13 | "No easy way to do topN and 'others'" (S1, Dapperscavenger, 09/10/2024, 4 pts) | Per report | Not a component - a DAX template (GROUP BY + Others row). Could be added as a pattern page |
| 14 | "just ask for a full Font list rather than what microsoft decide i can have" (S3, Photog_72, 16/04/2025, 24 pts) | Partially verified (https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes, 09/11/2026): theme JSON gives control over fonts, but rendering is limited to the fonts available in Power BI - no arbitrary font upload. HTML Content: Secure = system fonts; Regular with web fonts: not verified - do not claim |

## C. Gaps HTML Content will not solve (important for setting expectations)

| # | Request (quote, source, date, pts) | Why not |
|---|---|---|
| 15 | "No write back option / commenting" (S1, gaius_julius_caegull, 09/10/2024, 14 pts) | HTML Content does not write to the model |
| 16 | "I want a button: export to excel" (S2, Lauren-Ipsum-128, 12/05/2025, 10 pts) | A visual cannot trigger an export |
| 17 | All 6 S4 wishes: cross-highlighting between small multiples, synchronized tooltips with a shared vertical line, brushing | Accuracy correction (verified against the official docs https://html-content.com/docs/interactivity, 09/11/2026): **click cross-filtering is supported** - via the Context data role, Power BI resolves the element to a data row and filters other visuals (works in Secure too, without script; there are also tooltips, drillthrough and context menu). What is not possible: live JS-level sync between two visuals (hover in one visual highlighting a point in another) - there is no such communication channel. In other words: shared click-to-filter = yes; live hover-sync = no |
| 18 | "Slicer Default values" / "A slicer that picks the latest date" (S3, chubs66 58 pts, konwiddak 7 pts) | HTML Content does not control the state of other slicers. **Partially native** (verified against https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers, 09/11/2026): a relative date slicer ("last full month") rolls forward automatically on every load - covers the "latest date" case for dates only; a default for non-date values is still open |
| 19 | "page level security" (S2, yyavuz, 122 pts; S3, attaboy000, 80 pts) | At the service level, not a visual |

## Proposed priority order (based on audience score + fit with the library)
1. Table/matrix (#1) - the strongest request in the sample; covered - make sure the examples highlight this.
2. Histogram (#10) - the next strongest request that is not covered; feasible.
3. Pareto (#11), box plot (#12) - feasible, medium score.
4. TopN+Others (#13) - cheap DAX pattern page.
5. Do not promise: writeback, export, cross-visual sync, slicer control (C).


## Substantive decision (09/11/2026, after verifying the docs)
**Adding: histogram** - the strongest uncovered request (19+5 pts across two threads), no native type (verified in the official catalog), feasible as static SVG in Secure, and real HTML value: readable bin labels, conditional color, exact boundaries - without the manual binning workaround.
On documented hold: pareto (10 pts), box plot (5 pts), TopN+Others (DAX pattern page).
Important correction to the message to the user: HTML Content does support click cross-filtering (Context role) - do not say "there is no interactivity between visuals" without this distinction.
