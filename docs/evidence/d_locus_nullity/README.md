# Nullity across the A_5 D-locus of two sedenion zero divisors

`result.json` is the output of `scripts/d_locus_nullity.py --out`, exact
rational arithmetic on the build host in about 62 s. It reproduces, on 1000
exact pairs, the nullity table that Biss, Christensen, Dugger and Isaksen
(math/0702075; [source note](../../notes/math-0702075.md)) give for brackets
{a, b} of two sedenion zero divisors.

The two results it reproduces:

- **Theorem 1.5.** A bracket of two zero divisors has nullity 12 on the
  D-locus and 8 off it.
- **Corollary 7.4.** {a, b} lies on the D-locus exactly when b lies in
  V(a) = span{(a1, -a2), (a2, a1)} + Eig_2(a).

## Construction

- **Element.** The script uses (a + b, e_8 (b - a)), sqrt 2 times the bracket
  of Definition 3.1, in cd_core's doubling, so every entry stays rational.
  Lemma 3.5's norm identity is asserted on every pair at that scaling.
- **The zero divisor a.** Each of 200 frames takes a Cayley-frame zero
  divisor a, an exactly rational orthonormal pure pair from
  `scripts/moreno_stiefel_nullity.py`, times a seeded positive rational.
- **Checks on a.** The run asserts dim Ann(a) = 4, dim Eig_2(a) = 4,
  dim V(a) = 6, and Ann(a) orthogonal to V(a). Eig_2(a) is the kernel of
  L_a^2 + 2 |a|^2 I, which is scale-free.
- **The five b's.** Each frame pairs a with five b's, each times its own
  seeded positive rational:

  | kind | b |
  | --- | --- |
  | locus | a rational combination of a basis of V(a) |
  | generic | an independent Cayley-frame zero divisor |
  | annihilator | a rational combination of a basis of Ann(a) |
  | self | a |
  | swap | (a2, -a1), inside <<a1, a2>>^2 and outside span{(a1, -a2), (a2, a1)} |

  Each b is asserted to have nullity 4 in A_4. On V(a) that is Theorem 7.5's
  content, since the theorem's fiber is the whole unit sphere of V(a).
- **Membership** in V(a) is an exact rank test.
- **Nullity** is certified as in `moreno_stiefel_nullity.certify`. The rank
  modulo 2^61 - 1 bounds the rational rank below, and verified rational
  kernel vectors bound it above.

The falsifier, stated before the run, was any member with nullity other
than 12, or any non-member with nullity other than 8.

## Result

| kind | in V(a) | A_5 nullity | pairs |
| --- | --- | --- | --- |
| locus | yes | 12 | 200 |
| generic | no | 8 | 200 |
| annihilator | no | 8 | 200 |
| self | no | 8 | 200 |
| swap | no | 8 | 200 |

No pair violates the table.

Across the 200 member pairs the length ratio |b|/|a| runs from 0.18 to
508. Theorem 7.5 fixes |a| = |b| = 1. The note's positive length-ratio
family rests on the D-locus conditions being scale-invariant, and these rows
are exact finite instances of it at unequal lengths.

`annihilator_strata.py` carries the four fixed A_5 nullities of the source
note's action item 2 in its exact integer engine:

| element | nullity | source |
| --- | --- | --- |
| {e_1, 0} | 12 | Proposition 5.11 |
| (i_4, e_1) = e_8 + e_17 | 12 | Proposition 8.2 |
| e_1 + e_10 + 2 e_24 | 4 | Moreno's unequal-norm element |
| an integer element of H_5^perp | 0 | invertible |

Those four also appear in `results/hw_estimate/annihilator_strata.json`.

## Scope

This is a reproduction of known theorems on sampled exact points; it proves
nothing beyond them. It does not decompose D_(5,8) or D_(5,12), and it says
nothing about the members of ZD_12(A_5) outside H_5^perp or about the
bracket-axis limits. Those remain roadmap item 3 of
`gororoba_quantum/RANK_STRATUM_TOPOLOGY.md`.

## Replay

- `"$PYTHON" scripts/d_locus_nullity.py --check docs/evidence/d_locus_nullity/result.json --limit 20`
  recomputes the first 20 frames (100 pairs) in about 6 s (gate core-323,
  pr tier).
- Without `--limit` the same command recomputes all 1000 pairs in about
  62 s (gate core-324, full tier).

Both gates run in normal and `-O` mode, and both re-derive the summary from
the rows.
