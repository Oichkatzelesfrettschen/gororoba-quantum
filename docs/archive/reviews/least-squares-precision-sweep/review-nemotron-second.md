# Report: Portable Least-Squares Precision Sweep Review

## Most Consequential Finding: Claim 3 Falsified — x87 Refinement Scores Not Identical Across Hosts

**File/Location**: README.md lines 260-268 ("Results across hosts"); rows-summary.tsv lines 11-13, 26-28, 72-74, 370-372, 207-209 (x87 refinement rows)

**Status**: **FALSIFIED** (measured)

The README states: "on those five hosts every configuration run on two or more of them scores identically to the last recorded digit: 24 arb normal-equation configurations, 8 binary128 configurations through SLEEF (build-host, zen4-wsl, aws-sapphire-rapids) and 5 x87 configurations."

Data shows only **2 of 5 x87 configuration types** score identically across the five digest-agreeing hosts (build-host, zen4-wsl, aws-sapphire-rapids, oci-a1-neoverse-n1, zen4-windows):
- **Householder QR** (1,2,4,8,10/16/32 workers): all three hosts score **59.52742708597964** (identical)
- **Normal equations (Cholesky)**: all three hosts score **57.24159500238924** (identical)
- **Refinement 1 step**: build-host 51.5137, zen4-wsl 51.5847, aws 51.4305 — **differ at 2nd decimal**
- **Refinement 2 steps**: build-host 51.6013, zen4-wsl 51.5878, aws 51.4130 — **differ**
- **Refinement 3 steps**: build-host 51.5422, zen4-wsl 51.5736, aws 51.4329 — **differ**

The sentence "every configuration run on two or more of them scores identically" is false. The count "5 x87 configurations" is incorrect; only 2 types (Householder, normal) are identical.

---

## Claim 1: Cap Mechanism Recorded Correctly — **PROVED** (measured)

- Four Linux hosts (build-host, zen4-wsl, aws-sapphire-rapids, oci-a1-neoverse-n1): mechanism `systemd`, `enforced` true (trial scope readback ok)
- M1: mechanism `none`, `enforced` false — RLIMIT_AS probe failed in `preexec_fn` (host-records.json line 613)
- zen4-windows: mechanism `none`, `enforced` false — `--cap none` requested (host-records.json line 1120)
- All rows in rows-summary.tsv match host record mechanism/enforced per host

No row shows cap differing from applied; no path fails on its named OS.

---

## Claim 2: Thread Ladder and Skip Reasons Correct — **PROVED** (computed)

- Thread ladder never exceeds `host.cpus_used` (verified per host: build-host 10, zen4-wsl 32, aws 2, oci 2, zen4-windows 32, m1 8)
- Skip reasons match `fp_host` status functions:
  - x87 skipped on non-x86 (m1 arm64, oci aarch64) and Windows (nmant=52) — matches `x87_status()`
  - quaddtype skipped on oci (ModuleNotFoundError) — matches `quad_status()`
  - quaddtype longdouble backend skipped on m1 (needs x87) — correct
  - QuadBLAS errors on zen4-windows (12 rows, NotImplementedError) — matches `quadblas_status()` probe

---

## Claim 4: QuadBLAS Probe and 12 Error Rows — **PROVED** (measured)

- `fp_host.quadblas_status()` calls `numpy_quaddtype.get_quadblas_version()` (fp_host.py:198-208)
- All quaddtype configs require `quad+quadblas` (SLEEF) or `quad+quadblas+x87` (longdouble) — fp_sweep.py:78-83
- zen4-windows-full.jsonl lines 41-52: exactly 12 error rows (`NotImplementedError: QuadBLAS is disabled`) — 6 thread counts × 2 solvers (Householder, normal) for SLEEF backend
- README table correctly counts "12 QuadBLAS errors" for zen4-windows
- Probe returns `None` (ok) on hosts where QuadBLAS works (build-host, zen4-wsl, aws, m1 all run SLEEF successfully)

---

## Claim 5: Input Digests and M1 Difference — **PROVED** (measured)

- Four digests identical across all 6 hosts: design_matrix, rate_observables, hermitian_basis, ideal_choi_vector
- `observed_rate_columns` differs only on M1 (host-records.json: build-host f9b69..., M1 ae852e...)
- README states "4 of 5: observed_rate_columns differs" for M1 (line 258), makes no claim on difference location/magnitude
- Receipt comparing npz files labeled "not run" (line 276); libm accept-reject labeled "Hypothesis" (line 278)

---

## Claim 6: Row Hygiene — **PROVED WITH ACKNOWLEDGED GAP** (measured)

- No hostname, username, local path, kernel release, distribution string in hosts/*.jsonl or host-records.json
- `fp_export.py` validates `--host-label` via `fp_host.label_error()` (fp_export.py:42-45), same as fp_sweep.py
- **Gap**: `cap.bytes = min(8 GiB, 0.6 × physical memory)` implies memory size on hosts with cap < 8 GiB:
  - aws-sapphire-rapids: cap below 8 GiB → physical memory implied
  - oci-a1-neoverse-n1: cap below 8 GiB → physical memory implied
  - Acknowledged in brief as "known gap for you to judge"

---

## Claim 7: "Not Run" Entries Accurate — **PROVED** (measured)

All four README "not run" entries correctly describe unmeasured checks:
1. Windows `fp_export.py` — "not run: fp_export.py needs fcntl" (line 255, 289)
2. M1 npz comparison receipt — "not run because it needs the M1's fp-inputs.npz" (line 276)
3. turion-linux numpy 2.5.4 run — "is not run and has no retained record" (line 291)
4. Windows rerun after QuadBLAS probe — "retained rows predate the probe and stay as measured" (line 288)

---

## README Overstatements Beyond Claims

**File**: README.md lines 260-268 ("Results across hosts")

1. "5 x87 configurations" score identically — **false** (only 2 types)
2. "every configuration run on two or more of them scores identically" — **false** (refinement steps differ)
3. "zen4-wsl and aws-sapphire-rapids ... agree on 6 of the 10 float64 configurations they share" — **verified true** (gelsd 1,2; gelsy 1,2; gelss 1,2 agree; pinv 1,2 and numpy lstsq 1,2 differ)

---

## Defects in Code

| File | Defect | Severity |
|------|--------|----------|
| `fp_sweep.py:286` | `wait_for_idle` uses `os.cpu_count()` not `cpus` (min of cpu_count and workers()) for idle threshold | Minor |
| `fp_host.py:44-46` | `label_error` only checks hostname substrings len≥3; short hostnames could leak | Minor |
| `fp_host.py:111-115` | `cap.bytes` implies physical memory on small hosts (acknowledged gap) | Known/accepted |
| `fp_sweep.py:230-235` | `quadblas_status` probe added after zen4-windows run; retained rows show errors not skips (README acknowledges) | Not a current defect |

---

## BLAS Kernel Selection Conjecture

**Observation**: Float64 pinv/numpy lstsq scores vary across SkylakeX hosts despite same `blas.architecture` "SkylakeX":
- zen4-wsl (OpenBLAS 0.3.31.dev/0.3.34.106.0, MAX_THREADS=64): pinv 47.58, numpy lstsq 47.88
- aws-sapphire-rapids (OpenBLAS 0.3.31.dev/0.3.34.106.0, MAX_THREADS=64): pinv 47.99, numpy lstsq 47.97
- zen4-windows (OpenBLAS 0.3.34.106.0/0.3.31.dev, MAX_THREADS=24): pinv 49.60, numpy lstsq 48.01

Scipy drivers (gelsd, gelsy, gelss) agree on zen4-wsl and aws (both MAX_THREADS=64) but differ on zen4-windows (MAX_THREADS=24).

**Conjecture**: Float64 pinv/QR scores are sensitive to OpenBLAS build configuration (version, MAX_THREADS, core tuning) even within same architecture; scipy LAPACK drivers are more stable across SkylakeX builds. The zen4-windows OpenBLAS (MAX_THREADS=24, different build) yields higher pinv precision.

**Falsifier**: A SkylakeX host with OpenBLAS 0.3.34.106.0 MAX_THREADS=64 matching zen4-wsl/aws pinv scores (~47.6/47.9), or a different architecture matching zen4-windows pinv score (~49.6).
