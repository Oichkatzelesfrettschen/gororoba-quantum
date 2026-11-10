"""Probe: reduced row echelon form over F_p on the GPU from the PLUQ probe, against flint.nmod_mat.rref.

RREF of a row space is unique, so R = U1^{-1} U (U the echelon rows of the PLUQ factor, U1 = U[:, pivcols]) equals
flint's rref rows exactly when both are right. Seed: ANU QRNG draw-2026-11-08T170257Z index 1001 (36574).
Usage: python rref_probe.py PLUQ_DIR p rows cols rank [rows cols rank ...]
"""

import importlib
import sys
import time
from typing import Any

import flint
import numpy as np

# torch and CuPy load at run time, as in gororoba_quantum/modular_echelon.py, so a type check of this file
# does not walk the GPU packages of the host interpreter.
cp: Any = importlib.import_module("cupy")
torch: Any = importlib.import_module("torch")

sys.path.insert(0, sys.argv[1])
from pluq import Pluq  # noqa: E402

SEED = 36574


def inv_mod(x: int, p: int) -> int:
    return pow(int(x), p - 2, p)


def gpu_rref(a: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    t = {}
    t0 = time.time()
    f = Pluq(a, p)
    r = f.factor()
    torch.cuda.synchronize()
    t["pluq"] = time.time() - t0
    t0 = time.time()
    _, u, pc = f.extract()
    n = a.shape[1]
    if r == 0:
        return np.zeros((0, n), dtype=np.int64), np.zeros(0, dtype=np.int64), t
    u = u[:, :n].to(torch.int64)
    piv = pc.cpu().numpy()
    if np.any(np.diff(piv) <= 0):
        raise RuntimeError("pivot columns not increasing")
    d = u[torch.arange(r, device="cuda"), pc].cpu().numpy()
    dinv = torch.as_tensor([inv_mod(x, p) for x in d], device="cuda", dtype=torch.int64)
    R = torch.remainder(u * dinv[:, None], p).to(torch.int32).contiguous()
    Rc = cp.from_dlpack(R)
    pcc = pc.long()

    def solve(lo: int, hi: int) -> None:
        # rows lo..hi-1 of R hold unit-upper rows; clear their entries in pivot columns lo..hi-1 above the diagonal
        if hi - lo <= 1:
            return
        mid = lo + (hi - lo) // 2
        solve(mid, hi)
        coef = R[lo:mid].index_select(1, pcc[mid:hi]).contiguous()
        f.mm(cp.from_dlpack(coef), Rc[mid:hi], Rc[lo:mid], 1)
        solve(lo, mid)

    sys.setrecursionlimit(10000)
    solve(0, r)
    torch.cuda.synchronize()
    t["backsub"] = time.time() - t0
    return R.cpu().numpy().astype(np.int64), piv.astype(np.int64), t


def main() -> None:
    p = int(sys.argv[2])  # argv[1], the PLUQ directory, is on sys.path at import
    shapes = [tuple(int(x) for x in sys.argv[i : i + 3]) for i in range(3, len(sys.argv), 3)]
    rng = np.random.default_rng(SEED)
    for m, n, k in shapes:
        if k * (p - 1) ** 2 >= 2**63:
            raise SystemExit(f"inner dimension {k} overflows int64 products at p = {p}")
        x = rng.integers(0, p, (m, k), dtype=np.int64)
        y = rng.integers(0, p, (k, n), dtype=np.int64)
        y[:, rng.choice(n, n // 3, replace=False)] = 0  # zero columns, as in closure rows
        a = np.zeros((m, n), dtype=np.int64)
        for s in range(0, m, 512):
            a[s : s + 512] = (x[s : s + 512] @ y) % p
        Rg, pg, t = gpu_rref(a.astype(np.int32), p)
        t0 = time.time()
        M = flint.nmod_mat(m, n, a.ravel().tolist(), p)
        F, rk = M.rref()
        Fn = np.array([int(v) for v in F.entries()], dtype=np.int64).reshape(m, n)[:rk]
        tf = time.time() - t0
        pf = np.argmax(Fn != 0, axis=1)
        same = rk == len(pg) and np.array_equal(pf, pg) and np.array_equal(Fn, Rg)
        print(f"p={p} {m}x{n} rank={rk} gpu_rank={len(pg)} equal={same} gpu={t} flint={tf:.2f}s", flush=True)
        if not same:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
