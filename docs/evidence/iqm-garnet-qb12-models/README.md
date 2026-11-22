# QB12 fault models on the Garnet sedenion Walsh run

`qb12_models.py` compares models of a QB12 fault on the retained sedenion job of the Garnet follow-up
(`results/iqm/runs/2026-11-21T220406Z-garnet-grover-depth-sedenion-walsh-sedenion`, calibration set ea681de1) and
writes `qb12_models.json`. It is a descriptive comparison written after the analysis of the job and decides nothing;
the design's Result ([iqm-garnet-grover-depth-sedenion-walsh](../../design/iqm-garnet-grover-depth-sedenion-walsh.md))
states the reading. Gate `core-iqm-garnet-qb12-models-replay` reruns it and compares the bytes (about 27 minutes on
the compute workstation).

## Mechanism

- Both null arms, s5-id and s10-id, are the identity on the computational space: every gate between each partner's
  prx layers is a CZ, all of them diagonal, each pair of qubits meets in exactly two of them, and the two prx layers
  are inverses. The script certifies it on the noiseless circuits (largest entry of U - I 2e-11) and refuses to fit
  otherwise. A static QB12 state therefore moves neither partner, and a static excited population only re-labels
  QB12's readout.
- Every model carries the calibration's depolarizing PRX error, the two-qubit depolarizing CZ error (the
  sixteen-Pauli channel of parameter 4(1 - F)/3, QB12's Paulis acting as the identity on its level 2) and the
  herald-conditioned readout of QB11, QB17 and QB16 (`scripts/iqm_sim.py`, `Calibration`). QB12 is a three-level
  system; level 2 reads as 1. QB12's readout errors are free in every model.
- Every fault model shares the same QB12 single-qubit terms (an excited population p kept by the zeros herald, a
  detuning eta of each QB12 prx, a QB12 phase phi after each of its CZs) and adds its own: a CZ conditional-phase
  error (cz_phase), a QB12 bit flip after each of its CZs (transition), a 1 -> 2 transfer with its partner phase
  (leakage), or all of them (hybrid). Starting points come from a fixed grid and from each model's nested parents.

## Result

| model | parameters (radians for phases) | deviance | nominal df | AIC |
|---|---|---|---|---|
| hybrid | delta -0.7986, e01 0.0785, e10 0.2774, eta 0.6094, l 0.416, p 0.0119, phi -1.9134, q 0.0656, theta2 -2.5301 | 1102.8 | 411 | 43420.7 |
| transition | e01 0.0876, e10 0.0908, eta 0.7855, p 0, phi 0.8383, q 0.1106 | 1420.1 | 414 | 43732 |
| leakage | e01 0.0016, e10 0.2843, eta -0.377, l 0.3111, p 0.1757, phi -1.7002, theta2 0.6016 | 1442.7 | 413 | 43756.6 |
| cz_phase | delta -0.7974, e01 0.0348, e10 0.221, eta 0.5914, p 0.1457, phi -2.4546 | 1971.3 | 414 | 44283.2 |
| single | e01 0.1142, e10 0.2416, eta 0.5997, p 0, phi 1.6567 | 3172.7 | 415 | 45482.6 |
| readout | e01 0.216, e10 0.4556 | 8834.4 | 418 | 51138.3 |

- A QB12 state change during the CZ sequence ranks first: transition and leakage each lower the deviance by about
  1740 below the shared single-qubit terms, a conditional-phase error alone by about 1201, and the hybrid of all three
  lowers it by about 317 more. Each model's chosen optimum converged; the single and transition models' excited
  population p sits at the bound 0, which the record lists (`at_bound`).
- Every fault model searches its own full grid of starting points and its nested parents' optima (the hybrid its
  parents' only). A first version that seeded each model from its parent alone found the same order but higher
  deviances for the conditional-phase model (2186) and the hybrid (1182), so the ranking is not an artifact of one
  basin; the gate's replay takes about 27 minutes.
- No model fits absolutely (the hybrid's deviance is 1102.8 on a nominal 411 degrees of freedom). The likelihood
  multiplies the 28 circuits as independent multinomials while one playlist runs every circuit once per shot, so it
  is a composite likelihood: the deviances rank the models, and their degrees of freedom and information criteria lack
  the usual calibration.
- The models hold QB12's starting state fixed across the job, and the job contradicts it (`job_order`): in the
  readout preparations that leave QB12 in 0, QB12 reads 1 in 0.122, 0.072, 0.076 and 0.060 of the kept shots in
  succession (and 0.129, 0.109, 0.084, 0.057 in the second run of them), while the kept shots climb from 584 to 763,
  and the first preparation that drives QB12 (ro4-0100) is followed by a drop to 637 kept shots. The two copies of the
  e_10 null arm read QB12 at 0.298 and 0.227. hypothesis: QB12's excitation carries from one circuit to the next
  through active reset and the zeros herald; a model whose starting state depends on the circuit before it is the
  next test, on the retained shots.

## The next calibration set

`calibration-a0e725eb-QB12.json` retains a free calibration read of 2026-11-22T04:38Z. Garnet's set a0e725eb (created
2026-11-22T03:02Z) lists QB12 in no prx, cz, measure, reset_wait, cc_prx, prx_12 or measure_012 locus, only under
measure_fidelity, and carries PRX benchmarks for the other 19 qubits only. Its QB12 readout reads fidelity 0.802
(errors 0.313 from 1 to 0 and 0.083 from 0 to 1) against 0.985 (0.019 and 0.010) in ea681de1. The provider has taken
QB12 out of the gate set: the fault the retained jobs show persists into the next calibration, and no case can
address QB12 until a later set restores it.

## Command

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-qb12-models/qb12_models.py OUT.json
```
