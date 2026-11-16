# Red-team report: agy on Gemini 3.8 Flash

`agy --model gemini-3.8-flash-high`, regular mode, 2026-11-15, on [redteam-brief.md](redteam-brief.md) at head `5f4a0e26e`. Paths are relative to this repository. The text below is the reviewer's answer, with absolute local paths and link syntax rewritten to repository-relative code spans.

### Claims Under Review

1. **Claim 1 (No provider calls in generator): JUSTIFIED** [proved]
   Inspection of `scripts/qi_tuna17_characterization_cases.py:33-40` confirms imports are confined to standard modules (`argparse`, `hashlib`, `json`, `math`, `sys`, `pathlib`, `typing`) plus a lazy `qxelarator` import in `local()`. No network clients, credentials, or submission hooks exist.

2. **Claim 2 (Provider and batch limits): JUSTIFIED** [computed]
   `batches()` emits 6 batches of sizes `[2, 3, 3, 2, 2, 2]` ($\le 3$). Total circuits = 14; shots = $4 \times 16,384 + 10 \times 8,192 = 147,456$. Maximum shots per job is 16,384 ($< 131,072$ limit); measurements per qubit per job is 16,384 ($< 500,000$). Verified by `test_series_respects_batch_and_measurement_limits`.

3. **Claim 3 (Expected execution seconds): JUSTIFIED** [computed]
   Recomputed via `expected_seconds()`: $14 \times 2.6\,\text{s} + 45.134\,\text{s}$ (readouts) $+ 42.920\,\text{s}$ (T1 including waits) $+ 27.767\,\text{s}$ (ladder) $= 115.821\,\text{s} \approx 115.8\,\text{s}$. Retained median Tuna-17 execution times in `retained-context.json:106-128` (11.09 s at 16k shots, 72.31 s at 131k shots) match the model parameters ($2.6\,\text{s} + 0.53\,\text{ms/shot}$).

4. **Claim 4 (Circuit specifications and noiseless outcomes): JUSTIFIED** [proved]
   Inspection of `circuits()`: `readout-0` has no gates ($|0\rangle^{\otimes 17}$); `readout-1` applies $X^{\otimes 17}$ ($|1\rangle^{\otimes 17}$); `t1-N` applies $X^{\otimes 17}$ followed by `wait(N)` (noiseless $|1\rangle^{\otimes 17}$); `x90-K` applies $4K$ pulses of $X90$ ($2\pi K$ total rotation, noiseless $|0\rangle^{\otimes 17}$). All terminate on `barrier q` and `b = measure q`.

5. **Claim 5 (Analysis estimator and verdicts): FALSIFIED** [proved]
   - CLI invocation (`qi_tuna17_characterization_cases.py:401`) calls `analyze(args.analyze[1:])` with `retained=None`. Lines 339–345 never execute, silently dropping the `readout_within_tolerance` verdict from the JSON output.
   - For qubits with $T_1 \sim 5\,\mu\text{s}$ (Q6, Q9), points with wait $\ge 20\,\mu\text{s}$ fall below `POPULATION_FLOOR` (0.05). If $<3$ points survive, `decay_fit()` returns `None`, silently omitting $T_1$ and $T_1$ single-exponential verdicts without warning.

6. **Claim 6 (Sanity checks between batches): FALSIFIED** [proved]
   - In `qi_tuna17_characterization_cases.py:247`, data separation is gated by `if not problems and {"readout-0.cq", "readout-1.cq"} <= set(raw):`. For Batches 01, 02, 03, and 04, this evaluates to `False`. `sanity()` performs zero validation on measurement data for these batches. If Batch 01 (e.g. `t1-0`, which has zero wait) returns all zeros, `sanity()` exits 0 and allows subsequent batches to submit.
   - In Batch 00, `sanity()` checks only `sum(zero)/len(zero) > 0.2` and `sum(one)/len(one) < 0.8` (lines 248–250). Symmetrically summing across all 17 qubits is completely invariant to bit-order reversals.

7. **Claim 7 (--check byte-for-byte reproduction): JUSTIFIED** [measured]
   `python3 scripts/qi_tuna17_characterization_cases.py --check results/quantum_inspire/cases` exits 0 with no differences. Tracked files match generator outputs, and `CASE.md` is explicitly exempted.

8. **Claim 8 (Pre-registered thresholds and falsifiability): JUSTIFIED** [proved]
   Thresholds are hardcoded constants in `prediction.json`. Degraded readout ($>0.03$), non-exponential decay ($p < 0.01$), or low ladder transmission ($P(0) < 0.5$) trip the criteria. (Caveat: CLI `--analyze` fails to evaluate readout tolerance due to Claim 5).

9. **Claim 9 (No random seeds / QRNG rule): FALSIFIED** [measured]
   `tests/scripts/test_qi_tuna17_characterization_cases.py:62` invokes `rng = random.Random(20261115)`. Command `python3 ci/seed_provenance.py --check` fails with exit code 1:
   `tests/scripts/test_qi_tuna17_characterization_cases.py: seed Random=20261115 appears 1 times, 0 accounted; draw it from a QRNG source...`

---

### Red-Team Findings (Ranked by Consequence)

1. **Gate Blocker: Unregistered PRNG seed breaks CI gate** [measured]
   - **Path**: `tests/scripts/test_qi_tuna17_characterization_cases.py:62`
   - **Mechanism**: Hardcoded seed `random.Random(20261115)` violates the root `AGENTS.md` ("Seeds") ledger requirement.
   - **Evidence**: `python3 ci/seed_provenance.py --check` exits with code 1. The PR will fail the required `tests` CI admission check.

2. **Provider Waste: `sanity()` does no outcome checks on Batches 01–04** [proved]
   - **Path**: `scripts/qi_tuna17_characterization_cases.py:247-251`
   - **Mechanism**: The outcome check requires both `readout-0.cq` and `readout-1.cq` in the batch directory. Batches 01, 02, 03, and 04 contain only $T_1$ or $X90$ circuits.
   - **Consequence**: If hardware fails or state preparation crashes during Batch 01 (e.g. `t1-0` returns all 0s), `sanity()` checks only `job.status == 'completed'` and `shots_done`, passes cleanly, and proceeds to submit Batches 02, 03, 04, and 05, wasting queue priority, device time, and pause allocations.

3. **Defective Reporting: CLI `--analyze` drops readout tolerance verdict** [proved]
   - **Path**: `scripts/qi_tuna17_characterization_cases.py:339-345, 401`
   - **Mechanism**: `main()` calls `analyze(args.analyze[1:])` with `retained=None`. The function never loads `retained-context.json`.
   - **Consequence**: `row["readout_within_tolerance"]` is never written to output JSON, contradicting CASE.md and `prediction.json`.

4. **Confounded Physics: Simultaneous 17-qubit drive crosstalk in 256-pulse ladder** [hypothesis]
   - **Path**: `results/quantum_inspire/cases/characterization_tuna_17/CASE.md:16-18, 88-90`
   - **Mechanism**: Applying 256 consecutive $X90$ pulses to all 17 qubits simultaneously (5.12 $\mu\text{s}$) generates massive AC Stark shifts and microwave spectator-drive crosstalk (measured in `experiments.md:86-90` up to 0.63 rad in 800 ns).
   - **Consequence**: Attributing ladder decay solely to single-qubit coherent over-rotation or intrinsic decoherence overstates what parallel driving can isolate. There is no isolated single-qubit control arm.

5. **Design Blindspot: Delay grid discards Batch 02 on short-$T_1$ qubits** [computed]
   - **Path**: `scripts/qi_tuna17_characterization_cases.py:44, 285`
   - **Mechanism**: `retained-context.json:196-225` records Q6 ($T_1 \approx 5.5\,\mu\text{s}$) and Q9 ($T_1 \approx 5.1\,\mu\text{s}$). For $T_1 = 5.14\,\mu\text{s}$, populations at 20, 40, and 80 $\mu\text{s}$ are $0.020, 0.0004, 10^{-7}$, all $< \text{POPULATION\_FLOOR}$ (0.05).
   - **Consequence**: All three circuits in Batch 02 (`t1-1000`, `t1-2000`, `t1-4000`) are dropped from the fit for these qubits. Only 3 points survive ($\text{d.o.f.} = 1$), eliminating statistical power to detect multi-rate or non-exponential decay. If $T_1 \le 3.3\,\mu\text{s}$, $<3$ points remain and $T_1$ fitting is skipped silently.

6. **Unbounded Drift: Averaged readout ignores intra-series drift** [proved]
   - **Path**: `scripts/qi_tuna17_characterization_cases.py:330-345`
   - **Mechanism**: `zero` and `one` are unweighted averages of Batch 00 and Batch 05. `readout_within_tolerance` compares only the closing pair (`readouts[-1]`) against month-old retained data, never comparing `readouts[-1]` against `readouts[0]`.
   - **Consequence**: Drift occurring across the 6 batches and 5 hardware pauses is neither bounded nor alerted by the verdicts.

7. **False Ladder Verdict on Partial Collections** [proved]
   - **Path**: `scripts/qi_tuna17_characterization_cases.py:372-374`
   - **Mechanism**: `ladder_clears` is evaluated at `max(ladder_raw)`. If Batch 04 is missing, `max(ladder_raw)` is 32 pulses.
   - **Consequence**: `analyze()` marks `ladder_clears: True` based on 32 pulses rather than the preregistered 256-pulse requirement.
