# One-sided inverses in Cayley-Dickson algebras: exact replay

`record.json` is the exact record behind
[cd-one-sided-inverses.md](../../notes/topics/cd-one-sided-inverses.md).
`scripts/cd_one_sided_inverses.py` derives every entry from
`gororoba_quantum/cd_core.py` (`cd_sign` for the multiplication matrices,
`cd_multiply_exact` for the inverse products) in exact rational arithmetic.
Values are integers, booleans and strings; the record carries no floats,
paths, timestamps or worker counts, so pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes.

## What the record establishes

The `identities` block checks three multilinear identities on every basis
pair of the dimensions 2 through 128. Each identity is linear in each of its
arguments, so the basis check decides it for every element of that algebra:

| Identity | Basis form checked | Elements it covers |
| --- | --- | --- |
| L1: a conj(a) = conj(a) a = <a, a> 1 | e_i conj(e_j) + e_j conj(e_i) = 2 [i = j], both orders | every a |
| L2: <a x, y> = <x, conj(a) y> | sigma(i, j) = c_i sigma(i, i XOR j), c_0 = 1, c_i = -1 otherwise | every a, x, y |
| L2': <x a, y> = <x, y conj(a)> | sigma(j, i) = c_i sigma(i XOR j, i) | every a, x, y |

The `kernels` block, at dimensions 16 and 32, takes every element a of three
deterministic families, computes ker L_a and ker R_a by exact Gauss-Jordan
elimination, and requires: the two kernels span the same subspace; when the
kernel is nonzero, a and every kernel vector are pure; and for every kernel
basis vector z, b = conj(a)/<a, a> + z satisfies a b = b a = 1. A violated
requirement raises before any record is written, so the retained counts are
the counts of elements that passed.

| Dimension | Family | Elements | With a kernel | Kernel dimensions |
| --- | --- | ---: | ---: | --- |
| 16 | signed two-blades e_i + s e_j | 210 | 84 | 4 (84) |
| 16 | three-unit sums e_i + e_j + e_k, i < j < k < 16 | 455 | 0 | none |
| 16 | doubly pure grid, up to two coordinates per half | 3626 | 1848 | 4 (1848) |
| 32 | signed two-blades | 930 | 588 | 4 (168), 8 (168), 12 (252) |
| 32 | three-unit sums with indices below 16 | 455 | 0 | none |
| 32 | doubly pure grid, one coordinate per half | 450 | 420 | 4 (168), 12 (252) |

The 84 sedenion two-blade zero divisors match the census of
`cd_core.sedenion_zero_divisors`, and the 168, 168, 252 split at dimension 32
matches the annihilator dimensions of
[two_blade_blocks.json](../box_kite_census/two_blade_blocks.json). The
doubly pure grid at dimension 16 is every u + v with u in the octonion
imaginary span, v in the span of e_9 .. e_15, coordinates in {-1, 0, 1}, at
most two nonzero coordinates per half, the first nonzero coordinate of u
equal to 1 and <u, u> = <v, v>; 1848 of its 3626 elements are zero divisors,
every one with a four-dimensional annihilator, and every one passes.

## Replay

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error scripts/cd_one_sided_inverses.py --check docs/evidence/cd-one-sided-inverses/record.json
"$PYTHON" -B -W error scripts/cd_one_sided_inverses.py --self-test
```

Gate `core-record-check-08` (`tests/test_cli_record_checks.py`) runs the
check: `--check` recomputes the record and requires byte equality with the
canonical JSON (sorted keys, indent 2). The pooled run takes about 6 s on
the build host and the serial run about 20 s.
`tests/scripts/test_cd_one_sided_inverses.py`, in the behavioral suite,
holds the contracts and their planted defects: a conjugation that fixes e_1
fails L2 at dimension 4, a right-multiplication matrix with one flipped
sign fails the kernel equality on e_1 + e_10, and the partner blade
e_1 - e_10 has a kernel of the same dimension that the subspace test tells
apart. `--self-test` runs the first and third of these in the script.

## Boundary

The record covers the listed families at dimensions 16 and 32 and the basis
identities through dimension 128. The theorem for every element of every
dimension is the written argument of the note, which rests on L1, L2 and the
anti-automorphism law conj(x y) = conj(y) conj(x); the note proves all three
for every dimension by induction on the doubling. No Rocq source covers the
kernel equality. The falsifier of the theorem is one element a of any
Cayley-Dickson algebra with ker L_a different from ker R_a, or one pair with
a b = 1 and b a different from 1; the check at `--write` time raises on the
first such element.
