# -*- coding: utf-8 -*-
"""Power BI Desktop Bridge client in plain Python (no Node): JSON-RPC 2.0 with Content-Length framing over
\\\\.\\pipe\\pbi-desktop-bridge-<pid>. Needs Desktop's preview feature "external tool access" (Options > Preview features).

  python -I bridge.py status                     -> every Desktop with the bridge: pid, open file, unsaved changes
  python -I bridge.py reload  [--pid N] [--report-only]
                                               -> reload the REPORT (PBIR) and the MODEL (TMDL) from disk
                                                  (file.reload/v1 reloadModelDefinition=true: no Apply banner, no
                                                  click, no MCP push), then wait until the active page has rendered;
                                                  --report-only reloads the PBIR alone
  python -I bridge.py shot <page-id> out.png [--pid N] [--scale 1]
                                                  -> captures until two captures 5s apart are the same size: custom
                                                  visuals render after the page, and a capture right after a reload
                                                  (measured: 15s was not always enough) shows empty cards
Without --pid the Desktop whose open file is <project>.pbip (pipeline.json) is used. Exit 2 = no bridge (fall back to
Apply external changes + Refresh + a manual screenshot)."""
import base64, glob, json, os, sys, time

PIPE = r"\\.\pipe\pbi-desktop-bridge-"


def call(pid, method, args=None, wait=60):
    """one request per connection; the pipe is busy while another client talks to it -> retry until `wait` seconds"""
    msg = {"jsonrpc": "2.0", "id": 1, "method": method, "params": {"client": "pbi-html-pipeline", "args": args or {}}}
    if method == "bridge.manifest":
        msg["params"] = {}
    body = json.dumps(msg).encode("utf-8")
    end = time.time() + wait
    while True:
        try:
            with open(PIPE + str(pid), "r+b", buffering=0) as f:
                f.write(b"Content-Length: %d\r\n\r\n" % len(body) + body)
                head = b""
                while not head.endswith(b"\r\n\r\n"):
                    c = f.read(1)
                    if not c:
                        raise ConnectionError("bridge closed the connection")
                    head += c
                n = int(next(l for l in head.decode().split("\r\n") if l.lower().startswith("content-length")).split(":")[1])
                data = b""
                while len(data) < n:
                    data += f.read(n - len(data))
            out = json.loads(data)
            if "error" in out:
                err = out["error"]
                info = err.get("data") or {}
                # the bridge marks transient states retryable (e.g. CaptureMetadataNotReady right after a reload);
                # PrintMetadataUnavailable (reported after a fresh open, before the page rendered once) is retried too
                txt = json.dumps(err).lower()
                if time.time() < end and (info.get("retryable") or any(k in txt for k in ("busy", "metadatanotready", "printmetadataunavailable"))):
                    time.sleep(max(0.5, (info.get("retryAfterMs") or 1000) / 1000))
                    continue
                raise RuntimeError(f"{method}: {err}")
            return out["result"]
        except (FileNotFoundError, OSError) as e:   # busy pipe or Desktop still starting
            if time.time() >= end:
                raise SystemExit(f"bridge not reachable for pid {pid}: {e}")
            time.sleep(0.5)


def instances():
    out = []
    for p in glob.glob(PIPE + "*"):
        pid = p.rsplit("-", 1)[1]
        try:
            st = call(pid, "application.state.get/v1", wait=10)
        except (SystemExit, RuntimeError) as e:
            st = {"error": str(e)}
        out.append(dict(pid=int(pid), **st))
    return out


def find_pid(project):
    for i in instances():
        if os.path.basename(i.get("currentFilePath") or "").lower() == f"{project}.pbip".lower():
            return i["pid"]
    return None


def _active_page():
    """the PBIR active page id of this project (pipeline.json), or None"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from config import REPORT_DIR
        pj = json.load(open(os.path.join(REPORT_DIR, "definition", "pages", "pages.json"), encoding="utf-8"))
        return pj.get("activePageName") or (pj.get("pageOrder") or [None])[0]
    except Exception:
        return None


def _arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if not glob.glob(PIPE + "*"):
        print("no Desktop Bridge: enable Options > Preview features > external tool access, or use Apply external changes")
        sys.exit(2)
    if cmd == "status":
        print(json.dumps(instances(), indent=1))
        sys.exit(0)
    pid = _arg("--pid")
    if not pid:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from config import PROJECT
        pid = find_pid(PROJECT)
        if not pid:
            print(f"no Desktop has {PROJECT}.pbip open")
            sys.exit(2)
    methods = {m["name"] for m in call(pid, "bridge.manifest")["methods"]}
    if cmd == "reload":
        name = next((m for m in methods if m.startswith("report.reload")), None) or next(m for m in methods if "reload" in m)
        # file.reload/v1 takes reloadModelDefinition (required): True re-applies the TMDL on disk to the live model, so
        # report AND measures arrive with no Apply banner, no click and no MCP push; --report-only keeps the old behavior
        st = next((i for i in instances() if str(i["pid"]) == str(pid)), {})
        if st.get("hasUnsavedChanges"):
            print("WARNING: Desktop has unsaved changes - a reload can be refused or a later save can overwrite the files "
                  "on disk (incl. publicCustomVisuals); reloading anyway")
        print(name, call(pid, name, {"reloadModelDefinition": "--report-only" not in sys.argv}, wait=180))
        # right after a reload the custom visuals are empty and two empty captures are the same size, so "stable"
        # alone is not "rendered": wait until the active page's capture has GROWN past the first one and then held
        # still (or has held still for 4 captures, i.e. it was already rendered), up to ~90s
        page = _active_page()
        if not page:
            time.sleep(float(_arg("--settle", 20)))
        else:
            first = prev = None
            same = 0
            for _ in range(18):
                n = len(base64.b64decode(call(pid, "report.snapshot.capture/v1", {"pageId": page, "scale": 1.0}, wait=120)["payload"]))
                first = first or n
                same = same + 1 if prev and abs(n - prev) <= 0.01 * prev else 0
                if (same >= 1 and n > first * 1.05) or same >= 4:
                    break
                prev = n
                time.sleep(5)
            print(f"rendered: page {page} capture {first} -> {n} bytes")
    elif cmd == "shot":
        page, out = sys.argv[2], sys.argv[3]
        prev, png = None, b""
        for _ in range(12):   # up to ~60s: stop when the render is stable (same PNG size twice, within 1%)
            r = call(pid, "report.snapshot.capture/v1", {"pageId": page, "scale": float(_arg("--scale", 1))}, wait=120)
            png = base64.b64decode(r["payload"])
            if prev is not None and abs(len(png) - prev) <= 0.01 * prev:
                break
            prev = len(png)
            time.sleep(5)
        open(out, "wb").write(png)
        print(f"{out} ({r.get('mimeType')}, {len(png)} bytes, stable) from pid {pid}")
    else:
        sys.exit(__doc__)
