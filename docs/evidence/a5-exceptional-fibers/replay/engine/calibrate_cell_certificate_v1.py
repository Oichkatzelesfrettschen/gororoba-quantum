"""Calibration of check_cell_certificate_v1.py: each corrupted copy of a certificate must fail the checker.

The five corruptions are one M entry, one level, one left-inverse entry inside its support, one J coefficient and a
duplicated selected product. The unmodified file must pass first. Usage: calibrate_cell_certificate_v1.py CERT.json
[--header HEADER] [--record RECORD]; exit 0 only when the original passes and every corruption fails.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run_checker(cert: dict, extra: list[str]) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cert.json"
        path.write_text(json.dumps(cert))
        res = subprocess.run(
            [sys.executable, "-I", str(HERE / "check_cell_certificate_v1.py"), str(path), *extra],
            capture_output=True,
            text=True,
            check=False,
        )
    return res.returncode


def corruptions(cert: dict) -> dict[str, dict]:
    p = cert["prime"]
    out = {}
    c = copy.deepcopy(cert)
    ent = c["module"]["M"][0][0]
    ent[2] = ent[2] % (p - 1) + 1
    out["one M entry"] = c
    c = copy.deepcopy(cert)
    ent = c["module"]["M"][0][0]
    c["module"]["lev"][ent[0]] = c["module"]["lev"][ent[1]]
    out["one level"] = c
    c = copy.deepcopy(cert)
    prods = c["products"]
    row = prods["left_inverse"][0]
    col = next(i for i, x in enumerate(row) if x)
    row[col] = row[col] % (p - 1) + 1
    out["one left-inverse entry in its support"] = c
    c = copy.deepcopy(cert)
    term = c["header"]["J"][0][0]
    term[0] = term[0] % (p - 1) + 1
    out["one J coefficient"] = c
    c = copy.deepcopy(cert)
    prods = c["products"]
    prods["selected"][1] = prods["selected"][0]
    out["a duplicated selected product"] = c
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--header")
    ap.add_argument("--record")
    a = ap.parse_args()
    extra = (["--header", a.header] if a.header else []) + (["--record", a.record] if a.record else [])
    cert = json.loads(Path(a.cert).read_text())
    ok = run_checker(cert, extra) == 0
    print(("PASS" if ok else "FAIL") + " original certificate accepted")
    for name, bad in corruptions(cert).items():
        rejected = run_checker(bad, extra) != 0
        ok = ok and rejected
        print(("PASS" if rejected else "FAIL") + " rejected: " + name)
    print("CALIBRATION PASS" if ok else "CALIBRATION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
