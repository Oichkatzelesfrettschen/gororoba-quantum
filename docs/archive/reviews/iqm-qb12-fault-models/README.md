# Review record: post-hoc QB12 fault models, packed settling and Grover positions

Reviewers (owner's selection for pull requests 978 to 981, 2026-11-22): codex on gpt-daybreak-blue at high and grok as reviewers; agy on gemini-4-neon-high and opencode on opencode-go/deepseek-v4-pro as red-teamers; the Advisor last. All four read one brief covering the four pull requests at the heads below; this record keeps the findings on pull request 979 (head read e65ccd521). Raw reports stay outside the tree.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, agy | The CZ error entered as the two-qubit parameter on each qubit separately, about 1.6 times the calibrated infidelity | Fixed in 060df813d: the sixteen-Pauli two-qubit channel |
| 2 | codex, agy, opencode, grok | The model families were exclusive and unequal: only the frequency model had QB12's single-qubit terms, leakage was capped at 0.5 and no hybrid was fitted; with shared terms leakage reaches 1405 against 1901 | Fixed in 060df813d: every fault model shares the single-qubit base, leakage may reach 1, a hybrid joins; the ranking is now hybrid 1102.8, transition 1420, leakage 1443, conditional phase 1971.3. The Result states it in 2cb6a6467 |
| 3 | codex | The 28 circuits share one playlist, so the multinomial product is a composite likelihood whose degrees of freedom and criteria lack calibration | Fixed: the script docstring and the README state it |
| 4 | codex | Optimizer convergence was discarded | Fixed: each model records converged, iterations and the parameters at a bound |
| 5 | agy | The QB12 table dropped shots with QB16 = 1 instead of marginalizing | Fixed in 060df813d |
| 6 | agy | The static model is the readout model re-labelled | Fixed: static is dropped and the docstring states why |
| 7 | agy, grok | QB12's starting state is not stationary: the readout preparations show excitation carrying between circuits, and the two e_10 null copies read QB12 at 0.298 and 0.227 | Boundary: the record lists every circuit's kept shots and QB12 reading in job order and states the carryover as a hypothesis with its next test; no model holds it |
| 8 | codex, grok | The settling paragraph attributes the deficit to a six-circuit decay, while place, circuit identity and pair are confounded and the residuals are not monotone | Fixed in 2cb6a6467: confounding, the non-monotone sequence and the double all-ones adjacency stated; a rotated playlist named as the test |
| 9 | agy | Settling residuals used the full-job arm mean, including the circuit itself | Fixed in 060df813d: per-half references over the arm's other circuits with a combined error |
| 10 | codex, agy, grok | "Drift is closed" overstates a linear check, and the script opened with the corrected statistic instead of the preregistered raw one | Fixed: an inner-versus-outer check (-0.0005 +- 0.0036) joins, a step or circuit-specific effect at positions 15 and 16 is stated as open, and the opening states raw f -0.122 +- 0.039 against 0.010 |
| 11 | codex, grok | The correction note said every other gate between a partner's prx layers acts on another qubit; the partner's CZs with QB16 sit there | Fixed in 2cb6a6467 |
| 12 | agy, opencode | QB12 stays in the measure_fidelity locus of set a0e725eb | Fixed: the design names that exception |
| 13 | grok | "Reproduces the s10-id table" overstated a one-table prediction for two copies | Fixed: the README no longer says it |
| 14 | opencode | A claim pairs a raw f with a corrected-f z | Refuted: z -3.37 = (-0.1222 - 0.0104) / 0.0393, the raw statistic of analysis.json |
| 15 | agy | Unused names ARMS and positions in qb12_models.py | Fixed in 060df813d |
| 16 | agy | positions.py moves the k = 2 and 3 arms by an additive slope rather than one scaled with depth | Boundary: with every offset under 2.5 positions a depth-scaled slope still moves f by under 0.01; the README states the additive model |
| 17 | agy | The wrap loop of settling.py changes no count on this playlist, and circuit-002 follows two all-ones references across the wrap | Fixed: the design states the double adjacency; the loop stays, since a playlist whose all-ones reference is not last needs it |
| 18 | opencode | Level 2 reads as 1 is an untested readout assumption | Boundary: the docstring and README state it; a measure_012 readout is named in the QB12 test |
| 19 | grok | "No model reaches the saturated fit (deviance 1901 ... for the best)" reads ambiguously | Fixed: the README states the best model's deviance against its nominal degrees of freedom |
| 20 | Advisor | The ranking rested on starts seeded from one optimum | Fixed: every fault model also searches its own full grid; the conditional-phase model improves to 1971.3 and the hybrid to 1102.8, and the order holds |
