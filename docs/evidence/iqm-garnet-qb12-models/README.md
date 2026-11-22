# QB12 fault models on the Garnet sedenion Walsh run

`qb12_models.py` compares five models of a QB12 fault on the retained sedenion job of the Garnet follow-up
(`results/iqm/runs/2026-11-21T220406Z-garnet-grover-depth-sedenion-walsh-sedenion`, calibration set ea681de1) and
writes `qb12_models.json`. It is a descriptive comparison written after the analysis of the job and decides nothing;
the design's Result ([iqm-garnet-grover-depth-sedenion-walsh](../../design/iqm-garnet-grover-depth-sedenion-walsh.md))
states the reading. Gate `core-iqm-garnet-qb12-models-replay` reruns it and compares the bytes (266 s on the compute
workstation, one process pool of the fit starts).

## Mechanism

- Both null arms, s5-id and s10-id, are the identity for every static QB12 state: the script certifies it on the
  noiseless circuits (largest entry of U - I 2e-11 on the qubit subspace) and refuses to fit otherwise.
- Every model carries the calibration's depolarizing PRX and CZ error and the herald-conditioned readout of QB11, QB17
  and QB16 (`scripts/iqm_sim.py`, `Calibration`). A CZ's two-qubit depolarizing error enters as the same parameter
  on each of its qubits, a stated approximation. QB12 is a three-level system; level 2 reads as 1. QB12's two readout
  errors are free in every model.
- Each model is fitted by L-BFGS-B to the multinomial likelihood of all 28 circuits (12 sedenion arms and 16 readout
  preparations, 17,976 kept shots) from a fixed grid of starts, so no random number enters.

## Result

| model | parameters (radians for phases) | deviance | df | AIC | BIC |
|---|---|---|---|---|---|
| frequency | delta 0.7922, e01 0.0332, e10 0.2149, eta -0.5985, p 0.1439, phi 2.4576 | 1901 | 414 | 44212.9 | 44259.7 |
| leakage | e01 0.0307, e10 0.3623, l 0.5, p 0.1765, theta2 -0.0002 | 2857.6 | 415 | 45167.5 | 45206.5 |
| transition | e01 0.0797, e10 0.3182, p 0.201, q 0.1741 | 4317.1 | 416 | 46625 | 46656.2 |
| static | e01 0.0684, e10 0.3075, p 0.2402 | 8158.9 | 417 | 50464.8 | 50488.2 |
| readout | e01 0.2184, e10 0.4574 | 8158.9 | 418 | 50462.8 | 50478.4 |

- The frequency-shift model (an excited population p the zeros herald keeps, a detuning eta that tilts each QB12 prx
  axis toward Z, a QB12 phase phi after each of its CZs and a conditional-phase error delta on them) leads by 955 in
  AIC over leakage and reproduces the s10-id table of QB11 and QB17 given QB12 (`s10_id_table` against
  `observed`).
- The leakage fit sits at the bound l = 0.5 of its transfer probability, so its deviance is an upper bound for that
  family within the bounds.
- The static model gains nothing over readout alone: a static excitation leaves both null arms unchanged.
- No model reaches the saturated fit (deviance 1901 on 414 degrees of freedom for the best), so the comparison ranks
  hypotheses and does not identify a mechanism. hypothesis: QB12's frequency moved between the calibration at 02:43
  UTC and the job at 22:03 UTC; the next calibration set's QB12 frequency and T2, and a QB12 Ramsey with a CZ-phase
  echo, test it.

## Command

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-qb12-models/qb12_models.py OUT.json
```
