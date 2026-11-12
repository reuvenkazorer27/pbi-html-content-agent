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
- **Must: no card with a large empty area.** Content fills the card: below the lowest text, bar or box, at most max(40px, 15% of the card height) may stay blank. A card that is half empty looks broken. Fix it in this order: (1) let the content stretch - rows `flex:1 1 0` with a min and max height instead of a fixed height, charts sized in % of a `flex:1` area, an svg at `height:100%` with `aspect-ratio`; (2) show more of the data (more rows, a second view); (3) make the card smaller and give the space to a neighbour. A tall panel (e.g. a filter column) gets useful content under its controls - such as what the current selection is made of. Filter states shrink lists: one-column list rows stretch (`flex:1 1 0`, min 28px, max 40px), a two-column grid gets as many rows as items, and when a list is short (≤4 rows; ≤8 items in two columns; ≤4 dated rows) a status-mix block of the current selection sits at the bottom of the card (`margin-top:auto`) - real data, not filler. The builders do this by default: `lift_bars`, `heat_matrix` and `data_table` rows stretch (`stretch=False` gives the old fixed rows), one treemap tile takes the whole area, and `fill=components.mix(table, col, measure, title)` adds the status-mix block when the list is short (`short_when=`, counted from the builder's own rows). Gate it with `stress.py`, not only the unfiltered page. A short last row in a grid of panels widens to fill the row (`flex-wrap` with `flex:1 1 calc(100%/cols - gap)`). The fit check enforces the bottom band **and voids inside the card** (the biggest gap between painted boxes must stay under max(60px, 15% of the card height) - one tile at the top and a block at the bottom with nothing between them fails). The deliberate exceptions are marked `data-fill='free'` (the background layer, an empty-state message); room reserved for a native visual on top of the card (a slicer under its HTML label) is marked `data-fill='slot'`.
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

- **Must:** colors only as palette tokens - no hex literals inside measures. A palette defines every token; the page background, slicer colors and preview follow it. Colors come from the active style (`styles.py`, default `accent`, see §4) or, with `DASH_PALETTE`, from the legacy palettes in `palette.py`.
- **Must:** WCAG contrast on every text element: 4.5:1 for body text, 3:1 for large text (≥24px, or ≥18.7px bold). The pipeline checks the rendered page, not the palette table.
- A fill color is not a text color. Each status needs a fill token (bars, borders, dots) and a darker `*_text` token for text on its soft background (a typical teal on its pale fill measured 2.73:1). Dark palettes need lighter `*_text` variants.
- A fill that carries white text needs its own token (`strong`): a palette's primary can be too light for white text (a dark palette's light blue measured 2.68:1). Use `*_soft` + `*_text` pairs for tiles and pills, and `strong` + `on_accent` for filled highlights.
- Brand palettes: derive every token from one or two brand colors and push each text color toward black (light) or white (dark) until it passes 4.5:1 on its background - never accept a brand color as a text color unchecked.
- **Categorical colors** (`cat1`..`cat6`, each with `catN_soft` and a text-safe `catN_text`): use them when color encodes *which category*, not *how good*. A category keeps its color everywhere - assign by the value's rank over the whole column (`ALL(column)`), never by its position in the current top N, or a filter recolors it. Status colors (`done`, `bad`, ...) stay for status meaning only.
- Six hues are the limit a reader can tell apart; beyond six, colors repeat - put the label on the mark, not only in a legend.
- Native slicers default to a white dropdown: set `items.fontColor` / `items.background` from the palette, or a dark page gets white boxes.

### Colorful dashboards - one card material, one color mechanism

Measured on the reference build (1920x1080, RTL Hebrew and LTR English, live model, all filter states). Two earlier colorful attempts were rejected by the owner as cheap: (a) a saturated gradient page with five KPI cards in five solid colors next to white chart cards, and (b) chart cards tinted from the page with a gradient title band while the KPIs stayed solid. Both mixed two card families and spread saturation over large surfaces. What works, consistent with Radix Colors, Tremor, shadcn/ui, Carbon and Refactoring UI:

- **Must: KPI cards and analysis cards are one material** - same surface, border, radius, padding, title style and icon chip. Color reaches every card through **one repeated mechanism** per style (a tint, a top/start accent bar, or the icon chip), never a mix.
- **Saturation goes on small areas:** data marks, icons, the accent bar, and **at most one hero card** (a solid fill with white text). Five solid KPI fills side by side is the "Christmas tree" failure.
- **Tinted cards use a scale, not one color** (Radix steps): card background step 2-3, chip/track step 5, border step 6, solid marks step 9, secondary text step 11, primary text step 12 - all of the **card's own hue**. Gray text on a tinted card looks washed out.
- **Page:** flat; gradients on surfaces and colored glows are out. Separate cards from the page by a step and a 1px border, not a heavy shadow.
- **Data colors** keep their meaning (status = status), are pushed to 3:1 against the card they sit on, and text colors to 4.5:1 - computed per style, not hand-picked.
- **Few hues:** each card gets a role (`neutral`, `brand`, the status hues for the KPIs, `c1`..`c6` for analysis cards); a style maps roles to hues. Up to ~6 hues on a page; a duotone style uses one family plus one attention color.

The pipeline ships this as a tool, not a theme: `tools/pbip-html-pipeline/styles.py` builds a style from design inputs (`make_style(brand, accent, mode, mechanism, hero, ...)`), gives every card its tokens from a **role** (`neutral`, `hero`, `brand`, `good`/`bad`/`warn`, `c1`..`c6`), and computes every in-card color for contrast - verified over 800 generated styles (40 brand colors × light/dark × 5 mechanisms × hero on/off). Workflow and role mapping: `skills/colorful-styles/SKILL.md`. Default: `accent`; the project default goes in `pipeline.json` (`"style"`: a preset name or a `make_style()` dict). The presets below are worked examples of the inputs:

| Style | Page | Card | Color mechanism | Hero |
| --- | --- | --- | --- | --- |
| `accent` (default) | light gray | white, 1px border | 4px top bar in the card's hue + tinted chip | yes (total) |
| `tonal` | light gray | tinted in its own hue (step 3), border step 6 | the tint; text in the card's hue | no |
| `midnight` | near-black | dark gray | 3px top bar, luminous data | no |
| `sand` | linen | warm off-white | 3px top bar, earthy hues | yes (rust) |
| `ocean` | deep navy | navy | 3px top bar, aqua / sky / coral | no |
| `duotone` | light lavender-gray | white | indigo chip only; amber = attention | yes (indigo) |
| `sunset` | warm cream | white | 6px start-side bar (mirrors with direction), warm hues | no |
| `mint` | pale green-gray | strong tint, no border, radius 18 | the tint | no |

### The organization's logo

Measured in Desktop (Secure edition, 12 Nov 2026): an inline `<svg>` and an `<img>` with a base64 PNG both render in the header of an HTML Content card. `tools/pbip-html-pipeline/logo.py` builds the fragment and enforces these rules:

- **Never recolor a logo.** Its colors feed the style (brand + accent), not the other way round. When its main color is under 3:1 on the surface it sits on, and a white plate fixes that, it sits on a white plate.
- **SVG inline first; PNG only small.** The SVG is sanitized (no script, `foreignObject`, `on*=` or external `href`) and needs a `viewBox`; a PNG is resized to 2x its display height and palette-quantized. **Must:** the fragment stays at most 12 KB - every card that shows the logo carries it in its measure.
- **One place: the start of the header** (or the top of a side rail), 40px high in an 80px header at 1920×1080. It mirrors with the reading direction like any flex item. In a flex column give it `align="flex-start"`: a stretched `<svg>` centers its drawing.
- **Extracted colors are a proposal.** A flat logo gives its colors exactly; official brand hex values win.

Legacy palettes (`DASH_PALETTE=ocean|midnight|berry|vivid|...`) still build; an explicit `DASH_PALETTE` selects them. Every `components.py` builder takes the style's card material when a style is active. Both examples use roles.

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
- **Mixed Hebrew + Latin labels truncate badly** with `text-overflow:ellipsis` in RTL: `כונן SSD חיצוני` rendered as "כונן D…" in a narrow treemap tile (measured 10 Nov 2026, preview and Desktop). Give such labels room (fewer tiles, a wider card) or a shorter display name; the gates do not catch it.
- **Native slicers keep Power BI's own UI language:** on a Hebrew page an English Desktop shows "All" in the dropdown. The kit draws the labels, not the slicer's text; say so in the deliverable.
- **UI language:** some words are both labels and data values (a status shown in a pill is also a filter literal). Never translate data literals or model names: translate display strings only, give data values an explicit display-name map, and fail the build if any source-language text is left. Translated text is usually longer - the fit gate will catch it; shorten the wording, keep the layout.
- **Stress every language and direction** with slicer-like filters (one column at a time), an empty selection, and one scenario that marks every column filtered (the worst case for header filter chips).

## 7. Motion (measured 10 Nov 2026)

Only when the user asks for motion: load `skills/motion/SKILL.md` - it holds the rules (CSS `@keyframes` inline, what earns motion, alerts that stop within 5 s, the `prefers-reduced-motion` trap in Desktop, `fit-clip`, static exports). Every builder takes `motion=` / `alert=`; off is byte-identical.
