# Derivations of J_3(O): the F_4 anchor and the stabilizers of G_2 and su(3)

The derivation algebra of the exceptional Jordan algebra J_3(O) has dimension 52 over Q under the octonion product of
[`gororoba_quantum/cd_core.py`](../../../gororoba_quantum/cd_core.py), and the algebras G_2 and su(3) of the null-slice
covariance records sit inside it as stabilizers of Jordan subalgebras.
[`scripts/a5_albert_derivation_stabilizers.py`](../../../scripts/a5_albert_derivation_stabilizers.py) computes every number exactly, as ranks over Z
(python-flint `fmpz_mat`). Ledger row A5-661.

## Chain to the null-slice records

A5-615 records the covariance algebra of the A_5 null slice as 8-dimensional, and A5-619
([covariance blocks](../a5-null-slice-covariance/README.md)) identifies it with Stab_(G_2)(e_2) = su(3), the derivations of
the octonions that fix e_2. This record shows that the entrywise action of that su(3) on J_3(O) is the stabilizer in
Der(J_3(O)) of the subalgebra J_3(C_e2), C_e2 = span(1, e_2): both have dimension 8 and their bases stack to rank 8. The
octonion-space covariance algebra G_2 of A5-619 acts entrywise as the stabilizer of J_3(R). The run therefore places the
two covariance algebras inside Der(J_3(O)) as stabilizers of Jordan subalgebras.

## Method

A derivation is a 27 x 27 matrix D (729 unknowns, D(e_a) = sum_b D[b][a] e_b) with
D(e_i e_j) = D(e_i) e_j + e_i D(e_j) on every pair of basis vectors. The Jordan product enters as XY + YX, which has
integer structure constants and the same derivations as (XY + YX)/2. The system has 9063 rows of rank 677, so the
derivations span 729 - 677 = 52 dimensions. The basis of J_3(O) is E1, E2, E3 and the octonion units in the three
off-diagonal slots. A stabilizer is the kernel of the map D -> (D(b))_(b in S) on a set S of basis elements.

## Statements, each checked by `--check`

1. **Product.** The structure constants equal `cd_core.cd_multiply_exact` on all 64 octonion basis pairs.
2. **Der(O) and Der(J_3(R)).** dim Der(O) = 14 (rank 50 of 512 rows); dim Der(J_3(R)) = 3 (rank 33 of 117 rows).
3. **F_4.** dim Der(J_3(O)) = 52.
4. **G_2 inside F_4.** The entrywise action of the 14 octonion derivations on J_3(O) leaves zero residual in the
   derivation system, and stacked with a basis of Der(J_3(O)) it gives rank 52.
5. **su(3) as a stabilizer of e_2.** The octonion derivations with D e_2 = 0 span 8 dimensions (the map D -> D e_2 has
   rank 6 on the 14).
6. **Stabilizers of Jordan subalgebras.** The stabilizer in Der(J_3(O)) of J_3(R) (E1, E2, E3 and the real unit in each
   off-diagonal slot) has dimension 14, and stacked with the entrywise G_2 it has rank 14. The stabilizer of J_3(C_e2)
   has dimension 8, and stacked with the entrywise su(3) of e_2 it has rank 8.
7. **Further stabilizers.** The stabilizer of E1 has dimension 36 and that of E1, E2, E3 has dimension 28.

Statements 3, 4, 6 and 7 are known facts of the theory of F_4 (F_4 = Der(J_3(O)), its subgroups G_2 = Stab(J_3(R)) and
SU(3) = Stab(J_3(C)), the Spin(9) = Stab(E1) of dimension 36 and the Spin(8) of dimension 28); this record confirms them
under the cd_core convention and claims no new finding about F_4. What the record adds is the explicit binding of the
covariance algebras of A5-615 and A5-619 to those stabilizers, as rank equalities of the entrywise images.

## Prediction

The values 52, 14, 8, 13, 36 and 28 were written down before the run, with the falsifier for each (a different dimension,
or a stacked rank above the stabilizer's dimension). All held.

## Controls

| Control | Baseline | Mutant |
|---|---|---|
| zero product | | every linear map is a derivation: 64 |
| one anticommuting pair negated, for the pairs (1, 2), (1, 4), (3, 5) | Der(O) 14, Der(J_3(O)) 52 | Der(O) 4 and Der(J_3(O)) 7 for each pair |
| a vector that is not a derivation | stack with the entrywise G_2: rank 52, residual 0 | stack with the vector: rank 53, 26 nonzero residual entries |
| stabilizer of J_3(C_e3) | dim 8; stacked with the su(3) of e_3: rank 8 | stacked with the su(3) of e_2: rank 13 |

The last control separates e_2 from e_3: the two su(3) algebras meet in the 3-dimensional su(2) fixing both, so
8 + 8 - 3 = 13.

`--self-test` runs four paired controls: the negated sign pair against Der(O) and against Der(J_3(O)), the
non-derivation vector, and the su(3) of e_2 against the stabilizer of J_3(C_e3).

## Reproduction

```sh
"$PYTHON" -B -W error scripts/a5_albert_derivation_stabilizers.py --check docs/evidence/a5-albert-derivation-stabilizers/result.json
"$PYTHON" -B -W error scripts/a5_albert_derivation_stabilizers.py --self-test
```

Gates `core-a5-albert-derivation-stabilizers` and `core-a5-albert-derivation-stabilizers-self-test` run both.
