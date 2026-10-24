# Sedenion automorphism group and the Gresnigt Table 5 cells

The automorphism group of the `cd_core` sedenions is `G2 x S3`, and the 11 cells of
[Gresnigt's Table 5](../../notes/papers/2609.10569.md) that disagree with `cd_core` are printing errors.
[test_sedenion_automorphism_group.py](../../../tests/gororoba_quantum/test_sedenion_automorphism_group.py) computes
both in exact arithmetic on every pull request. It runs against the multiplication table that the pinned Rocq
evaluates from the integer pair tower of
[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v).

## Files

| File | Content |
| --- | --- |
| [TowerTable.v](TowerTable.v) | `vm_compute` of the 16 coordinates of `e_a e_b`, for every `a, b < 16`, under the tower's own `mul` at level 4 |
| [tower_table.txt](tower_table.txt) | the Rocq output that `rocq_tower_table.sh` reproduces byte for byte |
| [rocq_tower_table.sh](rocq_tower_table.sh) | compiles the two proofs unchanged and `TowerTable.v` in temporary storage under the toolchain that [cd-tower-basis-sign/toolchain.txt](../cd-tower-basis-sign/toolchain.txt) records, then compares the output |
| [gresnigt_table5_printed.json](gresnigt_table5_printed.json) | the 11 printed cells and their exchanged partners, transcribed from page 54 of arXiv 2609.10569v1 (PDF SHA-256 in the record) |
| [upstream/gresnigt-table5-erratum.md](upstream/gresnigt-table5-erratum.md) | the erratum report for the author |

Replay: `ROCQ=<rocq 9.3.0 of ci/rocq_toolchain.pin> sh docs/evidence/sedenion-automorphisms/rocq_tower_table.sh`
prints `tower_table_pass TowerTable`. `sh ci/pr_checks.sh tests
tests/gororoba_quantum/test_sedenion_automorphism_group.py` runs the certificate.

## Rocq tower and `cd_core`

All 256 products in `tower_table.txt` are signed basis elements, and each one equals `cd_sign(16, a, b)
e_(a XOR b)` (`test_rocq_tower_table_is_cd_core`). The table comes from the doubling `(a, b)(c, d) = (ac -
conj(d) b, da + b conj(c))` that the tower defines, not from `sigma` or the `cd_sign` transcription. So it checks
the [basis_mul](../cd-tower-basis-sign/README.md) theorem at k = 4, independently of that theorem's proof.

## The automorphism group

The test computes, over `Q`:

| Algebra | `dim Der` | commutant of `Der` | automorphisms in the commutant |
| --- | --- | --- | --- |
| octonions, `cd_core` dimension 8 | 14 | 2 | 1, the identity |
| sedenions, `cd_core` dimension 16 | 14 | 8 | 6, `{1, psi, psi^2, epsilon, epsilon psi, epsilon psi^2}` |
| sedenions as Table 5 prints them | 4 | not solved (32) | `epsilon` survives, `psi` fails |

The sedenion derivations span exactly the 14 maps `A + B s_8 -> d(A) + d(B) s_8` with `d` an octonion
derivation. A derivation is a linear map `D` with `D(e_p e_q) = D(e_p) e_q + e_p D(e_q)` on every basis pair, a
system of 4096 equations in 256 unknowns. The commutant is the solution space of `c D = D c` over that basis.
The automorphisms inside it come from a lex Groebner basis of `c(e_p e_q) = c(e_p) c(e_q)`. Its univariate
member `4 x^5 - 5 x^3 + x = x (2x - 1)(2x + 1)(x - 1)(x + 1)` has only real roots, and the zero map, the one
singular solution, is excluded. The six invertible solutions are, matrix for matrix, the group that
Gresnigt's `epsilon` and `psi` (Eqs. 60 to 62) generate. That group is `S3`, and no element other than the
identity acts as `d` on both halves, so it meets the diagonal `G2` only in the identity.

The argument from these computations to the group:

1. An automorphism `g` conjugates `Der(S)` onto itself, so `Ad(g)` is a Lie-algebra automorphism of `Der(S)`.
2. `Der(S)` is the diagonal image of `Der(O)`, which is the compact simple `g2` (Cartan). The `G2` Dynkin
   diagram has no symmetry, so every automorphism of `g2` is inner, `Ad(h)` with `h` in the connected group
   `exp(Der(S))`. That group consists of automorphisms and is the diagonal `G2`.
3. `c = h^(-1) g` is an automorphism that commutes with `Der(S)`, so `c` is one of the six.
4. The six commute with `Der(S)`, hence with its connected group, and meet it only in the identity.

So `Aut(S) = G2 x S3`, and by the same steps `Aut(O) = G2`. The computation supplies the dimensions, the
diagonal span, the commutants and every root. The imported facts are the theorems of step 2:
`Der(O) = g2`, `Aut(g2) = Int(g2)`, and `exp D` an automorphism for a derivation `D`.

Falsifiers: a 15th derivation, a seventh real root, or an `S3` element inside the diagonal `G2` changes the
group. Each of them fails a named check of the test. A flipped sign in the table is the mutation control: the
11 printed Table 5 signs leave 4 derivations and break `psi`.

### Wilmot's two statements

[Wilmot](../../notes/papers/2512.07210.md) (arXiv 2512.07210v3) states two incompatible results for `Aut(S)`.
For linear bijections `T` with `T(xy) = T(x) T(y)`, the computation decides each of them:

| Statement | Where | Result |
| --- | --- | --- |
| `G2 x S3` is contained in `Aut(S)` | abstract, introduction, Section 5 | holds: the diagonal `G2` and the `S3` above |
| "the full automorphism group is much more complicated", against Brown's `Aut(A_4) = Aut(A_3) x S3` | abstract, introduction, p. 24 | refuted: `Aut(S) = G2 x S3`, Brown's value |
| `Aut(S) = Phi_O^(C(1))`, a group of type `G2`, with "the same structure as for O" | Theorem 7, pp. 24-25 | refuted: `Aut(S)` has six components and `Aut(O)` one |

Theorem 7 defines its strong and weak automorphisms through invariance of a calibration under Clifford
conjugation, a different notion from algebra automorphism. Under those definitions the theorem is not
evaluated. The computation covers the sedenions only, so Brown's statements for the doublings beyond `S`
(`N = 5, 6`) stay open.

## The Gresnigt Table 5 cells

`test_gresnigt_erratum_cells` checks every cell of the JSON record. Each printed cell carries the same sign as
its printed exchanged partner, and Eq. 47 of the paper (`s_i s_j = -s_j s_i`) forbids that. The Rocq tower
gives the opposite sign of each printed value. Table 5 with these 11 cells corrected is `cd_core`'s table on all
225 cells. [Wilmot's Table 2](../../notes/papers/2512.07210.md#mapping-to-this-repository) also agrees with it,
under the index map that note records. [The erratum](upstream/gresnigt-table5-erratum.md) lists the corrections.
