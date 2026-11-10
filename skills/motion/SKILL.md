---
name: motion
description: Add motion to HTML Content visuals - an entrance that replays on every render (KPI odometer, growing bars, line draw-in, badge pop) or an ambient loop every viewer sees all the time (pulse on risk rows, sheen, live dot). CSS keyframes only, so it runs in the Secure edition. Use when the user asks for motion, animation, "alive" visuals, counting numbers, or attention on exceptions in a dashboard.
---

# Motion in HTML Content visuals

Motion in this kit is **CSS `@keyframes` in an inline `<style>` inside the measure**. No script, no GSAP, no external file: the Secure edition strips `<script>`, and the CSS route also works in the Regular edition, in Desktop and in the Service. Measured in Power BI Desktop (Secure edition, 10 Nov 2026) - see "Verified" below.

## Pick the kind of motion first

| Kind | When it plays | Use for | Component |
| --- | --- | --- | --- |
| **Entrance** | every time the visual renders: page open, slicer or cross-filter change, Refresh | KPI values, bars, lines - "the numbers just updated" | `library/components/kpi-card-motion.dax` |
| **Ambient loop** | all the time, for every viewer, with no interaction | exceptions that need attention: rows below target, live status | `library/components/watch-list-motion.dax` |

Motion must carry meaning. A loop goes only on things the reader should notice (risk rows, not every row); an entrance says "this changed". One or two moving regions per page - a page where everything moves has no focus.

## Patterns (all in the two components)

- **Odometer value:** each digit is a 0-9 strip (`<i>` per digit, `height:1em`) inside a clipped box; the strip's inline `transform:translateY(-Nem)` is its resting place and the keyframe only defines `from{transform:translateY(0)}`. Stagger with inline `animation-delay`. The number stays left to right (`direction:ltr; unicode-bidi:isolate`) in RTL pages.
- **Growing bars:** SVG `<rect>` with `transform-box:fill-box; transform-origin:50% 100%` (negative bars `50% 0`), `from{transform:scaleY(0)}`, a small overshoot easing `cubic-bezier(.34,1.4,.64,1)`, staggered per bar.
- **Line draw-in:** `<polyline pathLength='1'>` with `stroke-dasharray:1`, `from{stroke-dashoffset:1}`.
- **Badge pop:** `from{opacity:0;transform:scale(.6)}` with `cubic-bezier(.34,1.56,.64,1)`, delayed until the value has landed (~0.75 s).
- **Pulse ring (loop):** `box-shadow` growing from 0 to 9px while fading out, 2.4 s `ease-out infinite`. Red for loss, amber for under target; rows on target do not pulse.
- **Sheen (loop):** a 40px white-to-transparent gradient sweeping across a bar inside `overflow:hidden`, 2.8 s, staggered per row.
- **Live dot (loop):** opacity 1 -> .35 and scale 1 -> .7, 2 s `ease-in-out infinite`.

Timing budget: entrances finish within ~1.2 s; loops 2-3 s per cycle. Easing: ease-out for arrivals, small overshoot only on pops and bar tops.

## Rules (measured)

1. **Keyframe names and classes are per visual.** Every HTML Content visual is its own document, so put the `<style>` in each measure; short prefixed names (`kroll`, `mwpb`) avoid clashes when a measure is reused.
2. **Windows "Animation effects" off = `prefers-reduced-motion: reduce` inside Power BI Desktop.** Desktop's WebView2 follows the Windows setting. A `@media (prefers-reduced-motion: reduce)` rule therefore turns the motion off on such machines - and on the machine where this was built it did, so nobody saw any motion. Decide it per dashboard and say so in the deliverable: the components ship **without** the media query (motion always plays, kept short and flash-free); add `@media (prefers-reduced-motion: reduce){...{animation:none}}` when accessibility comes first.
3. **After "Apply external changes", click Refresh.** The visuals keep their cached HTML until Refresh; "the motion does not run" right after Apply usually means the old measure is still on screen. Check the model with a DAX query (`SEARCH` for a keyframe name in `INFO.VIEW.MEASURES()`) before judging the render.
4. **No flashes.** Animate opacity, shadow and transform gradually; never toggle a large area between light and dark. A burst of the Desktop window must show no frame-to-frame change near 10/255 or more (measured loop: 0.16/255).
5. **Elements clipped on purpose carry class `fit-clip`** (digit strips, sheens). The fit check skips them and settles every animation first (entrances finished, loops parked at time 0), so the gate measures the resting layout.
6. **Export to PDF / PowerPoint and subscriptions show one still moment.** Entrances show their end state; make sure any moment of a loop also reads well.
7. **DAX variable names:** `Rows` and `cell` are reserved words in a DAX query - name them `TopRows`, `tcell`.

## Verify (in this order)

1. Live DAX gate and preview as usual (`gen_query.py` -> `runq.ps1` -> `gen_preview.py` -> `fitcheck.mjs`): FIT OK and CONTRAST OK in every stress scenario.
2. **Frozen frames:** `node tools/pbip-html-pipeline/motion_frames.mjs preview.html out/frame 0.15,0.45,0.8,1.5 x,y,w,h` pauses every animation in every card at exact times and screenshots a region. Look at the frames: the motion is there, and the last frame equals the static card.
3. **Desktop:** write the PBIP, Apply external changes, **Refresh**, then record a burst of the window region with `tools/pbip-html-pipeline/burst.ps1` (Power BI Desktop must be the front window - the burst captures the screen, not the window). Entrance: change a filter during the burst. Loop: no interaction at all; most consecutive frames must differ.

## Verified

- Desktop, Secure edition, 10 Nov 2026: KPI entrance seen frame by frame after Refresh; watch-list loop changed on 39 of 39 frames of a 3.5 s burst with no interaction; largest frame-to-frame change 0.16/255. Both components re-run against a live model: FIT OK and CONTRAST OK for all data, a category filter and an empty selection.
- Not yet checked in the Power BI Service or on mobile.

## Brand loops from a video (experimental)

For a logo sting or a hero loop that is not data-driven, rebuild the clip as SVG + GSAP with [motion2code](https://github.com/lovisdotio/motion2code) (MIT), then bake it into CSS keyframes for HTML Content with `tools/motion-bake/bake.mjs` (see its README). Status: passed its own fidelity gate on two motion2code samples in headless Edge; **not run in Power BI** yet.
