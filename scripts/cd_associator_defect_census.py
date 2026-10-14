"""Census of non-associating basis triples along the Cayley-Dickson ladder.

For the algebra of dimension D = 2^n (cd_core.cd_sign) the basis associator
sign of an ordered triple of imaginary units is omega(a, b, c) = s(a, b)
s(a^b, c) s(b, c) s(a, b^c), the value predict.associator_phase(D, a, b)[c];
-1 marks a triple whose two bracketings differ. Kirshtein
(docs/notes/1207.4230.md, Lemma 3) gives the loop-level sufficient
conditions (associating inside H_8, non-associating when the triple
generates O_16). This census counts the triples and checks closed forms
against exact enumeration:

- every linearly dependent triple (c = a^b) associates, and the ordered
  triples of distinct imaginary units that do not associate number
  N(D) = (D - 2)(D - 4)(D + 6) / 2, so among the (D - 1)(D - 2)(D - 4)
  independent triples the fraction is (D/2 + 3) / (D - 1), tending to 1/2;
- each 3-dimensional index subspace carries either 168 non-associating
  ordered triples or 72, and O(D) = (D - 2)(D - 4)(D + 48) / 1344 carry 168;
- for D >= 16 an independent ordered pair (a, b) has no associating
  completion c exactly when {a, b, a^b} contains D/2, and otherwise exactly
  D/2 - 4;
- omega(1, 6, k) = (-1)^popcount((D - 2) & k), the degree-1 case of the
  associator degree formula max(1, bitlen(j) - 2) (task M1 in the notes);
- the pair (D/2 + 1, D/4 + 3) has Walsh support 5D/16 and largest Walsh
  amplitude 1 - 16/D for D >= 32;
- with the first 24 indices as one coordinate block, ordered pairs from the
  complement whose product index falls in the block number 24D - 704 for
  D >= 32, and ordered pairs from the block landing in the complement
  number 128.

The block counts follow from the XOR structure alone (proof in
docs/notes/cd_associator_defect_census.md). The other closed forms are
finite evidence over the enumerated ranges, and the sampled rates are finite
evidence beyond them; the note carries the literature comparison.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402
from predict import associator_phase  # noqa: E402

SEED = 20261013


def sign_array(dim: int, p: np.ndarray, q: np.ndarray) -> np.ndarray:
    """cd_sign over integer arrays; check_sign_array proves equality on every pair it is used for."""
    p, q = (np.array(x, dtype=np.int64) for x in np.broadcast_arrays(p, q))
    sign = np.ones(p.shape, dtype=np.int8)
    live = np.ones(p.shape, dtype=bool)
    half = dim >> 1
    while half:
        p_hi, q_hi = p >= half, q >= half
        swap = live & ~p_hi & q_hi
        low = q[swap] - half
        q[swap] = p[swap]
        p[swap] = low
        drop = live & p_hi & ~q_hi
        p[drop] -= half
        sign[drop & (q != 0)] *= -1
        both = live & p_hi & q_hi
        stop = both & (q == half)
        sign[stop] *= -1
        live[stop] = False
        go = both & ~stop
        low = q[go] - half
        q[go] = p[go] - half
        p[go] = low
        half >>= 1
    return sign


def omega(dim: int, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return sign_array(dim, a, b) * sign_array(dim, a ^ b, c) * sign_array(dim, b, c) * sign_array(dim, a, b ^ c)


def check_sign_array(max_dim: int, sampled_max: int) -> None:
    """sign_array equals cd_sign on every pair through max_dim and on seeded samples beyond.

    Every dimension the census evaluates, up to sampled_max, is compared with
    cd_sign: exhaustively where feasible and on 4096 seeded pairs (including the
    top-bit operands) above that.
    """
    rng = np.random.default_rng(SEED + 1)
    dim = 2 * max_dim
    while dim <= sampled_max:
        p = np.concatenate([rng.integers(0, dim, 4096), [dim - 1, dim // 2, dim // 2 + 1]])
        q = np.concatenate([rng.integers(0, dim, 4096), [dim // 2, dim - 1, dim // 2]])
        reference = np.array([cd_sign(dim, int(x), int(y)) for x, y in zip(p, q, strict=True)])
        if not np.array_equal(sign_array(dim, p, q), reference):
            raise RuntimeError(f"sign_array differs from cd_sign at dimension {dim}")
        dim *= 2
    dim = 8
    while dim <= max_dim:
        p, q = np.meshgrid(np.arange(dim), np.arange(dim), indexing="ij")
        reference = np.array([[cd_sign(dim, x, y) for y in range(dim)] for x in range(dim)])
        if not np.array_equal(sign_array(dim, p, q), reference):
            raise RuntimeError(f"sign_array differs from cd_sign at dimension {dim}")
        k = np.arange(dim)
        for a, b in ((1, 6), (3, 5), (dim // 2 + 1, dim // 4 + 3)):
            if list(omega(dim, np.full(dim, a), np.full(dim, b), k)) != associator_phase(dim, a, b):
                raise RuntimeError(f"omega differs from associator_phase at dimension {dim}")
        dim *= 2


def triple_counts(dim: int) -> dict[str, int]:
    """Exact counts over ordered triples of distinct imaginary units, one first index at a time."""
    units = np.arange(1, dim)
    b, c = (x.ravel() for x in np.meshgrid(units, units, indexing="ij"))
    defect = dependent_defect = independent = 0
    for a in range(1, dim):
        distinct = (b != a) & (c != a) & (b != c)
        dependent = distinct & (c == (a ^ b))
        free = distinct & ~dependent
        defect += int((omega(dim, np.full(int(free.sum()), a), b[free], c[free]) == -1).sum())
        dependent_defect += int((omega(dim, np.full(int(dependent.sum()), a), b[dependent], c[dependent]) == -1).sum())
        independent += int(free.sum())
    return {"non_associating": defect, "dependent_non_associating": dependent_defect, "independent": independent}


def subspace_types(dim: int) -> Counter[int]:
    """Non-associating ordered independent triples per 3-dimensional index subspace."""
    seen: dict[frozenset[int], int] = {}
    for a, b in itertools.combinations(range(1, dim), 2):
        for c in range(1, dim):
            if c in (a, b, a ^ b):
                continue
            key = frozenset({a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c})
            if key in seen:
                continue
            members = sorted(key)
            triples = np.array(
                [t for t in itertools.permutations(members, 3) if t[2] != (t[0] ^ t[1])],
                dtype=np.int64,
            )
            seen[key] = int((omega(dim, triples[:, 0], triples[:, 1], triples[:, 2]) == -1).sum())
    return Counter(seen.values())


def pair_completions(dim: int) -> dict[str, int]:
    """Counts of independent pairs by associating-completion number, split by whether D/2 is in {a, b, a^b}."""
    half = dim // 2
    rows: Counter[tuple[bool, int]] = Counter()
    units = np.arange(1, dim)
    for a in range(1, dim):
        for b in range(1, dim):
            if b == a:
                continue
            c = units[(units != a) & (units != b) & (units != (a ^ b))]
            associating = int((omega(dim, np.full(len(c), a), np.full(len(c), b), c) == 1).sum())
            rows[(half in (a, b, a ^ b), associating)] += 1
    return {f"{'contains' if hit else 'avoids'}_half:{count}": pairs for (hit, count), pairs in sorted(rows.items())}


def walsh(values: np.ndarray) -> np.ndarray:
    amp = values.astype(np.int64).copy()
    span = 1
    while span < len(amp):
        block = amp.reshape(-1, 2 * span)
        lo, hi = block[:, :span].copy(), block[:, span:].copy()
        block[:, :span], block[:, span:] = lo + hi, lo - hi
        span *= 2
    return amp


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def census(exhaustive_max: int, pair_max: int, subspace_max: int, sample_max: int, samples: int) -> dict[str, object]:
    check_sign_array(min(exhaustive_max, 256), max(exhaustive_max, sample_max, 4096))
    parameters = {
        "exhaustive_max": exhaustive_max,
        "pair_max": pair_max,
        "subspace_max": subspace_max,
        "sample_max": sample_max,
        "samples": samples,
    }
    out: dict[str, object] = {
        "seed": SEED,
        "parameters": parameters,
        "triples": {},
        "subspaces": {},
        "pairs": {},
        "walsh": {},
        "blocks": {},
    }
    triples = out["triples"]
    assert isinstance(triples, dict)
    dim = 8
    while dim <= exhaustive_max:
        counts = triple_counts(dim)
        require(counts["dependent_non_associating"] == 0, f"{dim}: a dependent triple fails to associate")
        require(counts["independent"] == (dim - 1) * (dim - 2) * (dim - 4), f"{dim}: independent triple count")
        require(counts["non_associating"] == (dim - 2) * (dim - 4) * (dim + 6) // 2, f"{dim}: N(D) closed form")
        triples[str(dim)] = counts | {"method": "exhaustive"}
        dim *= 2
    rng = np.random.default_rng(SEED)
    dim = exhaustive_max * 2
    while dim <= sample_max:
        a, b, c = (rng.integers(1, dim, samples) for _ in range(3))
        free = (a != b) & (a != c) & (b != c) & (c != (a ^ b))
        rate = float((omega(dim, a[free], b[free], c[free]) == -1).mean())
        predicted = (dim / 2 + 3) / (dim - 1)
        se = (predicted * (1 - predicted) / int(free.sum())) ** 0.5
        require(abs(rate - predicted) <= 4 * se, f"{dim}: sampled rate {rate} departs from {predicted}")
        triples[str(dim)] = {"method": "sampled", "independent_samples": int(free.sum()), "rate": rate, "se": se}
        dim *= 2
    subspaces = out["subspaces"]
    assert isinstance(subspaces, dict)
    dim = 16
    while dim <= subspace_max:
        types = subspace_types(dim)
        require(set(types) == {72, 168}, f"{dim}: subspace types {sorted(types)}")
        require(types[168] == (dim - 2) * (dim - 4) * (dim + 48) // 1344, f"{dim}: count of 168-type subspaces")
        subspaces[str(dim)] = {"type_168": types[168], "type_72": types[72]}
        dim *= 2
    pairs = out["pairs"]
    assert isinstance(pairs, dict)
    dim = 16
    while dim <= pair_max:
        rows = pair_completions(dim)
        expected = {"avoids_half:" + str(dim // 2 - 4): (dim - 2) * (dim - 4), "contains_half:0": 3 * (dim - 2)}
        require(rows == expected, f"{dim}: pair completions {rows}")
        pairs[str(dim)] = rows
        dim *= 2
    walsh_out = out["walsh"]
    blocks = out["blocks"]
    assert isinstance(walsh_out, dict) and isinstance(blocks, dict)
    for n in range(4, 13):
        dim = 1 << n
        k = np.arange(dim)
        linear = omega(dim, np.full(dim, 1), np.full(dim, 6), k)
        parity = np.array([1 - 2 * (bin((dim - 2) & int(x)).count("1") & 1) for x in k])
        require(np.array_equal(linear, parity), f"{dim}: omega(1, 6, k) parity law")
        spectrum = walsh(omega(dim, np.full(dim, dim // 2 + 1), np.full(dim, dim // 4 + 3), k))
        support, peak = int(np.count_nonzero(spectrum)), int(np.abs(spectrum).max())
        if dim >= 32:
            require(support == 5 * dim // 16 and peak == dim - 16, f"{dim}: cross-scale Walsh law")
            complement = sum(24 <= (i ^ m) < dim for i in range(24, dim) for m in range(24))
            block = sum(24 <= (i ^ j) < dim for i in range(24) for j in range(24))
            require(complement == 24 * dim - 704 and block == 128, f"{dim}: coordinate block counts")
            blocks[str(dim)] = {"complement_pairs_into_block": complement, "block_pairs_into_complement": block}
        walsh_out[str(dim)] = {"cross_scale_support": support, "cross_scale_peak": peak / dim}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exhaustive-max", type=int, default=128)
    parser.add_argument("--pair-max", type=int, default=64)
    parser.add_argument("--subspace-max", type=int, default=32)
    parser.add_argument("--sample-max", type=int, default=4096)
    parser.add_argument("--samples", type=int, default=400_000)
    parser.add_argument("--out", type=Path, help="JSON path; default prints a summary only")
    parser.add_argument("--replay", type=Path, help="retained census JSON to regenerate and compare")
    args = parser.parse_args()
    if args.replay:
        retained = json.loads(args.replay.read_text())
        replayed = census(**retained["parameters"])
        if json.loads(json.dumps(replayed)) != retained:
            raise RuntimeError(f"{args.replay} differs from a fresh census at its recorded parameters")
        print(f"replayed {args.replay}: identical")
        return 0
    result = census(args.exhaustive_max, args.pair_max, args.subspace_max, args.sample_max, args.samples)
    triples = result["triples"]
    assert isinstance(triples, dict)
    for dim, row in triples.items():
        print(f"dim {dim}: {row}")
    print(f"subspaces {result['subspaces']}")
    print(f"pairs {result['pairs']}")
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
