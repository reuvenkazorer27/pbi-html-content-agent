# Canvas and layout reference

Verified 9 Nov 2026. Microsoft Learn is the source for presets and mobile; the pixel-math convention and the Fluent 2 default note come from a third-party source (flagged in `../SOURCES.md`) and are conventions, not Microsoft specs.

## Page sizes (Format page → Canvas settings)

| Type | Pixels | Notes |
| --- | --- | --- |
| 16:9 (default) | 1280×720 (HD) | Default for classic/older reports |
| 16:9 | 1920×1080 (Full HD) | Default for new pages in current (Fluent 2) reports; common for presentation screens |
| 16:9 | 2560×1440 (QHD) | |
| 16:9 | 3840×2160 (4K UHD) | |
| 4:3 | 960×720 | Projectors, 4:3 slide embeds |
| Letter | 816×1056 | Portrait, prints cleanly to US Letter PDF |
| Tooltip | 320×240 | Report-page tooltips; design at Actual Size view |
| Custom | any | Tall scrolling pages, wall displays, embed targets |

A theme can set the default page size for new pages (March 2026 theme schema). Always read the target report's actual page size before producing coordinates: the Size dropdown under 16:9 tells you which one the report uses.

## Page view is not canvas size

View → Page view controls scaling: Fit to page (default), Fit to width, Actual size. A 1280×720 page on a QHD monitor renders at roughly 2x. Vectors (including SVG in HTML Content) stay sharp; bitmap backgrounds upscale, so export background images at 2x the canvas.

## Pixel-math convention (auditable layouts)

Use an 8px grid. On 1280×720:

- Outer margin 24px, gutters 16px → usable width 1232px.
- 4 equal cards: 296px wide. 3 cards: 400px. 2 cards: 608px.
- Header 64px + 16px gutter → first content row at y = 104.
- RTL side menu: dock right, width 200px → menu x = 1280 - 24 - 200 = 1056, y = 104, height = 720 - 104 - 24 = 592.

On 1920×1080 multiply every value by 1.5 (margin 36, gutters 24, header 96, menu width 288-300).

**Measured 1920×1080 layout that fits (the kit's reference build, a project-portfolio dashboard):** margin 32, gutter 16, right panel 296 (x=1592, y=112, h=936), content 32..1576. Header 24-96 (h72) · KPI row 112-272 (5 × 296 wide, h160 - 136 was too short) · middle 288-672 (h384: 496 + 520 + 496) · bottom 688-1048 (h360: 1016 + 512). Panel slicers at x=1608, w=264, h=40, y = 112 + 64 + 24 + 80·i. All with container padding 0 (`design-system.md` §1). For LTR the layout is mirrored: x' = 1920 - x - w.

Keep every x, y, width, height a multiple of 8. Ship layouts as a table the user can check, never as "drag until it looks right".

## Z-order and layering

- Order is managed in the Selection pane (and `visual.json` z / `tabOrder` in PBIR).
- Overlay pattern for navigation: HTML menu at the bottom of the stack, native blank buttons (transparent fill, no border, no text) exactly on top of each HTML menu item, button action = Page navigation / Bookmark.
- Native slicers that must sit "inside" an HTML panel: same overlay trick; give the HTML panel a matching solid surface under the slicer so the seam is invisible.

## Mobile layout (View → Mobile layout)

- Separate canvas per page; max content width **323pt**; grid scales across phone sizes.
- Recommended minimum sizes: L = 323×180pt (the floor for a custom visual), M = 323×100, S = 158×100.
- The canvas is interactive in Desktop, so you can test buttons/slicers while building. Tooltips are disabled on the layout canvas (they work in the app).
- Slicer selections made in the mobile canvas do not carry to web layout and vice versa; published reports use the web-layout slicer state.
- Size/position formatting in mobile layout is disconnected from desktop layout (changing one never moves the other).
- Auto-create (View → Mobile layout → Auto-create) produces a starting layout; treat it as a draft.
- Custom visuals in the mobile apps: AppSource visuals render, but multi-select of data points is not supported for custom visuals, and each visual should be validated on a device. Export/subscription rendering is a separate, certification-gated path.

## Backgrounds: page background vs wallpaper vs visual

- **Wallpaper** sits behind the page area (outside the canvas); **Page background** sits behind the visuals on the canvas; a visual's own **Effects → Background** is the container surface.
- HTML Content paints no background of its own: wherever your CSS does not set a background, the page background shows through. For blending HTML visuals into a designed (non-HTML) background: transparent container (default), no `background` on `body`/`#htmlContent`, card surfaces painted locally.
- To match the page color exactly inside HTML: `background: var(--pbi-theme-bg, #F3F2F1)` or the exact hex from the page background setting.
- If the page background is an image, align HTML "holes" (transparent regions) to the image's shapes using the pixel-math table; gradients rarely survive scaling, so prefer flat regions or soft borders where HTML meets the image.

## Layout and sizing rules

- Work on the page's actual canvas size. Defaults: 1280×720 (16:9 HD, classic) or 1920×1080 (16:9 Full HD, default for new reports on the current theme). Full table in `reference/canvas-and-layout.md`.
- Use the 8px grid convention: 24px outer margin, 16px gutters on 720p (scale ×1.5 on 1080p). Keep every coordinate a multiple of 8.
- Positions in PBIR `visual.json` are canvas pixels (`x`, `y`, `width`, `height`). Visual edges on multiples of 8.
- RTL dashboards: side menu docks to the **right**. Menu width convention: 200px on 720p, 288-300px on 1080p.
- HTML Content visuals do not paint a background by themselves; the page background/wallpaper shows through wherever your CSS does not paint one. To blend with a non-HTML background: leave the visual container background transparent (Format → Effects), do not set `background` on `body`/`#htmlContent`, and paint local card surfaces only where intended. To match a colored page exactly, use `var(--pbi-theme-bg, #F3F2F1)` or the exact page hex.
- **Dashboard anatomy is not optional**: header strip at the top, the KPI row immediately under it (KPIs are what the reader looks for first - never bury them mid-page), main analysis in the middle band, detail/exception rows at the bottom.
- **No dead space**: size every card to its content. If a card ends up with more than ~15% empty area, shrink it or feed it more content - stretch the grid, never the whitespace. After placing everything, scan the canvas: any region wider than one gutter with no visual is a defect, unless it deliberately separates groups.
- **Density check**: a composite page (1280×720 or 1920×1080) typically carries 8-14 visuals. Fewer than 6 usually means the canvas is under-used; more than 16 means it is crammed.
- **One rhythm**: one corner radius per dashboard (the style sets it, 8-18px), one card material, one shadow, uniform gaps (8 or 16px), and edges that align across rows and columns.
- Mobile: the phone layout is a separate canvas, max content width 323pt; a custom visual should not go below 323×180pt (size L). Never promise the desktop layout works on a phone; either build a mobile layout or say it is desktop-only. Note: multi-select of data points is not supported for custom visuals in the mobile apps.
