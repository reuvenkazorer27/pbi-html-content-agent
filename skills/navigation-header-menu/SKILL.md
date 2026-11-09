---
name: navigation-header-menu
description: Build dashboard headers and side menus in HTML Content with real navigation. Use when the user asks for a side menu, top header bar, page tabs, or app-like navigation inside a Power BI dashboard.
---

# Header and side menu with real navigation

## The one rule that keeps you honest

HTML inside the visual cannot navigate between report pages, set bookmarks, or change filters. Navigation is one of two real mechanisms:

1. **Native blank buttons layered over the HTML menu** (works everywhere, both editions). The HTML shows the designed menu; invisible native buttons on top carry the action (Page navigation / Bookmark / Back).
2. **Native page navigator**, styled to match, placed over or beside the HTML header/menu.

A `<button>` or `<a>` inside the HTML that looks like navigation but has no native button over it is a fake. Never ship one. (In-DOM section switching via script is allowed in the Regular edition, but that is not page navigation; see `skills/dashboard-shell/SKILL.md`.)

## Header bar

`library/components/header-bar.dax`: title, subtitle/date, optional KPI strip and context badges. Bind to a measure in Values (no Context needed unless header elements cross-filter). Recommended height: 64px at 720p, 96px at 1080p. Keep the header's right edge aligned with the RTL menu column.

## Side menu

`library/components/side-menu.dax`: a vertical menu column, RTL-docked to the right (200px at 720p). Two serving modes:

- **Menu + overlay buttons (recommended):** HTML menu renders items; for each item, a native blank button is placed at the item's exact rectangle, transparent (fill transparency 100%, no border, no text), Action = Page navigation to the target page (or Bookmark for panel states). Document each overlay rectangle in the delivery table.
- **Display-only menu:** the menu shows location and structure; navigation lives in a native page navigator strip inside the header. Choose this when overlay maintenance is a burden (menu items change often).

Active-page highlight must be computed per page (each page's menu measure marks its own active item, or use a measure with `SELECTEDVALUE` on a page table). Do not hard-code one "active" item across all pages.

## Overlay button spec (per item)

| Property | Value |
| --- | --- |
| Type | Blank button |
| Position/size | Exact menu-item rectangle from the coordinate table |
| Style | Fill transparency 100%, border off, text none |
| Action | On → Page navigation → target page (or Bookmark) |
| z-order | Directly above the menu visual |

Validate by clicking every item in Desktop reading view and again in the Service; an overlay that is 2px off still works but feels broken, so use the pixel-math convention for item rectangles.

## Header/side menu data honesty

Dates, "last refresh" and user name shown in the header must come from real measures (`NOW()`/`UTCNOW()` with the documented timezone caveat, a refresh-log table, `USERPRINCIPALNAME()` where applicable), never typed into the HTML as static text.
