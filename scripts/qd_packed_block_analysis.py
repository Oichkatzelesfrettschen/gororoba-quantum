"""Compare a collected box-kite block job with the ideal algebra fraction of each block.

Per block: a = (samples with one click inside the block that land on an algebra mode) / (samples with exactly one
click inside the block). A block with 0 < p < 1 reports z = (a - p) / sqrt(p (1 - p) / n); a dark or bright block
reports its violation count.

Usage: python3 scripts/qd_packed_block_analysis.py CASE_DIR [CASE_DIR ...]
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path


def analyze(case_dir: Path) -> list[dict[str, object]]:
    results = json.loads((case_dir / "results.json").read_text(encoding="utf-8"))
    manifest = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for index, block in enumerate(manifest["blocks"]):
        offset = block["offset"]
        algebra = [k for k, role in enumerate(block["roles"]) if role != "dilation"]
        width = len(block["roles"])
        one = hit = 0
        for key, count in results["counts"].items():
            modes = [int(v) for v in key.split(",")][offset : offset + width]
            if sum(modes) == 1:
                one += count
                if any(modes[k] for k in algebra):
                    hit += count
        p = float(Fraction(block["p_algebra"])) if block.get("p_algebra") else None
        a = hit / one if one else float("nan")
        row: dict[str, object] = {
            "block": index,
            "m": block.get("m"),
            "t": block.get("t"),
            "ideal": p,
            "n": one,
            "a": a,
        }
        if p is not None and 0 < p < 1 and one:
            row["z"] = (a - p) / math.sqrt(p * (1 - p) / one)
        elif p is not None:
            row["violations"] = one - hit if p == 1 else hit
        rows.append(row)
    return rows


def main() -> int:
    for arg in sys.argv[1:]:
        print(arg)
        for row in analyze(Path(arg)):
            extra = f" z={row['z']:+.2f}" if "z" in row else f" violations={row.get('violations')}"
            print(f"  {row['m']} t={row['t']} ideal={row['ideal']} n={row['n']} a={row['a']:.4f}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
