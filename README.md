<div align="center">

# PBI HTML Content Agent

**An AI agent kit that builds pixel-exact Power BI dashboards on the HTML Content visual, fitted to your data, your brand and your readers. It works left-to-right or right-to-left, adds color and motion where they earn their place, writes straight into PBIP/PBIR, checks every build automatically and versions it like code.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Power BI](https://img.shields.io/badge/Power%20BI-PBIP%20%2F%20PBIR-F2C811?logo=powerbi&logoColor=black)
![HTML Content](https://img.shields.io/badge/HTML%20Content-2.0%20Secure-0F6CBD)
![Direction](https://img.shields.io/badge/direction-LTR%20%2B%20RTL-7C3AED)
![Gates](https://img.shields.io/badge/gates-fit%20%C2%B7%20WCAG%20%C2%B7%20stress%20%C2%B7%20regression-15803D)
![Styles](https://img.shields.io/badge/styles-brand--fitted%2C%20contrast--computed-DB2777)
![Motion](https://img.shields.io/badge/motion-CSS%20keyframes%2C%20Secure--safe-0D9488)

<a href="https://github.com/reuvenkazorer27/pbi-html-content-agent/raw/main/docs/demo/ecommerce-dashboard-demo.mp4"><img src="https://github.com/reuvenkazorer27/pbi-html-content-agent/raw/main/docs/demo/demo.gif" alt="55-second demo: the agent reads a live Power BI model, lays out an executive page, writes the DAX, runs its gates, and the result in Power BI Desktop - KPI cards whose digits roll in, an exception list that keeps pulsing, every visual updating from a slicer" width="100%"></a>

<sub>From one prompt to a verified page: live model → layout → DAX → gates → Power BI Desktop → motion. Everything except the three slicers is HTML Content (Secure edition); sample data. <a href="https://github.com/reuvenkazorer27/pbi-html-content-agent/raw/main/docs/demo/ecommerce-dashboard-demo.mp4"><b>▶ Full-quality video (MP4, 55 s)</b></a></sub>

</div>

---

## Install

**Claude Code** (v2.1.275 or later), in any session:

```text
/plugin install pbi-html-content-agent --marketplace reuvenkazorer27/pbi-html-content-agent
```

On older versions, run `/plugin marketplace add reuvenkazorer27/pbi-html-content-agent` and then `/plugin install pbi-html-content-agent@pbi-html-content-agent`.

- **What you get:** the whole kit (instructions, references, the pipeline) and 8 skills. The entry skill, `pbi-html-dashboard`, starts any dashboard request.
- **Update:** run `/plugin marketplace update pbi-html-content-agent`, then `/plugin update pbi-html-content-agent@pbi-html-content-agent`.
- **No GitHub SSH key:** set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` before you add the marketplace.

**Any agent (Cursor, Codex, Claude Code, ...), set up next to your report in one step.** Run this in the folder that holds your `.pbip`:

```bash
npx pbi-html-content-agent init
```

It does the following:
- copies the kit next to the report and sets up `_build/` with a backup copy;
- asks which table, page and style to use, and writes `pipeline.json`;
- leaves a pointer to `AGENTS.md` for your agent;
- checks Python, Node, Edge and Power BI Desktop.

`npx pbi-html-content-agent doctor` runs only the checks. To get just the files, use `npx degit reuvenkazorer27/pbi-html-content-agent pbi-kit` or `git clone`.

**Then ask in plain language**, from the folder that holds your `.pbip`. For example: *"Set up the kit next to Sales.pbip and build an executive page with a KPI row, a filter panel and a regional breakdown, in our brand blue #0E7490."* The agent copies the pipeline next to your report, asks for what only you know (which table, which page, brand colors), and runs the gates before it writes anything.

## What it is

The kit is a set of instructions, tools and gates. It is not a template. An agent (Claude Code, Cursor, ...) reads [`AGENTS.md`](AGENTS.md) and then builds a dashboard for **your** model: it asks what only you know (tables, the questions the page must answer, brand colors, light or dark) and builds from gated card builders. Nothing is written into the report until the gates pass on your live data.

Everything on the page is HTML Content except the slicers: header, KPI cards (each with an icon), charts, tables and matrices. Native buttons are added only when a report needs several pages.

| Problem we hit in Desktop | What the kit does about it |
| --- | --- |
| Cards clipped at the bottom, titles wrapping | Writes **padding 0** on every visual and runs an **exact-size fit check** with 8px slack on every build |
| A card that is half empty, especially after a filter | The **fill gate** catches it. Rows stretch, and short lists show what the selection is made of |
| Hebrew titles left-aligned despite `dir="rtl"` | Direction-aware `direction` + `text-align` on every card root, plus one setting to flip the whole layout |
| 12px text unreadable after Fit-to-page | A central **type scale** for 1920×1080 |
| Colorful dashboards that look cheap, with KPI cards and charts that look like two products | **Styles**: one card material, one color mechanism, every in-card color computed for contrast (see [Colorful styles](#colorful-styles)) |
| "Looks fine" until a filter empties a list | **Stress scenarios** re-render every card under several filter states, including an empty selection |
| A change that breaks something unnoticed | A **byte-level regression gate** plus **versions with revert**, committed and tagged in git |
| "The animation doesn't run" | CSS-only **motion** that also runs in the Secure edition, gates that measure the resting layout, and a recording of Desktop itself (see [Motion](#motion)) |

## What you get

- **Gated card builders** ([`components.py`](tools/pbip-html-pipeline/components.py)): KPI card, data table, waterfall, heat matrix, lift bars, small multiples, scatter, treemap and decomposition tree. Each is parameterized by your tables, columns and measures, and each one's DAX is evaluated on a live model and passed the fit, contrast and stress gates before it ships.
- **Colorful styles** ([`styles.py`](tools/pbip-html-pipeline/styles.py), [skill](skills/colorful-styles/SKILL.md)): a style is generated from your brand and fitted to your cards' roles.
- **Motion** ([skill](skills/motion/SKILL.md)): every builder takes `motion=` and `alert=`. With motion off, the output is byte-identical.
- **LTR and RTL**: `DASH_DIR=ltr|rtl` flips the layout. RTL gets bidi isolation of numbers, currency and dates.
- **UI language**: `DASH_LANG` translates display strings and protects data values and model names, so filters never break.
- **Direct PBIR authoring**: TMDL measures and `visual.json` are written by script, and Desktop picks them up with *Apply external changes*.
- **Optional Microsoft tools**: the Power BI Modeling MCP, the Desktop Bridge and the report-authoring CLI are used when they are installed ([`build-workflow.md`](reference/build-workflow.md) §1b).
- **A static component library** ([`library/`](library/README.md)): bullet, IBCS variance, dumbbell, waffle, milestone timeline, org strip and more, each classified against the built-in visuals.
- **Honest by design**: no fake buttons, no promises the Secure sandbox cannot keep, and every claim labeled as measured or doc-based.

## Colorful styles

Two rules make a colorful dashboard look premium rather than cheap. First, **KPI cards and analysis cards are one material**: the same surface, border, radius, title and icon chip. Second, **color reaches every card through one mechanism**, with strong saturation kept to data marks, icons and at most one hero card. The engine enforces both, and computes every text and data color inside a card for WCAG contrast on that card.

```python
make_style(brand="#0E7490", accent="#F59E0B", mode="light" | "dark",
           mechanism="bar" | "start-bar" | "tint" | "tint-strong" | "chip", hero=True)
```

- **Choose a style.** Put it in `pipeline.json` (`"style": "accent"` or a `make_style()` dict), or pass it per build with `DASH_STYLE=<preset>` or `DASH_STYLE='{"brand": "#0E7490", "mode": "dark"}'`.
- **Give each card a role:** `neutral`, `hero`, `brand`, `good` / `bad` / `warn` or `c1`..`c6`. A KPI and the chart about the same category share a role, so they share a color.
- **Check a style without a model:** `python -I style_check.py` checks every preset and 800 generated styles.
- **Presets:** eight worked examples. `accent` (the default) has white cards with a top bar and one hero. The others are `tonal`, `midnight`, `sand`, `ocean`, `duotone`, `sunset` and `mint`; the table is in [`design-system.md`](reference/design-system.md) §4.
- **Legacy palettes** still build with `DASH_PALETTE`.

## Motion

Motion runs inside HTML Content with no script, so it also works in the certified **Secure** edition and in the Power BI Service. The kit animates only what earns it:
- **The change**: a KPI rolls from last period's value, and table bars move from their previous value.
- **An exception**: items that break a threshold pulse a red ring twice and stop, within 5 s (WCAG 2.2.2).
- **Freshness**: "Updated 5 min ago", or an amber "Stale".
- **A short entrance** when the view changes.

Decoration is left out on purpose: sheens, breathing, endless loops and bouncy bars.

| Kind | When it plays | Example |
| --- | --- | --- |
| **Entrance** | every render: page open, slicer change, Refresh | KPI digits roll to the value, bars grow, the line draws in ([`kpi-card-motion.dax`](library/components/kpi-card-motion.dax)) |
| **Alert** | on every render, twice, then still | rows at a loss pulse a red ring ([`watch-list-motion.dax`](library/components/watch-list-motion.dax)) |

**Every builder** takes `motion=True` and `alert="<DAX condition>"`. On top of that, `kpi_card` takes `prev=`, `updated=` and `stale_after=`, and `data_table` bars take `"prev"`.

Two traps were measured in Desktop. With Windows *Animation effects* turned off, Desktop reports `prefers-reduced-motion: reduce`. And after *Apply external changes*, visuals keep their old HTML until you press **Refresh**.

[`tools/motion-bake/`](tools/motion-bake/) is experimental: it bakes a motion2code SVG + GSAP loop into CSS keyframes. It is headless-verified only and has not been run in Power BI.

## Quick start

1. Install the kit (see [Install](#install)), or copy this folder anywhere your agent can read it.
2. In Claude Code the `pbi-html-dashboard` skill starts on its own. Other agents: tell them to read `AGENTS.md` first.
3. Ask in plain language, for example: *"Build an RTL portfolio dashboard on table X with a KPI row, a right filter panel and a timeline, in our brand blue."*

To drive the pipeline yourself:
1. Copy `tools/pbip-html-pipeline/` next to the PBIP as `_build/`.
2. Copy `pipeline.example.json` to `pipeline.json` and fill in your PBIP name, host table, page, backup folder and style.
3. Write your measures and `LAYOUT` in `measures.py`, starting from `measures_example_projects.py`.
4. Open the PBIP in Power BI Desktop and run the loop:

```bash
python -I gen_query.py q_all.dax                                     # define + evaluate every HTML measure
powershell -File runq.ps1 -QueryFile q_all.dax -OutFile r_all.json   # run it on the open Desktop model
python -I regress.py r_all.json                                      # only intended cards changed?
python -I gen_preview.py r_all.json preview.html                     # exact-size preview
node fitcheck.mjs preview.html --shot full.png                       # GATE: FIT OK + CONTRAST OK (+ no empty band)
python -I stress.py                                                  # GATE: filter scenarios, including an empty selection
python -I versions.py snapshot "what changed" --fit "FIT OK" --results r_all.json --shot full.png
python -I gen_pbip.py                                                # write TMDL + visual.json
```

Then, in Desktop: **Apply external changes → Home ▸ Refresh**.

Requirements: **Windows** with Power BI Desktop (PBIP enabled), Python 3, Node 22+ and Microsoft Edge. No npm or pip packages are needed. Details: [`tools/pbip-html-pipeline/README.md`](tools/pbip-html-pipeline/README.md).

## Repository map

| Path | What is there |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | The agent's brief: what it is built on, the contract, the honesty rules, the working method |
| [`reference/`](reference/) | `design-system.md` (measured rules), `build-workflow.md` (Desktop, gates, git), `capabilities.md`, `canvas-and-layout.md`, `pbir-visual-json.md` |
| [`skills/`](skills/) | pbi-html-dashboard (start here), composite-dashboard, dashboard-shell, html-slicers-filters, navigation-header-menu, rtl-hebrew, colorful-styles, motion |
| [`.claude-plugin/`](.claude-plugin/) | Claude Code plugin + marketplace manifests |
| [`tools/pbip-html-pipeline/`](tools/pbip-html-pipeline/) | Build, gate, version and write: builders, styles, gates, writer, two worked examples |
| [`tools/motion-bake/`](tools/motion-bake/) | Experimental motion2code → CSS keyframes |
| [`library/`](library/README.md) | Static components (`.dax`), icons (Kubai, MIT), fullscreen shell |
| [`checklists/validation.md`](checklists/validation.md) | What to check in Desktop, the Service, mobile and export |
| [`examples/`](examples/) · [`research/`](research/) · [`SOURCES.md`](SOURCES.md) · [`ROADMAP.md`](ROADMAP.md) | Worked examples, demand research, dated sources, what is next |

## Visual editions

- **HTML Content (Regular)**: the most flexible edition, with external images and, from 2.0, `<script>`. It is uncertified, so it is excluded from export to PDF/PowerPoint and from subscriptions.
- **HTML Content Secure** (formerly "lite"): certified, sanitized, with no scripts and no external resources. It is included in export. **The agent defaults to Secure.**

## Verification status

- **Measured in Power BI Desktop (9-10 Nov 2026):**
  - the fit contract, the pipeline and the rules in `reference/`, on a 1920×1080 Hebrew RTL dashboard (Secure edition);
  - the LTR/English build and the builders used by example 2;
  - the Microsoft tools route;
  - the two motion components (Secure edition), seen frame by frame and in a Desktop recording.
- **Gated on a live model, not yet confirmed in Desktop:**
  - `waterfall`, `scatter`, `decomp_static`;
  - the colorful styles on the reference build (RTL Hebrew): all eight presets passed fit and contrast, and `accent`, `sand` and `tonal` passed every stress scenario. These runs were on the engine before its final refactor into `styles.py`; after the refactor, `accent` passed fit and contrast again. The full stress run on the final code (every preset, LTR English) is still to do;
  - `style_check.py`: contrast over every preset and 800 generated styles (no model needed);
  - under a style, all builders with motion and alerts resolve every token. Motion off stays byte-identical to the previous builders in the legacy palettes.
- **Doc-based, not yet run in Desktop:** the static components in `library/` and the examples in `examples/`.

  Before production use, run `checklists/validation.md`.

## Contributing

Through pull requests only; see [`CONTRIBUTING.md`](CONTRIBUTING.md). Every change passes `regress.py`, `fitcheck.mjs` and `stress.py`, and a rule measured in Desktop that holds for everyone goes into the one document it belongs to.

## License

[MIT](LICENSE) © 2026 Reuven Kazorer.

Third-party: the **HTML Content** custom visual is a separate free, open-source project by Daniel Marsh-Patrick ([html-content.com](https://html-content.com), MIT) and is not included here. Icons in `library/icons/` are from Kubai Icons (MIT, see `library/icons/LICENSE-MIT-kubai`). Power BI is a trademark of Microsoft.
