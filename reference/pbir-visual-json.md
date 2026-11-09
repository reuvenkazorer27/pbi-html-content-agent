# PBIR authoring - HTML Content visual.json

Verified against the official PBIR Implementation Guide (html-content.com/docs/pbir-guide), 9 Nov 2026. Valid for HTML Content 2.0 and above; 1.x persists a different property set. Only sections whose heading says *measured in Desktop* were checked in Desktop (the settings `gen_pbip.py` writes). Every other section is source-verified only - validate it by opening the report in Desktop before relying on it.

## The short version

| Path | Value |
| --- | --- |
| `visual.visualType` | `"htmlContent443BE3AD55E043BF878BED274D3A6865"` (Secure) or `"htmlContent443BE3AD55E043BF878BED274D3A6855"` (Regular) |
| `visual.query.queryState.content.projections` | At least one projection into the `content` role (a measure or column producing HTML) |

Nothing else is mandatory. HTML Content's content comes from the data model, not from properties, so a visual with only a `content` projection renders with default formatting and no `objects` block.

Because the GUID matches an AppSource listing, Power BI retrieves and updates the visual code automatically; the visual does not need to be committed to the PBIP assets. The same `visual.json` body can render differently between editions because Secure sanitizes and Regular does not.

## Minimal working example

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json",
  "name": "kpiCard",
  "position": { "x": 24, "y": 104, "width": 296, "height": 128, "z": 1, "tabOrder": 1 },
  "visual": {
    "visualType": "htmlContent443BE3AD55E043BF878BED274D3A6855",
    "query": {
      "queryState": {
        "content": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_HTML" } },
                  "Property": "KPI Revenue"
                }
              },
              "queryRef": "_HTML.KPI Revenue",
              "nativeQueryRef": "KPI Revenue"
            }
          ]
        }
      }
    }
  }
}
```

Convention used across this folder: HTML-producing measures live in a dedicated empty-display-folder measure table named `_HTML`.

## Adding Context (cross-filter / tooltips / drillthrough) - source-verified, not yet run in Desktop

Add projections to the `sampling` role (the Context data role's persisted name). At least one column here, plus enabling cross-filtering, makes rows selectable:

```json
{
  "queryState": {
    "content": { "projections": [ "...the per-row HTML measure projection..." ] },
    "sampling": {
      "projections": [
        {
          "field": {
            "Column": {
              "Expression": { "SourceRef": { "Entity": "Sales" } },
              "Property": "Category"
            }
          },
          "queryRef": "Sales.Category",
          "nativeQueryRef": "Category"
        }
      ]
    }
  }
}
```

## Setting Body/Row templates - source-verified, not yet run in Desktop

Templates persist under `objects.templates` with `bodyTemplate` and `rowTemplate`:

```json
{
  "objects": {
    "templates": [
      {
        "properties": {
          "bodyTemplate": { "expr": { "Literal": { "Value": "'<div class=\"rows\">{{content}}</div>'" } } },
          "rowTemplate": { "expr": { "Literal": { "Value": "'{{row}}'" } } }
        }
      }
    ]
  }
}
```

## Container chrome: padding 0 (measured in Desktop - see `design-system.md` §1)

The Fluent 2 base theme pads every visual 16/14/16/16. Without overriding it the HTML viewport is 30px shorter and 32px narrower than `position`, and every card clips. Ship every HTML Content visual (and slicers that sit on an HTML panel) with:

```json
"visualContainerObjects": {
  "padding":      [{"properties": {"top": {"expr": {"Literal": {"Value": "0D"}}}, "bottom": {"expr": {"Literal": {"Value": "0D"}}},
                                    "left": {"expr": {"Literal": {"Value": "0D"}}}, "right": {"expr": {"Literal": {"Value": "0D"}}}}}],
  "background":   [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "border":       [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "title":        [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "dropShadow":   [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
  "visualHeader": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
}
```

Also register the AppSource visual once in `report.json`: `"publicCustomVisuals": ["htmlContent443BE3AD55E043BF878BED274D3A6865"]` (Secure) - Desktop then downloads it on open. Verified 9 Nov 2026 in Desktop 2.159 (Oct 2026).

Native dropdown slicer on an HTML panel (verified): `visualType: "slicer"`, projection under `queryState.Values` with `"active": true`, `objects.data[0].properties.mode = 'Dropdown'`, `objects.header[0].properties.show = false`, same chrome block as above.

## Literal-expression rules (the four escaping laws)

1. JSON strings must be properly escaped (quotes, backslashes, newlines).
2. Integer values end with a `D` suffix: `100D`.
3. Text values are wrapped in single quotes inside `Value`: `"'...'"`.
4. Booleans are the literals `true` / `false`.

These apply anywhere a property is written as a literal expression.

## Practical authoring notes

- Property names seen in this folder's examples (`bodyTemplate`, `rowTemplate`, the cross-filtering card, `bodyTemplate` measure binding) follow the 2.0 property set; when in doubt, add the visual once in Desktop, set the property by hand, and diff the written `visual.json`. That diff is the ground truth for any property not documented here.
- Keep HTML out of `visual.json` when you can: content belongs in measures. The exceptions are templates and stylesheet values, which are legitimately persisted as properties (or bound to measures via conditional formatting).
- `position` units are canvas pixels at the report's page size; see `canvas-and-layout.md` for the grid convention.

## HTML Content 2.0 persisted properties (research 9 Nov 2026 - source-verified, not yet run in Desktop)

Sources: html-content.com/docs/pbir-guide and github.com/dm-p/powerbi-visuals-html-content `capabilities.json` (main). Written as `visual.objects.<object>[0].properties.<prop>.expr.Literal.Value`; Desktop writes only non-default values.

| Setting | object.property | Notes |
| --- | --- | --- |
| Stylesheet | `stylesheet.stylesheet` | fx-bindable to a measure; never use `id="visualUserStylesheet"` in content |
| Cross-filtering | `crossFilter.enabled` | default false; needs a `sampling` (Context) projection |
| Dim unselected | `crossFilter.useTransparency`, `crossFilter.transparencyPercent` | defaults true / `70D` |
| Renderer, raw HTML, no-data, URLs, diagnostics | `contentFormatting.format` (`'html'`/`'markdown'`), `.showRawHtml`, `.noDataMessage` (fx), `.hyperlinks`, `.enableDiagnostics` | |
| Render mode | `contentFormatting.renderMode` | `'rebuild'` / `'reconcile'` |
| Legacy | `compatibility.legacyRendering` | |

Data roles: `content` max 1 field; `sampling` (Context) reduced to the top 30,000 rows.

## Native slicer colors (measured in Desktop for `items.fontColor` / `items.background`; other names from the Microsoft PBIR reference)

`objects.items[0].properties.fontColor` / `.background` (`{"solid":{"color":{"expr":{"Literal":{"Value":"'#hex'"}}}}}`), `objects.header[0].properties.fontColor` / `.background`. `items.background` defaults to white - on a dark page always set it (the pipeline does, from the palette). Unverified: the dropdown popup's own background/border property names - diff once in Desktop.

## Page background image / wallpaper (Microsoft PBIR reference - source-verified, not yet run in Desktop)

`page.json` `objects.background` (canvas) and `objects.outspace` (wallpaper) accept only `color`, `image`, `transparency` (no `show`). Image must be nested `image.image.{name,url,scaling}` with `url = {"expr":{"ResourcePackageItem":{"PackageName":"RegisteredResources","PackageType":1,"ItemName":"bg1712....png"}}}` and `scaling` `'Fit'|'Fill'|'Stretch'`. The file goes to `StaticResources/RegisteredResources/` and is listed in `report.json` `resourcePackages` (`type: "RegisteredResources"`, item `type: "Image"`, `name == ItemName`). Page colors cannot be measure-bound. For a dark page make canvas and wallpaper both opaque.

## Custom theme (Microsoft PBIR reference - source-verified, not yet run in Desktop)

`report.json` `themeCollection.customTheme = {"name":"X-<guid>.json","reportVersionAtImport":{...},"type":"RegisteredResources"}` + a `resourcePackages` item `type: "CustomTheme"`; the theme's internal `name` matches; rotate the GUID suffix on every edit (Desktop caches by filename). Generating a theme from `palette.py` makes `--pbi-theme-*` inside HTML Content match the palette. Unverified: theme key for page-background defaults (`page` vs `*`) - use per-page `page.json` instead.

## Accessibility and mobile (schema source-verified, placement partly inferred - not yet run in Desktop)

- Alt text: `general.altText` (bind to a measure for a dynamic summary); container placement inferred - diff in Desktop. Inside HTML: `role="img"` + `aria-label` on SVG survive the sanitizer.
- Tab order: `position.tabOrder` in RTL reading order (header, KPIs right-to-left, main band, detail).
- Mobile: `visuals/<id>/mobile.json` next to `visual.json` (schema `visualContainerMobileState/2.3.0`, `position` required); custom visuals ≥ 323×180pt.

## Secure sanitizer (html-content docs + sanitization-rules.md)

All SVG tags except `<use>`, `<foreignObject>`, `<script>` → gradients, filters, clipPath, mask, pattern with `url(#id)` refs survive. CSS: custom properties, `clamp()`, `rgba()`, `:hover`, `@media`, `@keyframes` allowed; `@import`, `@font-face`, `attr()`, external `url()` blocked. Unverified in Secure: `conic-gradient`, `backdrop-filter`, `<style>` element - check Diagnostics → Sanitizer before use.
