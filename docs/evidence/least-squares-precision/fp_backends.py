"""Precision and speed of least-squares backends on the ensemble's tomography prediction (501 right-hand sides).

Every backend solves min ||A x - b|| for the point rates and the 500 bootstrap replicates, maps x to the 32 predicted
outcome rates, and scores F, F' and the process fidelity; arb at 256 bits (python-flint) is the reference, with a
rigorous radius. Inputs are the producer's float64 values from fp-inputs.npz (fp_export.py), held fixed.

usage: python docs/local/fp_backends.py docs/local/fp-inputs.npz OUT.json [--mpmath]
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

PREC = 256
WORKERS = int(os.environ.get("FP_WORKERS", str(os.cpu_count() or 1)))
REFINE_STEPS = int(os.environ.get("FP_REFINE_STEPS", "2"))
QUAD_THREADS = int(os.environ.get("FP_QUAD_THREADS", "1"))
QUAD_BACKEND = os.environ.get("FP_QUAD_BACKEND", "sleef")
ARB_PREC = int(os.environ.get("FP_ARB_PREC", "128"))
FLINT_THREADS = int(os.environ.get("FP_FLINT_THREADS", "1"))
LSTSQ_DRIVER = os.environ.get("FP_LSTSQ_DRIVER", "gelsd")
REFERENCE_X: list = []  # the arb solution, for the mpmath certificate
SOLVE: dict[str, float] = {}  # solve-only seconds per backend, scoring excluded


def load(path: str) -> dict:
    data = np.load(path)
    return {k: data[k] for k in data.files}


def a_mat(m) -> arb_mat:
    return arb_mat([[arb(float(v)) for v in row] for row in np.asarray(m, dtype=np.float64)])


def mm(left, right):
    """left @ right on contiguous copies: numpy-quaddtype 1.0.0's QBLAS matmul ignores the strides of a view and
    returns wrong products, and an empty inner dimension raises "QBLAS operation failed" where NumPy returns zeros
    (quad_view_matmul.py); every product here goes through contiguous operands and the empty case returns zeros."""
    left, right = np.ascontiguousarray(left), np.ascontiguousarray(right)
    if left.shape[-1] == 0:
        shape = left.shape[:-1] + right.shape[1:] if right.ndim > 1 else left.shape[:-1]
        return np.zeros(shape, dtype=left.dtype)
    try:
        return left @ right
    except NotImplementedError:
        # QBLAS matmul serves only the SLEEF backend; the longdouble backend multiplies and sums elementwise
        if right.ndim == 1:
            return (left * right).sum(axis=-1)
        return (left[..., :, None] * right[None, :, :] if left.ndim == 2 else left[:, None] * right).sum(axis=-2)


# ------------------------------------------------------------------ scoring, generic over the element type


def tables(d: dict) -> list[tuple[str, list[int], list[int]]]:
    """(table, row indices of its four inputs' first outcome, correct outcome per input)."""
    out = []
    for t, table in enumerate(d["tables"]):
        inputs = list(range(4 * t, 4 * t + 4))
        out.append((str(table), [4 * i for i in inputs], [int(d["correct"][i]) for i in inputs]))
    return out


def scores(rates, d: dict, zero) -> dict:
    """F and F' per table from 32 rates (any element type supporting + and /)."""
    out = {}
    for table, starts, correct in tables(d):
        c = [rates[s + k] for s, k in zip(starts, correct, strict=True)]
        e = [rates[s] + rates[s + 1] + rates[s + 2] + rates[s + 3] for s in starts]
        out[f"{table}/F"] = sum(c, zero) / sum(e, zero)
        out[f"{table}/F_prime"] = sum((ci / ei for ci, ei in zip(c, e, strict=True)), zero) / 4
    return out


def summary(values: list, sqrt, zero) -> dict:
    """Sample sd (ddof 1) and numpy's linear 2.5 / 97.5 percentiles, in the values' own type."""
    vals = sorted(values, key=float)
    n = len(vals)
    mean = sum(vals, zero) / n
    sd = sqrt(sum(((v - mean) * (v - mean) for v in vals), zero) / (n - 1))

    def pct(q: float):
        h = q / 100 * (n - 1)
        lo = int(math.floor(h))
        return vals[lo] + (vals[lo + 1] - vals[lo]) * (h - lo)

    return {"F_sd": sd, "p2.5": pct(2.5), "p97.5": pct(97.5)}


def evaluate(x_cols, r, functional, d: dict, zero, sqrt, to_list) -> dict:
    """Point quantities from column 0 and bootstrap summaries from columns 1..500 of x (256 x 501)."""
    rates = mm(r, x_cols)
    fun = mm(functional, x_cols[:, :1])
    point_rates = to_list(rates[:, 0])
    out = {"rates": point_rates, **scores(point_rates, d, zero)}
    out["process_fidelity"] = fun[0, 0] / (4 * fun[1, 0])
    for table, *_ in tables(d):
        reps = [scores(to_list(rates[:, k]), d, zero)[f"{table}/F"] for k in range(1, rates.shape[1])]
        for key, value in summary(reps, sqrt, zero).items():
            out[f"{table}/{key}"] = value
    return out


def model_rows(d: dict, dtype) -> tuple:
    """Rate matrix R = Re(O H^T) and the fidelity functionals, built in the backend's own arithmetic."""
    o = d["obs"].reshape(len(d["obs"]), -1)
    h = np.transpose(d["basis"], (0, 2, 1)).reshape(len(d["basis"]), -1)
    cast = (lambda m: np.asarray(m, dtype=np.float64).astype(dtype)) if dtype is not None else np.asarray
    r = mm(cast(o.real), cast(h.real).T) - mm(cast(o.imag), cast(h.imag).T)
    v = d["v"]
    weights = np.vstack([np.outer(v, v).reshape(-1), np.eye(16).reshape(-1)])
    functional = mm(cast(weights), cast(d["basis"].real.reshape(len(d["basis"]), -1)).T)
    return r, functional


# ------------------------------------------------------------------ backends


def rhs(d: dict) -> np.ndarray:
    return np.column_stack([d["f"], d["batch"].T])  # 576 x 501


def float64_pinv(d: dict):
    t0 = time.perf_counter()
    p = np.linalg.pinv(d["a"])
    b = rhs(d)
    x = np.column_stack([p @ b[:, k] for k in range(b.shape[1])])  # matvec per column, the producer's order
    SOLVE["float64 pinv (producer)"] = time.perf_counter() - t0
    r, fn = model_rows(d, None)
    return evaluate(x, r, fn, d, 0.0, math.sqrt, lambda c: [float(v) for v in c])


def float64_qr(d: dict):
    t0 = time.perf_counter()
    x = np.linalg.lstsq(d["a"], rhs(d), rcond=None)[0]
    SOLVE["float64 QR lstsq"] = time.perf_counter() - t0
    r, fn = model_rows(d, None)
    return evaluate(x, r, fn, d, 0.0, math.sqrt, lambda c: [float(v) for v in c])


def float64_x87_refined(d: dict):
    """float64 pinv solve plus one refinement step whose residual and update run in x87 80-bit."""
    ld = np.longdouble
    t0 = time.perf_counter()
    p = np.linalg.pinv(d["a"])
    b = rhs(d)
    x = (p @ b).astype(ld)
    for _ in range(REFINE_STEPS):
        residual = b.astype(ld) - d["a"].astype(ld) @ x
        x = x + (p @ residual.astype(np.float64)).astype(ld)
    SOLVE["float64 + x87 refinement"] = time.perf_counter() - t0
    r, fn = model_rows(d, ld)
    return evaluate(x, r, fn, d, ld(0), np.sqrt, list)


def householder_factor(a: np.ndarray, zero):
    """Householder vectors and R of A (m x n) in the array's own dtype."""
    r = a.copy()
    m, n = r.shape
    vs, betas = [], []
    for j in range(n):
        col = r[j:, j]
        norm = np.sqrt(np.sum(col * col))
        alpha = -norm if col[0] >= zero else norm
        v = col.copy()
        v[0] = v[0] - alpha
        beta = 2 / np.sum(v * v)
        r[j:, j:] = r[j:, j:] - np.outer(v, beta * mm(v, r[j:, j:]))
        vs.append(v)
        betas.append(beta)
    return vs, betas, r[:n, :n]


def householder_apply(args):
    """Solve the least-squares columns of one RHS block with a precomputed factorization."""
    vs, betas, r, block = args
    b = block.copy()
    for j, (v, beta) in enumerate(zip(vs, betas, strict=True)):
        b[j:] = b[j:] - np.outer(v, beta * mm(v, b[j:]))
    n = r.shape[0]
    x = np.empty((n, b.shape[1]), dtype=b.dtype)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - mm(r[i, i + 1 :], x[i + 1 :])) / r[i, i]
    return x


def householder(d: dict, dtype, zero, sqrt, workers: int, name: str):
    t0 = time.perf_counter()
    a = d["a"].astype(dtype)
    vs, betas, r_fac = householder_factor(a, zero)
    b = rhs(d).astype(dtype)
    blocks = np.array_split(np.arange(b.shape[1]), max(1, workers))
    jobs = [(vs, betas, r_fac, b[:, idx]) for idx in blocks if len(idx)]
    if workers > 1:
        with ProcessPoolExecutor(workers) as pool:
            x = np.concatenate(list(pool.map(householder_apply, jobs)), axis=1)
    else:
        x = np.concatenate([householder_apply(j) for j in jobs], axis=1)
    SOLVE[name] = time.perf_counter() - t0
    r, fn = model_rows(d, dtype)
    return evaluate(x, r, fn, d, zero, sqrt, list)


def x87_householder(d: dict):
    ld = np.longdouble
    return householder(d, ld, ld(0), np.sqrt, WORKERS, "x87 80-bit Householder")


def quad_householder(d: dict):
    import numpy_quaddtype as nq
    from numpy_quaddtype import QuadPrecDType, QuadPrecision

    nq.set_num_threads(QUAD_THREADS)
    q = QuadPrecDType(backend=QUAD_BACKEND)
    return householder(d, q, QuadPrecision(0, backend=QUAD_BACKEND), np.sqrt, 1, "binary128 quaddtype Householder")


def cholesky_solve(gram, right, zero, sqrt):
    """Solve gram x = right (gram symmetric positive definite) by a right-looking Cholesky in gram's dtype."""
    n = gram.shape[0]
    low = gram.copy()
    for j in range(n):
        low[j, j] = sqrt(low[j, j])
        low[j + 1 :, j] = low[j + 1 :, j] / low[j, j]
        low[j + 1 :, j + 1 :] = low[j + 1 :, j + 1 :] - np.outer(low[j + 1 :, j], low[j + 1 :, j])
    y = right.copy()
    for i in range(n):
        y[i] = (y[i] - mm(low[i, :i], y[:i])) / low[i, i]
    x = y.copy()
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - mm(low[i + 1 :, i], x[i + 1 :])) / low[i, i]
    return x


def normal_equations(d: dict, dtype, zero, sqrt, name: str):
    t0 = time.perf_counter()
    a = d["a"].astype(dtype)
    at = np.ascontiguousarray(a.T)
    x = cholesky_solve(mm(at, a), mm(at, rhs(d).astype(dtype)), zero, sqrt)
    SOLVE[name] = time.perf_counter() - t0
    r, fn = model_rows(d, dtype)
    return evaluate(x, r, fn, d, zero, sqrt, list)


def x87_normal(d: dict):
    ld = np.longdouble
    return normal_equations(d, ld, ld(0), np.sqrt, "x87 80-bit normal equations (Cholesky)")


def quad_normal(d: dict):
    import numpy_quaddtype as nq
    from numpy_quaddtype import QuadPrecDType, QuadPrecision

    nq.set_num_threads(QUAD_THREADS)
    return normal_equations(
        d,
        QuadPrecDType(backend=QUAD_BACKEND),
        QuadPrecision(0, backend=QUAD_BACKEND),
        np.sqrt,
        "binary128 normal equations (Cholesky)",
    )


def float64_scipy(d: dict):
    import scipy.linalg

    t0 = time.perf_counter()
    x = scipy.linalg.lstsq(d["a"], rhs(d), lapack_driver=LSTSQ_DRIVER)[0]
    SOLVE["float64 scipy lstsq"] = time.perf_counter() - t0
    r, fn = model_rows(d, None)
    return evaluate(x, r, fn, d, 0.0, math.sqrt, lambda c: [float(v) for v in c])


def arb_candidate(d: dict):
    """arb normal equations at ARB_PREC bits with FLINT_THREADS threads, scored against the 256-bit reference."""
    ctx.prec, ctx.threads = ARB_PREC, FLINT_THREADS
    t0 = time.perf_counter()
    a = a_mat(d["a"])
    at = a.transpose()
    x = (at * a).solve(at * a_mat(rhs(d)))
    SOLVE["arb normal equations"] = time.perf_counter() - t0
    out = arb_from_x(d, x)
    ctx.prec, ctx.threads = PREC, 1
    return out


def arb_reference(d: dict):
    ctx.prec = PREC
    t0 = time.perf_counter()
    a = a_mat(d["a"])
    at = a.transpose()
    x = (at * a).solve(at * a_mat(rhs(d)))
    SOLVE["reference"] = time.perf_counter() - t0
    REFERENCE_X.append(x)
    return arb_from_x(d, x)


def arb_from_x(d: dict, x: arb_mat) -> dict:
    """Rates, scores and bootstrap summaries of an arb solution matrix x (256 x 577)."""
    o = d["obs"].reshape(len(d["obs"]), -1)
    h = np.transpose(d["basis"], (0, 2, 1)).reshape(len(d["basis"]), -1)
    r = a_mat(o.real) * a_mat(h.real).transpose() - a_mat(o.imag) * a_mat(h.imag).transpose()
    v = d["v"]
    weights = np.vstack([np.outer(v, v).reshape(-1), np.eye(16).reshape(-1)])
    fn = a_mat(weights) * a_mat(d["basis"].real.reshape(len(d["basis"]), -1)).transpose()
    rates, fun = r * x, fn * x
    col = lambda k: [rates[i, k] for i in range(rates.nrows())]  # noqa: E731
    out = {"rates": col(0), **scores(col(0), d, arb(0))}
    out["process_fidelity"] = fun[0, 0] / (4 * fun[1, 0])
    for table, *_ in tables(d):
        reps = [scores(col(k), d, arb(0))[f"{table}/F"] for k in range(1, x.ncols())]
        for key, value in summary(reps, lambda z: z.sqrt(), arb(0)).items():
            out[f"{table}/{key}"] = value
    return out


def flint_arb_package(d: dict, prec: int = 128):
    """Excluded from main(): numpy-flint-arb 1.5.4 maps matmul element by element over object arrays, and its peak
    memory grows about tenfold per doubling of the matrix side (1.1 GiB at 96 x 48; nfa_scaling.py), so the 576 x 256
    design exhausts memory.
    numpy-flint-arb's array API (matmul, linalg.solve) on the normal equations at prec bits."""
    from numpy_flint_arb import allow_input
    from numpy_flint_arb import np as xp

    ctx.prec = prec
    t0 = time.perf_counter()
    with allow_input(interval=True, float=True):
        a = xp.asarray(d["a"])
        b = xp.asarray(rhs(d))
    at = xp.linalg.matrix_transpose(a)
    x = xp.linalg.solve(xp.linalg.matmul(at, a), xp.linalg.matmul(at, b))
    SOLVE["numpy-flint-arb 128-bit normal equations"] = time.perf_counter() - t0
    rows = np.asarray(x)
    out = arb_from_x(d, arb_mat([[arb(v) for v in row] for row in rows]))
    ctx.prec = PREC
    return out


def mpmath_certificate(d: dict, x: arb_mat, columns: int = 4, dps: int = 80) -> dict:
    """Independent mpmath check of the arb solution: the normal-equation gradient g = A^T (A x - b) of its midpoints at
    dps digits. For full column rank, ||x - x*||_2 <= ||g||_2 / sigma_min(A)^2."""
    import mpmath as mp

    mp.mp.dps = dps
    a = d["a"]
    b = rhs(d)
    sigma_min = float(np.linalg.svd(a, compute_uv=False)[-1])
    worst_g, worst_bound = mp.mpf(0), mp.mpf(0)
    for k in range(min(columns, x.ncols())):
        xs = [mp.mpf(x[i, k].mid().str(dps, radius=False)) for i in range(x.nrows())]
        resid = [
            mp.fsum(mp.mpf(float(a[r, c])) * xs[c] for c in range(a.shape[1])) - mp.mpf(float(b[r, k]))
            for r in range(a.shape[0])
        ]
        g = [mp.fsum(mp.mpf(float(a[r, c])) * resid[r] for r in range(a.shape[0])) for c in range(a.shape[1])]
        norm = mp.sqrt(mp.fsum(v * v for v in g))
        worst_g = max(worst_g, norm)
        worst_bound = max(worst_bound, norm / mp.mpf(sigma_min) ** 2)
    return {
        "columns_checked": min(columns, x.ncols()),
        "dps": dps,
        "max_gradient_norm": mp.nstr(worst_g, 5),
        "max_solution_error_bound": mp.nstr(worst_bound, 5),
        "sigma_min": sigma_min,
    }


# ------------------------------------------------------------------ comparison


def as_arb(value) -> arb:
    """Exact arb of a float, longdouble or quad value by splitting it into float64 parts."""
    if isinstance(value, arb):
        return value
    parts, rest = [], value
    for _ in range(3):
        head = float(rest)
        parts.append(head)
        rest = rest - head if not isinstance(rest, float) else 0.0  # a Python float keeps the quad value's backend
        if not isinstance(rest, float) and float(rest) == 0.0:
            break
    return sum((arb(p) for p in parts), arb(0))


def compare(result: dict, reference: dict) -> dict:
    out = {"max_rate_abs_error": 0.0}
    for value, exact in zip(result["rates"], reference["rates"], strict=True):
        out["max_rate_abs_error"] = max(out["max_rate_abs_error"], abs(float((as_arb(value) - exact).mid())))
    worst = 0.0
    for key, exact in reference.items():
        if key == "rates":
            continue
        err = abs(float((as_arb(result[key]) - exact).mid())) / math.ulp(float(exact.mid()))
        out[f"{key}_ulp64"] = err
        worst = max(worst, err / 1.0)
    out["max_score_error_ulp64"] = worst
    out["bits_correct_on_scores"] = 52 - math.log2(worst) if worst > 0 else ">=106"
    return out


def main() -> int:
    inputs, out_path = sys.argv[1], Path(sys.argv[2])
    d = load(inputs)
    args = sys.argv[3:]
    if "--replicates" in args:
        d["batch"] = d["batch"][: int(args[args.index("--replicates") + 1])]
    chosen = args[args.index("--backends") + 1].split(",") if "--backends" in args else None
    report: dict = {
        "knobs": {
            "workers": WORKERS,
            "refine_steps": REFINE_STEPS,
            "quad_threads": QUAD_THREADS,
            "quad_backend": QUAD_BACKEND,
            "arb_prec": ARB_PREC,
            "flint_threads": FLINT_THREADS,
            "lstsq_driver": LSTSQ_DRIVER,
            "openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
        },
        "workers": WORKERS,
        "longdouble": {"nmant": int(np.finfo(np.longdouble).nmant)},
        "backends": {},
    }
    t0 = time.perf_counter()
    reference = arb_reference(d)
    report["reference"] = {
        "backend": f"arb {PREC}-bit normal equations",
        "seconds": time.perf_counter() - t0,
        "solve_seconds": SOLVE["reference"],
        "max_radius": max(float(v.rad()) for k, v in reference.items() if k != "rates"),
    }
    for name, fn in (
        ("float64 pinv (producer)", float64_pinv),
        ("float64 QR lstsq", float64_qr),
        ("float64 + x87 refinement", float64_x87_refined),
        ("x87 80-bit Householder", x87_householder),
        ("binary128 quaddtype Householder", quad_householder),
        ("x87 80-bit normal equations (Cholesky)", x87_normal),
        ("binary128 normal equations (Cholesky)", quad_normal),
        ("float64 scipy lstsq", float64_scipy),
        ("arb normal equations", arb_candidate),
    ):
        if chosen is not None and not any(c in name for c in chosen):
            continue
        t0 = time.perf_counter()
        try:
            result = fn(d)
        except Exception as exc:  # report a missing or failing backend rather than abort the study
            report["backends"][name] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        report["backends"][name] = {
            "seconds": time.perf_counter() - t0,
            "solve_seconds": SOLVE.get(name),
            **compare(result, reference),
        }
        print(
            name,
            json.dumps({k: v for k, v in report["backends"][name].items() if not k.endswith("_ulp64")}),
            flush=True,
        )
    if "--mpmath" in args:
        t0 = time.perf_counter()
        report["mpmath_certificate"] = {**mpmath_certificate(d, REFERENCE_X[0]), "seconds": time.perf_counter() - t0}
        print("mpmath certificate", json.dumps(report["mpmath_certificate"]), flush=True)
    report["replicates"] = int(d["batch"].shape[0])
    out_path.write_text(json.dumps(report, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
