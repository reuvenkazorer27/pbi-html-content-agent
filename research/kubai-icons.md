# Kubai Icons - identification, license and fit (checked live 09/11/2026)

User request (10:23): "אולי תטמיע את Kubai icons ליצירת אייקונים מותאמים לkpi או תפריט צד" (maybe embed Kubai icons to create custom icons for KPIs or a side menu).

## Identification (not guessed - verified)
- The repo: https://github.com/kubai087/kubai-icons (created 03/11/2026). The site: https://icons.kubai.design/
- The licensing document that was read: https://github.com/kubai087/kubai-icons/blob/master/LICENSING.md
- MIT license for the icons: https://github.com/kubai087/kubai-icons/blob/master/LICENSE-ICONS
- License for the Skill (source-available): https://github.com/kubai087/kubai-icons/blob/master/LICENSE
- The static SVG package on npm: https://www.npmjs.com/package/kubai-icons-static
- What it is: two things in the same repo:
  1. **Icon library** - many icons (icons/) + ready-made packages (packages/), including `kubai-icons-static` on npm: fully self-contained SVG files (no JS, no external CSS), 2,871 files (including variants).
  2. **A Skill for generating new icons** in the consistent style (SKILL.md/PROMPT.md/engine.js for Claude Code).

## License - three separate licenses (LICENSING.md in the repo)
| Part | License | What it means for us |
|---|---|---|
| The icons (icons/, packages/, badges/) | **MIT** (LICENSE-ICONS) | On the user's list of approved licenses. Commercial use, distribution, modification - allowed. The copyright notice is kept with the files. Attribution not required. |
| The Skill (SKILL.md, PROMPT.md, src/, scripts/) | Kubai Icons License (source-available, not OSI) | Free use including commercial; icons created with it belong to the user without attribution. Distributing the 66 examples in src/icons.js as a standalone set is prohibited. **We do not ship the Skill in the folder** - not needed. |
| The site (site/, docs/) | All rights reserved | Not relevant. |
- The Kubai/Lumno names and logos are outside every license - we do not use the names for branding.

## Technical fit for HTML Content
- Format: self-contained static SVG. Checked directly (grep on the shipped files): no `<script>`, no `href=`, no `src=`, no external references - only `xmlns`. Suitable in principle for the **Secure** edition (inline SVG allowed).
- Internal ids are namespaced by icon name (`loS-ki-chart-line` etc.) - no collision between different icons on the same page. The same icon twice = duplicate id (renders correctly in browsers; a suffix can be added).
- Shadows/glow: declarative SVG filters (feGaussianBlur/feDropShadow). **Not tested in actual Power BI** - if they are blocked, the icon looks flat but intact. Flagged in the notes files.
- Size: 24-28px, viewBox with padding for the shadow. No font dependency.
- RTL: the selected set is symmetric/neutral; directional icons (arrows) would need horizontal mirroring if added.
- Security: no code, no network - no attack surface beyond static SVG.

## What was shipped in the folder
- `library/icons/` - 12 selected SVGs (banknote, hand-coins, coins, users, chart-line, chart-funnel, gauge, circle-alert, calendar, filter, target, clipboard-check) + LICENSE-MIT-kubai + embedding README.
- `examples/kpi-with-icon.dax` - full KPI card with an inline icon (double quotes doubled for DAX).
- Rendering proof: KPI cards with the icons in the harness (tested in a browser only, not in Power BI).

## Conclusion
The tool is verified, free, and the icons are under MIT - within the user's licensing rules. No sign-up, payment or data upload needed. The embedding was done at the level of the static icons (MIT), not at the level of the Skill (source-available) - so there is no licensing constraint at all on the folder.
