"""Exact reduced row echelon form and growing echelon bases over F_p, on FLINT, compact host storage or CUDA.

`rref(a, p, backend)` returns the unique reduced row echelon rows and pivot columns of a residue matrix. The `flint`
backend runs `flint.nmod_mat.rref`; the `gpu` backend factors the matrix with the recursive PLUQ scheme of FFLAS-FFPACK
and clears the entries above each pivot by a blocked back substitution, so both backends return identical arrays for
every input (docs/design/gpu-exact-modular-linear-algebra.md, Layer 3).

`Echelon` is a reduced row echelon basis of a subspace of F_p^ncols that grows by row insertion, the structure the
fiber-rank closure keeps per character block. With `backend="gpu"` the basis B lives on the device as int32 residues
and `reduce`, `insert` and the update of B never leave it: the host passes the rows to insert and reads back only the
pivot columns and the rows it asks for.

With `backend="compact"`, pivot columns are implicit unit vectors and only nonpivot coefficients are retained as
uint16 column panels. Insertions update one panel at a time, so neither removing newly promoted pivot columns nor
growing the row count copies the whole basis. Arithmetic is tiled through float64 products whose inner dimension is
checked against the exact-integer bound. This representation is intended for CPU closures whose full float64 RREF
bases exceed memory; it changes storage, not the row space or insertion order. Its prime range is the device range
below: uint16 residues need p <= 2^16 and each float64 tile of COMPACT_INNER columns needs
COMPACT_INNER (p - 1)^2 < 2^53 (p <= 1,482,911 at 4,096), both wider than the shared bound p < PMAX = 2^15 that the
constructor enforces.

Exactness. Residues are int32 in [0, p) with an odd prime p < 2^15. A modular product splits each operand into signed
base-256 digits (a = 256 a1 + a0, a0 in [-128, 127], a1 in [-64, 64]) and runs four INT8 tensor-core products with
INT32 accumulation, A1 B1, A0 B1, A1 B0 and A0 B0. Digit products stay below 2^14 in magnitude, so an inner dimension
of at most KMAX = 32768 keeps every accumulator below 2^30; longer inner dimensions run in KMAX chunks. Each partial
sum reduces mod p before it is scaled by a weight below p, so every device value fits in int32. The pivot search
takes the smallest active row index with a nonzero entry, which makes the pivot set of one factorization equal to the
leftmost-pivot set of the row space; the reduced echelon form of a row space is unique, so it equals FLINT's.

Dependencies. torch (its `_int_mm` INT8 product, pinned to the torch release the design document records) and CuPy
(NVRTC compilation of the elimination kernel, `cp.from_dlpack`) load on first use of the `gpu` backend, so this module
imports on hosts without them. `gpu_available()` reports whether the backend can run.

Device memory. GOROROBA_GPU_GIB, when set, caps the process's device memory at that many GiB (a 1 GiB CuPy pool, 0.5 GiB
for the CUDA context and the rest as torch's allocator limit); unset, both allocators grow to the device size.
"""

from __future__ import annotations

import importlib
import os
import time
from typing import Any, Literal

import numpy as np

Backend = Literal["flint", "compact", "gpu"]

KMAX = 32768
IMAX = 0x7FFFFFFF
PMAX = 2**15
COMPACT_COLS = 1024
COMPACT_INNER = 4096

_KERNELS = r"""
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


def is_odd_prime(p: int) -> bool:
    """True for an odd prime."""
    return p > 2 and p % 2 == 1 and all(p % q for q in range(3, int(p**0.5) + 1, 2))


def check_modulus(p: int) -> None:
    """Raise unless p is an odd prime below 2^15, the range the int32 device arithmetic and the Fermat inverse need."""
    if not is_odd_prime(p) or p >= PMAX:
        raise ValueError(f"modulus {p} is not an odd prime below {PMAX}")


def _import_gpu() -> tuple[Any, Any]:
    """The torch and cupy modules; ImportError when either is missing."""
    return importlib.import_module("torch"), importlib.import_module("cupy")


def gpu_available() -> bool:
    """True when torch and CuPy import and torch sees a CUDA device."""
    try:
        torch, _ = _import_gpu()
        return bool(torch.cuda.is_available())
    except ImportError:
        return False


GPU_BUDGET_ENV = "GOROROBA_GPU_GIB"
_CUPY_POOL_GIB = 1.0
_CONTEXT_GIB = 0.5


def _limit_device_memory(torch: Any, cp: Any) -> None:
    """Cap this process's device memory at GOROROBA_GPU_GIB GiB when the variable is set.

    torch and CuPy keep separate caching allocators that never lend each other freed blocks. The CuPy pool, which holds
    the elimination kernels' small buffers, is limited to 1 GiB and torch's allocator to the budget minus that pool and
    0.5 GiB for the CUDA context; torch frees its cached blocks and retries before it raises an out-of-memory error at
    its limit, so the cap bounds the footprint without a per-call release."""
    raw = os.environ.get(GPU_BUDGET_ENV)
    if not raw:
        return
    budget = float(raw)
    torch_gib = budget - _CUPY_POOL_GIB - _CONTEXT_GIB
    total = torch.cuda.get_device_properties(0).total_memory
    if torch_gib <= 0 or budget * 2**30 > total:
        raise ValueError(f"{GPU_BUDGET_ENV}={raw} leaves no room on a {total / 2**30:.1f} GiB device")
    torch.cuda.set_per_process_memory_fraction(torch_gib * 2**30 / total)
    cp.get_default_memory_pool().set_limit(size=int(_CUPY_POOL_GIB * 2**30))


def modular_matmul_exact_bound(inner: int, p: int) -> bool:
    """True when a float64 product with this inner dimension stays exact: inner * (p - 1)^2 < 2^53."""
    return inner * (p - 1) ** 2 < 2**53


class DeviceArithmetic:
    """Modular products, PLUQ and reduced row echelon form over F_p on the current CUDA device, for one prime."""

    _instances: dict[int, DeviceArithmetic] = {}

    @classmethod
    def get(cls, p: int) -> DeviceArithmetic:
        """The shared instance for p, which owns the NVRTC-compiled kernel module of that prime."""
        if p not in cls._instances:
            cls._instances[p] = cls(p)
        return cls._instances[p]

    def __init__(self, p: int, w: int = 256, tb: int = 256):
        check_modulus(p)
        if w > 256 or w % 8 or tb > 256:
            raise ValueError("w and tb are limited to 256 and w to multiples of 8")
        self.torch, self.cp = _import_gpu()
        self.p, self.w, self.tb = p, w, tb
        _limit_device_memory(self.torch, self.cp)
        module = self.cp.RawModule(code=f"#define P {int(p)}\n" + _KERNELS, options=("-std=c++17",))
        self.k_split = module.get_function("split_k")
        self.k_comb = module.get_function("combine_k")
        self.k_gather = module.get_function("gather_k")
        self.k_inv = module.get_function("inv_k")
        self.k_panel = module.get_function("panel_k")
        sms = self.cp.cuda.Device().attributes["MultiProcessorCount"]
        per_sm = min(1536 // 256, 65536 // (256 * max(self.k_panel.num_regs, 1)))
        self.panel_blocks = sms * max(1, min(2, per_sm))

    # ------------------------------------------------------------------ products
    @staticmethod
    def _grid(n: int) -> tuple[int]:
        return (min(-(-n // 256), 1 << 16),)

    def _split(self, x: Any, lo: Any, hi: Any) -> None:
        rows, cols = x.shape
        if x.strides[1] != 4:
            raise ValueError("operand needs unit column stride")
        orows, ocols = lo.shape
        args = (x, np.int64(x.strides[0] // 4), np.int32(rows), np.int32(cols), self.cp.from_dlpack(lo))
        self.k_split(
            self._grid(orows * ocols),
            (256,),
            (*args, self.cp.from_dlpack(hi), np.int32(orows), np.int32(ocols)),
        )

    def _mm_chunk(self, x: Any, y: Any, d: Any, mode: int) -> None:
        """d (op)= x y mod p for cupy views with inner dimension at most KMAX; mode 0 sets, 1 subtracts, 2 adds."""
        torch, cp = self.torch, self.cp
        m, k = x.shape
        n = y.shape[1]
        mp, kp, npad = max(32, -(-m // 32) * 32), -(-k // 16) * 16, -(-n // 16) * 16
        i8 = {"dtype": torch.int8, "device": "cuda"}
        xl, xh = torch.empty((mp, kp), **i8), torch.empty((mp, kp), **i8)
        yl, yh = torch.empty((kp, npad), **i8), torch.empty((kp, npad), **i8)
        self._split(x, xl, xh)
        self._split(y, yl, yh)
        mmf = torch._int_mm
        c11, c01, c10, c00 = mmf(xh, yh), mmf(xl, yh), mmf(xh, yl), mmf(xl, yl)
        self.k_comb(
            self._grid(m * n),
            (256,),
            (
                cp.from_dlpack(c11),
                cp.from_dlpack(c01),
                cp.from_dlpack(c10),
                cp.from_dlpack(c00),
                np.int32(npad),
                d,
                np.int64(d.strides[0] // 4),
                np.int32(m),
                np.int32(n),
                np.int32(mode),
            ),
        )

    def mm(self, x: Any, y: Any, d: Any, mode: int) -> None:
        """d = x y (mode 0), d -= x y (mode 1) or d += x y (mode 2) mod p; cupy int32 views, unit column strides."""
        m, k = x.shape
        if y.shape[0] != k or d.shape != (m, y.shape[1]):
            raise ValueError("shape mismatch")
        if k == 0:
            if mode == 0:
                d[...] = 0
            return
        for k0 in range(0, k, KMAX):
            k1 = min(k, k0 + KMAX)
            self._mm_chunk(x[:, k0:k1], y[k0:k1], d, mode if (mode != 0 or k0 == 0) else 2)

    def matmul(self, x: Any, y: Any) -> Any:
        """x y mod p for int32 residue tensors on the device, as a new int32 tensor."""
        out = self.torch.empty((x.shape[0], y.shape[1]), dtype=self.torch.int32, device="cuda")
        self.mm(self.cp.from_dlpack(x), self.cp.from_dlpack(y), self.cp.from_dlpack(out), 0)
        return out

    # ------------------------------------------------------------------ elimination
    def _trsm(self, lt: Any, b: Any, a: int, e: int) -> None:
        cp = self.cp
        if e - a <= self.tb:
            n = e - a
            tmat = cp.empty((n, n), dtype=cp.int32)
            self.k_inv((1,), (256,), (lt[a:e, a:e], np.int64(lt.strides[0] // 4), np.int32(n), tmat))
            self.mm(tmat, b[a:e], b[a:e], 0)
        else:
            mid = a + ((e - a) // 2 + 7) // 8 * 8
            self._trsm(lt, b, a, mid)
            self.mm(lt[mid:e, a:mid], b[a:mid], b[mid:e], 1)
            self._trsm(lt, b, mid, e)

    def _gather(self, f: _Pluq, rowstart: int, nrows: int, k: int, unit: int) -> Any:
        out = self.cp.empty((nrows, k), dtype=self.cp.int32)
        self.k_gather(
            self._grid(nrows * k),
            (256,),
            (f.ac, np.int64(f.np_), f.pc, np.int32(k), np.int32(rowstart), np.int32(nrows), out)
            + (np.int32(nrows), np.int32(k), np.int32(unit)),
        )
        return out

    def _update(self, f: _Pluq, r0: int, k1: int, c1: int, nr: int) -> None:
        f.pc = f.pivc[r0 : r0 + k1]
        b = f.ac[r0 : r0 + k1, c1 : c1 + nr]
        self._trsm(self._gather(f, r0, k1, k1, 1), b, 0, k1)
        m = f.mp - (r0 + k1)
        if m > 0:
            self.mm(self._gather(f, r0 + k1, m, k1, 0), b, f.ac[r0 + k1 :, c1 : c1 + nr], 1)

    def _base(self, f: _Pluq, r0: int, c0: int, nc: int) -> int:
        cp = self.cp
        mrows = f.mp - r0
        if mrows <= 0:
            return 0
        nbk = max(1, min(self.panel_blocks, -(-mrows // 8)))
        used = cp.zeros(mrows, dtype=cp.int32)
        slot = cp.full(nc + 1, IMAX, dtype=cp.int32)
        bar = cp.zeros(1, dtype=cp.uint32)
        pivrow = cp.zeros(nc + 1, dtype=cp.int32)
        rank_out = cp.zeros(1, dtype=cp.int32)
        err = cp.zeros(1, dtype=cp.int32)
        self.k_panel(
            (nbk,),
            (256,),
            (f.ac[r0:, c0 : c0 + nc], np.int64(f.np_), np.int32(mrows), np.int32(nc), used, slot, bar, pivrow)
            + (f.pivc[r0:], rank_out, np.int32(c0), err),
        )
        k = int(rank_out.get()[0])
        if int(err.get()[0]):
            raise RuntimeError("grid barrier timed out")
        self._swap(f, r0, k, pivrow[:k].get())
        return k

    def _swap(self, f: _Pluq, r0: int, k: int, pr: np.ndarray) -> None:
        """Move the k pivot rows to rows r0.. as one gather, keeping the original order of the displaced rows."""
        pos_of: dict[int, int] = {}
        content: dict[int, int] = {}
        for s in range(k):
            tgt = r0 + s
            lab = r0 + int(pr[s])
            src = pos_of.get(lab, lab)
            if src == tgt:
                continue
            displaced = content.get(tgt, tgt)
            content[tgt] = lab
            pos_of[lab] = tgt
            content[src] = displaced
            pos_of[displaced] = src
        if not content:
            return
        dst = np.fromiter(content.keys(), dtype=np.int64)
        srcl = np.fromiter(content.values(), dtype=np.int64)
        di = self.torch.as_tensor(dst, device="cuda")
        si = self.torch.as_tensor(srcl, device="cuda")
        f.a.index_copy_(0, di, f.a.index_select(0, si))

    def _rec(self, f: _Pluq, r0: int, c0: int, nc: int) -> int:
        if r0 >= f.mp:
            return 0
        if nc <= self.w:
            return self._base(f, r0, c0, nc)
        n1 = (nc // self.w // 2) * self.w
        k1 = self._rec(f, r0, c0, n1)
        c1, nr = c0 + n1, nc - n1
        if k1 > 0:
            self._update(f, r0, k1, c1, nr)
        return k1 + self._rec(f, r0 + k1, c1, nr)

    def rref(self, z: Any) -> tuple[Any, Any]:
        """Reduced row echelon rows (int32, rank x n) and pivot columns (int64) of an int32 residue tensor (m x n)."""
        torch, cp = self.torch, self.cp
        m, n = z.shape
        if m == 0 or n == 0:
            return torch.zeros((0, n), dtype=torch.int32, device="cuda"), torch.zeros(
                0, dtype=torch.int64, device="cuda"
            )
        f = _Pluq(self, z)
        r = self._rec(f, 0, 0, f.np_)
        if r == 0:
            return torch.zeros((0, n), dtype=torch.int32, device="cuda"), torch.zeros(
                0, dtype=torch.int64, device="cuda"
            )
        pc = f.pivcols[:r].long()
        cols = torch.arange(f.np_, device="cuda")
        # U rows hold the echelon form in the pivot columns; each row scales to a unit pivot, which int32 holds
        # because a product of two residues stays below p^2 < 2^30.
        u = torch.where(cols[None, :] >= pc[:, None], f.a[:r], torch.zeros((), dtype=torch.int32, device="cuda"))
        diag = u[torch.arange(r, device="cuda"), pc].long()
        dinv = torch.ones(r, dtype=torch.int64, device="cuda")
        base, e = diag.clone(), self.p - 2
        while e:
            if e & 1:
                dinv = dinv * base % self.p
            base = base * base % self.p
            e >>= 1
        rr = torch.remainder(u * dinv.to(torch.int32)[:, None], self.p).contiguous()
        rc = cp.from_dlpack(rr)

        def solve(lo: int, hi: int) -> None:
            # rows lo..hi-1 hold unit-upper rows; clear their entries in the pivot columns lo..hi-1 above the diagonal
            if hi - lo <= 1:
                return
            mid = lo + (hi - lo) // 2
            solve(mid, hi)
            coef = rr[lo:mid].index_select(1, pc[mid:hi]).contiguous()
            self.mm(cp.from_dlpack(coef), rc[mid:hi], rc[lo:mid], 1)
            solve(lo, mid)

        solve(0, r)
        piv = pc.clone()
        if bool((piv[1:] <= piv[:-1]).any()):
            raise RuntimeError("pivot columns are not increasing")
        return rr[:, :n].contiguous(), piv


class _Pluq:
    """Working state of one PLUQ factorization: the padded matrix, its pivot columns and the cupy views of both."""

    def __init__(self, arith: DeviceArithmetic, z: Any):
        torch, cp = arith.torch, arith.cp
        m, n = z.shape
        w = arith.w
        self.mp = -(-m // w) * w
        self.np_ = -(-n // w) * w
        self.a = torch.zeros((self.mp, self.np_), dtype=torch.int32, device="cuda")
        self.a[:m, :n] = z
        self.ac = cp.from_dlpack(self.a)
        self.pivcols = torch.zeros(self.mp + self.np_ + w, dtype=torch.int32, device="cuda")
        self.pivc = cp.from_dlpack(self.pivcols)
        self.pc: Any = None


def rref_flint(a: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    """Reduced row echelon rows (int64, rank x n) and pivot columns of a residue matrix, by `flint.nmod_mat.rref`."""
    import flint

    m, n = a.shape
    if m == 0 or n == 0:
        return np.zeros((0, n), dtype=np.int64), np.zeros(0, dtype=np.int64)
    mat = flint.nmod_mat(m, n, np.mod(a, p).astype(np.int64).ravel().tolist(), p)
    red, rk = mat.rref()
    rows = np.array([int(v) for v in red.entries()], dtype=np.int64).reshape(m, n)[:rk]
    return rows, np.argmax(rows != 0, axis=1).astype(np.int64)


def rref_gpu(a: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    """The same arrays as `rref_flint`, from the device PLUQ factorization and back substitution."""
    arith = DeviceArithmetic.get(p)
    torch = arith.torch
    z = torch.remainder(torch.as_tensor(np.ascontiguousarray(a)).to("cuda"), p).to(torch.int32)
    rows, piv = arith.rref(z.contiguous())
    return rows.cpu().numpy().astype(np.int64), piv.cpu().numpy().astype(np.int64)


def rref(a: np.ndarray, p: int, backend: Backend = "flint") -> tuple[np.ndarray, np.ndarray]:
    """Reduced row echelon rows and pivot columns of a residue matrix over F_p on the chosen backend."""
    if backend in ("flint", "compact"):
        return rref_flint(a, p)
    if backend == "gpu":
        return rref_gpu(a, p)
    raise ValueError(f"unknown backend {backend!r}")


class Echelon:
    """Reduced row echelon basis over F_p of a subspace of F_p^ncols, grown by inserting rows.

    Invariant: basis row i has a one in column piv[i] and zeros in every other pivot column. `insert` reduces the
    incoming rows by the basis, takes the reduced row echelon form of what remains on the non-pivot columns and then
    clears the new pivot columns from the old rows, so the basis stays fully reduced. All backends produce the same
    basis and pivot list for the same insertion sequence.
    """

    def __init__(self, ncols: int, p: int, backend: Backend = "flint"):
        if backend not in ("flint", "compact", "gpu"):
            raise ValueError(f"unknown backend {backend!r}")
        if backend == "compact":
            check_modulus(p)
        self.p, self.ncols, self.backend = p, ncols, backend
        self.piv = np.zeros(0, dtype=np.int64)
        self.insert_seconds = 0.0
        self._nrows = 0
        self._host = np.zeros((0, ncols))
        self._compact_cols: list[np.ndarray] = []
        self._compact_parts: list[np.ndarray] = []
        self._dev: Any = None
        self._arith: DeviceArithmetic | None = None
        if backend == "compact":
            self._compact_cols = [
                np.arange(i, min(i + COMPACT_COLS, ncols), dtype=np.int64) for i in range(0, ncols, COMPACT_COLS)
            ]
            self._compact_parts = [np.zeros((0, len(cols)), dtype=np.uint16) for cols in self._compact_cols]
        if backend == "gpu":
            self._arith = DeviceArithmetic.get(p)
            self._dev = self._arith.torch.zeros((0, ncols), dtype=self._arith.torch.int32, device="cuda")

    def __len__(self) -> int:
        return self._nrows

    # ------------------------------------------------------------------ reading the basis
    @property
    def B(self) -> np.ndarray:
        """All basis rows as a float64 host array."""
        return self.rows(None)

    def rows(self, idx: np.ndarray | list[int] | None) -> np.ndarray:
        """Copy of basis rows `idx`; compact storage materializes only the rows requested."""
        if self.backend == "flint":
            return self._host.copy() if idx is None else self._host[np.asarray(idx, dtype=np.int64)]
        if self.backend == "compact":
            take = np.arange(self._nrows, dtype=np.int64) if idx is None else np.asarray(idx, dtype=np.int64)
            out = np.zeros((len(take), self.ncols), dtype=np.uint16)
            if len(take):
                out[np.arange(len(take)), self.piv[take]] = 1
                for cols, part in zip(self._compact_cols, self._compact_parts, strict=True):
                    out[:, cols] = part[take]
            return out
        torch = self._device().torch
        sel = (
            self._dev[: self._nrows]
            if idx is None
            else self._dev[torch.as_tensor(np.asarray(idx, dtype=np.int64)).cuda()]
        )
        return sel.cpu().numpy().astype(np.float64)

    def new_rows(self, start: set[int]) -> np.ndarray:
        """Basis rows whose pivot column is not in `start`, in basis order."""
        return self.rows(self.new_indices(start))

    def new_indices(self, start: set[int]) -> np.ndarray:
        """Indices of basis rows whose pivot column is not in `start`, without materializing those rows."""
        return np.array([i for i, c in enumerate(self.piv.tolist()) if c not in start], dtype=np.int64)

    def _device(self) -> DeviceArithmetic:
        if self._arith is None:
            raise RuntimeError("device operation on a flint-backed Echelon")
        return self._arith

    # ------------------------------------------------------------------ reduction and insertion
    def reduce(self, x: np.ndarray) -> np.ndarray:
        """Rows of x reduced by the basis (zero in every pivot column), as a float64 host array."""
        if self.backend == "flint":
            return self._reduce_host(x)
        if self.backend == "compact":
            return self._reduce_compact(x)
        out = self._reduce_dev(self._upload(x))
        return out.cpu().numpy().astype(np.float64)

    def insert(self, x: np.ndarray, chunk: int) -> np.ndarray:
        """Insert rows; returns the indices (into the basis) of rows whose pivots are new."""
        start = set(self.piv.tolist())
        t0 = time.perf_counter()
        for s in range(0, len(x), chunk):
            if self.backend == "flint":
                self._insert_host(x[s : s + chunk])
            elif self.backend == "compact":
                self._insert_compact(x[s : s + chunk])
            else:
                self._insert_dev(x[s : s + chunk])
        self.insert_seconds += time.perf_counter() - t0
        return np.array([i for i, c in enumerate(self.piv.tolist()) if c not in start], dtype=np.int64)

    # flint path: float64 basis, BLAS products guarded by the 2^53 bound
    def _matmul_host(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        if not modular_matmul_exact_bound(a.shape[1], self.p):
            raise RuntimeError(f"inner dimension {a.shape[1]} leaves the exact float64 range at p = {self.p}")
        return np.mod(a @ b, self.p)

    def _reduce_host(self, x: np.ndarray) -> np.ndarray:
        if len(self.piv) == 0 or len(x) == 0:
            return np.mod(x, self.p)
        return np.mod(x - self._matmul_host(x[:, self.piv], self._host), self.p)

    def _insert_host(self, x: np.ndarray) -> None:
        y = self._reduce_host(x)
        y = y[np.any(y != 0, axis=1)]
        if len(y) == 0:
            return
        free = np.setdiff1d(np.arange(self.ncols), self.piv)
        rows, piv_rel = rref_flint(y[:, free].astype(np.int64), self.p)
        rk = len(rows)
        if rk == 0:
            return
        xr = np.zeros((rk, self.ncols))
        xr[:, free] = rows
        q = free[piv_rel]
        if len(self.piv):
            self._host = np.mod(self._host - self._matmul_host(self._host[:, q], xr), self.p)
        self._host = np.vstack([self._host, xr])
        self._nrows = len(self._host)
        self.piv = np.concatenate([self.piv, q])

    # compact host path: uint16 nonpivot panels and implicit pivot identities
    def _subtract_compact_product(self, out: np.ndarray, a: np.ndarray, b: np.ndarray) -> None:
        """Set uint16 `out` to out - a @ b mod p, with bounded exact float64 tiles."""
        if a.shape[1] != b.shape[0] or out.shape != (a.shape[0], b.shape[1]):
            raise ValueError("compact product shape mismatch")
        for r0 in range(0, len(out), 128):
            r1 = min(r0 + 128, len(out))
            for c0 in range(0, out.shape[1], COMPACT_COLS):
                c1 = min(c0 + COMPACT_COLS, out.shape[1])
                z = out[r0:r1, c0:c1].astype(np.float64)
                for k0 in range(0, a.shape[1], COMPACT_INNER):
                    k1 = min(k0 + COMPACT_INNER, a.shape[1])
                    if not modular_matmul_exact_bound(k1 - k0, self.p):
                        raise RuntimeError(f"inner tile {k1 - k0} leaves the exact float64 range at p = {self.p}")
                    z = np.mod(
                        z - a[r0:r1, k0:k1].astype(np.float64) @ b[k0:k1, c0:c1].astype(np.float64),
                        self.p,
                    )
                out[r0:r1, c0:c1] = z.astype(np.uint16)

    def _reduce_compact(self, x: np.ndarray) -> np.ndarray:
        out = np.mod(x, self.p).astype(np.uint16)
        if self._nrows == 0 or len(out) == 0:
            return out
        coef = out[:, self.piv].copy()
        out[:, self.piv] = 0
        for cols, part in zip(self._compact_cols, self._compact_parts, strict=True):
            panel = out[:, cols].copy()
            self._subtract_compact_product(panel, coef, part)
            out[:, cols] = panel
        return out

    def _insert_compact(self, x: np.ndarray) -> None:
        y = self._reduce_compact(x)
        y = y[np.any(y != 0, axis=1)]
        if len(y) == 0:
            return
        free = np.concatenate(self._compact_cols) if self._compact_cols else np.zeros(0, dtype=np.int64)
        rows, piv_rel = rref_flint(y[:, free].astype(np.int64), self.p)
        rk = len(rows)
        if rk == 0:
            return
        rows = rows.astype(np.uint16)
        q = free[piv_rel]
        pivot_at = {int(pos): i for i, pos in enumerate(piv_rel.tolist())}
        coef = np.zeros((self._nrows, rk), dtype=np.uint16)
        offset = 0
        for part in self._compact_parts:
            for j in range(part.shape[1]):
                slot = pivot_at.get(offset + j)
                if slot is not None and self._nrows:
                    coef[:, slot] = part[:, j]
            offset += part.shape[1]

        new_cols: list[np.ndarray] = []
        new_parts: list[np.ndarray] = []
        offset = 0
        for cols, part in zip(self._compact_cols, self._compact_parts, strict=True):
            keep = np.array([offset + j not in pivot_at for j in range(len(cols))], dtype=bool)
            kept_cols = cols[keep]
            new_rows = rows[:, offset : offset + len(cols)][:, keep]
            grown = np.empty((self._nrows + rk, len(kept_cols)), dtype=np.uint16)
            if self._nrows:
                grown[: self._nrows] = part[:, keep]
                self._subtract_compact_product(grown[: self._nrows], coef, new_rows)
            grown[self._nrows :] = new_rows
            if len(kept_cols):
                new_cols.append(kept_cols)
                new_parts.append(grown)
            offset += len(cols)
        self._compact_cols = new_cols
        self._compact_parts = new_parts
        self._nrows += rk
        self.piv = np.concatenate([self.piv, q.astype(np.int64)])

    # device path: int32 basis on the GPU
    def _upload(self, x: np.ndarray) -> Any:
        torch = self._device().torch
        xd = torch.remainder(torch.as_tensor(np.ascontiguousarray(x)).to("cuda"), self.p)
        return xd.to(torch.int32).contiguous()

    def _reduce_dev(self, xd: Any) -> Any:
        arith = self._device()
        if self._nrows == 0 or xd.shape[0] == 0:
            return xd
        cp, torch = arith.cp, arith.torch
        y = xd.clone()
        coef = xd.index_select(1, torch.as_tensor(self.piv).cuda()).contiguous()
        arith.mm(cp.from_dlpack(coef), cp.from_dlpack(self._dev[: self._nrows]), cp.from_dlpack(y), 1)
        return y

    def _insert_dev(self, x: np.ndarray) -> None:
        arith = self._device()
        torch, cp = arith.torch, arith.cp
        if len(x) == 0:
            return
        y = self._reduce_dev(self._upload(x))
        y = y[(y != 0).any(dim=1)]
        if y.shape[0] == 0:
            return
        free = np.setdiff1d(np.arange(self.ncols), self.piv)
        free_t = torch.as_tensor(free).cuda()
        rows, piv_rel = arith.rref(y.index_select(1, free_t).contiguous())
        rk = rows.shape[0]
        if rk == 0:
            return
        xr = torch.zeros((rk, self.ncols), dtype=torch.int32, device="cuda")
        xr.index_copy_(1, free_t, rows)
        q = free[piv_rel.cpu().numpy()]
        if self._nrows:
            old = self._dev[: self._nrows]
            coef = old.index_select(1, torch.as_tensor(q).cuda()).contiguous()
            arith.mm(cp.from_dlpack(coef), cp.from_dlpack(xr), cp.from_dlpack(old), 1)
        if self._dev.shape[0] < self._nrows + rk:
            grown = torch.zeros(
                (max(self._dev.shape[0] * 5 // 4, self._nrows + rk), self.ncols), dtype=torch.int32, device="cuda"
            )
            grown[: self._nrows] = self._dev[: self._nrows]
            self._dev = grown
        self._dev[self._nrows : self._nrows + rk] = xr
        self._nrows += rk
        self.piv = np.concatenate([self.piv, q.astype(np.int64)])
