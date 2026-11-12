"""Exact certificate over Q(i) that the E8-bar slice ideal is an ideal of S = P + P b (I = I S).

Setting (`../a5-exceptional-fibers/monomial-ladder/README.md`, A5-306 and A5-309). In the polynomial model of S
(variables qw, qr, qs, qz, qa, qb, qu modulo qu (1 + qw) = 1 and qb^2 = EA (EA - qw (qw + 2)) qu^2), It_k is the
image of the k-th generator G_k of the Q(i) producer (`reduction_check._script`) under the slice parametrization
(`slice_rings_qi.E8_IMAGES`). The ideal m_R S equals n = (qa, qz, qr, qs, qb, qw^2) S: t2 = qa, t3 = qz,
t4 - t5 = qs, t6 + t7 = qr, t8 = -I qb and t9 = -sign qw^2 qu / 2 put n inside m_R S, and the exact run reduces the
nine coordinate images modulo n to zero, so m_R S lies in n. S / n = Q(i) + Q(i) qw (colength 2).

Certificate. For each of the 42 targets t = qw It_j and t = (qu - 1) It_j the record holds Gaussian rationals
alpha_tk, beta_tk and polynomials D_txk with

    t = sum_k (alpha_tk + beta_tk (qu - 1)) It_k + sum_(x, k) D_txk x It_k    in S,

x running over the six generators of n. Each identity is checked exactly over Q(i) in Singular (characteristic 0,
minpoly I^2 + 1, global ordering dp, reduction modulo the relations of S). Modulo n, qu - 1 = -qw + qw^2 qu, so in
I S / n I S the class [t] (= [qw It_j] or -[qw It_j]) plus sum_k beta_tk [qw It_k] lies in the span of the [It_k].
The 42 rows (+-e_j + beta_t) have exact rank 21 over Q(i), hence every qw It_j lies in sum_k Q(i) It_k + n I S. With
S = R + R qw (S finite over R and S / m_R S spanned by 1 and qw) and n I S = m_R (I S), I S = sum_k R It_k +
m_R (I S), and Nakayama's lemma over the local ring R gives I S = I.

Search. D_txk is a combination of monomials qb^b m^e qr^i qs^j qz^k qa^l (m = 1 + qw, m^-1 = qu) inside one box
(weight b + i + j + k + l + weight of x It_k at most WEIGHT, every exponent of m inside M_RANGE). At each split prime
p = 1 (mod 4) and each root r of -1 the generators are reduced at (p, i -> r), and the box matrix (columns It_k, the
box multiples of x It_k, then (qu - 1) It_k, then the 42 targets) is brought to reduced row echelon form; the target
columns give the coordinates on the pivot columns. The reduced echelon form is unique, so these coordinates are the
reductions of one Q(i) solution at all but finitely many primes. The two roots give the real and imaginary parts;
Chinese remaindering and rational reconstruction give Gaussian rationals, and primes are added until two consecutive
reconstructions agree. The modular work only finds the certificate; the exact check is the proof.

    "$PYTHON" docs/evidence/a5-char0-transfer/e8_closure_certificate.py --write --slug e8-nm
    "$PYTHON" docs/evidence/a5-char0-transfer/e8_closure_certificate.py --check --slug e8-nm

`--write` writes `e8-closure-certificate-SLUG.json` and the cofactor file `cofactors/e8-closure-SLUG.json.xz`;
`--check` verifies the recorded digests, reruns the exact check from the cofactor file, and runs two mutations that
must fail it: one cofactor coefficient changed, and one coefficient of the generator G_1 changed. The digests cover the
cofactor file, the Q(i) producer script, its J and G, and the sources of this script, `slice_rings_qi.py` and
`reduction_check.py`, so an edit of any of those three Python files makes `--check` fail with a request to regenerate
the records with `--write`; the README records measured generation costs. Check scripts and diagnostics go into
an ignored workspace, preserving retained generation logs. The default execution admits two process workers with
a twelve-GiB planning budget. An explicit four-worker run needs at least twenty-one GiB of declared budget, with
native arithmetic threads fixed at one. Each generated record binds the actual worker count and execution flags.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import lzma
import math
import os
import platform
import re
import resource
import signal
import subprocess
import sys
import time
from array import array
from collections.abc import Iterator
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint
import sympy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import reduction_check as rc  # noqa: E402
import slice_rings_qi as srq  # noqa: E402

import parallel  # noqa: E402

SIGN = {"e8-nm": 1, "e8-np": -1}
NAMES = ("qw", "qr", "qs", "qz", "qa", "qb", "qu")
LAURENT = ("qb", "m", "mi", "qr", "qs", "qz", "qa")
# The generators of n with their Singular text; "w2" is qw^2 = (m - 1)^2.
N_GENERATORS = (("qa", "qa"), ("qz", "qz"), ("qr", "qr"), ("qs", "qs"), ("qb", "qb"), ("w2", "qw^2"))
# Box of the search: total weight in (qb, qr, qs, qz, qa) and the exponent range of m = 1 + qw.
WEIGHT = 10
M_RANGE = (-7, 9)
# Split primes below 2^15 with a fixed root of -1: the two primes of the fiber track, then descending from 32749 with
# the smaller square root of -1. Both roots of each prime are used.
PRIMES = (
    (32009, 10754),
    (32029, 9115),
    (32749, 15645),
    (32717, 11332),
    (32713, 974),
    (32693, 8590),
    (32653, 4607),
    (32633, 1886),
    (32621, 7484),
    (32609, 4740),
    (32573, 2938),
    (32569, 15018),
    (32561, 744),
    (32537, 13908),
)
MIN_PRIMES = 2
TIMEOUT_SECONDS = 3300
DEFAULT_WORKERS = 2
DEFAULT_MEMORY_BUDGET_GIB = 12
WORKER_MEMORY_RESERVE_GIB = 5
CONTROLLER_MEMORY_RESERVE_GIB = 1
NATIVE_THREAD_FLAGS = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
WORK = ROOT / "docs" / "local" / "e8-closure-certificate"
LOGS = HERE / "logs"
COFACTORS = HERE / "cofactors"
Key = tuple[int, int, int, int, int, int]  # (b, e, i, j, k, l): qb^b m^e qr^i qs^j qz^k qa^l
Poly = dict[Key, int]
Label = tuple[str, int, str, int, Key]  # (kind, generator, x, qb factor, multiplier)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _execution_settings(workers: int, memory_budget_gib: int) -> dict[str, Any]:
    """Admit the requested process count against a declared resident-memory planning budget.

    Each modular worker measured 4.073 GiB peak process RSS; five GiB reserves that observation plus margin.
    The declared budget admits concurrency and sets no operating-system memory or swap limit.
    """
    if type(workers) is not int or not 1 <= workers <= 4:
        raise ValueError("workers must be between 1 and 4")
    if type(memory_budget_gib) is not int or memory_budget_gib < 1:
        raise ValueError("memory budget must be a positive number of GiB")
    effective = min(workers, parallel.workers())
    required = CONTROLLER_MEMORY_RESERVE_GIB + WORKER_MEMORY_RESERVE_GIB * effective
    if memory_budget_gib < required:
        raise ValueError(f"{effective} workers require a declared budget of at least {required} GiB")
    return {
        "requested_workers": workers,
        "effective_workers": effective,
        "memory_budget_gib": memory_budget_gib,
        "required_memory_gib": required,
        "worker_memory_reserve_gib": WORKER_MEMORY_RESERVE_GIB,
        "controller_memory_reserve_gib": CONTROLLER_MEMORY_RESERVE_GIB,
        "memory_budget_is_admission_only": True,
    }


@contextmanager
def _execution_scope(workers: int, memory_budget_gib: int) -> Iterator[dict[str, Any]]:
    settings = _execution_settings(workers, memory_budget_gib)
    replacements = {name: "1" for name in NATIVE_THREAD_FLAGS}
    replacements["GOROROBA_WORKERS"] = str(settings["effective_workers"])
    previous = {name: os.environ.get(name) for name in replacements}
    previous_flint_threads = flint.ctx.threads
    try:
        os.environ.update(replacements)
        flint.ctx.threads = 1
        settings.update(
            {
                "native_threads": 1,
                "environment": {
                    name: os.environ.get(name) for name in (*replacements, "GLIBC_TUNABLES", "MALLOC_ARENA_MAX")
                },
                "runtime": {
                    "python": platform.python_version(),
                    "python_flint": flint.__version__,
                    "sympy": sympy.__version__,
                },
            }
        )
        yield settings
    finally:
        flint.ctx.threads = previous_flint_threads
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


@contextmanager
def _check_workspace(slug: str) -> Iterator[None]:
    """Route a check's scripts and diagnostics to one ignored workspace, restoring the generation destinations."""
    global WORK, LOGS
    generation_work, generation_logs = WORK, LOGS
    WORK = generation_work / "checks" / f"{slug}-{os.getpid()}-{time.monotonic_ns()}"
    LOGS = WORK / "logs"
    try:
        yield
    finally:
        WORK, LOGS = generation_work, generation_logs


def _singular(script: str, name: str, timeout: int = TIMEOUT_SECONDS) -> dict[str, Any]:
    """Run one Singular script; its full output goes to logs/NAME.log and the time report to logs/NAME.time."""
    WORK.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    path = WORK / f"{name}.sing"
    path.write_text(script, encoding="utf-8")
    log, report = LOGS / f"{name}.log", LOGS / f"{name}.time"
    started = time.monotonic()
    with log.open("w", encoding="utf-8") as out, report.open("w", encoding="utf-8") as err:
        # Singular is a child of /usr/bin/time, so the command gets its own session and a timeout signals the group.
        process = subprocess.Popen(  # noqa: S603
            ("/usr/bin/time", "-v", "Singular", "-q", "--no-warn", path.name),
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            cwd=WORK,
            start_new_session=True,
        )
        try:
            status = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            status = 124
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
    text = log.read_text(encoding="utf-8")
    peak = re.search(r"Maximum resident set size \(kbytes\): (\d+)", report.read_text(encoding="utf-8"))
    results: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^RESULT (\S+) ?(.*)$", line.strip())
        if match:
            results[match[1]] = match[2].strip()
    errors = [line for line in text.splitlines() if line.strip().startswith("?")]
    return {
        "status": "completed" if status == 0 and not errors else ("timeout" if status == 124 else "failed"),
        "errors": errors[:5],
        "results": results,
        "wall_seconds": round(time.monotonic() - started, 1),
        "peak_rss_kib": int(peak[1]) if peak else None,
    }


def producer(slug: str) -> dict[str, Any]:
    """The Q(i) producer: its presolved J and generators G over Q(i) in t1..t9."""
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False)
    run = _singular(body, f"e8-closure-producer-{slug}")
    _require(run["status"] == "completed", f"{slug} producer: {run['status']} {run['errors']}")
    res = run["results"]
    _require(res["eliminated_count"] == "0", f"{slug}: the presolve removed variables")
    return {
        "J": [res[f"reduced_j_{i}"] for i in range(1, int(res["reduced_j_count"]) + 1)],
        "G": [res[f"reduced_g_{i}"] for i in range(1, int(res["reduced_g_count"]) + 1)],
        "script_sha256": _sha256_bytes(body.encode("utf-8")),
        "wall_seconds": run["wall_seconds"],
        "peak_rss_kib": run["peak_rss_kib"],
    }


def _input_digest(inputs: dict[str, Any]) -> str:
    return _sha256_bytes(json.dumps({"J": inputs["J"], "G": inputs["G"]}, sort_keys=True).encode("utf-8"))


def _setup(slug: str, inputs: dict[str, Any], prime: int | None, root: int | None) -> list[str]:
    """The generators It of I S in the polynomial model of S, over Q(i) or over F_p with I bound to root."""
    variables = ",".join(f"t{i}" for i in range(1, 10))
    if prime is None:
        head = [f"ring R0=(0,I),({variables}),dp;", "minpoly=I2+1;"]
        target = [f"ring G0=(0,I),({','.join(NAMES)}),dp;", "minpoly=I2+1;"]
        bind: list[str] = []
    else:
        head = [f"ring R0={prime},({variables}),dp;", f"number I={root};"]
        target = [f"ring G0={prime},({','.join(NAMES)}),dp;"]
        bind = [f"number I={root};"]
    images = ",".join(srq.E8_IMAGES[f"t{i}"].format(sign=SIGN[slug]) for i in range(1, 10))
    return [
        'system("--ticks-per-sec",1);',
        *head,
        f"ideal ReducedJ={','.join(inputs['J'])};",
        f"ideal ReducedG={','.join(inputs['G'])};",
        "ideal MX=maxideal(1);",
        *target,
        srq.E8_A,
        f"ideal Rel={srq.E8_REL};",
        "qring S=std(Rel);",
        *bind,
        f"map phi=R0,{images};",
        '"RESULT j_nonzero",size(simplify(reduce(phi(ReducedJ),std(0)),2));',
        "ideal It=reduce(phi(ReducedG),std(0)); ideal Am=reduce(phi(MX),std(0)); int n=ncols(It); int j; int k;",
        f"ideal X={','.join(text for _, text in N_GENERATORS)}; ideal sX=std(X);",
        '"RESULT generators",n; "RESULT colength",vdim(sX); "RESULT kbase",string(kbase(sX));',
        '"RESULT am_outside_n",size(simplify(reduce(Am,sX),2));',
        '"RESULT n_outside_am",size(simplify(reduce(X,std(Am)),2));',
    ]


def laurent_script(slug: str, inputs: dict[str, Any], prime: int, root: int, out: str) -> str:
    """Write It at (p, i -> root) in the Laurent form qb^b m^e (...), m = 1 + qw, with b <= 1."""
    lines = _setup(slug, inputs, prime, root) + [
        f"ring L={prime},({','.join(LAURENT)}),(lp(1),dp(6));",
        "poly EA=((m^2+1)*qa-(m^2-1)*qz)/2;",
        "ideal sL=std(ideal(m*mi-1,qb^2-EA*(EA-(m^2-1))*mi^2));",
        "map back=S,m-1,qr,qs,qz,qa,qb,mi; ideal ItL=reduce(back(It),sL);",
        f'link Lk=":w {out}"; for(j=1;j<=ncols(ItL);j++){{ write(Lk,string(ItL[j])); }} close(Lk);',
        "quit;",
    ]
    return "\n".join(lines) + "\n"


TERM = re.compile(r"([+-]?)([^+-]+)")


def _parse_laurent(text: str, prime: int) -> Poly:
    index = {name: i for i, name in enumerate(LAURENT)}
    out: Poly = {}
    for sign, body in TERM.findall(text.replace(" ", "")):
        coefficient, exponents = 1, [0] * len(LAURENT)
        for factor in body.split("*"):
            if factor[0].isdigit():
                coefficient = coefficient * int(factor) % prime
            else:
                name, _, power = factor.partition("^")
                exponents[index[name]] += int(power) if power else 1
        b, mp, mm, i, jj, kk, ll = exponents
        key: Key = (b, mp - mm, i, jj, kk, ll)
        out[key] = (out.get(key, 0) + (-coefficient if sign == "-" else coefficient)) % prime
    return {key: value for key, value in out.items() if value}


def _sum_keys(k1: Key, k2: Key) -> Key:
    return (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2], k1[3] + k2[3], k1[4] + k2[4], k1[5] + k2[5])


class Laurent:
    """Arithmetic in S_m = F_p[m, 1/m, qr, qs, qz, qa][qb] / (qb^2 - F) on dictionaries {Key: residue}."""

    def __init__(self, prime: int) -> None:
        self.p = prime
        half = pow(2, -1, prime)
        # EA = ((m^2 + 1) qa - (m^2 - 1) qz) / 2 and F = EA (EA - (m^2 - 1)) m^-2.
        ea: Poly = {
            (0, 2, 0, 0, 0, 1): half,
            (0, 0, 0, 0, 0, 1): half,
            (0, 2, 0, 0, 1, 0): prime - half,
            (0, 0, 0, 0, 1, 0): half,
        }
        shifted = self.add(ea, {(0, 2, 0, 0, 0, 0): 1, (0, 0, 0, 0, 0, 0): prime - 1}, -1)
        self.f = self.shift(self.mul(ea, shifted), (0, -2, 0, 0, 0, 0))

    def add(self, f: Poly, g: Poly, c: int = 1) -> Poly:
        h = dict(f)
        for key, value in g.items():
            h[key] = (h.get(key, 0) + c * value) % self.p
            if not h[key]:
                del h[key]
        return h

    @staticmethod
    def shift(f: Poly, mono: Key) -> Poly:
        return {_sum_keys(key, mono): c for key, c in f.items()}

    def mul(self, f: Poly, g: Poly) -> Poly:
        """Product of two qb-free polynomials."""
        out: Poly = {}
        for k1, c1 in f.items():
            for k2, c2 in g.items():
                key = _sum_keys(k1, k2)
                out[key] = (out.get(key, 0) + c1 * c2) % self.p
        return {key: c for key, c in out.items() if c}

    def times_qb(self, f: Poly) -> Poly:
        out: Poly = {}
        for key, c in f.items():
            if key[0] == 0:
                image = {(1, *key[1:]): c}
            else:
                image = self.shift({k: c * v % self.p for k, v in self.f.items()}, (0, *key[1:]))
            out = self.add(out, image)
        return out

    def times(self, f: Poly, x: str) -> Poly:
        if x == "qb":
            return self.times_qb(f)
        if x == "w2":
            return self.mul(f, {(0, 2, 0, 0, 0, 0): 1, (0, 1, 0, 0, 0, 0): self.p - 2, (0, 0, 0, 0, 0, 0): 1})
        position = {"qr": 2, "qs": 3, "qz": 4, "qa": 5}[x]
        mono: Key = tuple(1 if i == position else 0 for i in range(6))  # type: ignore[assignment]
        return self.shift(f, mono)


def _weight(key: Key) -> int:
    return key[0] + key[2] + key[3] + key[4] + key[5]


def columns(ring: Laurent, it: list[Poly]) -> Iterator[tuple[Label, Poly]]:
    """Columns in a fixed order: It_k, every box multiple of x It_k and qb x It_k, then (qu - 1) It_k.

    The (qu - 1) It_k come last, so the reduced echelon form takes one as a pivot only where the constants and the
    box multiples leave a target outside their span; (qu - 1 + qw) It_k = qw^2 qu It_k would otherwise solve every
    target with no information about I S / n I S."""
    zero: Key = (0, 0, 0, 0, 0, 0)
    for k, g in enumerate(it):
        yield ("g", k, "", 0, zero), g
    for k, g in enumerate(it):
        for x, _ in N_GENERATORS:
            base = ring.times(g, x)
            for b, f in ((0, base), (1, ring.times_qb(base))):
                if not f:
                    continue
                top = max(map(_weight, f))
                low, high = min(key[1] for key in f), max(key[1] for key in f)
                for extra in range(WEIGHT - top + 1):
                    for i, jj, kk, ll in itertools.product(range(extra + 1), repeat=4):
                        if i + jj + kk + ll != extra:
                            continue
                        for e in range(M_RANGE[0] - low, M_RANGE[1] - high + 1):
                            mono: Key = (0, e, i, jj, kk, ll)
                            yield ("d", k, x, b, mono), ring.shift(f, mono)
    inverse: Key = (0, -1, 0, 0, 0, 0)
    for k, g in enumerate(it):
        yield ("u", k, "", 0, zero), ring.add(ring.shift(g, inverse), g, -1)


def modular_run(job: tuple[str, dict[str, Any], int, int]) -> dict[str, Any]:
    """Solve the 21 box systems at (p, i -> root); returns {(j, column): residue} on the pivot columns."""
    slug, inputs, prime, root = job
    name = f"e8-closure-{slug}-p{prime}-r{root}"
    out = WORK / f"{name}.itl"
    run = _singular(laurent_script(slug, inputs, prime, root, out.name), name)
    _require(run["status"] == "completed", f"{name}: {run['status']} {run['errors']}")
    _require(run["results"]["j_nonzero"] == "0", f"{name}: J does not vanish on the parametrization")
    started = time.monotonic()
    ring = Laurent(prime)
    it = [_parse_laurent(line, prime) for line in out.read_text(encoding="utf-8").splitlines()]
    out.unlink()
    # qw It_j = (m - 1) It_j, then (qu - 1) It_j = (m^-1 - 1) It_j
    targets = [ring.add(ring.shift(g, (0, 1, 0, 0, 0, 0)), g, -1) for g in it]
    targets += [ring.add(ring.shift(g, (0, -1, 0, 0, 0, 0)), g, -1) for g in it]
    rows: dict[Key, int] = {}
    labels: list[Label] = []
    entry_rows, entry_columns, entry_values = array("l"), array("l"), array("l")
    stream = itertools.chain(
        columns(ring, it), ((("t", j, "", 0, (0, 0, 0, 0, 0, 0)), h) for j, h in enumerate(targets))
    )
    for c, (label, f) in enumerate(stream):
        labels.append(label)
        for key, value in f.items():
            entry_rows.append(rows.setdefault(key, len(rows)))
            entry_columns.append(c)
            entry_values.append(value)
    cols = labels[: len(labels) - len(targets)]
    matrix = flint.nmod_mat(len(rows), len(labels), prime)
    for r, c, value in zip(entry_rows, entry_columns, entry_values, strict=True):
        matrix[r, c] = value
    entries = len(entry_values)
    del entry_rows, entry_columns, entry_values
    # python-flint 0.9 accepts inplace; its stub omits the keyword
    reduced, rank = matrix.rref(inplace=True)  # type: ignore[call-arg]
    pivots = []
    for r in range(rank):
        c = 0
        while int(reduced[r, c]) == 0:
            c += 1
        pivots.append(c)
    _require(all(c < len(cols) for c in pivots), f"{name}: a target lies outside the box span")
    solution: dict[tuple[int, int], int] = {}
    for r, c in enumerate(pivots):
        for j in range(len(targets)):
            value = int(reduced[r, len(cols) + j])
            if value:
                solution[(j, c)] = value
    return {
        "prime": prime,
        "root": root,
        "labels": cols,
        "solution": solution,
        "rows": len(rows),
        "columns": len(cols),
        "rank": rank,
        "nonzero_entries": entries,
        "singular_seconds": run["wall_seconds"],
        "singular_peak_rss_kib": run["peak_rss_kib"],
        "linear_algebra_seconds": round(time.monotonic() - started, 1),
        "worker_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def _ratrec(value: int, modulus: int) -> Fraction | None:
    """The fraction a/b with |a|, b <= sqrt(modulus/2) and a = value b (mod modulus), or None.

    The extended Euclidean sequence yields a candidate (r1, s1) for every value; the candidate is kept only when its
    reduced form a/b has b invertible modulo `modulus` and satisfies the congruence, so a value with no such fraction
    (for example 32009 * 32029 modulo 32009 * 32029 * 32749) is None and never a spurious zero.
    """
    bound = math.isqrt(modulus // 2)
    r0, r1, s0, s1 = modulus, value % modulus, 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    if s1 == 0 or abs(s1) > bound:
        return None
    fraction = Fraction(r1, s1)
    if math.gcd(fraction.denominator, modulus) != 1:
        return None
    if (fraction.numerator - value * fraction.denominator) % modulus != 0:
        return None
    return fraction


def reconstruct(runs: dict[tuple[int, int], dict[str, Any]], primes: list[tuple[int, int]]) -> dict[Any, Any] | None:
    """Gaussian rationals {(j, column): (re, im)} from both roots of each prime, or None if a reconstruction fails."""
    keys: set[tuple[int, int]] = set()
    for prime, root in primes:
        for r in (root, prime - root):
            keys.update(runs[(prime, r)]["solution"])
    modulus, real, imag = 1, dict.fromkeys(keys, 0), dict.fromkeys(keys, 0)
    for prime, root in primes:
        plus, minus = runs[(prime, root)]["solution"], runs[(prime, prime - root)]["solution"]
        half, inverse, step = pow(2, -1, prime), pow(2 * root, -1, prime), pow(modulus, -1, prime)
        for key in keys:
            x, y = plus.get(key, 0), minus.get(key, 0)
            for table, value in ((real, (x + y) * half % prime), (imag, (x - y) * inverse % prime)):
                old = table[key]
                table[key] = old + modulus * ((value - old) * step % prime)
        modulus *= prime
    out = {}
    for key in sorted(keys):
        a, b = _ratrec(real[key], modulus), _ratrec(imag[key], modulus)
        if a is None or b is None:
            return None
        if a or b:
            out[key] = (a, b)
    return out


def _number(a: Fraction, b: Fraction) -> str:
    return f"({a}+({b})*I)"


def _multiplier(label: list[Any]) -> str:
    _, _, x, b, (_, e, i, jj, kk, ll) = label
    factors = [f"(1+qw)^{e}" if e > 0 else (f"qu^{-e}" if e < 0 else "")]
    factors += [f"{name}^{p}" for name, p in zip(("qr", "qs", "qz", "qa"), (i, jj, kk, ll), strict=True) if p]
    factors += ["qb"] * b + [dict(N_GENERATORS)[x]]
    return "*".join(f for f in factors if f)


def verify_script(slug: str, inputs: dict[str, Any], cofactors: dict[str, Any], mutate: str | None = None) -> str:
    """The exact check over Q(i); mutate is None, 'cofactor' or 'generator'."""
    data = dict(inputs)
    if mutate == "generator":
        # add the first term of G_1 once more: one coefficient of one generator changes
        first = data["G"][0]
        sign, body = TERM.findall(first)[0]
        data = {**data, "G": [f"({first})+({sign}{body})", *data["G"][1:]]}
    lines = _setup(slug, data, None, None) + ["int bad=0; poly s; poly q;"]
    labels = cofactors["labels"]
    for j, entries in enumerate(cofactors["targets"]):
        if mutate == "cofactor" and j == 0:
            column, a, b = entries[-1]
            entries = [*entries[:-1], [column, str(Fraction(a) + 1), b]]
        grouped: dict[int, list[str]] = {}
        for column, a, b in entries:
            kind, k = labels[column][0], labels[column][1]
            coefficient = _number(Fraction(a), Fraction(b))
            if kind == "g":
                term = coefficient
            elif kind == "u":
                term = f"{coefficient}*(qu-1)"
            else:
                term = f"{coefficient}*{_multiplier(labels[column])}"
            grouped.setdefault(k, []).append(term)
        n = len(cofactors["targets"]) // 2
        lines.append(f"s=qw*It[{j + 1}];" if j < n else f"s=(qu-1)*It[{j - n + 1}];")
        for k, terms in sorted(grouped.items()):
            lines.append(f"q={'+'.join(terms)}; s=s-q*It[{k + 1}];")
        lines.append(f'if(reduce(s,std(0))!=0){{ bad++; "RESULT failed_target_{j + 1}"; }}')
    lines += ['"RESULT bad_identities",bad; "STAGE verified",rtimer;', "quit;"]
    return "\n".join(lines) + "\n"


def nakayama_rank(cofactors: dict[str, Any], n: int) -> dict[str, int]:
    """Rank over Q(i) of the qw-parts of the 2n relations in I S / n I S.

    Target t has the identity t = sum_k alpha_k It_k + sum_k beta_k (qu - 1) It_k modulo n I S, and qu - 1 = -qw
    modulo n, so [t] + sum_k beta_k [qw It_k] lies in the span of the [It_k]. [t] is [qw It_j] for the first n targets
    and -[qw It_j] for the last n. Rank n of the rows (+-e_j + beta) puts every [qw It_k] in the span of the [It_k].
    """
    labels = cofactors["labels"]
    rows = sympy.zeros(2 * n, n)
    for t, entries in enumerate(cofactors["targets"]):
        rows[t, t % n] = 1 if t < n else -1
        for column, a, b in entries:
            if labels[column][0] == "u":
                rows[t, labels[column][1]] += sympy.Rational(a) + sympy.Rational(b) * sympy.I
    return {"qw_relation_rank": int(rows.rank()), "size": n}


def verdict(row: dict[str, Any]) -> str:
    """`i_equals_is` when every premise of the closure holds in the parsed result fields of ROW, else `failed`.

    The premises: J vanishes in S, S / n has colength 2, m_R S and n contain each other, every cofactor identity
    reduces to zero, and the 2n relations in I S / n I S have rank n (the number of generators).
    """
    closed = (
        row["j_nonzero"] == 0
        and row["colength_of_n"] == 2
        and row["am_outside_n"] == 0
        and row["n_outside_am"] == 0
        and row["bad_identities"] == 0
        and row["qw_relation_rank"] == row["generators"]
    )
    return "i_equals_is" if closed else "failed"


def mutation_detected(row: dict[str, Any]) -> bool:
    """True when the mutated check ran to completion, counted a failed cofactor identity and gave no closure verdict."""
    return (
        row.get("status") == "completed"
        and (row.get("bad_identities") or 0) > 0
        and row.get("verdict") != "i_equals_is"
    )


def verify(slug: str, inputs: dict[str, Any], cofactors: dict[str, Any], mutate: str | None = None) -> dict[str, Any]:
    tag = f"e8-closure-verify-{slug}" + (f"-mutate-{mutate}" if mutate else "")
    run = _singular(verify_script(slug, inputs, cofactors, mutate), tag)
    res = run["results"]
    row: dict[str, Any] = {
        "status": run["status"],
        "wall_seconds": run["wall_seconds"],
        "peak_rss_kib": run["peak_rss_kib"],
    }
    if run["status"] != "completed":
        row.update({"errors": run["errors"], "verdict": "failed"})
        return row
    n = int(res["generators"])
    row.update(
        {
            "j_nonzero": int(res["j_nonzero"]),
            "generators": n,
            "colength_of_n": int(res["colength"]),
            "kbase_of_s_mod_n": res["kbase"],
            "am_outside_n": int(res["am_outside_n"]),
            "n_outside_am": int(res["n_outside_am"]),
            "bad_identities": int(res["bad_identities"]),
            **nakayama_rank(cofactors, n),
        }
    )
    row["verdict"] = verdict(row)
    return row


def _record_path(slug: str) -> Path:
    return HERE / f"e8-closure-certificate-{slug}.json"


def _cofactor_path(slug: str) -> Path:
    return COFACTORS / f"e8-closure-{slug}.json.xz"


def _stats(cofactors: dict[str, Any]) -> dict[str, Any]:
    values = [Fraction(x) for entries in cofactors["targets"] for _, a, b in entries for x in (a, b)]
    return {
        "cofactor_terms": sum(len(entries) for entries in cofactors["targets"]),
        "max_numerator_digits": len(str(max(abs(v.numerator) for v in values))),
        "max_denominator_digits": len(str(max(v.denominator for v in values))),
    }


def write(
    slug: str, workers: int = DEFAULT_WORKERS, memory_budget_gib: int = DEFAULT_MEMORY_BUDGET_GIB
) -> dict[str, Any]:
    with _execution_scope(workers, memory_budget_gib) as execution:
        return _write(slug, execution)


def _write(slug: str, execution: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    inputs = producer(slug)
    runs: dict[tuple[int, int], dict[str, Any]] = {}
    used: list[tuple[int, int]] = []
    solution = previous = None
    for start in range(0, len(PRIMES), 2):
        batch = list(PRIMES[start : start + 2])
        jobs = [(slug, inputs, p, r) for p, root in batch for r in (root, p - root)]
        for result in parallel.ordered_map(modular_run, jobs, min_items=2):
            runs[(result["prime"], result["root"])] = result
        for prime, root in batch:
            for r in (root, prime - root):
                _require(
                    runs[(prime, r)]["labels"] == runs[PRIMES[0]]["labels"], f"{slug}: column set differs at {prime}"
                )
            used.append((prime, root))
            current = reconstruct(runs, used)
            if len(used) >= MIN_PRIMES and current is not None and current == previous:
                solution = current
                break
            previous = current
        if solution is not None:
            break
    if solution is None:
        raise SystemExit(f"{slug}: reconstruction did not stabilize over {len(used)} primes")
    first = runs[PRIMES[0]]
    n = len(inputs["G"])
    targets: list[list[list[Any]]] = [[] for _ in range(2 * n)]
    for (j, column), (a, b) in sorted(solution.items()):
        targets[j].append([column, str(a), str(b)])
    cofactors = {
        "schema": "a5-e8-closure-cofactors-v1",
        "slug": slug,
        "box": {"weight": WEIGHT, "m_range": list(M_RANGE)},
        "labels": [list(label) for label in first["labels"]],
        "targets": targets,
    }
    COFACTORS.mkdir(exist_ok=True)
    blob = json.dumps(cofactors, sort_keys=True, separators=(",", ":")).encode("utf-8")
    _cofactor_path(slug).write_bytes(lzma.compress(blob, preset=9))
    cofactors = json.loads(blob)
    exact = verify(slug, inputs, cofactors)
    record = {
        "schema": "a5-e8-closure-certificate-v1",
        "slug": slug,
        "field": "Q(i), minpoly I^2+1; exact check in Singular 4.4.1, global ordering dp",
        "statement": "for j = 1..21: qw It_j = sum_k (alpha_jk + beta_jk (qu - 1)) It_k + sum_(x,k) D_jxk x It_k in S, "
        "x in n = (qa, qz, qr, qs, qb, qw^2) = m_R S, and Id + beta has rank 21; hence I = I S by Nakayama",
        "primes": [{"prime": p, "root": r, "roots_used": [r, p - r]} for p, r in used],
        "reconstruction": "CRT of real and imaginary parts, rational reconstruction, stable over two prime sets",
        "execution": execution,
        "box": cofactors["box"],
        "counts": {
            "generators": n,
            "targets": 2 * n,
            "rows": first["rows"],
            "columns": first["columns"],
            "rank_mod_p": first["rank"],
            "nonzero_matrix_entries": first["nonzero_entries"],
            **_stats(cofactors),
        },
        "sha256": {
            "producer_script": inputs["script_sha256"],
            "header_j_and_g": _input_digest(inputs),
            "certificate_producer": _sha256_file(Path(__file__)),
            "slice_rings_qi": _sha256_file(HERE / "slice_rings_qi.py"),
            "reduction_check": _sha256_file(HERE / "reduction_check.py"),
            "cofactor_file": _sha256_file(_cofactor_path(slug)),
        },
        "inputs": {"J": inputs["J"], "G": inputs["G"]},
        "stages": {
            "producer": {k: inputs[k] for k in ("wall_seconds", "peak_rss_kib")},
            "modular": [
                {
                    k: run[k]
                    for k in (
                        "prime",
                        "root",
                        "rows",
                        "columns",
                        "rank",
                        "singular_seconds",
                        "singular_peak_rss_kib",
                        "linear_algebra_seconds",
                        "worker_peak_rss_kib",
                    )
                }
                for run in runs.values()
            ],
            "verification": exact,
        },
        "verdict": exact["verdict"],
        "wall_seconds": round(time.monotonic() - started, 1),
    }
    _record_path(slug).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return record


def check(slug: str) -> dict[str, Any]:
    record = json.loads(_record_path(slug).read_text(encoding="utf-8"))
    digests = record["sha256"]
    for key, name in (
        ("certificate_producer", Path(__file__).name),
        ("slice_rings_qi", "slice_rings_qi.py"),
        ("reduction_check", "reduction_check.py"),
    ):
        _require(
            _sha256_file(HERE / name) == digests[key],
            f"{slug}: {name} differs from the digest in {_record_path(slug).name}; regenerate the record with --write",
        )
    _require(_sha256_file(_cofactor_path(slug)) == digests["cofactor_file"], f"{slug}: cofactor file digest")
    with _check_workspace(slug):
        inputs = producer(slug)
        _require(inputs["script_sha256"] == digests["producer_script"], f"{slug}: producer script changed")
        _require(_input_digest(inputs) == digests["header_j_and_g"], f"{slug}: producer J or G changed")
        cofactors = json.loads(lzma.decompress(_cofactor_path(slug).read_bytes()))
        exact = verify(slug, inputs, cofactors)
        _require(exact["verdict"] == "i_equals_is", f"{slug}: exact check {exact}")
        mutations = {}
        for kind in ("cofactor", "generator"):
            row = verify(slug, inputs, cofactors, kind)
            mutations[kind] = {k: row.get(k) for k in ("status", "bad_identities", "verdict")}
            _require(mutation_detected(row), f"{slug}: mutation {kind} was not detected: {row}")
    return {"slug": slug, "verdict": exact["verdict"], "mutations": mutations, "wall_seconds": exact["wall_seconds"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--slug", choices=sorted(SIGN), action="append")
    parser.add_argument(
        "--workers",
        type=int,
        choices=range(1, 5),
        default=DEFAULT_WORKERS,
        help="process cap, default two; a larger cap requires a sufficient declared memory budget",
    )
    parser.add_argument(
        "--memory-budget-gib",
        type=int,
        default=DEFAULT_MEMORY_BUDGET_GIB,
        help="resident-memory planning budget; admits workers without imposing a system memory limit",
    )
    args = parser.parse_args()
    try:
        _execution_settings(args.workers, args.memory_budget_gib)
    except ValueError as error:
        parser.error(str(error))
    slugs = args.slug or sorted(SIGN)
    # `write` pools its modular solves itself; the checks of the two signs share no file and run as pooled items.
    with _execution_scope(args.workers, args.memory_budget_gib):
        rows = (
            (write(slug, args.workers, args.memory_budget_gib) for slug in slugs)
            if args.write
            else parallel.ordered_map(check, slugs, min_items=2)
        )
        for slug, row in zip(slugs, rows, strict=True):
            print(
                json.dumps(
                    {
                        key: row[key]
                        for key in row
                        if key in ("slug", "verdict", "mutations", "wall_seconds", "execution")
                    }
                )
            )
            if row["verdict"] != "i_equals_is":
                raise SystemExit(f"{slug}: {row['verdict']}")


if __name__ == "__main__":
    main()
