# Validation checklist - before calling a dashboard "done"

Run this in the real target environment. Mark each item Pass / Fail / N/A. Until this passes, the delivery note must say "doc-based, not run in Power BI".

## 0. Fit (before writing the PBIP, then in Desktop) - see `../reference/design-system.md`

- [ ] Base theme padding read; every HTML visual and panel slicer has padding 0 + chrome off in `visual.json`.
- [ ] Exact-size preview fit check prints `FIT OK` (8px slack on every card).
- [ ] Font sizes meet the 1080p scale (body ≥15px, captions ≥13px) - or the 720p equivalent.
- [ ] After Apply external changes + Home → Refresh: screenshot; no card clipped, every title on one line, Hebrew right-aligned in every card.
- [ ] "ועוד N" ("and N more") lines carry a hover tooltip with the hidden items.

## 1. Power BI Desktop - render

- [ ] Every HTML Content visual renders (no blank box, no error icon).
- [ ] Open each visual's *Show raw HTML* (or Diagnostics > Raw HTML) and confirm the measure produced the markup you expected.
- [ ] Secure edition only: open Diagnostics > Sanitizer and confirm nothing you need was stripped. If it was, rework the markup or move that visual to Regular with an explicit reason.
- [ ] Fonts/alignment: Hebrew right-aligned, no flipped numbers, ₪ attached to amounts, dates well-formed.
- [ ] Background blending: transparent regions show the intended page background; no white boxes over a colored/image background.

## 2. Interactivity (Desktop reading view)

- [ ] Native slicer/filter pane change → every HTML visual updates.
- [ ] Cross-filter visuals (Context + Enable): click a row/chip → other visuals filter; unselected entries dim; click again clears.
- [ ] Inner controls marked `data-hc-suppress` do not cross-filter and do not open the context menu.
- [ ] Right-click on a Context row → context menu; drillthrough appears if a drillthrough page exists.
- [ ] Tooltips: contextual tooltips on rows; manual `tooltipEnabled` tooltips on one-giant-measure visuals.
- [ ] Navigation: every overlaid native button navigates; no HTML "button" that does nothing.
- [ ] Empty state: select a filter combination with no data → "No Data" message shows correctly.

## 3. Scripting (Regular edition only)

- [ ] Diagnostics > Console shows expected logs, no errors.
- [ ] Diagnostics > Events shows updates and cross-filter add/remove/clear as expected.
- [ ] *On data update* mode chosen deliberately (Rebuild vs Preserve unchanged); in-DOM state behaves as designed across a slicer change.
- [ ] No `eval`, no external JS files, no fetch/XHR inside content.

## 4. Power BI Service

- [ ] Published report renders identically; re-test every interactivity item.
- [ ] Links (if any): *Allow opening URLs* is on; clicking prompts consent and opens http/https only.
- [ ] iframes (Regular only, if used): render in the Service (they never render in Desktop).
- [ ] "Last refresh" text is truthful (Service runs in UTC; verify the timezone logic).

## 5. Export and sharing

- [ ] Export to PDF/PowerPoint: HTML visuals appear only if they are the Secure edition; Regular visuals show an error/blank. Confirm the chosen edition matches the distribution need.
- [ ] Email subscription snapshot: same rule.
- [ ] Tenant policy: if "certified visuals only" is enforced, uncertified visuals are blocked; check with the admin or use Secure / organizational visuals.

## 6. Mobile (only if promised)

- [ ] A mobile layout exists (View > Mobile layout); custom visuals are at least 323×180pt.
- [ ] On a real device: rendering, single-tap selection, no reliance on multi-select (not supported for custom visuals).
- [ ] If mobile was not built, the delivery note says "desktop only".

## 7. Honesty label on delivery

- [ ] The delivery note lists: what was run and where, what is doc-based and untested, and which items above are still open.
