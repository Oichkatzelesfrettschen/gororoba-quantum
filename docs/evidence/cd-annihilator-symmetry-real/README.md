# Annihilator-symmetry proof on the real tower

[CdAnnihilatorSymmetryReal.v](../../../proofs/CdAnnihilatorSymmetryReal.v)
proves, for every Cayley-Dickson dimension n = 2^k, that left and right
annihilators coincide on the real pair tower that
[CdTowerReal.v](../../../proofs/CdTowerReal.v) defines: a z = 0 exactly
when z a = 0, for every pair of elements with real coordinates. The tower
file restates the definitions and linear laws of
[CdImaginarySumConference.v](../../../proofs/CdImaginarySumConference.v)
with the Stdlib reals in place of the integers, so the theorem is the
real-coefficient statement of
[cd-one-sided-inverses.md](../../notes/topics/cd-one-sided-inverses.md),
which the integer-tower bundle
[cd-annihilator-symmetry](../cd-annihilator-symmetry/README.md) reaches only
for rational elements. The route is the one of Biss, Dugger and Isaksen
([math-0511691.md](../../notes/math-0511691.md)), Lemma 9.2 and Corollary
9.3, where the integer bundle follows the note's trace-form argument.

| Theorem | Statement, for every k and all x, y, z, a, b of the level-k tower |
| --- | --- |
| `norm_mul` | x conj(x) = <x, x> 1 and conj(x) x = <x, x> 1 (Lemma 3.6) |
| `adjoint` | <x y, z> = <y, conj(x) z> and <x y, z> = <x, z conj(y)> (Lemma 3.4) |
| `re_commutator` | re(x y) = re(y x) (Lemma 2.6) |
| `re_associator` | re((x y) z) = re(x (y z)) (Lemma 2.8) |
| `conj_mul_left` | x (conj(x) y) = conj(x) (x y), the identity of Lemma 9.2 |
| `conj_mul_right` | (x y) conj(y) = (x conj(y)) y |
| `lemma_9_2` | x y = 0 exactly when conj(x) y = 0, and exactly when x conj(y) = 0 |
| `kernel_equality` | a z = 0 exactly when z a = 0 (Corollary 9.3) |
| `purity_left` | a z = 0 with a != 0 and z != 0 implies re(a) = 0 and re(z) = 0 (Lemma 9.4) |
| `purity_right` | z a = 0 with a != 0 and z != 0 implies re(a) = 0 and re(z) = 0 |
| `right_inverse_form` | a b = 1 implies b = conj(a)/<a, a> + w for some w with a w = 0 |
| `direct_finiteness` | a b = 1 implies b a = 1 |
| `lemma_9_5` | at level k + 1, x y = 0 with y != 0 implies <x, 1> = 0 and <x, i> = 0, where i = (0, 1) is the adjoined unit (Lemma 9.5) |
| `annihilator_orthogonal` | at level k + 1, x != 0 and x y = 0 imply <y, 1> = 0 and <y, i> = 0 |

The norm and adjoint laws run by induction on the doubling as in the integer
bundle. The identity of Lemma 9.2 needs no induction: `conj_split` writes
conj(x) = 2 re(x) 1 - x, and the `alg` rewrite database expands both sides
of x (conj(x) y) = conj(x) (x y) to 2 re(x) (x y) - x (x y); the mirror
identity is the same reflection applied to y. Lemma 9.2 then reads the norm
of conj(x) y as <y, x (conj(x) y)> = <y, conj(x) (x y)> by the adjoint law,
which x y = 0 annihilates, and `dot_self_zero` (a sum of squares vanishes
only at zero) closes it; the converse direction substitutes conj(x) for x.
Corollary 9.3 conjugates a z = 0 to conj(z) conj(a) = 0 and applies the two
equivalences in turn. The real parts of commutators and associators are
<x y, 1> moved through the adjoints, and the purity lemma reads a z = 0 and
conj(a) z = 0 as (a + conj(a)) z = 2 re(a) z = 0 with z nonzero. The
corollary applies the theorem to b - conj(a)/<a, a>, which a annihilates,
and cancels the positive real <a, a>. Lemma 9.5 is stated one level up,
where the adjoined unit i = (0, 1) exists: `dot_i_unit` reads <x, i> as the
real part of the second half of x, and `swap_zero_divisor` is the paper's
computation that (a, b)(c, d) = 0 with a imaginary gives
(-conj(d), c)(b, a) = (a c - conj(d) b, conj(d a + b conj(c))) = 0; the
kernel swap and the purity lemma on (b, a) then make b imaginary, and
`swap_nonzero` carries the nonzero hypothesis from (c, d) to (-conj(d), c).
`annihilator_orthogonal` applies the lemma to the annihilated element through
the kernel equality.

No step uses associativity, alternativity or multiplicativity of the norm,
which fail from k = 4 on. The real coefficients admit division, so the
right-inverse family is stated in the note's affine form rather than the
integer-cleared one.

Every theorem rests on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)): the Calculus of Inductive Constructions with a
predicative Set and no rewrite rules, with the equality types `eq`,
`eq_true` and `eq_dep` and Btauto's `null` typed under the default rule that
inductive indices do not raise the universe level. Each of the fourteen
assumption queries lists exactly the two axioms of Stdlib's construction of
the reals, `ClassicalDedekindReals.sig_forall_dec` and
`FunctionalExtensionality.functional_extensionality_dep`
([assumptions.txt](assumptions.txt)); the full imported-library kernel
context also names `ClassicalDedekindReals.sig_not_dec` and
`Classical_Prop.classic`, as the real terminal-channel certificate of
[formal_certificates](../formal_certificates/README.md) does. No proof here
introduces an axiom of its own.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-annihilator-symmetry-real/replay_rocq.sh
sha256sum -c docs/evidence/cd-annihilator-symmetry-real/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
real tower, this proof and [assumptions.v](assumptions.v) in temporary
storage with `-w @all`, fails on any warning or compiler output, runs
`rocq check`, and compares the outputs byte for byte with
[assumptions.txt](assumptions.txt) and [kernel.txt](kernel.txt). The ci.yml
job rocq-replay runs it beside the other tower bundles, and
`scripts/rocq_kaggle_replay.py --only cd-annihilator-symmetry-real` selects
it. `source_hashes.sha256` binds both proof sources and the receipts, so the
ledger test fails on an edit to either source without new receipts. The
replay takes about 28 s on the build host.
