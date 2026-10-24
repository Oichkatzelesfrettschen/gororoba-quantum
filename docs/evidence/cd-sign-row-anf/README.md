# Sign-row ANF proof

[CdSignRowAnf.v](../../../proofs/CdSignRowAnf.v) proves the algebraic normal
form (ANF) results of [cd_phase_degree.md](../../notes/cd_phase_degree.md)
for the sign rows of every Cayley-Dickson dimension n = 2^k. It requires
[CdTowerBasisSign.v](../../../proofs/CdTowerBasisSign.v) and the conference
proof below it unchanged ([tower basis-sign bundle](../cd-tower-basis-sign/README.md)).
The left sign row of e_m is f_m(x) = [sigma_k(m, x) = -1] and the right sign
row is h_m(x) = [sigma_k(x, m) = -1], both read through `am_sign` as
`am_exponent k x m` and `am_exponent k m x`.

A truth table f on x < 2^k has coefficient `anf_coef k f s` on the monomial
prod_(i in s) x_i: the Moebius transform, the parity of f over the submasks
of s. `anf_inversion` rebuilds f from those coefficients and `anf_unique`
shows that no other coefficient table rebuilds f, so `anf_coef` is the ANF.
A monomial's weight is its count of variables, and `degree_is k f d` states
that every monomial f carries has weight at most d and one of weight d is
present.

| Theorem | Statement, for every k and m < 2^k |
| --- | --- |
| `anf_inversion` | f(x) = sum over submasks s of x of `anf_coef k f s` |
| `anf_unique` | the coefficients of the table a coefficient vector c rebuilds are c |
| `sign_row_sigma`, `right_row_sigma` | (-1)^f_m(x) = sigma_k(m, x) and (-1)^h_m(x) = sigma_k(x, m) |
| `sign_row_top` | k >= 2: f_m carries no degree-k monomial |
| `sign_row_leading` | k >= 3: the monomial omitting x_i has coefficient bit i of m (Theorem 3) |
| `sign_row_degree` | k >= 3, m != 0: the full monomial is absent and the one omitting x_(log2 m) is present |
| `sign_row_degree_is` | k >= 3, m != 0: f_m has degree exactly k - 1 |
| `sign_row_degree_all` | k >= 1, m != 0: f_m has degree exactly max(1, k - 1) (Theorem 1) |
| `right_row_degree` | m != 0: h_m has degree 1 when m is a power of two and max(1, bitlen(m) - 2) otherwise (Proposition 4) |

The coefficient arguments split every sum at the highest index bit j: the
pair x = (y, 0), (y, 1) of a left sign row sums to the commutator exponent of
Definition 3.2 of Albuquerque and Majid (`am_altercommutative`), complemented
when m has bit j set, and that exponent is the indicator of y outside
{0, m'}. Its parity over a half range with bit i clear is bit i of m', which
gives the leading layer; the top bit reads the row one level down and the
diagonal F(y, y) = -1 off the identity (`am_diagonal`). The right rows
satisfy three slice identities read from the Corollary 4.3 recursion
(`am_ll`, `am_lh`, `am_hl`, `am_hh`):

- m < 2^j: h_m(y, xi) = h_m(y) + xi, so the top variable adds only the
  monomial x_j;
- m = 2^j: h_m(y, xi) = xi;
- m = m' + 2^j with m' != 0: h_m(y, xi) = f_(m')(y), the left sign row of
  e_(m') one level down, of degree max(1, j - 1).

The degree of h_m is therefore fixed at the level bitlen(m) where e_m first
appears, which `right_row_degree` proves by induction on k. The quaternion
and complex rows of `sign_row_degree_all` (k <= 2) close by evaluation of
the closed terms, without `vm_compute`.

The theorems rest on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)), identical to the tower basis-sign bundle's: the
Calculus of Inductive Constructions with a predicative Set and no rewrite
rules, with `eq`, `eq_true`, `eq_dep` and Btauto's `null` typed under the
default rule that inductive indices do not raise the universe level. Beyond
the kernel the proofs use the definitions and proved lemmas of Corelib and
Stdlib 9.2.0: natural-number arithmetic through `lia`, the bitwise operations
`Nat.lxor`, `Nat.ldiff`, `Nat.ones`, `Nat.testbit` and `Nat.log2` with their
Stdlib lemmas, and Btauto's Boolean normalization. Each of the ten assumption
queries in [assumptions.v](assumptions.v) prints `Closed under the global
context` ([assumptions.txt](assumptions.txt)): the proof terms reach the
kernel through those definitions alone, with every classical, extensionality
and choice principle absent. The remaining trust is the transcription of the
cd_sign loop and of Corollary 4.3 that the tower bundle names, and the
reading of `anf_coef` as the ANF, which `anf_inversion` and `anf_unique`
settle inside the proof.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-sign-row-anf/replay_rocq.sh
sha256sum -c docs/evidence/cd-sign-row-anf/source_hashes.sha256
```

`replay_rocq.sh` requires the banner of [toolchain.txt](toolchain.txt) (Rocq
9.3.0 on OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`), compiles the
three proof sources and [assumptions.v](assumptions.v) in temporary storage
with `-w @all`, fails on any warning or compiler output, runs `rocq check`,
and compares the outputs byte for byte with the receipts. The ci.yml job
rocq-replay runs it beside the other Rocq bundles, and `source_hashes.sha256`
binds the three proof sources and the receipts. The replay takes about 26 s
on the build host.
