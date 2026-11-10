# Design system - rules that make HTML Content cards fit, read and scale

Every rule here was measured in Power BI Desktop (Secure edition, 1920×1080 pages), not only read in documentation. Rules marked **must** are gates: the pipeline (`tools/pbip-html-pipeline/`) checks them before anything is written to a report. When a rule here conflicts with a component in `library/` or an older note in `reference/`, this page wins.

Everything on the page is HTML Content except the slicers (AGENTS.md, "What this agent is built on"). No tool or agent label on the dashboard.

## 1. The card frame

| Rule | Why | Verify |
| --- | --- | --- |
| **Must:** container padding 0 on every HTML Content visual (and every native slicer placed on an HTML panel), with background, border, title, drop shadow and visual header off - see `pbir-visual-json.md` | Current base themes (e.g. Fluent 2) pad every visual `16/14/16/16`. The HTML viewport is the frame minus that padding - 30px shorter and 32px narrower than `position` - so every card clips and titles wrap. Do not compensate with extra line height; remove the padding. | Read the base theme's `visualStyles["*"]["*"].padding`; after applying, the card's painted edge coincides with the selection frame. |
| **Must:** card root `height:100vh; box-sizing:border-box; overflow:hidden; line-height:1.35` | The visual's iframe is the frame; an explicit line height removes the browser/Desktop difference in text height. | Fit check. |
| **Must:** card root carries the reading direction inline: `direction` + `text-align` (start side) and `dir`/`lang` attributes | The visual injects a default body alignment (`text-align:left`); `dir="rtl"` alone leaves titles left-aligned. | Desktop screenshot: every title on the start side. |
| Fixed-height children of a flex column get `flex:none` | Otherwise they shrink to 0 when content is tight (bars and slicer slots disappear). | Fit check / screenshot. |
| Titles, subtitles, legends and chip rows are single-line (`white-space:nowrap`, ellipsis or clipping) | Translated or filtered text is longer; one wrapped line pushes everything below out of the frame. | Stress scenarios. |

## 2. Fit budget

- Rows are fixed-height; the number of rows comes from the frame, not from the data: `rows = floor((H - padding - header - footer - 8) / rowPitch)`.
- **Must:** every card keeps 8px of slack at the bottom and sides. The pipeline's exact-size fit check renders each measure in an iframe of the visual's exact size and fails on any element past `edge - 8px` or a root taller than the frame. A full-page screenshot is not enough: cards that look fine overflow by 2-30px.
- **Must: no card with a large empty area.** Content fills the card: below the lowest text, bar or box, at most max(40px, 15% of the card height) may stay blank. A card that is half empty looks broken. Fix it in this order: (1) let the content stretch - rows `flex:1 1 0` with a min and max height instead of a fixed height, charts sized in % of a `flex:1` area, an svg at `height:100%` with `aspect-ratio`; (2) show more of the data (more rows, a second view); (3) make the card smaller and give the space to a neighbour. A tall panel (e.g. a filter column) gets useful content under its controls - such as what the current selection is made of. A short last row in a grid of panels widens to fill the row (`flex-wrap` with `flex:1 1 calc(100%/cols - gap)`). The fit check enforces the bottom band; the deliberate exceptions are marked `data-fill='free'` (the background layer, an empty-state message).
- Gate every combination you ship (direction × language × palette), and every filter state (see §6).

## 3. Type scale

Fit to page shows a 1920×1080 canvas at roughly 0.70-0.75 on a laptop, so 12px renders like 9px. Minimums on 1920×1080 (divide by 1.25 on 1280×720):

| Element | Size |
| --- | --- |
| Header title | 26-28px |
| KPI value | 48-50px |
| Big numbers (stages, donut center) | 26-36px |
| Card title | 20px |
| Body, list labels | 15px |
| Secondary text | 14px |
| Captions (never smaller) | 13px |

Author measures with a base scale and remap sizes in one place (`FONT_SCALE` in the pipeline) - never hand-edit sizes per card.

## 4. Color and contrast

- **Must:** colors only as palette tokens - no hex literals inside measures. A palette defines every token; the page background, slicer colors and preview follow it. Palettes in the pipeline: `ocean` (light), `midnight` (dark), `berry` and `vivid` (colorful).
- **Must:** WCAG contrast on every text element: 4.5:1 for body text, 3:1 for large text (≥24px, or ≥18.7px bold). The pipeline checks the rendered page, not the palette table.
- A fill color is not a text color. Each status needs a fill token (bars, borders, dots) and a darker `*_text` token for text on its soft background (a typical teal on its pale fill measured 2.73:1). Dark palettes need lighter `*_text` variants.
- A fill that carries white text needs its own token (`strong`): a palette's primary can be too light for white text (a dark palette's light blue measured 2.68:1). Use `*_soft` + `*_text` pairs for tiles and pills, and `strong` + `on_accent` for filled highlights.
- Brand palettes: derive every token from one or two brand colors and push each text color toward black (light) or white (dark) until it passes 4.5:1 on its background - never accept a brand color as a text color unchecked.
- **Categorical colors** (`cat1`..`cat6`, each with `catN_soft` and a text-safe `catN_text`): use them when color encodes *which category*, not *how good*. A category keeps its color everywhere - assign by the value's rank over the whole column (`ALL(column)`), never by its position in the current top N, or a filter recolors it. Status colors (`done`, `bad`, ...) stay for status meaning only.
- Six hues are the limit a reader can tell apart; beyond six, colors repeat - put the label on the mark, not only in a legend.
- Native slicers default to a white dropdown: set `items.fontColor` / `items.background` from the palette, or a dark page gets white boxes.

### Colorful dashboards

- **Gradient page without an image:** one full-page HTML Content visual (0,0,page width,page height), first in the layout so it gets the lowest z, padding 0, chrome off, content `<div style='height:100vh;background:linear-gradient(135deg,from,mid 55%,to)'>`. Works in the Secure edition. Keep cards on a light `surface` so text stays readable.
- **Filled KPI cards:** `background:linear-gradient(160deg,rgba(0,0,0,0),rgba(0,0,0,.24)),<accent>` - the overlay only darkens, so white-text contrast only improves; swap icon roles (white glyph, accent details); progress track `rgba(255,255,255,.30)` with a white fill. White text needs deep accents (blue `#1D4ED8`, violet `#7C3AED`, teal `#0F766E`, green `#15803D`, red `#C81E1E`; `#DC2626` fails as text on a pale inset).
- Switch looks with palette flags (`kpi_filled`, `bg_layer`) that exist in every palette, so a light build stays byte-identical while a colorful one is added.

## 5. Lists, slicers and interactivity

- **Lists that do not fit:** show the top N rows; the overflow line ("and N more") carries a manual tooltip that lists the hidden items: `class='tooltipEnabled'` + `data-tooltip-title-NN` / `data-tooltip-value-NN` (one pair per item, NN zero-padded). Works in Secure. *Click to expand* is not possible in Secure - it needs the Regular edition with script, or a native drillthrough page.
- **Tables in HTML:** a header row on a tinted band, fixed 30px rows, zebra striping, numbers end-aligned with tabular figures (`font-variant-numeric:tabular-nums`) and isolated (`direction:ltr;unicode-bidi:isolate`), text clipped with an ellipsis (never wrapped), an optional totals row with a heavier top rule, and an "and N more" line with the hover list. Rows come from the fit budget, not the data.
- **Must: column headers line up with their columns.** Header, rows and totals use the same grid template, and every flexible track is `minmax(0, Nfr)` with `min-width:0` cells: each row is its own grid, and a plain `1fr` (= `minmax(auto,1fr)`) lets one wide value widen its column in that row only. Never put a value in a fixed box narrower than the formatted value (a 44px box let `$284,605` stick out past its header). Check in the screenshot that each header's end edge meets its values' end edge, in LTR and RTL.
- **Must: every KPI card has an icon** (`kpi_card` rejects one without): title and icon chip on one line, one big number, one caption line.
- **A dominant blank category** ("no department" at 35%) is not a bar - drop it from the list and state it in a note line; otherwise it compresses every real bar.
- **Short categorical lists** (≤12 items) fit in two columns (`display:grid; grid-auto-flow:column; grid-template-rows:repeat(n,28px)`) instead of being truncated.
- **Native slicers on an HTML panel:** draw only the label in HTML (no box - it doubles the border); the slicer (padding 0, header off, background off, dropdown mode) supplies its own box. Position: `y = panelTop + titleBlock + i × slotPitch + labelHeight`, from the same constants the HTML uses.

## 5b. Text built from numbers

- **Must:** every number concatenated into text goes through `+ 0` or `IF ( ISBLANK ( ... ), ... )`. A BLANK measure under a filter turns `x & " vs " & y` into `" vs ·"` and `"2 of 3"` into `" of 3"` - the stress scenarios (one value, empty selection) are where it shows.

## 6. Direction and language

- **Direction is a build setting, not a rewrite.** Components never hardcode `rtl`/`ltr`/`left`/`right`: card roots use direction tokens, numeric cells align to the end side, "next" arrows flip, and the layout is mirrored for LTR (`x' = page width - x - w`). Time axes stay left-to-right in both directions (say so in the subtitle).
- **RTL text:** isolate every number, currency, date and Latin run (LRI/PDI in DAX strings, `<bdi>` in static markup) - see `skills/rtl-hebrew/SKILL.md`.
- **UI language:** some words are both labels and data values (a status shown in a pill is also a filter literal). Never translate data literals or model names: translate display strings only, give data values an explicit display-name map, and fail the build if any source-language text is left. Translated text is usually longer - the fit gate will catch it; shorten the wording, keep the layout.
- **Stress every language and direction** with slicer-like filters (one column at a time), an empty selection, and one scenario that marks every column filtered (the worst case for header filter chips).
