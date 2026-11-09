# Palettes - color systems for HTML Content dashboards

Status: doc-based, NOT run in Power BI. The measured palettes the pipeline uses live in `tools/pbip-html-pipeline/palette.py`.

Rule zero: **prefer the report theme.** `--pbi-theme-*` variables keep HTML visuals in sync with the theme and high-contrast mode (see `reference/capabilities.md`). Use a hard-coded palette from this file only when the report has no governed theme or the design calls for a fixed identity. Every palette here ships with a variable-mapped usage example.

Naming: each palette lists `bg` (page), `surface` (cards), `fg` (text), `primary`, `accent`, `good`, `bad`, `neutral`, plus `track` (chart backgrounds) and a 6-color categorical series for charts.

## 1. Ocean BI (default, light, enterprise-calm)

```
bg       #F4F7FA   surface  #FFFFFF   fg  #1F2937
primary  #0F6CBD   accent   #00B7C3
good     #107C10   bad      #D13438   neutral #8A8886
track    #E5EDF3
series   #0F6CBD #00B7C3 #5B5FC7 #8764B8 #CA5010 #107C10
```

## 2. Slate & Amber (light, executive)

```
bg       #F7F5F2   surface  #FFFFFF   fg  #252423
primary  #31425A   accent   #E8A33D
good     #4E7C43   bad      #C43B3B   neutral #A19F9D
track    #EDEAE4
series   #31425A #E8A33D #6B7F99 #C4B28A #4E7C43 #C43B3B
```

## 3. Forest (light, operations/finance)

```
bg       #F3F7F4   surface  #FFFFFF   fg  #1E2B23
primary  #1E6B4F   accent   #8FBC5A
good     #2E7D32   bad      #C62828   neutral #93A29A
track    #E4EEE7
series   #1E6B4F #8FBC5A #3E8E7E #C9A227 #2E7D32 #C62828
```

## 4. Berry (light, marketing/product)

```
bg       #FAF5F8   surface  #FFFFFF   fg  #2B1F29
primary  #7C2D5E   accent   #E56BA0
good     #3E7D4E   bad      #D13438   neutral #A79AA4
track    #F1E4EC
series   #7C2D5E #E56BA0 #4A3B76 #D9A441 #3E7D4E #D13438
```

## 5. Midnight (dark)

```
bg       #141A22   surface  #1D2632   fg  #E8EDF2
primary  #4EA3F1   accent   #34D3BE
good     #4CC38A   bad      #F16B6B   neutral #7A8794
track    #2A3646
series   #4EA3F1 #34D3BE #9B8AFB #F0B35E #4CC38A #F16B6B
```

## 6. Mono Blue (light, minimal, print-friendly)

```
bg       #FFFFFF   surface  #F7F9FB   fg  #1A1A1A
primary  #165A9E   accent   #165A9E
good     #2E7D32   bad      #B00020   neutral #6E6E6E
track    #E8EEF4
series   #165A9E #3E7CC0 #6A9AD2 #96B8E4 #C2D6F0 #2E7D32
```

## Mapping a palette to theme variables

Use variables with palette fallbacks so the component follows the theme when one exists:

```css
.card {
  background: var(--pbi-theme-bg-light, #FFFFFF);
  color: var(--pbi-theme-fg, #1F2937);
}
.kpi.up   { color: var(--pbi-theme-good, #107C10); }
.kpi.down { color: var(--pbi-theme-bad,  #D13438); }
.bar-fill { fill: var(--pbi-theme-color-1, #0F6CBD); }
a, .link  { color: var(--pbi-theme-hyperlink, #0F6CBD); }
```

## Design rules

- One palette per dashboard. Sentiment colors (`good/bad/neutral`) come only from the palette or theme; never a third red.
- Contrast: text on `surface` must pass roughly 4.5:1; all `fg` values above were chosen against their `surface`.
- Dark mode: use Midnight as a full system (bg + surface + fg), not dark accents on a light page.
- Categorical series order matters: assign series colors in the listed order and keep them stable across pages.
- RTL dashboards change direction, not color; do not mirror the palette.
