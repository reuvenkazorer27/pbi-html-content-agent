# motion-bake - a motion2code loop as CSS keyframes for HTML Content

**Status: experimental.** Passed its own fidelity gate on two motion2code samples in headless Edge (template "LOOP": worst mean pixel difference 0.0001; gallery "think-big", 10 s, 49 elements: 0.0003, checked every 0.5 s). **Not run in Power BI yet** - verify in Desktop before shipping (`skills/motion/SKILL.md`, "Verify").

[motion2code](https://github.com/lovisdotio/motion2code) (MIT) rebuilds a motion-design video as inline SVG driven by one GSAP timeline. HTML Content's Secure edition strips `<script>`, so that page cannot run inside Power BI. `bake.mjs` samples the page through its contract (`window.anim.seek(t)`, `<html data-ready="1">`) and writes the same motion as pure CSS `@keyframes`:

```bash
node tools/motion-bake/bake.mjs path/to/index.html --out baked --name brand [--fps 30] [--check 0.5] [--max-diff 0.02]
```

Outputs in `--out`: `baked.html` (one self-contained `<div>`: CSS + SVG, no script, no external URL), `measure.dax` (a DAX measure returning it, quotes doubled), `preview.html` (source fonts kept, for the fidelity check), `report.json` (size, keyframes, per-time scores) and the worst source/baked pair as PNG.

## What it handles

- Transforms (attribute or CSS) as `matrix()`; a scale-0 matrix is nudged to 0.0001 because CSS cannot interpolate a singular matrix (it jumps at 50%).
- Opacity, fill, stroke, stroke width/dash/offset, and SVG geometry (`x y width height rx ry cx cy r d`) as CSS properties.
- `polygon` / `polyline` / `line` are rewritten as `<path>` so their geometry animates through `d`.
- `display` toggles become `visibility` computed from the element **and its ancestors** (a child's explicit `visible` would otherwise override a hidden parent).
- Shapes a page creates lazily inside `draw(t)`: one full sweep runs before sampling.
- Web fonts are blocked in HTML Content: text falls back to `--font` (default Segoe UI). The fidelity check keeps the source font so it compares motion, not typefaces.

## Gates

- **Fidelity:** screenshots of the GSAP page and the baked page at the same times, compared in the browser; worst mean pixel difference must stay under `--max-diff`.
- **Control:** the source must actually move between the checked frames, otherwise the score proves nothing.
- **Secure edition:** no `<script>`, no `on*=` handlers, no external `url()`, `@import`, `@font-face` or `http(s)` (in-document `url(#id)` references are fine).
- **Size:** warns above 30,000 characters, fails above 200,000.

It needs Microsoft Edge (headless, DevTools protocol) and Node 22+ - no npm packages, the same pattern as `tools/pbip-html-pipeline/fitcheck.mjs`.
