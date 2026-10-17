# Split linear encodings of N=21 order finding

A per-round linear encoding of the work register lowers the ten-round
circuit's routed CZ. Among the routed two-round candidates, none beats a
single encoding.

- **Ten-round.** The best split holds coset 15265 for rounds 1 to 9 and
  coset 111 for round 10, joined by a 3-CNOT transition. It routes to a
  median 3,754 CZ on FakeFez and FakeKingston, 179 below the best single-B
  circuit (coset 15241, 3,933). On the Garnet square grid it routes to
  3,026.5, against 3,190 for the best single B.
- **Two-round, routed.** None of the 16 routed two-round splits beats the
  best single-B circuit on any target. The claim covers those candidates
  only. A split of higher surrogate cost that routes better stays
  unsearched.
- **Two-round, surrogate.** No split has a lower surrogate cost than the
  single-B optimum of 372. That is a theorem of the surrogate, not a routed
  bound.

`split.json` holds the record, which
[`scripts/gl52_split_conjugators.py`](../../../scripts/gl52_split_conjugators.py)
writes. No QPU job ran.

## Construction

Round k encodes the work register as `x_k = B_k^-1 v`, and applies the
one-clean target-flip network of `B_k^-1 f_k B_k` under the phase control.

- **Transition.** Between rounds k and k+1 the uncontrolled map
  `T_k = B_(k+1)^-1 B_k` carries `x_k` to `x_(k+1)`. That is the inverse of
  `B_k^-1 B_(k+1)` and costs the same number of CNOTs.
- **Placement.** The transition sits on the work qubits right after round
  k's network. The H, if_else, measure and reset between rounds act on the
  control alone, so the phase register keeps the unencoded law.
- **Cost.** The schedule costs `sum_k s(B_k^-1 f_k B_k) + sum_k d(T_k)`. An
  uncontrolled CNOT weighs 1, the same as `CONTROLLED_CX_COST[0]`.
- **Exact checks.** The record retains three checks:
  - the challenger's conjugation and controlled-network checks on every
    column order a split uses;
  - an Operator check of every emitted transition on all 32 register values;
  - a check that the split builder, given one encoding for every round,
    emits `factor_order_finding(work_columns=B)` exactly.
- **Sampled check.** Aer's seeded phase counts (4,000 shots) match the
  unencoded circuit's with total variation 0 for all 32 splits.

## CNOT distance in GL(5,2)

A breadth-first search from the identity reaches all 9,999,360 invertible
matrices over the 20 ordered CNOT generators.

- **Packing.** Each matrix is a 25-bit integer: row r sits in bits 5r to
  5r+4, and bit j of that row is M[r][j].
- **Generator.** CNOT(c -> t) is the row operation `row_t ^= row_c`.
- **Table.** The 2^25-entry uint8 table holds 255 at singular packings.

**Qubit permutations are free.** B and B Q (Q a permutation matrix) lie in
one coset and share s. Choosing Q for the next encoding realizes
`d_perm(T) = min_P d(P T) = min_P d(T P)` with no SWAP and no relabeling,
because a permutation conjugates a CNOT into a CNOT. The permutation-free
table comes from the same search seeded with the 120 permutation matrices.

| CNOTs | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d | 1 | 20 | 260 | 2,570 | 19,680 | 117,860 | 540,470 | 1,769,710 | 3,571,175 | 3,225,310 | 736,540 | 15,740 | 24 |
| d_perm | 120 | 2,400 | 28,800 | 238,800 | 1,260,000 | 3,679,200 | 3,981,000 | 800,400 | 8,640 | | | | |

| Table | sha256 of the 2^25 uint8 table |
| --- | --- |
| d | `f69b7b6fb99e20bf5cede9cf04ebcc56c66bd903fcfff7a1e297e329c1d81bc0` |
| d_perm | `d1170f2f27f65789a58bc1ef887dc6d84db0deba0257c15533512b56efcb66a3` |

**Coset distance.** It is the graph distance on the 83,328 cosets `B S_5`.
Each coset has 20 neighbors, each replacing one column c_a by c_a ^ c_b, and
the graph distance equals d_perm of `B_Y^-1 B_X`. The self-test checks that
identity on 64 seeded coset pairs.

**Device coupling.** It is not tabulated. The retained layouts change with
backend and transpiler seed, and SabreSwap moves the work qubits during the
circuit, so no fixed coupled sub-path exists at a round boundary. The
routed admission below measures each transition under routing directly.

## Surrogate optimum

Per-round costs depend only on the coset, so a dynamic program runs on the
coset graph.

- **Recurrence.** `v_1 = s_(m_1)` and `v_k = s_(m_k) + relax(v_(k-1))`, with
  `relax(v)(C) = min_A v(A) + d(A, C)`. The relax step is a multi-source
  unit-edge distance transform.
- **Free ends.** The first encoding is a basis-state preparation and the
  last is never measured, so neither costs a transition.
- **Retained costs.** s(4) and s(2) come from
  `docs/evidence/linear_conjugation/search.json`, bound by its sha256.
- **The 16 encoding.** `s(B^-1 f_16 B) = s(B^-1 f_4 B)` holds exactly,
  because 16 is 4^-1 mod 21 and the synthesis minimizes over reversed
  inverse networks.

| Problem | Single-B optimum | Split optimum | Optimal split |
| --- | --- | --- | --- |
| Two-round, multipliers 16, 4 | 372 (cosets 281, 308, 353, 15233, 15265) | 372 | none: one coset on both rounds |
| Ten-round, multipliers 4, 16 (x4), 4, 2 | 1,896 (coset 281) | 1,857 | 15265 on rounds 1 to 9, then 111 (s(2) = 180), d = 3 |

**Two-round.** Both rounds pay s(4) of their coset, so any split costs at
least 2 min s(4) = 372. That bound is the single-B optimum, so no split
lowers the surrogate cost. The routed cost does not follow the surrogate
exactly, so the theorem leaves open a split that costs more under the
surrogate and routes to fewer CZ.

**Ten-round.**
- **Shape of the optimum.** Only a split before round 10 can pay. By the
  triangle inequality, moving every round-1-to-9 encoding to the cheapest
  of them never costs more.
- **Pruning.** With s(2) >= 180, `9 s(4) + 180 < 1,896` admits only the five
  s(4) = 186 cosets on rounds 1 to 9.
- **Enumeration.** Enumerating them against all 83,328 round-10 cosets
  reproduces 1,857, a tie between 353 -> 16769 and the program's
  15265 -> 111.
- **The 42-unit bound.** The bound in the linear_conjugation README holds
  only against coset 281. Each admitted single-B coset X gains
  `s2(X) - s2(Y) - d` from its own best Y: 38 for 281, 93 for 15265 and 56
  for 15241.

## Routed admission

**Candidate lists**, fixed before compiling:
- **Single B.** The challenger's eight cosets per problem. The two-round
  problem adds every coset with s(4) <= 192, 16 in all.
- **Two-round splits.** The 16 ordered pairs X != Y from that pool of least
  `s4(X) + s4(Y) + d(X, Y)`. All have d of 1 to 4.
- **Ten-round splits.** The two round-10 cosets of least `s2(Y) + d(X, Y)`
  for each of the eight challenger cosets X, 16 in all.

**Compilation.** Every circuit compiles at optimization level 3 over
transpiler seeds 0 to 7, with the challenger's preset pass manager and no
HLS configuration.

**Targets.**
- **FakeFez and FakeKingston (Heron r2).** Both share the heavy-hex
  coupling map. Routed CZ agrees between them on 721 of 728 runs, and every
  routed-CZ median in the tables below agrees; depth and scheduled duration
  differ.
- **IQM Garnet coupling.** It has 20 qubits and 30 undirected edges, from
  `docs/evidence/open_quantum/catalogue.json` (`iqm:garnet`, retrieved
  2026-10-17T05:24:54Z, sha256 `5a3e1f5a...`). CZ runs both directions,
  plus rz, sx, x, measure, reset and if_else. The target carries no error
  or duration data, so the comparison isolates the square-grid coupling.
  Garnet admits on routed CZ and depth. Its native prx gate is not modeled.

**Rule.** A split wins on a target only when its median routed CZ is
strictly below the best single-B median on that target, over the same
seeds, on every arm. Every split was also held to the challenger's rule
against the unencoded circuit (no per-seed regression, a lower median), and
all 96 entries pass it.

| Target | Problem | Unencoded | Incumbent single B | Best single B | Best split | Splits that win |
| --- | --- | --- | --- | --- | --- | --- |
| FakeFez | ten-round | 5,422 | 15241: 3,933 | 15241: 3,933 | 15265 -> 111: 3,754 | 10 of 16 |
| FakeKingston | ten-round | 5,422 | 15241: 3,933 | 15241: 3,933 | 15265 -> 111: 3,754 | 10 of 16 |
| Garnet coupling | ten-round | 4,439.5 | 15241: 3,225.5 | 281: 3,190 | 15265 -> 111: 3,026.5 | 14 of 16 |
| FakeFez | two-round | 1,107 | 15265: 739 | 15275: 734 | 15265 -> 15233: 741 | 0 of 16 |
| FakeKingston | two-round | 1,107 | 15265: 739 | 15275: 734 | 15265 -> 15233: 741 | 0 of 16 |
| Garnet coupling | two-round | 840.5 | 15265: 584 | 353: 580 | 15265 -> 15233: 580 | 0 of 16 (tie) |

**Prediction check.** Twice the surrogate gain predicted the ten-round
saving before compiling. For X = 15265 that is 2 x 93 = 186 below the
single-B 3,954, or 3,768; the split routed to 3,754.
- **Depth.** The ten-round split also lowers median depth on FakeFez, from
  9,847 to 9,340.
- **Duration.** It lowers scheduled duration from 96,196.5 to 90,847.5 dt.

**Selection-bias check.** Picking the best of many candidates on seeds 0 to
7 favors the pick, so seeds 8 to 15 recompile the decisive circuits.

| Target | Problem | Incumbent | Best single B on 0-7 | Best split on 0-7 |
| --- | --- | --- | --- | --- |
| FakeFez, FakeKingston | ten-round | 15241: 3,945.5 | 15241: 3,945.5 | 15265 -> 111: 3,746 |
| Garnet coupling | ten-round | 15241: 3,217 | 281: 3,172 | 15265 -> 111: 3,018.5 |
| FakeFez, FakeKingston | two-round | 15265: 717.5 | 15275: 723 | 15265 -> 15233: 731.5 |
| Garnet coupling | two-round | 15265: 588.5 | 353: 580.5 | 15265 -> 15233: 589 |

- **Ten-round.** The held-out seeds keep the split's lead: 199.5 CZ on
  Heron r2 and 153.5 on the Garnet coupling.
- **Two-round.** On Heron r2, coset 15275's 5-CZ lead on seeds 0 to 7
  reverses on seeds 8 to 15, where the incumbent 15265 leads. That lead is
  selection noise, so coset 15265 stays the two-round hardware candidate.

## Scope

- **What the counts are.** They are routed CZ, depth and Target duration
  from captured fake backends and from one retained coupling map, and they
  predict no fidelity.
- **Hardware use.** The ten-round split would need its own submit-free
  live_run dry run, and any execution needs an approved case.
- **Searched family.** The routed search covers splits with one boundary
  per circuit. The dynamic program proves that more boundaries never lower
  the surrogate cost; their routed cost stays unsearched.
- **Routed candidates.** The routed comparison covers only the listed
  candidates. A routed optimum outside them stays unsearched.
- **Execution host.** The record was produced on the build host under
  Python 3.14.7, numpy 2.5.4 (AOCL BLAS), qiskit 2.5.2 and
  qiskit-ibm-runtime 0.50.0, the CI pins. Routed CZ, qubit counts, final
  layouts and classical stages replay exactly across BLAS builds. Depth and duration replay
  within the challenger's relative tolerance of 0.002.

## Replay

```sh
"$PYTHON" scripts/gl52_split_conjugators.py --check docs/evidence/gl52_split_conjugators/split.json
"$PYTHON" scripts/gl52_split_conjugators.py --self-test docs/evidence/gl52_split_conjugators/split.json
```

**`--check`** (gate core-491, full tier) recomputes:
- both distance tables and their hashes;
- the dynamic program and the enumeration;
- the candidate lists and every exact check;
- the sampled check of each best split;
- every median and verdict from the retained runs;
- complete target and problem sets in the routed and held-out sections.

It then recompiles the best single B, the best split and the incumbent of
every problem on every target over seeds 0 to 7. Routed CZ, qubit counts,
final layout, if_else count, feed-forward stages and the digest of the
measure, reset and if_else sequence must match exactly. Depth and duration
must match within 0.002.

**`--self-test`** (gate core-490) runs these checks:
- the packed search on GL(3,2), against a brute-force search of its 168
  elements;
- the permutation-free identities and the coset-graph distance, on 64
  seeded coset pairs;
- the vectorized pair distance, on the same pairs;
- rejection of twelve corrupted copies of the record, one missing a
  target in both the routed and held-out sections;
- rejection, against a fresh recompilation, of four corrupted runs: a
  changed routed CZ, a swapped layout entry, a changed feed-forward stage
  count, and a changed classical-sequence digest;
- acceptance of a copy whose catalogue timestamp and sha256 differ. A
  catalogue refresh rewrites those fields, while the replay binds Garnet's
  qubit count and coupling.
