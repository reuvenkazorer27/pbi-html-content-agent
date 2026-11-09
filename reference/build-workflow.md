# Build workflow - iterating safely on a PBIP in Power BI Desktop

How to build, test, version and ship a dashboard with this kit without losing work, corrupting the report or leaving the machine in a bad state. Measured in Power BI Desktop (PBIP/PBIR, Windows).

## 1. Iterating while Desktop is open

- Write the files, then click **Apply external changes** in Desktop's banner. Do not close Desktop between iterations. The banner can be hidden behind the canvas until the window repaints - take a screenshot to find it.
- After Apply the **model** is updated, but visuals keep **cached query results**: click Home → **Refresh** (or switch page) before judging the render. To check whether the model has the new version, evaluate the measure text (e.g. DAX `SEARCH` for a new string).
- If Desktop must be closed, close it **before** writing - it saves on close and can overwrite your files.
- One Desktop window per project. Two windows on the same PBIP each save their own state and overwrite each other.
- A project whose folder was moved fails Apply with `ArtifactShortcut: Required artifact is missing`: the open window still points to the old path - reopen the `.pbip` from its new location.
- An invisible dialog (one that opens without rendering) blocks every click. Find it in the window's accessibility tree (`FloatingDialog`) and answer it; do not kill the app.
- Never force-kill Desktop or stop a Power BI process you did not start - a windowless one may be the user's own reopen in progress. Ask first.

## 2. Writing PBIP files

- Generate TMDL measures and `visual.json` files from one source of truth (the pipeline's `measures.py` + `pipeline.json`), rebuilt from a clean backup copy on every run so reruns are idempotent.
- In TMDL a line starting with `///` is the **description** of the next object - never use it as a marker around generated code.
- DAX `VAR` names must be ASCII identifiers (a Hebrew variable name is a syntax error); non-Latin text is fine in measure, table and column names and in strings.
- Register the AppSource visual in `report.json` (`publicCustomVisuals`) so Desktop fetches it on open.

## 3. Testing before writing

- Evaluate every HTML measure against the open model before writing anything: `runq.ps1` loads `Microsoft.PowerBI.AdomdClient.dll` from Desktop's own folder, finds the model port in `...\AnalysisServicesWorkspaces\*\Data\msmdsrv.port.txt` (UTF-16, newest file) and runs a `DEFINE MEASURE ... EVALUATE ROW(...)` query. The real HTML it returns feeds the preview.
- Gates, in order: `regress.py` (only the intended cards changed), `fitcheck.mjs` (fit + WCAG contrast on the exact-size preview), `stress.py` (filter scenarios). Verify that a scenario really filters - a gate that tests nothing passes everything.
- Headless browser checks must clean up after themselves. `child.kill()` stops only the browser launcher; Edge's GPU/renderer children outlive it and accumulate into hundreds of processes, which then make later checks fail at random. Wait for real readiness (page and every card rendered) instead of a fixed sleep, close the browser over the DevTools protocol (`Browser.close`), kill anything left on the run's temporary profile, and delete the profile. Check: a process count before and after a run must match.
- Color changes: a JPEG zoom cannot tell close shades apart. Verify from a PNG of the Desktop window by reading pixels in the element's box.

## 4. Versions and revert

- End every iteration with `versions.py snapshot "what changed"`: report and model definitions, build sources, the real HTML of every card and a screenshot. `versions.py revert vN` restores a version and first snapshots the current state, so a revert is itself undoable. Then Apply external changes → Refresh.
- Refactors are proven safe by `regress.py`: the HTML of every card must be byte-identical to the previous version. Intended changes list exactly which cards changed.

## 5. Git

- Make the dashboard project a git repo. `versions.py` then commits and tags `vNNN` on every snapshot and commits every revert; the zip snapshots stay as a local backup (ignored by git).
- Recommended for shared or long-lived dashboards: once a basic version exists, make each change on its own branch and merge it through a pull request with a review. (Changes to this kit itself always follow that flow - see the README's Contributing section.)
- `.gitignore` must exclude secrets and local state: env/key files, pulled data, `**/.pbi/cache.abf`, `**/.pbi/localSettings.json`, build scratch. Before the first commit, list tracked files and check that none of those appear.
- Ignore by prefix, not by extension: a broad `*.dax` rule meant for scratch queries silently drops a whole component library. Compare the tracked file count with the files on disk before pushing.
- Scan for secrets (API keys, tokens, `Bearer` strings) before every push.
