# Signed kernel probe under the Kingston noise model

`result.json` is the output of `scripts/signed_kernel_noise.py`. It ran as
Kaggle kernel version 3 of `gororoba-signed-kernel-noise`, and the run is
retained under `results/kaggle/2026-10-16T071913Z-gororoba-signed-kernel-noise/`.
Version 2 lacked the bright control and the term arms. It is retained under
`results/kaggle/2026-10-16T064039Z-gororoba-signed-kernel-noise/` as history
only, and its laws for the probes it shared equal version 3's.

- **Machine and software.** Two Tesla T4 GPUs, Python 3.13.15, qiskit 2.5.2
  and qiskit-aer-gpu-cu11 0.17.2 (`kaggle_environment.json`).
- **Stack proof.** The kernel built the hypercomplex package stack before
  its entry ran, and it regenerated the retained tables byte for byte
  (`kaggle_hypercomplex.json`).
- **Noise.** `docs/evidence/calibration/ibm_kingston.json`, calibration
  2026-10-15T19:42:21-07:00.
- **Agreement with the CPU.** Every law agrees with a CPU run of the same
  commit to 2.4e-14.

## Question

`docs/notes/signed_kernel_probe.md` prices the dark count and the signed
Hadamard test of `B(t) u = t v / (2 + |t|)` from a hardware anchor. It
scales the signed visibility by `(1 - e)^CZ` at a median CZ error. This run
asks what live_run's noise model itself predicts for both readouts at
`t` in {0, +-0.05, +-0.1, +-0.2}.

**Falsifiers, stated before the run.**
- **(a)** The pricing's gate factor fails if the simulated signed visibility
  departs from `(1 - e)^CZ` by more than 25 percent.
- **(b)** The signed readout misreads the sign if its offset at `t = 0` is at
  least half the signal `V s(t)` at `t = +-0.05`.

## Method

`scripts/signed_kernel_noise.py` compiles four probes to the snapshot
Target, at optimization level 3 with seed 20261015. The layout of each
probe is pinned by its `t = -0.05` compile. The four probes are:

- **dark** and **signed**, the retained probes of `signed_kernel_probe.py`.
  They put `sign(t)` inside a 128-entry `DiagonalGate`, so each `t`
  compiles to its own circuit: 272 CZ for `t < 0` and 274 for `t >= 0`.
- **dark_matched** and **signed_matched**. Each compiles once with
  parameters: two RY angles for the selector amplitudes and a
  multi-controlled phase `phi` on selector 00 for the sign. Every `t` binds
  the same 114 or 279 CZ, so the probes differ between `t` only in rotation
  angles.

Both dark forms also run the bright control `u' = (e4 + e15)/sqrt2`, whose
ideal success is `(4 + t^2)/(2 + |t|)^2`. It separates attenuation of the
whole success channel from behavior specific to the dark witness.

`snapshot_laws.outcome_law` gives each arm's exact law under live_run's
gate, idle and assignment noise. The noiseless law of every compiled arm
equals its ideal law to 1e-9. The matched signed probe also runs two kinds
of extra arm:

- **Null arms**, at `t = 0` with each phase. At `t = 0` the phase
  multiplies a zero amplitude, so both null arms ideally read 0.
- **Six term arms**, which load the selector with one LCU term (e2, e1 or
  e10) at each phase. Ideally e2 reads +1 or -1 and the other two read 0.

## Result

| Probe | CZ | Visibility (fit slope or null-subtracted) | `(1 - e_median)^CZ` | prod `(1 - e)` over used edges |
| --- | ---: | ---: | ---: | ---: |
| signed | 272/274 | 0.88 slope; offsets -0.010 and +0.027 by sign | 0.577 | 0.671 |
| signed_matched | 279 | 0.601 to 0.602 after null subtraction | 0.569 | 0.663 |

1. **Gate factor holds (falsifier a passes).** The null-subtracted visibility
   of 0.60 lies 6 percent above the median-error factor and 9 percent below
   the product over the CZ edges the compile uses.
2. **Sign-phase offset (falsifier b is triggered).** The null arms read
   +0.0264 at `phi = 0` and -0.0109 at `phi = pi`, a difference of 0.037. The
   ideal signal `0.60 s` is 0.015 at `t = 0.05`. The offset survives the
   structure-matched compile, so it does not come from synthesis. The term
   arms (`signed_matched_terms`) locate it: Pauli errors inside the
   multi-controlled phase propagate differently at its two angles.
   - The e1 and e10 terms, whose ideal overlap is 0, read +0.028 and +0.027
     at `phi = 0`, and -0.016 and -0.007 at `phi = pi`.
   - The e2 term reads +0.628 and -0.606, nearly symmetric.
3. **The raw differential is biased.** `<Z_c>(t) - <Z_c>(-t)` reads a
   visibility of 1.37 at `t = 0.05`, 0.99 at 0.1 and 0.81 at 0.2, because
   the phase offset adds to every sign difference.
4. **Null subtraction fixes it.**
   `(<Z_c>(t) - N_0) - (<Z_c>(-t) - N_pi)` reads 0.602, 0.602 and 0.601 at
   the three values of `t`: an unbiased first-order signed readout at every
   `t`. A z = 3 resolution over its four equal arms needs 166,687 shots at
   `t = 0.05`, 43,810 at 0.1 and 12,025 at 0.2 under this model.
5. **The dark contrast is inverted.** The selector-00 rate at `t`
   minus the `t = 0` arm is negative at every evaluated `t` = +-0.05,
   +-0.1 and +-0.2: -0.0029, -0.0047
   and -0.0054 at `t` = 0.05, 0.1 and 0.2, against ideal +0.0006, +0.0023 and
   +0.0083. The matched form gives -0.0028 to -0.0044.
   - Such a contrast is resolvable: 404,180, 156,745 and 118,841 equal-arm
     shots at z = 3. What it resolves, though, is a background that falls
     with `|t|` faster than `p(t)` rises, not `p(t)`.
   - The bright control moves in its ideal direction. Its contrast is
     -0.040, -0.074 and -0.134 against ideal -0.048, -0.091 and -0.165, a
     transmission of 0.81 to 0.83. So the success channel as a whole is
     attenuated, not inverted, and the inversion belongs to the dark
     witness's background.

## Limits

- **Model scope.** The model has live_run's incoherent noise only. Coherent
  over-rotation, crosstalk and leakage are absent, and the hardware floor
  the note anchors on (0.182) is above the model's.
- **What the run establishes.** The offset mechanism and the null
  subtraction are statements about this model. A hardware case would carry
  both null arms as part of its design, and measure them rather than assume
  them.
- **Hardware price.** The note's hardware price of 190,895 shots at
  `t = 0.05` assumes a two-arm readout with no sign-dependent offset. A
  four-arm null-subtracted design at the anchor visibility would cost more.

## Replay

Gate core-304 first requires `result.json` to be byte-identical to the
output recorded in the run's `collect.json` ledger. It then recompiles every
probe and recomputes the laws at `t` in {-0.05, 0, 0.05} on the CPU, and
requires the layouts and CZ counts to match exactly and each law to match
to 1e-8. Gate core-303 lints and type-checks the script. Gate core-273
still re-derives the retained probe evidence, which the matched probes
leave unchanged.
