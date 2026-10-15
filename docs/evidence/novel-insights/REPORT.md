# Novel-insights hunt: handoff report (2026-10-15)

## Ranked insights

### #1 (SOLID): Unmodeled quasi-static detuning ~20–40 kHz on both Heron devices — one mechanism behind two "separate" open items

**What it is.** The N21 orbit phases (Fez, "model-dependent fit parameters") and the Kingston
coherence-window drift (−1.130 rad, "directly measured") are the same phenomenon: idle qubits
accrue 20–40 kHz of phase that no calibration reports.

**Numbers.**
- Kingston (`2026-10-15T030748.903241Z/coherence-analysis.json`): matched idle adds 4.392 µs
  exposure; argument rotates −1.130 rad → **0.257 rad/µs = 40.9 kHz**.
- **New from existing strata (not remarked in any doc):** the idle rotation is
  branch-INDEPENDENT. b0=0: −1.133−(−0.011) = **−1.122 rad**; b0=1: 1.981−3.123 = **−1.142 rad**
  (CIs overlap). This rules out ZZ coupling to the branch qubit and any branch-dependent
  mechanism — the source is a spectator in a fixed state or the work qubit's own frame detuning.
- Fez N21 (`N21_ORBIT_RCA.md`): nominal phase +0.59 rad over mean window idle 1187 dt
  (4.75 µs at 4 ns/dt) → **0.124 rad/µs = 19.8 kHz**; repeat +0.70 → 23.5 kHz.
- Echo arm: 0.17 rad residual with qubit 136 fully refocused and 144 keeping 532 dt
  (2.13 µs) unrefocused → 12.7 kHz on the unrefocused portion — the residual scales with
  unrefocused idle, as quasi-static detuning predicts. (Caveat: the window_delay arm gives
  only 10.2 kHz, but that arm carries extra decoherence the fit may misattribute.)
- Calibration is structurally blind here: backend properties report no qubit frequency, and
  IBM's T2 is Hahn-echo (refocuses exactly this). The N21 doc's candidate 1 ("coherent
  exchange with spectator") is the same idea, but the two measurements were never connected.

**Confirm/refute.** Repeat the coherence window with the spectator patch in |0…0⟩ vs |1…1⟩:
ZZ predicts the rate changes sign/magnitude with spectator state; intrinsic frame detuning
predicts no change. Alternatively echo the work qubit mid-idle: full refocus ⇒ quasi-static.

**Cheapest follow-up.** Static-circuit Ramsey on the Kingston patch qubits (57/66/67/68),
sweeping idle 0–10 µs, spectators parked in |0⟩ then |1⟩. No orbit, no feed-forward, ~2 s of
QPU time. Also re-analyzes free: the fringe φ0 = +0.197 rad and V-loss may carry the same
detuning — check whether the fringe's 336-CZ circuit duration × 41 kHz predicts its
visibility deficit.

### #2 (SOLID): The ~11% first-bit disagreement is a quantum-state defect on qubit 79 — pure readout error ruled out by existing data

**What it is.** The correction runs' "first bit" (clbit 0, physical qubit 79, expected |1⟩)
reads 0 in ~11% of shots. The repo lists three candidate mechanisms (assignment, preparation,
evolution) as unresolved. The retained data resolves it further than the docs claim.

**Numbers** (recomputed from raw `pub_*.json` bitstrings + `analysis-*.json`, both runs).
- First-bit-0 rate is **identical across all 8 PUBs**: run 1: 11.01/10.96/11.00/10.33%;
  run 2: 11.10/11.56/10.63/10.64% — independent of label (s1/s3), correction mode
  (known/measured), and run. Label-dependent preparation/evolution is out.
- **Discriminator the docs missed:** in the KNOWN arms (correction ignores the measured bit),
  terminal success is 0.51–0.57 inside the first-bit-0 stratum vs 0.77–0.81 in the
  first-bit-1 stratum (both runs, both labels). Pure readout misassignment would leave the
  known-arm terminal rate at ~0.78 regardless of the misread bit. The gap proves the defect
  is in the **quantum state** (T1 decay / preparation loss on qubit 79), not the readout.
- Mechanism for the correlation: qubit 79 shares **28 CZs** with the terminal qubit 93
  (plus 13 with qubit 73) in the 70-CZ correction circuit (`isa.qpy`), so a decayed 79
  propagates through the entanglers and sinks the terminal measurement in every arm.

**Confirm/refute.** 0-CZ SPAM on qubit 79: prepare |1⟩, measure immediately vs after 16 µs
(the mid-circuit measurement time). Constant 11% ⇒ preparation defect; growing with delay
⇒ T1. (This narrows roadmap item 9's controls to a single-qubit experiment.)

**Cheapest follow-up.** The SPAM pair above, ~1024 shots each, negligible QPU cost. If T1,
qubit 79 wants exclusion from future dynamic circuits the way qubits 0/1 were excluded
after the corner baseline.

### #3 (PROPOSAL, needs new data): Hardware-test the exact census — 45.117% of sedenion triples are defective

**What it is.** The proved census (Theorem 1) gives N(16) = 1848 non-associating ordered
triples out of 16³ = 4096, i.e. **45.117%**. Every hardware experiment to date tests
*chosen* defective triples (implementation contrasts). Nothing tests the census *count*.

**Proposal.** Sample K≈1000 random ordered basis triples (a,b,c); for each, run both
bracketings (ab)c vs a(bc) through the existing algebra builders (PR #102) and read the
associator sign. Exact prediction: 45.1% ± 1.6% defective. A match turns the "finished
mathematics" into a hardware-verified statistical law; a mismatch would be the most
interesting possible result (it would mean the implementation doesn't faithfully realize
the algebra). D=8 (32.8%) and D=32 (48.7%) give two more rungs on the same ladder.

**Cost.** Simulation-first (free); hardware needs ~1000 shallow triple-product circuits,
packable into a few jobs under the existing budget pattern.

## Secondary anomalies (worth a look, lower confidence)

- **Mirror-twin overcorrection** (fringe): the mirror circuits have FEWER CZs than the
  witness (320 vs 336, `isa.qpy`) yet attenuate ⟨Z⟩ more (0.64 vs modeled 0.86). The excess
  is not gate count — compare coupler-level placement and scheduled durations.
- **Weak fringe replica** (qubits 138, 149–152, V = 0.447 vs pooled 0.678): tile-specific,
  unexplained; cross-check against that tile's calibration when available.
- **Scaffolding reframing** (from the parallel assessment: scaffolding confined to walk
  members): the depth-4 class-return null was retained on circuits from a different builder
  (~37 CZ atlas) — but any future re-run should still bind-then-optimize first, since the
  walk finding proved the pipeline can silently pad.

## Neglected-artifact inventory

- All 14 `results/live/*/collect.json` bundles are referenced in findings docs — none neglected.
- `isa.qpy` per-run circuits now mined (gate counts, layouts, measured-qubit mapping);
  full table in `isa_stats.json`. **Per-qubit calibration is NOT retained anywhere**
  (record.json keeps only medians + policy thresholds: max_readout_error 0.08, max_cz_error
  0.03) — the corner table's "reported readout error / T1" columns are unrecoverable from
  the repo, confirming the audit's flag.
- `docs/notes/` (157 files): overwhelmingly literature/source records; no unintegrated
  analysis found. `results/hw_estimate/`: fake-provider simulations and proof artifacts,
  no unanalyzed hardware data.
- **Exploitable gap:** the coherence strata (`b0=0`/`b0=1` arguments) already contained the
  branch-independence result above — the repo analyzed the pooled signed coherence but never
  differenced the strata. Other stratified analyses may hold similar free insights.

## Figures
- `fig1_detuning.png`: phase vs idle exposure across N21 arms + Kingston point (10–41 kHz band)
- `fig2_eleven_percent.png`: 11% uniformity across 8 PUBs + known-arm stratum gap
- `isa_stats.json`: per-circuit gate counts/depths for every retained isa.qpy
