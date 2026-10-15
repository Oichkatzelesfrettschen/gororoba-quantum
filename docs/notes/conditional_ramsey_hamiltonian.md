# Conditional Ramsey: identifying the diagonal pair Hamiltonian

The branch-signed coherence window measures how an idle rotates one Bell
coherence. Two Bell sectors cannot identify every diagonal interaction of the
pair, and the measurement that fixes this is a conditional Ramsey pair, not
more shots of the same sectors. `gororoba_quantum/conditional_ramsey.py`
builds the design, its analysis and its checks (gate core-272); live_run.py
runs it as the opt-in `conditional_ramsey` campaign.

## Model and design matrix

The reduced model is `H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2`
on `|ab>` with `Z|0> = |0>`. A coherence between basis states `x` and `y`
winds as `rho_xy(t) = exp(-i nu t) rho_xy(0)` with `nu = E_x - E_y`:

| Sector | States | Rate | Row over (omega_A, omega_B, J) |
| --- | --- | --- | --- |
| Bell even | `|00>, |11>` | `omega_A + omega_B` | (1, 1, 0) |
| Bell odd | `|01>, |10>` | `omega_A - omega_B` | (1, -1, 0) |
| A given B = 0 | `|00>, |10>` | `omega_A + J` | (1, 0, 1) |
| A given B = 1 | `|01>, |11>` | `omega_A - J` | (1, 0, -1) |

The two states of a Bell sector share one `Z_A Z_B` eigenvalue, so both Bell
rows are blind to `J`: the Bell-only design has rank two with null direction
`J`. The conditional rows raise the rank to three:

- `omega_A = (nu_odd + nu_even) / 2`, `omega_B = (nu_even - nu_odd) / 2`;
- `J = (nu_A|0 - nu_A|1) / 2`;
- the fourth row is redundant under the model, which makes
  `nu_odd + nu_even = nu_A|0 + nu_A|1` a falsifier: a resolved residual
  rejects a static diagonal pair Hamiltonian under the measurement
  assumptions below.

`design_rank` computes both ranks exactly over Q.

## Circuits and estimator

A on qubit 0, B on qubit 1, each measured into its own clbit. A Bell arm
prepares the sector with H and CX (B flipped first for odd), idles, undoes the
CX and reads A; a conditional arm prepares B in `|b>`, applies H to A, idles
and reads A. In every arm A ends in `(|0> + exp(i(nu t + phi0))|1>) / sqrt2`,
so the X and Y readouts give `<X_A> = V cos(nu t + phi0)` and
`<Y_A> = V sin(nu t + phi0)`. Barriers keep the transpiler from merging the
preparation into the idle.

Delays are 0, 1250, 2500, 5000, 7500 and 10000 dt (0 to 40 us at dt = 4 ns):
48 Ramsey circuits plus two calibration circuits that read both qubits
prepared in `|0>` and in `|1>`. The calibration gives A's flips
`e10 = P(1 | 0)` and `e01 = P(0 | 1)`, measured in the job, because the
corner baseline showed reported readout errors off by a factor of 40. The
channel maps a true expectation `q` to `(1 - e10 - e01) q + (e01 - e10)` in
both quadratures. The common offset moves the centre of the Ramsey circle,
so the phase of the raw expectations errs by an amount that depends on the
true phase, and therefore on delay, which biases the rate. The summary
inverts the channel before taking phases.

The estimator unwraps the corrected phase `atan2(<Y>, <X>)` across
consecutive delays and fits a straight line. The slope is `nu` in rad per dt;
fixed gate durations and preparation phases go into the intercept, so they
leave the rate unchanged. Unwrapping is unambiguous for
`|nu| < pi / 2500` rad per dt, 50 kHz; a faster rate aliases, which the
self-check demonstrates.

Each rate, parameter and the falsifier residual carries a delta-method
standard error at one shot per circuit (`*_se_one_shot`; divide by
`sqrt(shots)`). Every circuit is an independent multinomial, and central
differences propagate its covariance through the calibration, the phase fits
and the reconstruction. A collected run therefore yields intervals from a
single replica.

## Checks

- Every arm matches its ideal outcome law under an ideal idle.
- With the idle replaced by `RZ_A(omega_A t) RZ_B(omega_B t) RZZ(J t)` at
  30, -12 and 8 kHz, the summary recovers all three parameters to 1e-12, with
  zero falsifier residual.
- A detuning delta added to the conditional arms only leaves a residual of
  exactly `-2 delta`.
- With asymmetric channels on both qubits (A: 0.04 and 0.12, B: 0.02 and
  0.08), the corrected summary still recovers `J` to 1e-10, and the summary
  without the calibration is biased.
- Over 40 multinomial resamplings at 1024 shots, the spread of `J` and of the
  falsifier residual lies within 0.7 to 1.4 times the propagated standard
  error (about 89 Hz for `J`), with no resolved bias.

## Nuisances the design leaves in place

- **B preparation error.** A fraction `eps` of B in the wrong state mixes the
  two conditional coherences. Each conditional phase moves by at most
  `arcsin(eps / (1 - eps))` at every delay, because
  `|arg(1 + r exp(i theta))| <= arcsin r` for `r < 1`. The summary reports
  the measured `P(B != prepared)` per sector. B in `|1>` also relaxes during
  the idle, which ends the conditioning partway through the exposure.
- **Readout.** The in-job calibration corrects A's assignment channel,
  including its asymmetric offset. The correction assumes that the channel
  measured with both qubits in one basis state also holds for the Ramsey arms.
  It leaves readout crosstalk that depends on B's state uncorrected, and it
  is distinct from `live_run.corrected_summary`, which inverts the
  calibration-reported flips. The B preparation error is reported raw, so it
  includes B's assignment error.
- **Spectators.** The model covers one pair. The campaign runs one replica
  without dynamical decoupling, and Z Z couplings to idle neighbors in `|0>`
  shift `omega_A` and `omega_B` by a constant that the design absorbs.
- **Time dependence.** A rate that drifts within the job, or a non-diagonal
  term, breaks the linear phase model. The falsifier and the fit residuals
  detect it without identifying it.

## What it does not establish

The planner's calibrated noise model carries no detuning or Z Z term, so
local simulation predicts zero rates. Only hardware measures them. A
hardware run gives `omega_A`, `omega_B` and `J` for one pair under one
calibration, and a resolved falsifier residual rejects the reduced model. It
does not identify which unmodeled term is responsible, and it says nothing
about the Fez orbit phase, which came from different circuits, qubits and
calibrations.
