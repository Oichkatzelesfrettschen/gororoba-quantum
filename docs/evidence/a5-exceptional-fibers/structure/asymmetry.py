"""Germs at the N+ and N- representatives that explain the same-sign / opposite-sign difference of the X fibers.

The regularity record's germ_job (reduced germ through the global-ordering deformation to the normal cone, over Q)
runs on three ideals beyond its closure table:

- EhatMu: E8-bar cut by mu' = 0. Its reduced germ at N- splits into the sheets X+ (smooth, (4,1,4)) and X-
  ((4,2,7)), of total multiplicity 3 = mult(E8-bar) along N+-, meeting in a 3-dimensional germ; at N+ the roles swap.
- MuEtaD: {mu' = 0, eta(d) = 0}, the conditions that single out X+ inside E8-bar: smooth at N- (d = 2u' != 0) and a
  rank-7 quadric cone at N+ (d = 0).
- MuEtaS: {mu' = 0, eta(s) = 0}, the X- conditions, with the roles of N+ and N- exchanged.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/structure/asymmetry.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "a5-strata-regularity"))

import strata_regularity as sr  # noqa: E402

BASE = sr.closure_ideals


def extended_ideals(mutation: str = "") -> dict[str, list[Any]]:
    out = BASE(mutation)
    out["EhatMu"] = [*out["Ehat"], out["Xp"][0]]
    out["MuEtaD"] = out["Xp"][:2]
    out["MuEtaS"] = out["Xm"][:2]
    return out


def main() -> int:
    sr.closure_ideals = extended_ideals
    jobs = [(closure, orbit, "") for closure in ("EhatMu", "MuEtaD", "MuEtaS") for orbit in ("Nm", "Np")]
    rows = [sr.germ_job(job) for job in jobs]
    (HERE / "logs").mkdir(exist_ok=True)
    (HERE / "logs" / "asymmetry.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    for row in rows:
        if "singular_error" in row:
            raise RuntimeError(f"{row['closure']} at {row['orbit']}: {row['singular_error']}")
        comps = [c and (c["dim"], c["mult"], c["embdim"]) for c in row["components"]]
        print(row["closure"], row["orbit"], row["germ"], comps, row["meets"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
