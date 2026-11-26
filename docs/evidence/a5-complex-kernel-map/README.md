# A_5 complex kernel map: noiseless statevector

The pathion kernel map reads the nullity of a complex two-term operand of A_5 when its orientation oracle carries the
selector phase. For e_i + t e_j with t = i or -i, the map with selector phase t and upper-member oracle phases
+-t s_k reads N = 16 at e_1 + i e_3 and N = 12 at e_1 + i e_26 in an exact statevector. N equals the nullity of
L_(e_i + t e_j) over C on all 465 pairs of imaginary units, and the same circuit with plain phases +-i reads -14 and
-2. Ledger rows A5-630 and A5-631 record the result; A5-632 holds the device hypothesis.

## Circuit

[`scripts/a5_complex_kernel_map_statevector.py`](../../../scripts/a5_complex_kernel_map_statevector.py) builds the
map of [`gororoba_quantum/pathion_kernel_map.py`](../../../gororoba_quantum/pathion_kernel_map.py) for
t in {1, -1, i, -i} on six qubits (algebra index bit b on qubit b, selector on qubit 5):

1. H on the five data qubits.
2. A diagonal oracle: +1 on the lower member k of every XOR pair {k, u = k XOR m}, m = i XOR j, and -t s_k (arm
   minus) or +t s_k (arm plus) on the upper member u, with s_k = (L_i^T L_j)[u, k] the pair sign.
3. H on the selector, then the selector phase t: Z for -1, S for i, S-dagger for -i.
4. `select_lcu.select_circuit(32, i, j)`, then H on the selector.

The pinned module keeps its bytes: digest-bound receipts and Kaggle submissions cite it. At t = +1 and -1 the new
builder reproduces the module's outcome laws on all six operands and both twins, 16 laws in all.

## Statements, each checked by `--check`

1. At t = i and t = -i, half the sum of the output contrasts c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) and 16
   times the selector contrast both equal the nullity of L_(e_i + t e_j) over C. The nullity is computed exactly as
   half the nullity of the 64 x 64 real form [[L_i, -s L_j], [s L_j, L_i]] for t = s i. Every c(y) is +1 or -1.
   This holds on all 465 pairs; the real circuit at t = 1 reads the real nullity on the same pairs.
2. Real over complex nullity of the 465 pairs: 0/16 at 171 pairs, the anticommuting tables; 4/12 at 84; 8/8 at 84;
   12/4 at 126. Every pair satisfies the complement law nullity(e_i + i e_j) = 16 - nullity(e_i + e_j) of A5-629.
3. Named points: e_1 + e_3 reads 0, e_1 + i e_3 reads 16, e_1 + e_26 reads 4, and e_1 + i e_26 and e_1 - i e_26 read 12.
   P(s = 0) in the minus and plus arms is 0 and 1 at e_1 + i e_3, and 0.125 and 0.875 at e_1 + i e_26. The six
   operands of the pinned module read 16, 12, 12, 8, 4, 4 at t = i against real nullities 0, 4, 4, 8, 12, 12.
4. Plain phases +-i on the upper members, with s_k dropped, read -14 at e_1 + i e_3 and -2 at e_1 + i e_26.
5. The complex circuit is the pinned real circuit of e_i + e_j with two added gates: S (S-dagger for t = -i) on data
   qubit h, the highest set bit of m, after the oracle, and S on the selector after its first H. The statevectors
   agree in both arms at t = i and -i on all 465 pairs. Transpiled to the basis cz, rz, sx, x at optimization level 1 without a coupling map, both
   circuits have 96 cz gates at e_1 +- i e_26 and 91 at e_1 + i e_3. S is rz(pi/2) up to a global phase, and rz
   belongs to the Heron basis, so the complex strata cost single-qubit rotations alone.

## Mechanism

Write the oracle as psi_k = 1 on the lower member and psi_u = eps t s_k on the upper, with eps = +1 in the plus arm and
-1 in the minus arm. The selector-zero branch carries (L_i + t L_j) psi / 2, which has the norm of
(I + t K) psi / 2 with K = L_i^T L_j. On the pair {k, u}:

- the u component is psi_u + t K[u, k] psi_k = t s_k (1 + eps);
- the k component is psi_k + t K[k, u] psi_u = 1 + eps t^2 sigma_k, with sigma_k = +1 on an aligned pair
  (K[k, u] = K[u, k]) and -1 on a misaligned one.

For real t, t^2 = 1, and the arm contrast counts aligned pairs: the real nullity, as the pinned module states. For
t = +-i, t^2 = -1 swaps the roles, so the contrast counts the misaligned pairs, 16 - N(e_i + e_j). By A5-629 that
count is the nullity over C. Dropping s_k makes the k and u weights depend on each pair's own signs, which gives -14
and -2 in place of a nullity. A reviewer gave this explanation in round 2 of the null-slice review ("i^2 = -1 swaps
aligned and misaligned pairs"). The record checks it on every pair.

## Predictions and controls

The predictions were in ledger row A5-630 and pool row MATH-72 before the run: 16 and 12 at the named points, -14 and -2
for plain phases (the reviewer's values), and the complement law on every pair. All held at the first run.

`--self-test` runs five paired controls, each a baseline that passes and a mutant that fails:

| Control | Baseline | Mutant |
|---|---|---|
| s_k | oracle with s_k reads 12 | plain phases do not |
| selector phase | S reads 12 | Z with the i oracle does not |
| tie to the pinned module | laws equal at e_1 + e_18 | one negated oracle entry differs |
| S on qubit h | S-form statevector equals the direct one | S on the next qubit does not |
| real form | [[A, -B], [B, A]] gives 12 | [[A, B], [B, A]] does not |

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_complex_kernel_map_statevector.py --check docs/evidence/a5-complex-kernel-map/result.json
"$PYTHON" -B -W error scripts/a5_complex_kernel_map_statevector.py --self-test
```

Gates `core-a5-complex-kernel-map` and `core-a5-complex-kernel-map-self-test` in `ci/gates.json` run both.

## Open

- A5-632: on a device, the visibility-corrected estimate of the complex map reads 16 and 12. A run needs its own
  written case under the repository's hardware rules. The hardware record of the real map left 23 of 32 signs
  unresolved for the full map ([findings](../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md)), so the coset-block
  variant is the likely first candidate.
