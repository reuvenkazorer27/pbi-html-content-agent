# PBIP HTML pipeline - build, gate, version, write, apply

Measured end to end on 9 Nov 2026 (Power BI Desktop 2.159, Oct 2026) on the demo "תיק פרויקטים" (Project Portfolio) dashboard. See `../../LESSONS.md` for why each step exists. Copy this folder next to the PBIP as `_build/`.

## The loop (every iteration, in this order)

```
python -I gen_query.py q_all.dax                         # 1. DEFINE every measure + EVALUATE all HTML measures
powershell -File runq.ps1 -QueryFile q_all.dax -OutFile r_all.json   # 2. run it on the open Desktop model (port auto)
python -I regress.py r_all.json                          # 3. which cards changed vs the last version (byte compare)
python -I gen_preview.py r_all.json preview.html         # 4. exact-size preview of every card
node fitcheck.mjs preview.html --shot full.png           # 5. GATE: FIT OK + CONTRAST OK (headless Edge, no npm)
python -I stress.py                                      # 6. GATE: 6 filter scenarios (all, one status, one owner, blanks, empty)
python -I versions.py snapshot "what changed" --fit "FIT OK" --results r_all.json --shot full.png   # 7. version
python -I gen_pbip.py                                    # 8. write TMDL + visual.json (padding 0, palette slicers)
# 9. Desktop: Apply external changes -> Home > Refresh -> screenshot and compare with full.png
```

Never write the PBIP (8) unless 5 and 6 pass. Never skip 7: it is what makes revert possible.

## Files

| File | Role |
| --- | --- |
| `measures.py` (start from `measures_example_projects.py`) | Single source of truth: measures, `LAYOUT`, `SLICERS`. Inline styles only; colors only as `@@token@@`; `FONT_SCALE` remaps sizes; `CARD` root carries `height:100vh;overflow:hidden;line-height:1.35;direction:rtl;text-align:right`. |
| `palette.py` | Color tokens for `ocean` (light), `midnight` (dark), `berry` (colorful). Every palette defines every token, including `*_text` variants chosen for WCAG 4.5:1 on their soft backgrounds. Switch: `DASH_PALETTE=midnight`. Page background, preview and slicer colors follow the palette. |
| `gen_query.py` / `runq.ps1` | Live DAX test against the open model through Desktop's own AdomdClient. Optional 2nd arg to `gen_query.py` = a DAX filter table (used by `stress.py`). |
| `gen_preview.py` | Places each measure's real HTML in an iframe of its exact visual size on the page background; defines `fitCheck()` (8px safe edge). |
| `fitcheck.mjs` | Headless Edge via DevTools protocol + Node's built-in WebSocket. Runs `fitCheck()` and a WCAG contrast check on every text element (4.5:1, large text 3:1); optional screenshot. Exit 1 on failure. |
| `stress.py` | Re-renders all cards under filter scenarios and gates each with `fitcheck.mjs`. |
| `regress.py` | Byte-compares every measure's HTML with the last version: refactors must print IDENTICAL; intended changes list exactly which cards changed. |
| `versions.py` | `snapshot` / `list` / `diff vA vB` / `revert vN` (auto pre-revert snapshot). A version = zip of .pbip + report/model definitions + `_build` sources + the real HTML outputs + screenshot, in `<project>/_versions/`. After revert: Apply external changes -> Refresh. |
| `gen_pbip.py` | Measures into TMDL (rebuilt from a backup copy each run), optional partition M swap, page background from palette, `visual.json` per visual with padding 0 / chrome off, slicer `items.fontColor`/`items.background` from palette, AppSource visual registered in `report.json`. |
