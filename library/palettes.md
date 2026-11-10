# Palettes - where colors come from

Colors are not hand-picked here any more. They come from code, with contrast computed:

- **Styles** - `tools/pbip-html-pipeline/styles.py` (default `accent`; `make_style()` builds one from the user's brand). See `skills/colorful-styles/SKILL.md` and `reference/design-system.md` §4.
- **Legacy palettes** - `tools/pbip-html-pipeline/palette.py` (`ocean`, `midnight`, `berry`, `vivid`, presets, `DASH_PRIMARY` brand derivation), selected with `DASH_PALETTE`.
- **Report theme** - prefer it when the report has a governed theme: the `--pbi-theme-*` variables keep HTML visuals in sync with the theme and high-contrast mode (`reference/capabilities.md`); `python -I palette.py theme out.json` writes the active palette as a theme so native visuals match.

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
