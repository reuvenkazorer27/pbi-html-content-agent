# -*- coding: utf-8 -*-
"""Fetch one element from Uiverse.io's open-source library (github.com/uiverse-io/galaxy, MIT License,
Copyright (c) 2023 Uiverse.io) and adapt it for an HTML Content page. Python stdlib only.

  python -I uiverse.py list Patterns                 # file names in a folder (Patterns, Cards, Notifications, ...)
  python -I uiverse.py search Patterns dots grid     # elements whose author/tags comment matches all words (cached)
  python -I uiverse.py get Patterns/<file>.html --prefix bg1 [--split] [--out el.html]

--split prints the CSS (ready to merge into your page's ONE <style>) and the markup separately, with rem/em
converted to px (16px = 1rem) so page_kit.fluid() can scale them.

`get` downloads the raw file, keeps the author/tags comment as attribution, scopes every class to `<prefix>-`
(so two elements never clash inside one measure), and REPORTS what the Secure edition / the dashboard rules
reject: script, :hover-only effects, infinite animations, external url(), form controls. It never runs anything.
Use the element as a texture, frame, badge or card surface behind real data - never as a fake control.
Record what you used in the deliverable: element path, author, MIT."""
import sys, re, os, json, tempfile, urllib.request

RAW = "https://raw.githubusercontent.com/uiverse-io/galaxy/main/"
API = "https://api.github.com/repos/uiverse-io/galaxy/contents/"


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pbi-html-content-agent"}), timeout=30) as r:
        return r.read().decode("utf-8")


def list_folder(folder):
    return [f["name"] for f in json.loads(_get(API + folder))]


CACHE = os.path.join(tempfile.gettempdir(), "uiverse_cache")


def search(folder, words):
    """match all words against each element's author/tags comment; files are cached in the temp folder"""
    os.makedirs(os.path.join(CACHE, folder), exist_ok=True)
    hits = []
    for name in list_folder(folder):
        p = os.path.join(CACHE, folder, name)
        if not os.path.exists(p):
            open(p, "w", encoding="utf-8").write(_get(RAW + folder + "/" + name))
        head = " ".join(re.findall(r"/\*\s*From Uiverse\.io[^*]*\*/", open(p, encoding="utf-8").read()))
        if all(w.lower() in head.lower() for w in words):
            hits.append((name, head.strip()[:120]))
    return hits


def to_px(css):
    return re.sub(r"(-?\d*\.?\d+)r?em(?![\w-])", lambda m: f"{float(m.group(1)) * 16:g}px", css)


def adapt(src, prefix):
    classes = sorted(set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", "".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S)))), key=len, reverse=True)
    out = src
    for c in classes:
        out = re.sub(rf"(?<![\w-])\.{re.escape(c)}(?![\w-])", f".{prefix}-{c}", out)
        out = re.sub(rf"(class=['\"][^'\"]*?)(?<![\w-]){re.escape(c)}(?![\w-])", rf"\g<1>{prefix}-{c}", out)
    notes = []
    for pat, msg in ((r"<script", "has <script> - not usable in Secure"), (r":hover", "uses :hover - report users rarely hover; keep only a static state"),
                     (r"\binfinite\b", "loops forever - set a finite iteration count or drop the animation"),
                     (r"url\(\s*['\"]?https?:", "loads an external file - not allowed"), (r"<(input|button|form|select)", "form control - never in a dashboard (fake control)")):
        if re.search(pat, out, re.I):
            notes.append(msg)
    return out, notes


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "list":
        print("\n".join(list_folder(sys.argv[2])))
    elif len(sys.argv) >= 4 and sys.argv[1] == "search":
        for name, head in search(sys.argv[2], sys.argv[3:]):
            print(f"{sys.argv[2]}/{name}  {head}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "get":
        path = sys.argv[2]
        prefix = sys.argv[sys.argv.index("--prefix") + 1] if "--prefix" in sys.argv else "uv"
        el, notes = adapt(_get(RAW + path), prefix)
        head = f"<!-- Uiverse.io element {path} (MIT License, Copyright (c) 2023 Uiverse.io), scoped as {prefix}- -->\n"
        if "--split" in sys.argv:   # CSS ready to merge into the page's single <style>; rem/em -> px for fluid()
            css = to_px("\n".join(re.findall(r"<style[^>]*>(.*?)</style>", el, re.S))).strip()
            markup = re.sub(r"<style[^>]*>.*?</style>", "", el, flags=re.S).strip()
            el = (f"/* ---- CSS: merge into your page's single <style> ---- */\n/* Uiverse.io {path}, MIT, scoped {prefix}- */\n"
                  f"{css}\n\n<!-- ---- markup ---- -->\n{markup}\n")
            head = ""
        if "--out" in sys.argv:
            open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8").write(head + el)
        else:
            print(head + el)
        print("CHECK:", "OK" if not notes else "; ".join(notes), file=sys.stderr)
    else:
        print(__doc__)
