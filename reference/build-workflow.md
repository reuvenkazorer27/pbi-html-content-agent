# Build workflow - iterating safely on a PBIP in Power BI Desktop

How to build, test, version and ship a dashboard with this kit without losing work, corrupting the report or leaving the machine in a bad state. Measured in Power BI Desktop (PBIP/PBIR, Windows).

## 0. No PBIP or no model yet (measured 10 Nov 2026)

Creating the model is not the kit's job, but the route is short. With the **Power BI Modeling MCP** only one GUI step is left:

1. Desktop: Home → **Blank report** → File → Save as → *Power BI project files (\*.pbip)*, in its own folder (make it its own git repo - §5).
2. Modeling MCP on the open window (`ListLocalInstances` names it by window title): `table_operations` Create with an M partition (e.g. `Excel.Workbook(File.Contents(...))`) **and every column declared** (`sourceColumn`, `dataType` - the MCP does not infer columns from M), `relationship_operations` Create, `model_operations` RefreshWithXMLA (Full), `table_operations` MarkAsDateTable. Calculated columns: `column_operations` Create, then a `Calculate` refresh. Desktop shows the tables at once, no Apply.
3. **Save in Desktop (Ctrl+S)** - until then the TMDL on disk is still the empty model.
4. Then `npx pbi-html-content-agent init`.

The M path is absolute: a moved data file breaks refresh. Data that is already loaded (the user imported it in Desktop) needs none of this.

**Star schemas.** The measures live on one host table (`pipeline.json` `table`), but the columns they break down by can come from any table: every builder column argument takes a full reference (`'Products'[Name]`, `'Calendar'[Date]`), a slicer in `SLICERS` takes `'Table'[Column]`, `lift_bars` counts the rows of `fact=` (default: `table`), and `data_table` leaves out keys whose sort value is BLANK - so a dimension key follows a filter on the fact table and the empty state shows. Calculated `RELATED(...)` columns on the fact table are no longer needed for this.

## 1. Iterating while Desktop is open

- Write the files, then click **Apply external changes** in Desktop's banner. Do not close Desktop between iterations. The banner can be hidden behind the canvas until the window repaints - take a screenshot to find it.
- **The banner needs a saved Desktop.** `gen_pbip.py` warns when `bridge.py status` reports `hasUnsavedChanges` for the project. Measured: with no unsaved changes the banner appeared after `gen_pbip.py`; with unsaved changes (e.g. after a Desktop refresh) no banner came. The flag can also stay `true` - after Modeling MCP edits even through Ctrl+S, and right after opening a PBIP. Then either push the measures with the Modeling MCP and `bridge.py reload` (§1b), or close Desktop with **Don't save** (only a window you opened - ask the user otherwise) and reopen the `.pbip`.
- **The first write into a report that never had an HTML Content visual** can show "To see this custom visual, add it to this report first" on every card after Apply, although `report.json` registers it: Desktop fetches the AppSource visual only when it opens the report. Measured: a reload did not fetch the visual; close Desktop with Don't save (only a window you opened - ask otherwise) and reopen the `.pbip` once. Later writes are fine. A screenshot of that state is still "stable" - check it before you call the page done.
- **Desktop can stay windowless after opening a `.pbip`.** Observed 3 times in 8 opens on 12 Nov 2026 (each right after the previous Desktop window was closed): the process runs, shows no window for minutes, its model engine has no database, and the bridge answers `OperationInProgress` - once with no bridge request sent at all, so the bridge is not the cause. Wait about 2 minutes for the report title; if none, close that window (only one you opened - ask otherwise) and open the `.pbip` again. `bridge.py` copes with it: it does not contact a Desktop until a window shows a report - its title is the file name alone, not "<blank> - Power BI Desktop" (any UI language) - it reads titles without sending the window a message (a precaution: a first status call against an opening Desktop once took 3 minutes and once 66 s, cause not established), and every request times out and cancels its pipe read instead of hanging.
- **A copy of a PBIP without `.pbi/cache.abf`** (copies should not carry it) opens with "Some of the tables have incomplete or no data": run a Full refresh (Modeling MCP `RefreshWithXMLA` Full, or Home → Refresh) before judging the page - right after opening, before any `bridge.py reload`: a Full refresh sent right after a reload left Desktop not responding for 30 minutes (measured once). After a reload, `Calculate` is enough.
- **After opening a PBIP the canvas can stay blank for up to a minute** while the HTML Content visual loads (measured 30-60 s). It is not a failure: wait for `bridge.py status`, then `bridge.py shot` (it retries until the page has rendered, including `PrintMetadataUnavailable` before the first render).
- After Apply the **model** is updated, but visuals keep **cached query results**: click Home → **Refresh** (or switch page) before judging the render. To check whether the model has the new version, evaluate the measure text (e.g. DAX `SEARCH` for a new string).
- Save in Desktop **before** you write files; after writing, do **not** save from Desktop until you have applied the external changes - a save writes Desktop's in-memory state over your files.
- If Desktop must be closed, close it **before** writing - it saves on close and can overwrite your files.
- One Desktop window per project. Two windows on the same PBIP each save their own state and overwrite each other.
- A project whose folder was moved fails Apply with `ArtifactShortcut: Required artifact is missing`: the open window still points to the old path - reopen the `.pbip` from its new location.
- An invisible dialog (one that opens without rendering) blocks every click. Find it in the window's accessibility tree (`FloatingDialog`, `desktopDialogHost`) and answer it; do not kill the app. The usual one after Apply is **"Overwrite your unsaved edits"** - an Apply that seems to do nothing is waiting on it. It discards the user's unsaved work in Desktop, so ask the user before confirming.
- If the agent cannot click in Desktop itself, ask the user to Apply external changes → Refresh and to send a screenshot of **every** page that changed - never infer one page's render from another's.
- Never force-kill Desktop or stop a Power BI process you did not start - a windowless one may be the user's own reopen in progress. Ask first.

## 1b. With Power BI's own tools (optional, measured 10 Nov 2026)

Use them first: what Power BI's own tools can do (model, measures, refresh, loading the files into Desktop) goes through them, and the kit decides what to build and gates it. When they are available the loop needs no clicks and no manual screenshots. Each tool has one job; the file route stays the fallback.

**Preferred loop (measured 11 Nov 2026, no click):** `gen_pbip.py` writes TMDL + PBIR (and runs `powerbi-report-author validate` when the CLI is on PATH: a verdict, the known false positive `PBIR_SLICER_HEIGHT_BELOW_FLOOR` ignored, an unregistered visual flagged as `VISUAL_TYPE_UNKNOWN`) → load the report **and the model** from disk into the open Desktop: `powerbi-report-author preview <project folder> --host desktop --reload-with-model` (Microsoft's `@microsoft/powerbi-report-authoring-cli`, ~4 s) or, without the CLI, `bridge.py reload` (~15 s; it sends `reloadModelDefinition: true`) - no banner, no Apply, no DAX passed inline → Modeling MCP `model_operations` RefreshWithXMLA `Calculate` (~2 s; without it the cards keep their cached results - measured) → screenshot: `powerbi-report-author preview ... --screenshot --all-pages` (a separate call, never combined with the reload) or `bridge.py shot`. Right after a reload or Calculate the CLI can answer `HOST_UNAVAILABLE ... no open instance has this report's folder open` (marked not retryable): wait 3-5 s and retry once - it succeeded on the retry. Writing to the PBIP to Desktop screenshot took ~40 s this way (vs ~14 min with Apply, reopen and clicks).

| Step | Tool | What it does | Measured |
| --- | --- | --- | --- |
| Find the window | `bridge.py status` (Desktop Bridge pipe) or the Modeling MCP `ListLocalInstances` | pid, open file, unsaved state; the MCP names each model by its window title, so no port guessing | both see every open Desktop |
| Measures into the live model | **Power BI Modeling MCP** `measure_operations` Create/Update - **all changed measures in one call** (`definitions` is a list) | applied at once, no Apply, no Refresh; a batch is one transaction | caught a measure named like a column (`Units`) and rolled the whole batch back - the file route only fails inside Desktop |
| Report and model into Desktop | `bridge.py reload` (`file.reload/v1` with `reloadModelDefinition: true`) | reloads the PBIR **and the TMDL** from disk, ~15 s, no click (measured 11 Nov 2026); `--report-only` reloads the PBIR alone | then MCP `Calculate` (the cards show cached results until then); warns when Desktop has unsaved changes |
| Validate PBIR | `powerbi-report-author validate` (`@microsoft/powerbi-report-authoring-cli`, Node) | schema + layout diagnostics | found a real bug: a new page is 1280×720 unless the writer sets 1920×1080. Its slicer-height error (40 < 48px) is a false positive when padding is 0 - Desktop rendered the 40px slicer correctly; Desktop wins |
| Screenshot | `bridge.py shot <page-id>` (`report.snapshot.capture/v1`) | real Desktop render as PNG, ~8s | right after a reload the bridge first answers `CaptureMetadataNotReady` (retryable), then returns empty cards (an empty capture was ~15 KB, the rendered page ~200 KB), and a fixed 15s wait was not always enough - `reload` waits until the capture has grown and held still, and `shot` until it is stable |
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
- `gen_pbip.py` rebuilds the host table's `.tmdl` from the backup copy (`backup_dir`) on every run. When the live TMDL has a column, partition or hierarchy the backup does not (a model change after `init`, e.g. a calculated column added with the Modeling MCP and saved in Desktop), it writes nothing and says so; save in Desktop and run `python -I gen_pbip.py --refresh-backup`, which copies the live table into the backup without the generated measures.
- DAX `VAR` names must be ASCII identifiers (a Hebrew variable name is a syntax error); non-Latin text is fine in measure, table and column names and in strings.
- Register the AppSource visual in `report.json` (`publicCustomVisuals`) so Desktop fetches it on open.
- Write the page canvas (`width`/`height` in `page.json`) with the layout: a new or scaffolded page is 1280×720 and clips a 1920×1080 layout.
- **Never place a visual on top of another.** `layout_check.py` (run by `gen_pbip.py`, which refuses to write on failure) checks that every visual is on the page, HTML visuals do not overlap (a full-page background layer is the one exception), and each slicer sits inside exactly one HTML panel. Adding a region means re-laying out or a new page, not stacking. Navigation buttons link to the pages' actual names.
- DAX style: `VAR` for every reused value, `DIVIDE` instead of `/`, a filter argument as `KEEPFILTERS ( col = value )` when the user's selection on that column must still apply (a slicer); `FILTER ( ALL ( ... ) )` / `REMOVEFILTERS` only when you mean to ignore it - they return different numbers under a slicer.

## 3. Testing before writing

- **Motion** (`skills/motion/SKILL.md`): freeze frames with `motion_frames.mjs` (pauses every animation at exact times - deterministic), then after Apply + **Refresh** record the Desktop window with `burst.ps1` (Desktop must be the front window: the burst captures the screen). An entrance is checked during a filter change, a loop with no interaction at all.

- **Several Desktop models open:** `runq.ps1` without `-Port` uses the newest model where the query runs - a query that fails on yours can silently run on another window with the same tables. Pin the model: `runq.ps1 -Port <port>` and `"port"` in `pipeline.json` (or `DASH_PORT`) for `stress.py`; the Modeling MCP's `ListLocalInstances` lists each window's port.
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

- Make the dashboard project **its own** git repo (`git init` in the project folder). `versions.py` then commits the project folder and tags `vNNN` on every snapshot and commits every revert. The zip snapshots (`_versions/*.zip`) and Python caches are never committed - they stay a local backup. Inside a parent repo `versions.py` does not use git at all (zip-only, with a note), so it can never commit someone else's work, and it never moves an existing tag.
- Recommended for shared or long-lived dashboards: once a basic version exists, make each change on its own branch and merge it through a pull request with a review. (Changes to this kit itself always follow that flow - see the README's Contributing section.)
- `.gitignore` must exclude secrets and local state: env/key files, pulled data, `**/.pbi/cache.abf`, `**/.pbi/localSettings.json`, build scratch. Before the first commit, list tracked files and check that none of those appear.
- Ignore by prefix, not by extension: a broad `*.dax` rule meant for scratch queries silently drops a whole component library. Compare the tracked file count with the files on disk before pushing.
- Scan for secrets (API keys, tokens, `Bearer` strings) before every push.
