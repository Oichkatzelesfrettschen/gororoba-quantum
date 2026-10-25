# Erratum report: Table 5 of arXiv 2609.10569v1

Recipient: Niels Gresnigt, Xi'an Jiaotong-Liverpool University, author of "Sedenions, Clifford Algebras, and
Three Fermion Generations: A Focused Review" (arXiv 2609.10569v1, 2 September 2026). The report goes to the
contact address the arXiv listing or the author's institutional page gives. The repository owner sends it, and
the plan record `gresnigt-table5-erratum-contact` tracks the reply.

---

Dear Dr. Gresnigt,

Eleven cells of the sedenion multiplication table in Appendix A (Table 5, page 54) of arXiv 2609.10569v1 carry
the wrong sign. The table is read row times column, as page 53 states. The corrected entries are:

| Product | Printed | Printed exchanged product | Corrected |
| --- | --- | --- | --- |
| `s_9 s_6` | `-s_15` | `s_6 s_9 = -s_15` | `s_15` |
| `s_9 s_7` | `s_14` | `s_7 s_9 = s_14` | `-s_14` |
| `s_9 s_8` | `s_1` | `s_8 s_9 = s_1` | `-s_1` |
| `s_9 s_14` | `-s_7` | `s_14 s_9 = -s_7` | `s_7` |
| `s_9 s_15` | `s_6` | `s_15 s_9 = s_6` | `-s_6` |
| `s_10 s_8` | `s_2` | `s_8 s_10 = s_2` | `-s_2` |
| `s_11 s_8` | `s_3` | `s_8 s_11 = s_3` | `-s_3` |
| `s_12 s_8` | `s_4` | `s_8 s_12 = s_4` | `-s_4` |
| `s_13 s_8` | `s_5` | `s_8 s_13 = s_5` | `-s_5` |
| `s_14 s_8` | `s_6` | `s_8 s_14 = s_6` | `-s_6` |
| `s_15 s_8` | `s_7` | `s_8 s_15 = s_7` | `-s_7` |

The other 214 cells, and every result index (`s_i s_j = +-s_(i XOR j)`), are correct as printed.

The evidence, each item from the paper's own conventions or from an independent implementation:

1. Anticommutativity. Each printed cell has the same sign as the printed product in the exchanged order (third
   column), and Eq. 47 requires `s_i s_j = -s_j s_i` for `i != j`. The exchanged cells agree with every other
   check below, so the eleven listed cells are the defective ones.
2. Eq. 63 and the quaternion subalgebras. With `s_(i+8) = s_i s_8` for `i = 1, ..., 7`, the associative
   subalgebra spanned by `1, s_i, s_8, s_(i+8)` gives `s_(i+8) s_8 = s_i s_8 s_8 = -s_i`. These are the
   corrected seven cells of column `s_8`, rows `s_9` to `s_15`.
3. The `S3` maps. The map `psi` of Eq. 61 satisfies `psi(xy) = psi(x) psi(y)` on all 256 basis pairs of the
   corrected table, in exact arithmetic over `Q(sqrt 3)`, and fails it on the printed table. `epsilon` is an
   automorphism of both, as of every table of the form `s_i s_j = +-s_(i XOR j)`: it multiplies each side of a
   product by the same sign.
4. Independent implementations. The corrected table equals the standard Cayley-Dickson doubling
   `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))` (your Eq. 40) in two independent programs: a Python
   implementation, and a Rocq definition of the integer doubling tower evaluated by the Rocq kernel. It also
   equals the sedenion table of G. P. Wilmot, arXiv 2512.07210v3, Table 2, under that paper's index map.

The same computation confirms your statement `Aut(S) = G2 x S3` (Eq. 53) for the corrected table. The
derivation algebra is 14-dimensional, and the automorphisms commuting with it are exactly the six elements that
your `epsilon` and `psi` generate. The printed table has only 4 derivations, so the misprints affect
calculations that start from Table 5 rather than from Eq. 40.

The scripts, the Rocq output and the transcription of the printed cells are public, in the repository
https://github.com/Oichkatzelesfrettschen/gororoba-quantum under `docs/evidence/sedenion-automorphisms/`.

With thanks for the review,

[sender]
