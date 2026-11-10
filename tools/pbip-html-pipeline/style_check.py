# -*- coding: utf-8 -*-
"""Contrast check for styles - no model needed.

  python -I style_check.py                       -> every preset + a sweep of 40 brand colors x light/dark x
                                                    every mechanism x hero on/off (800 generated styles)
  python -I style_check.py '{"brand": "#0E7490", "mode": "dark", "mechanism": "tint"}'   -> one style
  python -I style_check.py sand                  -> one preset

For every card role it checks: card text >= 4.5:1, data colors used as text >= 4.5:1 on the card (not on the
hero). Exit 1 on any failure. It complements, not replaces, fitcheck.mjs + stress.py on the real data."""
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402,F401  (loads styles)
import styles as S  # noqa: E402
from palette import contrast  # noqa: E402

DATA = ("primary", "design", "maint", "done", "bad")


def check(st):
    p = S.style_palette(st)
    for role in S.ROLES:
        t = S.card_tokens(st, role)
        bg = t["c_bg"]
        for k in ("fg", "fg2", "fg3"):
            c = t.get(k, p[k])
            if contrast(c, bg) < 4.5:
                return f"{role}: text {k} {c} on {bg} = {contrast(c, bg):.2f}"
        if role != "hero":
            for k in DATA:
                c = t.get(k, p[k])
                if contrast(c, bg) < 4.5:
                    return f"{role}: data {k} {c} on {bg} = {contrast(c, bg):.2f}"
    return None


def main():
    if len(sys.argv) > 1:
        st = S.resolve_style(sys.argv[1])
        err = check(st)
        print("STYLE OK" if not err else "STYLE FAIL " + err)
        return 0 if not err else 1
    random.seed(7)
    brands = ["#0E7490", "#B4532A", "#16A34A", "#DC2626", "#FACC15", "#111827", "#F8FAFC", "#9333EA", "#EC4899",
              "#64748B"] + ["#%06X" % random.randrange(0x1000000) for _ in range(30)]
    fails = [f"preset {n}: {e}" for n, st in S.PRESETS.items() if (e := check(st))]
    n = 0
    for b, mode, mech, hero in itertools.product(brands, ("light", "dark"), S.MECHANISMS, (True, False)):
        n += 1
        e = check(S.make_style(b, mode=mode, mechanism=mech, hero=hero))
        if e:
            fails.append(f"{b} {mode} {mech} hero={hero}: {e}")
    print(f"{len(S.PRESETS)} presets + {n} generated styles: " + ("STYLES OK" if not fails else f"{len(fails)} FAIL"))
    for f in fails[:20]:
        print("  " + f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
