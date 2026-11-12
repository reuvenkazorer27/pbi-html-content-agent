# Contributing to the kit

Work happens through pull requests: one branch per change, a review on the PR, merge through the PR - never directly to `main`. Every change to the pipeline or an example must pass `regress.py`, `fitcheck.mjs` and `stress.py` (and `style_check.py` for color changes). Never commit keys, env files, pulled data or `.pbi` caches (see `.gitignore` and `reference/build-workflow.md`).

## Releasing

Users get a change only when the version changes, so bump `version` in both `package.json` and `.claude-plugin/plugin.json` (same number) after a change is merged.
- Claude Code users pick it up through `/plugin update`.
- For npm, run `npm publish` from `main`. Check the package first with `npm pack --dry-run`: no `__pycache__`, no video, about 200 KB.

## Keeping the kit right

When you measure something new in Desktop that is true for everyone (not specific to one model or one person), add it as a rule to the document it belongs to - `reference/design-system.md`, `reference/build-workflow.md`, `reference/pbir-visual-json.md`, a skill or the checklist - with the reason and how to verify it. One rule lives in one place; other files link to it. Do not keep a diary of sessions, names or chat quotes in this kit.

**The kit stays general: improvements only, no reports.** A PR carries the improvement itself, written into the file where it belongs (code, an existing reference page, a skill, the checklist). Never commit test reports, dashboards or measures built for one user's model, screenshots of a run, or a new Markdown file that only records what happened in a session - those stay with the project they were made for. Prefer extending an existing page over adding a new `.md` file; a new file needs a reason that no existing page can hold the content.

## Adding a component

- Demand before build. Before adding a component to the library, find evidence that users actually ask for it (Microsoft Fabric Ideas, r/PowerBI, community blogs; AppSource download leaderboards only as a labeled proxy) - not only that the catalog lacks it. Record the evidence, the native status, the HTML feasibility and the build/skip decision in `research/user-demand.md`. Note that some teams avoid custom visuals for maintainability reasons; the library answers this with few, strong, documented components that run in the certified Secure edition.
- Static path before "needs JS". Before classifying a visual as requiring the Regular edition, check the static route first: DAX-computed SVG coordinates, absolute-positioned divs, and flex/grid compositions cover more than expected (timelines, fixed-depth hierarchies, connectors). "Needs JS" must be justified by what actually cannot be precomputed in DAX (e.g. force-directed or flow layout over arbitrary data).

**Claim discipline (load-bearing).** Never write "no built-in equivalent" from the overview catalog alone. Before such a claim, open the feature-owning Microsoft Learn page and check the actual capability, then classify honestly:
- **native absent** - no built-in visual does it (e.g. bullet chart: SQLBI shows it must be hand-assembled from core bar charts; IBCS variance columns; dumbbell; lollipop; waffle; operational exception queues; connected stage trackers).
- **native workaround exists** - achievable with effort in built-ins, but not in this form (calendar heatmap as a matrix with conditional-formatting backgrounds; a donut coerced into a progress ring; a card with a dynamic-text measure printing filter state).
- **native exists, HTML composes richer** - the capability is real and shipped; HTML adds composition on top (table/matrix sparklines are native, in preview as of 9 Nov 2026 - the scorecard adds a full per-row composition; the modern Card visual has reference labels and images but no embedded sparkline; the Narrative visual writes dynamic text but cannot inline a chart, styled tokens, or precise bidi control; data alerts notify, they do not render a designed in-canvas banner).

Date every check in the deliverable ("verified 9 Nov 2026") - Microsoft ships new built-in visuals often, and a gap that was real last year may be native today. The dated source list lives in `SOURCES.md`.
