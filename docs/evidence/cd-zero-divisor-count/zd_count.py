"""Count |ZD(n)| of Levratti's Definition 2.3 from cd_core signs and compare it with Theorem 7.16.

ZD(n) is the set of ordered pairs (e_i + s e_j, e_k + t e_l), 0 <= i < j < 2^n, 0 <= k < l < 2^n, s, t = +-1, whose
product vanishes. A product of two such elements has four basis terms with +-1 coefficients at indices i^k, i^l, j^k
and j^l; when i^j != k^l the four indices are distinct and the product is nonzero (the paper's Theorem 3.6, Case A),
so the count runs only over pairs sharing one XOR class v = i^j = k^l, about 4^n (2^n - 1) products in place of
16^n. Theorem 7.16 states |ZD(n)| = 336 [n-1 choose 3]_2 for n >= 4.

Writes zd_count.json beside this file. Run from the repository root:
"$PYTHON" docs/evidence/cd-zero-divisor-count/zd_count.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import cd_sign  # noqa: E402

LEVELS = range(3, 8)


def gaussian_binomial(n: int, k: int, q: int = 2) -> int:
    numerator = denominator = 1
    for i in range(k):
        numerator *= q ** (n - i) - 1
        denominator *= q ** (i + 1) - 1
    return numerator // denominator


def zero_divisor_count(n: int) -> int:
    dim = 2**n
    sign = [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]
    count = 0
    for v in range(1, dim):
        elements = [(i, i ^ v, s) for i in range(dim) if i < i ^ v for s in (1, -1)]
        for i, j, s in elements:
            for k, q, t in elements:
                terms: dict[int, int] = defaultdict(int)
                terms[i ^ k] += sign[i][k]
                terms[i ^ q] += t * sign[i][q]
                terms[j ^ k] += s * sign[j][k]
                terms[j ^ q] += s * t * sign[j][q]
                count += all(c == 0 for c in terms.values())
    return count


def main() -> dict[str, object]:
    rows = {}
    for n in LEVELS:
        counted = zero_divisor_count(n)
        predicted = 336 * gaussian_binomial(n - 1, 3) if n >= 4 else None
        rows[str(n)] = {"counted": counted, "theorem_7_16": predicted, "agree": counted == predicted or n < 4}
    return {"definition": "Levratti 2026, Definition 2.3", "levels": rows}


if __name__ == "__main__":
    result = main()
    Path(__file__).with_name("zd_count.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result["levels"]))
