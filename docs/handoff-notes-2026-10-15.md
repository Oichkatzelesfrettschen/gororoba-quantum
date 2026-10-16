# Handoff Notes: Chat Session 2026-10-15 (Ferreton → Claude Code)

> Audit: `docs/evidence/simulation-notebook-audit/README.md` reads every
> notebook named here against its retained Kaggle log, and
> `docs/state/research_state.json` carries the resulting claim status.

These notes capture decisions, framings, and falsification results from the
2026-10-15 chat session that are not yet in the repository. Written in
declarative style per the project style guide.

## Interpretive Framings (Adopted)

**Substrate is physical.** The "associative substrate" in the sedenion
documents refers to the quantum hardware itself. Quantum operators compose
associatively by the physics of Hilbert space. The sedenion algebra
(non-associative) is encoded into circuits run on that associative physical
substrate. The measured 0.59 is the difference between bracketings, not a
claim that hardware becomes non-associative.

**Simulation, not emulation of space.** The work simulates algebraic
relationships (composition rules), not a different physical space. Hilbert
space is Hilbert space. Analogous to drawing non-Euclidean geometry on a
flat screen: the screen stays flat, the displayed relationships follow
different rules.

**Verification layer, not calibrator.** The falsification toolkit
(transpiler audit, sensitivity proofs, linearity arguments) is a diagnostic
protocol. It checks whether hardware behavior tracks intended mathematics.
It does not adjust hardware parameters.

**Why 84/84 is non-trivial.** Circuits with 37 CZ gates at ~2% error per
gate should be noise-dominated. The algebraic signature surviving 84/84
means the signal exceeds the noise floor. A quantum computer that cannot
hold coherence through the calculation produces random numbers, not
mathematics.

## Environmental Falsification (Ghost Frequency)

**Schumann resonance: ruled out.** Frequencies are 7.83 Hz fundamental,
harmonics at ~14, 20, 27, 33 Hz. The ghost is at ~30,000 Hz. Three orders
of magnitude mismatch. No harmonic relationship. No coupling mechanism
between picotesla ELF fields and GHz qubits at kHz detuning.

**VLF military transmitters: unlikely, one check remaining.**
- DHO38 (German Navy): 23.4 kHz, 800 kW, Rhauderfehn Germany.
- NAA (US Navy): 24.0 kHz, ~1 MW, Cutler Maine.
- ibm_fez is in Ehningen Germany; ibm_kingston is at Poughkeepsie NY.
- Against: wrong frequencies (23.4/24.0 vs ~30 kHz), wrong modulation
  (MSK 50-baud vs quasi-static), no clear coupling path for
  fixed-frequency transmons.
- Remaining check: correlate ghost presence with known transmitter
  maintenance outages. If ghost persists through an outage, VLF is dead.
  This is a calendar check, not a QPU experiment.

**AM radio: ruled out.** 530–1700 kHz. Order of magnitude above the band.

**Data center PSU switching: unlikely.** Typically 50–500 kHz. Would be
site-specific; ghost appears on both ibm_fez and ibm_kingston.

**Ghost hypothesis ranking (current):**
1. AC Stark from residual resonator photons (~0.01 thermal). Fits all
   signatures. Testable via pre-delay discriminator.
2. Unmodeled control-electronics tone. Same design at both sites explains
   the match.
3. VLF pickup. Band overlap demands the outage check, but frequency and
   modulation mismatch.
4. Schumann. Dead.
5. Intrinsic qubit frequency offset. Uninformative label for "unknown."

## Practical Outcomes (Three Optimizations)

1. **Circuit simplification.** CCZ reduction: 360 associator circuits →
   1 CCZ + Cliffords each. 18.9% fewer CZ gates, 60% fewer single-qubit
   gates, 1.19x fidelity improvement. GPU-validated. Drop-in replacement
   confirmed (fidelity 1.0, TV distance 1.67e-16).

2. **Hardware verification methodology.** The falsification toolkit is
   independently derived and openly documented. Applicable to any
   superconducting qubit verification task.

3. **Noise spectroscopy.** The ghost-frequency protocol detects detuning
   that standard calibration misses. If confirmed on hardware, it is a
   second-layer software tuning tool.

## Explicit Non-Goals

This work does not advance: cold fusion, fusion, quantum gravity, black
hole detection, gravitational-wave interferometry, or telescope
calibration. It is gate-level quantum characterization. The Planck-time
quantum clock concept was considered and rejected: Planck time is not a
measurable tick, and the 30 kHz unmodeled detuning is evidence these
qubits are poor frequency references.

## QPU Run Designs (Ready for Claude Code)

**Algebraic-frequency Ramsey.** For ~20 defective and ~20 clean triples,
run Ramsey at [1,2,4,8] µs. Extract δ per triple. Compare distributions.
Sensitivity: 5 kHz with current shot budget. Notebook:
`docs/evidence/ghost-frequency/algebraic-frequency.ipynb`.

**Differential interleaved.** Interleave defective/clean shots to cancel
common-mode drift. Optimal Ramsey delay: 8.3 µs (t = 1/4δ for 30 kHz
ghost). Scaling: 500 Hz → 7,200 shots (~1s); 50 Hz → 720k shots (~72s);
5 Hz → 72M shots (~2hrs). Start coarse (500 Hz), go deeper only if null.
Notebook: `docs/evidence/ghost-frequency/differential-interleaved.ipynb`.

**Factorized vs CCZ on hardware.** Both give identical ideal outcomes
(verified). Run the CCZ normal form to confirm the fidelity improvement
on real hardware. Notebook:
`docs/evidence/ccz-reduction/factorized-vs-ccz.ipynb`.

## Style Guide (Project-Wide)

Eric's voice for all repository documents, visualizations, PDFs, and his
social media posts: declarative, indicative, non-prophetic. Plain
statements of fact. No metaphors, no "we," no visionary language, no
self-reference. Describe what is.

Ferreton's own voice (social posts written as Ferreton): playful, goofy.
These are two distinct voices. Do not mix them.

## Session Artifacts

All GPU-validated notebooks from this session are in:
- `docs/evidence/cd_census/census-4096-repaired.ipynb`
- `docs/evidence/ccz-reduction/ccz-optimization.ipynb`
- `docs/evidence/ccz-reduction/factorized-vs-ccz.ipynb`
- `docs/evidence/ghost-frequency/algebraic-frequency.ipynb`
- `docs/evidence/ghost-frequency/differential-interleaved.ipynb`
- `docs/evidence/ghost-frequency/predelay-84-84.ipynb`
- `docs/evidence/simulation/qiskit-aer-simulation.ipynb`
- `docs/evidence/falsification/gemma-falsification-review.ipynb`

## Red-Team Review (Ferreton, 2026-10-15)

An LLM red-team was attempted via Gemma 4 on Kaggle. RCA: v1/v2 returned
empty because Gemma instruction-tuned models require the chat template
(`apply_chat_template` with `<start_of_turn>` markers); raw text input
produces no generation. Also requires `transformers>=5.5`. v3 with the fix
was submitted; results pending.

Manual red-team findings (Gemma v3 confirms Q2, Q3, Q4 below):

**Claim 1 (Compiler) — strongest.** Gap: the audit verified submitted
circuits, not executed circuits. IBM's runtime could apply additional
optimization. Test: compare QPY bytes in the job record against submitted
circuits.

**Claim 2 (Coherent error) — strong but narrow.** dΔ/dα=0 covers angle
miscalibration only. Gap: axis miscalibration, correlated coherent errors
across 37 CZ gates untested. Test: GPU sim with axis-error and
correlated-error models.

**Claim 3 (Readout) — strong.** Linearity argument is airtight for
classical readout. Gap: assumes classical linear readout. Quantum
measurement backaction could differ between bright/dark because
pre-measurement states differ. Test: model measurement as quantum channel.

**Claim 4 (Resonator) — weakest, in tension with ghost hypothesis.**
The arithmetic bound assumed photons manifest as readout bias. But AC
Stark shifts qubit frequency, a different mechanism. The ghost hypothesis
H2 *is* resonator photons. Cannot simultaneously claim photons explain
the ghost and are ruled out for 84/84 without distinguishing the
mechanisms.

Ranking by vulnerability: 4 > 2 > 3 > 1.

**Gemma v3 confirmations (2026-10-15):**
- Q2 (readout): Confirmed. "Relies on the assumption that the readout
  error is modeled purely as a classical bit-flip channel."
- Q3 (AC Stark): Confirmed. "By varying the photon number in the
  resonator while keeping the qubit state fixed, one can measure the
  shift's dependence on nbar to differentiate the two effects."
- Q4 (backaction): Confirmed. "The measurement process acts as a
  non-trivial quantum channel whose effect depends on the input quantum
  state."
- Q1 (transpiler): Non-answer. Gemma gave a generic "transpilers can
  introduce differences" without engaging with the byte-identical
  evidence. Demonstrates LLM review limitation: does not weigh specific
  evidence against general principles.

## Pre-Delay Discriminator: Negative Result for 84/84

A GPU simulation tested whether a pre-delay sweep [0,1,2,5,10,20,50] µs
could detect photonic contribution to the 84/84 contrast. Result: 11%
detection power. The differential photonic effect on Δ is second-order
and buried in measurement noise.

Implication: do not spend QPU time on a pre-delay sweep of the 84/84
circuits expecting to resolve photonic contribution. The pre-delay test
is strong for the ghost itself (absolute detuning, H1 vs H2) but weak
for 84/84 (differential contrast).

## What Claude Must Test (QPU Priority Order)

1. **Ghost pre-delay discriminator** (highest value). Ramsey with
   pre-delay sweep on a single qubit. If detuning decays with pre-delay:
   photonic (H2). If flat: intrinsic (H1). This resolves the leading
   hypothesis. Notebook: `docs/evidence/ghost-frequency/` suite.

2. **Algebraic-frequency Ramsey.** ~20 defective + ~20 clean triples,
   Ramsey at [1,2,4,8] µs each. Tests whether ghost detuning correlates
   with sedenion structure. Start at 500 Hz sensitivity (~1s per point).

3. **Differential interleaved** (only if 1 and 2 are null). Interleaved
   defective/clean shots for Hz-level differential sensitivity. Optimal
   Ramsey delay: 8.3 µs. Expensive: 50 Hz needs 720k shots (~72s);
   5 Hz needs 72M shots (~2hrs). Parallelize across qubits.

4. **CCZ normal form on hardware.** Run the CCZ circuits to confirm the
   1.19x fidelity improvement on real hardware. Ideal outcomes verified
   identical (fidelity 1.0).

5. **QPY comparison** (no QPU needed). Compare submitted circuit bytes
   against job record QPY to close the Claim 1 gap.

Do NOT run: pre-delay sweep on 84/84 circuits (11% power, negative
result). Do NOT run: VLF correlation (calendar check first, free).
