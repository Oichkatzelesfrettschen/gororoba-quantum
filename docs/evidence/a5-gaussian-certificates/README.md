# Gaussian-integer certificates of the G_2 derivation tables and the W8 arc matrices

Three Rocq sources of gororoba-math (`rocq/quantum`) are rendered from tracked records by the generators in this
directory, so that every integer in them has one home here and a `--check` that compares the two:

| Rocq source | Generator | Record it reads | What it states |
| --- | --- | --- | --- |
| `gororoba-math:rocq/quantum/CdTowerG2Derivations.v` | `gaussian_certificates.py` | [g2-derivation-tables.json](../a5-kernel-attachments/g2-derivation-tables.json) (ledger row `A5-453`), `left-inverses.json` | each of the 14 tables satisfies the Leibniz rule D(xy) = D(x) y + x D(y) on the sedenions over every commutative ring that receives the Gaussian integers, and the 14 maps are linearly independent there |
| `gororoba-math:rocq/quantum/A5W8ArcMatrixRanks.v` | `gaussian_certificates.py` | [w8-component-arc-matrices-qi.json](../a5-char0-transfer/w8-component-arc-matrices-qi.json) (ledger row `A5-448`), `left-inverses.json` | for each of the eight 24 x 6 matrices M a 6 x 24 matrix L and a Gaussian integer d with L M = d I, so that a column relation M a = 0 has h(d) a_l = 0 and the six columns are independent where h(d) is a nonzero divisor |
| `gororoba-math:rocq/quantum/CdTowerG2DerivationSpan.v` | `render_span.py` | `span.json` | for every linear map F of the sedenions that satisfies the Leibniz rule on the basis units, h(6) F is a combination of the 14 tables ([derivations_spanned]); where h(6) is invertible, F is that combination |

## Files

| File | Kind | Content |
| --- | --- | --- |
| `gaussian_certificates.py` | generator | reads the two records with exact key sets and integer types, computes a left inverse of each matrix (adjugate of the first independent rows, divided by the integer content of the block; a unit scalar becomes 1), renders the first two Rocq files and `left-inverses.json` |
| `left-inverses.json` | record | the selected rows, the scalar d, its norm and the nonzero entries of each left inverse (one for the 256 x 14 matrix of the derivation tables, eight for the arc matrices); every entry is [real part, imaginary part] |
| `make_mutants.py` | mutation controls | six edited copies of the first two Rocq files, each of which must fail to compile in the lemma named beside it |
| `span_certificate.py` | computation | the Leibniz system of the sedenions (4096 forms in 256 unknowns, product `cd_sign(16, a, b)` of `gororoba_quantum/cd_core.py`), a greedy choice of 242 independent forms, and P, d with P M + d V C = d I for the tables V and their left inverse C; writes `span.json`, or verifies it |
| `span.json` | record | row order 0 (`"seed": 0`, the lexicographic order of the triples, no random draw): d = 6, 242 triples, 1195 nonzero entries of P, largest absolute value 12 |
| `render_span.py` | generator | reads `span.json` with exact key sets, integer types, counts and index ranges and renders the third Rocq source |
| `make_span_mutants.py` | mutation controls | six edited copies of the span source, each with the lemma that must reject it |
| `run_span_checks.sh`, `SpanQueries.v` | driver | the Rocq half of the span checks for a machine that holds Rocq: compile of the three span sources, 10 assumption queries, kernel check, the six mutants, one verdict line |

The tests are [test_a5_gaussian_certificates.py](../../../tests/gororoba_quantum/test_a5_gaussian_certificates.py).

## Commands

Run from the repository root with `PYTHON` naming the interpreter of the pins. The `--check` commands read
gororoba-math through `GOROROBA_MATH` at the commit of `ci/gororoba_math.pin`, with each source checked against the
sha256 the retained records hold ([math_source_generators.py](../../../scripts/math_source_generators.py));
`--write` replaces the sources in that checkout and `left-inverses.json` here.

```sh
"$PYTHON" scripts/math_source_generators.py gaussian_certificates --check
"$PYTHON" scripts/math_source_generators.py render_span --check
"$PYTHON" docs/evidence/a5-gaussian-certificates/span_certificate.py \
  --left-inverses docs/evidence/a5-gaussian-certificates/left-inverses.json --verify
```

The first two are on-demand gates of `ci/gates.json` (`sources-a5-gaussian-certificates-check` and
`sources-a5-gaussian-certificates-span-check`, tagged `requires: ["gororoba-math"]`). The third checks
C V = I and P M + d V C = d I on `span.json` in Python integers, a Gaussian integer being a pair, and needs no
python-flint. Without the runner, `--rocq DIRECTORY` names the directory of the Rocq files.

`span_certificate.py` without `--verify` recomputes `span.json`; with `--check` it compares the recomputation with the
file. It needs python-flint 0.9.0, the pin of `requirements.txt`, which the pull-request environment holds, so the
test `test_flint_recomputes_the_tracked_span_record` recomputes the record at row order 0 on every run. The left-inverse
record is an explicit argument (`--left-inverses`), and C V = I is checked before P is computed.

The mutation controls need Rocq. On a machine that has it, `make_mutants.py ROCQ_DIRECTORY OUTPUT_DIRECTORY` and
`make_span_mutants.py SOURCE_V OUTPUT_DIRECTORY` write the edited copies, and `sh run_span_checks.sh BUILD_DIRECTORY`
runs the span checks. The build directory holds the three span sources, `SpanQueries.v`, `make_span_mutants.py` and the
compiled sources they import (`MatrixSplittingCertificate.v`, `CdTowerLeibnizSystem.v`, `CdTowerG2Derivations.v` and
the files below them). No Rocq compile
runs in the pull-request checks; the tests check that each mutant differs from its original in the one intended line,
ahead of the lemma named for it.

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
  F itself only where 6 is invertible.
- Computed, not proved: with exact arithmetic (python-flint), the Leibniz system for a linear map of the sedenions,
  4096 equations in 256 unknowns, has rank 242 and nullity 14 over Q, with Smith invariants 1 (192 times), 2 (49
  times) and 6 (once). With the independence theorem this gives a derivation algebra of dimension 14 in
  characteristic zero, spanned by the 14 tables; the span theorem is the Rocq statement of the spanning half, with the
  multiplier 6. That the algebra is g_2 is not stated by any theorem.
- Rocq receipts (compile without warnings, closed assumptions, kernel check without axioms, mutants rejected) are
  those of gororoba-math pull requests 14 (merged) and 16 (open). This directory holds no compile or kernel-check
  receipt, and the pull-request checks run none.

## Binding to gororoba-math

`scripts/math_source_generators.py` resolves each source through `gororoba_quantum/math_sources.py`. A checkout at the
commit of `ci/gororoba_math.pin` supplies the sources, and a retained record must hold the sha256 of each one it
reads: a ledger row `DIGEST  proofs/NAME.v` in `docs/evidence/*/*.sha256`, or a registry evidence entry. Every name in
the `_RocqProject` of the pinned checkout needs such a digest, because the shadow root of the replay bundles and
`verified_sources` read them all; the sources of this directory add seven names to that list: the three generated
files named above and the hand-written `GaussianIntegerHom.v`, `MatrixLeftInverseCertificate.v`,
`MatrixSplittingCertificate.v` and `CdTowerLeibnizSystem.v`. A pin that holds a source without its digest fails every
gate tagged `requires: ["gororoba-math"]` and the Rocq replay of `proofs.yml`, with a message that names the missing
digest.
