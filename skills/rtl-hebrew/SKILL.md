---
name: rtl-hebrew
description: Produce Hebrew RTL dashboards in HTML Content with correct bidi behavior for mixed Hebrew/English/numbers/currency/dates, RTL charts and right-docked menus. Load for any Hebrew content.
---

# Hebrew and RTL done right

`dir="rtl"` alone is not RTL support. The failure modes are all in the mixed runs: a number jumping to the wrong side of a sentence, "₪" detached from its amount, a date rendering inside-out, an English product name flipping punctuation. This skill is the checklist that prevents them.

## Base rules

1. Root container carries `dir="rtl"` and `lang="he"` **and inline `direction:rtl;text-align:right`**. Measured in Desktop (`reference/design-system.md` §1): the visual's default body styling injects `text-align:left`, so `dir` alone leaves titles and paragraphs left-aligned. Nested English-only blocks may carry `dir="ltr"`.
2. Text alignment: right. Numbers in tables: visual right-aligned in RTL is still `text-align: right` for Hebrew columns; numeric columns get `direction: ltr; unicode-bidi: isolate;` and stay readable.
3. Font stack: `'Segoe UI', 'Assistant', 'Rubik', sans-serif`. Web fonts via `@font-face` are blocked in Secure (and unreliable cross-origin in Regular); Segoe UI renders Hebrew cleanly on every Windows machine.
4. Power BI canvas coordinates are always LTR. RTL is content and layout intent, not a canvas flip. The side menu docks right because *you* place it at x = pageWidth - margin - menuWidth.

## Bidi isolation in DAX (the load-bearing technique)

Wrap every Latin, number, currency or date run in Unicode isolates inside the measure string:

- `LRI = UNICHAR(8294)` - Left-to-Right Isolate
- `PDI = UNICHAR(8297)` - Pop Directional Isolate
- `RLM = UNICHAR(8207)` - Right-to-Left Mark (for punctuation anchoring)

Pattern:

```dax
VAR LRI = UNICHAR ( 8294 )
VAR PDI = UNICHAR ( 8297 )
RETURN "<div>סך הכנסות: " & LRI & FORMAT ( [Revenue], "#,##0" ) & " ₪" & PDI & " | " &
       "דגם " & LRI & SELECTEDVALUE ( Product[Model] ) & PDI & "</div>"
```

Equivalent markup-level tool: `<bdi>...</bdi>` around the run, or a span with `unicode-bidi: isolate`. Use isolates when the value is generated inside DAX; use `<bdi>` when writing static markup.

## Currency, numbers, dates

- Currency: `FORMAT([Amount], "#,##0") & " ₪"` inside the isolate - digits first, then the sign (the CLDR he-IL convention, so the symbol stays glued to the amount and does not jump sides). Do not rely on bidi auto-placement of the symbol; anchor it inside the isolate.
- Percentages and deltas: keep the sign and digits in one isolate: `LRI & "+12.4%" & PDI`.
- Dates: decide one format per dashboard and keep it: `FORMAT([Date], "dd/MM/yyyy")` (DD/MM/YYYY with leading zero is the common Israeli convention; use the audience's locale, and uppercase `MM` so it is never read as minutes) inside an isolate. Hebrew month names from `FORMAT(..., "d MMMM", "he-IL")` are RTL-safe as words but the day/year digits still need the isolate around the whole run.
- Phone/ID/English model numbers: always isolated; they are pure LTR runs.

## RTL charts (SVG)

Charts in an RTL dashboard read from the right. For hand-built SVG:

- Bars anchor to the right edge: `x = width - barWidth` for a bar of `barWidth`.
- Text labels: `text-anchor="end"` at the right edge for values, `text-anchor="start"`... flip deliberately per element; test with mixed Hebrew/English labels.
- Time axes are the exception: keep them LTR (time flows left to right even in Hebrew BI convention) unless the user explicitly asks otherwise, and say which choice you made.
- `viewBox` arithmetic stays the same; only the x-mapping changes. `library/components/bar-chart-svg.dax` shows the pattern.

## Menus, headers, tables

- Side menu on the right; item text right-aligned; icons to the right of the label.
- Header: title block on the right, actions/date on the left.
- Tables: first column is the rightmost column; define `<table dir="rtl">` and let the browser order the cells; numbers get the ltr-isolate treatment per cell.
- Arrows and chevrons flip meaning: "forward" in RTL points left (`◀` / `‹`), breadcrumbs read right to left.

## Validation pass (always)

Render one screen containing: a Hebrew sentence with an embedded English product name, a currency amount, a negative percentage delta, a date, and a Hebrew-labeled bar chart. Check: nothing flipped, symbols attached, alignment consistent, menu on the right, chart reads correctly. Mark the pass in the delivery note; it has not been run in Power BI unless you actually ran it.
