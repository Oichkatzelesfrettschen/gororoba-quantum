# IQM Garnet follow-up: Grover depth, single-qubit load, qubit role and sedenion sign-row Walsh peaks

This case follows the retained grover-line-ccz run
([iqm-garnet-grover-line-ccz.md](iqm-garnet-grover-line-ccz.md)) and the gap review of its results
([reconciliation](../archive/reviews/grover-line-gap-review/reconciliation.md), questions 2, 3, 5 and 6). It runs
two jobs on one Garnet calibration set and answers four questions:

1. Does the line-native retention stay geometric at a third depth (k = 3, 42 CZ)?
2. How much of the generic compile's loss is single-qubit load, at a fixed CZ sequence?
3. Does QB20's lower error follow the qubit or its logical role?
4. Does a sedenion left sign row imprint its exact Walsh peak on four qubits, against its degree-two
   truncation and a null on the identical CZ list?

`scripts/iqm_garnet_followup.py` builds the case into
`results/iqm/cases/grover-depth-sedenion-walsh/`; gate core-777 rebuilds it from the retained calibration
copy and compares every byte, core-776 checks every circuit against its exact ideal, and core-775 checks every
sedenion row's oracle against `cd_core.cd_sign`. The review of this case is recorded in
[garnet-followup-case](../archive/reviews/garnet-followup-case/reconciliation.md).

## Mechanism

**Depth.** `iqm_grover_line.line_arm` compiles k Grover iterations at 14k CZ. The ideal marked probability
is sin^2((2k + 1) asin(1/sqrt 8)): 0.781, 0.945 and 0.330 at k = 1, 2, 3 (k = 3 over-rotates). Retention
lambda_k = (P_k - 1/8) / (P_k^ideal - 1/8). Two depths fit lambda_k = A r^k exactly (the retained run gives
A = 1.00 +- 0.02 and 0.96 +- 0.03), so a third depth is the first test of the law: f = lambda_3 -
lambda_2^2 / lambda_1 is zero under it.

**Single-qubit load.** Four one-iteration arms form a two-by-two design. The generic arm is qiskit's
optimization level 3 at the retained seed `iqm_grover_line.TRANSPILER_SEED` with the logical wires permuted by
`GENERIC_PERMUTATION` = (2, 0, 1): of the six permutations, this one measures logical bit q on path position q,
the line-native arm's mapping, at the retained compile's 18 CZ and 68 prx (the retained generic compile measured
QB16, QB17, QB20 and is not rerun). `fused` walks that compile and merges
each run of prx on one qubit between two CZ into one prx, carrying the residual Z rotation as a frame through
the CZ, which commutes with it: the CZ list and loci stay identical, every computational-basis probability
agrees to 4e-11, and the count falls to 38 prx (the native compiles drop their final Z frames, so the
operators themselves differ by those frames). 38 is the floor of frame fusion at this CZ sequence, since every
segment between CZ whose fused rotation is not diagonal keeps one prx; a resynthesis that moves the CZ list
was not searched. Fusing all six logical-wire permutations at the retained seed gives 37 or 38 prx, so the
requested 22-prx generic arm does not exist on this route. `padded` inserts 8 identity pairs prx(pi/2, 0)
prx(pi/2, pi) into the line-native arm, placed so that its per-qubit prx counts match the fused arm's within one
(18, 11, 9 on QB16, QB17, QB20 against 18, 12, 8), bringing it from 22 to 38 prx at its own 14-CZ list.

| Arm | CZ | prx | measurement locus | model P(101) |
|---|---|---|---|---|
| line (L) | 14 | 22 | QB20, QB16, QB17 | 0.678 |
| padded line (P) | 14 | 38 | QB20, QB16, QB17 | 0.670 |
| fused generic (F) | 18 | 38 | QB20, QB16, QB17 | 0.657 |
| generic (G) | 18 | 68 | QB20, QB16, QB17 | 0.642 |

L - P (16 prx) and F - G (30 prx) each change only the prx count at a fixed CZ list. P - F holds the prx count
at 38 (per qubit within one) and the measurement mapping, and changes only the CZ list.

**Qubit or role.** The reversed path QB17-QB16-QB20 runs the same line-native circuits. Its measurement locus
is QB17, QB16, QB20 against QB20, QB16, QB17 forward, so the two end qubits exchange logical roles while QB16
keeps the middle. On mark 101 both end bits are ideally 1, so D = w(QB17) - w(QB20), the difference of their
wrong-bit probabilities, compares the two qubits alone; on mark 011 the ends are ideally 0 and 1 and D mixes
qubit quality with the asymmetry of e01 and e10. The retained run read, readout-corrected, D = +0.023 on
m101-k1 (w = 0.154 on QB20, 0.178 on QB17) and D = -0.026 on m011-k1; from raw frequencies, with the paired per-shot variance, D = +0.0204 +- 0.0039 (z 5.3,
13,688 kept shots) on m101-k1 and -0.019 +- 0.008 on m011-k1.

**Sedenion sign rows.** `gororoba_quantum/sedenion_sign_oracle.py` writes the left row of e_m,
diag(cd_sign(16, m, x)), as the phase pi h_m(x) = const + sum_S (pi/8) c_S [S.x], c_S = W(S)/2 from the Walsh
transform of the sign row. Every row carries exactly the eight parities S with S.m odd, each at an odd multiple
of pi/4. A breadth-first search over CNOT networks on the couplers of a four-qubit shape, with a phase at each
parity's first appearance and a final wire permutation, gives the minimal network:

| row popcount | rows | best shape | CNOT (= CZ) |
|---|---|---|---|
| 1 | 4 | T, bit at the center | 8 |
| 2 | 6 | square, bits on opposite corners | 8 |
| 3 | 4 | square | 9 |
| 4 | 1 | square | 10 |

All 90 shape-and-row networks multiply out to the cd_sign row up to the permutation (residual 1.1e-15). With H
on every wire before and after, the output distribution is P(y) = W(y)^2 / 256: 9/16 on one string, 1/16 on
seven, 0 on eight. The case runs e_5 and e_10 (bits 0 and 2, bits 1 and 3: the two diagonals of the square),
whose peaks sit on different strings (1001 and 0110, bit q read from square position q).

The mutation arm satisfies the hardware-probe rule
([algebra_circuit_rules.md](../notes/algebra_circuit_rules.md#hardware-probes)): removing the cubic monomials
from h_m leaves a quadratic phase whose parity expansion lies on four of the row's eight parities, with changed
coefficients (for e_5, parity 3 moves from 2 to 4 eighths of pi), so the row's network with the other four
phases removed realizes it. For the ten rows of popcount 1 and 2 the truncation fits the row's parities; for
the five of popcount 3 and 4 it does not. The CZ list and loci are identical (core-776 and an audit test check
the retained bytes); the prx count falls from 12 to 8, because a zero phase lets the Hadamards of a CNOT on
either side of it fuse away. The ideal probability at the row's peak falls from 9/16 to 1/4. Each row's null
arm runs that row's network with every phase zero: a linear relabeling that fixes |0000>, so the ideal output
is 0000 and the row's peak reads only noise, on the same CZ list with 4 prx.

## Why it needs the service

The model (`iqm_grover_line.predicted`: depolarizing PRX and CZ from the calibration's fidelities, idle T1 and
T2 over the ASAP schedule, herald-conditioned readout) predicted the retained line-minus-generic difference at
+0.035 and the run measured +0.070; it predicts uniform unmarked error and the run rejected that (Wald 95.7 on
6 degrees of freedom); it rates QB20 the worst of the three path qubits and the run measured it best. Each
question here concerns the part the model leaves out: coherent single-qubit error, error that grows with depth
faster or slower than per-gate depolarizing, and qubit-specific error beyond the calibration table. Aer answers
only the model's own prediction, which the decisions use as the reference.

## Pre-flight

| Question | Hypothesis | Quantity | Falsifier | Model prediction, SE, z | Next step by result |
|---|---|---|---|---|---|
| Depth | lambda_k = A r^k through k = 3 | f = lambda_3 - lambda_2^2/lambda_1 from raw marked frequencies, per marked string | f beyond 3 SE of the model's f (raw frequencies carry readout, so the model's f is not zero) | +0.010 (101), +0.025 (011); SE 0.041 by the delta method over the three arms | inside: geometric budgets stand for 42 CZ; outside: per-iteration error depends on depth (coherent accumulation, leakage) |
| prx load, generic | 30 extra prx cost marked probability at 18 CZ | P(101) fused minus generic, four copies each | a resolved negative difference | +0.015, SE 0.0058, z 2.64 | resolved: the generic loss includes prx error, and every compile fuses single-qubit runs |
| prx load, line | 16 identity-pair prx cost marked probability at 14 CZ | P(101) line minus padded line | a resolved negative difference | +0.0085, SE 0.0057, z 1.50 | with the generic contrast, a per-prx cost on two CZ sequences |
| CZ sequence | 14 line-native CZ beat 18 generic CZ at equal prx and mapping | P(101) padded line minus fused generic | a resolved negative difference | +0.013, SE 0.0057, z 2.24 | resolved: the CZ list carries the line-native gain on its own |
| Qubit or role | QB20's advantage belongs to the qubit | D = w(QB17) - w(QB20), raw, on m101-k1 forward and r-m101-k1 reversed (four copies each), paired per-shot SE | given a resolved forward D, a resolved reversed D of opposite sign | model D -0.010 forward and -0.009 reversed, paired SE 0.0038 each (z -2.66, -2.38); retained raw forward D +0.020, paired SE 0.0039 (z 5.3) | qubit: choose paths by per-qubit error; role: the network's position assigns error, and the exchanged network's end wire is the one to protect |
| Sedenion peak | Garnet keeps the row's Walsh peak and the truncation removes it | P(row peak) of row minus truncation, per row; row minus the row's null | a difference below 3 SE, a row peak within 3 SE of its null, or the row arms' most frequent string not the row peak | +0.283 (both rows; row 0.511, truncation 0.228, null 0.002 and 0.003), SE 0.016, z 17.97; row minus null z 42 | resolved: the eight-CZ sign oracle is a Garnet primitive and the next case composes rows into products; unresolved: the oracle's coherent phase error comes first |

The SE are binomial (paired multinomial for D) at the planned shots and the retained run's heralded kept
fraction, 85.6 %: 3424 kept shots per Grover circuit and 856 per sedenion circuit, each arm pooled over its
copies.

Probability that each decision resolves (z > 3) when the true difference is the stated row value:

| Scenario | prx load, generic | prx load, line | CZ sequence | sedenion |
|---|---|---|---|---|
| model | 0.36 (z 2.64) | 0.07 (z 1.50) | 0.22 (z 2.24) | 1.00 (z 17.97) |
| retained line-generic excess, x 2.0 on every Grover term | 0.99 (z 5.3) | 0.50 (z 3.0) | 0.93 (z 4.5) | not applicable |
| contrast at 0.75 of the model (the [kernel cancellation](iqm-garnet-kernel-cancellation-probe.md) and [signed kernel](iqm-garnet-signed-kernel-probe.md) shortfalls) | 0.15 (z 1.98) | 0.03 (z 1.12) | 0.09 (z 1.68) | 1.00 (z 13.4) |

The single-qubit contrasts resolve only if the retained excess is real and splits as the model's terms do; an
unresolved result does not separate "no effect" from "small effect", and the two prx contrasts together bound
a per-prx cost. The role decision resolves the forward D at z about 5.3 if the retained raw +0.020 repeats, and
the reversed D at |D| > 0.011. The depth statistic
resolves a deviation of f above 0.12; a second k = 3 copy or k = 5 (70 CZ, ideal 0.548, denominator 0.42
against 0.21) lowers that, each for about 0.25 credits more.

Tuna-17 ran two cubic associator classes of dimension 32 through H^4, phase, H^4
([tuna17-walsh-exemplars.md](../notes/quantum_inspire/tuna17-walsh-exemplars.md)); it kept the order of the
classes and rejected the shape of every listed combination. This case reads a different object, one sedenion
sign row on a square, and decides on the peak against a mutation and a null with the same CZ list, which the
Tuna series lacked; the shape of the full 16-outcome distribution is reported beside the decision and does not
decide it.

## Case

Calibration set `ea681de1-9661-41e5-bd6f-cb524fa056a6` (snapshot 2026-11-21T04:12Z). The Grover arms run on
the retained case's path, QB20-QB16-QB17, chosen on the earlier calibration and not re-selected here, and on its
reversal. The square is the best of Garnet's 11 squares by predicted mean peak probability of the two rows on
this calibration: QB11-QB12-QB17-QB16 (0.5115; the next three score 0.5101, 0.5098, 0.5081). The builder
freezes it (`SQUARE`): a rebuild on a later calibration keeps the square and records the new scores beside it.

| Job | Circuits | Shots | Order |
|---|---|---|---|
| grover | 36: one iteration line, padded, fused and generic, four copies each; m101-k2, m101-k3, m011-k1, m011-k2, m011-k3, k0; r-m101-k1 (four copies) and r-m011-k1 (two); ro-xyz (8) | 4000 | LPFG, ro 1-4, R101 R011, GFPL, R101, depth block, R101, LPFG, R011 R101, ro 5-8, GFPL |
| sedenion | 28: id, row and truncation for e_5 and e_10, two copies each; ro4-wxyz (16) | 1000 | id5 id10 R5 T5 R10 T10, ro4 (16), T10 R10 T5 R5 id10 id5 |

Every multi-copy arm of a decision sits at positions mirrored about its job's center, so its summed position
equals every other's and a drift linear in position cancels from each pairwise contrast;
`test_retained_case_mirrors_its_contrasts` checks the retained bytes. The depth arms and k0 form one block at
the center and are not mirrored: a linear drift enters each depth statistic through offsets of at most three
positions, about 0.0006 at the retained copy slope of 0.0002 per position against an SE of 0.041. Every circuit
runs under the shared Garnet options (all-zeros heralding, one active reset cycle) and pins the calibration
set; a submission after that set retires rebuilds the case, and a changed build waits for a new approval.

## Seconds and credits

| Job | Requested shots | Expected seconds | Ceiling (garnet) |
|---|---|---|---|
| grover | 144,000 | 5.40 | 3.50 credits |
| sedenion | 28,000 | 1.05 | 1.50 credits |

The builder's `expected_seconds` uses 37.5 us per shot and `ceiling_credits` adds the 1.6 s job overhead at
0.5 credits per second, rounded up to whole seconds. The retained Garnet Grover job ran 1.27 s of runtime for
80,000 requested shots (compiled estimate 2.14 s) and billed 2 s, 1.00 credit; IQM bills the runtime rounded
up. Scaling that runtime by requested shots gives 2.3 s for the grover job (3 s billed, 1.50 credits) and
0.45 s for the sedenion job (1 s, 0.50 credits): about 2.0 credits in all. That is an extrapolation from one
job; the k = 3 arms are longer than any retained circuit (42 CZ against 28). The other retained Garnet job of
these options, the QET ladder, billed 13 s for 38,400 kept shots because its circuits were long (compiled
estimate 13.4 s). The ceilings, which `iqm_jobs.py submit` enforces and the approval quotes, sum to 5.0
credits, above the "about 1 to 3 credits" scope. The balance read 29.00 credits on 2026-11-20 (expires
2026-12-01).

## Preregistered decisions

`prediction.json` (`decisions`) holds each rule with its model value; the analysis decides on these and
nothing else:

- prx load, generic: P(101) of fused minus generic, pooled over four copies each; resolves at z 3.
- prx load, line: P(101) of line minus padded line.
- CZ sequence: P(101) of padded line minus fused generic, at equal prx and one measurement mapping.
- Depth law, per marked string: f from raw frequencies against the model's f; the readout-corrected f is
  reported beside. k0's corrected uniformity Wald statistic is the reference of the unmarked-uniformity test,
  as in the retained analysis.
- Qubit or role: D = w(QB17) - w(QB20) on m101-k1 and r-m101-k1 with the paired per-shot variance; when the
  forward D resolves, a resolved reversed D of the same sign keeps the difference with the qubits, one of the
  opposite sign moves it with the roles, and anything else leaves the question open; the m011 arms are
  reported beside.
- Sedenion, per row e_5 and e_10: P(row peak) of row minus truncation, two copies each, resolved at z 3; the
  row's P(row peak) must also exceed its null arm's by 3 SE, and the most frequent string of the row arms must
  equal the row's ideal peak (1001 for e_5 and 0110 for e_10; `prediction.json`, `row_peak`).
- The bit order of the Grover arms follows the retained run: the most frequent outcome of m011 arms is 011.
- Binding: `cases.json` carries `prediction_sha256`, and `iqm_records.validate_job`, which submission, the
  run copy and the analysis reader all pass through, refuses a case whose `prediction.json` differs from it.

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
Zen 4 workstation; the generic and fused arms' gate sequences follow the qiskit release.

## Residual risk

- The model omits coherent error; every Grover prediction is a reference, and the retained run measured twice
  the model's line-minus-generic gain.
- The single-qubit contrasts resolve with probability 0.36 and 0.07 under the model.
- The peak observable is a probability of a real Walsh amplitude: a pure diagonal phase error delta_x moves it
  at second order (the first-order term of |W|^2 is 2 W Re(i sum_x s_x (-1)^(y.x) delta_x / 16) = 0), while prx
  over-rotations enter at first order; `scripts/iqm_probe_audit.py`, which computes such responses for the
  signed kernel probe, was not run on these circuits.
- The generic arms use the mapped permutation, not the retained generic compile, so this job does not replicate
  the retained line-minus-generic difference itself.
- IQM's server compiler might merge adjacent prx; then the padded and generic arms would run fewer pulses than
  their files hold, and L - P and F - G would read zero. Hypothesis; the retained generic arm's loss argues
  against it.
- The square was chosen on calibration ea681de1 by the model's own score and is frozen; the four best squares
  lie within 0.004 of each other, so the choice carries little selection gain.
- The reversed path exchanges the roles of the two end qubits only; QB16 keeps the middle role, so the test
  cannot separate QB16's qubit and role.
- The depth arms are centrally grouped, not mirrored.
- One calibration set for both jobs: drift between the two jobs enters no decision, since each contrast lies
  inside one job.
