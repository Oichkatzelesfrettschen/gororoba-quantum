# Gaussian-integer certificates of the G_2 derivation tables and the W8 arc matrices

Three Rocq sources of gororoba-math (`rocq/quantum`) are rendered from tracked records by generators that live in gororoba-math (`ci/quantum-sources/`), so that every
integer in them has one home and a `--check` that compares the two:

| Rocq source | Generator | Record it reads | What it states |
| --- | --- | --- | --- |
| `gororoba-math:rocq/quantum/CdTowerG2Derivations.v` | `gaussian_certificates.py` | [g2-derivation-tables.json](../a5-kernel-attachments/g2-derivation-tables.json) (ledger row `A5-453`), `left-inverses.json` | each of the 14 tables satisfies the Leibniz rule D(xy) = D(x) y + x D(y) on the sedenions over every commutative ring that receives the Gaussian integers, and the 14 maps are linearly independent there |
| `gororoba-math:rocq/quantum/A5W8ArcMatrixRanks.v` | `gaussian_certificates.py` | [w8-component-arc-matrices-qi.json](../a5-char0-transfer/w8-component-arc-matrices-qi.json) (ledger row `A5-448`), `left-inverses.json` | for each of the eight 24 x 6 matrices M a 6 x 24 matrix L and a Gaussian integer d with L M = d I, so that a column relation M a = 0 has h(d) a_l = 0 and the six columns are independent where h(d) is a nonzero divisor |
| `gororoba-math:rocq/quantum/CdTowerG2DerivationSpan.v` | `render_span.py` | `span.json` | for every linear map F of the sedenions that satisfies the Leibniz rule on the basis units, h(6) F is a combination of the 14 tables ([derivations_spanned]); where h(6) is invertible or a nonzero divisor, F is that combination ([derivations_spanned_invertible], [derivations_spanned_regular]), and so over the Gaussian integers ([derivations_spanned_gaussian]) |

## Generators

The generators `gaussian_certificates.py`, `span_certificate.py` and `render_span.py`, the records they write
(`left-inverses.json`, `span.json`) and the mutation controls and Rocq driver of the span checks (`make_mutants.py`,
`make_span_mutants.py`, `run_span_checks.sh`, `SpanQueries.v`) are files of gororoba-math under `ci/quantum-sources/`.
They read the two records named above and `gororoba_quantum/cd_core.py` of this repository through
`GOROROBA_QUANTUM`, and `GOROROBA_QUANTUM=PATH sh ci/check_quantum_sources.sh` there renders the three sources again
and compares each with the tracked file. Three of them, `gaussian_certificates.py`, `span_certificate.py` and
`render_span.py`, and `span.json` stay here with their bytes, because the A5-500 row of the findings ledger cites them
as evidence; no gate renders a source from them. This directory also keeps [source_hashes.sha256](source_hashes.sha256), the
sha256 of the seven gororoba-math sources that the retained records bind (the three generated files and
`GaussianIntegerHom.v`, `MatrixLeftInverseCertificate.v`, `MatrixSplittingCertificate.v` and
`CdTowerLeibnizSystem.v`).

## Scope and limits

- The proofs take the tables as given. That the 14 tables are the G_2 derivations, and that the 24 x 6 matrices are
  the Jacobians [dF | F] of the arc families, is the claim of the producers of the two records, outside the proofs.
- Independence over Q(i) follows from the Gaussian-integer statement by clearing denominators, in prose: no
  theorem models Q(i).
- Where the image h(d) of the scalar of an arc certificate is a zero divisor, the theorem gives no conclusion about
  the columns. Over a field this happens only in a characteristic that divides the norm of d, and the image depends
  on the homomorphism h: one of the two square roots of -1 modulo a prime can send d to 0 while the other does not.
  The scalars are d = (-461761890399040, 4026451401753088) and (-37777639648320, 2610795944739840) for the linear
  family at the two points, -3600 and -134784 for the series family; the N- and N+ matrices of one family and point
  share their scalar.
- The derivation certificate has d = 1, so its 14 maps are independent over every commutative ring that receives
  the Gaussian integers.
- The span theorem multiplies by 6: it states h(6) F = sum c_t D_t. It says nothing about a ring where 2 or 3 is a zero
  divisor (h(6) is then a zero divisor, and the combination holds only after multiplication by it), and it states
  F itself where the image of 6 is a nonzero divisor ([derivations_spanned_regular]) or invertible
  ([derivations_spanned_invertible]).
- Computed, not proved: with exact arithmetic (python-flint), the Leibniz system for a linear map of the sedenions,
  4096 equations in 256 unknowns, has rank 242 and nullity 14 over Q, with Smith invariants 1 (192 times), 2 (49
  times) and 6 (once), hence nullity 64 over F_2 and 15 over F_3 (`span_certificate.py --smith` recomputes the
  invariants and compares them). With the independence theorem this gives a derivation algebra of dimension 14 in
  characteristic zero, spanned by the 14 tables; the span theorem is the Rocq statement of the spanning half, with the
  multiplier 6. That the algebra is g_2 is not stated by any theorem.
- Rocq receipts (compile without warnings, closed assumptions, kernel check without axioms, mutants rejected) are
  those of gororoba-math pull requests 14 and 16 (both merged). This directory holds no compile or kernel-check
  receipt, and the pull-request checks run none.

## Binding to gororoba-math

`gororoba_quantum/math_sources.py` resolves each source of that ledger through a gororoba-math checkout at the commit
of `ci/gororoba_math.pin`, and a pin that holds a different byte of one of the seven fails the gates tagged
`requires: ["gororoba-math"]`. A source of gororoba-math that no record here or elsewhere cites is not read.
