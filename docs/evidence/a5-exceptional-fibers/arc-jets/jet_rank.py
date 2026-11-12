"""Lower bounds on the fiber-cone Hilbert function h_d of E8-bar -> N- from jets of formal arcs.

Let R be the local ring of the slice V(J) at the origin, m_R its maximal ideal, I = (G_1, ..., G_21) R and
F(I) = k[y]/L = sum_d I^d / m_R I^d. An arc gamma: R -> k[[s]] with gamma(t_i) = t_i(s) of valuation at least 1 has

    v = min_j val G_j(t(s)),  e = min_i val t_i(s),  G_j(t(s)) = s^v c_j(s).

Valuations multiply in k[[s]], so gamma(I^d) lies in (s^(d v)) and gamma(m_R I^d) in (s^(e + d v)). A form f in L_d
satisfies f(G) in m_R I^d, hence f(c(s)) = s^(-d v) f(G(t(s))) lies in (s^e): the coefficients of s^0, ..., s^(e-1)
of f(c(s)) are linear functionals on k[y]_d that vanish on L_d. The rank of any family of such functionals,
restricted to any set of columns, is therefore at most dim k[y]_d / L_d = h_d. The bound needs no premise beyond the
arc lying on V(J). With K2 inside L (the degree-two receipts of A5-251) a rank equal to HF(k[y]/K2, d) proves
h_d = HF(k[y]/K2, d). A coefficient of s^0 sees only the reduced support; the coefficients of s^k with k >= 1 see
the nilpotent directions of F(I), so every arc here has e >= 2.

Every arc is Phi(w, rho, sigma, e_par, zeta) of ../arcs/README.md, so it lies on V(J); the run also checks all 16
generators of J on each arc to the working precision. The arc parameters are polynomials in s with the fixed integer
coefficients of `coefficients` below; nothing is drawn at random.

Columns: every monomial of degree d for d <= 4; for d = 5 and 6 the standard monomials of K2 in degree d from the
retained target basis (../monomial-ladder/target-records/<target>-d<d>-basis.json), a basis of k[y]_d / K2_d.

    $PYTHON docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py --target e8nm-p32009 --degree 6 \
        --arcs 1200 --step 100 --write docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
    $PYTHON docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py --check \
        docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(EVIDENCE / "arcs"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import arclib as A  # noqa: E402
import laurent as Lm  # noqa: E402
from arc_targets import TARGETS, Target, k2_hilbert_function, k2_ideal  # noqa: E402
from flint import nmod_mat, nmod_poly  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-arc-jet-rank/1"
TOP = 70
NTERMS = 4
# HF(k[y]/sqrt(K2), d) of ../arcs/README.md, the reduced part of F(I).
RADICAL_HF = {1: 16, 2: 69, 3: 195, 4: 440, 5: 861, 6: 1526}
# (valuation of w, rho, sigma, zeta; kind and k of e_par): "const" gives e_par(0) away from 0, 1 and -1, "near" puts
# e_par = -1 + s^k (...) at the conic point of ../arcs. Every t_i then has valuation at least 2. The limits of the
# "const" arcs lie on the scroll V(P2), those of (4, 2, 2, 2, near, 4) on V(P1), and those of (1, 2, 2, 2, near, k)
# on the quadric threefold that carries the nilpotents of K2 (A5-312), with first jets off the reduced locus.
FAMILIES: tuple[tuple[int, int, int, int, str, int], ...] = (
    (2, 2, 2, 2, "const", 0),
    (4, 2, 2, 2, "near", 4),
    (1, 2, 2, 2, "near", 1),
    (4, 2, 2, 2, "near", 4),
    (1, 2, 2, 2, "near", 2),
    (1, 2, 2, 2, "near", 1),
)
# A fixed integer per (arc, parameter, term): the first eight bytes of SHA-256 of the ASCII string "idx:var:j",
# read big-endian, reduced modulo p, with 0 replaced by 1. This is a deterministic enumeration with no generator
# state, and every value is written into the record. A rule polynomial or exponential in idx alone would put all
# parameter points on one rational curve or line, and a rule periodic in idx repeats arcs; both cap the rank.
COEFFICIENT_RULE = "c(idx, var, j) = int.from_bytes(sha256(f'{idx}:{var}:{j}'.encode()).digest()[:8], 'big') mod p or 1"
PARAMETERS = ("w", "rho", "sigma", "zeta", "e")


def coefficients(idx: int, var: int, prime: int) -> list[int]:
    """The NTERMS fixed coefficients of parameter `var` (1..5) of arc `idx` (COEFFICIENT_RULE)."""
    out = []
    for j in range(NTERMS):
        value = int.from_bytes(hashlib.sha256(f"{idx}:{var}:{j}".encode()).digest()[:8], "big") % prime
        out.append(value or 1)
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def basis_path(target: Target, degree: int) -> Path:
    return EVIDENCE / "monomial-ladder" / "target-records" / f"{target.name}-d{degree}-basis.json"


def columns(target: Target, degree: int) -> tuple[list[tuple[int, ...]], dict[str, str]]:
    """The column monomials and a description of their source."""
    if degree <= 4:
        monos = []
        for comb in itertools.combinations_with_replacement(range(A.NGEN), degree):
            exps = [0] * A.NGEN
            for j in comb:
                exps[j] += 1
            monos.append(tuple(exps))
        return monos, {"kind": "all monomials of the degree"}
    path = basis_path(target, degree)
    record = json.loads(path.read_text(encoding="utf-8"))
    if record["prime"] != target.prime or record["degree"] != degree or record["target"] != target.name:
        raise ValueError(f"{relative(path)} does not describe {target.name} in degree {degree}")
    monos = [tuple(int(x) for x in m) for m in record["monomials"]]
    return monos, {"kind": "standard monomials of K2", "path": relative(path), "sha256": sha256(path)}


def series(order: int, coeffs: list[int], prime: int) -> Lm.L:
    out = Lm.L([], 0, TOP, prime)
    for i, c in enumerate(coeffs):
        out = out + Lm.L.mono(c, order + i, TOP, prime)
    return out


@functools.cache
def slice_ideals(name: str) -> tuple[list[A.Poly], list[A.Poly], list[A.Poly]]:
    target = TARGETS[name]
    ideal_j, ideal_g = A.load_slice(target)
    return ideal_j, ideal_g, A.load_yideal(k2_ideal(target), target.prime)


def arc(target: Target, idx: int) -> list[Lm.L]:
    ow, orho, osig, ozeta, kind, k = FAMILIES[idx % len(FAMILIES)]
    p = target.prime
    w, rho, sig, zeta = (series(o, coefficients(idx, var, p), p) for var, o in enumerate((ow, orho, osig, ozeta), 1))
    ec = coefficients(idx, 5, p)
    if kind == "const":
        # e_par(0) in [2, p - 2] avoids the pole 0 and the conic points 1 and -1.
        e_par = Lm.L.const(2 + ec[0] % (p - 3), TOP, p) + series(1, ec[1:], p)
    else:
        e_par = Lm.L.const(-1, TOP, p) + series(k, ec, p)
    return Lm.phi_laurent(target, w, rho, sig, e_par, zeta)


def truncated_product(polys: list[Any], exps: tuple[int, ...], length: int, prime: int) -> Any:
    acc = nmod_poly([1], prime)
    for j, k in enumerate(exps):
        for _ in range(k):
            acc = acc.mul_low(polys[j], length)
    return acc


def jet_rows(job: tuple[str, int, int, list[tuple[int, ...]]]) -> dict[str, Any]:
    """The functionals of one arc on the columns, with its valuations and its J and K2 checks."""
    name, idx, _degree, monos = job
    target = TARGETS[name]
    p = target.prime
    ideal_j, ideal_g, k2 = slice_ideals(name)
    ts = arc(target, idx)
    vals = [t.val() for t in ts]
    if any(v is not None and v < 1 for v in vals):
        raise RuntimeError(f"arc {idx} does not pass through the origin")
    precision = min(TOP, *(t.top for t in ts))
    eo = min(v if v is not None else precision for v in vals)
    if eo < 2:
        raise RuntimeError(f"arc {idx}: some t_i has valuation 1, so its jets see the reduced support only")
    xs = [t.to_series(precision) for t in ts]
    j_nonzero = sum(1 for g in ideal_j if A.eval_poly(g, xs, precision).val() is not None)
    gs = [A.eval_poly(g, xs, precision) for g in ideal_g]
    v = min(val for val in (g.val() for g in gs) if val is not None)
    if v + eo > precision:
        raise RuntimeError(f"arc {idx}: precision {precision} below v + e = {v + eo}")
    polys = [nmod_poly([g.coeff(v + k) for k in range(eo)], p) for g in gs]
    k2_nonzero = 0
    for q in k2:
        acc = nmod_poly([], p)
        for exps, cf in q.items():
            acc += truncated_product(polys, exps, eo, p) * cf
        if any(int(x) for x in acc.coeffs()[:eo]):
            k2_nonzero += 1
    rows = [[0] * len(monos) for _ in range(eo)]
    for col, exps in enumerate(monos):
        cs = truncated_product(polys, exps, eo, p).coeffs()
        for r in range(min(eo, len(cs))):
            rows[r][col] = int(cs[r])
    coeffs = {param: coefficients(idx, var, p) for var, param in enumerate(PARAMETERS, 1)}
    return {
        "index": idx,
        "family": list(FAMILIES[idx % len(FAMILIES)]),
        "coefficients": coeffs,
        "e": eo,
        "v": v,
        "j_nonzero": j_nonzero,
        "k2_nonzero": k2_nonzero,
        "rows": rows,
    }


def rank(rows: list[list[int]], ncols: int, prime: int) -> int:
    matrix = nmod_mat(len(rows), ncols, prime)
    for i, row in enumerate(rows):
        for j, x in enumerate(row):
            if x:
                matrix[i, j] = x
    return int(matrix.rank())


def inputs(target: Target, source: dict[str, str]) -> dict[str, str]:
    files = [
        Path(__file__),
        EVIDENCE / "arcs" / "arclib.py",
        EVIDENCE / "arcs" / "laurent.py",
        EVIDENCE / "arcs" / "arc_targets.py",
        ROOT / target.header,
        ROOT / target.k2_relations,
        EVIDENCE / "k2-hilbert.jsonl",
    ]
    out = {relative(f): sha256(f) for f in files}
    if "path" in source:
        out[source["path"]] = source["sha256"]
    return out


def compute(name: str, degree: int, narcs: int, step: int, out: Path | None) -> dict[str, Any]:
    target = TARGETS[name]
    started = time.monotonic_ns()
    monos, source = columns(target, degree)
    upper = int(k2_hilbert_function(target)[str(degree)])
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "target": name,
        "fiber": target.fiber,
        "prime": target.prime,
        "root": target.root,
        "degree": degree,
        "columns": len(monos),
        "column_source": source,
        "hf_k2": upper,
        "hf_radical": RADICAL_HF[degree],
        "families": [list(f) for f in FAMILIES],
        "family_of_arc": "FAMILIES[idx % len(FAMILIES)]",
        "parameters": list(PARAMETERS),
        "coefficient_rule": COEFFICIENT_RULE,
        "terms_per_parameter": NTERMS,
        "precision": TOP,
        "arcs_requested": narcs,
        "step": step,
        "inputs": inputs(target, source),
        "python_flint": metadata.version("python-flint"),
        "arcs": [],
        "checkpoints": [],
        "status": "running",
    }
    rows: list[list[int]] = []
    current = 0
    for start in range(0, narcs, step):
        jobs = [(name, idx, degree, monos) for idx in range(start, min(start + step, narcs))]
        for result in parallel.ordered_map(jet_rows, jobs, min_items=2):
            rows.extend(result.pop("rows"))
            record["arcs"].append(result)
        current = rank(rows, len(monos), target.prime)
        record["checkpoints"].append({"arcs": len(record["arcs"]), "rows": len(rows), "rank": current})
        record["elapsed_ms"] = (time.monotonic_ns() - started) // 1_000_000
        if out is not None:
            out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(record["checkpoints"][-1]), file=sys.stderr, flush=True)
        if current >= upper:
            break
    bad = [a["index"] for a in record["arcs"] if a["j_nonzero"] or a["k2_nonzero"]]
    if current > upper or bad:
        record["status"] = "inconsistent"
    elif current == upper:
        record["status"] = "equal_to_k2_bound"
    else:
        record["status"] = "lower_bound_only"
    record["rank"] = current
    record["bound"] = f"{current} <= h_{degree} <= {upper}"
    record["arcs_with_failed_check"] = bad
    record["elapsed_ms"] = (time.monotonic_ns() - started) // 1_000_000
    if out is not None:
        out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def strip_times(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k != "elapsed_ms"}


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--target", choices=sorted(TARGETS), default="e8nm-p32009")
    parser.add_argument("--degree", type=int, choices=range(1, 7))
    parser.add_argument("--arcs", type=int, default=1200)
    parser.add_argument("--step", type=int, default=100)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, help="compute and write the record, rewritten at every checkpoint")
    mode.add_argument("--check", type=Path, help="recompute a record from its own parameters and compare")
    args = parser.parse_args()
    if args.write is not None:
        if args.degree is None:
            parser.error("--write needs --degree")
        record = compute(args.target, args.degree, args.arcs, args.step, args.write)
        print(json.dumps({k: record[k] for k in ("target", "degree", "rank", "hf_k2", "status")}))
        return
    old = json.loads(args.check.read_text(encoding="utf-8"))
    fresh = compute(old["target"], old["degree"], old["arcs_requested"], old["step"], None)
    if strip_times(fresh) != strip_times(old):
        raise SystemExit(f"{args.check}: the recomputed record differs")
    print(json.dumps({"check": "identical", "target": old["target"], "degree": old["degree"], "rank": old["rank"]}))


if __name__ == "__main__":
    main()
