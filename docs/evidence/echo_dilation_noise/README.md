# Echo-matched dilation pair under the retained calibrations

`result.json` is the output of `scripts/echo_dilation_noise.py`. It ran as
Kaggle kernel version 3 of `gororoba-echo-dilation-noise` on a CPU machine
in 137.8 s, and the run is retained under
`results/kaggle/2026-10-16T174357Z-gororoba-echo-dilation-noise/`. Earlier
versions stay as history:
- Version 1 (GPU, `results/kaggle/2026-10-16T153522Z-gororoba-echo-dilation-noise/`)
  lacked the per-edge sweep and sized the PREP shots on the device baseline.
- Version 2 (CPU, `results/kaggle/2026-10-16T162448Z-gororoba-echo-dilation-noise/`)
  bounded the conditional phase by the mean of its two sign responses.

All three agree on every law they share: version 1 against version 2 to
5.3e-15, and version 2 against version 3 bit for bit.
`arms.qpy` holds the compiled device arms (amplified, echo) of each backend,
in the order `result.json` lists under `qpy_arms`.

- **Machine and software.** A 4-core Kaggle CPU machine, Python 3.13.15,
  qiskit 2.5.2 and qiskit-aer 0.17.2, with four workers
  (`kaggle_environment.json`).
- **Stack proof.** The kernel built the hypercomplex package stack and
  regenerated the retained tables byte for byte before its entry ran
  (`kaggle_hypercomplex.json`).
- **Noise.** The latest retained snapshot of each backend:
  - ibm_fez, 2026-10-15T20:31:28-07:00;
  - ibm_kingston, 2026-10-15T20:35:33-07:00;
  - ibm_marrakesh, 2026-10-15T20:46:35-07:00.

  The files are under `docs/evidence/calibration/history/`.

## Question

`docs/notes/singular_sector_dynamics.md` proposes the pair below as a
coherent-error discriminator for Design B's dark probe of `e1 + e10`:
- amplified: `U Z U^dagger Z U`;
- echo: `U U^dagger U`.

A PREP angle `pi/4 + eps` is undone by the compiled inverse, so ideally
amplified - echo = `sin^2(6 eps) - sin^2(2 eps) > 0`. A CZ conditional phase
survives the inverse. The FakeFez record showed the two moving the difference
in opposite directions. On hardware, though, the PREP angle is exact in
software. The pair separates classes only if some physical error lands in
the undone class. This run asks, under each retained calibration, which
class each physical coherent channel lands in, and what a device case would
need in shots and in an independent CZ-phase reference.

**Falsifier, stated before the run.**
- **Matched null.** The baseline difference is a matched null when it lies
  within one standard error at 40,000 shots per arm.
- **Class verdict.** A class's verdict is the sign of its shift of
  amplified - echo at both signs of its magnitude:
  - undone when every shift of 1e-3 or more is positive;
  - surviving when every such shift is negative;
  - odd when they differ;
  - null when no shift reaches 1e-3.
- **Separation.** The pair separates rotation errors from CZ phases on a
  calibration only when the CZ conditional phase is surviving and SX
  over-rotation or CZ local phase is undone.

## Method

1. **Compile.** Separate compiles of the two arms route differently: 145
   against 141 CZ on Kingston at the same layout. So the pair compiles once,
   as `U R U^dagger R U` with `R = RZ(reflection)` on the ancilla, at
   optimization level 3 (seed 7). It then binds `reflection = pi` for the
   amplified arm and 0 for the echo arm, and both arms carry the identical
   sequence of non-virtual gates on the same qubits.
   - **Device compile.** It binds `beta = pi/4` and picks the layout. This
     is the circuit a device case would run.
   - **eps family.** It compiles once with `beta = pi/4 + eps` symbolic on
     the same layout, then binds each eps. A bound pi/4 synthesizes
     differently from a generic angle.
   - **Noiseless check.** Every compiled arm's noiseless P(anc = 0) equals
     `sin^2(6 eps)` or `sin^2(2 eps)` to 1e-9.
2. **Model.** Each arm keeps its barriers, is scheduled ALAP on the
   restricted Target, and runs live_run's gate, idle and assignment noise
   (`walk_scaffold_channels.LaneModel`). On the device compile one channel
   is inserted uniformly on every qubit or edge:
   - SX over-rotation (RX after every SX);
   - CZ local phase (RZ on both qubits after every CZ);
   - CZ conditional phase (CP after every CZ);
   - extra depolarizing after every CZ, the incoherent control.

   With every parameter at zero, each channel reproduces the baseline.
3. **Mixtures.** The eps members at 0.03 and 0.06 rad also run with a
   conditional phase delta of +-0.01 and +-0.02 rad.
4. **CZ-phase reference.** It runs on each of the four edges the device
   compile uses:
   - the control in `|+>` and the target in `|0>` or `|1>`;
   - 2m barrier-separated CZ, with m = 8 or 24;
   - the control read in the Y basis.

   The target-1 minus target-0 readout carries `2m delta` and cancels each
   qubit's local phase. It runs under every channel.
5. **Per-edge sweep.** Each of the four edges alone carries a conditional
   phase of +-0.01 and +-0.02 rad, and the sum of the four single-edge
   shifts is compared with the uniform shift at the same delta.
6. **Sizing.**
   - **Pair shots.** The shots per arm that resolve each shift at z = 3,
     against the baseline of the shift's own compile (the eps family for
     PREP, the device compile for the physical channels).
   - **Phase bound.** The conditional phase moves the pair about evenly in
     delta, so the reference must bound |delta| below the magnitude whose
     shift equals the pair's standard error. That magnitude comes from
     power-law interpolation on the delta grid.
   - **Reference shots.** The shots per edge and target state that reach
     that bound at z = 3 through the reference's own slope, for the uniform
     bound and for each edge's single-edge bound.

**Algebra.** `cd_core` certifies `(e1 + e10)(e4 - e15) = 0` and
`(e1 + e10)(e4 + e15) = 2 e5 - 2 e14` on the 32 basis products SELECT
encodes. python-hypercomplex 0.3.4 (exact `Fraction` coefficients) and
python-hypercomplex-engine 0.5.0 agree with it on all 32, under the identity
map `docs/notes/packages/` declares.

## Result

**The pair does not separate rotation errors from CZ phases on any of the
three calibrations.** Every shift of 1e-3 or more that a physical coherent
channel produces moves amplified - echo negative, the same direction as the
CZ conditional phase; only the PREP angle, which has no physical source on
this gate set, moves it positive by that much. Below the 1e-3 threshold the
sign is not determined: SX over-rotation at +0.01 and +0.02 rad on Marrakesh
shifts it by +2.5e-4 and +8e-6.

| Backend (device layout) | CZ | Baseline amplified, echo | Difference | SE at 40,000 |
| --- | ---: | --- | ---: | ---: |
| ibm_fez (37, 25, 26, 45, 24) | 141 | 0.2603, 0.2556 | +0.0046 | 0.0031 |
| ibm_kingston (152, 151, 138, 153, 150) | 141 | 0.2068, 0.2046 | +0.0022 | 0.0029 |
| ibm_marrakesh (88, 89, 90, 87, 78) | 141 | 0.2928, 0.2885 | +0.0043 | 0.0032 |

Shift of amplified - echo from the baseline, at both signs of each magnitude:

| Class | Magnitude | Fez | Kingston | Marrakesh | Verdict |
| --- | ---: | --- | --- | --- | --- |
| PREP eps | 0.03 rad | +0.0144, +0.0159 | +0.0186, +0.0173 | +0.0123, +0.0152 | undone |
| SX over-rotation | 0.02 rad | -0.0035, -0.0026 | -0.0038, -0.0032 | -0.0023, +0.0000 | surviving |
| SX over-rotation | 0.04 rad | -0.0135, -0.0093 | -0.0147, -0.0115 | -0.0072, -0.0016 | |
| CZ local phase | 0.01 rad | -0.0262, -0.0253 | -0.0293, -0.0292 | -0.0244, -0.0247 | surviving |
| CZ conditional phase | 0.01 rad | -0.0104, -0.0096 | -0.0117, -0.0113 | -0.0094, -0.0092 | surviving |
| CZ conditional phase | 0.02 rad | -0.0404, -0.0352 | -0.0461, -0.0411 | -0.0362, -0.0333 | |
| Extra depolarizing | 0.01 per CZ | -0.0033 | -0.0010 | -0.0031 | surviving on Fez and Marrakesh, null on Kingston |

1. **No separation.** The pair cannot tell SX over-rotation or CZ local phase
   from a CZ conditional phase by its sign. Physically realized rotation
   errors survive the compiled inverse, because the inverse reverses the
   gate order but applies the same SX and CZ pulses.
2. **What the pair does detect.** A negative shift beyond the modeled
   incoherent floor is an error-channel signal whose source stays
   unidentified: the coherent channels move the pair strongly, but an
   unmeasured rise in the incoherent floor moves it the same way, and the
   one depolarizing magnitude tested bounds no incoherent change in general.
   - It is very sensitive to CZ phases: about 7,100 to 12,700 shots per arm
     resolve a 0.01 rad local phase at z = 3, and 43,500 to 88,400 a
     0.01 rad conditional phase.
   - SX over-rotation needs 0.04 rad, above the 0.035 rad the calibrated
     SX errors imply. At -0.04 rad that takes 28,700 to 146,600 shots per
     arm; at +0.04 rad on Marrakesh, 3.1 million.
   - The conditional-phase response is not monotone: at 0.1 rad it falls
     back below its 0.05 rad value.
3. **The matched null holds on Kingston only.** On Fez and Marrakesh, the
   calibrated incoherent noise alone gives a difference of 1.3 to 1.5
   standard errors at 40,000 shots. Extra depolarizing at 0.01 per CZ
   (several times the calibrated error) shrinks that contrast by 0.003 and
   so reads as surviving under the preregistered rule. It is a scaling of
   the incoherent baseline, about one standard error at the largest budget,
   while the coherent channels at 0.01 rad move the difference by 3 to 10
   standard errors.
4. **Mixtures cancel.** A PREP eps of 0.03 rad cancels against a conditional
   phase of |delta| = 0.0116 to 0.0134 rad on every backend. At eps = 0.06,
   the grid up to |delta| = 0.02 does not cancel it. So a null difference
   certifies neither class, as the note already states.
5. **The CZ-phase reference is independent and cheap.**
   - **Readout.** Under the calibrated noise its target-1 minus target-0
     readout is 0 to 1.1e-16.
   - **Cross-sensitivity.** SX over-rotation, CZ local phase and extra
     depolarizing bias its delta estimate by at most 8.3e-4 rad. The
     tolerance the 40,000-shot pair needs is 0.0048 to 0.0057 rad.
   - **Visibility.** On hardware the Y-basis readout difference is
     `V [sin(theta + 2m delta) - sin(theta)]`, with an unknown visibility V
     and common phase theta. The slope here comes from the model's known
     deltas, so the device case adds an X-quadrature arm for each edge and
     depth to measure V and theta before its counts bound any phase.
   - **Shots.** At m = 24 it reaches that tolerance with 355 to 529 shots
     per edge and target state, so four edges cost about 4,000 shots.
6. **Edge phases add coherently, not edge by edge.** The four single-edge
   shifts sum to 0.25 to 0.33 of the uniform shift on every backend (Fez at
   0.02 rad: -0.0115 against -0.0404). Four comparable edges whose phases
   add inside the shift, which grows about quadratically, give 1/4. So the
   pair responds to a weighted sum of the edge phases, and one edge's
   contribution depends on the others.
   - Two edges per backend move the pair by less than its 40,000-shot
     standard error alone, even at 0.02 rad, and the other two need 0.013 to
     0.019 rad.
   - Bounding each edge to its single-edge tolerance would therefore under-size
     the reference about tenfold (32 to 64 shots per target where the joint
     bound needs 355 to 529). The joint tolerance, 0.0048 to 0.0057 rad on
     every edge, is the sizing a case uses under the uniform-phase model.
   - Mixed phase vectors, with unequal or opposite-signed phases across
     edges, are untested. The response is nonlinear, so the joint tolerance
     bounds equal phases on every edge, not an arbitrary mix.

## Consequences for the proposal

`proposed-echo-matched-dilation` asked the pair to separate inverse-undone
rotation errors from CZ conditional phases. Under these noise models no
physical rotation error is inverse-undone, so the pair's negative shift is
a sum of coherent channels and of changes in the incoherent floor: extra
depolarizing moves the pair the same way on Fez and Marrakesh, and the
calibrated baseline already misses the matched null there.
- **Conditional share.** Under the uniform-phase model, the per-edge
  reference, with X-quadrature arms that calibrate its visibility and
  common phase, bounds every edge's conditional phase to the joint
  tolerance. The model maps those bounds onto the pair only jointly, and
  mixed phase vectors need their own sweep before they bound anything.
- **Residual.** What remains after the conditional share is unidentified.
  Attributing it to local phase or SX over-rotation needs an independently
  measured incoherent control on the same compile, which this run does not
  design.

## Limits

- **Channels.** Each channel is injected alone, uniformly on every qubit or
  edge; the conditional phase is also swept one edge at a time.
  Non-uniform local phases and SX over-rotations, drifting or crosstalk
  errors, and leakage are outside the run.
- **Model.** The noise model is live_run's (gate depolarizing, thermal
  relaxation, asymmetric readout). The baselines are predictions, and no
  hardware run of the pair exists.
- **Compiles.** The verdicts hold for these compiles at seed 7. A different
  layout or synthesis can change the magnitudes, and the retained QPY binds
  the device compile.

## Replay

Gate core-313 checks the result on the CPU:
- **Provenance.** It requires `result.json` and `arms.qpy` to be
  byte-identical to the outputs the run's `collect.json` ledger records.
- **Algebra.** It recomputes the `cd_core` signs without importing any
  package.
- **Compile.** It recompiles Kingston and requires the compile summary
  (layout, CZ counts, gate-sequence digests, duration, edges) and both
  device arms to match the retained ones.
- **Laws.** It recomputes a reduced set of Kingston laws to 1e-8:
  - the baseline;
  - every channel at 0.002 and 0.02, and the first edge alone at 0.02;
  - eps = +-0.03;
  - one mixture;
  - one reference edge.
- **Analysis.** It recomputes every verdict, mixture and shot count from the
  retained laws.

Gate core-312 lints and type-checks the script.
