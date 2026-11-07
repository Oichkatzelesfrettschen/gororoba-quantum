"""C2 q12-correlation check from retained data: does the selector (q8) assignment depend on what q12 reads?

The q12-flip model of c2_one_cz_mech.py flips the selector's read value with probability x = 0.036 when q12 reads 0. A
flip conditioned on a read value acts at assignment, so the coin series' readout brackets (all 17 qubits prepared 0, then
all five register qubits prepared 1, every shot retained per qubit) measure it directly: P(q8 reads 1) splits by q12's read
value by about x (1 - 2 P(q8 reads 1 | q12 reads 1)) in either bracket. Both bit orders of the shot strings are read; the
selector q8 is the middle bit in either. The check covers the assignment context only: a correlation that appears only
after the template's gate schedule is outside it.
"""

import glob
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUNS = "results/quantum_inspire/runs/2026-11-07T001031Z-pathion_coset_coin_tuna_17-batch-0*/raw/{}.cq.json"
X = 0.036


def split(kind: str, i12: int) -> tuple[int, float, int, float]:
    n0 = s0 = n1 = s1 = 0
    for f in sorted(glob.glob(str(ROOT / RUNS.format(kind)))):
        for s in json.loads(Path(f).read_text()):
            if s[i12] == "1":
                n1 += 1
                s1 += s[8] == "1"
            else:
                n0 += 1
                s0 += s[8] == "1"
    return n0, s0 / n0, n1, s1 / n1


def main() -> None:
    print("selector q8 assignment split by q12's read value, coin series brackets (batches 00-03)")
    for kind in ("readout-0", "readout-1"):
        for order, i12 in (("rightmost bit is q0", 16 - 12), ("leftmost bit is q0", 12)):
            n0, p0, n1, p1 = split(kind, i12)
            d = p0 - p1
            se = math.sqrt(p0 * (1 - p0) / n0 + p1 * (1 - p1) / n1)
            need = X * (1 - 2 * p1)
            print(
                f"  {kind} ({order}): q12 reads 0: n {n0} P(q8=1) {p0:.4f}; q12 reads 1: n {n1} P(q8=1) {p1:.4f};"
                f" difference {d:+.4f} se {se:.4f}; the flip model needs {need:+.4f}, excluded at {abs(need - d) / se:.1f} se"
            )


if __name__ == "__main__":
    main()
