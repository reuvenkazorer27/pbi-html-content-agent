# -*- coding: utf-8 -*-
"""Version control for a PBIP + HTML Content dashboard - snapshot / list / diff / revert.

  python -I versions.py snapshot "label" [--fit "FIT OK"] [--results r_all.json] [--shot full.png]
  python -I versions.py list
  python -I versions.py diff v003 [v004|current]
  python -I versions.py revert v003          (snapshots the current state first as 'pre-revert')

A version is a zip under <project>/_versions/ holding: the .pbip, the report and model
definitions (no caches/local settings), the _build sources (measures, M, scripts), the
real HTML output of every measure (r_all.json, when given) and an optional screenshot.
After revert: Desktop -> Apply external changes -> Home > Refresh.

Git: when the project folder is a git repo, every snapshot is also committed and tagged vNNN
(and every revert is committed), so history, diffs and a remote backup come for free.
The project's .gitignore must exclude env/key files, .pbi caches and localSettings.
"""
import datetime, hashlib, io, json, os, re, shutil, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import ROOT, PROJECT                     # ROOT = the PBIP project folder
VDIR = os.path.join(ROOT, "_versions")
INDEX = os.path.join(VDIR, "index.json")
# what a version contains (relative to ROOT); caches, localSettings and data files are excluded
INCLUDE_DIRS = [f"{PROJECT}.Report/definition", f"{PROJECT}.Report/StaticResources", f"{PROJECT}.SemanticModel/definition"]
INCLUDE_FILES = [f"{PROJECT}.pbip", f"{PROJECT}.Report/definition.pbir", f"{PROJECT}.SemanticModel/definition.pbism"]
BUILD_EXT = (".py", ".m", ".ps1", ".sh", ".md")
# restore only these on revert (never the data folder, env files, or _versions itself)
RESTORE_DIRS = INCLUDE_DIRS


def _index():
    return json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []


def _save_index(ix):
    os.makedirs(VDIR, exist_ok=True)
    json.dump(ix, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _files():
    out = []
    for d in INCLUDE_DIRS:
        base = os.path.join(ROOT, d)
        for dp, _, fs in os.walk(base):
            out += [os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/") for f in fs]
    out += [f for f in INCLUDE_FILES if os.path.exists(os.path.join(ROOT, f))]
    for f in os.listdir(HERE):
        if f.endswith(BUILD_EXT) and os.path.isfile(os.path.join(HERE, f)):
            out.append("_build/" + f)
    return sorted(set(out))


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def snapshot(label, fit=None, results=None, shot=None):
    ix = _index()
    n = (max([v["n"] for v in ix]) + 1) if ix else 1
    vid = f"v{n:03d}"
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    # labels may be Hebrew or English (א-ת keeps Hebrew letters in the zip name)
    zname = f"{vid}_{stamp}_{re.sub(r'[^A-Za-z0-9א-ת_-]+', '-', label)[:40]}.zip"
    files = _files()
    hashes = {}
    os.makedirs(VDIR, exist_ok=True)
    with zipfile.ZipFile(os.path.join(VDIR, zname), "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(os.path.join(ROOT, f), f)
            hashes[f] = _sha(os.path.join(ROOT, f))
        if results and os.path.exists(results):
            z.write(results, "_outputs/r_all.json")
        if shot and os.path.exists(shot):
            z.write(shot, "_outputs/" + os.path.basename(shot))
    entry = {"n": n, "id": vid, "zip": zname, "time": stamp, "label": label, "fit": fit,
             "files": len(files), "hashes": hashes, "has_outputs": bool(results and os.path.exists(results))}
    ix.append(entry)
    _save_index(ix)
    print(f"{vid} saved: {label} ({len(files)} files){' · ' + fit if fit else ''}")
    _git_commit(f"{vid}: {label}" + (f" [{fit}]" if fit else ""), tag=vid)
    return vid


# ---------------------------------------------------------------- git (optional, used when ROOT is a git repo)
def _git(*args):
    import subprocess
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


def _is_git():
    return _git("rev-parse", "--is-inside-work-tree")[0] == 0


def _git_commit(msg, tag=None):
    """Commit everything .gitignore allows (never env files, caches, local settings) and tag it."""
    if not _is_git():
        return
    _git("add", "-A")
    code, out = _git("commit", "-m", msg)
    if code != 0 and "nothing to commit" not in out:
        print("git commit failed: " + out[-300:])
        return
    if tag:
        _git("tag", "-f", tag)
    print(f"git: committed{' + tagged ' + tag if tag else ''}")


def _get(vid):
    for v in _index():
        if v["id"] == vid:
            return v
    sys.exit(f"no version {vid}")


def list_versions():
    ix = _index()
    if not ix:
        print("no versions yet")
    for v in ix:
        print(f"{v['id']}  {v['time']}  {v.get('fit') or '-':8}  {v['label']}")


def _outputs(v):
    with zipfile.ZipFile(os.path.join(VDIR, v["zip"])) as z:
        if "_outputs/r_all.json" not in z.namelist():
            return None
        row = json.loads(z.read("_outputs/r_all.json").decode("utf-8-sig"))
        return {k.strip("[]"): val for k, val in (row[0] if isinstance(row, list) else row).items()}


def diff(a, b="current"):
    va = _get(a)
    hb = {f: _sha(os.path.join(ROOT, f)) for f in _files()} if b == "current" else _get(b)["hashes"]
    ha = va["hashes"]
    changed = sorted(f for f in set(ha) & set(hb) if ha[f] != hb[f])
    added, removed = sorted(set(hb) - set(ha)), sorted(set(ha) - set(hb))
    print(f"{a} -> {b}: {len(changed)} changed, {len(added)} added, {len(removed)} removed")
    for tag, lst in (("~", changed), ("+", added), ("-", removed)):
        for f in lst:
            print(f"  {tag} {f}")
    if b != "current":
        oa, ob = _outputs(va), _outputs(_get(b))
        if oa and ob:
            for k in sorted(set(oa) | set(ob)):
                if oa.get(k) != ob.get(k):
                    print(f"  HTML changed: {k} ({len(oa.get(k) or '')} -> {len(ob.get(k) or '')} chars)")


def revert(vid):
    v = _get(vid)
    snapshot(f"pre-revert-to-{vid}")
    with zipfile.ZipFile(os.path.join(VDIR, v["zip"])) as z:
        names = [n for n in z.namelist() if not n.startswith("_outputs/")]
        for d in RESTORE_DIRS:                      # remove files that did not exist in the version
            base = os.path.join(ROOT, d)
            if os.path.isdir(base):
                shutil.rmtree(base)
        for n in names:
            dst = os.path.join(ROOT, n)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(z.read(n))
    _git_commit(f"revert to {vid}: {v['label']}")
    print(f"reverted to {vid} ({v['label']}). In Desktop: Apply external changes -> Home > Refresh.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "list":
        list_versions()
    elif a[0] == "snapshot":
        opt = {k: a[i + 1] for i, k in enumerate(a) if k.startswith("--") and i + 1 < len(a)}
        snapshot(a[1] if len(a) > 1 else "manual", opt.get("--fit"), opt.get("--results"), opt.get("--shot"))
    elif a[0] == "diff":
        diff(a[1], a[2] if len(a) > 2 else "current")
    elif a[0] == "revert":
        revert(a[1])
    else:
        sys.exit(__doc__)
