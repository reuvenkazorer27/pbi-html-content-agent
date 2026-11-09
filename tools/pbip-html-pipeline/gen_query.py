# -*- coding: utf-8 -*-
"""Emit a DAX test query: DEFINE every measure, EVALUATE all HTML measures.
Optional filter: python gen_query.py out.dax "<DAX filter table expr>" """
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures import M, T

out = sys.argv[1]
flt = sys.argv[2] if len(sys.argv) > 2 else None
defs = "\n".join(f"MEASURE {T}[{n}] =\n{d['expr']}" for n, d in M.items())
cols = ",\n".join(f'"{n}", [{n}]' for n in M if n.startswith("HTML"))
body = f"ROW (\n{cols}\n)"
if flt:
    body = f"CALCULATETABLE ( {body}, {flt} )"
q = f"DEFINE\n{defs}\nEVALUATE\n{body}\n"
open(out, "w", encoding="utf-8").write(q)
print(len(q), "chars")
