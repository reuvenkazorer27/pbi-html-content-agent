# -*- coding: utf-8 -*-
"""Power BI Desktop Bridge client in plain Python (no Node): JSON-RPC 2.0 with Content-Length framing over
\\\\.\\pipe\\pbi-desktop-bridge-<pid>. Needs Desktop's preview feature "external tool access" (Options > Preview features).

  python -I bridge.py status                     -> every Desktop with the bridge: pid, open file, unsaved changes
  python -I bridge.py reload  [--pid N] [--settle 15]  -> reload the REPORT (PBIR) from disk, then wait for the
                                                  HTML visuals to render; the live MODEL is NOT reloaded from TMDL
                                                  (push measures with the Modeling MCP, or Apply external changes)
  python -I bridge.py shot <page-id> out.png [--pid N] [--scale 1]
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
                if time.time() < end and "busy" in json.dumps(err).lower():
                    time.sleep(1)
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
        print(name, call(pid, name, {}, wait=120))
        time.sleep(float(_arg("--settle", 15)))   # a capture right after reload shows empty custom visuals
    elif cmd == "shot":
        page, out = sys.argv[2], sys.argv[3]
        r = call(pid, "report.snapshot.capture/v1", {"pageId": page, "scale": float(_arg("--scale", 1))}, wait=120)
        open(out, "wb").write(base64.b64decode(r["payload"]))
        print(f"{out} ({r.get('mimeType')}) from pid {pid}")
    else:
        sys.exit(__doc__)
