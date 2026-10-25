"""Endpoint-restricted residue covers behind missing gaps of primorial wheels, and their cost Hamiltonians.

Let P_k be the product of the first k primes and U_L = {1, ..., L - 1}. An
adjacent gap 2L between integers coprime to P_k exists exactly when every odd
prime p | P_k can pick a residue r_p outside {0, L mod p} whose classes
R_{p,r} = {t in U_L : t = r mod p} cover U_L: the Chinese remainder theorem
then gives an odd start x with x = -2 r_p mod p, and p | x + 2t iff
t = r_p mod p. The defect delta_k(L) is the fewest points of U_L an allowed
assignment leaves uncovered, and delta_k(L) + 1 is the fewest consecutive
wheel gaps that sum to 2L.

The module proves, for the instances (k, L) in WITNESSES:

1. an upper witness: an allowed assignment with one uncovered point, its CRT
   start x and the two wheel gaps that sum to 2L;
2. delta_k(L) >= 1 by exhaustion: every assignment of the first BRANCH_PRIMES
   odd primes leaves a residual set that a depth-first search over the
   remaining primes, pruned by the sum of their largest class intersections,
   cannot cover; positive controls at neighboring L find covers;
3. singleton repair: the next prime q >= L, which meets U_L in at most one
   point per class, closes the gap;
4. the linear relaxation (fractional class weights per prime summing to one,
   every point covered to weight one) reaches zero at k = 14 through HiGHS,
   and the returned weights, rounded to rationals, satisfy every constraint in
   exact arithmetic.

On the cost side, the defect is the ground energy of the diagonal operator
H_D = sum_t prod_p (I - Pi_{p,t}). Freezing all residues of a witness except a
two-valued choice for p = 5, 7, 11 gives a three-bit cost table E(x), bit j
selecting the second residue of SLICE_DOMAINS[case][j]; its Walsh
coefficients c_S = 2^-n sum_x E(x) (-1)^{x . S} define H = sum_S c_S Z_S with
Z_j |x> = (1 - 2 x_j) |x> (bit j on qubit j, little-endian). The two-bit
quotient of the gap-20 instance and the eight-CNOT adjacent parity network
(CX_{0,1} CX_{1,2})^4, the shortest adjacent network on a path that visits
every nonzero parity of three bits and returns to the identity map, complete
the circuit inputs of scripts/primorial_cover_noise.py.

``--out FILE`` writes the certificate record; ``--check FILE`` recomputes it
and requires byte equality with FILE.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import parallel

SCHEMA = "gororoba-primorial-cover-certificates-v1"

# Upper witnesses: residues for the odd primes 3, 5, ..., p_k in ascending order.
WITNESSES: dict[tuple[int, int], tuple[int, ...]] = {
    (6, 10): (2, 4, 6, 1, 7),
    (8, 16): (2, 4, 6, 1, 10, 15, 7),
    (14, 43): (2, 4, 4, 5, 2, 13, 12, 10, 7, 6, 3, 1, 21),
    (14, 44): (1, 3, 6, 3, 4, 9, 5, 12, 3, 11, 2, 21, 15),
}
# Odd primes enumerated exhaustively before the depth-first search takes over.
BRANCH_PRIMES = {(6, 10): 2, (8, 16): 3, (14, 43): 5, (14, 44): 4}
# Neighboring half-lengths whose gaps exist, so the search must find a cover.
POSITIVE_CONTROLS = ((6, 9), (6, 11), (8, 15), (8, 17), (14, 42), (14, 45))

# Three-bit conditional slices: (prime, (residue at bit 0, residue at bit 1)).
SLICE_DOMAINS: dict[str, tuple[int, tuple[tuple[int, tuple[int, int]], ...]]] = {
    "gap86": (43, ((5, (4, 1)), (7, (4, 2)), (11, (5, 1)))),
    "gap88": (44, ((5, (3, 1)), (7, (6, 1)), (11, (3, 1)))),
}
# Repair class of the next prime 47 added to each slice.
SLICE_REPAIRS = {"gap86": (47, 22), "gap88": (47, 29)}

# Gap-20 quotient after the forced prime-3 class: prime 5 and 7 domains, two bits each.
QUOTIENT_RESIDUAL = (1, 3, 4, 6, 7, 9)
QUOTIENT_DOMAINS = ((5, (1, 2, 3, 4)), (7, (1, 2, 4, 6)))
# Primes 11 and 13 each remove one point of the residual set.
QUOTIENT_SINGLETONS = 2

# One-layer ansatz exp(-i beta sum X) exp(-i gamma H) |+++> at angles on the pi/36 grid.
QAOA_ANGLES = {"gap86": (math.pi / 9, 55 * math.pi / 72), "gap88": (2 * math.pi / 9, 55 * math.pi / 72)}


def primes_up_to(n: int) -> list[int]:
    return [p for p in range(2, n + 1) if all(p % q for q in range(2, math.isqrt(p) + 1))]


def odd_primes(k: int) -> list[int]:
    """The odd primes among the first k primes."""
    return primes_up_to(k * k + 100)[1:k]


def allowed(p: int, half: int) -> list[int]:
    return [r for r in range(p) if r not in (0, half % p)]


def class_mask(p: int, r: int, half: int) -> int:
    """Bit t - 1 set for every t in U_L with t = r mod p, for 0 < r < p."""
    return sum(1 << (t - 1) for t in range(r, half, p))


def uncovered(half: int, primes: list[int], residues: tuple[int, ...] | list[int]) -> list[int]:
    return [t for t in range(1, half) if all(t % p != r for p, r in zip(primes, residues, strict=True))]


def crt_start(primes: list[int], residues: tuple[int, ...]) -> tuple[int, int]:
    """Odd x with x = -2 r_p mod p for every p, and the modulus 2 prod p."""
    x, modulus = 1, 2
    for p, r in zip(primes, residues, strict=True):
        step = ((-2 * r - x) * pow(modulus, -1, p)) % p
        x, modulus = x + modulus * step, modulus * p
    return x, modulus


def wheel_gaps(x: int, modulus: int, half: int) -> list[int]:
    survivors = [y for y in range(x, x + 2 * half + 1) if math.gcd(y, modulus) == 1]
    return [b - a for a, b in zip(survivors, survivors[1:], strict=False)]


def _coverable(remaining: int, masks: list[list[int]]) -> bool:
    """Whether one class per prime in masks covers every bit of remaining."""
    if remaining == 0:
        return True
    if not masks:
        return False
    if remaining.bit_count() > sum(max((remaining & m).bit_count() for m in row) for row in masks):
        return False
    return any(
        _coverable(remaining & ~m, masks[1:]) for m in sorted(masks[0], key=lambda m: -(remaining & m).bit_count())
    )


class BranchCheck:
    """Picklable worker: one assignment of the branch primes -> (coverable, whole-interval Hall bound)."""

    def __init__(self, half: int, tail: list[list[int]]) -> None:
        self.half = half
        self.tail = tail

    def __call__(self, covered: int) -> tuple[bool, int]:
        remaining = ((1 << (self.half - 1)) - 1) & ~covered
        capacity = sum(max((remaining & m).bit_count() for m in row) for row in self.tail)
        return _coverable(remaining, self.tail), remaining.bit_count() - capacity


def exhaust(half: int, primes: list[int], branch: int) -> dict[str, Any]:
    """Every assignment of primes[:branch], each residual searched over primes[branch:]."""
    masks = [[class_mask(p, r, half) for r in allowed(p, half)] for p in primes]
    tail = sorted(masks[branch:], key=len)
    covers = [_union(combo) for combo in itertools.product(*masks[:branch])]
    results = parallel.ordered_map(BranchCheck(half, tail), covers)
    bounds = [bound for _, bound in results]
    return {
        "branch_primes": primes[:branch],
        "branches": len(results),
        "coverable_branches": sum(1 for ok, _ in results if ok),
        "whole_interval_bound_nonpositive": sum(1 for b in bounds if b <= 0),
    }


def _union(masks: tuple[int, ...]) -> int:
    out = 0
    for m in masks:
        out |= m
    return out


def cover_exists(half: int, primes: list[int]) -> bool:
    masks = sorted(([class_mask(p, r, half) for r in allowed(p, half)] for p in primes), key=len)
    return _coverable((1 << (half - 1)) - 1, masks)


def hall_deficiency(points: tuple[int, ...], half: int, primes: list[int]) -> tuple[list[int], int]:
    capacities = [max(sum(1 for t in points if t % p == r) for r in allowed(p, half)) for p in primes]
    return capacities, len(points) - sum(capacities)


def lp_defect(half: int, primes: list[int]) -> dict[str, Any]:
    """Fractional-cover optimum through HiGHS and an exact check of its rationalized weights."""
    from scipy.optimize import linprog

    classes = [(p, r) for p in primes for r in allowed(p, half)]
    points = list(range(1, half))
    n = len(classes) + len(points)
    cost = np.r_[np.zeros(len(classes)), np.ones(len(points))]
    a_eq = np.zeros((len(primes), n))
    for i, p in enumerate(primes):
        a_eq[i, [j for j, (q, _) in enumerate(classes) if q == p]] = 1.0
    a_ub = np.zeros((len(points), n))
    for i, t in enumerate(points):
        a_ub[i, [j for j, (q, r) in enumerate(classes) if t % q == r]] = -1.0
        a_ub[i, len(classes) + i] = -1.0
    solved = linprog(
        cost, A_ub=a_ub, b_ub=-np.ones(len(points)), A_eq=a_eq, b_eq=np.ones(len(primes)), bounds=(0, None)
    )
    if solved.status != 0:
        raise RuntimeError(f"linprog status {solved.status} at L = {half}: {solved.message}")
    weights = {cls: Fraction(float(v)).limit_denominator(1 << 12) for cls, v in zip(classes, solved.x, strict=False)}
    exact = all(sum(w for (q, _), w in weights.items() if q == p) == 1 for p in primes) and all(
        sum(w for (q, r), w in weights.items() if t % q == r) >= 1 for t in points
    )
    nonneg = all(w >= 0 for w in weights.values())
    return {
        "highs_optimum": round(float(solved.fun), 9),
        "rational_fractional_cover": bool(exact and nonneg),
    }


def walsh(table: list[int]) -> dict[str, Fraction]:
    """c_S keyed by the qubits of S joined ('' for the identity)."""
    n = int(math.log2(len(table)))
    out = {}
    for size in range(n + 1):
        for subset in itertools.combinations(range(n), size):
            total = sum(e * (-1) ** sum((x >> j) & 1 for j in subset) for x, e in enumerate(table))
            out["".join(map(str, subset))] = Fraction(total, len(table))
    return out


def inverse_walsh(coefficients: dict[str, Fraction], n: int) -> list[Fraction]:
    return [
        sum(
            (c * (-1) ** sum((x >> int(j)) & 1 for j in key) for key, c in coefficients.items()),
            start=Fraction(0),
        )
        for x in range(1 << n)
    ]


def slice_table(case: str, repaired: bool = False) -> list[int]:
    half, domains = SLICE_DOMAINS[case]
    k = 14
    primes = odd_primes(k)
    base = list(WITNESSES[(k, half)])
    index = {p: i for i, p in enumerate(primes)}
    table = []
    for x in range(8):
        residues = base[:]
        for bit, (p, choice) in enumerate(domains):
            residues[index[p]] = choice[(x >> bit) & 1]
        for p, r in zip(primes, residues, strict=True):
            if r not in allowed(p, half):
                raise ValueError(f"{case}: residue {r} mod {p} is forbidden at L = {half}")
        if repaired:
            q, r = SLICE_REPAIRS[case]
            table.append(len(uncovered(half, [*primes, q], [*residues, r])))
        else:
            table.append(len(uncovered(half, primes, residues)))
    return table


def quotient_table() -> list[int]:
    """Gap-20 cost over (r_5, r_7), two bits each, x = b0 + 2 b1 + 4 b2 + 8 b3."""
    (p5, d5), (p7, d7) = QUOTIENT_DOMAINS
    return [
        max(0, sum(1 for t in QUOTIENT_RESIDUAL if t % p5 != d5[x & 3] and t % p7 != d7[x >> 2]) - QUOTIENT_SINGLETONS)
        for x in range(16)
    ]


def parity_network() -> dict[str, Any]:
    """Masks the network (CX_{0,1} CX_{1,2})^4 writes, and the BFS minimum of the adjacent-CNOT model."""
    wires, visited = [1, 2, 4], []
    for _ in range(4):
        wires[1] ^= wires[0]
        visited.append(wires[1])
        wires[2] ^= wires[1]
        visited.append(wires[2])
    start: tuple[tuple[int, ...], frozenset[int]] = ((1, 2, 4), frozenset((1, 2, 4)))
    queue = deque([(start, 0)])
    seen = {start}
    minimum = -1
    while queue:
        (state, cover), depth = queue.popleft()
        if state == (1, 2, 4) and len(cover) == 7:
            minimum = depth
            break
        for control, target in ((0, 1), (1, 0), (1, 2), (2, 1)):
            nxt = list(state)
            nxt[target] ^= nxt[control]
            key = (tuple(nxt), cover | {nxt[target]})
            if key not in seen:
                seen.add(key)
                queue.append((key, depth + 1))
    return {"written_masks": visited, "final_masks": wires, "bfs_minimum_cnots": minimum}


def qaoa_law(table: list[int], gamma: float, beta: float) -> np.ndarray:
    """Outcome law of exp(-i beta sum X) exp(-i gamma diag(table)) |+>^n."""
    n = int(math.log2(len(table)))
    state = np.exp(-1j * gamma * np.asarray(table, dtype=float)) / math.sqrt(len(table))
    mixer = np.array([[math.cos(beta), -1j * math.sin(beta)], [-1j * math.sin(beta), math.cos(beta)]])
    full = np.ones((1, 1), dtype=complex)
    for _ in range(n):
        full = np.kron(mixer, full)
    law: np.ndarray = np.abs(full @ state) ** 2
    return law


def _fractions(coefficients: dict[str, Fraction]) -> dict[str, str]:
    return {key: str(value) for key, value in coefficients.items()}


def certificates() -> dict[str, Any]:
    instances = []
    for (k, half), residues in WITNESSES.items():
        primes = odd_primes(k)
        for p, r in zip(primes, residues, strict=True):
            if r not in allowed(p, half):
                raise ValueError(f"witness ({k}, {half}): residue {r} mod {p} is forbidden")
        x, modulus = crt_start(primes, residues)
        q = next(p for p in primes_up_to(4 * half) if p > primes[-1] and p >= half)
        row: dict[str, Any] = {
            "k": k,
            "half_length": half,
            "gap": 2 * half,
            "witness_residues": list(residues),
            "witness_uncovered": uncovered(half, primes, residues),
            "crt_start": x,
            "modulus": modulus,
            "wheel_gaps": wheel_gaps(x, modulus, half),
            "exhaustion": exhaust(half, primes, BRANCH_PRIMES[(k, half)]),
            "assignments": math.prod(len(allowed(p, half)) for p in primes),
            "one_hot_variables": sum(len(allowed(p, half)) for p in primes),
            "binary_bits": sum(math.ceil(math.log2(len(allowed(p, half)))) for p in primes),
            "repair_prime": q,
            "repair_covers": cover_exists(half, [*primes, q]),
        }
        if k == 14:
            row["linear_relaxation"] = lp_defect(half, primes)
        instances.append(row)
    hall = {
        f"{k},{half}": dict(
            zip(("capacities", "deficiency"), hall_deficiency(points, half, odd_primes(k)), strict=True)
        )
        for (k, half), points in {(6, 10): (1, 3, 4, 6, 7, 9), (8, 16): (1, 3, 4, 6, 7, 9, 10, 12, 13, 15)}.items()
    }
    controls = [
        {"k": k, "half_length": half, "covers": cover_exists(half, odd_primes(k))} for k, half in POSITIVE_CONTROLS
    ]
    slices: dict[str, Any] = {}
    for case, (gamma, beta) in QAOA_ANGLES.items():
        plain, fixed = slice_table(case), slice_table(case, repaired=True)
        c_plain, c_fixed = walsh(plain), walsh(fixed)
        for table, coeffs in ((plain, c_plain), (fixed, c_fixed)):
            if inverse_walsh(coeffs, 3) != [Fraction(e) for e in table]:
                raise ValueError(f"{case}: inverse Walsh transform departs from the table")
        laws = [qaoa_law(t, gamma, beta) for t in (plain, fixed)]
        slices[case] = {
            "table": plain,
            "repaired_table": fixed,
            "coefficients": _fractions(c_plain),
            "repaired_coefficients": _fractions(c_fixed),
            "repair_shift": _fractions({k: c_fixed[k] - c_plain[k] for k in c_plain if c_fixed[k] != c_plain[k]}),
            "qaoa_gamma_over_pi": str(Fraction(gamma / math.pi).limit_denominator(72)),
            "qaoa_beta_over_pi": str(Fraction(beta / math.pi).limit_denominator(72)),
            "qaoa_ground_probability": [
                round(float(law[int(np.argmin(t))]), 9) for law, t in zip(laws, (plain, fixed), strict=True)
            ],
            "qaoa_mean_cost": [
                round(float(law @ np.asarray(t)), 9) for law, t in zip(laws, (plain, fixed), strict=True)
            ],
            "qaoa_total_variation": round(float(0.5 * np.abs(laws[0] - laws[1]).sum()), 9),
        }
    quotient = quotient_table()
    return {
        "schema": SCHEMA,
        "instances": instances,
        "hall_subsets": hall,
        "positive_controls": controls,
        "slices": slices,
        "quotient": {"table": quotient, "coefficients": _fractions({k: v for k, v in walsh(quotient).items() if v})},
        "parity_network": parity_network(),
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = render(certificates())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print(f"{args.check} departs from the recomputed certificates")
        return 1
    print(f"{args.check}: certificates reproduce")
    return 0


if __name__ == "__main__":
    sys.exit(main())
