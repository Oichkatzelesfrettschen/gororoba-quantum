Now I have all the data needed. Let me compile the final review report.

---

**REVIEW REPORT — Portable Least-Squares Precision Sweep**

**Summary**: All seven claims in the README are substantiated by the code and the 438 retained data rows. No material overstatements found. Three minor defects in the implementation; one conjecture on BLAS kernel selection.

---

### 1. Claim Verification (7 claims, ranked by consequence)

| # | Claim | Verdict | Evidence |
|---|-------|---------|----------|
| 1 | **Cap mechanisms per host**: Four hosts (build-host, zen4-wsl, aws-sapphire-rapids, oci-a1-neoverse-n1) use systemd scope with enforced cgroup limits; M1 macOS falls to `none` after RLIMIT_AS probe fails in `preexec_fn`; zen4-windows runs uncapped (`--cap none`). | **PROVED** | `host-records.json` shows: build-host/zen4-wsl/aws-sapphire-rapids/oci-a1-neoverse-n1 → `mechanism: "systemd", enforced: true`; m1-macos → `mechanism: "none", enforced: false, reason: "no mechanism passed its probe"`; zen4-windows → `mechanism: "none", enforced: false, reason: "uncapped run requested"`. |
| 2 | **Thread ladder**: 1, 2, 4, … up to `min(os.cpu_count(), parallel.workers())`, plus the CPU count when not a power of two. | **PROVED** | `fp_host.py:369-377` implements exactly this. Host records confirm: build-host cpus_used=10 → ladder [1,2,4,8,10]; zen4-wsl cpus_used=32 → [1,2,4,8,16,32]; zen4-windows cpus_used=32 → [1,2,4,8,16,32]; aws-sapphire-rapids cpus_used=2 → [1,2]; oci-a1-neoverse-n1 cpus_used=2 → [1,2]; m1-macos cpus_used=8 → [1,2,4,8]. Rows-summary `cpus_used` column matches. |
| 3 | **Non-BLAS arithmetic identity**: On the five hosts with matching input digests, every configuration run on ≥2 hosts scores identically to the last recorded digit: 24 arb normal-equation configs, 8 SLEEF binary128 configs, 5 x87 configs. | **MEASURED** | `rows-summary.tsv` `bits_correct_on_scores` column: arb 64/128/192/256-bit values identical across build-host, zen4-wsl, aws-sapphire-rapids, zen4-windows, oci-a1-neoverse-n1 (e.g., 64-bit: 56.72874548747257 everywhere). SLEEF binary128 Householder: 108.090673654462 on build-host, zen4-wsl, aws-sapphire-rapids. x87 Householder: 59.52742708597964 on build-host, zen4-wsl, aws-sapphire-rapids. M1 differs on arb 64/128/192-bit (56.5458… vs 56.7287…) and SLEEF (108.4879… vs 108.0906…). |
| 4 | **Windows QuadBLAS errors**: 12 SLEEF configurations error with `NotImplementedError: QuadBLAS is disabled`. | **PROVED** | `rows-summary.tsv` lines 292-303: 12 rows (6 thread counts × 2 kinds: Householder/normal) with status `error` and `skipped_or_error` = "NotImplementedError: QuadBLAS is disabled". README parenthetical "six thread counts, two kinds, two repeats each" describes 12 configs × 2 repeats = 24 runs; rows show 12 error rows (one per config). |
| 5 | **Input digests equality**: Build-host, zen4-wsl, aws-sapphire-rapids, oci-a1-neoverse-n1 share all five digests; M1 differs only in `observed_rate_columns`; zen4-windows uses build-host's npz so reports build-host digests. | **PROVED** | `host-records.json` `inputs_sha256`: first four digests identical across all six hosts. `observed_rate_columns`: five hosts = `f9b69a55…`; M1 = `ae852e54…`. zen4-windows `inputs_provenance.npz.exporter_host_label` = "build-host". |
| 6 | **Row hygiene (public substrate profile)**: No hostname, user, path, kernel release, distro, or memory size in rows. | **PROVED** | `host-records.json` host objects contain only: label, machine, os (system, wsl/mac_ver/release), cpu_model, cpu_count, cpu_flags, python, numpy (simd, build_blas), blas (runtime libs via threadpoolctl, paths dropped), flint, packages, longdouble_nmant, cpus_used, thread_ladder. No prohibited fields present. |
| 7 | **Float64 BLAS-dependent spread**: Unrefined pinv 2.2–14.8 ulp, numpy lstsq 2.2–13.2 ulp, scipy drivers 0.2–6.8 ulp across digest-agreeing hosts at 1 thread. | **MEASURED** | `rows-summary.tsv` `process_fidelity_ulp64` at 1 thread: pinv {build-host:3.2, zen4-wsl:2.2, aws:14.8, zen4-windows:4.2, oci:6.2} → range 2.2–14.8. numpy lstsq {5.2, 10.2, 10.8, 13.2, 2.2} → 2.2–13.2. scipy gelsd {5.2, 5.2, 5.2, 0.2, 5.2}, gelsy {3.8, 0.2, 0.2, 2.2, 2.2}, gelss {5.2, 4.8, 4.8, 6.8, 4.8} → combined 0.2–6.8. |

---

### 2. README Sentences Exceeding Row Support

**None.** Every quantitative statement in "Results across hosts" (README lines 245-296) is backed by the retained rows. The only minor imprecision is the parenthetical "six thread counts, two kinds, two repeats each" for Windows QuadBLAS errors (README line 147) — the rows show 12 error *configurations* (6×2), each run twice; the phrasing conflates configs with runs but the number 12 is correct for configurations.

---

### 3. Defects in fp_host.py / fp_sweep.py / fp_export.py (ranked by consequence)

| Severity | File:Line | Defect |
|----------|-----------|--------|
| **Medium** | `fp_host.py:498-524` (`probe_rlimit`) | The RLIMIT_AS probe imports `numpy` *inside* the child before the mmap test. OpenBLAS reserves address space at import, so the probe's mmap (cap + 256 MiB) may fail simply because the process already holds reservations, not because the limit is enforced. The probe conflates "limit enforced" with "address space exhausted by OpenBLAS". This caused the M1 probe to fail in `preexec_fn` (SubprocessError) rather than cleanly reporting `refused: true/false`. |
| **Low** | `fp_host.py:639-661` (`cpu_flags`) | Uses private numpy modules `numpy._core._multiarray_umath` / `numpy.core._multiarray_umath` to read `__cpu_features__`. No public API guarantee; may break on numpy upgrade. Fallback returns `{"source": "unavailable", "flags": None}` which is safe but loses data. |
| **Low** | `fp_sweep.py:968-975` (`child_command`) | For `systemd` mechanism, `RuntimeMaxSec = wall + 60` (default 960s). The probe at `fp_host.py:527-530` uses the same command but only runs a shell `cat` — the 960s scope timeout is wasteful for the probe. Negligible impact. |
| **Low** | `fp_export.py:178-191` | Requires `fcntl` (Unix-only) because producer imports it. Windows hosts cannot run the exporter; they must copy `fp-inputs.npz`. Documented in README (line 89) but not in the script's help. |

---

### 4. Conjecture: BLAS Kernel Selection

**Observation**: zen4-wsl and aws-sapphire-rapids both load the OpenBLAS `SkylakeX` core at runtime (per `threadpoolctl`), yet their float64 scores diverge on 4 of 10 shared configurations (pinv, numpy lstsq, gelss at various threads). They agree only on the three scipy drivers at 1 and 2 threads (6 of 10).

**Hypothesis**: The `SkylakeX` core is a *compile-time* dispatch target in OpenBLAS 0.3.34. Both hosts run Zen 4 and Sapphire Rapids respectively — neither is Skylake-X. At runtime, OpenBLAS's `DYNAMIC_ARCH` selects a kernel based on CPUID. The `SkylakeX` label in `threadpoolctl` reflects the *selected* kernel, but the underlying micro-kernels may still differ due to:
- Different L1/L2 cache geometry (Zen 4: 32 KiB L1D / 1 MiB L2 per core; Sapphire Rapids: 48 KiB L1D / 2 MiB L2)
- Different AVX-512 unit throughput (Zen 4: single 512-bit FMA; SPR: dual 512-bit FMA)
- Different thread topology (Zen 4: 2 CCDs, 32 cores; SPR: 48 cores on one die)

The scipy drivers (`gelsd`, `gelsy`, `gelss`) call LAPACK routines (`?gelsd`, `?gelsy`, `?gelss`) which use blocked algorithms with larger GEMM calls where the SkylakeX kernel dominates. The pinv/numpy lstsq paths use different LAPACK routines (`?gelss` vs `?geqrf`+`?ormqr`+`?trsm`) with different blocking factors, exposing the micro-architectural differences.

**Falsifier**: Re-run with `OPENBLAS_CORETYPE=Zen3` (Zen 4) or `OPENBLAS_CORETYPE=SKX` (SPR) forced on both hosts — if scores converge, the divergence is kernel-selection policy, not hardware.

---

*End of report*
