---
name: dashboard-shell
description: Build a complete dashboard inside one HTML Content visual that covers the whole report canvas. Use when the user asks for a fullscreen app-like dashboard, a single-visual layout, or a web-app look inside Power BI.
---

# Dashboard shell (single fullscreen visual)

## When to use

The user wants the whole page to be one designed surface: header, side menu, KPI row, charts, table, footer, all inside one HTML Content visual.

## Decide the binding model first

| Model | Binding | Cross-filter out | Scripts | Best for |
| --- | --- | --- | --- | --- |
| A1 One giant measure | Values only | Never | Yes (Regular) | Pixel-perfect app look, story pages |
| A2 Rows + Context | Values (per-row measure) + Context column | Yes, per row | Yes (Regular) | Shell regions that must filter the report |

State the trade-off to the user in one sentence before building: A1 gives freedom but nothing inside it can filter other visuals; A2 filters but the shell must be row-structured.

## Shell structure

Use `library/shell/dashboard-shell-body.html` as the Body template and `library/shell/dashboard-shell.css` as the Stylesheet. The shell gives:

- `header` (title block, date, context actions)
- `aside` side menu (RTL: docked right; LTR: left) with in-DOM tab items
- `main` content area with `{{content}}` injected rows
- `footer` strip

For A1, `{{content}}` receives the single measure's markup. For A2, each Context row lands as one `.htmlViewerEntry`; shape rows with the Row template `{{row}}` passthrough and per-row measures from `library/components/`.

## Canvas sizing

Set the visual to the full page: x=0, y=0, width=page width, height=page height (1280×720 or 1920×1080 by default). Turn off the visual container's Effects → Background, Border and Shadow, or set them deliberately. Inside the DOM, size the shell with `100%` / `100vh`-style flex or grid, not fixed pixels, so the shell survives page-view scaling.

## In-DOM navigation vs real navigation

The shell's side menu can switch **sections inside the visual** using a script (Regular edition) per the documented pattern: shared `window.app` functions defined once in the Body template, tiny per-row init scripts, sections shown/hidden in the DOM. This is real and documented (in-DOM filtering / progressive disclosure). What it does not do: switch Power BI pages, change filters, or affect other visuals. If a menu item must open another report page, overlay a native transparent button on that item (see `skills/navigation-header-menu/SKILL.md`) or move navigation out of the visual.

If the target edition is Secure, menu interactions are impossible; make the menu display-only plus native overlay buttons.

## State honesty

No localStorage/cookies exist in the sandbox. Any in-DOM state (open tab, expanded card) resets when the visual re-renders: on data refresh, on cross-filter, on *Rebuild content* updates. Choose *On data update → Preserve unchanged content* when in-DOM state matters, and know that rows which move are re-inserted and reset.

## RTL

The shell ships RTL-ready: `dir="rtl"` on the root, menu docked right, numbers isolated. Verify mixed-direction runs with the rules in `skills/rtl-hebrew/SKILL.md`.

## Delivery checklist

- Binding model chosen and stated (A1/A2), edition chosen and stated.
- Body template, Row template, Stylesheet, measures: all delivered as copyable code.
- Interactions enumerated, each marked: cross-filter (real), in-DOM script (real, Regular only), native overlay (real), or display-only.
- Verification label: doc-based, not run in Power BI; hand over `checklists/validation.md`.
