# Red-team report: agy on Gemini 4 Hydrogen

`agy --model gemini-4-hydrogen-high`, regular mode, 2026-11-15, on [redteam-brief.md](redteam-brief.md) at head `5f4a0e26e`. Paths are relative to this repository. The text below is the reviewer's answer, with absolute local paths and link syntax rewritten to repository-relative code spans.

# Red-team review: PR 931 (`5f4a0e26e`, Tuna-17 characterization case)

Ranked by operational and scientific consequence; no files modified, no provider/network/emulator runs executed.

## 1. Critical findings (ranked by consequence)

1. **`analyze()` crashes on dead qubits, emits invalid JSON `NaN`, drops CLI tolerance checks, and falsifies exponential fits (`computed`, `proved`)**
   - `ZeroDivisionError` crash: qi_tuna17_characterization_cases.py:350 (`scripts/qi_tuna17_characterization_cases.py#L350`) divides by `span` before checking `if span > 0.2` at `:352`; a single stuck qubit (`span == 0.0`) aborts all 17 rows.
   - Invalid JSON output: for `0 < span <= 0.2`, `:364,373` assigns `float("nan")`, serializing `NaN` via `json.dumps` (`analyze_q1_nan_in_json: True nan`, computed).
   - Disconnected `readout_within_tolerance`: CLI `--analyze` calls `analyze(args.analyze[1:])` with `retained=None` (qi_tuna17_characterization_cases.py:401 (`scripts/qi_tuna17_characterization_cases.py#L401`)), so `readout_within_tolerance` (`has_tol: False`) is never emitted in production, masked because test_qi_tuna17_characterization_cases.py:87 (`tests/scripts/test_qi_tuna17_characterization_cases.py#L87`) passes `retained` directly. Also, `:339-345` ignores opening-vs-closing bracket drift, which `:330-332` silently averages.
   - Zero-variance & flat-curve fit failure: `max(p * (1 - p), 1e-12)` (`:350`) gives `t1-0` at `p = 1.0` a `~1e16` weight when `readout-1 < 1.0`, biasing `T1=20 us` to `18.899 us` and failing `chi_square_probability` (`9.20e-6 < 0.01`, computed). Conversely, a non-decaying constant `p = 0.985` passes `t1_single_exponential = True` via floating-point noise (`length = 2.96e19`, `chi_square_probability = 1.0`, computed). Readout-pair variance and covariance across points are omitted, and `ladder_points` (`:368,285`) drops any point with `2*p0 - 1 <= 0.05` (`p0 <= 0.525`), discarding aliased/pi-inverted failures from the ladder fit.

2. **`sanity()` between batches cannot stop a failed, inverted, or collapsed run (`proved`, `computed`)**
   - qi_tuna17_characterization_cases.py:247-250 (`scripts/qi_tuna17_characterization_cases.py#L247-L250`) inspects outcomes only when `{"readout-0.cq", "readout-1.cq"} <= set(raw)`. Batches `01`–`04` lack readout files, so `sanity()` returns `[]` even for all-zero `t1-*` shots (`sanity_allzero_b1: []`, computed).
   - On `batch-00` and `batch-05`, `:249` checks only the 17-qubit means (`sum(zero)/17 > 0.2` or `sum(one)/17 < 0.8`), so bit-reversed outputs pass (`sanity_bitrev_b0: []`) and historical per-qubit collapse (`q9 P(1|0)=0.28`, `q0 P(1|1)=0.565`, `q6 P(1|1)=0.163`, tuna-17.md:33-42 (`docs/notes/quantum_inspire/tuna-17.md#L33-L42`)) passes (`sanity_collapse_b0: []`, computed), wasting all 5 remaining batches.

3. **Unchecked 4,352-gate `x90-64.cq` queue/rejection risk and 17-qubit simultaneous physics confounds (`proved`, `measured`, `hypothesis`)**
   - Operation-count waste risk: `batch-04/x90-64.cq` is `4360` lines (`4352` `X90` gates), `6.26x` longer than the longest retained Tuna-17 circuit (`696` lines in `latin-3.cq`, measured via `wc -l`). kbase_hardware-backends.md:44 (`docs/notes/quantum_inspire/site/kbase_hardware-backends.md#L44`) warns individual backends reject jobs exceeding an undocumented operation cap; a `batch-04` rejection orphans `batch-00`–`batch-03` spend/queue.
   - Compiler fusion vs aliasing (`hypothesis`): backends_transmons.md:103 (`docs/notes/quantum_inspire/site/backends_transmons.md#L103`) documents server-side OpenSquirrel "merging of single-qubit rotations" downstream of client-visible `default_compiler_config` (catalogue.json:1077-1093 (`docs/evidence/quantum_inspire/catalogue.json#L1077-L1093`)). If fused, `x90-64` measures zero physical pulses; if unfused, coherent error wraps `cos^2(256*e/2)` modulo `pi` (aliasing bad `X90` angles back above `LADDER_MIN_P0 = 0.5`). Pure depolarizing/T1 relaxation also satisfies `p0 >= 0.5` asymptotically.
   - Simultaneous 17-qubit crosstalk & context bias (`measured` in retained records): driving all 17 qubits simultaneously triggers documented `Q1`/`Q2` crosstalk (`Q2` P1 after `40 X` jumps `0.046 -> 0.893` with partner, and `Q6/Q8/Q9` reach `0.717/0.764/0.883`, experiments.md:105-115 (`docs/notes/quantum_inspire/experiments.md#L105-L115`)) and neighbor-dependent assignment (`q13` `e10` doubles from `0.044` isolated to `0.090` in all-17 `readout-1`, tuna-17.md:184-194 (`docs/notes/quantum_inspire/tuna-17.md#L184-L194`)), so `readout-1` over-corrects late `t1-N` tails as neighbors decay toward `|0>`.
   - Unmodeled state-prep / leakage / between-batch drift: `readout-1` and `t1-N` start with `X q[q]` (`:80`), confounding `|1>` prep failure/leakage with `T1` intercept; short-T1 qubits (`Q9=5.14 us`, `Q6=5.50 us`, `Q15=6.27 us` in `retained-context.json`, computed) retain only 3 points `[0.0, 5.0, 10.0]` (`df=1`) above `POPULATION_FLOOR=0.05` (`T1 < 3.34 us` returns `None`); splitting `t1` across `batch-01`/`batch-02` exposes the curve to queue delays (`med_turn` `57.1s–2257.0s`), calibration pauses (tuna-17.md:50-54 (`docs/notes/quantum_inspire/tuna-17.md#L50-L54`)), and 50 Hz mains drift (`±0.02` between batches gives `chi_square=13.73/15.73`, `p=0.0033/0.0013 < 0.01`, computed).

4. **CI seed-provenance break and `CASE.md` overstatements (`proved`)**
   - Unledgred test seed: test_qi_tuna17_characterization_cases.py:62 (`tests/scripts/test_qi_tuna17_characterization_cases.py#L62`) uses `random.Random(20261115)`, which ci/seed_provenance.py:3,12-14 (`ci/seed_provenance.py#L3-L14`) scans under `tests/`, yet `rg -n "20261115" ci/reproduction_seeds.json docs/evidence/qrng_seeds/allocations.json` finds no entry.
   - Unsupported `"500,000"` quota claim: CASE.md:50 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md#L50`) ("against the provider's 500,000"), tuna17-characterization-case-draft.md:55 (`docs/notes/quantum_inspire/tuna17-characterization-case-draft.md#L55`), and test_qi_tuna17_characterization_cases.py:24 (`tests/scripts/test_qi_tuna17_characterization_cases.py#L24`) invent a `500,000` per-qubit limit absent from `catalogue.json` (`max_number_of_shots: 131072`) and all QI docs (`rg -n "500,?000" docs/notes/quantum_inspire docs/evidence/quantum_inspire` hits only draft line 55).
   - Broken downstream claim: CASE.md:96-98 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md#L96-L98`) states `--analyze` rows enter `scripts/qi_retained_context.py`'s inputs, whereas qi_retained_context.py:39 (`scripts/qi_retained_context.py#L39`) reads `readout_ringdown_tuna_17_device_context.json`, not `qi-tuna17-characterization-analysis-v1`. CASE.md:91-92 (`results/quantum_inspire/cases/characterization_tuna_17/CASE.md#L91-L92`) also assumes ZZ moves no population despite neighbor `X` drive crosstalk (`experiments.md:107-108`) and state-dependent readout (`tuna-17.md:184-194`).

## 2. Verdicts on Claims 1–9

| Claim | Verdict | Basis & key evidence |
|---|---|---|
| 1. No submit/read account | **Justified (`proved`)** | Stdlib imports only (`:33-39`); `qxelarator` lazy-imported only in `local()` (`:212`); `main()` (`:386-406`) has zero HTTP/account/cancel/submit calls. |
| 2. Provider limits & counts | **Partial (`proved` / `falsified`)** | Batch size `<=3` (`:93`, qi_platform.py:81 (`scripts/qi_platform.py#L81`)), 14 jobs, 147,456 shots, max 16,384 <= 131,072 (catalogue.json:1129 (`docs/evidence/quantum_inspire/catalogue.json#L1129`)) **proved**. `"500,000"` limit (`CASE.md:50`) **falsified** (absent from API/docs). |
| 3. `expected_seconds()` = 115.8 s | **Verified (`computed` / `measured`)** | `expected_seconds` gives `tuna_17: 115.8`, `qx: 44.2`, max job `11.284s` << `300s` (`computed`, ignores `x90` gate time). Retained `med_exec` matches within `0.73x–1.33x` (`measured`), but queue `med_turn` (`57.1–2257s`) + 5 pauses (`qi_platform.py:90`) dominate wall time. |
| 4. Circuits & outcome | **Justified (`proved`) + `hypothesis`** | Circuit text (`:67-85`) and `bit()` (`:198-199`, `batch-00/cases.json:7`) **proved**; 28/28 `ok` in `toolchain-token-recovery.json`. Unfused 256-pulse execution on device remains unverified `hypothesis` (backends_transmons.md:103 (`docs/notes/quantum_inspire/site/backends_transmons.md#L103`)). |
| 5. `analyze()` math & verdicts | **Falsified (`computed`, `proved`)** | `chi_square_probability` (`:252-280`) accurate (`<=3.56e-14`), but `analyze()` has `ZeroDivisionError` at `span=0`, `NaN` JSON at `span<=0.2`, missing CLI `retained`, `1e16` zero-variance weight spike, flat-curve pass, and `ladder_points` dropping `p0<=0.525`. |
| 6. `sanity()` stops bad series | **Falsified (`computed`, `proved`)** | Skips `batch-01`–`04` shot checks (`[]` on all-zero `batch-01`) and averages qubits on `00`/`05` (`[]` on bit-reversed shots and 2026-10-17 `q0/q6/q9` collapse). |
| 7. `--check` byte-for-byte | **Justified (`computed`) with gap** | `check(repo / "results/quantum_inspire/cases")` returns `[]`, deterministic over 22 generated files/profile, but excludes `CASE.md` (`:194`) so doc numbers can drift undetected. |
| 8. Thresholds falsifiable | **Falsified (`computed`, `measured`)** | Three retained qubits leave only 3 T1 points (`df=1`); `±0.02` inter-batch drift fails `p>=0.01`; `LADDER_MIN_P0=0.5` aliases over-rotations and never catches depolarizing/T1 decay; `readout_tolerance=0.03` compares against month-old `2026-10-17` rows. |
| 9. No random seed / QRNG rule | **Falsified in PR (`proved`)** | Generator script uses no RNG (`proved`), **but** test_qi_tuna17_characterization_cases.py:62 (`tests/scripts/test_qi_tuna17_characterization_cases.py#L62`) adds unledgred `random.Random(20261115)` scanned by `ci/seed_provenance.py`. |

## 3. Command evidence (read-only `/tmp` pure-Python checks)

```text
check(): []
expected_seconds: {'tuna_17': 115.8, 'qx': 44.2}
max_job_sec: ('readout-0.cq', 11.284)
retained_min_t1: (5.14269, 9)
retained_3pt_qubits: {6: (5.49741, [0.0, 5.0, 10.0]), 9: (5.14269, [0.0, 5.0, 10.0]), 15: (6.27035, [0.0, 5.0, 10.0])}
sanity_collapse_b0: []   sanity_bitrev_b0: []   sanity_allzero_b1: []
analyze_q0_zero_var: {'us': 18.8990944910018, ..., 'chi_square': 26.0751751423421, 'chi_square_probability': 9.197923999347322e-06} False has_tol: False
analyze_q1_nan_in_json: True nan
const_lt1 (p=0.985): {'points': 6, 'chi_square': 2.660845791480765e-30, 'freedom': 4, 'chi_square_probability': 1.0, 'length': 2.9618554288875016e+19, ...}
drift_+0.020: {'points': 5, 'chi_square': 13.728452539422433, 'freedom': 3, 'chi_square_probability': 0.0032990735022309166, 'length': 20.891217391447054, ...}
```
