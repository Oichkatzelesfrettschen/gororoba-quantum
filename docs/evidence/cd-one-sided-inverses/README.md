# One-sided inverses in Cayley-Dickson algebras: exact replay

`record.json` is the exact record behind
[cd-one-sided-inverses.md](../../notes/topics/cd-one-sided-inverses.md).
`scripts/cd_one_sided_inverses.py` derives every entry from
`gororoba_quantum/cd_core.py` (`cd_sign` for the multiplication matrices,
`cd_multiply_exact` for the inverse products) in exact rational arithmetic.
Values are integers, booleans and strings; the record carries no floats,
paths, timestamps or worker counts, so pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes, which
`tests/scripts/test_cd_one_sided_inverses.py` checks on the two-blade family.
Tags: [E] exact finite computation of this record; [T] written argument of
the note; [I] interpretation.

## What the record establishes

[E] The `identities` block checks four identities on every basis pair of
the dimensions 2 through 128. L0, L2 and L2' are linear in each argument
and L1 is checked in its polarized bilinear form, so each basis check
decides its identity for every element of that algebra:

| Identity | Basis form checked | Elements it covers |
| --- | --- | --- |
| L0: conj(x y) = conj(y) conj(x) | sigma(i, j) c_(i XOR j) = c_j c_i sigma(j, i), c_0 = 1, c_i = -1 otherwise | every x, y |
| L1: a conj(a) = conj(a) a = <a, a> 1 | e_i conj(e_j) + e_j conj(e_i) = 2 [i = j], both orders (polarization) | every a |
| L2: <a x, y> = <x, conj(a) y> | sigma(i, j) = c_i sigma(i, i XOR j) | every a, x, y |
| L2': <x a, y> = <x, y conj(a)> | sigma(j, i) = c_i sigma(i XOR j, i) | every a, x, y |

[E] The `kernels` block takes every element a of the families below,
computes ker L_a and ker R_a by exact Gauss-Jordan elimination, and
requires: the two kernels span the same subspace; when the kernel is
nonzero, a and every kernel vector are pure; and for every kernel basis
vector z, b = conj(a)/<a, a> + z satisfies a b = b a = 1. A violated
requirement raises before any record is written, so the retained counts are
the counts of elements that passed, and `strictly_one_sided_inverses` and
`annihilators_agree` are derived from the worker results.

| Dimension | Family | Elements | With a kernel | Kernel dimensions | Inverse offsets checked |
| --- | --- | ---: | ---: | --- | ---: |
| 16 | signed two-blades e_i + s e_j | 210 | 84 | 4 (84) | 336 |
| 16 | three-unit sums e_i + e_j + e_k, i < j < k | 455 | 0 | none | 0 |
| 16 | doubly pure grid, two coordinates per half | 1764 | 882 | 4 (882) | 3528 |
| 32 | signed two-blades | 930 | 588 | 4 (168), 8 (168), 12 (252) | 5040 |

[E] The 84 sedenion two-blade zero divisors match the census of
`cd_core.sedenion_zero_divisors`, and the 168, 168, 252 split at dimension
32 matches the two-blade histogram of
[annihilator_strata.json](../../../results/hw_estimate/annihilator_strata.json).
The doubly pure grid is every u + v with u in the octonion imaginary span,
v in the span of e_9 .. e_15, exactly two coordinates of each half in
{-1, 1} and the first nonzero coordinate of each half equal to 1; it shares
no element with the two-blades, and 882 of its 1764 elements are zero
divisors, every one with a four-dimensional annihilator.

[I] Dimension 32 checks the two-blades alone. The three-unit sums with
indices below 16 are the sedenions embedded as (a, 0), whose
L_(a, 0) = L_a (+) R_a repeats the dimension-16 check, and every doubly pure
element with one coordinate per half is a two-blade; both were dropped for
that reason. The sign of v's lead coordinate adds no new kernel because the
automorphism (p, q) -> (p, -q) of the doubling carries u - v onto u + v.

## Replay

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error scripts/cd_one_sided_inverses.py --check docs/evidence/cd-one-sided-inverses/record.json
"$PYTHON" -B -W error scripts/cd_one_sided_inverses.py --self-test
```

Gate `core-record-check-08` (`tests/test_cli_record_checks.py`) runs the
check in process: `--check` recomputes the record and requires byte equality
with the canonical JSON (sorted keys, indent 2). The serial run takes about
10 s on the build host and the pooled command-line run about 2 s.
`tests/scripts/test_cd_one_sided_inverses.py`, in the behavioral suite,
holds the contracts and their planted defects: the matrices are the columns
of `cd_multiply_exact`; one flipped sign-table entry at dimension 4 fails L1,
L2 or L2' by name; a conjugation that fixes e_1 fails the identities; a
right-multiplication matrix with one flipped sign fails the kernel equality
on e_1 + e_10; a kernel vector with a real part fails purity; a corrupted
b a product is reported as a one-sided inverse; a wrong conjugation breaks
the canonical inverse; and the partner blade e_1 - e_10 has a kernel of the
same dimension that the subspace test tells apart. `--self-test` runs the
conjugation and partner-blade checks in the script.

## Boundary

[I] The record covers the listed families at dimensions 16 and 32 and the
basis identities through dimension 128. The theorem for every element of
every dimension is the written argument of the note [T], which rests on L0,
L1 and L2; the note proves all three for every dimension by induction on the
doubling, and the kernel equality itself is Corollary 9.3 of math/0511691.
No Rocq source covers the kernel equality. The falsifier of the theorem is
one element a of any Cayley-Dickson algebra with ker L_a different from
ker R_a, or one pair with a b = 1 and b a different from 1; the check at
`--write` time raises on the first such element.
