"""Singular scheme and irreducibility of the kernel quartic on the discriminant of chi.

Ledger rows A5-531, A5-533 and A5-540. At the normal-form point (e_1; mu; v_1, rho, 0) of V(Q) minus V(G), mu^2 = -(1
+ v_1^2 + rho^2), rho nonzero (items 3 and 5 of nullity4_orbit_normal_forms.py), the kernel quartic is F = 4 (n (n +
r^2) + q^2) = -4 w.w for w = x cross y, the three 2 x 2 minors of the matrix (x; y) of linear forms in (c0, s, t). The
minors cut the base scheme B of the net of conics. At every point with rho nonzero the producer proves that the
singular scheme S of F has length 3 + deg gcd(chi, chi'), that F is absolutely irreducible, and that the second
triple-root branch v_1^2 = 27, rho^2 = -32, mu^2 = 4 behaves like the first.

Mechanism, with the evidence class of each step.
1. F = -4 w.w and w.x = w.y = 0 (exact identity over Q modulo the relation of mu).
2. The base points are the points with y = lambda x for a root lambda of chi, since x never vanishes on P^2. A root
   whose pencil matrix has a two-dimensional kernel would give a line of base points; a line meets the conic n = 0,
   and the certificate base_points_avoid_the_conic_n excludes a base point there, so every root has corank 1 and B is
   finite. A finite determinantal scheme of 2 x 3 linear forms has length 3 (Hilbert-Burch), and the Smith form of the
   pencil at a root of multiplicity e is diag(1, 1, (lambda - lambda_0)^e), so B has length e at the base point of
   that root (argument, resting on that certificate and on the identity node_pencil_determinant: the pencil
   determinant is -chi).
3. The partials of F lie in I_B because F lies in I_B^2 (certificate partials_lie_in_the_base_ideal), so S contains B.
4. Exact certificates over Q for every point with rho nonzero, each a Groebner basis that equals (1) after saturation
   by the irrelevant ideal (c0, s, t) and by rho (Singular): the singular points of F lie on B; n = c0^2 + s^2 + t^2
   is nonzero at each base point; the Hessian of F is nonzero at each base point. The quotient J : I_B for the
   Jacobian ideal J also becomes the unit ideal after saturation by rho and the discriminant D, so J = I_B near every
   point with D nonzero: a second route to length 3 off the discriminant that uses neither step 2 nor step 5 beyond
   the length of B. Calibrations leave out the saturation by rho or by D and report a non-unit ideal, so each check
   can fail.
5. At a base point P, w lies in x^perp, a rank-2 bundle near P with a local frame (e, e'), so w = f e + g e' with (f,
   g) = I_B at P. When n(P) is nonzero the Gram form of the frame is nondegenerate at P, so F = unit f' g' with (f',
   g') = (f, g) = I_B at P. The multiplicity of F at P is that of f' plus that of g' and equals 2 where the Hessian is
   nonzero, so both branches are smooth and meet with contact e: F has an A_{2e-1} point, Tjurina number 2e - 1
   (argument, resting on the certificates of step 4).
6. S has length the sum of (2 e_i - 1) over the roots of chi, which is 6 - N for N distinct roots and equals 3 + deg
   gcd(chi, chi'): 3 off the discriminant, 4 at a double root and 5 at a triple root.
7. A product of two smooth conics without common component meets in contact orders k_i with sum 4 (Bezout) and has
   A_{2k_i-1} points, so its singular scheme has length 8 - N; S has length 6 - N. A quartic with a line is excluded
   by A5-531, a quartic with a double conic has infinite S, and a quartic with a singular conic holds a line. So F is
   absolutely irreducible.
8. The discriminant of chi is 4 D; chi has a double root a exactly where v_1 (1 - a^2) = 2 a^3 and 2 rho^2 = 3 a^2 + 2
   a v_1 - 1 - 2 v_1^2 (Groebner basis of the coefficient equations), and a triple root exactly where v_1 (v_1^2 - 27)
   = 0 with a = -v_1 / 3 and 7 v_1^2 + 6 rho^2 + 3 = 0: the branches (v_1, rho^2, mu^2) = (0, -1/2, -1/2) and (+-3
   sqrt 3, -32, 4).
9. Singular computes the length of S at fibers over the prime components of rational points of each stratum (the
   residue fields Q(sqrt -2), Q(sqrt 3, sqrt -2) and the quadratic or biquadratic fields of the sample points); the
   components of one prime are Galois conjugate and F has rational coefficients, so the length is uniform on a
   component. A fiber at rho = 0, outside the stratum, has length 7 and calibrates the reading.

Premises: rho nonzero (the normal form of A5-530), the exclusion of lines of A5-531, characteristic 0, the
classification of two smooth branches with contact e as A_{2e-1}, and the polynomials of the two Singular scripts,
which the unmarked tests compare with the formulas of nullity4_orbit_normal_forms.py. Steps 2 and 5 to 7 are written
arguments; no function replays them.

--write writes nullity4-quartic-discriminant-result.json beside this file; --check recomputes and compares. Singular
4.4 comes from PATH or the SINGULAR environment variable; without it the run reports "not run".

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_quartic_discriminant.py --check
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-quartic-discriminant-v1"
RECORD = HERE / "nullity4-quartic-discriminant-result.json"
CERTIFICATE_SCRIPT = HERE / "nullity4_quartic_discriminant_certificates.sing"
FIBER_SCRIPT = HERE / "nullity4_quartic_discriminant_fiber.sing"
SOURCE_PATHS = (
    HERE / "nullity4_quartic_discriminant.py",
    CERTIFICATE_SCRIPT,
    FIBER_SCRIPT,
    HERE / "nullity4_orbit_normal_forms.py",
)
FIELD = "Q: sympy identities, Singular unit ideals and Singular fibers over the prime components of rational points"
SINGULAR_TIMEOUT = 600
ENVIRONMENT_NAMES = ("PATH", "HOME", "SINGULARPATH", "LD_LIBRARY_PATH")

LAM, A, B, W, V = sp.symbols("lambda a b w v")
CHI = forms.node_cubic().subs({forms.RHO**2: W, forms.V1: V})
IDENTITIES = (
    "quartic_is_minus_four_cross_square",
    "pencil_determinant_is_minus_chi",
    "discriminant_polynomial",
    "double_root_locus",
    "triple_root_locus",
    "discriminant_vanishes_on_the_double_root_curve",
    "first_triple_branch",
    "second_triple_branch",
)
# Lex Groebner bases of the coefficient equations of chi = (lambda - a)^2 (lambda - b) in (b, w, a, v) and of
# chi = (lambda - a)^3 in (a, w, v), with w = rho^2.
DOUBLE_ROOT_BASIS = ["2*a + b + v", "-3*a**2 - 2*a*v + 2*v**2 + 2*w + 1", "2*a**3 + a**2*v - v"]
TRIPLE_ROOT_BASIS = ["3*a + v", "7*v**2 + 6*w + 3", "v**3 - 27*v"]
# Per stratum, the multiplicities of the roots of chi.
ROOT_PATTERNS = {"off the discriminant": [1, 1, 1], "double root": [2, 1], "triple root": [3]}
CERTIFICATES = {
    "quartic_is_minus_the_cross_square": True,
    "partials_lie_in_the_base_ideal": True,
    "singular_points_lie_on_the_base_scheme": True,
    "base_points_avoid_the_conic_n": True,
    "hessian_nonzero_at_the_base_points": True,
    "quotient_route_unit_off_the_discriminant": True,
}
# The same ideals without the saturation by rho or by the discriminant: none is the unit ideal.
CALIBRATIONS = {
    "singular_points_off_the_base_without_rho_saturation_unit": False,
    "base_points_avoid_the_conic_without_rho_saturation_unit": False,
    "hessian_nonzero_without_rho_saturation_unit": False,
    "hessian_nonzero_off_the_base_unit": False,
    "quotient_route_unit_without_discriminant_saturation": False,
}
FIBER_LABELS = (
    "off the discriminant",
    "double root",
    "triple root, v_1 = 0",
    "triple root, v_1^2 = 27",
    "rho = 0, outside the stratum",
)
SAMPLES = {"off the discriminant": 2, "double root": 3}
FIXED_PARAMETERS = {
    "triple root, v_1 = 0": ["v, 2*p^2+1"],
    "triple root, v_1^2 = 27": ["v^2-27, p^2+32"],
    "rho = 0, outside the stratum": ["v-1, p"],
}
# Per label, the length of the singular scheme at every point of every prime component.
FIBER_LENGTHS = {
    "off the discriminant": 3,
    "double root": 4,
    "triple root, v_1 = 0": 5,
    "triple root, v_1^2 = 27": 5,
    "rho = 0, outside the stratum": 7,
}
# Per label and sample: the (points, length) pairs of the prime components of the rational point.
FIBER_TALLY: dict[str, list[list[list[int]]]] = {
    "off the discriminant": [[[2, 3]], [[2, 3]]],
    "double root": [[[4, 4]], [[4, 4]], [[4, 4]]],
    "triple root, v_1 = 0": [[[2, 5], [2, 5]]],
    "triple root, v_1^2 = 27": [[[4, 5], [4, 5]]],
    "rho = 0, outside the stratum": [[[2, 7]]],
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _draw(label: str, counter: int, modulus: int) -> int:
    digest = hashlib.sha256(f"nullity4-quartic-discriminant:{label}:{counter}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def _kernel_quartic_vectors() -> tuple[list[Any], list[Any], Any]:
    k = forms.kernel_vector(forms.C0, forms.S, forms.T)
    return list(k[0:3]), list(k[8:11]), forms._forms(k)[2]


def quartic_cross_square(sign: int = 1) -> bool:
    """G on K(z) plus 4 |x cross y|^2 vanishes modulo the relation, and w is orthogonal to x and y."""
    x, y, g = _kernel_quartic_vectors()
    cross = sp.Matrix(x).cross(sp.Matrix(y))
    square = sum(entry * entry for entry in cross)
    orthogonal = [sum(a * b for a, b in zip(cross, vector, strict=True)) for vector in (x, y)]
    return forms._zero([g + 4 * sign * square, *orthogonal])


def discriminant_polynomial() -> bool:
    lam = sp.Symbol("lambda")
    return sp.expand(sp.discriminant(forms.node_cubic(), lam) - sp.sympify(forms.NODE_DISCRIMINANT)) == 0


def _coefficient_basis(target: Any, *generators: Any) -> list[str]:
    equations = [sp.expand(c) for c in sp.Poly(sp.expand(CHI - target), LAM).all_coeffs()]
    return [str(g) for g in sp.groebner(equations, *generators, order="lex").exprs]


def double_root_locus() -> bool:
    return _coefficient_basis((LAM - A) ** 2 * (LAM - B), B, W, A, V) == DOUBLE_ROOT_BASIS


def triple_root_locus() -> bool:
    return _coefficient_basis((LAM - A) ** 3, A, W, V) == TRIPLE_ROOT_BASIS


def _double_root_relations() -> list[Any]:
    return [V * (1 - A**2) - 2 * A**3, 2 * W - (3 * A**2 + 2 * A * V - 1 - 2 * V**2)]


def discriminant_vanishes_on_the_double_root_curve() -> bool:
    basis = sp.groebner(_double_root_relations(), W, V, A, order="lex")
    factored = sp.expand(CHI - (LAM - A) ** 2 * (LAM + V + 2 * A))
    remainders = (
        sp.reduced(sp.expand(expression), list(basis.exprs), LAM, W, V, A, order="lex")[1]
        for expression in (sp.discriminant(CHI, LAM), factored)
    )
    return all(remainder == 0 for remainder in remainders)


def first_triple_branch() -> bool:
    return sp.expand(CHI.subs({V: 0, W: sp.Rational(-1, 2)}) - LAM**3) == 0


def second_triple_branch() -> bool:
    # v = -3 a with a^2 = 3, rho^2 = -32 and mu^2 = -(1 + v^2 + rho^2) = 4.
    reduced = sp.rem(sp.expand(CHI.subs({V: -3 * A, W: -32}) - (LAM - A) ** 3), A**2 - 3, A)
    return reduced == 0 and sp.expand(-(1 + 27 - 32) - 4) == 0


def pencil_determinant_is_minus_chi() -> bool:
    return forms.identity("node_pencil_determinant")


def identity(name: str) -> bool:
    checks = {
        "quartic_is_minus_four_cross_square": quartic_cross_square,
        "pencil_determinant_is_minus_chi": pencil_determinant_is_minus_chi,
        "discriminant_polynomial": discriminant_polynomial,
        "double_root_locus": double_root_locus,
        "triple_root_locus": triple_root_locus,
        "discriminant_vanishes_on_the_double_root_curve": discriminant_vanishes_on_the_double_root_curve,
        "first_triple_branch": first_triple_branch,
        "second_triple_branch": second_triple_branch,
    }
    return checks[name]()


def pattern_row(multiplicities: Sequence[int]) -> list[int]:
    """(distinct roots, length of S, 3 + deg gcd(chi, chi'), length of a product of two smooth conics)."""
    distinct = len(multiplicities)
    length = sum(2 * e - 1 for e in multiplicities)
    gcd_degree = sum(e - 1 for e in multiplicities)
    return [distinct, length, 3 + gcd_degree, 8 - distinct]


def _chi_at(v: Fraction, w: Fraction, lam: Fraction) -> Fraction:
    return lam**3 + v * lam**2 - (1 + 2 * v * v + 2 * w) * lam + v


def double_root_point(a: Fraction) -> tuple[Fraction, Fraction] | None:
    """(v_1, rho^2) of the double-root curve at the root a, or None where a leaves the stratum."""
    if a in (0, 1, -1):
        return None
    v = 2 * a**3 / (1 - a * a)
    w = (3 * a * a + 2 * a * v - 1 - 2 * v * v) / 2
    b = -v - 2 * a
    if w == 0 or b == a:
        return None
    slope = 3 * a * a + 2 * v * a - (1 + 2 * v * v + 2 * w)
    _require(_chi_at(v, w, a) == 0 and slope == 0, "a is not a double root of chi at the computed point")
    return v, w


def _off_discriminant(v: int, rho: int) -> bool:
    w = rho * rho
    value = sp.sympify(forms.NODE_DISCRIMINANT).subs({forms.V1: v, forms.RHO: rho})
    return bool(w != 0 and value != 0)


def _clear(value: Fraction) -> tuple[int, int]:
    return value.numerator, value.denominator


def fiber_jobs() -> list[tuple[str, str]]:
    """(label, parameter ideal) of every fiber; the rational points come from sha256 of the label and a counter."""
    jobs: list[tuple[str, str]] = []
    counter = 0
    found = 0
    while found < SAMPLES["off the discriminant"]:
        counter += 1
        v, rho = 1 + _draw("off", 2 * counter, 9), 1 + _draw("off", 2 * counter + 1, 9)
        if _off_discriminant(v, rho):
            jobs.append(("off the discriminant", f"v-{v}, p-{rho}"))
            found += 1
    counter = 0
    found = 0
    while found < SAMPLES["double root"]:
        counter += 1
        a = Fraction(2 + _draw("double", 2 * counter, 40), 2 + _draw("double", 2 * counter + 1, 40))
        point = double_root_point(a)
        if point is None:
            continue
        (vn, vd), (wn, wd) = _clear(point[0]), _clear(point[1])
        jobs.append(("double root", f"{vd}*v-({vn}), {wd}*p^2-({wn})"))
        found += 1
    for label in FIBER_LABELS[2:]:
        jobs.extend((label, parameters) for parameters in FIXED_PARAMETERS[label])
    return jobs


def _singular() -> str:
    path = os.environ.get("SINGULAR") or shutil.which("Singular")
    if path is None:
        raise SystemExit("not run: Singular 4.4 is missing (package singular); set SINGULAR to its path")
    return path


def _run_singular(script: Path, extra: dict[str, str]) -> list[str]:
    """The output lines of a script run with stdin closed; the terminal marker, not the exit status, ends a run."""
    environment = {name: os.environ[name] for name in ENVIRONMENT_NAMES if name in os.environ}
    environment.update({"MALLOC_ARENA_MAX": "2", "LC_ALL": "C", **extra})
    done = subprocess.run(
        [_singular(), "-q", str(script)],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=environment,
        timeout=SINGULAR_TIMEOUT,
        check=False,
    )
    lines = done.stdout.splitlines()
    _require(not any(line.lstrip().startswith("?") for line in lines), f"{script.name} reports an error")
    _require(any(line.startswith("MARKER DONE") for line in lines), f"{script.name} ends without its marker")
    return lines


def certificate_facts() -> dict[str, dict[str, bool]]:
    lines = _run_singular(CERTIFICATE_SCRIPT, {})
    found: dict[str, dict[str, bool]] = {"CERT": {}, "CAL": {}}
    for line in lines:
        kind, _, rest = line.partition(" ")
        if kind in found:
            name, _, flag = rest.rpartition(" ")
            _require(flag in ("0", "1") and name not in found[kind], f"a malformed line: {line}")
            found[kind][name] = flag == "1"
    return {"certificates": found["CERT"], "calibrations": found["CAL"]}


def fiber_facts(job: tuple[str, str]) -> list[list[int]]:
    """(points, length) of each prime component of the fiber; a nonzero remainder fails the uniformity premise."""
    label, parameters = job
    lines = _run_singular(FIBER_SCRIPT, {"FIBER_LABEL": "point", "FIBER_PARAMETERS": parameters})
    row = next(line for line in lines if line.startswith("FIBER "))
    pairs = []
    for part in row.split("|")[1:]:
        tokens = part.split()
        _require(
            tokens[0] == "points" and tokens[2] == "length" and tokens[4] == "remainder", f"a malformed row: {row}"
        )
        _require(int(tokens[5]) == 0, f"the length is not uniform on a component: {row}")
        pairs.append([int(tokens[1]), int(tokens[3])])
    return sorted(pairs)


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def _fiber_record(
    jobs: Sequence[tuple[str, str]], facts: Sequence[list[list[int]]]
) -> dict[str, list[list[list[int]]]]:
    record: dict[str, list[list[list[int]]]] = {label: [] for label in FIBER_LABELS}
    for (label, _), pairs in zip(jobs, facts, strict=True):
        record[label].append(pairs)
    return record


def compute() -> dict[str, Any]:
    _singular()
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    jobs = fiber_jobs()
    facts = parallel.ordered_map(fiber_facts, jobs, min_items=2)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "double_root_basis": _coefficient_basis((LAM - A) ** 2 * (LAM - B), B, W, A, V),
        "triple_root_basis": _coefficient_basis((LAM - A) ** 3, A, W, V),
        "root_patterns": {label: [pattern, *pattern_row(pattern)] for label, pattern in ROOT_PATTERNS.items()},
        **certificate_facts(),
        "fiber_parameters": {label: [p for j, p in jobs if j == label] for label in FIBER_LABELS},
        "fibers": _fiber_record(jobs, facts),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    jobs = fiber_jobs()
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": dict.fromkeys(IDENTITIES, True),
        "double_root_basis": list(DOUBLE_ROOT_BASIS),
        "triple_root_basis": list(TRIPLE_ROOT_BASIS),
        "root_patterns": {label: [list(pattern), *pattern_row(pattern)] for label, pattern in ROOT_PATTERNS.items()},
        "certificates": dict(CERTIFICATES),
        "calibrations": dict(CALIBRATIONS),
        "fiber_parameters": {label: [p for j, p in jobs if j == label] for label in FIBER_LABELS},
        "fibers": copy.deepcopy(FIBER_TALLY),
        "pass": True,
    }


def pattern_problems(record: dict[str, Any]) -> list[str]:
    """The rules a record must meet whatever its pinned text: length = 3 + deg gcd and a reducible quartic differs."""
    problems = []
    for label, row in record.get("root_patterns", {}).items():
        distinct, length, formula, reducible = row[1:]
        if length != formula or length == reducible or length + distinct != 6:
            problems.append(f"the singular scheme length of {label} breaks 3 + deg gcd or the reducible length")
    for label, samples in record.get("fibers", {}).items():
        for pairs in samples:
            if any(length != FIBER_LENGTHS[label] for _, length in pairs):
                problems.append(f"a fiber of {label} has another length than {FIBER_LENGTHS[label]}")
    return problems


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "double_root_basis": "the double-root locus of chi differs",
        "triple_root_basis": "the triple-root locus of chi differs",
        "root_patterns": "the root patterns of chi or their lengths differ",
        "certificates": "a Singular certificate fails",
        "calibrations": "a calibration ideal is the unit ideal, so its certificate cannot fail",
        "fiber_parameters": "the sampled points differ from the points the labels determine",
        "fibers": "the fiber lengths differ from their pinned tallies",
    }
    problems = [
        message
        for group, message in messages.items()
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True)
    ]
    problems.extend(pattern_problems(record))
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        f"pass: {len(record['identities'])} identities, {len(record['certificates'])} certificates, "
        f"{sum(len(v) for v in record['fibers'].values())} fibers"
    )


if __name__ == "__main__":
    main()
