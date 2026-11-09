# Capabilities reference - HTML Content 2.0

Everything on this page was verified against the official documentation at html-content.com on 9 Nov 2026 (URLs in `../SOURCES.md`). Where behavior depends on the host (Desktop/Service/mobile), it is marked. The behaviors the pipeline relies on (Secure edition rendering, padding, RTL, theme variables, palette slicers) were measured in Power BI Desktop - see `design-system.md`. Everything else on this page is documented behavior: run `../checklists/validation.md` before relying on it in production.

## Editions

| | Regular | Secure (Certified) 🛡️ |
| --- | --- | --- |
| AppSource GUID (PBIR `visualType`) | `htmlContent443BE3AD55E043BF878BED274D3A6855` | `htmlContent443BE3AD55E043BF878BED274D3A6865` |
| Certified by Microsoft | No | Yes |
| Sanitization | None; content rendered as written | Allowlist sanitizer on HTML, attributes, URLs and CSS |
| `<script>` and inline `on*` handlers | Execute (documented, not formally supported) | Stripped (elements with handlers are dropped) |
| External resources (images, fonts, iframes) | Allowed (visual declares WebAccess `*`), subject to CORS/sandbox | Blocked (no privileges declared) |
| Export to PDF / PowerPoint, email subscriptions | Not rendered | Rendered |
| Tenant "certified visuals only" policy | Blocked | Allowed |
| Price / license | Free, MIT | Free, MIT |
| Minimum host | Desktop July 2024 / PBIRS Sep 2024 | Same |

A standalone build of the Regular edition is published on the GitHub repo for side-loading; it behaves like Regular but does not auto-update from AppSource.

## Data roles

- **Values** (`content` in PBIR): the column or measure whose value is rendered as HTML (or Markdown, if the renderer property is switched).
- **Context** (`sampling` in PBIR; renamed from "Granularity" in 2.0): columns and/or measures that create row context without being rendered. One dataset row per unique combination of Context column values. This role is the key to interactivity.
- **Tooltips**: fields shown in the standard tooltip for the hovered data point.

## Templates (2.0)

- **Body template**: wraps all rows; `{{content}}` marks where rows are injected. Can be bound to a measure via conditional formatting (fx).
- **Row template**: wraps each row; `{{row}}` marks the row value. Use `{{row}}` alone when the per-row measure returns its own root element. An authored row template always wins over the default structure.
- Render order: body template first, then rows (matters for scripting: define shared functions in the body template).
- A per-row measure that returns `BLANK()` drops that row instead of leaving an empty slot.

## Interactivity (verified)

Power BI only lets a visual cross-filter, drill through, or show a report-page tooltip when it can reconcile the clicked element to a row in the visual's dataset. Hence two design classes:

**With Context (rows exist):**
- **Cross-filtering**: turn on *Cross-filtering → Enable* (off by default; the card only appears when the dataset has row context). Clicking a row element filters other visuals. Unselected rows get the `unselected` class and are dimmed (default 70% transparency; configurable; overridable via CSS on `.htmlViewerEntry.unselected`).
- **Contextual tooltips**: fields from Context and Tooltips roles; report-page tooltips and modern tooltip actions reconcile through Context fields.
- **Right-click context menu**: data-point actions including drillthrough when a valid drillthrough page exists.
- **Hover**: the row element gets a `hover` class; `:hover` CSS also works.

**One giant measure (no rows):**
- No cross-filtering, no contextual tooltips, no drillthrough.
- Manual tooltips: `class="tooltipEnabled"` plus `data-tooltip-title-XX` / `data-tooltip-value-XX` attributes (XX is a matching key per field).

**Suppressing interactivity (2.0):** `data-hc-suppress="filter|context-menu|tooltip|all"` on any element makes it and its children inert to the visual's own handling. Declarative, works in both editions, no script. Hyperlinks still work under suppression.

## Scripting (Regular edition only)

- `<script>` elements and inline `on*` handlers execute. The visual builds DOM via `Range.createContextualFragment()`, so scripts run when their node is inserted.
- Execution model: a script runs once on insertion. Body template inserts first, then rows. Define shared functions once on `window` in the body template; per-row scripts should only call them.
- *On data update* render mode: **Rebuild content** re-parses everything (all scripts re-run); **Preserve unchanged content** re-inserts only changed rows (body/global script persists, unchanged rows keep DOM state). Rows that move during an update are detached/reattached and re-run.
- Inline `on*` handlers fire on every event with no timing caveat.
- Gotchas: with `{{row}}` passthrough the row must have exactly one root element (it becomes the selectable node); nest modals/scripts inside it. Inner controls that must not cross-filter: `data-hc-suppress="filter"` or `event.stopPropagation()`.
- Scripts cannot reach the Power BI host page (sandboxed iframe). No `fetch`/XHR to pull data; the dataset supplies everything.
- Theme colors in script: read `getComputedStyle(document.documentElement).getPropertyValue('--pbi-theme-*')`; re-read after updates.
- Debugging: enable *Content formatting → Enable diagnostics*; the diagnostics dialog (icon on the visual in edit mode, or Ctrl/Cmd+D) has Raw HTML, Sanitizer (Secure only), Console and Events tabs. Console and event logs persist across updates until cleared.

## Sandbox limitations (all editions, all hosts)

Blocked by the Power BI custom-visual sandbox, not by the visual: some hyperlink behaviors (http/https work through the *Allow opening URLs* property, which delegates to Power BI and asks the user's consent; `javascript:`, `mailto:`, `file:`, `ftp:` do not work), `<iframe>` in Power BI Desktop (test iframes in the Service), iframes to sites that block framing/CORS (YouTube blocked; Vimeo documented as working), externally hosted JavaScript files, `<video>` elements, modal windows/popups, cookies and local storage.

## Secure edition sanitizer essentials

- Reduced accepted-tag list (HTML + SVG allowlist); disallowed tags are dropped with their content.
- Event-handler attributes cause the whole element to be dropped.
- External URLs blocked everywhere: `<img src>`, CSS `url()`, `@import`, `@font-face`. Workaround for images: base64 `data:image/...` URIs (SVG data URIs allowed since 1.6.1, recursively scanned). Use the system font stack (`'Segoe UI', sans-serif`) instead of web fonts.
- `href` on links is stripped unless *Allow opening URLs* is enabled.
- CSS comments must be `/* ... */`; `//` comments break the stylesheet.

## Theme colors (2.0)

`--pbi-theme-*` CSS variables on `:root`, updating on theme or high-contrast change. Groups: data colors (`--pbi-theme-color-1..N`), structural (`--pbi-theme-fg`, `-fg-neutral-secondary`, `-fg-neutral-tertiary`, `-bg`, `-bg-light`, `-bg-neutral`, `-fg-selected`, `-hyperlink`), sentiment (`-good`, `-bad`, `-neutral`), divergent (`-min`, `-center`, `-max`). Always pass a fallback to `var()`. High contrast adds class `pbi-theme-hc` on `#htmlContent`; only `-fg`, `-bg`, `-fg-selected`, `-hyperlink` are guaranteed meaningful there, and forced-colors mode may require `forced-color-adjust: none` for elements you must color yourself.

## Useful formatting properties

- Renderer: HTML (default) or Markdown.
- Show raw HTML: renders the processed markup for debugging (plain text above ~200 KB, truncated above ~512 KB; same caps in the Diagnostics Raw HTML tab).
- "No Data" message: customizable, conditional-formatting capable, rendered under `#statusMessage`.
- Default body styling (font family/size/color/alignment) applies only where content has no inline styles; *Override inline styles* forces it (coarse). A Stylesheet property entry beats both.
- Stylesheet property: paste CSS or bind to a measure via fx; when set, the simple font/color properties are disabled.

## Host differences to remember

- **Desktop is not a full browser**: iframes do not render in Desktop; test in the Service.
- **Mobile apps**: AppSource custom visuals do render, with caveats (for example multi-select of data points is not supported for custom visuals). The mobile layout is a separate canvas (see `canvas-and-layout.md`). Validate on a real device before promising mobile behavior.
- **Export/subscriptions**: certified edition only.
- **Publish to web / sovereign clouds / Report Server**: check the environment before committing; uncertified visuals can be blocked by tenant policy ("Add and use certified visuals only"), which the admin can also bypass via the organizational store.
