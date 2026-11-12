# -*- coding: utf-8 -*-
"""Fetch one element from Uiverse.io's open-source library (github.com/uiverse-io/galaxy, MIT License,
Copyright (c) 2023 Uiverse.io) and adapt it for an HTML Content page. Python stdlib only.

  python -I uiverse.py list Patterns                 # file names in a folder (Patterns, Cards, Notifications, ...)
  python -I uiverse.py get Patterns/<file>.html --prefix bg1 [--out el.html]

`get` downloads the raw file, keeps the author/tags comment as attribution, scopes every class to `<prefix>-`
(so two elements never clash inside one measure), and REPORTS what the Secure edition / the dashboard rules
reject: script, :hover-only effects, infinite animations, external url(), form controls. It never runs anything.
Use the element as a texture, frame, badge or card surface behind real data - never as a fake control.
Record what you used in the deliverable: element path, author, MIT."""
import sys, re, json, urllib.request

RAW = "https://raw.githubusercontent.com/uiverse-io/galaxy/main/"
API = "https://api.github.com/repos/uiverse-io/galaxy/contents/"


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pbi-html-content-agent"}), timeout=30) as r:
        return r.read().decode("utf-8")


def list_folder(folder):
    return [f["name"] for f in json.loads(_get(API + folder))]


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
    elif len(sys.argv) >= 3 and sys.argv[1] == "get":
        path = sys.argv[2]
        prefix = sys.argv[sys.argv.index("--prefix") + 1] if "--prefix" in sys.argv else "uv"
        el, notes = adapt(_get(RAW + path), prefix)
        head = f"<!-- Uiverse.io element {path} (MIT License, Copyright (c) 2023 Uiverse.io), scoped as {prefix}- -->\n"
        if "--out" in sys.argv:
            open(sys.argv[sys.argv.index("--out") + 1], "w", encoding="utf-8").write(head + el)
        else:
            print(head + el)
        print("CHECK:", "OK" if not notes else "; ".join(notes), file=sys.stderr)
    else:
        print(__doc__)
