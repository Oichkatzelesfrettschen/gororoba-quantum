# Simulation notebooks: committed verdicts against their own outputs

The notebooks under `docs/evidence/{cd_census,ccz-reduction,simulation,falsification}`
and the newer ones under `docs/evidence/ghost-frequency` ran as Kaggle
kernels and were committed with their outputs stripped. `retrieval.json`
names each kernel, and `kaggle_logs/` retains its output log as Kaggle
returned it (`kaggle kernels output`); `SHA256SUMS` binds the bytes (gate
sources-246). For the eight newest kernels, `kaggle kernels pull` returned
code cells identical to the notebooks at commit 900461a, so each log is the
output of the committed code.

A kernel log is a simulation output. It enters `docs/state/research_state.json`
only through a CPU replay gate; until then the notebooks are design sketches.

## Verdicts

| Notebook | Committed verdict | What its kernel printed | Reading |
| --- | --- | --- | --- |
| `cd_census/census-4096-repaired` | 1848/4096 defective | `Defective: 1848/4096`, `MATCH: True` | Correct. It reproduces the census that gate core-212 already re-derives (claim `cd-associator-census`); the earlier `census-4096` kernel printed 1728 from a hand-written table and is superseded. |
| `ccz-reduction/ccz-optimization` | 18.9 % fewer CZ, 60 % fewer 1q gates, 1.19x (cell text: 1.3x) fidelity, "measurably more noise-resilient on real hardware" | the same numbers | The gate counts are typed-in estimates (`orig_1q = 50  # estimate`, `opt_cz = 6 + 12 + 12`), the fidelity is `0.98^n` arithmetic on them, and nothing ran on hardware. The 15 x 24 = 360 count is printed, not computed. The structural claim is true; see below. |
| `ccz-reduction/factorized-vs-ccz` | the CCZ normal form is a drop-in replacement (fidelity 1.0) | `Fidelity: 1.000000`, `U_A...reproduces f(x) for all inputs: True` | Both "constructions" are diag(1, ..., 1, -1): H CCX H on the target is CCZ by definition. The "general case" uses l3 = x0 + x2 = l1 + l2, so l1 l2 l3 = 0 for every x, U_A is singular, and both sides are the constant +1. Neither test touches an associator circuit. |
| `simulation/qiskit-aer-simulation` | the bright/dark split emerges from quantum simulation and survives Heron-level noise | ideal difference 0.089, noisy 0.055, `Signal survives Heron-level noise: False` | The circuit (`ry(angle/4)` layers, CZ ladders, `rx(0.1)`) is no repository design, so it says nothing about the 84/84 ripple pairs, and its own printed result contradicts its verdict. The noise model's 2 % CZ error is about eight times the calibrated Heron value. |
| `ghost-frequency/algebraic-frequency` | a structure-dependent detuning is detectable to about 5 kHz with 20 triples per group | `True: 30.0 kHz, Measured: -29.5 kHz`; every group mean negative | The single-quadrature `cos` fit cannot tell +delta from -delta, which the sanity line shows. The design names no circuit in which a triple label sets a qubit frequency: bright and dark members differ in one virtual RZ (claim `hw-box-kite-executed-pairs`), so the hypothesis has no lever. |
| `ghost-frequency/differential-interleaved` | interleaving cancels drift, "verified on GPU" | expected dP 1.18e-03, measured -6.00e-05 +- 3.23e-03, `SNR: 0.0`; with drift -4.29e-03 +- 2.37e-03 | The GPU check failed by its own numbers. The scaling formula N = 1/dP^2 is right, but its "10 kHz repetition rate" is about 2.6 times the Heron rate (250 us default `rep_delay` plus circuit), and the committed table ("minutes", "hours", "days") disagrees with the printed 1 s, 72 s, 7188 s. Circuits already iterate column-wise over shots on IBM backends, so a two-circuit job is interleaved without a design change. |
| `ghost-frequency/predelay-84-84` | negative: 11 % power, do not run | `Stark (kHz)` 0.010 at zero delay, `Detection power: 11%` | The model sets the contrast change to 0.1 per kHz of Stark shift and the shift to 0.01 kHz, so the effect is 0.001 against a 0.02 standard error by construction. The power figure restates those inputs; it is neither a negative result nor evidence. The notebook's own verdict cell still recommends the run. |
| `falsification/gemma-falsification-review` | Gemma confirms Q2-Q4 | Gemma 4 E2B answers | A language-model answer is not evidence for or against a physical claim. Q1's answer ("the transpiler could have introduced a systematic difference") is refuted by the executed-gate audit: the 84 bright/dark pairs execute identical gates and differ in one virtual RZ. |

The older kernels (`falsify-84-84`, `falsify-resonator-readout`,
`ghost-falsification-suite`, `ac-stark-discriminator`,
`ghost-frequency-gpu-validation`) belong to notebooks already corrected in
`docs/evidence/transpiler-audit/README.md` and
`docs/evidence/ghost-frequency/README.md`; their logs are retained here
for completeness.

## The cubic normal form, checked exactly

`scripts/associator_cubic_normal_form.py` (gate core-278) settles the
structural claim behind the CCZ notebooks from `cd_core`:

- Each of the 360 dim-32 associator phases of degree 3 is
  `f = l1 l2 l3 + q` with three linearly independent forms and `deg q <= 2`,
  so `W_ij = D_q U_A^dagger (CCZ x I) U_A`. The cubic part takes 15 values,
  24 pairs each, with 1, 2, 3 or 4 cubic monomials (96, 144, 96 and 24 pairs).
- Compiled to the ibm_kingston coupling map (basis cz, rz, sx, x;
  optimization level 3; seed 11), mean CZ counts by monomial count are:

  | cubic monomials | pairs | factorized (Design C) | Reed-Muller diagonal | CCZ normal form | normal form fewer CZ |
  | ---: | ---: | ---: | ---: | ---: | ---: |
  | 1 | 96 | 121.6 | 9.9 | 24.6 | 3 |
  | 2 | 144 | 124.6 | 21.7 | 32.5 | 22 |
  | 3 | 96 | 125.9 | 32.9 | 32.3 | 48 |
  | 4 | 24 | 130.6 | 42.7 | 29.3 | 24 |

- The factorized circuit keeps the barriers between its three blocks, so
  each block compiles separately, as in the hardware design.
- The normal form uses fewer CZ than the direct diagonal oracle on 97 of
  360 pairs: every four-monomial pair, half of the three-monomial pairs and
  a few with one or two. The 18.9 % and 1.19x figures have no counterpart in
  any compiled circuit.
- Both diagonal circuits are built from the precomputed phase, so they
  encode the predicted answer. They cannot replace the factorized circuit,
  whose hardware run tests whether the device composes the three
  multiplication blocks; they serve as references that carry the same ideal
  distribution at a quarter or less of the CZ count.
- Every circuit is compared entry by entry with `diag((-1)^f)`, global
  phase included, because a controlled copy turns a global sign into a
  relative one.
- The 84/84 sedenion ripple circuits are dim 16, where every associator
  phase has degree at most 2, so the CCZ normal form does not apply to them.
