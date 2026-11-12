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
import base64, glob, json, os, sys, threading, time

PIPE = r"\\.\pipe\pbi-desktop-bridge-"


def _exchange(pid, body, timeout):
    """one request/response on the pipe, in a worker thread: a pipe read has no timeout of its own, and a Desktop that
    is busy or stuck opening can accept the connection and never answer (measured) - the caller must not hang"""
    box = {}

    def run():
        box["tid"] = threading.get_native_id()
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
            box["data"] = data
        except BaseException as e:   # handed over to the caller's thread
            box["err"] = e

    t = threading.Thread(target=run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        # cancel the pending pipe read: a handle with pending synchronous I/O cannot be closed, so the process would
        # hang at exit (measured)
        try:
            import ctypes
            from ctypes import wintypes
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.OpenThread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            k32.OpenThread.restype = wintypes.HANDLE   # a 64-bit handle: the default int restype would truncate it
            k32.CancelSynchronousIo.argtypes = (wintypes.HANDLE,)
            k32.CloseHandle.argtypes = (wintypes.HANDLE,)
            h = k32.OpenThread(0x0001, False, box.get("tid", 0))   # THREAD_TERMINATE: required by CancelSynchronousIo
            if h:
                k32.CancelSynchronousIo(h)
                k32.CloseHandle(h)
            t.join(2)
        except Exception:   # not Windows, or the cancel failed: the timeout below still frees the caller
            pass
        raise SystemExit(f"bridge did not answer in {timeout:.0f} s for pid {pid} - Desktop busy or still opening")
    if "err" in box:
        raise box["err"]
    return box["data"]


def report_window(pid):
    """the title of the Desktop window of `pid` once it shows a report, else None.
    Measured: while opening, Desktop has no window or one titled '<blank> - Power BI Desktop' ('Untitled - ...'); with
    a report open the title is the file's base name alone ('sales-demo'). So: ready = a visible window whose title does
    not end with the product name - no dependence on the UI language, and a report saved as 'Untitled.pbip' still
    counts. Off Windows (no user32) it does not block: returns ''."""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.WinDLL("user32")
    except (ImportError, AttributeError, OSError):
        return ""
    user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    user32.IsWindowVisible.argtypes = (wintypes.HWND,)
    user32.InternalGetWindowText.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
    proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = (proc, wintypes.LPARAM)
    found = []

    def each(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == int(pid) and user32.IsWindowVisible(hwnd):
            # InternalGetWindowText reads the title without sending the window a message (GetWindowTextW does, and a
            # Desktop busy opening may not answer it); a precaution - the cause of the slow first status call that was
            # seen (3 min, and once 66 s after this change) is not established
            buf = ctypes.create_unicode_buffer(512)
            if user32.InternalGetWindowText(hwnd, buf, 512):
                found.append(buf.value)
        return True

    user32.EnumWindows(proc(each), 0)
    titles = [t for t in found if is_report_title(t)]
    if titles:
        return titles[0]
    # only measured on one Desktop build: a build that titles an open report '<name> - Power BI Desktop' would never
    # count as ready - so a titled window that has existed for READY_AFTER seconds counts as ready anyway
    if found and _process_age(pid) >= READY_AFTER:
        return found[0]
    return None


READY_AFTER = 90   # seconds; a normal open showed its report title within 20-30 s (measured 12 Nov 2026)


def _process_age(pid):
    """seconds since the process started (Windows), 0 when unknown"""
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32")
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        k32.GetSystemTimeAsFileTime.argtypes = (ctypes.POINTER(wintypes.FILETIME),)
        h = k32.OpenProcess(0x1000, False, int(pid))   # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return 0
        t = [wintypes.FILETIME() for _ in range(4)]
        ok = k32.GetProcessTimes(h, *[ctypes.byref(x) for x in t])
        k32.CloseHandle(h)
        now = wintypes.FILETIME()
        k32.GetSystemTimeAsFileTime(ctypes.byref(now))
        ft = lambda f: (f.dwHighDateTime << 32 | f.dwLowDateTime) / 1e7
        return ft(now) - ft(t[0]) if ok else 0
    except Exception:
        return 0


def is_report_title(title):
    """a Desktop window title that shows an open report: the file name alone, not '<blank> - Power BI Desktop'"""
    return bool(title.strip()) and not title.rstrip().lower().endswith("power bi desktop")


def call(pid, method, args=None, wait=60):
    """one request per connection; the pipe is busy while another client talks to it -> retry until `wait` seconds"""
    msg = {"jsonrpc": "2.0", "id": 1, "method": method, "params": {"client": "pbi-html-pipeline", "args": args or {}}}
    if method == "bridge.manifest":
        msg["params"] = {}
    body = json.dumps(msg).encode("utf-8")
    end = time.time() + wait
    while True:
        try:
            out = json.loads(_exchange(pid, body, max(5.0, end - time.time())))
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
        if report_window(pid) is None:   # still opening: do not touch it (a request now can wedge it)
            out.append({"pid": int(pid), "error": "no report window yet (Desktop still opening) - not contacted"})
            continue
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
