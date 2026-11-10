# Build workflow - iterating safely on a PBIP in Power BI Desktop

How to build, test, version and ship a dashboard with this kit without losing work, corrupting the report or leaving the machine in a bad state. Measured in Power BI Desktop (PBIP/PBIR, Windows).

## 1. Iterating while Desktop is open

- Write the files, then click **Apply external changes** in Desktop's banner. Do not close Desktop between iterations. The banner can be hidden behind the canvas until the window repaints - take a screenshot to find it.
- After Apply the **model** is updated, but visuals keep **cached query results**: click Home → **Refresh** (or switch page) before judging the render. To check whether the model has the new version, evaluate the measure text (e.g. DAX `SEARCH` for a new string).
- Save in Desktop **before** you write files; after writing, do **not** save from Desktop until you have applied the external changes - a save writes Desktop's in-memory state over your files.
- If Desktop must be closed, close it **before** writing - it saves on close and can overwrite your files.
- One Desktop window per project. Two windows on the same PBIP each save their own state and overwrite each other.
- A project whose folder was moved fails Apply with `ArtifactShortcut: Required artifact is missing`: the open window still points to the old path - reopen the `.pbip` from its new location.
- An invisible dialog (one that opens without rendering) blocks every click. Find it in the window's accessibility tree (`FloatingDialog`, `desktopDialogHost`) and answer it; do not kill the app. The usual one after Apply is **"Overwrite your unsaved edits"** - an Apply that seems to do nothing is waiting on it. It discards the user's unsaved work in Desktop, so ask the user before confirming.
- If the agent cannot click in Desktop itself, ask the user to Apply external changes → Refresh and to send a screenshot of **every** page that changed - never infer one page's render from another's.
- Never force-kill Desktop or stop a Power BI process you did not start - a windowless one may be the user's own reopen in progress. Ask first.

## 1b. With Power BI's own tools (optional, measured 10 Nov 2026)

When they are available the loop needs no clicks and no manual screenshots. Each tool has one job; the file route stays the fallback.

| Step | Tool | What it does | Measured |
| --- | --- | --- | --- |
| Find the window | `bridge.py status` (Desktop Bridge pipe) or the Modeling MCP `ListLocalInstances` | pid, open file, unsaved state; the MCP names each model by its window title, so no port guessing | both see every open Desktop |
| Measures into the live model | **Power BI Modeling MCP** `measure_operations` Create/Update | applied at once, no Apply, no Refresh; a batch is one transaction | caught a measure named like a column (`Units`) and rolled the whole batch back - the file route only fails inside Desktop |
| Report files into Desktop | `bridge.py reload` (`file.reload/v1`) | reloads the PBIR from disk, ~10s, no click | **does not reload the model**: TMDL written to disk stays out of the live model (cards show "Something's wrong with one or more fields") - push measures with the MCP first, or use Apply external changes |
| Validate PBIR | `powerbi-report-author validate` (`@microsoft/powerbi-report-authoring-cli`, Node) | schema + layout diagnostics | found a real bug: a new page is 1280×720 unless the writer sets 1920×1080. Its slicer-height error (40 < 48px) is a false positive when padding is 0 - Desktop rendered the 40px slicer correctly; Desktop wins |
| Screenshot | `bridge.py shot <page-id>` (`report.snapshot.capture/v1`) | real Desktop render as PNG, ~8s | right after a reload the HTML visuals are still empty - wait (`--settle`, default 15s) |
| Gate the HTML | `runq.ps1` → preview → `fitcheck.mjs` (unchanged) | evaluates every card to files | keep it: the MCP's DAX results come back inline, and HTML cards are kilobytes each |

Safety with the Modeling MCP:
- Commit the TMDL (git) before the first MCP edit - the MCP changes the live model, and the commit is your way back.
- Never run it with `--skipconfirmation`; against a published model work in a dedicated development workspace, never in production.
- A local MCP server runs with all of your permissions. Turn off write tools you do not need, and keep secrets in the client config only as references (`"${TOKEN}"`), never as values.

Reach: besides Desktop, the Modeling MCP connects to a model in the Power BI service / Fabric (`ConnectFabric`) and to TMDL folders on disk; Microsoft also offers a remote authoring MCP endpoint for service models (preview, needs tenant approval).

Costs and limits:
- The MCP takes every expression inline in the call. A 20-card dashboard is ~27K characters per full push - push only the cards that changed, and keep the TMDL on disk in sync (`gen_pbip.py`) so the PBIP stays the source of truth.
- Writing TMDL while the live model already has the same measures still raises Desktop's "Apply external changes" banner; `bridge.py reload` clears it once disk and model agree.
- The bridge needs Options › Preview features › *external tool access*. `bridge.py` is plain Python (no Node). The `powerbi-desktop open` CLI does not find a Microsoft Store install (`DESKTOP_EXE_NOT_FOUND`) - open the `.pbip` normally and wait for `bridge.py status`.
- One request per pipe connection; a busy pipe answers "not found" for a moment - retry (bridge.py does).
- One operation at a time per Desktop window: a reload and a screenshot sent together come back `Cancelled`. Run them in sequence.

## 2. Writing PBIP files

- Generate TMDL measures and `visual.json` files from one source of truth (the pipeline's `measures.py` + `pipeline.json`), rebuilt from a clean backup copy on every run so reruns are idempotent.
- In TMDL a line starting with `///` is the **description** of the next object - never use it as a marker around generated code.
- DAX `VAR` names must be ASCII identifiers (a Hebrew variable name is a syntax error); non-Latin text is fine in measure, table and column names and in strings.
- Register the AppSource visual in `report.json` (`publicCustomVisuals`) so Desktop fetches it on open.
- Write the page canvas (`width`/`height` in `page.json`) with the layout: a new or scaffolded page is 1280×720 and clips a 1920×1080 layout.
- **Never place a visual on top of another.** `layout_check.py` (run by `gen_pbip.py`, which refuses to write on failure) checks that every visual is on the page, HTML visuals do not overlap (a full-page background layer is the one exception), and each slicer sits inside exactly one HTML panel. Adding a region means re-laying out or a new page, not stacking. Navigation buttons link to the pages' actual names.
- DAX style: `VAR` for every reused value, `DIVIDE` instead of `/`, a filter argument as `KEEPFILTERS ( col = value )` when the user's selection on that column must still apply (a slicer); `FILTER ( ALL ( ... ) )` / `REMOVEFILTERS` only when you mean to ignore it - they return different numbers under a slicer.

## 3. Testing before writing

- Evaluate every HTML measure against the open model before writing anything: `runq.ps1` loads `Microsoft.PowerBI.AdomdClient.dll` from Desktop's own folder, finds the model port in `...\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt` (UTF-16, newest file) and runs a `DEFINE MEASURE ... EVALUATE ROW(...)` query. The real HTML it returns feeds the preview.
- Gates, in order: `regress.py` (only the intended cards changed), `fitcheck.mjs` (fit + WCAG contrast on the exact-size preview), `stress.py` (filter scenarios). Verify that a scenario really filters - a gate that tests nothing passes everything.
- Headless browser checks must clean up after themselves. `child.kill()` stops only the browser launcher; Edge's GPU/renderer children outlive it and accumulate into hundreds of processes, which then make later checks fail at random. Wait for real readiness (page and every card rendered) instead of a fixed sleep, close the browser over the DevTools protocol (`Browser.close`), kill anything left on the run's temporary profile, and delete the profile. Check: a process count before and after a run must match.
- Color changes: a JPEG zoom cannot tell close shades apart. Verify from a PNG of the Desktop window by reading pixels in the element's box.

### The review loop and what "done" means

`edit → gates → write → into Desktop (Apply or bridge) → screenshot every changed page → review against checklists/validation.md → fix → review → report`

- **Fix budget: one round.** The second review only checks and reports what is still broken - it does not start another fix loop.
- **A page is done only after a screenshot of it was checked.** If Desktop is not available, say the Desktop check was **skipped** - never report it as checked. Report pages by display name.
- **When a validator and Desktop disagree, Desktop is right.** Fix the source (TMDL, PBIR, theme, measure) - never edit a screenshot or tune to the validator.

## 4. Versions and revert

- End every iteration with `versions.py snapshot "what changed"`: report and model definitions, build sources, the real HTML of every card and a screenshot. `versions.py revert vN` restores a version and first snapshots the current state, so a revert is itself undoable. Then Apply external changes → Refresh.
- Refactors are proven safe by `regress.py`: the HTML of every card must be byte-identical to the previous version. Intended changes list exactly which cards changed.

## 5. Git

- Make the dashboard project a git repo. `versions.py` then commits and tags `vNNN` on every snapshot and commits every revert; the zip snapshots stay as a local backup (ignored by git).
- Recommended for shared or long-lived dashboards: once a basic version exists, make each change on its own branch and merge it through a pull request with a review. (Changes to this kit itself always follow that flow - see the README's Contributing section.)
- `.gitignore` must exclude secrets and local state: env/key files, pulled data, `**/.pbi/cache.abf`, `**/.pbi/localSettings.json`, build scratch. Before the first commit, list tracked files and check that none of those appear.
- Ignore by prefix, not by extension: a broad `*.dax` rule meant for scratch queries silently drops a whole component library. Compare the tracked file count with the files on disk before pushing.
- Scan for secrets (API keys, tokens, `Bearer` strings) before every push.
