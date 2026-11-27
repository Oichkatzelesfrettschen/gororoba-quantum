"""Pauli-plus-sparse-flip structure of the Cayley-Dickson sign table and the residue decoupling, exact for n = 3 to 8.

With f(p, q) in F_2 and (-1)^f(p, q) = cd_core.cd_sign(2^n, p, q) (the specification), the script decides:

- degrees (S1): the F_2 degree of f is 2, 2, 3, 4, 5, 6, 7, 8 for n = 1 to 8; the row q -> f(p, q) has degree n - 1 for
  every p != 0 and n >= 2; the associator sign f(p, q) + f(p ^ q, r) + f(q, r) + f(p, q ^ r) has degree n for
  n = 3 to ASSOC_MAX, and its support has (D - 2)(D - 4)(D + 6)/2 points;
- flip structure (S2): each row p equals c_p + u_p . q except on a flip set F_p, with (u_p, c_p, F_p) given by the
  doubling recursion from the octonion seed; the recursion output equals the exact closest affine function and its
  mismatch set for n = 4 to 8 (unique there), and reproduces every row exactly for n = 3 to 8;
- bound: |F_p| <= 2^(n-2) - 2, from |F_n(p)| <= 2 |F_(n-1)(p)| + 2 and the n = 4 maximum 2, so the closest affine
  function is unique for n >= 4;
- lemmas of the written proof: the transposition identity s(q, p) = s(p, q) (-1)^[p, q > 0, p != q] and the four
  doubling cases of cd_sign, each as an exhaustive finite check;
- residue decoupling (S3): for p mod 8 = r != 0, F_p lies in {q : q mod 8 in {0, r}}, and L_a equals its Pauli part on
  every basis vector outside that set for each a supported on the class r.

--self-test runs paired controls that each must fail: a perturbed sign table, a wrong seed, an alternate closest
affine seed at n = 3, a residue modulus of 16, the transposition identity without its correction, and a degree
engine calibrated on known functions. Independent items run through parallel.ordered_map. No random draw enters.

Usage:
    "$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --self-test
    "$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --write
    "$PYTHON" -B -W error docs/evidence/cd-sign-pauli-structure/cd_sign_pauli_structure.py --check
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

RESULT = HERE / "result.json"
LEVEL_MIN = 3
LEVEL_MAX = 8
ASSOC_MAX = 8
# Octonion seed: row p of A_3 is (-1)^(SEED_C[p] + SEED_U[p] . q) except at q in {0, p} (p != 0).
SEED_U = (0, 7, 6, 5, 4, 1, 3, 2)
SEED_C = (0, 1, 1, 1, 1, 1, 1, 1)
Level = list[tuple[int, int, frozenset[int]]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parity(x: int) -> int:
    return x.bit_count() & 1


# ---------------------------------------------------------------------------------------------------------------
# Truth tables and the algebraic normal form, as Python integers used as bit sets


def row_bits(n: int, p: int) -> int:
    """Bit q of the result is f(p, q), with (-1)^f = cd_core.cd_sign(2^n, p, q)."""
    dim = 1 << n
    return sum(((1 - cd_core.cd_sign(dim, p, q)) >> 1) << q for q in range(dim))


@functools.cache
def block_mask(k: int, i: int) -> int:
    """Over 2^k positions, the indices whose bit i is 0."""
    mask = (1 << (1 << i)) - 1
    width = 2 << i
    while width < (1 << k):
        mask |= mask << width
        width <<= 1
    return mask


def anf(table: int, k: int) -> int:
    """Moebius transform over F_2: the coefficient of the monomial with variable set m is bit m of the result."""
    for i in range(k):
        table ^= (table & block_mask(k, i)) << (1 << i)
    return table


@functools.cache
def weight_masks(k: int) -> tuple[int, ...]:
    """Entry w holds the indices below 2^k of popcount w."""
    masks = [1]
    for i in range(k):
        shifted = [m << (1 << i) for m in masks]
        masks = [(masks[w] if w < len(masks) else 0) | (shifted[w - 1] if w >= 1 else 0) for w in range(len(masks) + 1)]
    return tuple(masks)


def degree(table: int, k: int) -> int:
    """F_2 degree of the function on k variables with the given truth table; -1 for the zero function."""
    coefficients = anf(table, k)
    best = -1
    for w, mask in enumerate(weight_masks(k)):
        if coefficients & mask:
            best = w
    return best


def walsh(row: int, n: int) -> list[int]:
    """Fast Walsh-Hadamard transform of (-1)^f, exact integers."""
    dim = 1 << n
    values = [1 - 2 * ((row >> q) & 1) for q in range(dim)]
    step = 1
    while step < dim:
        for start in range(0, dim, 2 * step):
            for j in range(start, start + step):
                a, b = values[j], values[j + step]
                values[j], values[j + step] = a + b, a - b
        step *= 2
    return values


def analyze_row(n: int, row: int) -> dict[str, Any]:
    """Closest affine functions of one row: the maximal |Walsh| value, its multiplicity and one representative."""
    dim = 1 << n
    spectrum = walsh(row, n)
    top = max(abs(v) for v in spectrum)
    best = [w for w in range(dim) if abs(spectrum[w]) == top]
    w0 = best[0]
    c0 = 0 if spectrum[w0] > 0 else 1
    flips = tuple(q for q in range(dim) if ((row >> q) & 1) != (c0 ^ parity(w0 & q)))
    return {"u": w0, "c": c0, "flips": flips, "count": len(best), "distance": (dim - top) // 2}


def row_item(task: tuple[int, int]) -> dict[str, Any]:
    n, p = task
    row = row_bits(n, p)
    return {"row": row, **analyze_row(n, row)}


# ---------------------------------------------------------------------------------------------------------------
# The doubling recursion of the written proof


def seed_level(
    u: tuple[int, ...] = SEED_U, c: tuple[int, ...] = SEED_C, flips: dict[int, frozenset[int]] | None = None
) -> Level:
    sets = flips if flips is not None else {p: frozenset({0, p}) if p else frozenset() for p in range(8)}
    return [(u[p], c[p], sets[p]) for p in range(8)]


def double_level(level: Level) -> Level:
    """(u, c, F) of A_(n+1) from those of A_n, with D = 2^n."""
    d = len(level)
    out: Level = [(0, 0, frozenset())]
    for p in range(1, d):
        u, c, f = level[p]
        out.append((u | d, c, f | frozenset(d + x for x in f) ^ frozenset({d, d + p})))
    out.append((d, 1, frozenset({0, d})))
    for p in range(1, d):
        u, c, f = level[p]
        out.append((u, c ^ 1, (f ^ frozenset({0})) | frozenset(d + x for x in f) ^ frozenset({d + p})))
    return out


def build_levels(seed: Level, n_max: int = LEVEL_MAX) -> dict[int, Level]:
    levels = {LEVEL_MIN: seed}
    for n in range(LEVEL_MIN + 1, n_max + 1):
        levels[n] = double_level(levels[n - 1])
    return levels


def reconstruct(n: int, entry: tuple[int, int, frozenset[int]]) -> int:
    u, c, f = entry
    return sum((c ^ parity(u & q) ^ (q in f)) << q for q in range(1 << n))


def level_hash(level: Level) -> str:
    text = ";".join(f"{u},{c},{'.'.join(map(str, sorted(f)))}" for u, c, f in level)
    return hashlib.sha256(text.encode()).hexdigest()


def compare_level(n: int, level: Level, measured: list[dict[str, Any]]) -> dict[str, int]:
    """Rows reproduced exactly, and rows whose (u, c, F) differs from the measured closest affine function."""
    exact = sum(reconstruct(n, level[p]) == measured[p]["row"] for p in range(1 << n))
    differing = sum(
        (level[p][0], level[p][1], level[p][2]) != (m["u"], m["c"], frozenset(m["flips"]))
        for p, m in enumerate(measured)
    )
    return {"rows": 1 << n, "rows_exact": exact, "rows_differing_from_closest_affine": differing}


# ---------------------------------------------------------------------------------------------------------------
# Residue decoupling


def residue_report(n: int, level: Level, rows: list[int], modulus: int = 8) -> dict[str, int]:
    """Check F_p inside {q : q mod m in {0, p mod m}} and the Pauli-part equality outside it, for p mod m != 0."""
    dim = 1 << n
    violations = pauli_mismatch = checked = flips_in_class = flips_in_zero = leaving = 0
    for p in range(1, dim):
        r = p % modulus
        if r == 0:
            continue
        u, c, f = level[p]
        checked += 1
        for q in f:
            if q % modulus not in (0, r):
                violations += 1
            elif q % modulus == r:
                flips_in_class += 1
            else:
                flips_in_zero += 1
        for q in range(dim):
            if q % modulus not in (0, r):
                pauli_mismatch += ((rows[p] >> q) & 1) != (c ^ parity(u & q))
                leaving += (p ^ q) % modulus in (0, r)
    return {
        "rows_checked": checked,
        "flip_violations": violations,
        "pauli_part_mismatches_outside": pauli_mismatch,
        "outside_set_leaving_images": leaving,
        "flips_in_class_r": flips_in_class,
        "flips_in_class_0": flips_in_zero,
    }


# ---------------------------------------------------------------------------------------------------------------
# Lemmas of the written proof, as exhaustive finite checks


def sign_bit(dim: int, p: int, q: int) -> int:
    return (1 - cd_core.cd_sign(dim, p, q)) >> 1


def transposition_failures(n: int, corrected: bool = True) -> int:
    """Pairs with s(q, p) != s(p, q) (-1)^[p, q > 0, p != q]; the correction is dropped when corrected is false."""
    dim = 1 << n
    bad = 0
    for p in range(dim):
        for q in range(dim):
            t = int(p > 0 and q > 0 and p != q) if corrected else 0
            bad += sign_bit(dim, q, p) != sign_bit(dim, p, q) ^ t
    return bad


def doubling_failures(n: int) -> int:
    """Pairs of A_(n+1) whose sign differs from the four doubling cases written over A_n (D = 2^n)."""
    d = 1 << n
    bad = 0
    for p in range(2 * d):
        for q in range(2 * d):
            ph, pl, qh, ql = p >= d, p % d, q >= d, q % d
            if not ph and not qh:
                want = sign_bit(d, pl, ql)
            elif not ph and qh:
                want = sign_bit(d, ql, pl)
            elif ph and not qh:
                want = sign_bit(d, pl, ql) ^ int(ql != 0)
            else:
                want = sign_bit(d, ql, pl) ^ int(ql == 0)
            bad += sign_bit(2 * d, p, q) != want
    return bad


def transposition_item(n: int) -> int:
    return transposition_failures(n)


def doubling_item(n: int) -> int:
    return doubling_failures(n)


# ---------------------------------------------------------------------------------------------------------------
# Associator sign


def assoc_item(task: tuple[int, int, tuple[int, ...]]) -> int:
    """Block p of the truth table of f(p, q) + f(p ^ q, r) + f(q, r) + f(p, q ^ r), at index q * 2^n + r."""
    n, p, rows = task
    dim = 1 << n
    full = (1 << dim) - 1
    fp = [(rows[p] >> q) & 1 for q in range(dim)]
    out = 0
    for q in range(dim):
        shifted = sum(fp[q ^ r] << r for r in range(dim))
        block = rows[p ^ q] ^ rows[q] ^ shifted ^ (full if fp[q] else 0)
        out |= block << (q * dim)
    return out


def associator_report(n: int, rows: list[int]) -> dict[str, int]:
    dim = 1 << n
    blocks = parallel.ordered_map(assoc_item, [(n, p, tuple(rows)) for p in range(dim)], min_items=1)
    table = sum(b << (p * dim * dim) for p, b in enumerate(blocks))
    return {
        "nonassociating_triples": table.bit_count(),
        "formula": (dim - 2) * (dim - 4) * (dim + 6) // 2 if dim >= 4 else 0,
        "degree": degree(table, 3 * n),
    }


# ---------------------------------------------------------------------------------------------------------------
# The record


def measure() -> dict[int, list[dict[str, Any]]]:
    tasks = [(n, p) for n in range(1, LEVEL_MAX + 1) for p in range(1 << n)]
    items = parallel.ordered_map(row_item, tasks, min_items=1)
    out: dict[int, list[dict[str, Any]]] = {n: [] for n in range(1, LEVEL_MAX + 1)}
    for (n, _p), item in zip(tasks, items, strict=True):
        out[n].append(item)
    return out


def degree_record(n: int, rows: list[int]) -> dict[str, Any]:
    dim = 1 << n
    table = sum(r << (p * dim) for p, r in enumerate(rows))
    row_degrees = sorted({degree(rows[p], n) for p in range(1, dim)})
    return {"f": degree(table, 2 * n), "row_degrees": row_degrees}


def flip_record(n: int, level: Level, measured: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = [len(level[p][2]) for p in range(1 << n)]
    histogram: dict[int, int] = {}
    for s in sizes:
        histogram[s] = histogram.get(s, 0) + 1
    out: dict[str, Any] = {
        **compare_level(n, level, measured),
        "max_flips": max(sizes),
        "bound_2^(n-2)-2": (1 << (n - 2)) - 2,
        "flip_histogram": histogram,
        "rows_with_several_closest_affine": sum(m["count"] > 1 for m in measured),
        "level_sha256": level_hash(level),
    }
    if n <= 5:
        out["table"] = [[u, c, sorted(f)] for u, c, f in level]
    return out


def build_record() -> dict[str, Any]:
    measured = measure()
    rows = {n: [m["row"] for m in measured[n]] for n in measured}
    levels = build_levels(seed_level())
    record: dict[str, Any] = {"seed": {"u": list(SEED_U), "c": list(SEED_C)}, "levels": {}, "degrees": {}}
    for n in range(1, LEVEL_MAX + 1):
        record["degrees"][n] = degree_record(n, rows[n])
    for n in range(LEVEL_MIN, LEVEL_MAX + 1):
        entry = flip_record(n, levels[n], measured[n])
        entry["residue_mod_8"] = residue_report(n, levels[n], rows[n])
        record["levels"][n] = entry
    for n in range(LEVEL_MIN, ASSOC_MAX + 1):
        record["degrees"][n]["associator"] = associator_report(n, rows[n])
    record["lemmas"] = {
        "transposition_failures": dict(
            zip(
                range(1, LEVEL_MAX + 1),
                parallel.ordered_map(transposition_item, list(range(1, LEVEL_MAX + 1)), min_items=1),
                strict=True,
            )
        ),
        "doubling_failures": dict(
            zip(
                range(1, LEVEL_MAX),
                parallel.ordered_map(doubling_item, list(range(1, LEVEL_MAX)), min_items=1),
                strict=True,
            )
        ),
    }
    return record


def validate(record: dict[str, Any]) -> None:
    """Every statement of the record, as a failing assertion."""
    expected = {1: 2, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
    for n, want in expected.items():
        d = record["degrees"][n]
        require(d["f"] == want, f"degree of f at n = {n}")
        if n >= 2:
            require(d["row_degrees"] == [n - 1], f"row degrees at n = {n}")
    for n in range(LEVEL_MIN, ASSOC_MAX + 1):
        a = record["degrees"][n]["associator"]
        require(a["degree"] == n, f"associator degree at n = {n}")
        require(a["nonassociating_triples"] == a["formula"], f"associator count at n = {n}")
    previous = 0
    for n in range(LEVEL_MIN, LEVEL_MAX + 1):
        lv = record["levels"][n]
        require(lv["rows_exact"] == lv["rows"], f"rows reproduced at n = {n}")
        require(lv["max_flips"] <= lv["bound_2^(n-2)-2"] or n == 3, f"flip bound at n = {n}")
        if n >= 4:
            require(lv["rows_differing_from_closest_affine"] == 0, f"closest affine at n = {n}")
            require(lv["rows_with_several_closest_affine"] == 0, f"unique closest affine at n = {n}")
            require(lv["max_flips"] <= 2 * previous + 2, f"flip growth at n = {n}")
        res = lv["residue_mod_8"]
        require(
            res["flip_violations"] == 0
            and res["pauli_part_mismatches_outside"] == 0
            and res["outside_set_leaving_images"] == 0,
            f"residue at n = {n}",
        )
        previous = lv["max_flips"]
    require(all(v == 0 for v in record["lemmas"]["transposition_failures"].values()), "transposition identity")
    require(all(v == 0 for v in record["lemmas"]["doubling_failures"].values()), "doubling cases")


# ---------------------------------------------------------------------------------------------------------------
# Controls


def alternate_seed(measured3: list[dict[str, Any]]) -> Level:
    """A valid but non-standard octonion seed: for each row the lexicographically last closest affine function."""
    dim = 8
    level: Level = [(0, 0, frozenset())]
    for p in range(1, dim):
        row = measured3[p]["row"]
        spectrum = walsh(row, 3)
        top = max(abs(v) for v in spectrum)
        w = max(w for w in range(dim) if abs(spectrum[w]) == top)
        c = 0 if spectrum[w] > 0 else 1
        flips = frozenset(q for q in range(dim) if ((row >> q) & 1) != (c ^ parity(w & q)))
        level.append((w, c, flips))
    return level


def self_test() -> None:
    measured = {n: parallel.ordered_map(row_item, [(n, p) for p in range(1 << n)], min_items=1) for n in range(3, 6)}
    good = build_levels(seed_level(), 5)
    for n in range(4, 6):
        c = compare_level(n, good[n], measured[n])
        require(c["rows_exact"] == c["rows"] and c["rows_differing_from_closest_affine"] == 0, "known-good recursion")
    # Control 1: one sign of the table perturbed.
    perturbed = [dict(m) for m in measured[5]]
    perturbed[5] = {**analyze_row(5, measured[5][5]["row"] ^ (1 << 9)), "row": measured[5][5]["row"] ^ (1 << 9)}
    c1 = compare_level(5, good[5], perturbed)
    require(
        c1["rows_exact"] == c1["rows"] - 1 and c1["rows_differing_from_closest_affine"] >= 1, "perturbed table passes"
    )
    # Control 2: a wrong seed (one row's u changed).
    bad_u = (SEED_U[0], 6, *SEED_U[2:])
    bad = build_levels(seed_level(u=bad_u), 5)
    c2 = compare_level(4, bad[4], measured[4])
    require(c2["rows_exact"] < c2["rows"], "wrong seed passes")
    # Control 3: an alternate closest affine seed reproduces every row yet leaves the closest affine function.
    alt = build_levels(alternate_seed(measured[3]), 5)
    c3 = compare_level(4, alt[4], measured[4])
    require(c3["rows_exact"] == c3["rows"] and c3["rows_differing_from_closest_affine"] > 0, "alternate seed passes")
    # Control 4: the residue statement with modulus 16 fails at n = 4.
    rows4 = [m["row"] for m in measured[4]]
    c4 = residue_report(4, good[4], rows4, modulus=16)
    require(c4["flip_violations"] > 0, "modulus 16 passes")
    # Control 5: the transposition identity without its correction fails.
    require(
        transposition_failures(3, corrected=False) > 0 and transposition_failures(3) == 0, "uncorrected identity passes"
    )
    # Control 6: the degree engine on known functions.
    k = 4
    require(degree(0, k) == -1, "zero function degree")
    require(degree(sum(1 << i for i in range(16) if parity(i)), k) == 1, "parity degree")
    require(degree(sum(1 << i for i in range(16) if i & 7 == 7), k) == 3, "monomial degree")
    require(degree(sum(1 << i for i in range(16) if i == 15), k) == 4, "point function degree")
    print(f"self-test passed: perturbed {c1}, wrong seed {c2}, alternate seed {c3}, modulus 16 {c4}")


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    record = build_record()
    validate(record)
    text = render(record)
    if args.write:
        RESULT.write_text(text)
        print(f"wrote {RESULT.name}")
        return 0
    require(RESULT.read_text() == text, "result.json differs from the recomputed record")
    print("check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
