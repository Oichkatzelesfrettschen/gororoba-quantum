"""Calibration of check_k2_cofactor_certificate_v1: the clean file passes each check, and three corruptions fail.

The corruptions are one cofactor coefficient (the b entry of the quadric with the fewest cofactor terms), the constant
term of the unit of that quadric, and one coefficient of one Groebner element. Each calls the checker's own functions
on a modified copy of the loaded file. Exit 0 when the clean checks pass and every corruption is rejected.

Usage: calibrate_k2_cofactor_certificate_v1.py CERT.json
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("chk", HERE / "check_k2_cofactor_certificate_v1.py")
if spec is None or spec.loader is None:
    raise SystemExit("cannot load the checker")
chk = importlib.util.module_from_spec(spec)
sys.modules["chk"] = chk
spec.loader.exec_module(chk)


def rejected(fn) -> str | None:
    try:
        fn()
    except chk.Reject as err:
        return str(err)
    return None


def main() -> None:
    doc = json.loads(Path(sys.argv[1]).read_text())
    p = doc["prime"]
    quads = doc["quadrics"]
    j_a = min(range(len(quads)), key=lambda i: quads[i]["terms"])
    j_b = min((i for i in range(len(quads)) if quads[i]["b"]), key=lambda i: quads[i]["terms"])
    ctx = chk.Ctx(doc)
    for j in (j_a, j_b):
        chk.check_quadric(ctx, quads[j])
    chk.check_groebner(doc)
    print(f"clean: identities of quadrics {j_a} and {j_b} and the Groebner checks pass")
    msgs = []
    for j, part in ((j_a, "a"), (j_b, "b")):
        bad = copy.deepcopy(doc)
        ent = bad["quadrics"][j]
        term = (ent["b"][0][3] if part == "b" else ent["a"][0][1])[0]
        term[0] = term[0] % (p - 1) + 1
        msgs.append(
            (f"cofactor coefficient in {part} of quadric {j}", rejected(lambda ent=ent: chk.check_quadric(ctx, ent)))
        )
    bad = copy.deepcopy(doc)
    ent = bad["quadrics"][j_b]
    c0 = [t for t in ent["u"] if not any(t[1])][0]
    c0[0] = 0
    msgs.append((f"unit constant term of quadric {j_b}", rejected(lambda: chk.check_quadric(ctx, ent))))
    bad = copy.deepcopy(doc)
    k = max(range(len(bad["groebner"]["basis"])), key=lambda i: len(bad["groebner"]["basis"][i]))
    el = bad["groebner"]["basis"][k]
    lm = max(el, key=lambda t: (sum(t[1]), tuple(-x for x in reversed(t[1]))))
    t = [t for t in el if t is not lm][0]
    t[0] = t[0] % (p - 1) + 1
    msgs.append((f"non-leading coefficient of Groebner element {k}", rejected(lambda: chk.check_groebner(bad))))
    for name, msg in msgs:
        print(f"corrupt {name}: {'REJECTED: ' + msg if msg else 'ACCEPTED'}")
    if not all(m for _, m in msgs):
        sys.exit(1)
    print("calibration PASS")


if __name__ == "__main__":
    main()
