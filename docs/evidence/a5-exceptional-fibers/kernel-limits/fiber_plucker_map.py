"""The map from an exceptional fiber to the Grassmannian of kernel planes, fitted on sampled arcs.

plucker_limits.py computes, along one arc of an incidence S -> T through a point b of T, the fiber point y (the
normalized leading vector of the generators G) and the limit of ker L_a, an 8-plane inside the 16-dimensional kernel
of L_b. Its records show one plane per fiber point on each sampled family. This script samples many arcs with distinct
leading parameters and tests whether the Plucker vector of the plane is a vector of forms of one degree delta in y:

    c_s Pl_s = v_delta(y_s) T   for scalars c_s and one matrix T,

with v_delta the monomials of degree delta. With N a basis of the left kernel of the sample matrix V of v_delta, the
scalars solve N diag(Pl[:, j]) c = 0 for every Plucker coordinate j, a linear system in c alone. The record holds, per
incidence and prime: the ranks of V for delta = 1, 2, 3 (the Hilbert function of the fiber on the sample), the rank of
the Plucker vectors, the least delta with a solution, the dimension of its solution space, the rank of T, and the
number of held-out arcs whose Plucker vector is proportional to v_delta(y) T. A solution space of dimension 1 with T
of rank equal to the rank of V makes the fitted map a linear injection of the degree-delta piece of the fiber ring,
so the image of the fiber in the Grassmannian is its delta-uple re-embedding. The statement is a fit on samples with
held-out validation, at the prime of the run.

Run from the repository root:
    "$PYTHON" docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py iso --fit 240 --held-out 40
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import plucker_limits as limits
import vb_limit_span as span
from flint import nmod_mat

import parallel

SCHEMA = "a5-fiber-plucker-map-v1"
HERE = Path(__file__).resolve().parent
# family: (slug, truncation order, kinds of arc)
FAMILIES: dict[str, tuple[str, int, tuple[str, ...]]] = {
    "x": ("xp-nm", limits.FAMILIES["x"][1], ("x",)),
    "x-same": ("xm-nm", limits.FAMILIES["x-same"][1], ("x-same",)),
    "iso": ("iso-nm", limits.FAMILIES["iso"][1], ("iso",)),
    "w8": ("w8-nm", limits.FAMILIES["w8-c30"][1], ("c30", "c20")),
    "e8": ("e8-nm", limits.FAMILIES["e8"][1], ("p2", "p1")),
}
# family: the slug of the N+ header, on which the same arc formulas run with the sign of the incidence table
PLUS = {"x": "xm-np", "x-same": "xp-np", "iso": "iso-np", "w8": "w8-np", "e8": "e8-np"}
SHAPES = {"x": (3, 5), "x-same": (4, 4), "iso": (4, 2), "c30": (5, 2), "c20": (5, 2), "p2": (5, 10), "p1": (5, 10)}


def value(arc: int, index: int) -> int:
    """A fixed integer in 1..101 for each arc and parameter index, from a hash; a formula affine in the arc index puts
    the parameter points on a line. The ranks of the Veronese sample matrices in the record are the evidence that
    the sampled fiber points satisfy no relation beyond those of the fiber."""
    digest = hashlib.sha256(f"fiber-plucker-map:{arc}:{index}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 101 + 1


def parameters(kind: str, arc: int) -> tuple[Any, ...]:
    lead, extra = SHAPES[kind]
    point = tuple(value(arc, i) for i in range(lead))
    rest = tuple(value(arc, lead + i) for i in range(extra))
    if kind in ("x", "x-same", "iso"):
        return (point, rest)
    if kind in ("c30", "c20"):
        return (kind, point, rest)
    return (kind, point, (rest[:5], rest[5:]))


def base_kernel(data: dict[str, Any]) -> list[limits.Vector]:
    field = limits.Field(data["prime"], data["order"])
    point = [limits.Series((Fraction(v),), field) for v in data["boundary_point"]]
    matrix = limits.left_matrix(limits.operand(point, field))
    return limits.rref(limits.saturated_kernel(matrix, field)[0], field)


def sample(item: tuple[dict[str, Any], list[limits.Vector], str, int]) -> dict[str, Any] | None:
    data, basis, kind, arc = item
    record = limits.one_arc((data, parameters(kind, arc), False))
    good = (
        record["limit_dimension"] == limits.SOURCE_NULLITY
        and record["limit_in_base_kernel"]
        and record.get("j_nonzero") == 0
        and "g_limit" in record
    )
    if not good:
        return None
    plane = [tuple(int(v) for v in row) for row in record["plane"]]
    return {
        "kind": kind,
        "arc": arc,
        "y": [int(v) for v in record["g_limit"]],
        "plucker": span.plucker(plane, basis, data["prime"]),
    }


def veronese(y: list[int], delta: int, prime: int) -> list[int]:
    out = []
    for combo in itertools.combinations_with_replacement(range(len(y)), delta):
        product = 1
        for i in combo:
            product = product * y[i] % prime
        out.append(product)
    return out


def scalar_system(left_rows: list[list[int]], pr: list[list[int]], prime: int) -> nmod_mat:
    """The equations N diag(Pl[:, j]) c = 0 over the pivot Plucker coordinates j, with N the rows of left_rows."""
    return nmod_mat(
        [[row[s] * pr[s][j] % prime for s in range(len(pr))] for j in range(len(pr[0])) for row in left_rows],
        prime,
    )


def normalized_digest(t: nmod_mat, prime: int) -> str:
    """SHA-256 of T scaled so that its first nonzero entry in row-major order is 1; T is defined up to one scalar."""
    entries = [int(t[i, j]) for i in range(t.nrows()) for j in range(t.ncols())]
    lead = next((v for v in entries if v), 1)
    inverse = pow(lead, -1, prime)
    text = ",".join(str(v * inverse % prime) for v in entries)
    return hashlib.sha256(f"{t.nrows()}x{t.ncols()}:{text}".encode()).hexdigest()


def pivot_columns(matrix: nmod_mat) -> list[int]:
    reduced, rank = matrix.rref()
    out = []
    for i in range(rank):
        out.append(next(j for j in range(matrix.ncols()) if int(reduced[i, j])))
    return out


def fit(
    samples: list[dict[str, Any]], held: list[dict[str, Any]], prime: int, max_delta: int, retain_map: bool = False
) -> dict[str, Any]:
    plucker = nmod_mat([s["plucker"] for s in samples], prime)
    plucker_pivots = pivot_columns(plucker)
    pr = [[s["plucker"][j] for j in plucker_pivots] for s in samples]
    out: dict[str, Any] = {"samples": len(samples), "plucker_rank": len(plucker_pivots), "veronese_ranks": {}}
    for delta in range(1, max_delta + 1):
        rows = [veronese(s["y"], delta, prime) for s in samples]
        v = nmod_mat(rows, prime)
        v_pivots = pivot_columns(v)
        out["veronese_ranks"][str(delta)] = len(v_pivots)
        if len(v_pivots) >= len(samples) or "delta" in out:
            continue
        vr = nmod_mat([[row[j] for j in v_pivots] for row in rows], prime)
        left = vr.transpose().nullspace()[0].transpose()
        left_rows = [[int(left[i, s]) for s in range(len(samples))] for i in range(len(samples) - len(v_pivots))]
        kernel, nullity = scalar_system(left_rows, pr, prime).nullspace()
        if not nullity:
            continue
        # Mutation: each Plucker vector paired with the fiber point of the next arc; a real fit has no solution.
        shifted = scalar_system(left_rows, pr[1:] + pr[:1], prime)
        out["mutation_solution_dimension"] = int(shifted.nullspace()[1])
        c = [int(kernel[s, 0]) for s in range(len(samples))]
        out.update({"delta": delta, "solution_dimension": int(nullity), "scalars_all_nonzero": all(c)})
        if nullity != 1 or not all(c):
            continue
        # T on the pivot monomials: Vr T = diag(c) Pl, solved on len(v_pivots) independent samples.
        rows_used = pivot_columns(vr.transpose())
        square = nmod_mat([[int(vr[s, i]) for i in range(len(v_pivots))] for s in rows_used], prime)
        full = [[c[s] * p % prime for p in samples[s]["plucker"]] for s in rows_used]
        t = square.inv() * nmod_mat(full, prime)
        out["t_rank"] = int(t.rank())
        out["t_sha256"] = normalized_digest(t, prime)
        if retain_map:
            # Columns use the same Plucker ordering as span.plucker().
            # Rows use veronese()'s combinations_with_replacement ordering.
            entries = [[int(t[i, j]) for j in range(t.ncols())] for i in range(t.nrows())]
            lead = next((value for row in entries for value in row if value), 1)
            scale = pow(lead, -1, prime)
            out["map"] = {
                "field_prime": prime,
                "degree": delta,
                "monomial_indices": v_pivots,
                "plucker_coordinate_count": t.ncols(),
                "matrix_rows": [[value * scale % prime for value in row] for row in entries],
                "convention": "v_delta(y)[monomial_indices] times matrix_rows",
            }
        residual = vr * t - nmod_mat(
            [[c[s] * p % prime for p in samples[s]["plucker"]] for s in range(len(samples))], prime
        )
        out["fit_exact_on_all_samples"] = residual.rank() == 0
        agree = 0
        for h in held:
            image = nmod_mat([[veronese(h["y"], delta, prime)[j] for j in v_pivots]], prime) * t
            fitted = [int(image[0, j]) for j in range(image.ncols())]
            # A zero fitted vector names no point of Plucker space, so it never counts as agreement.
            agree += int(any(fitted) and nmod_mat([fitted, h["plucker"]], prime).rank() == 1)
        out["held_out"] = len(held)
        out["held_out_proportional"] = agree
        points = {tuple(s["y"]) for s in (*samples, *held)}
        out["distinct_fiber_points"] = len(points)
        validated = (
            out["solution_dimension"] == 1
            and out["scalars_all_nonzero"]
            and out["t_rank"] == len(v_pivots)
            and out["fit_exact_on_all_samples"]
            and held
            and agree == len(held)
            and out["mutation_solution_dimension"] == 0
            and len(points) == len(samples) + len(held)
        )
        out["verdict"] = f"degree_{delta}_fit_validated" if validated else "fit_not_validated"
    out.setdefault("verdict", "no_fit")
    return out


def fit_case(job: tuple[list[dict[str, Any]], list[dict[str, Any]], int, int, bool]) -> dict[str, Any]:
    return fit(*job)


def build(
    family: str, prime: int, count: int, held_out: int, max_delta: int, plus: bool = False, retain_map: bool = False
) -> dict[str, Any]:
    slug, order, kinds = FAMILIES[family]
    if plus:
        slug = PLUS[family]
    data = limits.slice_data(slug, limits.Field(prime, order))
    basis = base_kernel(data)
    total = count + held_out
    items = [(data, basis, kind, arc) for arc in range(total) for kind in kinds]
    results = [r for r in parallel.ordered_map(sample, items, min_items=1) if r is not None]
    by_kind = {kind: [r for r in results if r["kind"] == kind] for kind in kinds}
    groups = (*by_kind.items(), *((("all", results),) if len(kinds) > 1 else ()))
    # Arcs below count are fitted and the rest are held out, by arc index, so a rejected arc never shifts the split.
    jobs = [
        ([r for r in rows if r["arc"] < count], [r for r in rows if r["arc"] >= count], prime, max_delta, retain_map)
        for _, rows in groups
    ]
    cases = dict(zip((name for name, _ in groups), parallel.ordered_map(fit_case, jobs, min_items=2), strict=True))
    return {
        "schema": SCHEMA,
        "family": family,
        "slug": slug,
        "prime": prime,
        "order": order,
        "base_nullity": len(basis),
        "generators": len(results[0]["y"]) if results else 0,
        "arcs_requested": len(items),
        "arcs_with_limit": len(results),
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("family", choices=tuple(FAMILIES))
    parser.add_argument("--prime", type=int, choices=tuple(limits.PRIMES), default=32009)
    parser.add_argument("--fit", type=int, default=240)
    parser.add_argument("--held-out", type=int, default=40)
    parser.add_argument("--max-delta", type=int, default=3)
    parser.add_argument("--plus", action="store_true", help="use the N+ header of the family")
    parser.add_argument(
        "--retain-map", action="store_true", help="retain the complete normalized fitted matrix (large JSON)"
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    record = build(args.family, args.prime, args.fit, args.held_out, args.max_delta, args.plus, args.retain_map)
    suffix = "-plus" if args.plus else ""
    out = args.out or HERE / f"fiber-plucker-map-{args.family}{suffix}-p{args.prime}.json"
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record))
    failed = [name for name, case in record["cases"].items() if case["verdict"] != "degree_2_fit_validated"]
    if record["arcs_with_limit"] != record["arcs_requested"]:
        missing = record["arcs_requested"] - record["arcs_with_limit"]
        raise SystemExit(f"{record['slug']} p={args.prime}: {missing} requested arcs have no validated limit")
    if failed:
        raise SystemExit(f"{record['slug']} p={args.prime}: no validated quadratic fit on {', '.join(failed)}")


if __name__ == "__main__":
    main()
