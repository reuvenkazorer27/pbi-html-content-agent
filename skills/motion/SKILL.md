---
name: motion
description: Add motion to HTML Content visuals where it carries meaning - the change from the previous value (KPI digits roll from last period, table bars move from their previous value), a brief alert pulse on items that break a threshold, data freshness (updated / stale), and an entrance on every render. CSS keyframes only, so it runs in the Secure edition. Use when the user asks for motion, animation, "alive" or "live" visuals, counting numbers, attention on exceptions, or freshness of a dashboard.
---

# Motion in HTML Content visuals

Motion in this kit is **CSS `@keyframes` in an inline `<style>` inside the measure**. No script, no GSAP, no external file: the Secure edition strips `<script>`, and the CSS route also works in the Regular edition, in Desktop and in the Service. Measured in Power BI Desktop (Secure edition, 10 Nov 2026) - see "Verified".

## What motion is for (research, checked 10 Nov 2026)

| Use | Why it earns motion | In this kit |
| --- | --- | --- |
| **Show the change** | Static updates get missed (change blindness); animating from the old value to the new one shows how the data moved - the main reason to animate a chart | `kpi_card(prev=...)`: digits roll from last period's value; `data_table` bar `"prev"`: the bar moves from its previous value |
| **Draw attention to an exception** | Alerts are "essential motion"; keep them brief, one kind at a time, stop after a few cycles | `alert="<DAX condition>"` on every builder: a red ring pulses twice (4.8 s) on items that break it, then stops |
| **Say how fresh the data is** | A visible "data as of" and a stale flag past a budget; a "live" label on data that is not live misleads | `kpi_card(updated=..., stale_after=60)`: "Updated N min ago" / amber "Stale · 3 h ago"; a fresh dot pulses twice |
| **Show flow and its direction** | Moving dashes along a connector, speed tied to volume (process / network flow panels) | not built yet - needs flow data (source -> target -> volume) |
| **Keep orientation on a view change** | Elements that move rather than jump keep the reader's place | entrance on every render (page open, filter change, Refresh) |

What does **not** earn motion, and is left out on purpose:

- **Decoration:** sheens, "breathing" elements, grow-in for its own sake, motion on a chart that never changes.
- **Bounce or overshoot on data:** it misstates the values while it plays - bars grow from the axis with ease-out (pops keep a small overshoot on badges and chips only, which are not data).
- **Endless loops:** WCAG 2.2.2 (level A) requires a pause control for moving content that starts by itself and lasts more than 5 seconds. HTML Content has no script for a control, so every loop in this kit stops within 5 seconds and plays again on the next render.
- **Many things moving at once:** one attention animation at a time - alert only what breaks a threshold, never "the largest" or every row.

Sources: [Geckoboard - To animate or not to animate](https://www.geckoboard.com/blog/to-animate-or-not-to-animate/) · [NN/g - The role of animation and motion in UX](https://www.nngroup.com/articles/animation-purpose-ux/) · [W3C - Understanding SC 2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) · [Colorado Digital Service - Motion & Interaction (essential vs non-essential)](https://dcs.colorado.gov/ids/digital-guidelines/design-tokens/motion-interaction) · [Carbon - Motion](https://v9.carbondesignsystem.com/guidelines/motion) · [Data Trust Engineering - Data freshness pattern](https://github.gg22.workers.dev/datatrustengineering/DataTrustEngineering/blob/main/docs/patterns/data-freshness/data-freshness.md) · [Grafana Flow panel](https://grafana.com/grafana/plugins/andrewbmchugh-flow-panel/). Most dashboard-specific guidance is vendor and practitioner advice, not research studies - treat the numbers as conventions.

## Every builder: `motion=` and `alert=`

All nine builders in `tools/pbip-html-pipeline/components.py` take `motion=False | True | k` and `alert=None | "<DAX condition>"`. `motion=False` (default) leaves the output byte-identical, so existing dashboards do not change. `k > 1` slows every animation k times - only to check frames in Desktop.

| Builder | Entrance (`motion=True`) | `alert=` evaluates in this row context |
| --- | --- | --- |
| `kpi_card` | digits roll to the value - from `prev=` when given; the icon chip pops last | `_v` (the value) - the chip pulses |
| `waterfall` | bars grow from their base one after another | `_v` (the step) |
| `heat_matrix` | cells pop row by row | `_v` (the cell value) |
| `lift_bars` | bars grow from the start side (right in RTL) | `_l` (the lift) |
| `small_multiples` | mini columns grow, panel by panel | `[@v]` (the month's value) |
| `scatter` | bubbles pop, labels slide in | `[@x]`, `[@y]`, `[@s]` |
| `treemap_rows` | tiles pop, tile by tile | `[@v]` (the tile value) |
| `decomp_static` | the total pops, then each level slides in after the previous one | `[@v]` (the branch value) |
| `data_table` | rows slide in, in-cell bars grow - or move from `"prev"` | the key's row context (measures, `[@s]`) |

```python
# KPI: rolls from last period's value, pulses when below target, shows freshness
add("HTML KPI Revenue", K.kpi_card("Revenue", "[Revenue]", "$#,0", "money", sub, motion=True,
    prev="[Revenue PM]", alert="_v < [Revenue Target]", updated="MAX ( 'Refresh'[UTC] )", stale_after=60), "HTML")
# table: bars move from last month, rows below target pulse
add("HTML Regions", K.data_table(T, "Region",
    [{"label": "Sales", "value": "[Revenue]", "kind": "bar", "prev": "[Revenue PM]"}, ...],
    "Regions", "vs last month", sort_by="[Revenue]", motion=True, alert="[Margin] < [Margin Target]"), "HTML")
```

`updated` must be a UTC datetime (it is compared with `UTCNOW()`), for example a one-row refresh table filled by Power Query with `DateTimeZone.UtcNow()`.

One shared CSS block drives all of it: `MOTION_CSS` (entrance: `mo-gy` / `mo-gx` grow, `mo-pop`, `mo-in` slide in, `mo-gw` width from the previous value, `mo-st` staggers a container's children 55 ms apart, `mo-late` waits for the value, `mo-od`/`mo-os` odometer) and `ALERT_CSS` (`mo-focus`: the entrance and a two-cycle ring in one animation list; an outer ring for chips, cells and rows, an inner ring for bars, whose track clips anything outside; `mo-fd` fresh dot). It animates the individual properties `scale` and `translate`, so an element's own inline `transform` (the scatter bubbles) keeps working.

## Patterns

- **Odometer value:** each digit is a 0-9 strip in a clipped box; the strip's inline `translate:0 -Nem` is its resting place, the keyframe starts from `var(--mo-from,0em)` - the previous value's digit when `prev` is given. The number stays left to right (`direction:ltr; unicode-bidi:isolate`) in RTL pages.
- **Bars from the axis:** `scale` from 0 with `transform-origin` at the base (start side for horizontal bars), ease-out, no overshoot.
- **Bars from the previous value:** `--mo-w0` (previous width, inline) -> `@keyframes {from{width:var(--mo-w0)}}`.
- **Line draw-in:** `<polyline pathLength='1'>` with `stroke-dasharray:1`, `from{stroke-dashoffset:1}`.
- **Alert ring:** `box-shadow` from 0 to 9px while fading out (`color-mix` on the `@@bad@@` token), 2.4 s, **2 iterations**, starting after the entrance.
- **Freshness:** green `@@done_text@@` "Updated N ago" with a dot that pulses twice; past `stale_after` an amber `@@warn_text@@` "Stale · N ago" with a still dot.

Timing: entrances finish within ~1.2 s; attention motion stops within 5 s.

## Rules (measured)

1. **One `<style>` per measure.** Every HTML Content visual is its own document; prefixed names (`mo-*`) avoid clashes.
2. **Windows "Animation effects" off = `prefers-reduced-motion: reduce` inside Power BI Desktop.** Desktop's WebView2 follows the Windows setting, so a reduced-motion rule hides all motion on such machines (on the machine where this was built, nobody saw any motion). The kit ships without it - every animation is short and stops within 5 s; add `@media (prefers-reduced-motion: reduce){...}` when the audience needs it, and say which in the deliverable.
3. **After "Apply external changes", click Refresh.** The visuals keep their cached HTML until Refresh. Check the model first with a DAX query (`SEARCH` for a keyframe name in `INFO.VIEW.MEASURES()`).
4. **Switching pages replays the entrance** (the visuals are rebuilt); "Refresh visuals" on the Optimize tab does not.
5. **No flashes.** Gradual opacity, shadow and transform only; a Desktop burst must show no frame-to-frame change near 10/255.
6. **Clipped on purpose = class `fit-clip`.** The fit gate skips those elements; it parks every animation at its resting moment to measure and then **puts every animation back** (a `finish()` would end a fill-less alert for good and change the page under test).
7. **Static outputs** (PDF/PowerPoint export, subscriptions) show one still moment - the end state of entrances; alerts are visible through their color (the red badge, the amber "Stale") even when not pulsing.
8. **DAX variable names:** `Rows`, `cell` and `on` are reserved words in a DAX query - name them `TopRows`, `tcell`, `isOn`.

## Verify (in this order)

1. Live DAX gate and preview as usual: FIT OK and CONTRAST OK in every stress scenario (all, a filter, an empty selection).
2. **Frozen frames:** `node tools/pbip-html-pipeline/motion_frames.mjs preview.html out/frame 0.35,1.3,1.8,6.5 x,y,w,h` pauses every animation at exact times (it can capture below the fold). The alerts are visible at ~1.8 s and gone at 6.5 s.
3. **Desktop:** Apply external changes, **Refresh**, then switch to the page. Alerts last under 5 s and a slow machine draws cards one by one, so check them with a `k = 8` build of the same cards (the ring then lasts ~45 s) or a `burst.ps1` recording (Desktop must be the front window - the burst captures the screen).

## Verified

- **Desktop, Secure edition, 10 Nov 2026, all nine builders:** entrance (8x slow: bars growing from the base, cells and tiles popping, rows sliding in, digits rolling) and `alert=` on a lab page bound to a live model - every ring sat exactly on the items breaking their condition (waterfall steps < 100, heat cells < 100, lift < 1.0x, scatter margin < 15%, treemap tiles < 300, table rows with margin < 15%, KPI below target); KPI rolling from the previous value; "Updated 5 min ago" and amber "Stale · 3 h ago".
- **Gates:** `motion=False` byte-identical for all builders; motion on: FIT OK and CONTRAST OK for all data, a category filter and an empty selection (fit check stable 6 of 6 runs).
- **Components:** `kpi-card-motion.dax` (entrance) and `watch-list-motion.dax` (alert list) measured in Desktop.
- Not yet checked in the Power BI Service or on mobile.

## Brand loops from a video (experimental)

For a logo sting that is not data-driven, rebuild the clip as SVG + GSAP with [motion2code](https://github.com/lovisdotio/motion2code) (MIT) and bake it into CSS keyframes with `tools/motion-bake/bake.mjs`. Status: passed its own fidelity gate on two samples in headless Edge; **not run in Power BI** yet. A brand loop is decoration - keep it out of analytical pages, or let it stop within 5 s.
