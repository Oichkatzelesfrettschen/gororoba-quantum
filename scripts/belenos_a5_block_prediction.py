"""Exact single-photon predictions of A_5 coset blocks on a 24-mode linear-optics chip, computed offline.

For a two-term operand a = e_i + e_j of the 32-dimensional Cayley-Dickson algebra, L_a splits into blocks over the
cosets of span{i, j} in F_2^5. With alpha = |c_i| + |c_j| = 2 the contraction V = B / alpha has Gram spectrum inside
{0, 1/2, 1} (an orthogonal block gives 1/2, a rank-2 block gives {0, 1}), the case of qd_box_kite_cases.dilation, whose
exact Halmos unitary this module reuses. A photon launched in a basis mode reads the in-block probability
sum_i c_i^2 / alpha^2 = 1/2 on every block of every operand (ledger row A5-371), so basis inputs cannot see the nullity.
A photon prepared in a right singular vector x of B reads |V x|^2 = sigma^2 / alpha^2, which is 0 on a kernel vector and
separates a rank-2 block (1 on its support) from an orthogonal block (1/2). SLOS (Perceval's exact simulator) must
equal the exact value for each prepared input; the record states the quantity a job asks the chip to reproduce. The
numbers are classical and exact, so a job measures the chip, not the algebra.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import qd_box_kite_cases as bk  # noqa: E402

from cd_core import left_mult_matrix  # noqa: E402

DIM = 32
ALPHA = 2
OPERANDS = {"e1+e26": (1, 26), "e1+e10": (1, 10), "e1+e17": (1, 17)}
TOL = 1e-9


def coset_blocks(support: tuple[int, int]) -> list[list[int]]:
    """The index sets of the cosets of span(support) in F_2^5, in order of their least element."""
    span = {0}
    for s in support:
        span |= {x ^ s for x in span}
    seen: set[int] = set()
    blocks: list[list[int]] = []
    for q in range(DIM):
        if q not in seen:
            block = sorted(q ^ s for s in span)
            seen.update(block)
            blocks.append(block)
    return blocks


def to_float(u: bk.Matrix) -> Any:
    return np.array([[float(x[0]) + float(x[1]) * 2**0.5 for x in row] for row in u])


def prepared(unitary: Any, vector: Any) -> Any:
    """The unitary U (P + I) whose column 0 sends mode 0 through an orthogonal P with first column vector."""
    n = len(vector)
    p, _ = np.linalg.qr(np.column_stack([vector, np.eye(n)]))
    p = p[:, :n] * np.sign(p[:, 0] @ vector)
    total = np.eye(unitary.shape[0])
    total[:n, :n] = p
    return unitary @ total


def slos_in_block(unitary: Any, n: int) -> float:
    """Perceval SLOS probability that a photon launched on mode 0 exits on modes 0 to n - 1."""
    import perceval as pcvl

    processor = pcvl.Processor("SLOS", pcvl.Unitary(pcvl.Matrix(unitary)))
    state = [0] * unitary.shape[0]
    state[0] = 1
    processor.with_input(pcvl.BasicState(state))
    probs = processor.probs()["results"]
    return float(sum(p for s, p in probs.items() if sum(s[:n]) == 1))


def block_record(a: Any, block: list[int]) -> dict[str, Any]:
    b = a[np.ix_(block, block)]
    v = [[bk.q(Fraction(int(round(x)), ALPHA)) for x in row] for row in b]
    exact = to_float(bk.dilation(v))
    _, sv, vt = np.linalg.svd(b)
    inputs = []
    for sigma, x in zip(sv, vt, strict=True):
        share = float(sigma**2 / ALPHA**2)
        got = slos_in_block(prepared(exact, x), len(block))
        if abs(got - share) > TOL:
            raise ValueError(f"SLOS reads {got} for a prepared input whose exact share is {share}")
        inputs.append({"sigma": round(float(sigma), 9), "in_block": round(got, 9)})
    basis = round(slos_in_block(exact, len(block)), 9)
    return {
        "block_indices": block,
        "modes_halmos": exact.shape[0],
        "prepared_right_singular_inputs": inputs,
        "nullity": int(sum(sv < TOL)),
        "basis_input_0_in_block": basis,
    }


def record() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, support in OPERANDS.items():
        vec = [0.0] * DIM
        for i in support:
            vec[i] = 1.0
        a = np.array(left_mult_matrix(DIM, vec))
        blocks = [block_record(a, block) for block in coset_blocks(support)]
        out[name] = {
            "support": list(support),
            "global_nullity": int(sum(np.linalg.svd(a, compute_uv=False) < TOL)),
            "block_nullities": [r["nullity"] for r in blocks],
            "first_blocks": blocks[:2],
        }
        if out[name]["global_nullity"] != sum(out[name]["block_nullities"]):
            raise ValueError(f"{name}: block nullities do not sum to the global nullity")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = json.dumps(record(), indent=1, sort_keys=True) + "\n"
    if args.out is None:
        sys.stdout.write(text)
    else:
        args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
