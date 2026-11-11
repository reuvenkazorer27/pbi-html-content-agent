---
name: colorful-styles
description: Make an HTML Content dashboard colorful and still premium and consistent - fit a style to the user's brand, data and audience with tools/pbip-html-pipeline/styles.py, give every card a role, and gate contrast in every filter state. Use when the user asks for a colorful, branded, dark, warm, "more alive" or "less boring" dashboard, or when KPI cards and chart cards look like two different products.
---

# Colorful dashboards with styles

Status: gated, not yet confirmed in Desktop. On the kit's reference build against a live model (RTL Hebrew), all eight presets passed fit and contrast, and `accent`, `sand` and `tonal` passed all 7 filter scenarios. These runs were on the engine before its final refactor; after it, `accent` passed fit and contrast again. The full re-run on the final code is open: every preset, LTR English. `style_check.py` checks contrast over every preset and 800 generated styles without a model. A style you generate for a new model goes through the same gates; it counts as confirmed only after a Desktop screenshot.

## The rules (why colorful dashboards look cheap, and what fixes it)

From `reference/design-system.md` §4:

1. **One card material.** KPI cards and analysis cards share surface, border, radius, padding, title and icon chip. Five solid KPI tiles next to white chart cards reads as two products.
2. **One color mechanism per style:** a top or start accent bar, a tint, or the icon chip. Never mix them.
3. **Saturation on small areas only:** data marks, icons, the bar, and **at most one hero card**.
4. **Contrast is computed, not picked:** every in-card text color clears 4.5:1 on its card, and every data mark clears 3:1. `styles.py` does this for any color; you never hand-tune hex.
5. **The page is flat.** No gradient surfaces and no glow. Cards separate from the page by a step plus a 1px border.

## Workflow

1. **Ask, in one round, what decides the style:**
   - Brand colors (one or two hex values, or "none").
   - Light or dark.
   - Who reads the dashboard: executive, operations, or public.
   - Whether one number is the headline (that gives the hero card).

   If there are no answers, start from a preset.
2. **Pick or build the style.** Show 2-3 options as real previews before writing the PBIP: render each through the pipeline and send the screenshots.
   - Preset: `DASH_STYLE=accent | tonal | midnight | sand | ocean | duotone | sunset | mint`. `accent` is the default.
   - From the brand: `make_style(brand, accent=None, mode="light"|"dark", mechanism="bar"|"start-bar"|"tint"|"tint-strong"|"chip", hero=True, colors={...})`.
   - Make it the project default in `pipeline.json`: `"style": "accent"` or `"style": {"brand": "#0E7490", "mode": "dark", "mechanism": "tint", "hero": false}`.
   - Try one in a single build: `DASH_STYLE='{"brand": "#0E7490", "mode": "dark"}'`.
3. **Give every card a role from the user's data, not from its chart type.**
   - `neutral`: header and filter panel.
   - `hero`: the one headline KPI. It falls back to `brand` when the style has no hero.
   - `good` / `bad` / `warn`: semantic cards (overdue, risk, on target).
   - `c1`..`c6`: one per category the user cares about.

   A KPI and the chart about the same category get the same role, so they share a color. Keep it to about 6 hues.
4. **Wire it once in your measures:**
   - In `add()`: `expr = styles.apply(expr, ROLE.get(name, "neutral"))`.
   - Card roots: use `styles.CARD`. The builders in `components.py` already do this when a style is active.
   - Icon chips: `@@c_chip@@`, the glyph `@@c_icon@@`, glyph details `@@c_icon_in@@`.
   - Data colors stay tokens (`@@primary@@`, `@@cat1@@`, ...). A style maps c1..c6 to them, so data and cards share one set of colors.
5. **Gate every style you ship:**
   - `fitcheck.mjs` on the preview.
   - `stress.py`. Filter states shrink lists, and the fill rule must hold there too.
   - Both reading directions if you ship both.
   - After Apply external changes + Refresh, take a Desktop screenshot.

Dark + tint: `mode="dark"` with `mechanism="tint"` / `"tint-strong"` tints dark card surfaces in each role's hue (text pushed toward white), not light pastels on a dark page.

A preset with some inputs changed: `"style": {"preset": "accent", "hero": false}` (or `"page": "#..."` for a colored page) - no need to copy the preset's colors.

## Choosing a mechanism

| Reader / need | Mechanism | Presets |
| --- | --- | --- |
| Most dashboards: calm, clearly colorful, one headline | `bar` + hero | `accent`, `sand` |
| Several topics that should read as color zones | `tint` / `tint-strong` | `tonal`, `mint` |
| Wall screens, operations rooms, evening use | dark `bar` | `midnight`, `ocean` |
| Strong brand, little color noise | `chip` (one family + one attention color) | `duotone` |
| Warm brand, editorial feel | `start-bar` (mirrors with direction) | `sunset` |

## Do not

- Do not fill KPI cards with different solid colors. Use one hero at most.
- Do not use a gradient page or gradient title bands. Do not add glows or colored shadows.
- Do not use gray text on a tinted card. The style already gives text in the card's own hue.
- Do not hand-pick a text color. Use `styles.readable(color, [backgrounds], 4.5, toward)`.
- Do not judge a style on the unfiltered page only.

