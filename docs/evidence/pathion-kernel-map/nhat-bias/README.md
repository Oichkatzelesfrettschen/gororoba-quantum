# N_hat bias audit: the estimator's bias identity, forced blocks and block profiles

`nhat_bias.py` audits the kernel-map nullity estimator N_hat on the five retained IBM runs that read it and on the two
retained wide runs. [`result.json`](result.json) holds the 32-dimensional readings, [`result_wide.json`](result_wide.json)
the 64- and 128-dimensional readings, and every number below comes from one of them.

## Estimator and notation

For one circuit pair the code (`pathion_kernel_map._pair_summary`, `pathion_coset_block.pathion_coset_map_group`,
`pathion_parallel_coset.estimate`) forms c_obs(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) on the output bins y and
reads

- V_hat = mean over bins of c_obs(y) sign(c_ideal(y)),
- N_hat = (sum over y of c_obs(y) / 2) / V_hat, undefined when |V_hat| is at most 1e-9.

B+ and B- are the bins with c_ideal = +1 and -1, N = (|B+| - |B-|) / 2, Vbar+ is the mean of c_obs over B+ and Vbar- the
mean of -c_obs over B-. Every two-term bin is decided (|c_ideal| = 1); the four-term blocks read levels, not output
contrasts, and carry no N_hat. A block of 2^d bins with N_b aligned XOR pairs has |B+| = 2^(d-1) + N_b and
|B-| = 2^(d-1) - N_b.

Aggregation. The note under audit averages c(y) over the replicas of a run, then applies the estimator (`n_hat` in
`result.json`). The findings table and the hardware-orbits table average the per-replica N_hat instead
(`n_hat_mean_of_replicas`). On the ibm_fez kernel map the two differ by 0.1 to 24 (e1 + e17: 1.399 against 1.537;
e1 + e26: 10.036 against 34.089), because V_hat is near zero on single replicas.

## Verdicts

| Claim | Verdict | Evidence | Falsifier |
|---|---|---|---|
| 1. N_hat - N = \|B+\|\|B-\|/\|B\| (Vbar+ - Vbar-)/V_hat | proved, and computed | derivation below; exact rational residual 0 on all 171 units (replica mean and every replica of five runs); double-precision residual at most 7.1e-15; 192 wide placements: 0 exactly, 4.4e-16 | a residual above 1e-12 on a unit with every bin decided and \|V_hat\| above 1e-9; none found |
| 2. The null operand reads 1.40 and e1 + e26 reads 10.04 on the full map, from Vbar+ above Vbar- | computed; the class gap is significant on e2 + e27 alone after correction over 8 circuits and unresolved on the null operand | 1.3993 (Vbar+ 0.3754, Vbar- 0.3150) and 10.0357 (Vbar+ 0.1221, Vbar- 0.0466); per-replica class gap t of 2.11 (null), 4.28 (e1 + e26, p 0.013 uncorrected and 0.10 corrected), 8.27 (e2 + e27, p 0.0093 corrected) on 4 degrees of freedom against 2.776 | an ibm_fez full-map rerun whose class gaps all lie within 2.776 standard errors of zero |
| 3. Blocks with N_b = 4 read exactly 4.00 on any hardware | proved, and computed | below; 52 forced units over four runs, largest departure from the forced value 0.0 over every replica, no replica under the 1e-9 guard, stored readout-corrected values equal 4 on 40 of 40 blocks | a block with B- empty and \|V_hat\| above 1e-9 whose N_hat differs from \|B+\|/2 |
| 4. The headline 12.015 is 4 + 4 + 4 + 0.015 and only N_b in {0, 2} carry information | computed for the six measured operands; refuted as a general statement | ibm_fez coset map e1 + e18: blocks 0.0151, 4, 4, 4; the informative blocks are those with N_b below 4, and N_b = 1 and 3 occur (384 blocks each of 3,720 in the default tiling, four N_b = 3 blocks in the 128-dimensional operand) | a measured operand whose block profile holds a value outside 0 to 4 |
| 5. The profiles [2.08, 4, 2.06, 4] and [0.02, 4, 4, 4] separate the two nullity-12 orbits | the profiles are computed and separate the two measured operands at 65 to 137 standard errors; refuted as an orbit discriminator | ideal profiles [2, 4, 2, 4] (e1 + e24, orbit V) and [0, 4, 4, 4] (e1 + e18 and e17 - e2, orbit VB); census of the 252 two-term operands of nullity 12 below | an operand of orbit V with the profile [0, 4, 4, 4] under its default tiling, which would also void the one-directional statement below |
| 6. The accuracy claim fails as stated; the identity and the profile discriminator survive | partly confirmed: the unconditional accuracy claim fails because its premise (Vbar+ = Vbar-) is falsified on the full map and the coset readings of forced blocks are algebra; the identity survives (proved); the profile discriminator survives only for the measured pair, not as an orbit statement | claims 1, 2, 3 and 5 | rows 2, 3 and 5 |
| 7. The parallel coset runs and the wide runs | the identity and the forced-block law hold on both; details below | `result.json`, `result_wide.json` | see rows 1 and 3 |

## Claim 1: derivation

Let n = |B|, S = sum of c_obs, so S = |B+| Vbar+ - |B-| Vbar-, and V_hat n = |B+| Vbar+ + |B-| Vbar-. Then

n S - (|B+| - |B-|)(V_hat n) = 2 |B+||B-| (Vbar+ - Vbar-),

and dividing by 2 n V_hat gives N_hat - N = |B+||B-|/n (Vbar+ - Vbar-)/V_hat, since S/(2 V_hat) = N_hat and
(|B+| - |B-|)/2 = N. For a block of 8 bins the factor |B+||B-|/n is (16 - N_b^2)/8; for the 32-bin full map it is
(256 - N^2)/32. The identity holds for any c_obs, so it holds for every replica and for every aggregate of replicas.
N_hat equals N exactly when the two class means agree: Vbar+ = Vbar- is the premise of the claim that N_hat returns N
whatever the visibility (`gororoba_quantum/pathion_kernel_map.py`, module docstring and the comment in
`_pair_summary`). Domain: every bin decided with |c_ideal| = 1, which holds for the primary operands, twins,
cocycle-free controls, flip mutation and the `cflip` and `crep` families of the parallel runs.

Commands, from the repository root (about 20 s each for the first two):
`"$PYTHON" -B docs/evidence/pathion-kernel-map/nhat-bias/nhat_bias.py --out docs/evidence/pathion-kernel-map/nhat-bias`
writes `result.json`, and `--check docs/evidence/pathion-kernel-map/nhat-bias` recomputes and compares it. The wide
record replays from a tree that holds `gororoba_quantum/pathion_wide_coset.py` and the two collect files: extract
`git archive 4c4d5bd06 gororoba_quantum` and the `collect.json` of `results/live/2026-11-07T153325.440007Z` and
`results/live/2026-11-07T153325.886771Z` into one directory `SRC`, then run
`NHAT_BIAS_SOURCE=SRC "$PYTHON" -B nhat_bias.py --wide results/live/2026-11-07T153325.440007Z results/live/2026-11-07T153325.886771Z --source-commit 4c4d5bd0655e9c030055a8db5b3c08bb29868463 --out-wide result_wide.json`.
`--self-test` checks the identity on a grid of class sizes in rational arithmetic and the loader against the group's own
`summarize` on every replica of the ibm_fez coset map and of the full map (agreement to 1e-9). The collector stores each measured law rounded to six decimals, so per-replica N_hat
rebuilt from `collect.json` differs from the collector's `summary_per_replica` by at most 2.2e-5 on the coset and
parallel runs; on the full map, where single-replica V_hat is near zero, by 0.025, which the stored rounding amplifies (the loader
itself matches `summarize` on the stored laws to 1e-9).

## Claim 2: the full map

`kernel_map.readings` of `result.json` lists the six operands and the two twins of
`results/live/2026-11-06T183538.809814Z`. Replica-mean N_hat reads 1.399, 10.036, 6.483, 9.172, 12.752, 12.536 for the
operands of nullity 0, 4, 4, 8, 12, 12 and 6.003, 11.929 for the twins; the biases follow the closed form to the last
digit. Vbar+ exceeds Vbar- on 7 of 8 circuits, and the per-replica class gap clears the 95 percent critical value of
2.776 on two (e1 + e26, e2 + e27); after a Bonferroni correction over the 8 circuits only e2 + e27 (p 0.0093) stays
significant. The null operand's gap t is 2.11, so its reading of 1.40 sits inside the
interval [-0.47, 3.54] of the findings table and the bin-dependent visibility is not resolved on it.

Where the accuracy claim is stated, with its status after this audit:

| Statement | Location | Status |
|---|---|---|
| N_hat estimates N whatever visibility the circuit has, hypothesis-level when the contraction depends on the output bin | `pathion_kernel_map.py` module docstring; comment in `_pair_summary` | conditional, correct as written; premise falsified on the full map |
| N_hat returns N under any contraction toward the uniform law | `results/live/2026-11-06T180755.872625Z/CASE.md` | correct for a global contraction; a per-bin contraction is not one |
| e1 + e18 reads N_hat 12.65 [11.87, 13.42], which resolves its nullity of 12 | findings table; ledger A5-180; synthesis "What the hardware establishes about the algebra" | the interval excludes 8 and 16, so the resolution among those values stands; the point reading carries a bias of +0.75 (replica mean) from Vbar+ - Vbar- = 0.030, and the full map's signs miss the 31 of 32 rule (26 of 32 on pooled laws, 29 of 32 on the replica mean of the contrasts); the findings paragraph, the A5-180 basis and the synthesis gain the bias qualifier, and the original sentence stays |
| N_hat is exact only under a bin-independent contraction | `docs/state/research_state.json` boundary of `hw-pathion-kernel-map-fez` and the two coset claims | correct as written |
| coset blocks recover the nullity of all six operands | ledger A5-182 and A5-192, findings coset paragraph, claims `hw-pathion-coset-map-*` | scoped by claims 3 and 4: the integer part of three nullity-12 and two nullity-8 readings is algebra |

Mechanism. hypothesis: misassignment of the output bits mixes neighboring bins, a bin of the smaller class has more
neighbors of the other class, and Vbar- falls below Vbar+ by an amount that grows with the class imbalance. A symmetric
bit-flip channel of probability 0.02 on a block of contrast 0.9 reads Vbar+ 0.876, Vbar- 0.829 and N_hat 2.082 on an
N_b = 2 block and leaves N_b = 0 blocks at exactly 0 (`mixing_toy` in `result.json`); the measured N_b = 2 blocks read
2.04 to 2.09 and the N_b = 0 blocks read 0.00 to 0.07 (the null-operand offsets have their own record in the findings).
Confidence 0.5; a block-level fit of the per-bit assignment errors from the readout circuits raises it, and an N_b = 2
bias that does not follow those errors lowers it. On the 32-bin estimator applied to the assembled coset-run data
(`n_hat_32_bin`), Vbar+ exceeds Vbar- by 0.014 to 0.088 on every operand of nullity 4 to 12 in all four coset runs.

## Claims 3 and 4: forced blocks

With B- empty, Vbar- does not enter: V_hat = Vbar+ = S/|B+|, so N_hat = (S/2)/(S/|B+|) = |B+|/2 for any c_obs whose
|V_hat| clears the guard. On eight bins that is 4, reached when all four XOR pairs of the block are aligned (N_b = 4),
and the reading survives a negative V_hat, a bin that reads the wrong sign and a replaced law. With B+ empty the
reading is -|B-|/2; the cocycle-free blocks of the 128-dimensional mutation read -4 this way. A block with both classes
occupied reads a function of the data. Command: `--self-test` replaces the arm laws of an N_b = 4 block by seven fixed
count edits (swapped arms, cyclic shifts, geometric weights, an alternating pattern; no random draw) and requires 4 to
1e-12, and requires the same edits to move an N_b = 0 block by at least 0.05, so the control has power.

On the retained runs the forced blocks are e1 + e10 (2 of 4), e1 + e18 and e17 - e2 (3 of 4) and e1 + e24 (2 of 4);
the nullity-0 and nullity-4 operands and the cocycle-free control have none. The ibm_fez coset map reads

| Operand (nullity) | Block readings | Forced part | Informative part (ideal) |
|---|---|---|---|
| e1 + e18 (12) | 0.0151, 4, 4, 4 = 12.0151 | 12 | 0.0151 (0) |
| e1 + e24 (12) | 2.080, 4, 2.057, 4 = 12.137 | 8 | 4.137 (4) |
| e1 + e10 (8) | 0.020, 4, 0.030, 4 = 8.050 | 8 | 0.050 (0) |
| e1 + e26 (4) | 2.064, 0.058, 2.052, 0.058 = 4.233 | 0 | 4.233 (4) |

The whole deviation of every operand from its nullity sits in the informative blocks. The same data through the 32-bin
estimator read 12.317 for e1 + e18, 12.300 for e1 + e24 and 8.155 for e1 + e10, so the block-sum estimator reads 0.28 to
0.30 closer to the integer on the nullity-12 operands than the whole-operand estimator of the same contrasts, because
the forced blocks remove the part of the bias that Vbar+ - Vbar- would have added. The sign map is the information the
hardware carries: the replica-mean signs of c(y) agree with all 32 ideal signs on every operand of the four coset runs,
and half the sum of the signs (`sign_count_nullity`) equals the integer nullity on each, with no visibility estimate.

## Claim 5: block profiles

Profiles are the aligned-pair counts per coset in the default tiling, listed in ascending coset representative. Measured
`n_hat` per block on the four coset runs for e1 + e24 against e1 + e18 differ in block 0 by 2.054 to 2.069 and in block
2 by -1.938 to -1.964. Unpaired z on the replica spread is 65.6 to 104.8 (block 0) and 78.8 to 136.9 (block 2); the
least resolved single bin of any block is at z 21 to 48 along its ideal sign. Block 0 compares two informative
readings. Block 2 compares an informative reading with the forced value 4, so it tests that the e1 + e24 block is not
all aligned, not a hardware reading of the e1 + e18 block.

The census of the 930 two-term operands (counts equal `census.json`'s nullity counts 342, 168, 168, 252) gives for the
252 operands of nullity 12, by sorted profile and orbit of `hardware_orbits.classify`:

| Sorted profile | V | VB | V^a- | V^a+ |
|---|---:|---:|---:|---:|
| 0, 4, 4, 4 | 0 | 12 | 0 | 0 |
| 2, 2, 4, 4 | 24 | 108 | 6 | 6 |
| 3, 3, 3, 3 | 32 | 48 | 8 | 8 |

The profile is a property of the operand and its 3-dimensional subspace: e1 + e18 reads [0, 4, 4, 4], [2, 2, 4, 4] and
[3, 3, 3, 3] under the subspaces spanned by (19, 1, 2), (19, 2, 4) and (19, 4, 8), and e1 + e24 reads [2, 4, 2, 4] and
[3, 3, 3, 3] under (25, 1, 2) and (25, 2, 4). Two statements survive. A reading of [0, 4, 4, 4] under the default tiling
excludes V among two-term operands of nullity 12 (12 of 12 are VB), and the measured pair e1 + e24 and e1 + e18 is
separated because its orbits were known before the tiling was chosen. A reading of [2, 4, 2, 4] does not identify V:
108 operands of VB share its sorted profile.

## Claim 7: parallel and wide runs

The two parallel coset runs of 2026-11-07 store `measured` per block (`cmap_<operand>_k<coset>_<arm>`, one array per
placement), so the keys match the coset map and the placements play the role of replicas; the per-shot streams sit in
`raw/<job>/pub_NN.json`, which this audit does not read. Claims 1 to 5 hold on both with the numbers in `result.json`: forced blocks read 4
exactly (16 forced units per run, including the `cflip` twins and `crep` repeats), the profiles match, and the
nullity-12 readings read 12.011 and 12.014 for e1 + e18 and 12.118 and 12.143 for e1 + e24.

The wide runs (`result_wide.json`, group `pathion_wide_coset` with its 32-dimensional reference placement) are read
from the `main` tree at commit 4c4d5bd06 (`NHAT_BIAS_SOURCE`; `pathion_wide_coset.py` and the records are not on this
branch). The estimator applies per block on raw laws. o64 holds six forced blocks of eight (24 of its 28) and o128
twelve of sixteen (48 of its 60), plus four blocks with N_b = 3; their whole-operand raw readings are 28.121 and 60.384
(ibm_kingston), 28.247 and 61.291 (ibm_fez). The forced blocks contribute 48 and 24 by algebra (ratio 2.0) and the informative blocks 12 and 4 (ratio 3.0), so the
ratio 2.148 of the 128- and 64-dimensional readings in the synthesis (27.995 and 60.126 after readout correction)
measures only the informative part's departure from its ideal, and its agreement with 60/28 = 2.143 is not an
independent test of the law. The
cocycle-free mutation of o128 holds fifteen forced blocks of sixteen (+4 or -4) and one informative block. The null
operands n64 and n128 have no forced block. The ibm_fez o128 block k28 reads exactly 4.000 at raw block visibility
0.633 while its null twin reads -0.718, the forced-block signature the synthesis describes.

Where the estimator does not apply: the four-term blocks (levels, no output contrast), and any block with an undecided
bin (the identity gains the term sum over undecided bins of c_obs / (2 V_hat)).

Inputs: the five run directories of `RUNS` in the script (collect.json sha256 in `result.json`), `census.json`, and
`hardware-orbits/hardware_orbits.py` for the orbit of each nullity-12 operand.
