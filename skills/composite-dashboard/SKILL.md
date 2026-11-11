---
name: composite-dashboard
description: Build a dashboard from multiple HTML Content visuals tiled over a standard Power BI page background, mixed with native visuals. Use for team dashboards, multi-region layouts, or anything that must keep native slicers, native charts, export or mobile support.
---

# Composite dashboard (multi-visual)

## When to use

The default pattern for production team dashboards. Each region is its own visual with its own binding, native slicers stay native, and the page background does the framing. Required when the consumer needs export to PDF/PowerPoint or subscriptions (then all HTML Content visuals must be the Secure edition).

## Layout protocol

1. Read the report's page size (1280×720 or 1920×1080 by default). Never guess.
2. Apply the 8px grid convention from `reference/canvas-and-layout.md`: margin 24px, gutters 16px (×1.5 on 1080p).
3. Produce a coordinate table for every visual before writing any code: name, type, x, y, width, height, z. All multiples of 8.
4. RTL pages: side menu and primary reading flow start from the right. The menu column is the rightmost column.

A standard RTL composite at 1280×720:

| Region | x | y | w | h |
| --- | --- | --- | --- | --- |
| Header (HTML Content) | 24 | 24 | 1232 | 64 |
| Side menu (HTML Content) | 1056 | 104 | 200 | 592 |
| KPI cards x3 (HTML Content each) | 24 / 368 / 712 | 104 | 328 | 128 |
| Main chart (native or HTML) | 24 | 248 | 664 | 296 |
| Second chart | 704 | 248 | 336 | 296 |
| Table (HTML Content) | 24 | 560 | 1016 | 136 |

The arithmetic: menu docks right (1056 = 1280 - 24 - 200), so content width is 1016 (24..1040 with a 16 gutter before the menu). Three cards: 3x328 + 2x16 = 1016. 664 + 16 + 336 = 1016. Table y 560 = 248 + 296 + 16, and 560 + 136 = 696 = 720 - 24. Recompute with the same method for any other region count; this table is a starting point, not a rule. A fully documented RTL example lives in `examples/sales-dashboard-he/`.

## Making separate visuals look like one surface

- Page background or wallpaper carries the design (color or image). HTML Content containers: Effects → Background off, Border off, Shadow off unless intentionally added.
- Card look: paint `background` on the component's own root element from the active style's tokens (`styles.CARD`, `@@surface@@` / the role tokens - `reference/design-system.md` §4), with one consistent border-radius (8-12px) and padding across every component.
- Same font stack everywhere: `'Segoe UI', 'Assistant', sans-serif` (system fonts only; no @font-face, especially in Secure).
- Same internal spacing scale: 4/8/16/24.

## Data and binding

- The pipeline's host table (`pipeline.json` `"table"`) holds every HTML-producing measure, in the `HTML` display folder; the static `library/components/` files keep one component per file.
- Each HTML Content visual binds its own measure (Values) and its own Context column(s) when it must cross-filter.
- Cross-filter direction: HTML visuals filter native visuals and each other normally once *Cross-filtering → Enable* is on and a Context column exists. Native visuals (charts, slicers) filter HTML visuals automatically.

## Slicers and filters

- Native slicers: style them to sit inside the design (overlay on a painted HTML strip, matching colors). They are the only mechanism that stores real slicer state.
- HTML chip slicers: `library/components/slicer-chips.dax` (cross-filter selection, not a real slicer; no "select all", no search, no single-select enforcement). Tell the user which kind they are getting.

## Consistency checklist

- One style from `styles.py` (`skills/colorful-styles/SKILL.md`; default `accent`), colors only as tokens, never ad-hoc hex. `library/palettes.md` is the static library's doc-based palette list; where it differs, `reference/design-system.md` wins.
- Every region's verification label listed.
- Mobile: decide explicitly - build a mobile layout (323pt width floor, custom visual min 323×180pt) or declare desktop-only.
