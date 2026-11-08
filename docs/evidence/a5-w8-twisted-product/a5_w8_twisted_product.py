"""The A_5 piece W8 as a twisted product of two sedenion zero-divisor ideals, and the nullity-fold spectrum.

Coordinates. A_5 has real coordinates x_0..x_31, the cd_core doubling e_p e_q = cd_sign(dim, p, q) e_(p XOR q), and
left multiplication L_x = cd_core.left_mult_matrix_exact(32, x). Over a field F_p that holds i with i^2 = -1 the
complex coordinates z_k = x_k + i x_(16+k) and z'_k = x_k - i x_(16+k), k = 0..15, are 32 independent linear forms.
The sedenion zero-divisor ideal is J = (y_0, y_8, U - V, W) in the variables y_0..y_15 with u = y_1..y_7,
v = y_9..y_15, U = u.u, V = v.v, W = u.v (docs/evidence/a5-w8-a4-restriction).

Statement 1 (twisted product). The 32-coordinate W8 closure ideal built by the strata record's own code (the real and
imaginary parts of mu, U - V and W in z_1..z_15, with the doubly pure equations x_0 = x_16 = 0) equals J(z) + J(z')
over F_32009. The reason is linear: for a polynomial f with rational coefficients, Re f(z) = (f(z) + f(z'))/2 and
Im f(z) = (f(z) - f(z'))/(2 i), so the two ideals contain each other whenever 2 and i are units. Singular decides both
containments by standard bases, reads dimension 24, degree 16 and the first Hilbert numerator N_J(t)^2, and repeats the
Hilbert series at p = 32003, which has no i (32003 = 3 mod 4). The real slice x_16..x_31 = 0 is the diagonal z = z'
and cuts the ideal down to J. Mutation controls: flipping the sign of i in one coordinate of the change of variables
breaks the containment W8 in J(z) + J(z'), flipping every sign swaps z and z' and keeps the equality, and the W8 ideal
with U + V in place of U - V or without x_0 = x_16 = 0 differs from J(z) + J(z').

Statement 2 (nullity-fold spectrum). For each mixed basis pair x = e_i + s e_(16+j), i, j in 0..15, s = +-1, the
script computes n_32(x) = 32 - rank L_x, n_16(z) and n_16(z') for z = x_low + i x_high and z' = x_low - i x_high, and
the real nullity n_16(e_i + s e_j), every rank over F_32009 from cd_core.cd_sign, with the rank over Q of the real
matrices as a cross-check, and tabulates their joint law.

Statement 3 (seeded random points). Points of four classes are drawn from numpy.random.default_rng(W8_SAMPLE_SEEDS),
the first two values of the ANU draw named by DRAW: W8 (z and z' independent points of V(J)), diag (z = z' in V(J), the
real slice), offW8 (z in V(J), z' uniform) and generic (z, z' uniform). The first ten draws of the stream in the order
W8 x 6, diag x 2, offW8 x 2 reproduce the orchestrator's recorded sample; the run then draws a fresh stream per
200-point class and counts where n_32 = n_16(z) + n_16(z') holds.

Usage:
    "$PYTHON" -B -W error a5_w8_twisted_product.py --self-test
    "$PYTHON" -B -W error a5_w8_twisted_product.py --out docs/evidence/a5-w8-twisted-product
"""

from __future__ import annotations

import argparse
import functools
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any

import flint
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign, left_mult_matrix_exact  # noqa: E402

P = 32009
P_NO_I = 32003
DRAW = "docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json"
# Values at indices 0 and 1 of the retained draw DRAW; the run raises when the file disagrees.
W8_SAMPLE_SEEDS = [48732, 12744]
SEED_INDICES = (0, 1)
NEIGHBOR = ROOT / "docs/evidence/a5-w8-a4-restriction/a5_w8_a4_restriction.py"
NEIGHBOR_J = ROOT / "docs/evidence/a5-w8-a4-restriction/ideal_J.sing"
X_NAMES = tuple(f"x{k}" for k in range(32))
Y_NAMES = tuple(f"y{k}" for k in range(16))
CLASSES = ("W8", "diag", "offW8", "generic")
SAMPLE10_KINDS = ("W8",) * 6 + ("diag",) * 2 + ("offW8",) * 2
# The orchestrator's recorded rows (n_32, n_16(z), n_16(z')) for the ten-point sample.
SAMPLE10_ROWS = [(8, 4, 4)] * 8 + [(4, 4, 0)] * 2
POINTS_PER_CLASS = 200
BASIS_CELLS = {(0, 0, 0): 32, (0, 8, 8): 60, (4, 4, 4): 168, (12, 8, 8): 252}
MEMORY_CAP = os.environ.get("MEM", "8G")
WALL_LIMIT = int(os.environ.get("LIMIT", "3600"))


class CheckError(RuntimeError):
    pass


def check(cond: bool, message: str) -> None:
    if not cond:
        raise CheckError(message)


# ---------------------------------------------------------------------------------------------------------------
# Arithmetic over F_p


def sqrt_minus_one(p: int) -> int:
    """The root of -1 modulo p that the orchestrator's probe used: the first of 3^((p-1)/4), +1, +2, ..."""
    root = pow(3, (p - 1) // 4, p)
    while root * root % p != p - 1:
        root += 1
        check(root < p, f"no square root of -1 modulo {p}")
    return root


I = sqrt_minus_one(P)  # noqa: E741 -- the imaginary unit of F_P
INV2 = pow(2, P - 2, P)
INV2I = pow(2 * I, P - 2, P)
# SQRT_TABLE[a] is the smaller square root of a modulo P (0 when a is not a square): roots come in pairs t, P - t.
SQRT_TABLE = np.zeros(P, dtype=np.int64)
SQRT_TABLE[(np.arange(1, (P - 1) // 2 + 1, dtype=np.int64) ** 2) % P] = np.arange(1, (P - 1) // 2 + 1)
IS_SQUARE = np.zeros(P, dtype=bool)
IS_SQUARE[0] = True
IS_SQUARE[(np.arange(1, (P - 1) // 2 + 1, dtype=np.int64) ** 2) % P] = True


def sqrt_mod(a: int) -> int | None:
    """The smaller square root of a modulo P, or None for a non-residue."""
    a %= P
    if not IS_SQUARE[a]:
        return None
    return int(SQRT_TABLE[a])


@functools.cache
def sign_table(dim: int) -> np.ndarray:
    return np.array([[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)], dtype=np.int64)


def left_matrix(dim: int, x: Any) -> np.ndarray:
    """L_x modulo P: column c holds x e_c = sum_k x_k cd_sign(dim, k, c) e_(k XOR c)."""
    sign = sign_table(dim)
    cols = np.arange(dim)
    m = np.zeros((dim, dim), dtype=np.int64)
    for k in range(dim):
        xk = int(x[k]) % P
        if xk:
            m[k ^ cols, cols] += (xk * sign[k]) % P
    return m % P


def rank_mod(m: np.ndarray, p: int = P) -> int:
    """Rank over F_p by Gauss-Jordan elimination; every entry stays below p^2 < 2^63."""
    a = m.copy() % p
    rows, cols = a.shape
    r = 0
    for c in range(cols):
        nonzero = np.nonzero(a[r:, c])[0]
        if nonzero.size == 0:
            continue
        piv = r + int(nonzero[0])
        if piv != r:
            a[[r, piv]] = a[[piv, r]]
        a[r] = a[r] * pow(int(a[r, c]), p - 2, p) % p
        factor = a[:, c].copy()
        factor[r] = 0
        a = (a - np.outer(factor, a[r])) % p
        r += 1
        if r == rows:
            break
    return r


def nullity_mod(dim: int, x: Any) -> int:
    return dim - rank_mod(left_matrix(dim, x))


def nullity_q(dim: int, x: list[int]) -> int:
    """dim - rank of L_x over Q for an integer vector, from cd_core.left_mult_matrix_exact."""
    rows = [[flint.fmpq(c.numerator, c.denominator) for c in r] for r in left_mult_matrix_exact(dim, x)]
    return dim - int(flint.fmpq_mat(rows).rank())


# ---------------------------------------------------------------------------------------------------------------
# W8 and J from the strata record's code, through the neighbor evidence script


@functools.cache
def neighbor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_w8_a4_restriction_neighbor", NEIGHBOR)
    if spec is None or spec.loader is None:
        raise CheckError("the W8 restriction script is not importable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sing_ideal(name: str, gens: list[Any]) -> str:
    return f"ideal {name} = " + ",\n".join(str(g) for g in gens) + ";\n"


def sparse(gens: list[Any]) -> list[list[tuple[tuple[tuple[int, int], ...], int]]]:
    """Each polynomial as ((variable, exponent) pairs, coefficient) terms, for evaluation in worker processes."""
    out = []
    for g in gens:
        terms = []
        for exps, coeff in g.to_dict().items():
            terms.append((tuple((i, e) for i, e in enumerate(exps) if e), int(coeff)))
        out.append(terms)
    return out


def evaluate_sparse(poly: list[tuple[tuple[tuple[int, int], ...], int]], x: list[int]) -> int:
    total = 0
    for mono, coeff in poly:
        term = coeff
        for var, exp in mono:
            term = term * pow(x[var], exp, P) % P
        total = (total + term) % P
    return total


def j_values(y: list[int]) -> list[int]:
    """J(y) = (y_0, y_8, U - V, W) modulo P."""
    u, v = y[1:8], y[9:16]
    uu = sum(a * a for a in u) % P
    vv = sum(a * a for a in v) % P
    uv = sum(a * b for a, b in zip(u, v, strict=True)) % P
    return [y[0] % P, y[8] % P, (uu - vv) % P, uv]


# ---------------------------------------------------------------------------------------------------------------
# Singular drivers


def change_of_variables(signs: list[int]) -> str:
    """The images y_k -> x_k + signs[k] * c * x_(16+k), k = 0..15, with c the root of -1 of the Singular ring."""
    parts = []
    for k, s in enumerate(signs):
        parts.append(f"x{k} {'+' if s > 0 else '-'} c*x{16 + k}")
    return ", ".join(parts)


def variant_block(tag: str, w_name: str, signs_z: list[int], signs_b: list[int]) -> str:
    """Singular text that tests W = J(z) + J(z') for one choice of the two changes of variables."""
    return (
        f"map Fz_{tag} = r, {change_of_variables(signs_z)};\n"
        f"map Fb_{tag} = r, {change_of_variables(signs_b)};\n"
        f"ideal T_{tag} = Fz_{tag}(J) + Fb_{tag}(J);\n"
        f"ideal sT_{tag} = std(T_{tag});\n"
        f'"RESULT {tag}_W_in_T", size(reduce({w_name}, sT_{tag})) == 0;\n'
        f'"RESULT {tag}_T_in_W", size(reduce(T_{tag}, s{w_name})) == 0;\n'
        f'"RESULT {tag}_reduced_bases_identical", string(sT_{tag}) == string(s{w_name});\n'
    )


def ring_text(prime: int) -> str:
    return f"ring R = {prime}, ({', '.join(X_NAMES)}), dp;\n"


def j_ring_text(prime: int) -> str:
    return f"ring r = {prime}, ({', '.join(Y_NAMES)}), dp;\n"


def hilbert_lines(tag: str, ideal_name: str) -> str:
    return (
        f'"RESULT {tag}_dim", dim({ideal_name});\n'
        f'"RESULT {tag}_mult", mult({ideal_name});\n'
        f'"RESULT {tag}_hilb1", string(hilb({ideal_name}, 1));\n'
        f'"RESULT {tag}_hilb2", string(hilb({ideal_name}, 2));\n'
    )


def main_driver() -> str:
    """p = 32009: both containments, dimension, degree, Hilbert numerators and the real slice."""
    plus = [1] * 16
    minus = [-1] * 16
    slice_vars = ", ".join(f"x{k}" for k in range(16, 32))
    f0_images = ", ".join(f"x{k}" for k in range(16))
    return (
        "// W8 = J(z) + J(z') over F_32009; every result line starts with RESULT.\n"
        + j_ring_text(P)
        + '< "ideal_J.sing";\n'
        + ring_text(P)
        + '< "ideal_W8.sing";\n'
        + f"number c = {I};\n"
        + 'option(redSB);\n"RESULT c_squared_is_minus_one", c*c + 1 == 0;\n'
        + '"RESULT generators_W8", size(W);\n'
        + "ideal sW = std(W);\n"
        + hilbert_lines("W8", "sW")
        + variant_block("twisted", "W", plus, minus)
        + hilbert_lines("twisted", "sT_twisted")
        + f"ideal S = {slice_vars};\n"
        + f"map F0 = r, {f0_images};\n"
        + "ideal JS = F0(J) + S;\n"
        + "ideal sJS = std(JS);\n"
        + "ideal sWS = std(W + S);\n"
        + "ideal sZS = std(Fz_twisted(J) + S);\nideal sBS = std(Fb_twisted(J) + S);\n"
        + '"RESULT slice_W8_plus_S_in_JS", size(reduce(W + S, sJS)) == 0;\n'
        + '"RESULT slice_JS_in_W8_plus_S", size(reduce(JS, sWS)) == 0;\n'
        + '"RESULT slice_reduced_bases_identical", string(sWS) == string(sJS);\n'
        + '"RESULT slice_Jz_equals_JS", string(sZS) == string(sJS);\n'
        + '"RESULT slice_Jzp_equals_JS", string(sBS) == string(sJS);\n'
        + hilbert_lines("slice", "sWS")
        + "quit;\n"
    )


def hilbert_driver() -> str:
    """p = 32003 holds no square root of -1: the W8 ideal's dimension, degree and Hilbert numerators only."""
    return (
        "// W8 over F_32003 (no i): Hilbert data only; every result line starts with RESULT.\n"
        + ring_text(P_NO_I)
        + '< "ideal_W8.sing";\n'
        + "option(redSB);\n"
        + "ideal sW = std(W);\n"
        + '"RESULT generators_W8", size(W);\n'
        + hilbert_lines("W8", "sW")
        + "quit;\n"
    )


def controls_driver() -> str:
    """Mutation controls at p = 32009: one flipped sign, every sign flipped, and two altered W8 ideals."""
    plus = [1] * 16
    minus = [-1] * 16
    one_flip = [-1] * 16
    one_flip[3] = 1
    swap_z = [-1] * 16
    swap_b = [1] * 16
    return (
        "// Mutation controls of the twisted-product identity at p = 32009; every result line starts with RESULT.\n"
        + j_ring_text(P)
        + '< "ideal_J.sing";\n'
        + ring_text(P)
        + '< "ideal_W8.sing";\n'
        + '< "ideal_W8_sign.sing";\n'
        + '< "ideal_W8_nopure.sing";\n'
        + f"number c = {I};\n"
        + "option(redSB);\n"
        + "ideal sW = std(W);\nideal sWsign = std(Wsign);\nideal sWnopure = std(Wnopure);\n"
        + variant_block("unmutated", "W", plus, minus)
        + variant_block("one_sign_flipped", "W", plus, one_flip)
        + variant_block("all_signs_flipped_swaps_z_and_zprime", "W", swap_z, swap_b)
        + variant_block("W8_with_U_plus_V", "Wsign", plus, minus)
        + variant_block("W8_without_x0_x16", "Wnopure", plus, minus)
        + "quit;\n"
    )


def singular_binary() -> str:
    given = os.environ.get("SINGULAR")
    if given:
        return given
    found = sorted(
        glob.glob(
            str(Path.home() / ".cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages")
            + "/sage_wheels/bin/Singular"
        )
    )
    check(bool(found), "the passagemath Singular binary is missing; set SINGULAR")
    return found[0]


RESULT_LINE = re.compile(r"^RESULT (\S+) ?(.*)$")


def parse_results(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        match = RESULT_LINE.match(line)
        if match:
            out[match.group(1)] = match.group(2).strip()
    return out


def run_singular(workdir: Path, driver_name: str, log_name: str, label: str) -> dict[str, Any]:
    """Run one driver in workdir under a cgroup memory cap with /usr/bin/time -v, write the log, parse RESULT lines."""
    binary = singular_binary()
    version = subprocess.run(
        [binary, "-v", "-q", "--execute", "quit;"], capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    version_line = (version.stdout.splitlines() or ["unknown"])[0]
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cmd = [
        "systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={MEMORY_CAP}", "-p", "MemorySwapMax=0",
        "timeout", "-k", "10", str(WALL_LIMIT), "/usr/bin/time", "-v", binary, "-q", "--no-warn", driver_name,
    ]  # fmt: skip
    env = dict(os.environ, MALLOC_ARENA_MAX="2")
    done = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    header = (
        f"driver {driver_name}\nlabel {label}\nbinary Singular (passagemath venv)\n{version_line}\n"
        f"memory cap {MEMORY_CAP} (cgroup MemoryMax, MemorySwapMax=0), wall cap {WALL_LIMIT} s\n{started}\n"
    )
    footer = f"exit status {done.returncode}\n{finished}\n"
    # Singular writes RESULT lines to stdout and /usr/bin/time -v writes its accounting to stderr.
    (workdir / log_name).write_text(header + done.stdout + done.stderr + footer, encoding="utf-8")
    check(done.returncode == 0, f"Singular driver {driver_name} exited {done.returncode}: {done.stderr[-400:]}")
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", done.stderr)
    wall = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)", done.stderr)
    if rss is None or wall is None:
        raise CheckError(f"{driver_name}: /usr/bin/time -v accounting is missing")
    return {
        "results": parse_results(done.stdout),
        "version": version_line,
        "max_rss_kib": int(rss.group(1)),
        "wall": wall.group(1),
        "log": log_name,
    }


def hilbert_numerator(text: str) -> list[int]:
    """The first Hilbert numerator that Singular's string(hilb(I, 1)) prints; the trailing zero entry is dropped."""
    values = [int(t) for t in text.split(",")]
    check(values[-1] == 0, "hilb(I, 1) ends with the 0 entry that closes the numerator")
    return values[:-1]


def polynomial_product(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def n_j() -> list[int]:
    """The first Hilbert numerator of J over (1 - t)^16: (1 - t)^2 (1 - t^2)^2."""
    num = [1]
    for factor in ([1, -1], [1, -1], [1, 0, -1], [1, 0, -1]):
        num = polynomial_product(num, factor)
    return num


def write_inputs(workdir: Path) -> dict[str, str]:
    """Write the Singular inputs; the generators come from the strata record's own code."""
    nb = neighbor()
    w8 = nb.w8_ideal_32()
    j = nb.restrict_to_a4(w8)
    files = {
        "ideal_J.sing": sing_ideal("J", j),
        "ideal_W8.sing": sing_ideal("W", w8),
        "ideal_W8_sign.sing": sing_ideal("Wsign", nb.w8_ideal_32("w8_sign")),
        "ideal_W8_nopure.sing": sing_ideal("Wnopure", nb.w8_ideal_32("w8_no_pure")),
        "driver_32009.sing": main_driver(),
        "driver_32003.sing": hilbert_driver(),
        "driver_controls.sing": controls_driver(),
    }
    hashes = {}
    for name, text in files.items():
        (workdir / name).write_text(text, encoding="utf-8")
        hashes[name] = hashlib.sha256(text.encode()).hexdigest()
    return hashes


# ---------------------------------------------------------------------------------------------------------------
# Statement 1


def twisted_product(workdir: Path) -> dict[str, Any]:
    main = run_singular(workdir, "driver_32009.sing", "log_32009.txt", "twisted product at p = 32009")
    low = run_singular(workdir, "driver_32003.sing", "log_32003.txt", "Hilbert series at p = 32003")
    r, h = main["results"], low["results"]
    expected = polynomial_product(n_j(), n_j())
    nb = neighbor()
    j_text = (workdir / "ideal_J.sing").read_text(encoding="utf-8")
    out: dict[str, Any] = {
        "N_J": n_j(),
        "N_J_squared": expected,
        "i_modulo_32009": I,
        "i_squared_plus_one_mod_32009": (I * I + 1) % P,
        "no_square_root_of_minus_one_mod_32003": not any((t * t + 1) % P_NO_I == 0 for t in range(P_NO_I)),
        "w8_crosscheck_against_record_piece_ideals": nb.w8_crosscheck(),
        "ideal_J_matches_neighbor_file": j_text == NEIGHBOR_J.read_text(encoding="utf-8"),
        "W8_generators": int(r["generators_W8"]),
        "p32009": {
            "W8_in_J_z_plus_J_zprime": r["twisted_W_in_T"] == "1",
            "J_z_plus_J_zprime_in_W8": r["twisted_T_in_W"] == "1",
            "reduced_standard_bases_identical": r["twisted_reduced_bases_identical"] == "1",
            "dim": int(r["W8_dim"]),
            "degree": int(r["W8_mult"]),
            "hilbert_numerator": hilbert_numerator(r["W8_hilb1"]),
            "hilbert_second_series": r["W8_hilb2"],
            "twisted_ideal_dim": int(r["twisted_dim"]),
            "twisted_ideal_degree": int(r["twisted_mult"]),
            "twisted_ideal_hilbert_numerator": hilbert_numerator(r["twisted_hilb1"]),
        },
        "p32003_hilbert_only": {
            "dim": int(h["W8_dim"]),
            "degree": int(h["W8_mult"]),
            "hilbert_numerator": hilbert_numerator(h["W8_hilb1"]),
            "hilbert_second_series": h["W8_hilb2"],
        },
        "real_slice": {
            "W8_plus_slice_in_J_plus_slice": r["slice_W8_plus_S_in_JS"] == "1",
            "J_plus_slice_in_W8_plus_slice": r["slice_JS_in_W8_plus_S"] == "1",
            "reduced_standard_bases_identical": r["slice_reduced_bases_identical"] == "1",
            "J_z_slice_equals_J_slice": r["slice_Jz_equals_JS"] == "1",
            "J_zprime_slice_equals_J_slice": r["slice_Jzp_equals_JS"] == "1",
            "dim": int(r["slice_dim"]),
            "degree": int(r["slice_mult"]),
        },
        "singular": {k: main[k] for k in ("version", "max_rss_kib", "wall", "log")},
        "singular_32003": {k: low[k] for k in ("max_rss_kib", "wall", "log")},
    }
    p9, p3 = out["p32009"], out["p32003_hilbert_only"]
    out["pass"] = bool(
        out["w8_crosscheck_against_record_piece_ideals"]["pass"]
        and out["ideal_J_matches_neighbor_file"]
        and out["i_squared_plus_one_mod_32009"] == 0
        and out["no_square_root_of_minus_one_mod_32003"]
        and p9["W8_in_J_z_plus_J_zprime"]
        and p9["J_z_plus_J_zprime_in_W8"]
        and p9["reduced_standard_bases_identical"]
        and p9["dim"] == 24
        and p9["degree"] == 16
        and p9["hilbert_numerator"] == expected
        and p9["twisted_ideal_hilbert_numerator"] == expected
        and (p3["dim"], p3["degree"], p3["hilbert_numerator"]) == (24, 16, expected)
        and p3["hilbert_second_series"] == p9["hilbert_second_series"]
        and all(v for k, v in out["real_slice"].items() if isinstance(v, bool))
        and out["real_slice"]["dim"] == 12
        and out["real_slice"]["degree"] == 4
    )
    return out


def mutation_controls(workdir: Path) -> dict[str, Any]:
    run = run_singular(workdir, "driver_controls.sing", "log_controls.txt", "mutation controls at p = 32009")
    r = run["results"]

    def pair(tag: str) -> tuple[bool, bool]:
        return r[f"{tag}_W_in_T"] == "1", r[f"{tag}_T_in_W"] == "1"

    tags = [
        "unmutated",
        "one_sign_flipped",
        "all_signs_flipped_swaps_z_and_zprime",
        "W8_with_U_plus_V",
        "W8_without_x0_x16",
    ]
    rows = {
        t: {"W_in_T": pair(t)[0], "T_in_W": pair(t)[1], "identical": r[f"{t}_reduced_bases_identical"] == "1"}
        for t in tags
    }
    out: dict[str, Any] = {
        "rows": rows,
        "unmutated_equal": rows["unmutated"]["identical"],
        "one_sign_flip_breaks_equality": not (
            rows["one_sign_flipped"]["W_in_T"] and rows["one_sign_flipped"]["T_in_W"]
        ),
        "swap_keeps_equality": rows["all_signs_flipped_swaps_z_and_zprime"]["identical"],
        "U_plus_V_breaks_equality": not (rows["W8_with_U_plus_V"]["W_in_T"] and rows["W8_with_U_plus_V"]["T_in_W"]),
        "without_pure_equations_breaks_equality": not (
            rows["W8_without_x0_x16"]["W_in_T"] and rows["W8_without_x0_x16"]["T_in_W"]
        ),
        "singular": {k: run[k] for k in ("max_rss_kib", "wall", "log")},
    }
    out["pass"] = bool(
        out["unmutated_equal"]
        and out["one_sign_flip_breaks_equality"]
        and out["swap_keeps_equality"]
        and out["U_plus_V_breaks_equality"]
        and out["without_pure_equations_breaks_equality"]
    )
    return out


# ---------------------------------------------------------------------------------------------------------------
# Statement 2


def spectrum_row(w8: list[Any], item: tuple[int, int, int]) -> dict[str, Any]:
    """The nullities of the mixed basis pair x = e_i + s e_(16+j) and of its two complex halves."""
    i, j, s = item
    x = [0] * 32
    x[i] = 1
    x[16 + j] = s % P
    low, high = x[:16], x[16:]
    z = [(a + I * b) % P for a, b in zip(low, high, strict=True)]
    zb = [(a - I * b) % P for a, b in zip(low, high, strict=True)]
    real = [0] * 16
    real[i] += 1
    real[j] += s % P
    x_exact = [0] * 32
    x_exact[i] = 1
    x_exact[16 + j] = s
    real_exact = [0] * 16
    real_exact[i] += 1
    real_exact[j] += s
    n32 = nullity_mod(32, x)
    n_real = nullity_mod(16, real)
    return {
        "i": i,
        "j": j,
        "s": s,
        "n32": n32,
        "n16z": nullity_mod(16, z),
        "n16zb": nullity_mod(16, zb),
        "n16real": n_real,
        "n32_over_Q": nullity_q(32, x_exact),
        "n16real_over_Q": nullity_q(16, real_exact),
        "w8_member": all(evaluate_sparse(g, x) == 0 for g in w8),
        "z_in_J": not any(j_values(z)),
        "zb_in_J": not any(j_values(zb)),
    }


def pair_class(i: int, j: int) -> str:
    if i == 0 and j == 0:
        return "i=j=0"
    if i == j:
        return "i=j>0"
    if i == 0:
        return "i=0,j>0"
    if j == 0:
        return "j=0,i>0"
    return "i,j>0,i!=j"


def nullity_spectrum(w8_sparse: list[Any]) -> dict[str, Any]:
    items = [(i, j, s) for i in range(16) for j in range(16) for s in (1, -1)]
    rows = parallel.ordered_map(functools.partial(spectrum_row, w8_sparse), items)
    cells = Counter((r["n32"], r["n16z"], r["n16zb"]) for r in rows)
    joint = Counter((r["n32"], r["n16z"], r["n16zb"], r["n16real"]) for r in rows)
    on_w8 = Counter((r["n32"], r["n16z"], r["n16zb"], r["n16real"], r["w8_member"]) for r in rows)
    by_class: dict[str, Counter[tuple[int, int, int, int]]] = {}
    for r in rows:
        by_class.setdefault(pair_class(r["i"], r["j"]), Counter())[(r["n32"], r["n16z"], r["n16zb"], r["n16real"])] += 1
    holds = sum(1 for r in rows if r["n32"] == r["n16z"] + r["n16zb"])
    generic = [r for r in rows if r["i"] > 0 and r["j"] > 0 and r["i"] != r["j"]]
    exceptional = [r for r in rows if not (r["i"] > 0 and r["j"] > 0 and r["i"] != r["j"])]
    mixed_rule_generic = all(r["n32"] == 12 - 2 * r["n16real"] for r in generic)
    mixed_rule_whole = [(r["i"], r["j"], r["s"]) for r in rows if r["n32"] != 12 - 2 * r["n16real"]]
    mixed_rule_failing_classes = Counter(pair_class(i, j) for i, j, _ in mixed_rule_whole)
    equal_halves = all(r["n16z"] == r["n16zb"] for r in rows)
    out: dict[str, Any] = {
        "pairs": len(rows),
        "cells_n32_n16z_n16zb": {",".join(map(str, k)): v for k, v in sorted(cells.items())},
        "sum_rule_holds": holds,
        "sum_rule_fails": len(rows) - holds,
        "joint_law_n32_n16z_n16zb_n16real": {",".join(map(str, k)): v for k, v in sorted(joint.items())},
        "joint_law_with_w8_membership": {
            ",".join(str(t) if not isinstance(t, bool) else ("on_W8" if t else "off_W8") for t in k): v
            for k, v in sorted(on_w8.items())
        },
        "joint_law_by_pair_class": {
            cls: {",".join(map(str, k)): v for k, v in sorted(c.items())} for cls, c in sorted(by_class.items())
        },
        "pair_class_sizes": dict(sorted(Counter(pair_class(r["i"], r["j"]) for r in rows).items())),
        "n16z_equals_n16zb_on_every_pair": equal_halves,
        "n16z_eq_8_minus_n16real_on_i_j_positive_distinct": all(r["n16z"] == 8 - r["n16real"] for r in generic),
        "mixed_rule_n32_eq_12_minus_2_n16real_on_i_j_positive_distinct": mixed_rule_generic,
        "generic_pairs": len(generic),
        "exceptional_pairs": len(exceptional),
        "mixed_rule_failing_pairs": len(mixed_rule_whole),
        "mixed_rule_failing_pair_classes": dict(sorted(mixed_rule_failing_classes.items())),
        "exceptional_pairs_n32_values": sorted({r["n32"] for r in exceptional}),
        "exceptional_pairs_real_nullity_values": sorted({r["n16real"] for r in exceptional}),
        "x_in_W8_pairs": sum(1 for r in rows if r["w8_member"]),
        "z_in_J_pairs": sum(1 for r in rows if r["z_in_J"]),
        "ranks_over_Q_agree_with_mod_p": all(
            r["n32_over_Q"] == r["n32"] and r["n16real_over_Q"] == r["n16real"] for r in rows
        ),
        "rows": [[r["i"], r["j"], r["s"], r["n32"], r["n16z"], r["n16zb"], r["n16real"]] for r in rows],
    }
    out["pass"] = bool(
        len(rows) == 512
        and dict(cells) == BASIS_CELLS
        and out["sum_rule_holds"] == 32
        and out["sum_rule_fails"] == 480
        and equal_halves
        and mixed_rule_generic
        and out["n16z_eq_8_minus_n16real_on_i_j_positive_distinct"]
        and out["exceptional_pairs_n32_values"] == [0]
        and out["ranks_over_Q_agree_with_mod_p"]
    )
    return out


# ---------------------------------------------------------------------------------------------------------------
# Statement 3


def point_on_j(rng: np.random.Generator) -> np.ndarray:
    """A point of V(J) over F_P: u in F_P^7 and v in u-perp with v.v = u.u, so that u.v = 0 and U = V.

    The draw order (u, two basis vectors, retries on a zero norm, a zero quadratic coefficient or a non-residue
    discriminant) fixes the stream, which the recorded ten-point sample depends on.
    """
    while True:
        u = rng.integers(0, P, 7)
        c = int(u @ u % P)
        basis = [rng.integers(0, P, 7) for _ in range(2)]
        if c == 0:
            continue
        inv = pow(c, P - 2, P)
        v0, w = [(b - (int(u @ b) * inv % P) * u) % P for b in basis]
        a, b1, c0 = int(w @ w % P), int(2 * (v0 @ w) % P), int((v0 @ v0 - c) % P)
        if a == 0:
            continue
        root = sqrt_mod(b1 * b1 - 4 * a * c0)
        if root is None:
            continue
        t = (-b1 + root) * pow(2 * a, P - 2, P) % P
        v = (v0 + t * w) % P
        z = np.zeros(16, dtype=np.int64)
        z[1:8] = u
        z[9:16] = v
        check(
            int(z[1:8] @ z[1:8] - z[9:16] @ z[9:16]) % P == 0 and int(z[1:8] @ z[9:16]) % P == 0,
            "the sampled point lies on U = V and W = 0",
        )
        return z


def draw_halves(rng: np.random.Generator, kind: str) -> tuple[np.ndarray, np.ndarray]:
    """The pair (z, z') of a class; offW8 keeps the orchestrator's discarded V(J) draw so the stream matches."""
    z = point_on_j(rng) if kind != "generic" else rng.integers(0, P, 16)
    if kind == "diag":
        return z, z.copy()
    if kind == "generic":
        return z, rng.integers(0, P, 16)
    zb = point_on_j(rng)
    if kind == "offW8":
        zb = rng.integers(0, P, 16)
    return z, zb


def to_x(z: np.ndarray, zb: np.ndarray) -> list[int]:
    """x_low = (z + z')/2 and x_high = (z - z')/(2 i), so that z = x_low + i x_high and z' = x_low - i x_high."""
    low = (z + zb) * INV2 % P
    high = (z - zb) * INV2I % P
    return [int(t) for t in low] + [int(t) for t in high]


def point_row(w8: list[Any], item: tuple[str, list[int], list[int]]) -> dict[str, Any]:
    kind, z, zb = item
    x = to_x(np.array(z, dtype=np.int64), np.array(zb, dtype=np.int64))
    x_low, x_high = x[:16], x[16:]
    check(
        all((a + I * b) % P == c for a, b, c in zip(x_low, x_high, z, strict=True))
        and all((a - I * b) % P == c for a, b, c in zip(x_low, x_high, zb, strict=True)),
        "the change of variables inverts",
    )
    return {
        "kind": kind,
        "n32": nullity_mod(32, x),
        "n16z": nullity_mod(16, z),
        "n16zb": nullity_mod(16, zb),
        "z_in_J": not any(j_values(z)),
        "zb_in_J": not any(j_values(zb)),
        "x_in_W8": all(evaluate_sparse(g, x) == 0 for g in w8),
    }


def seed_values() -> list[int]:
    """The two draw values the literal W8_SAMPLE_SEEDS names, re-read from the retained draw."""
    draw = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    values = [int(draw["values"][k]) for k in SEED_INDICES]
    check(values == W8_SAMPLE_SEEDS, f"{DRAW} indices {SEED_INDICES} hold {values}, not {W8_SAMPLE_SEEDS}")
    return values


def sample_points(w8_sparse: list[Any]) -> dict[str, Any]:
    values = seed_values()
    # Draw every input first, then map the rank computations.
    rng10 = np.random.default_rng(W8_SAMPLE_SEEDS)
    sample10 = []
    for kind in SAMPLE10_KINDS:
        z, zb = draw_halves(rng10, kind)
        sample10.append((kind, [int(t) for t in z], [int(t) for t in zb]))
    rng = np.random.default_rng(W8_SAMPLE_SEEDS)
    batches = []
    for kind in CLASSES:
        for _ in range(POINTS_PER_CLASS):
            z, zb = draw_halves(rng, kind)
            batches.append((kind, [int(t) for t in z], [int(t) for t in zb]))
    worker = functools.partial(point_row, w8_sparse)
    rows10 = parallel.ordered_map(worker, sample10)
    rows = parallel.ordered_map(worker, batches)
    triples10 = [(r["n32"], r["n16z"], r["n16zb"]) for r in rows10]
    classes: dict[str, Any] = {}
    for kind in CLASSES:
        cls = [r for r in rows if r["kind"] == kind]
        joint = Counter((r["n32"], r["n16z"], r["n16zb"]) for r in cls)
        holds = sum(1 for r in cls if r["n32"] == r["n16z"] + r["n16zb"])
        classes[kind] = {
            "points": len(cls),
            "sum_rule_holds": holds,
            "sum_rule_fails": len(cls) - holds,
            "joint_n32_n16z_n16zb": {",".join(map(str, k)): v for k, v in sorted(joint.items())},
            "z_in_J": sum(1 for r in cls if r["z_in_J"]),
            "zprime_in_J": sum(1 for r in cls if r["zb_in_J"]),
            "x_in_W8": sum(1 for r in cls if r["x_in_W8"]),
        }
    out: dict[str, Any] = {
        "draw": DRAW,
        "seed_indices": list(SEED_INDICES),
        "seed_values": values,
        "numpy": np.__version__,
        "ten_point_sample": {
            "kinds": list(SAMPLE10_KINDS),
            "rows_n32_n16z_n16zb": [list(t) for t in triples10],
            "reproduces_recorded_sample": triples10 == SAMPLE10_ROWS,
            "sum_rule_held_on_all": all(a == b + c for a, b, c in triples10),
            "on_W8_points": [r["x_in_W8"] for r in rows10],
        },
        "points_per_class": POINTS_PER_CLASS,
        "classes": classes,
        "class_order": list(CLASSES),
    }
    out["pass"] = bool(
        out["ten_point_sample"]["reproduces_recorded_sample"]
        and classes["W8"]["x_in_W8"] == POINTS_PER_CLASS
        and classes["diag"]["x_in_W8"] == POINTS_PER_CLASS
        and classes["offW8"]["x_in_W8"] < POINTS_PER_CLASS
        and all(c["points"] == POINTS_PER_CLASS for c in classes.values())
    )
    return out


# ---------------------------------------------------------------------------------------------------------------
# Self-test


def self_test() -> int:
    nb = neighbor()
    # The F_P matrices agree with cd_core on integer vectors in 16 and 32 dimensions.
    for dim in (16, 32):
        for j in range(6):
            v = [((k * k * 7 + j * 13 + 3) % 11) - 5 for k in range(dim)]
            exact = left_mult_matrix_exact(dim, v)
            check(
                all(int(exact[r][c]) % P == int(left_matrix(dim, v)[r, c]) for r in range(dim) for c in range(dim)),
                f"left_matrix agrees with cd_core at dimension {dim}",
            )
            check(nullity_mod(dim, v) == nullity_q(dim, v), f"rank mod P equals the rank over Q at dimension {dim}")
    # rank_mod on a matrix of known rank and on a zero-divisor of A_4.
    check(rank_mod(np.eye(5, dtype=np.int64)) == 5 and rank_mod(np.zeros((4, 6), dtype=np.int64)) == 0, "rank_mod")
    zd = [0] * 16
    zd[1], zd[10] = 1, 1
    check(nullity_mod(16, zd) == 4, "e_1 + e_10 is a zero-divisor of nullity 4")
    # The sqrt table equals the first root a brute-force search finds.
    for a in (0, 1, 4, 9, 2, 3, 5, 12345, 32008, 31999):
        brute = next((t for t in range(P) if t * t % P == a), None)
        check(sqrt_mod(a) == brute, f"sqrt_mod({a}) equals the brute-force root")
    check(I * I % P == P - 1, "I squares to -1 modulo P")
    # A W8 point (z, z') lies on W8, and moving one coordinate of z off V(J) changes the sum-rule row.
    w8_sparse = sparse(nb.w8_ideal_32())
    rng = np.random.default_rng(W8_SAMPLE_SEEDS)
    z, zb = draw_halves(rng, "W8")
    row = point_row(w8_sparse, ("W8", [int(t) for t in z], [int(t) for t in zb]))
    check(row["x_in_W8"] and row["z_in_J"] and row["zb_in_J"], "a sampled W8 point vanishes on every W8 generator")
    moved = z.copy()
    moved[1] = (moved[1] + 1) % P
    row2 = point_row(w8_sparse, ("W8", [int(t) for t in moved], [int(t) for t in zb]))
    check(not row2["x_in_W8"] and not row2["z_in_J"], "moving one coordinate of z leaves V(J) and W8")
    check(row2["n16z"] < row["n16z"], "the moved point has lower nullity than the zero-divisor point")
    # The mixed basis pair e_0 + e_17 breaks the sum rule: n_32 = 0 while z = e_0 + i e_1 has n_16 = 8.
    r01 = spectrum_row(w8_sparse, (0, 1, 1))
    check((r01["n32"], r01["n16z"], r01["n16zb"]) == (0, 8, 8), "the mixed pair e_0 + e_17 has cell (0, 8, 8)")
    # Singular mutation controls: one flipped sign breaks the identity, the swap keeps it.
    with tempfile.TemporaryDirectory(prefix="w8twisted-") as tmp:
        work = Path(tmp)
        write_inputs(work)
        controls = mutation_controls(work)
    check(controls["pass"], f"mutation controls: {json.dumps(controls['rows'])}")
    print("self-test ok")
    return 0


# ---------------------------------------------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", type=Path, help="evidence directory: Singular inputs, logs and result.json")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        ap.error("--out DIR or --self-test is required")
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    report: dict[str, Any] = {}
    nb = neighbor()
    w8_sparse = sparse(nb.w8_ideal_32())
    stamps: dict[str, float] = {}

    def stage(name: str, fn: Any) -> None:
        start = time.perf_counter()
        report[name] = fn()
        stamps[name] = round(time.perf_counter() - start, 2)

    report["sing_sha256"] = write_inputs(out)
    stage("twisted_product", lambda: twisted_product(out))
    stage("mutation_controls", lambda: mutation_controls(out))
    stage("nullity_spectrum", lambda: nullity_spectrum(w8_sparse))
    stage("seeded_points", lambda: sample_points(w8_sparse))
    report["stage_seconds"] = stamps
    report["total_s"] = round(time.perf_counter() - t0, 2)
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["versions"] = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "python-flint": flint.__version__,
        "singular": report["twisted_product"]["singular"]["version"],
    }
    failed = [k for k, v in report.items() if isinstance(v, dict) and v.get("pass") is False]
    (out / "result.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"total {report['total_s']} s; failed: {', '.join(failed) or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
