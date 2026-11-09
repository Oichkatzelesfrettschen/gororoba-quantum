"""Exact PLUQ / rank over F_p (p < 2^15) on the GPU: fused base-case kernel, INT8 tensor-core Schur updates.

Algorithm (in place on an int32 matrix, rows and columns padded with zeros to a multiple of W):
  plu(r0, c0, nc): column range [c0, c0+nc), active rows r0..m.
    nc <= W : base case, one cooperative RawKernel `panel_k` (pivot search + elimination, one grid barrier per column).
    else    : k1 = plu(left half); apply TRSM (recursive, INT8 products) to the top-right block with the unit lower
              triangle gathered from the pivot columns; Schur update of the bottom-right block with the INT8 product;
              k2 = plu(right half at row offset r0 + k1).
  Pivot rows are swapped (whole rows) to positions r0.. after each base case, so rows < rank are the pivot rows.
  Result layout: pivcols[t] = column of pivot t; L(i, t) = A[i, pivcols[t]] (strictly below the pivot row, unit
  diagonal implicit); U(i, c) = A[i, c] for i < rank and c >= pivcols[i]; P = row permutation `perm`.
  All device arithmetic is int32; the modular product is the four-GEMM base-256 signed-digit scheme of Layer 1.
"""

import importlib
import os
import sys
import time
from typing import Any

import numpy as np

# torch and CuPy load at run time, as in gororoba_quantum/modular_echelon.py, so a type check of this file
# does not walk the GPU packages of the host interpreter.
cp: Any = importlib.import_module("cupy")
torch: Any = importlib.import_module("torch")

KMAX = 32768
IMAX = 0x7FFFFFFF

SRC = r"""
#define IMAX 0x7fffffff
#define WMAX 256
#define W2 (65536 % P)

__device__ __forceinline__ int mulmod(int a, int b) { return (a * b) % P; }
__device__ __forceinline__ int modp(int x) { x %= P; return x < 0 ? x + P : x; }
__device__ int powmod(int a, int e) {
  int r = 1;
  while (e) { if (e & 1) r = mulmod(r, a); a = mulmod(a, a); e >>= 1; }
  return r;
}

extern "C" {

__global__ void split_k(const int* src, long long ld, int rows, int cols, signed char* lo, signed char* hi,
                        int orows, int ocols) {
  long long n = (long long)orows * ocols;
  for (long long t = (long long)blockIdx.x * blockDim.x + threadIdx.x; t < n; t += (long long)gridDim.x * blockDim.x) {
    int i = (int)(t / ocols), j = (int)(t % ocols);
    int v = 0;
    if (i < rows && j < cols) { v = src[i * ld + j]; if (v > P / 2) v -= P; }
    int d = ((v + 128) & 255) - 128;
    lo[t] = (signed char)d;
    hi[t] = (signed char)((v - d) >> 8);
  }
}

// mode 0: dst = prod; mode 1: dst = dst - prod; mode 2: dst = dst + prod (all mod P)
__global__ void combine_k(const int* c11, const int* c01, const int* c10, const int* c00, int ccols, int* dst,
                          long long ld, int rows, int cols, int mode) {
  long long n = (long long)rows * cols;
  for (long long t = (long long)blockIdx.x * blockDim.x + threadIdx.x; t < n; t += (long long)gridDim.x * blockDim.x) {
    int i = (int)(t / cols), j = (int)(t % cols);
    long long idx = (long long)i * ccols + j;
    int r = mulmod(modp(c11[idx]), W2);
    int x = modp(c01[idx] + c10[idx]);
    int z = modp(c00[idx]);
    int s = (r + x * 256 + z) % P;
    long long o = i * ld + j;
    if (mode == 0) dst[o] = s;
    else if (mode == 1) { int d = dst[o] - s; dst[o] = d < 0 ? d + P : d; }
    else { int d = dst[o] + s; dst[o] = d >= P ? d - P : d; }
  }
}

__global__ void gather_k(const int* A, long long ld, const int* pc, int k, int rowstart, int nrows, int* out,
                         int orows, int ocols, int unit) {
  long long n = (long long)orows * ocols;
  for (long long t = (long long)blockIdx.x * blockDim.x + threadIdx.x; t < n; t += (long long)gridDim.x * blockDim.x) {
    int i = (int)(t / ocols), j = (int)(t % ocols);
    int v = 0;
    if (i < nrows && j < k) {
      if (unit) { if (j < i) v = A[(long long)(rowstart + i) * ld + pc[j]]; else if (j == i) v = 1; }
      else v = A[(long long)(rowstart + i) * ld + pc[j]];
    }
    out[t] = v;
  }
}

// T = L^{-1} for the unit lower triangular n x n block L (n <= blockDim.x); thread j builds column j.
__global__ void inv_k(const int* L, long long ld, int n, int* T) {
  int j = threadIdx.x;
  if (j >= n) return;
  for (int i = 0; i < n; i++) {
    int x;
    if (i < j) x = 0;
    else if (i == j) x = 1;
    else {
      int s = 0;
      for (int t = j; t < i; t++) s += mulmod(L[i * ld + t], T[t * n + j]);
      x = (P - s % P) % P;
    }
    T[i * n + j] = x;
  }
}

__device__ void gsync(unsigned* bar, unsigned nb, int* err) {
  __threadfence();
  __syncthreads();
  if (threadIdx.x == 0) {
    unsigned t = atomicAdd(bar, 1u) + 1u;
    unsigned goal = ((t - 1u) / nb + 1u) * nb;
    long long spins = 0;
    while (*(volatile unsigned*)bar < goal) { if (++spins > (1LL << 27)) { *err = 1; break; } }
    __threadfence();
  }
  __syncthreads();
}

__device__ void scan_col(const int* A, long long ld, int mrows, int col, const int* used, int* slot, int* sh_min) {
  const int lane = threadIdx.x & 31;
  if (threadIdx.x == 0) *sh_min = IMAX;
  __syncthreads();
  int cand = IMAX;
  long long gt = (long long)blockIdx.x * blockDim.x + threadIdx.x, st = (long long)gridDim.x * blockDim.x;
  for (long long i = gt; i < mrows; i += st) {
    if (!__ldcg(&used[i]) && __ldcg(&A[i * ld + col]) != 0) { cand = (int)i; break; }
  }
  for (int o = 16; o; o >>= 1) cand = min(cand, __shfl_down_sync(0xffffffff, cand, o));
  if (lane == 0 && cand != IMAX) atomicMin(sh_min, cand);
  __syncthreads();
  if (threadIdx.x == 0 && *sh_min != IMAX) atomicMin(&slot[col], *sh_min);
}

// Panel of mrows x ncols (leading dimension ld). Pivot = smallest active row index with a nonzero in the column.
// Rows are not swapped here: a pivot row is frozen (flag in `used`) and later rows eliminate against it.
__global__ void panel_k(int* A, long long ld, int mrows, int ncols, int* used, int* slot, unsigned* bar,
                        int* pivrow, int* pivcol, int* rank_out, int cabs, int* err) {
  __shared__ int u[WMAX];
  __shared__ int s_inv;
  __shared__ int sh_min;
  const int tid = threadIdx.x, lane = tid & 31, nw = blockDim.x >> 5;
  const int gw = blockIdx.x * nw + (tid >> 5), nbw = gridDim.x * nw;
  const unsigned nb = gridDim.x;
  int rank = 0;

  scan_col(A, ld, mrows, 0, used, slot, &sh_min);
  gsync(bar, nb, err);

  for (int j = 0; j < ncols; j++) {
    int piv = __ldcg(&slot[j]);
    if (piv == IMAX) {
      if (j + 1 < ncols) { scan_col(A, ld, mrows, j + 1, used, slot, &sh_min); gsync(bar, nb, err); }
      continue;
    }
    if (tid == 0) sh_min = IMAX;
    for (int k = tid; k < ncols; k += blockDim.x) u[k] = (k >= j) ? __ldcg(&A[(long long)piv * ld + k]) : 0;
    __syncthreads();
    if (tid == 0) s_inv = powmod(u[j], P - 2);
    if (blockIdx.x == 0 && tid == 0) { pivrow[rank] = piv; pivcol[rank] = cabs + j; }
    __syncthreads();
    const int inv = s_inv;
    int cand = IMAX;
    const int nxt = (j + 1) & 31;
    for (int i = gw; i < mrows; i += nbw) {
      if (i == piv || used[i]) continue;
      long long base = (long long)i * ld;
      int v = A[base + j];
      if (v == 0) {
        if (lane == nxt && j + 1 < ncols && cand == IMAX && A[base + j + 1] != 0) cand = i;
        continue;
      }
      int l = mulmod(v, inv);
      for (int k = lane; k < ncols; k += 32) {
        if (k < j) continue;
        if (k == j) { A[base + k] = l; continue; }
        int a = A[base + k] - l * u[k];
        a %= P; if (a < 0) a += P;
        A[base + k] = a;
        if (k == j + 1 && cand == IMAX && a != 0) cand = i;
      }
    }
    if (lane == 0 && (piv % nbw) == gw) used[piv] = 1;
    rank++;
    if (j + 1 < ncols) {
      if (cand != IMAX) atomicMin(&sh_min, cand);
      __syncthreads();
      if (tid == 0 && sh_min != IMAX) atomicMin(&slot[j + 1], sh_min);
      gsync(bar, nb, err);
    }
  }
  if (blockIdx.x == 0 && tid == 0) *rank_out = rank;
}

}
"""

# ANU QRNG draw-2026-11-08T170257Z index 2 (docs/evidence/qrng_seeds/allocations.json)
VERIFY_SEED = 11166

_MODULES: dict[str, Any] = {}


def module(p):
    if p not in _MODULES:
        _MODULES[p] = cp.RawModule(code=f"#define P {int(p)}\n" + SRC, options=("-std=c++17",))
    return _MODULES[p]


def cpv(t):
    return cp.from_dlpack(t)


class Pluq:
    def __init__(self, a, p, w=256, tb=256, prof=False):
        if not (2 <= p < 2**15):
            raise ValueError("p must be below 2^15")
        if w > 256 or w % 8 or tb > 256:
            raise ValueError("w and tb are limited to 256 and w to multiples of 8")
        self.p, self.w, self.tb, self.prof = p, w, tb, prof
        self.mod = module(p)
        self.k_split = self.mod.get_function("split_k")
        self.k_comb = self.mod.get_function("combine_k")
        self.k_gather = self.mod.get_function("gather_k")
        self.k_inv = self.mod.get_function("inv_k")
        self.k_panel = self.mod.get_function("panel_k")
        self.sms = cp.cuda.Device().attributes["MultiProcessorCount"]
        regs = self.k_panel.num_regs
        per_sm = min(1536 // 256, 65536 // (256 * max(regs, 1)))
        self.panel_blocks = self.sms * max(1, min(2, per_sm))
        m, n = a.shape
        self.m, self.n = m, n
        self.mp = -(-m // w) * w
        self.np_ = -(-n // w) * w
        self.A = torch.zeros((self.mp, self.np_), dtype=torch.int32, device="cuda")
        self.A[:m, :n] = torch.as_tensor(a, dtype=torch.int32).to("cuda")
        self.Ac = cpv(self.A)
        self.pivcols = torch.zeros(self.mp + self.np_ + w, dtype=torch.int32, device="cuda")
        self.pivc = cpv(self.pivcols)
        self.perm = np.arange(self.mp)
        self.rank = 0
        self.ev = {}
        self.tag = ""

    # ---------------------------------------------------------------- timing
    class _T:
        def __init__(self, owner, name):
            self.o, self.name = owner, name

        def __enter__(self):
            if self.o.prof:
                self.s = torch.cuda.Event(enable_timing=True)
                self.s.record()

        def __exit__(self, *a):
            if self.o.prof:
                e = torch.cuda.Event(enable_timing=True)
                e.record()
                self.o.ev.setdefault(self.name, []).append((self.s, e))

    def t(self, name):
        return Pluq._T(self, name)

    def times(self):
        torch.cuda.synchronize()
        return {k: sum(s.elapsed_time(e) for s, e in v) / 1e3 for k, v in self.ev.items()}

    # ---------------------------------------------------------------- products
    @staticmethod
    def _grid(n):
        return (min(-(-n // 256), 1 << 16),)

    def split(self, x, lo, hi):
        rows, cols = x.shape
        ld = x.strides[0] // 4
        if x.strides[1] != 4:
            raise ValueError("operand needs unit column stride")
        orows, ocols = lo.shape
        self.k_split(
            self._grid(orows * ocols),
            (256,),
            (x, np.int64(ld), np.int32(rows), np.int32(cols), cpv(lo), cpv(hi), np.int32(orows), np.int32(ocols)),
        )

    def mm(self, x, y, d, mode):
        """d = (+/-) x y mod p, or d = x y for mode 0; x (M,K), y (K,N), d (M,N) strided cupy views."""
        m, k = x.shape
        k2, n = y.shape
        if k != k2 or d.shape != (m, n):
            raise ValueError("shape mismatch")
        if k > KMAX:
            raise ValueError("inner dimension beyond the exact chunk")
        mp, kp, npad = max(32, -(-m // 32) * 32), -(-k // 16) * 16, -(-n // 16) * 16
        dev = "cuda"
        tag = self.tag
        with self.t(f"{tag}.split"):
            xl = torch.empty((mp, kp), dtype=torch.int8, device=dev)
            xh = torch.empty((mp, kp), dtype=torch.int8, device=dev)
            yl = torch.empty((kp, npad), dtype=torch.int8, device=dev)
            yh = torch.empty((kp, npad), dtype=torch.int8, device=dev)
            self.split(x, xl, xh)
            self.split(y, yl, yh)
        with self.t(f"{tag}.int8"):
            mmf = torch._int_mm
            c11, c01, c10, c00 = mmf(xh, yh), mmf(xl, yh), mmf(xh, yl), mmf(xl, yl)
        with self.t(f"{tag}.combine"):
            ld = d.strides[0] // 4
            self.k_comb(
                self._grid(m * n),
                (256,),
                (
                    cpv(c11),
                    cpv(c01),
                    cpv(c10),
                    cpv(c00),
                    np.int32(npad),
                    d,
                    np.int64(ld),
                    np.int32(m),
                    np.int32(n),
                    np.int32(mode),
                ),
            )

    # ---------------------------------------------------------------- elimination
    def gather(self, rowstart, nrows, k, unit, ncols=None):
        out = cp.empty((nrows, k), dtype=cp.int32)
        self.k_gather(
            self._grid(nrows * k),
            (256,),
            (
                self.Ac,
                np.int64(self.np_),
                self._pc,
                np.int32(k),
                np.int32(rowstart),
                np.int32(nrows),
                out,
                np.int32(nrows),
                np.int32(k),
                np.int32(unit),
            ),
        )
        return out

    def trsm(self, lt, b, a, e):
        if e - a <= self.tb:
            n = e - a
            tmat = cp.empty((n, n), dtype=cp.int32)
            with self.t("trsm.inv"):
                self.k_inv((1,), (256,), (lt[a:e, a:e], np.int64(lt.strides[0] // 4), np.int32(n), tmat))
            self.mm(tmat, b[a:e], b[a:e], 0)
        else:
            mid = a + ((e - a) // 2 + 7) // 8 * 8
            self.trsm(lt, b, a, mid)
            self.mm(lt[mid:e, a:mid], b[a:mid], b[mid:e], 1)
            self.trsm(lt, b, mid, e)

    def update(self, r0, k1, c1, nr):
        self._pc = self.pivc[r0 : r0 + k1]
        b = self.Ac[r0 : r0 + k1, c1 : c1 + nr]
        self.tag = "trsm"
        with self.t("trsm.total"):
            with self.t("gather"):
                lt = self.gather(r0, k1, k1, 1)
            self.trsm(lt, b, 0, k1)
        m = self.mp - (r0 + k1)
        if m > 0:
            self.tag = "schur"
            with self.t("schur.total"):
                with self.t("gather"):
                    lb = self.gather(r0 + k1, m, k1, 0)
                self.mm(lb, b, self.Ac[r0 + k1 :, c1 : c1 + nr], 1)

    def base(self, r0, c0, nc):
        mrows = self.mp - r0
        if mrows <= 0:
            return 0
        nbk = max(1, min(self.panel_blocks, -(-mrows // 8)))
        used = cp.zeros(mrows, dtype=cp.int32)
        slot = cp.full(nc + 1, IMAX, dtype=cp.int32)
        bar = cp.zeros(1, dtype=cp.uint32)
        pivrow = cp.zeros(nc + 1, dtype=cp.int32)
        rank_out = cp.zeros(1, dtype=cp.int32)
        err = cp.zeros(1, dtype=cp.int32)
        with self.t("base.kernel"):
            self.k_panel(
                (nbk,),
                (256,),
                (
                    self.Ac[r0:, c0 : c0 + nc],
                    np.int64(self.np_),
                    np.int32(mrows),
                    np.int32(nc),
                    used,
                    slot,
                    bar,
                    pivrow,
                    self.pivc[r0:],
                    rank_out,
                    np.int32(c0),
                    err,
                ),
            )
        k = int(rank_out.get()[0])
        if int(err.get()[0]):
            raise RuntimeError("grid barrier timed out")
        with self.t("base.swap"):
            self.swap(r0, k, pivrow[:k].get())
        return k

    def swap(self, r0, k, pr):
        pos_of, content = {}, {}
        for s in range(k):
            tgt = r0 + s
            lab = r0 + int(pr[s])
            src = pos_of.get(lab, lab)
            if src == tgt:
                continue
            lt = content.get(tgt, tgt)
            content[tgt] = lab
            pos_of[lab] = tgt
            content[src] = lt
            pos_of[lt] = src
        if not content:
            return
        dst = np.fromiter(content.keys(), dtype=np.int64)
        srcl = np.array([content[d] for d in dst], dtype=np.int64)
        di = torch.as_tensor(dst, device="cuda")
        si = torch.as_tensor(srcl, device="cuda")
        tmp = self.A.index_select(0, si)
        self.A.index_copy_(0, di, tmp)
        old = self.perm.copy()
        self.perm[dst] = old[srcl]

    def rec(self, r0, c0, nc):
        if r0 >= self.mp:
            return 0
        if nc <= self.w:
            return self.base(r0, c0, nc)
        nb = nc // self.w
        n1 = (nb // 2) * self.w
        k1 = self.rec(r0, c0, n1)
        c1, nr = c0 + n1, nc - n1
        if k1 > 0:
            self.update(r0, k1, c1, nr)
        k2 = self.rec(r0 + k1, c1, nr)
        return k1 + k2

    def factor(self):
        self.rank = self.rec(0, 0, self.np_)
        return self.rank

    # ---------------------------------------------------------------- results
    def extract(self):
        r = self.rank
        pc = self.pivcols[:r].long()
        a = self.A
        lmat = a.index_select(1, pc).clone()
        if r:
            lmat[:r] = torch.tril(lmat[:r], -1)
            lmat[:r].diagonal().fill_(1)
        cols = torch.arange(self.np_, device="cuda")
        u = torch.where(cols[None, :] >= pc[:, None], a[:r], torch.zeros((), dtype=torch.int32, device="cuda"))
        return lmat, u, pc


# ------------------------------------------------------------------- verification
def matvec_mod(mat, x, p, chunk=512):
    out = torch.empty(mat.shape[0], dtype=torch.int64, device="cuda")
    for s in range(0, mat.shape[0], chunk):
        out[s : s + chunk] = (mat[s : s + chunk].long() * x).sum(1) % p
    return out


def verify(a_np, f, p, rng, nvec=4, nsamp=256):
    """Raises on any failure; returns a dict of what was checked."""
    m, n = a_np.shape
    r = f.rank
    lmat, u, pc = f.extract()
    a0 = torch.zeros((f.mp, f.np_), dtype=torch.int32, device="cuda")
    a0[:m, :n] = torch.as_tensor(a_np).to("cuda")
    perm = torch.as_tensor(f.perm, device="cuda")
    if len(set(f.perm.tolist())) != f.mp:
        raise RuntimeError("row permutation is not a permutation")
    piv = np.zeros(f.np_, dtype=bool)
    piv[pc.cpu().numpy()] = True
    if len(set(pc.cpu().tolist())) != r or not np.all(np.diff(pc.cpu().numpy()) > 0):
        raise RuntimeError("pivot columns are not strictly increasing")
    order = torch.as_tensor(np.concatenate([np.flatnonzero(piv), np.flatnonzero(~piv)]), device="cuda")
    uq = u.index_select(1, order)
    head = uq[:, :r]
    if torch.count_nonzero(torch.tril(head, -1)) != 0:
        raise RuntimeError("U Q^T leading block is not upper triangular")
    if r and torch.count_nonzero(head.diagonal()) != r:
        raise RuntimeError("zero on the diagonal of U")
    for _ in range(nvec):
        xq = torch.as_tensor(rng.integers(0, p, f.np_), device="cuda", dtype=torch.int64)
        w = torch.zeros(f.np_, dtype=torch.int64, device="cuda")
        w[order] = xq
        lhs = matvec_mod(a0, w, p)[perm]
        y = matvec_mod(uq, xq, p) if r else torch.zeros(0, dtype=torch.int64, device="cuda")
        rhs = matvec_mod(lmat, y, p) if r else torch.zeros(f.mp, dtype=torch.int64, device="cuda")
        if not torch.equal(lhs, rhs):
            raise RuntimeError("Freivalds check failed for P L U Q = A")
    if r:
        ii = torch.as_tensor(rng.integers(0, f.mp, nsamp), device="cuda")
        jj = torch.as_tensor(rng.integers(0, f.np_, nsamp), device="cuda")
        lrows = lmat[ii].long()
        ucols = uq[:, jj].long().T
        got = (lrows * ucols).sum(1) % p
        want = a0[perm[ii], order[jj]].long()
        if not torch.equal(got, want):
            raise RuntimeError("sampled entry mismatch")
    return {"rank": r, "freivalds_vectors": nvec, "sampled_entries": nsamp if r else 0}


# ------------------------------------------------------------------- matrices
def lowrank(m, n, r, p, rng):
    x = torch.as_tensor(rng.integers(0, p, (m, r)), dtype=torch.float64, device="cuda")
    y = torch.as_tensor(rng.integers(0, p, (r, n)), dtype=torch.float64, device="cuda")
    return torch.fmod(x @ y, p).to(torch.int32).cpu().numpy()


def make(cls, m, n, p, rng):
    k = min(m, n)
    if cls == "full":
        return rng.integers(0, p, (m, n), dtype=np.int32)
    if cls == "lowrank_half":
        return lowrank(m, n, max(1, k // 2), p, rng)
    if cls == "lowrank_eighth":
        return lowrank(m, n, max(1, k // 8), p, rng)
    if cls == "rank_n_minus_1":
        return lowrank(m, n, k - 1, p, rng)
    if cls == "rank1":
        return lowrank(m, n, 1, p, rng)
    if cls == "sparse":
        a = np.zeros((m, n), dtype=np.int32)
        cnt = max(m, n) * 3
        a[rng.integers(0, m, cnt), rng.integers(0, n, cnt)] = rng.integers(1, p, cnt)
        return a
    if cls == "zero_rows_cols":
        a = rng.integers(0, p, (m, n), dtype=np.int32)
        a[rng.random(m) < 0.3] = 0
        a[:, rng.random(n) < 0.3] = 0
        return a
    if cls == "permutation":
        a = np.zeros((m, n), dtype=np.int32)
        rows = rng.permutation(m)[:k]
        cols = rng.permutation(n)[:k]
        a[rows, cols] = rng.integers(1, p, k)
        return a
    if cls == "vandermonde_dup":
        nodes = rng.permutation(p)[: max(1, m // 2)]
        x = nodes[rng.integers(0, len(nodes), m)].astype(np.int64)
        a = np.empty((m, n), dtype=np.int64)
        cur = np.ones(m, dtype=np.int64)
        for j in range(n):
            a[:, j] = cur
            cur = cur * x % p
        return a.astype(np.int32)
    if cls == "hankel_lowrank":
        r = max(1, k // 4)
        lam = rng.permutation(np.arange(1, p))[:r].astype(np.int64)
        c = rng.integers(1, p, r).astype(np.int64)
        h = np.zeros(m + n - 1, dtype=np.int64)
        cur = c.copy()
        for t in range(m + n - 1):
            h[t] = int(cur.sum()) % p
            cur = cur * lam % p
        idx = np.arange(m)[:, None] + np.arange(n)[None, :]
        return h[idx].astype(np.int32)
    if cls == "hankel_full":
        h = rng.integers(0, p, m + n - 1)
        idx = np.arange(m)[:, None] + np.arange(n)[None, :]
        return h[idx].astype(np.int32)
    raise ValueError(cls)


CLASSES = [
    "full",
    "lowrank_half",
    "lowrank_eighth",
    "rank_n_minus_1",
    "rank1",
    "sparse",
    "zero_rows_cols",
    "permutation",
    "vandermonde_dup",
    "hankel_lowrank",
    "hankel_full",
]


def flint_rank(a, p):
    import flint

    mat = flint.nmod_mat(a.shape[0], a.shape[1], a.ravel().tolist(), p)
    t = time.perf_counter()
    r = mat.rank()
    return r, time.perf_counter() - t


def gpu_factor(a, p, **kw):
    f = Pluq(a, p, **kw)
    torch.cuda.synchronize()
    t = time.perf_counter()
    f.factor()
    torch.cuda.synchronize()
    return f, time.perf_counter() - t


def versions():
    import flint

    return {
        "torch": torch.__version__,
        "cupy": cp.__version__,
        "python-flint": flint.__version__,
        "cuda_driver": cp.cuda.runtime.driverGetVersion(),
        "cuda_runtime": cp.cuda.runtime.runtimeGetVersion(),
        "gpu": torch.cuda.get_device_name(0),
        "python": sys.version.split()[0],
    }


def rss_gib():
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20


def cmd_verify(args):
    p = int(args[0])
    sizes = [int(v) for v in args[1].split(",")]
    classes = args[2].split(",") if len(args) > 2 and args[2] != "all" else CLASSES
    shapes = args[3] if len(args) > 3 else "square,tall,wide"
    use_flint = os.environ.get("NO_FLINT") is None
    print(versions(), flush=True)
    rng = np.random.default_rng(VERIFY_SEED)
    warm = rng.integers(0, p, (300, 300), dtype=np.int32)
    gpu_factor(warm, p)
    for n in sizes:
        for shape in shapes.split(","):
            m, nn = {"square": (n, n), "tall": (n + n // 2, n), "wide": (n, n + n // 2), "odd": (n - 37, n + 11)}[shape]
            for cls in classes:
                if shape != "square" and cls in ("hankel_lowrank", "vandermonde_dup") and n > 1024:
                    continue
                a = make(cls, m, nn, p, rng)
                f, dt = gpu_factor(a, p)
                res = verify(a, f, p, rng)
                line = (
                    f"n={n} shape={shape} {m}x{nn} class={cls} p={p} gpu_rank={f.rank} "
                    f"gpu_time={dt:.3f}s verify=PASS {res}"
                )
                if use_flint:
                    fr, ft = flint_rank(a, p)
                    if fr != f.rank:
                        print(line + f" flint_rank={fr} MISMATCH", flush=True)
                        raise RuntimeError("rank mismatch against FLINT")
                    line += f" flint_rank={fr} flint_time={ft:.3f}s rank_match=PASS"
                print(line + f" rss_gib={rss_gib():.2f}", flush=True)
                del f
                torch.cuda.empty_cache()
                cp.get_default_memory_pool().free_all_blocks()


def cmd_bench(args):
    p = int(args[0])
    n = int(args[1])
    cls = args[2]
    reps = int(args[3])
    flint_on = args[4] == "flint"
    w = int(args[5]) if len(args) > 5 else 256
    tb = int(args[6]) if len(args) > 6 else 256
    rng = np.random.default_rng(7 + n)
    print(versions(), flush=True)
    gpu_factor(rng.integers(0, p, (1024, 1024), dtype=np.int32), p, w=w, tb=tb)
    a = make(cls, n, n, p, rng)
    ts = []
    for _ in range(reps):
        f, dt = gpu_factor(a, p, w=w, tb=tb)
        ts.append(dt)
        r = f.rank
        del f
    print(
        f"bench n={n} class={cls} p={p} w={w} tb={tb} gpu_rank={r} "
        f"gpu_times={[f'{t:.3f}' for t in ts]} gpu_min={min(ts):.3f}s",
        flush=True,
    )
    f, dt = gpu_factor(a, p, w=w, tb=tb)
    res = verify(a, f, p, rng)
    print(f"verify=PASS {res}", flush=True)
    del f
    if flint_on:
        fr, ft = flint_rank(a, p)
        print(f"flint n={n} class={cls} rank={fr} time={ft:.3f}s rank_match={fr == r}", flush=True)
        if fr != r:
            raise RuntimeError("rank mismatch")
    print(f"rss_gib={rss_gib():.2f}", flush=True)


def cmd_profile(args):
    p, n, cls = int(args[0]), int(args[1]), args[2]
    w = int(args[3]) if len(args) > 3 else 256
    tb = int(args[4]) if len(args) > 4 else 256
    rng = np.random.default_rng(7 + n)
    gpu_factor(rng.integers(0, p, (1024, 1024), dtype=np.int32), p, w=w, tb=tb)
    a = make(cls, n, n, p, rng)
    f = Pluq(a, p, w=w, tb=tb, prof=True)
    torch.cuda.synchronize()
    t = time.perf_counter()
    f.factor()
    torch.cuda.synchronize()
    wall = time.perf_counter() - t
    tm = f.times()
    print(f"profile n={n} class={cls} w={w} tb={tb} wall={wall:.3f}s rank={f.rank}", flush=True)
    for k in sorted(tm):
        print(f"  {k:18s} {tm[k]:8.4f}s  calls={len(f.ev[k])}", flush=True)
    print("  (event sums; wall minus base.kernel/base.swap/trsm.total/schur.total = host gaps)", flush=True)


if __name__ == "__main__":
    {"verify": cmd_verify, "bench": cmd_bench, "profile": cmd_profile}[sys.argv[1]](sys.argv[2:])
