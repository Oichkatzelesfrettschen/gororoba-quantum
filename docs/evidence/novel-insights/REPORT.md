# Cross-run observations: idle phase, the first-bit stratum and a census test

Three observations drawn from retained runs, each recomputed from the cited
artifact. Each carries a verdict on what it establishes. They are
exploratory: they were found after seeing the data, so the prospective tests
named here decide them.

## 1. Idle phase on two devices (exploratory hypothesis)

**Kingston coherence window** (`2026-10-15T030748.903241Z/coherence-analysis.json`):
- The matched idle adds 4.392 us of exposure and rotates the branch-signed
  coherence by -1.130 rad.
- The coherence is `rho_{01,10}` of the work pair: work_a on qubit 68 and
  work_b on qubit 66, with spectator 67 between them in |0>. It is an
  odd-sector coherence, so it winds at the detuning difference
  `omega_68 - omega_66`.
- The -1.130 rad is therefore a 40.9 kHz difference between the two work
  qubits, provided the phase does not wind by a further 2 pi during the
  idle. The analyzer keeps those winding alternatives open, so 40.9 kHz is the
  slowest consistent difference, not a measured single-qubit rate.
- The rotation is the same in both branch strata:
  - b0 = 0: -1.133 - (-0.011) = -1.122 rad;
  - b0 = 1: 1.981 - 3.122 = -1.141 rad.
- A Z Z coupling J between the work coherence and the branch bit would
  separate the strata by 2 J t. Interval arithmetic over the four argument
  regions (half-widths 0.092 to 0.108 rad) bounds `|J| <= 7.6 kHz` at this
  exposure. The bound holds if the two strata do not differ by whole extra
  turns; the arguments fix that difference only modulo 2 pi.

**Fez N21 orbit** (`N21_ORBIT_RCA.md`):
- The fitted phase of +0.59 rad over the 1187 dt mean feedback-arm idle
  corresponds to 19.8 kHz (23.5 kHz on the repeat). That too is a phase of
  the work superposition, so it combines the work qubits' detunings.
- The echo arm's +0.17 rad over 532 dt of unrefocused idle corresponds to
  12.7 kHz.
- The orbit law sees only the summed phase, so these rates assume the whole
  phase accrues on the idle window. They are scale estimates from a model
  fit.

**Verdict:** both observations fit quasi-static detuning differences of tens of kHz,
which backend properties do not report: Heron reports no qubit frequency, and
an echo-based T2 refocuses such detunings. They come from different devices,
qubits, days and circuits, so they show a recurring scale, not one
mechanism. The fringe gives a third view of that scale: across its eight
replicas the fitted phase spreads from -0.26 to +0.50 rad (standard deviation
0.24 rad) on a 42-CZ circuit, and the replica on the coherence-window patch
(47, 57, 66, 67, 68) reads +0.29, inside that spread
(`walk-control-scaffolding/exposure.json`).

**Test:** the conditional Ramsey design (`docs/notes/conditional_ramsey_hamiltonian.md`)
is this measurement. It gives `omega_A`, `omega_B` and `J` of one coupled
pair over a delay ladder that resolves winding to 1 MHz, and its falsifier
tests the static diagonal model. Work qubits 68 and 66 are not coupled to
each other; both couple to spectator 67. Runs on the pairs (68, 67) and
(66, 67) therefore give both work detunings, the spectator's, and each
work-spectator J. Together they predict the window's rotation rate as
`nu_68|67=0 - nu_66|67=0`, and so test whether the -1.130 rad is a frame
detuning difference.

## 2. The first-bit stratum is not state-independent assignment (exploratory, sharpened)

Both correction runs record the first bit (clbit 0, physical qubit 79) as 0
in 10.3 to 11.6 percent of shots, in all eight PUBs, both labels and both
arms. Qubit 79 shares 28 CZ with the terminal qubit 93 and 13 with qubit 73
in the 70-CZ circuit.

In the known-label arms, where the correction ignores the recorded bit,
terminal success is 0.540 and 0.567 when the first bit reads 0, against 0.804
and 0.806 when it reads 1 (first run; `analysis-1fdb68508f14.json`). An
assignment error that leaves the state untouched cannot change what the
known arm does next. An assignment error that is also independent of
everything else in the shot would therefore leave the two strata equal.

The strata differ, so the recorded bit is correlated with terminal success.
Two kinds of cause remain:

- a real change of qubit 79's state (preparation, relaxation before readout,
  or a measurement that flips the state);
- a common cause that both misreads 79 and degrades the terminal result,
  while 79's state is preserved.

Assume the second contributes nothing, so that misread shots succeed like
recorded-1 shots. A fraction f of recorded-0 shots with a real state change
of terminal success s0 then gives

    0.54 = f s0 + (1 - f) 0.80,   so   f >= 0.33 for any s0 >= 0.

That bound holds only under the assumption; the counts alone do not establish
it.

**Verdict:** independent, state-preserving assignment error is excluded. A
state change of qubit 79 and a correlated common cause remain, and the
strata stay descriptive, as `correction_statistics.py` records them.

**Test:** read qubit 79 prepared in |1> immediately and after the
mid-circuit-measurement delay. A constant rate points to preparation, and a
rate that grows with delay points to relaxation. The run is a 0-CZ pair, and
it refines `proposed-first-bit-readout-controls`.

## 3. A hardware test of the census frequency (proposal)

The census gives 1848 of the 4096 ordered sedenion basis triples as
non-associating (231/512 = 45.117 percent), and the same law gives 168/512 at
D = 8 and 15960/32768 at D = 32. A hardware associator witness on uniformly
sampled triples reads
`P(c = 1) = 1/2 - V (1/2 - 231/512)`, where V is the witness visibility on
that hardware. It therefore tests how faithfully the implementation carries
the sign function, not the theorem, which is already proved. It needs bright
and dark reference triples to fix V, and per-triple circuits must avoid the
shared-template scaffolding of section 1 of the walk audit.

## Corrections to the original report

- **Per-qubit calibration** is retained: every `record.json` carries
  `placed_qubit_calibration` (T1, T2, readout error and both flip
  probabilities) for each placed qubit.
- **Corner table rows are not transposed.** The `qubit_baseline` summary
  keys `q0` to `q5` index classical bits, and the corner run's clbit-to-qubit
  map is 0 -> 1, 1 -> 0, 2 -> 16, 3 -> 4, 4 -> 2, 5 -> 3. Read by physical
  qubit, `ZERO_DIVISOR_AND_CORNER_FINDINGS.md` is correct.
- **The fringe's 336 CZ** are eight replicas of 42 run in parallel, so no
  circuit duration of 336 CZ enters its phase.
- **The -1.130 rad rotation** is a measured rotation, not a dephasing drift;
  the dephasing-drift wording is a withdrawn claim.

## Files

- `fig1_detuning.png`: phase against idle exposure for the N21 arms and the
  Kingston point.
- `fig2_eleven_percent.png`: the first-bit rate across the eight PUBs and the
  known-arm stratum gap.
- `isa_stats.json`: per-circuit gate counts and depths of the retained
  `isa.qpy` files. These are whole fused PUBs. Per-member counts are in
  `walk-control-scaffolding/exposure.json`.
