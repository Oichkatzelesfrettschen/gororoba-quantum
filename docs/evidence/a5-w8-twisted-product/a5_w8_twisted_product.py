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

Statement 4 (pair table). On W8 = V(J) x V(J) the script tabulates n_32 against the pair (n_16(z), n_16(z')) over
finite classes (the 512 mixed basis pairs, the 168 basis-type deep points of V(J) with every relation to each other,
the real zero-divisor diagonals) and 64-point random classes drawn from numpy.random.default_rng(PAIR_TABLE_SEEDS),
the values at indices 7 and 8 of the draw named by DRAW. A deep point has n_16 = 8: u isotropic and v = 0, or u = 0
and v isotropic. Every rank is also computed by python-flint's nmod_mat, and Gaussian-rational points are checked
by exact ranks over Q(i). Diagonal points (z = z') also check L_x = diag(L_z, R_z) and rank R_z = rank L_z.

Usage:
    "$PYTHON" -B -W error a5_w8_twisted_product.py --self-test
    "$PYTHON" -B -W error a5_w8_twisted_product.py --out docs/evidence/a5-w8-twisted-product
    "$PYTHON" -B -W error a5_w8_twisted_product.py --out docs/evidence/a5-w8-twisted-product --pair-table
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
# Values at indices 7 and 8 of the same draw DRAW, for the pair table; the run raises when the file disagrees.
PAIR_TABLE_SEEDS = [45825, 59536]
PAIR_SEED_INDICES = (7, 8)
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


def left_matrix(dim: int, x: Any, sign: np.ndarray | None = None) -> np.ndarray:
    """L_x modulo P: column c holds x e_c = sum_k x_k cd_sign(dim, k, c) e_(k XOR c); sign replaces the table."""
    if sign is None:
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


def nullity_mod(dim: int, x: Any, sign: np.ndarray | None = None) -> int:
    return dim - rank_mod(left_matrix(dim, x, sign))


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


def memory_cap_command() -> tuple[list[str], str]:
    """The limiter prefix and its log description: a user cgroup scope where the user bus answers, else prlimit --as."""
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime and Path(runtime, "bus").is_socket():
        prefix = ["systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={MEMORY_CAP}", "-p", "MemorySwapMax=0"]
        return prefix, f"memory cap {MEMORY_CAP} (cgroup MemoryMax, MemorySwapMax=0)"
    units = {"K": 1 << 10, "M": 1 << 20, "G": 1 << 30, "T": 1 << 40}
    match = re.fullmatch(r"(\d+)([KMGT]?)", MEMORY_CAP)
    if match is None:
        raise CheckError(f"MEM={MEMORY_CAP!r} is not a size such as 8G")
    limit = int(match.group(1)) * units.get(match.group(2), 1)
    return ["prlimit", f"--as={limit}"], f"address-space cap {MEMORY_CAP} (prlimit --as; no user bus)"


def run_singular(workdir: Path, driver_name: str, log_name: str, label: str) -> dict[str, Any]:
    """Run one driver in workdir under a memory cap with /usr/bin/time -v, write the log, parse RESULT lines."""
    binary = singular_binary()
    version = subprocess.run(
        [binary, "-v", "-q", "--execute", "quit;"], capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    version_line = (version.stdout.splitlines() or ["unknown"])[0]
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    prefix, cap_note = memory_cap_command()
    cmd = [
        *prefix, "timeout", "-k", "10", str(WALL_LIMIT), "/usr/bin/time", "-v", binary, "-q", "--no-warn", driver_name,
    ]  # fmt: skip
    env = dict(os.environ, MALLOC_ARENA_MAX="2")
    done = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    header = (
        f"driver {driver_name}\nlabel {label}\nbinary Singular (passagemath venv)\n{version_line}\n"
        f"{cap_note}, wall cap {WALL_LIMIT} s\n{started}\n"
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
# Statement 4 (pair table)

RANDOM_POINTS = 64
RANDOM_CLASS_ORDER = (
    "gen-gen",
    "gen-deep",
    "deep-gen",
    "deep-deep",
    "deep-deep-from-basis",
    "zero-gen",
    "gen-zero",
    "zero-deep",
    "deep-zero",
    "diag-gen",
    "diag-deep",
    "conj-gen",
    "conj-deep",
    "proportional-deep",
)
# Expected cells (n_32, n_16(z), n_16(z')) per class; deep-deep-from-basis meets proportional pairs now and then.
PAIR_EXPECTED: dict[str, set[tuple[int, int, int]]] = {
    "gen-gen": {(8, 4, 4)},
    "gen-deep": {(10, 4, 8)},
    "deep-gen": {(10, 8, 4)},
    "deep-deep": {(12, 8, 8)},
    "deep-deep-from-basis": {(12, 8, 8), (16, 8, 8)},
    "zero-gen": {(20, 16, 4)},
    "gen-zero": {(20, 4, 16)},
    "zero-deep": {(22, 16, 8)},
    "deep-zero": {(22, 8, 16)},
    "diag-gen": {(8, 4, 4)},
    "diag-deep": {(16, 8, 8)},
    "conj-gen": {(8, 4, 4)},
    "conj-deep": {(16, 8, 8)},
    "proportional-deep": {(16, 8, 8)},
    "mixed-basis": set(BASIS_CELLS),
    "zero-zero": {(32, 16, 16)},
    "deep-basis-diag": {(16, 8, 8)},
    "deep-basis-conj": {(16, 8, 8)},
    "deep-basis-gauss-conj": {(12, 8, 8)},
    "deep-basis-zero": {(22, 8, 16)},
    "zero-deep-basis": {(22, 16, 8)},
    "real-zd-diag": {(8, 4, 4)},
    "deep-basis-all-pairs": {(12, 8, 8), (16, 8, 8)},
}
FINITE_CLASSES = (
    "mixed-basis",
    "zero-zero",
    "deep-basis-diag",
    "deep-basis-conj",
    "deep-basis-gauss-conj",
    "deep-basis-zero",
    "zero-deep-basis",
    "real-zd-diag",
    "deep-basis-all-pairs",
)
# The mutated sign entry (dimension 32, row k, column c) flips cd_sign for the product e_1 e_3 and acts on x = e_1 + ...
MUTATED_SIGN_ENTRY = (1, 3)


def conj_vector(z: Any) -> list[int]:
    """The sedenion conjugate: the real coordinate stays and every other coordinate changes sign."""
    return [int(z[0]) % P] + [(-int(t)) % P for t in z[1:]]


def right_matrix(dim: int, z: Any) -> np.ndarray:
    """R_z modulo P: column c holds e_c z = sum_k z_k cd_sign(dim, c, k) e_(c XOR k)."""
    sign = sign_table(dim)
    cols = np.arange(dim)
    m = np.zeros((dim, dim), dtype=np.int64)
    for k in range(dim):
        zk = int(z[k]) % P
        if zk:
            m[cols ^ k, cols] += (zk * sign[cols, k]) % P
    return m % P


def conj_matrix(dim: int) -> np.ndarray:
    return np.diag([1] + [P - 1] * (dim - 1)).astype(np.int64)


def flint_rank(m: np.ndarray) -> int:
    rows, cols = m.shape
    return int(flint.nmod_mat(rows, cols, [int(t) for t in m.flatten()], P).rank())


def diag_identities(z: list[int], m32: np.ndarray) -> tuple[bool, bool, bool]:
    """For x = (z, 0): L_x = diag(L_z, R_z), rank R_z = rank L_z, and R_z = C L_(z*) C with C the conjugation."""
    lz = left_matrix(16, z)
    rz = right_matrix(16, z)
    block = (
        np.array_equal(m32[:16, :16], lz)
        and np.array_equal(m32[16:, 16:], rz)
        and not m32[:16, 16:].any()
        and not m32[16:, :16].any()
    )
    c = conj_matrix(16)
    conj_ok = np.array_equal(rz, c @ left_matrix(16, conj_vector(z)) @ c % P)
    return bool(block), rank_mod(rz) == rank_mod(lz), bool(conj_ok)


def integer_basis_identities() -> dict[str, bool]:
    """The two diagonal identities on the 16 basis vectors over Z; both are linear in z, so they hold over every ring.

    L_(z,0) = diag(L_z, R_z) is read off cd_core.left_mult_matrix_exact, and R_z = C L_(z*) C compares the integer
    right matrix built from cd_core.cd_sign with the conjugated left matrix. For pure z, z* = -z, so rank R_z =
    rank L_z over every field in which C is invertible, which holds in every characteristic since C * C = 1.
    """
    block, conj = True, True
    sgn = [1] + [-1] * 15
    for k in range(16):
        e = [0] * 16
        e[k] = 1
        e32 = [0] * 32
        e32[k] = 1
        big = left_mult_matrix_exact(32, e32)
        lz = left_mult_matrix_exact(16, e)
        rz = [[0] * 16 for _ in range(16)]
        for c in range(16):
            rz[c ^ k][c] += cd_sign(16, c, k)
        zstar = [0] * 16
        zstar[k] = sgn[k]
        lzs = left_mult_matrix_exact(16, zstar)
        block &= all(
            big[r][c] == lz[r][c] and big[16 + r][16 + c] == rz[r][c] and big[r][16 + c] == 0 and big[16 + r][c] == 0
            for r in range(16)
            for c in range(16)
        )
        conj &= all(rz[r][c] == sgn[r] * lzs[r][c] * sgn[c] for r in range(16) for c in range(16))
    return {"block_form_on_16_basis_vectors": bool(block), "R_z_equals_C_L_zbar_C_on_16_basis_vectors": bool(conj)}


def pair_row(flip: tuple[int, int] | None, w8: list[Any], item: tuple[str, list[int], list[int]]) -> tuple[Any, ...]:
    """(class, n_32, n_16(z), n_16(z'), flint agrees, x on W8, z in V(J), z' in V(J), diagonal identities or None).

    flip names one dimension-32 sign entry whose sign is reversed before the rank; the 16-dimensional ranks keep
    the cd_core table. The flint rank is an independent implementation of the same matrix rank over F_P.
    """
    kind, z, zb = item
    x = to_x(np.array(z, dtype=np.int64), np.array(zb, dtype=np.int64))
    sign32 = None
    if flip is not None:
        sign32 = sign_table(32).copy()
        sign32[flip] = -sign32[flip]
    m32 = left_matrix(32, x, sign32)
    n32 = 32 - rank_mod(m32)
    agree = 32 - flint_rank(m32) == n32
    diag = diag_identities(z, m32) if z == zb and flip is None else None
    on_w8 = all(evaluate_sparse(g, x) == 0 for g in w8)
    return (
        kind,
        n32,
        nullity_mod(16, z),
        nullity_mod(16, zb),
        agree,
        on_w8,
        not any(j_values(z)),
        not any(j_values(zb)),
        diag,
    )


def deep_basis_points() -> list[list[int]]:
    """z = e_a + i s e_b for a != b in 1..15, s = +-1, that lie in V(J) with n_16(z) = 8: 84 per block, 168 in all."""
    points = []
    for a in range(1, 16):
        for b in range(1, 16):
            for s in (1, -1):
                if a == b:
                    continue
                z = [0] * 16
                z[a] = 1
                z[b] = I * s % P
                if not any(j_values(z)) and nullity_mod(16, z) == 8:
                    points.append(z)
    return points


def real_zd_points() -> list[list[int]]:
    """z = e_a + s e_b for a < b in 1..15, s = +-1, that lie in V(J): the real zero-divisors among the basis pairs."""
    points = []
    for a in range(1, 16):
        for b in range(a + 1, 16):
            for s in (1, -1):
                z = [0] * 16
                z[a] = 1
                z[b] = s % P
                if not any(j_values(z)):
                    points.append(z)
    return points


def isotropic_vector(rng: np.random.Generator) -> list[int]:
    """A nonzero u in F_P^7 with u.u = 0: six uniform coordinates and the last from a square root table."""
    while True:
        head = rng.integers(0, P, 6)
        root = sqrt_mod(-int(head @ head))
        if root is not None and (root or head.any()):
            return [int(t) for t in head] + [root]


def deep_point(rng: np.random.Generator) -> list[int]:
    """A point of V(J) with n_16 = 8: v = 0 and u isotropic, or u = 0 and v isotropic (a fair coin picks the block)."""
    z = [0] * 16
    block = int(rng.integers(0, 2))
    z[1 + 8 * block : 8 + 8 * block] = isotropic_vector(rng)
    return z


def zero_vector() -> list[int]:
    return [0] * 16


def basis_form(z: list[int]) -> tuple[int, int, int]:
    """(p, q, t) with p < q and z = z_p (e_p + t e_q) for a deep basis point z (two nonzero coordinates)."""
    p, q = [k for k in range(16) if z[k]]
    return p, q, z[q] * pow(z[p], P - 2, P) % P


def twisted_match(z: list[int], zb: list[int]) -> tuple[bool, bool]:
    """(same XOR class p xor q, t' = cd_sign(p, p') cd_sign(q, q') t) for two deep basis points."""
    p, q, t = basis_form(z)
    p2, q2, t2 = basis_form(zb)
    sign = cd_sign(16, p, p2) * cd_sign(16, q, q2)
    return (p ^ q) == (p2 ^ q2), t2 == sign * t % P


def relation(z: list[int], zb: list[int]) -> str:
    """The family of an ordered pair of deep basis points, by support, XOR class and the twisted sign match."""
    same_class, matched = twisted_match(z, zb)
    if not same_class:
        return "different XOR class"
    if basis_form(z)[:2] == basis_form(zb)[:2]:
        return "same support, same line (z' = z up to a scalar)" if matched else "same support, other line"
    return "same XOR class, other support, sign match" if matched else "same XOR class, other support, sign mismatch"


def mixed_basis_items() -> list[tuple[str, list[int], list[int]]]:
    items = []
    for i in range(16):
        for j in range(16):
            for s in (1, -1):
                x = [0] * 32
                x[i] = 1
                x[16 + j] = s % P
                items.append(
                    (
                        "mixed-basis",
                        [(a + I * b) % P for a, b in zip(x[:16], x[16:], strict=True)],
                        [(a - I * b) % P for a, b in zip(x[:16], x[16:], strict=True)],
                    )
                )
    return items


def finite_items(deep: list[list[int]]) -> list[tuple[str, list[int], list[int]]]:
    zero = zero_vector()
    items = [("zero-zero", zero, zero)]
    items += mixed_basis_items()
    for z in deep:
        items.append(("deep-basis-diag", z, z))
        items.append(("deep-basis-conj", z, conj_vector(z)))
        flipped = list(z)
        flipped[[k for k in range(16) if z[k]][1]] *= -1
        items.append(("deep-basis-gauss-conj", z, [t % P for t in flipped]))
        items.append(("deep-basis-zero", z, zero))
        items.append(("zero-deep-basis", zero, z))
    items += [("real-zd-diag", z, z) for z in real_zd_points()]
    items += [("deep-basis-all-pairs", z, zb) for z in deep for zb in deep]
    return items


def random_items(rng: np.random.Generator, deep: list[list[int]]) -> list[tuple[str, list[int], list[int]]]:
    """64 points per random class in RANDOM_CLASS_ORDER; every input is drawn before any rank."""
    zero = zero_vector()
    items: list[tuple[str, list[int], list[int]]] = []

    def gen() -> list[int]:
        return [int(t) for t in point_on_j(rng)]

    for kind in RANDOM_CLASS_ORDER:
        for _ in range(RANDOM_POINTS):
            if kind == "gen-gen":
                pair = (gen(), gen())
            elif kind == "gen-deep":
                pair = (gen(), deep_point(rng))
            elif kind == "deep-gen":
                pair = (deep_point(rng), gen())
            elif kind == "deep-deep":
                pair = (deep_point(rng), deep_point(rng))
            elif kind == "deep-deep-from-basis":
                pair = (deep[int(rng.integers(0, len(deep)))], deep[int(rng.integers(0, len(deep)))])
            elif kind == "zero-gen":
                pair = (zero, gen())
            elif kind == "gen-zero":
                pair = (gen(), zero)
            elif kind == "zero-deep":
                pair = (zero, deep_point(rng))
            elif kind == "deep-zero":
                pair = (deep_point(rng), zero)
            elif kind == "diag-gen":
                z = gen()
                pair = (z, list(z))
            elif kind == "diag-deep":
                z = deep_point(rng)
                pair = (z, list(z))
            elif kind == "conj-gen":
                z = gen()
                pair = (z, conj_vector(z))
            elif kind == "conj-deep":
                z = deep_point(rng)
                pair = (z, conj_vector(z))
            else:
                z = deep_point(rng)
                lam = int(rng.integers(2, P - 1))
                pair = (z, [lam * t % P for t in z])
            items.append((kind, pair[0], pair[1]))
    return items


def pair_seed_values() -> list[int]:
    """The two draw values the literal PAIR_TABLE_SEEDS names, re-read from the retained draw."""
    draw = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    values = [int(draw["values"][k]) for k in PAIR_SEED_INDICES]
    check(values == PAIR_TABLE_SEEDS, f"{DRAW} indices {PAIR_SEED_INDICES} hold {values}, not {PAIR_TABLE_SEEDS}")
    return values


# Gaussian-rational points for the characteristic-0 cross-check: real parts and imaginary parts as integer lists.
GaussVector = tuple[list[int], list[int]]


def nullity_qi(dim: int, vec: GaussVector) -> int:
    """dim - rank over Q(i) of L_(re + i im), from the realified matrix [[A, -B], [B, A]] whose rank is twice it."""
    a = [[flint.fmpq(c.numerator, c.denominator) for c in r] for r in left_mult_matrix_exact(dim, vec[0])]
    b = [[flint.fmpq(c.numerator, c.denominator) for c in r] for r in left_mult_matrix_exact(dim, vec[1])]
    rows = [ra + [-t for t in rb] for ra, rb in zip(a, b, strict=True)] + [rb + ra for ra, rb in zip(a, b, strict=True)]
    rank = int(flint.fmpq_mat(rows).rank())
    check(rank % 2 == 0, "the realified rank is even")
    return dim - rank // 2


def gauss_to_mod(vec: GaussVector) -> list[int]:
    return [(a + I * b) % P for a, b in zip(vec[0], vec[1], strict=True)]


def gauss_x(z: GaussVector, zb: GaussVector) -> GaussVector:
    """2 x for z = x_low + i x_high and z' = x_low - i x_high: (z + z') then -i (z - z'); the rank is scale free."""
    sum_re = [a + c for a, c in zip(z[0], zb[0], strict=True)]
    sum_im = [a + c for a, c in zip(z[1], zb[1], strict=True)]
    dif_re = [a - c for a, c in zip(z[0], zb[0], strict=True)]
    dif_im = [a - c for a, c in zip(z[1], zb[1], strict=True)]
    # -i (dif_re + i dif_im) = dif_im - i dif_re
    return sum_re + dif_im, sum_im + [-t for t in dif_re]


def qi_point(rng: np.random.Generator, kind: str) -> GaussVector:
    """A rational point of V(J) over Q(i) with n_16 = 4 (gen), 8 (deep) or 0 (zero), built from Pythagorean triples."""
    re, im = [0] * 16, [0] * 16
    if kind == "zero":
        return re, im
    offsets = [int(t) for t in rng.permutation(7)]
    triples = [(1, 2, 2), (2, 2, 1), (2, 1, 2)]
    pick = triples[int(rng.integers(0, 3))]
    sign = [int(rng.choice([-1, 1])) for _ in range(3)]
    if kind == "gen":
        # u = (1, 2, 2) and v = (2, 2, 1) permuted on disjoint offsets: U = V = 9 and W = 0, a real zero-divisor
        for t in range(3):
            re[1 + offsets[t]] = pick[t] * sign[t]
            re[9 + offsets[3 + t]] = triples[(triples.index(pick) + 1) % 3][t]
        return re, im
    # deep: u = a + i b with a = (1, 2, 2) and b = (2, 1, -2) on the same offsets: a.a = b.b = 9 and a.b = 0
    base = 1 if int(rng.integers(0, 2)) == 0 else 9
    for t in range(3):
        re[base + offsets[t]] = (1, 2, 2)[t]
        im[base + offsets[t]] = (2, 1, -2)[t]
    return re, im


QI_CLASSES = (
    ("gen-gen", "gen", "gen"),
    ("gen-deep", "gen", "deep"),
    ("deep-gen", "deep", "gen"),
    ("deep-deep", "deep", "deep"),
    ("zero-gen", "zero", "gen"),
    ("deep-zero", "deep", "zero"),
    ("diag-deep", "deep", "same"),
    ("conj-deep", "deep", "negative"),
    ("proportional-deep", "deep", "double"),
)


def q_cross_row(item: tuple[str, Any, Any]) -> tuple[str, tuple[int, int, int], tuple[int, int, int]]:
    """Exact nullities over Q(i) of one point pair against the F_P nullities of the same pair."""
    name, z, zb = item
    x = gauss_x(z, zb)
    exact = (nullity_qi(32, x), nullity_qi(16, z), nullity_qi(16, zb))
    zp, zbp = gauss_to_mod(z), gauss_to_mod(zb)
    modp = (
        nullity_mod(32, to_x(np.array(zp, dtype=np.int64), np.array(zbp, dtype=np.int64))),
        nullity_mod(16, zp),
        nullity_mod(16, zbp),
    )
    return name, exact, modp


def q_cross_check(rng: np.random.Generator) -> dict[str, Any]:
    """Exact ranks over Q(i) of L_x for Gaussian-rational points, against the F_P ranks of the same points."""
    # Every point is drawn first, in the generator's order, then the independent rank checks are mapped.
    items = []
    for name, first, second in QI_CLASSES:
        for _ in range(8):
            z = qi_point(rng, first)
            if second == "same":
                zb = (list(z[0]), list(z[1]))
            elif second == "negative":
                zb = ([z[0][0]] + [-t for t in z[0][1:]], [z[1][0]] + [-t for t in z[1][1:]])
            elif second == "double":
                zb = ([2 * t for t in z[0]], [2 * t for t in z[1]])
            else:
                zb = qi_point(rng, second)
            items.append((name, z, zb))
    rows = parallel.ordered_map(q_cross_row, items)
    classes: dict[str, Any] = {}
    for name, _, _ in QI_CLASSES:
        cls = [r for r in rows if r[0] == name]
        classes[name] = {
            "points": len(cls),
            "cells": [list(k) for k in sorted({r[1] for r in cls})],
            "cells_over_Q_i": dict(Counter(",".join(map(str, r[1])) for r in cls)),
            "agrees_with_mod_p": all(r[1] == r[2] for r in cls),
        }
    return {
        "points": len(rows),
        "classes": classes,
        "expected_cells_only": all(set(map(tuple, c["cells"])) <= PAIR_EXPECTED[n] for n, c in classes.items()),
        "all_agree": all(r[1] == r[2] for r in rows),
    }


def witness_pair() -> dict[str, Any]:
    """The two points of the factor stratum (8, 8) that carry n_32 = 12 and 16, with exact ranks over Q(i)."""
    low, high = [0] * 16, [0] * 16
    low[1], high[2] = 1, 1
    z = (low, high)  # z = e_1 + i e_2
    zc = (list(low), [-t for t in high])  # z' = e_1 - i e_2
    out = {}
    for label, pair in (("n32_12_gaussian_conjugate", (z, zc)), ("n32_16_diagonal", (z, z))):
        x = gauss_x(*pair)
        zp, zbp = gauss_to_mod(pair[0]), gauss_to_mod(pair[1])
        out[label] = {
            "z": "e_1 + i e_2",
            "zprime": "e_1 - i e_2" if label.endswith("conjugate") else "e_1 + i e_2",
            "over_F_32009": [
                nullity_mod(32, to_x(np.array(zp, dtype=np.int64), np.array(zbp, dtype=np.int64))),
                nullity_mod(16, zp),
                nullity_mod(16, zbp),
            ],
            "over_Q_i": [nullity_qi(32, x), nullity_qi(16, pair[0]), nullity_qi(16, pair[1])],
        }
    return out


def pair_table(w8_sparse: list[Any]) -> dict[str, Any]:
    values = pair_seed_values()
    deep = deep_basis_points()
    check(len(deep) == 168, f"{len(deep)} deep basis points, expected 168")
    rng = np.random.default_rng(PAIR_TABLE_SEEDS)
    items = random_items(rng, deep) + finite_items(deep)
    # The Q(i) points draw from the same stream after every random class, so the whole run follows one seed.
    q_check = q_cross_check(rng)
    worker = functools.partial(pair_row, None, w8_sparse)
    rows = parallel.ordered_map(worker, items)
    by_class: dict[str, list[tuple[Any, ...]]] = {}
    for r in rows:
        by_class.setdefault(r[0], []).append(r)
    classes: dict[str, Any] = {}
    for kind in (*RANDOM_CLASS_ORDER, *FINITE_CLASSES):
        cls = by_class[kind]
        cells = Counter((r[1], r[2], r[3]) for r in cls)
        diag = [r[8] for r in cls if r[8] is not None]
        classes[kind] = {
            "kind": "finite" if kind in FINITE_CLASSES else "random",
            "points": len(cls),
            "cells_n32_n16z_n16zb": {",".join(map(str, k)): v for k, v in sorted(cells.items())},
            "expected_cells_only": set(cells) <= PAIR_EXPECTED[kind],
            "sum_rule_holds": sum(1 for r in cls if r[1] == r[2] + r[3]),
            "x_on_W8": sum(1 for r in cls if r[5]),
            "z_in_J": sum(1 for r in cls if r[6]),
            "zprime_in_J": sum(1 for r in cls if r[7]),
            "flint_rank_agrees": sum(1 for r in cls if r[4]),
            "diagonal_points": len(diag),
            "diagonal_block_form": sum(1 for d in diag if d[0]),
            "diagonal_rank_R_eq_rank_L": sum(1 for d in diag if d[1]),
            "diagonal_R_eq_C_L_conj_C": sum(1 for d in diag if d[2]),
        }
    # Relation to the cells of every ordered pair of deep basis points.
    rel_cells: dict[str, Counter[tuple[int, int, int]]] = {}
    for (kind, z, zb), r in zip(items, rows, strict=True):
        if kind == "deep-basis-all-pairs":
            rel_cells.setdefault(relation(z, zb), Counter())[(r[1], r[2], r[3])] += 1
    # Fitted on this enumeration: n_32 = 16 exactly when p xor q = p' xor q' and t' = cd_sign(p, p') cd_sign(q, q') t.
    relation_rule = all(
        (r[1] == 16) == all(twisted_match(z, zb))
        for (kind, z, zb), r in zip(items, rows, strict=True)
        if kind == "deep-basis-all-pairs"
    )
    # The joint map over the points on W8: (n_16(z), n_16(z')) -> {n_32: count}.
    joint: dict[tuple[int, int], Counter[int]] = {}
    for r in rows:
        if r[5]:
            joint.setdefault((r[2], r[3]), Counter())[r[1]] += 1
    joint_map = {f"{a},{b}": {str(k): v for k, v in sorted(c.items())} for (a, b), c in sorted(joint.items())}
    multivalued = {key: val for key, val in joint_map.items() if len(val) > 1}
    generic_sum = classes["gen-gen"]["sum_rule_holds"] == RANDOM_POINTS
    diag_rows = [r for r in rows if r[8] is not None]
    out: dict[str, Any] = {
        "draw": DRAW,
        "seed_indices": list(PAIR_SEED_INDICES),
        "seed_values": values,
        "numpy": np.__version__,
        "points_per_random_class": RANDOM_POINTS,
        "deep_basis_points": len(deep),
        "total_points": len(rows),
        "classes": classes,
        "deep_basis_all_pairs_by_relation": {
            rel: {",".join(map(str, k)): v for k, v in sorted(c.items())} for rel, c in sorted(rel_cells.items())
        },
        "rule_n32_16_iff_same_xor_class_and_sign_match": relation_rule,
        "joint_map_on_W8": joint_map,
        "pair_law_refuted": bool(multivalued),
        "pair_law_multivalued_keys": multivalued,
        "generic_stratum_sum_rule_on_sampled_class": generic_sum,
        "diagonal_identities": {
            "points": len(diag_rows),
            "pure_points": sum(1 for (_, z, zb), r in zip(items, rows, strict=True) if r[8] is not None and z[0] == 0),
            "block_form_L_z_R_z": sum(1 for r in diag_rows if r[8][0]),
            "rank_R_z_equals_rank_L_z": sum(1 for r in diag_rows if r[8][1]),
            "R_z_equals_C_L_zbar_C": sum(1 for r in diag_rows if r[8][2]),
            "n32_equals_2_n16": sum(1 for r in rows if r[8] is not None and r[1] == 2 * r[2]),
        },
        "integer_basis_identities": integer_basis_identities(),
        "witnesses": witness_pair(),
        "cross_check_over_Q_i": q_check,
    }
    flint_ok = all(r[4] for r in rows)
    out["flint_rank_agrees_on_every_point"] = flint_ok
    out["pass"] = bool(
        all(c["expected_cells_only"] for c in classes.values())
        and all(c["points"] == RANDOM_POINTS for k, c in classes.items() if c["kind"] == "random")
        and all(c["x_on_W8"] == c["points"] for k, c in classes.items() if k != "mixed-basis")
        and classes["mixed-basis"]["x_on_W8"] == 168
        and relation_rule
        and bool(multivalued)
        and set(multivalued) == {"8,8"}
        and generic_sum
        and flint_ok
        and out["diagonal_identities"]["block_form_L_z_R_z"] == len(diag_rows)
        and out["diagonal_identities"]["rank_R_z_equals_rank_L_z"] == len(diag_rows)
        and out["diagonal_identities"]["R_z_equals_C_L_zbar_C"] == len(diag_rows)
        and all(out["integer_basis_identities"].values())
        and q_check["all_agree"]
        and q_check["expected_cells_only"]
        and all(w["over_F_32009"] == w["over_Q_i"] for w in out["witnesses"].values())
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
    # Pair-table mutation: the clean cells of the mixed basis pairs and the deep diagonal hit their expected values,
    # and reversing one dimension-32 sign entry changes at least one cell.
    deep = deep_basis_points()
    check(len(deep) == 168, "168 deep basis points")
    probe = mixed_basis_items() + [("deep-basis-diag", z, z) for z in deep]
    clean = Counter(pair_row(None, w8_sparse, it)[:4] for it in probe)
    expected = Counter({("mixed-basis", *k): v for k, v in BASIS_CELLS.items()})
    expected[("deep-basis-diag", 16, 8, 8)] = 168
    check(clean == expected, f"clean pair-table cells {dict(clean)}")
    mutated = Counter(pair_row(MUTATED_SIGN_ENTRY, w8_sparse, it)[:4] for it in probe)
    check(mutated != clean, f"flipping the sign entry {MUTATED_SIGN_ENTRY} leaves every pair-table cell unchanged")
    check(len(pair_seed_values()) == 2, "the pair-table draw values match PAIR_TABLE_SEEDS")
    # Singular mutation controls: one flipped sign breaks the identity, the swap keeps it.
    with tempfile.TemporaryDirectory(prefix="w8twisted-") as tmp:
        work = Path(tmp)
        write_inputs(work)
        controls = mutation_controls(work)
    check(controls["pass"], f"mutation controls: {json.dumps(controls['rows'])}")
    print("self-test ok")
    return 0


# ---------------------------------------------------------------------------------------------------------------


def pair_table_only(out: Path) -> int:
    """Recompute the pair table and store it under "pair_table" in the existing result.json, keeping the other keys."""
    path = out / "result.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    start = time.perf_counter()
    table = pair_table(sparse(neighbor().w8_ideal_32()))
    table["seconds"] = round(time.perf_counter() - start, 2)
    table["python"] = sys.version.split()[0]
    table["python_flint"] = flint.__version__
    table["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["pair_table"] = table
    path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"pair table {table['seconds']} s; pass: {table['pass']}")
    return 0 if table["pass"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", type=Path, help="evidence directory: Singular inputs, logs and result.json")
    ap.add_argument(
        "--pair-table",
        action="store_true",
        help="with --out: recompute only the pair table into the existing result.json and keep every other key",
    )
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        ap.error("--out DIR or --self-test is required")
    out: Path = args.out
    if args.pair_table:
        return pair_table_only(out)
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
    stage("pair_table", lambda: pair_table(w8_sparse))
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
