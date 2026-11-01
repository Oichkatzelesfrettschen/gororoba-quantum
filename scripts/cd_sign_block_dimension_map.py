"""Map two-label Cayley-Dickson products at D = 16 .. 8192 onto the 16 retained photonic sign blocks.

Every sign comes from cd_core.cd_sign. For x = e_L + e_U (U = L ^ S) and y = e_L' + t e_U' (U' = L' ^ S):

    M = [[g(L,L'), g(U,U')], [g(U,L'), g(L,U')]],  (c0, c1) = M (1, t),  p_algebra = (c0^2 + c1^2) / 8,

with g = cd_sign(D, ., .). The class is "edge" when det M = 0 (a zero divisor for one sign t, P = 0 or 1)
and "strut" when perm M = 0 (P = 1/2 for both t, no zero divisor). The mutation test flips one entry of M
and requires p_algebra to change. Each enumerated pair is also checked against cd_multiply on the full
D-dimensional vectors, so the 2 x 2 block is the product and not a stand-in for it.

Usage:
  python3 scripts/cd_sign_block_dimension_map.py [--max-index N] [--dims 16,32,...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import cd_multiply, cd_sign  # noqa: E402

Block = tuple[tuple[int, int], tuple[int, int]]


def block(dim: int, low: int, up: int, low2: int, up2: int) -> Block:
    g = cd_sign
    return ((g(dim, low, low2), g(dim, up, up2)), (g(dim, up, low2), g(dim, low, up2)))


def det(m: Block) -> int:
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def perm(m: Block) -> int:
    return m[0][0] * m[1][1] + m[0][1] * m[1][0]


def p_algebra(m: Block, t: int) -> float:
    c0 = m[0][0] + t * m[0][1]
    c1 = m[1][0] + t * m[1][1]
    return (c0 * c0 + c1 * c1) / 8.0


def flip(m: Block, row: int, col: int) -> Block:
    rows = [list(m[0]), list(m[1])]
    rows[row][col] = -rows[row][col]
    return ((rows[0][0], rows[0][1]), (rows[1][0], rows[1][1]))


def full_product_check(dim: int, low: int, up: int, low2: int, up2: int, t: int, m: Block) -> None:
    x = [0.0] * dim
    y = [0.0] * dim
    x[low] = x[up] = 1.0
    y[low2] = 1.0
    y[up2] = float(t)
    z = cd_multiply(dim, x, y)
    expected = (m[0][0] + t * m[0][1]) ** 2 + (m[1][0] + t * m[1][1]) ** 2
    if abs(sum(v * v for v in z) - expected) > 1e-9:
        raise RuntimeError(f"D={dim} pair {(low, up, low2, up2)} t={t}: cd_multiply norm^2 differs from the block")


def mutation_changes_output(m: Block) -> bool:
    for row in (0, 1):
        for col in (0, 1):
            f = flip(m, row, col)
            if all(p_algebra(f, t) == p_algebra(m, t) for t in (1, -1)):
                return False
    return True


def survey(dim: int, strut: int, max_index: int, product_check_limit: int = 64) -> dict[str, object]:
    limit = min(max_index, dim - 1)
    edge = struts = checked = 0
    blocks: dict[Block, int] = {}
    first: dict[str, tuple[int, int]] = {}
    for low in range(1, limit + 1):
        up = low ^ strut
        if up >= dim or up == low:
            continue
        for low2 in range(1, limit + 1):
            up2 = low2 ^ strut
            if up2 >= dim or low2 in (low, up) or up2 in (low, up):
                continue
            m = block(dim, low, up, low2, up2)
            if (det(m) == 0) == (perm(m) == 0):
                raise RuntimeError("a sign block is neither edge nor strut")
            kind = "edge" if det(m) == 0 else "strut"
            if kind == "edge":
                edge += 1
            else:
                struts += 1
            blocks[m] = blocks.get(m, 0) + 1
            first.setdefault(kind, (low, low2))
            if dim <= product_check_limit and checked < 40:
                for t in (1, -1):
                    full_product_check(dim, low, up, low2, up2, t, m)
                checked += 1
    return {
        "dim": dim,
        "strut": strut,
        "edge_pairs": edge,
        "strut_pairs": struts,
        "distinct_blocks": len(blocks),
        "first_edge_L_Lprime": first.get("edge"),
        "first_strut_L_Lprime": first.get("strut"),
        "mutation_ok_on_all_blocks": all(mutation_changes_output(m) for m in blocks),
        "product_checks": checked,
        "blocks": {json.dumps(m): n for m, n in sorted(blocks.items())},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-index", type=int, default=48)
    parser.add_argument("--dims", default="16,32,64,128,256,512,1024,2048,4096,8192")
    args = parser.parse_args()
    report = []
    for dim in (int(v) for v in args.dims.split(",")):
        for strut in sorted({1, 7, dim // 4 + 1, dim // 2 - 1, dim // 2 + 1, dim // 2 + 3, dim - 1}):
            if 0 < strut < dim:
                row = survey(dim, strut, args.max_index)
                report.append(row)
                print(
                    f"D={dim:5d} S={strut:5d} edge={row['edge_pairs']:5d} strut={row['strut_pairs']:5d} "
                    f"blocks={row['distinct_blocks']:2d} mutation_ok={row['mutation_ok_on_all_blocks']} "
                    f"first_edge={row['first_edge_L_Lprime']} first_strut={row['first_strut_L_Lprime']}"
                )
    print(json.dumps({"rows": len(report)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
