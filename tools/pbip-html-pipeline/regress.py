# -*- coding: utf-8 -*-
"""Regression gate: compare the real HTML of every measure with a saved version.

  python -I regress.py r_all.json            (against the latest version that has outputs)
  python -I regress.py r_all.json v003

Prints IDENTICAL, or each changed measure with its size delta and the first differing snippet.
Exit code 1 when anything changed - an intended change is accepted by taking a new snapshot.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import versions as V


def load(path):
    row = json.load(open(path, encoding="utf-8-sig"))
    return {k.strip("[]"): v for k, v in (row[0] if isinstance(row, list) else row).items()}


new = load(sys.argv[1])
cands = [v for v in V._index() if v.get("has_outputs")]
base_v = V._get(sys.argv[2]) if len(sys.argv) > 2 else (cands[-1] if cands else None)
if not base_v:
    sys.exit("no version with outputs yet - take a snapshot with --results first")
old = V._outputs(base_v)
changed = [k for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)]
if not changed:
    print(f"IDENTICAL to {base_v['id']} ({base_v['label']}): {len(new)} measures")
    sys.exit(0)
print(f"CHANGED vs {base_v['id']} ({base_v['label']}): {len(changed)} of {len(new)} measures")
for k in changed:
    a, b = old.get(k) or "", new.get(k) or ""
    i = next((j for j in range(min(len(a), len(b))) if a[j] != b[j]), min(len(a), len(b)))
    print(f"  {k}: {len(a)} -> {len(b)} chars; first diff: ...{b[max(0, i - 40):i + 60]}...")
sys.exit(1)
