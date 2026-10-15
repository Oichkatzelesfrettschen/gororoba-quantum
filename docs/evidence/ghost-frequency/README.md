# Idle-phase campaign design, audited against the retained data

The three notebooks here simulate Ramsey designs for the idle phase seen in
two retained runs. They test three hypotheses: no detuning (H0), a
quasi-static detuning (H1), and an AC Stark shift from residual resonator
photons (H2). This README states what the retained data already settle
before any of these designs spends QPU time. Every QPU run still needs the
owner's approval of a written case.

## The observations, read correctly

- **Kingston coherence window** (`results/live/2026-10-15T030748.903241Z`).
  - The matched idle rotates the work pair's branch-signed coherence by
    -1.130 rad over 4.392 us.
  - That coherence is `rho_{01,10}` of work qubits 68 and 66, an odd-sector
    coherence, so it winds at the difference `omega_68 - omega_66`. The 40.9
    kHz figure is a detuning difference between two qubits, not one qubit's
    detuning, and a 2 pi winding alternative remains.
  - The rotation is the same in both branch strata (-1.122 and -1.141 rad).
- **Fez N21 orbit** (`results/live/N21_ORBIT_RCA.md`). A model-fit phase of
  +0.59 rad over a 4.75 us mean idle, which also combines work-qubit
  detunings.

These are two devices, different qubits, different circuits and different
days. They show a recurring scale of tens of kHz, which backend properties
do not report: there is no reported qubit frequency, and an echo-based T2
refocuses quasi-static detuning. They do not show one effect common to all
qubits, and nothing here points beyond ordinary transmon physics: frequency
drift, two-level-system coupling, Stark shifts and Z Z.

## What the retained data already decide

- **H2 for the coherence window is disfavored.** A residual-photon Stark
  shift needs a recent readout. In the matched-idle context nothing is
  measured before the idle, and the previous shot's readout lies a 250 us
  repetition delay back, yet the rotation is present. Adding a mid-circuit
  measure and reset changes it by only +0.054 rad. H2 can still apply to
  windows that follow a mid-circuit readout, such as the N21 orbit's.
- **A sign-blind estimator cannot resolve the sign.** The power analysis
  estimates the phase as `arccos(2 p - 1)`, which cannot tell +delta from
  -delta. The conditional Ramsey design reads both X and Y quadratures and
  avoids this.
- **The budget was misstated.** The service inventory observed at
  2026-10-15T07:13Z reports 334 of 600 s consumed, 266 s remaining, and
  nothing has run since, not about 120 s.

## Where the designs go

- **A pairwise test of the window rotation.** Conditional Ramsey on the
  coupled pairs (68, 67) and (66, 67) (`docs/notes/conditional_ramsey_hamiltonian.md`)
  measures both work detunings, the spectator's, and each work-spectator Z Z.
  It predicts the window rate as `nu_68|67=0 - nu_66|67=0` and resolves
  winding to 1 MHz. It covers the spectator |0>/|1> comparison of the
  original Experiment A on the qubits that matter.
- **The pre-delay discriminator.** A variable delay between a mid-circuit
  readout and the Ramsey idle separates H2 from H1 where a readout precedes
  the idle. It is worth a case only for the readout-adjacent windows.
- **A full-chip checkerboard Ramsey.** A detuning map across the chip is a
  characterization in its own right. It needs its own written case, with
  spectators in |0> and |1>, two quadratures and a delay ladder that
  resolves winding.

## Files

- `ghost-frequency-gpu.ipynb`: the null and detuning Ramsey models, a power
  analysis, an amplitude-miscalibration mimic and a Z Z mimic.
- `ac-stark-discriminator.ipynb`: a residual-photon Stark model and its
  pre-delay signature.
- `ghost-falsification-suite.ipynb`: the three hypotheses together.

The notebooks ran in their own environment. Their outputs are retained as
produced and are not replayed in CI; CI checks only that their code passes
the docs ruff and type gates.
