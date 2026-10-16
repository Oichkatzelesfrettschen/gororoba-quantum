# Census-frequency witness under Kingston noise

`scripts/census_frequency_design.py` builds the 5-qubit Hadamard test of
`W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j)` for every ordered sedenion pair
(i, j), 1 <= i, j <= 15, i != j, from `designs.left_mult_gate` exactly as
`scripts/algebra_circuit_fixtures.py` does. It compiles each pair once to the
ibm_kingston calibration snapshot `docs/evidence/calibration/ibm_kingston.json`
(calibration 2026-10-15T19:42:21-07:00, optimization level 3, seed 11) and
samples all 16 data inputs under that snapshot's noise model, 4000 shots
each. [result.json](result.json) is the output of a Kaggle T4 kernel
(qiskit 2.5.2, qiskit-aer 0.17.2); the kernel's measured substrate
([kaggle_environment.json](kaggle_environment.json)) and its hypercomplex
stack proof ([kaggle_hypercomplex.json](kaggle_hypercomplex.json),
`identical: true`) sit beside it. Gate core-288 recomputes the summary from
the retained records exactly and reruns pairs (1, 2) and (2, 1) on the CPU.

W_ij and W_ji are different circuits: their signs differ on 336 of the 1680
(i < j, k) triples, so every ordered pair runs its own circuit. Pairs with
i = 0, j = 0 or i = j have W = +-I and enter the census at their exact value.

## Result

| Quantity | Value |
| --- | --- |
| Ideal census, P(c = 1) over 4096 triples | 231/512 = 0.451172 |
| Compiled CZ per test, mean (range) | 433.9 (412 to 457) |
| Visibility per pair, mean (range) | 0.357 (0.327 to 0.387), sd 0.012 |
| Bright visibility V+ (omega = +1 triples) | 0.370 |
| Dark visibility V- (omega = -1 triples) | 0.346 |
| Noisy census | 0.419873 |
| Common-visibility prediction 1/2 - V (1/2 - 231/512) | 0.424786 |
| Two-reference census, V+ and V- pooled over all pairs | 0.451172 |
| Two-reference census, V+ and V- from one pair, range over 210 pairs | 0.4299 to 0.4699 |
| Total shots for +-0.01 at 2 sigma at the simulated visibility | 78,601 |

## Readings

- **One visibility does not describe the witness.** Bright triples keep more
  contrast than dark ones, so the common-visibility formula misses the noisy
  census by 0.0049, about half the target resolution. The estimator
  `f = (P - (1 - V+)/2) / ((V+ + V-)/2)` with separate bright and dark
  references recovers 231/512 when the references are pooled over every
  pair (by construction here, since they come from the same triples). A
  bias toward outcome 0 explains the split: P(c = 1) = 1/2 - V omega / 2 - b
  gives V+ - V- = 4b, so b is about 0.006 (inferred; control relaxation and
  readout asymmetry both produce it, and a run with the control's readout
  calibrated separately would split them).
- **References from one pair carry a +-0.02 systematic.** Per-pair
  visibility varies with the compiled circuit (sd 0.012), so bright and dark
  references taken from one pair move the census over 0.430 to 0.470, twice
  the +-0.01 target. A hardware design pools its references over many pairs,
  or interleaves references from the same compiled circuits it samples.
- **The shot cost depends on the hardware visibility, which simulation does
  not give.** At the simulated V = 0.357 the census needs about 79k shots in
  total. The walk scaffold measured hardware loss per CZ 1.8 to 4.4 times
  the calibrated model's on the same backends
  (`docs/evidence/walk-control-scaffolding/README.md`). If that ratio holds
  over 434 CZ and visibility decays exponentially in the CZ count (an
  assumption; confirming it needs one bright and one dark pair on hardware),
  V falls to 0.156 to 0.011, and the shots to about 409k to 87 million. At
  the 250 us default repetition delay, 409k shots already exceed 100 s,
  against 266 s left at the last recorded service inventory.

## Consequence for the proposed experiment

The census test (`proposed-census-frequency`) needs a cheaper witness
circuit before a hardware case. The CCZ normal form compiles the dim-32
associator phase to about 30 CZ against about 125 for the factorized form
(`docs/evidence/simulation-notebook-audit/README.md`), and a sedenion
version of that reduction is the next design step. A case also needs one
hardware bright/dark pair to replace the visibility assumption above with a
measurement.
