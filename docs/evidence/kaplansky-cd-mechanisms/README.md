# Kaplansky-type mechanisms in the Cayley-Dickson algebras

`kaplansky_cd_replay.py` computes, from `cd_core.cd_sign` alone, the exact facts the
[Kaplansky mechanisms note](../../notes/topics/kaplansky-mechanisms-cayley-dickson.md) cites, and writes them to
`result.json`. Gate sources-412 reruns it with `--check` and compares the bytes.

```sh
"$PYTHON" -B -W error docs/evidence/kaplansky-cd-mechanisms/kaplansky_cd_replay.py --check
```

| Section of `result.json` | Content | Dimensions |
| --- | --- | --- |
| `fano` | the seven octonion Fano lines, their pairwise intersections and mod-2 incidence Gram, their complements as nontrivial cosets of order-4 subgroups, and the complement incidence counts of family 197 p. 5 | 8 |
| `skeleton` | ordered pairs of index pairs with `i xor j = k xor l`, the cocycle cross-ratio `chi`, the brute-force sign lift, zero products off the skeleton, invariance of `chi` under every single-index re-signing, and the distribution of `m = i xor j` | 8, 16, 32 |
| `units_square_to_minus_one` | `e_m^2 = -1` for every `m != 0` | 8, 16, 32 |
| `affine_sign_rows` | rows `m` whose sign function `x -> sigma(m, x)` is affine over `F_2` | 4, 8, 16, 32 |
| `annihilators` | nullity of `L_a` on every two-blade zero divisor, and whether its kernel is pure and right-annihilated by `a` | 16, 32 |
| `qubit_reading` | `X^m` eigenstates and zero Bloch vectors on the support of `m` | 16, 32 |
| `left_multiplication_squares` | scalar `L_u^2` on two-unit `u`, and the invertible three-unit counterexample `e_1 + e_2 + e_12` | 16 |
| `inverse_and_zero_divisor` | the products of `e_1 + e_10`, its inverse and `e_4 - e_15` | 16 |

The script raises before writing when a written claim fails: a zero product off the skeleton, `chi` failing to
predict the lift or changing under a re-signing, a unit square other than `-1`, a mixed or one-sided kernel, a
nonzero Bloch vector on the support of `m`, or a failed inverse. Arithmetic is integer or `Fraction` throughout,
and the per-index loops run through `parallel.ordered_map`. A serial run takes about 3 s.

The source manuscripts are registered in [SOURCES.json](../../SOURCES.json) with notes
[openai-2026-torsion-free-zero-divisors.md](../../notes/papers/openai-2026-torsion-free-zero-divisors.md),
[openai-2026-torsion-free-not-directly-finite.md](../../notes/papers/openai-2026-torsion-free-not-directly-finite.md)
and [openai-2026-kadison-kaplansky-projection.md](../../notes/papers/openai-2026-kadison-kaplansky-projection.md).
The replay reads none of their bytes; the Fano incidence counts it checks are the ones those notes transcribe.
