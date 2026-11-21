# IQM Garnet follow-up: Grover depth, single-qubit load, qubit role and sedenion sign-row Walsh peaks

This case follows the retained grover-line-ccz run
([iqm-garnet-grover-line-ccz.md](iqm-garnet-grover-line-ccz.md)) and the gap review of its results
([reconciliation](../archive/reviews/grover-line-gap-review/reconciliation.md), questions 2, 3, 5 and 6). It runs
two jobs on one Garnet calibration set and answers four questions:

1. Does the line-native retention stay geometric at a third depth (k = 3, 42 CZ)?
2. Is the generic compile's loss its single-qubit load or its CZ sequence?
3. Does QB20's lower error follow the qubit or its logical role?
4. Does a sedenion left sign row imprint its exact Walsh peak on four qubits, against its degree-two
   truncation on the identical CZ sequence?

`scripts/iqm_garnet_followup.py` builds the case into
`results/iqm/cases/grover-depth-sedenion-walsh/`; gate core-777 rebuilds it from the retained calibration
copy and compares every byte, core-776 checks every circuit against its exact ideal, and core-775 checks every
sedenion row's oracle against `cd_core.cd_sign`.

## Mechanism

**Depth.** `iqm_grover_line.line_arm` compiles k Grover iterations at 14k CZ. The ideal marked probability
is sin^2((2k + 1) asin(1/sqrt 8)): 0.781, 0.945 and 0.330 at k = 1, 2, 3 (k = 3 over-rotates). Retention
lambda_k = (P_k - 1/8) / (P_k^ideal - 1/8). Two depths fit lambda_k = A r^k exactly (the retained run gives
A = 1.00 +- 0.02 and 0.96 +- 0.03), so a third depth is the first test of the law: lambda_3 - lambda_2^2 /
lambda_1 is zero under it.

**Single-qubit load.** `fused` walks the retained generic compile (qiskit optimization level 3, seed
`iqm_grover_line.TRANSPILER_SEED`, 18 CZ and 68 prx) and merges each run of prx on one qubit between two CZ
into one prx, carrying the residual Z rotation as a frame through the CZ, which commutes with it. The CZ
sequence and its loci stay identical, the unitary agrees to 7e-11, and the count falls to 38 prx. That is the
floor for this CZ sequence: every segment between CZ whose fused rotation is not diagonal keeps one prx, so a
generic compile at 22 prx exists only with another CZ sequence. The line-native compile has 14 CZ and 22 prx.
Fused against generic isolates 30 prx at a fixed CZ sequence; line against fused isolates the CZ sequence
(4 CZ and 16 prx).

**Qubit or role.** The reversed path QB17-QB16-QB20 runs the same line-native circuits. The compile's
measurement locus changes from QB20, QB16, QB17 to QB17, QB16, QB20, so the two end qubits exchange logical
roles while QB16 keeps the middle role. The retained run read wrong-bit probabilities 0.154 on QB20 against
0.180 and 0.178 on QB16 and QB17.

**Sedenion sign rows.** `gororoba_quantum/sedenion_sign_oracle.py` writes the left row of e_m,
diag(cd_sign(16, m, x)), as the phase pi h_m(x) = const + sum_S (pi/8) c_S [S.x], c_S = W(S)/2 from the Walsh
transform of the sign row. Every row carries exactly the eight parities S with S.m odd, each at an odd multiple
of pi/4. A breadth-first search over CNOT networks on the couplers of a four-qubit shape, with a phase at each
parity's first appearance and a free final relabeling, gives the minimal network:

| row popcount | rows | best shape | CNOT (= CZ) |
|---|---|---|---|
| 1 | 4 | T, bit at the center | 8 |
| 2 | 6 | square, bits on opposite corners | 8 |
| 3 | 4 | square | 9 |
| 4 | 1 | square | 10 |

All 90 shape-and-row networks multiply out to the cd_sign row up to the relabeling (residual 1.1e-15). With H
on every wire before and after, the output distribution is P(y) = W(y)^2 / 256: 9/16 on one string, 1/16 on
seven, 0 on eight. The case runs e_5 and e_10 (bits 0 and 2, bits 1 and 3: the two diagonals of the square),
whose peaks sit on different strings.

The mutation arm satisfies the hardware-probe rule
([algebra_circuit_rules.md](../notes/algebra_circuit_rules.md#hardware-probes)): removing the cubic monomials
from h_m leaves a quadratic phase on four of the row's eight parities, so the same network with the other four
phases set to zero realizes it. The CZ sequence is identical (core-776 checks the loci), only the virtual frames
of the prx differ, and the ideal probability at the row's peak falls from 9/16 to 1/4. The null arm sets every
phase to zero: the network becomes a linear relabeling that fixes |0000>, so the ideal output is 0000 and the
row's peak reads only noise.

## Why it needs the service

The model (`iqm_grover_line.predicted`: depolarizing PRX and CZ from the calibration's fidelities, idle T1 and
T2 over the ASAP schedule, herald-conditioned readout) predicted the retained line-minus-generic difference at
+0.035 and the run measured +0.070; it predicts uniform unmarked error and the run rejected that (Wald 95.7 on
6 degrees of freedom). Each question here concerns the part the model leaves out: coherent single-qubit error,
error that grows with depth faster or slower than per-gate depolarizing, and qubit-specific error beyond the
calibration table. Aer answers only the model's own prediction, which the decisions use as the reference.

## Pre-flight

| Question | Hypothesis | Quantity | Falsifier | Model prediction, SE, z | Next step by result |
|---|---|---|---|---|---|
| Depth | lambda_k = A r^k through k = 3 | lambda_3 - lambda_2^2/lambda_1 from raw marked frequencies, per marked string | a deviation beyond 3 SE | +0.010 (101), +0.025 (011); SE of lambda_3 0.037 | inside: geometric budgets stand for 42 CZ; outside: per-iteration error depends on depth (coherent accumulation over-rotates, positive; leakage, negative) |
| Single-qubit load | 30 extra prx cost marked probability | P(101) fused minus generic, four copies each | a resolved negative difference | +0.015, SE 0.0058, z 2.6 | resolved positive: the generic loss is prx error, and every compile fuses single-qubit runs; unresolved: the retained gap lies in the CZ sequence |
| CZ sequence | 14 CZ beat 18 CZ at equal fusion | P(101) line minus fused | a resolved negative difference | +0.020, SE 0.0057, z 3.5 | resolved: line-native synthesis carries the gain on its own |
| Qubit or role | QB20's advantage belongs to the qubit | wrong-bit probability per physical qubit, k = 1 arms, each path | QB20 not lowest on the reversed path while lowest forward | retained 0.154, 0.180, 0.178 | qubit: path choice by per-qubit error; role: the network's position assigns error, and the exchanged network's end wire is the one to protect |
| Sedenion peak | Garnet keeps the row's Walsh peak and the truncation removes it | P(row peak) of row minus truncation, per row; the null arm's floor beside | a difference below 3 SE, or the measured peak on another string | +0.283 (both rows; row 0.511, truncation 0.228, null 0.002 to 0.004), SE 0.016, z 18 | resolved: the eight-CZ sign oracle is a Garnet primitive and the next case composes rows into products; unresolved: the oracle's coherent phase error comes first |

The SE are binomial at the planned shots and the retained run's heralded kept fraction, 85.6 %: 3424 kept
shots per Grover circuit and 856 per sedenion circuit, each arm pooled over its copies.

Probability that each decision resolves (z > 3) when the true difference is the stated row value:

| Scenario | prx load | CZ sequence | sedenion |
|---|---|---|---|
| model | 0.34 (z 2.6) | 0.69 (z 3.5) | 1.00 (z 18) |
| retained line-generic excess, x 2.0 on both Grover terms | 0.99 (z 5.2) | 1.00 (z 7.0) | not applicable |
| contrast at 0.75 of the model (the [kernel cancellation](iqm-garnet-kernel-cancellation-probe.md) and [signed kernel](iqm-garnet-signed-kernel-probe.md) shortfalls) | 0.14 (z 1.9) | 0.36 (z 2.6) | 1.00 (z 13.4) |

The prx-load contrast is underpowered under the model itself; it resolves only if the retained excess is real
and splits as the model's own terms do. The depth test resolves a deviation of lambda_3 larger than 0.11. Both
are stated limits of this budget: a second k = 3 copy lowers the depth SE to 0.026 and k = 5 (70 CZ, ideal
0.548, denominator 0.42 against 0.21) to about 0.019, each for about 0.25 credits more.

Tuna-17 ran two cubic associator classes of dimension 32 through H^4, phase, H^4
([tuna17-walsh-exemplars.md](../notes/quantum_inspire/tuna17-walsh-exemplars.md)); it kept the order of the
classes and rejected the shape of every listed combination. This case reads a different object, one sedenion
sign row on a square, and decides on the peak against a mutation with the same CZ sequence, which the Tuna
series lacked; the shape of the full 16-outcome distribution is reported beside the decision and does not
decide it.

## Case

Calibration set `ea681de1-9661-41e5-bd6f-cb524fa056a6` (snapshot 2026-11-21T04:12Z). The Grover arms run on
the retained case's path, QB20-QB16-QB17, chosen on the earlier calibration and not re-selected here, and on its
reversal. The square is the best of Garnet's 11 squares by predicted mean peak probability of the two rows:
QB11-QB12-QB17-QB16 (0.5115; the next three score 0.5101, 0.5098, 0.5081).

| Job | Circuits | Shots | Order |
|---|---|---|---|
| grover | 29: one iteration line, fused and generic, four copies each; k0; m101-k2, m101-k3; m011-k1, m011-k2, m011-k3; r-m101-k1, r-m011-k1, r-k0; ro-xyz (8) | 4000 | LFG, ro 1-4, GFL, depth and reversed, LFG, ro 5-8, GFL |
| sedenion | 26: s-id, s5-row, s5-trunc, s10-row, s10-trunc, two copies each; ro4-wxyz (16) | 1000 | id, R5, T5, R10, T10, ro4 (16), T10, R10, T5, R5, id |

Each contrast's arms sit at positions mirrored about its job's center, so every arm's summed position is
equal and a drift linear in position cancels; `test_retained_case_mirrors_its_contrasts` checks the
retained bytes. Every circuit runs under the shared Garnet options (all-zeros heralding, one active reset
cycle) and pins the calibration set; a submission after that set retires rebuilds the case, and a changed
build waits for a new approval.

## Seconds and credits

| Job | Requested shots | Expected seconds | Ceiling (garnet) |
|---|---|---|---|
| grover | 116,000 | 4.35 | 3.00 credits |
| sedenion | 26,000 | 0.975 | 1.50 credits |

The builder's `expected_seconds` uses 37.5 us per shot and `ceiling_credits` adds the 1.6 s job overhead at
0.5 credits per second. The retained Garnet run billed 2 s (1.00 credit) for 80,000 requested shots against an
expected 3.0 s, so the expected charge here is about 3 s (1.5 credits) for the grover job and 1 s (0.5 credits)
for the sedenion job: about 2.0 credits, with 4.5 credits as the sum of the ceilings. The balance is 29.00
credits (expires 2026-12-01).

## Preregistered decisions

`prediction.json` (`decisions`) holds each rule with its model value; the analysis decides on these and
nothing else:

- prx load: P(101) of fused minus generic, pooled over four copies each; resolves at z 3.
- CZ sequence: P(101) of line minus fused.
- Depth law, per marked string: lambda_3 - lambda_2^2 / lambda_1 from raw frequencies; the readout-corrected
  value is reported beside.
- Qubit or role: the wrong-bit probability of each physical qubit, pooled over m101-k1 and m011-k1 per path;
  the qubit hypothesis holds when QB20 is lowest on both paths, the role hypothesis when the lowest moves to
  the qubit that takes QB20's forward role.
- Sedenion, per row e_5 and e_10: P(row peak) of row minus truncation, two copies each; the null arm's
  P(row peak) is reported as the floor, and the most frequent string of each row arm must equal the row's
  ideal peak (1001 for e_5 and 0110 for e_10, bit q read from square position q after the network's final relabeling; `prediction.json`, `row_peak`).
- The bit order of the Grover arms follows the retained run: the most frequent outcome of m011 arms is 011.

Mock runs, other case bytes and other calibration sets stay out of the analysis. The analysis module for this
case lands before the run is analyzed and reuses `grover_line_analysis` for the readout correction and the
Wald uniformity statistic of the Grover arms.

## Commands

```sh
"$PYTHON" -B -W error gororoba_quantum/sedenion_sign_oracle.py            # core-775
"$PYTHON" -B -W error scripts/iqm_garnet_followup.py --self-test          # core-776
"$PYTHON" -B -W error scripts/iqm_garnet_followup.py check results/iqm/cases/grover-depth-sedenion-walsh  # core-777
"$PYTHON" -B -W error scripts/iqm_garnet_followup.py build DIR --calibration SNAPSHOT/qc/garnet/calibration
```

The build ran under requirements.txt (qiskit 2.6.2, qiskit-aer 0.18.2, numpy 2.5.4, Python 3.14.9) on the
Zen 4 workstation; the generic arm's gate sequence follows the qiskit release.

## Residual risk

- The model omits coherent error; every Grover prediction is a reference, and the retained run measured twice
  the model's line-minus-generic gain.
- The prx-load decision resolves with probability 0.34 under the model; an unresolved result does not
  separate "no prx effect" from "small prx effect".
- The square was chosen on this calibration by the model's own score; the four best squares lie within 0.004
  of each other, so the choice carries little selection gain.
- The reversed path exchanges the roles of the two end qubits only; QB16 keeps the middle role, so the test
  cannot separate QB16's qubit and role.
- One job per question family and one calibration set: drift between the two jobs enters no decision, since
  each contrast lies inside one job.
