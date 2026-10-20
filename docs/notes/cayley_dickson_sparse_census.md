# Cayley-Dickson sparse census: domain, evidence, and count conventions

The exact census has one current numerical owner: the dimension-32 entry in
[annihilator_strata.json](../../results/hw_estimate/annihilator_strata.json).
The per-paper notes own the published theorems. The independent scratch
calculation in the [group-theory handback](../archive/handbacks/cayley_dickson_group_theory.md)
provides historical corroboration of the same finite count.

## Dimension-32 domain and complete count

The domain consists of `(e_i + s e_j)/sqrt(2)` with `1 <= i < j <= 31`
and `s in {+1,-1}`, under the multiplication convention in
[cd_core.py](../../gororoba_quantum/cd_core.py). Fixing the leading coefficient
positive omits each global negative duplicate. The denominator is
`2*binomial(31,2)=930` unit elements.

| Annihilator dimension | Left-multiplication rank | Elements |
| ---: | ---: | ---: |
| 0 | 32 | 342 |
| 4 | 28 | 168 |
| 8 | 24 | 168 |
| 12 | 20 | 252 |
| 16 | 16 | 0 |
| Total | | 930 |

The JSON histogram stores the four occurring nullities. The zero count for
nullity 16 follows from the complete finite denominator; the largest nullity
in this family is 12. [annihilator_strata.py](../../gororoba_quantum/annihilator_strata.py)
computes every rank through exact integer `2x2` blocks. Independent
fraction-free elimination and full-matrix kernel checks verify representatives
of every occurring stratum.

The retained file has SHA-256
`3e7064c2c99a71519b221420cb70793818400f0dc4df59d46ad8a32f40ca151b`.
The ordered dimension-32 row digest is
`9d21744b5e2c5494fb6a006732bdbc603fece830bf6ca1721678607e40a0dcf8`.
The [verification manifest](../../results/hw_estimate/cayley_dickson_topology_verification.json)
records the source and execution provenance. The earlier independent SVD
scratch census agrees with the exact count; floating-point residuals and
scratch provenance give that cross-check a weaker certification boundary.

Replay from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" annihilator_strata.py --max-dimension 32
)
```

Compare the `dimensions` entry with `dimension == 32`. The retained file
covers dimensions through 256, so its whole-file bytes differ from a replay
that stops at 32.

## Continuous loci and the missing sparse stratum

The finite census exhausts its two-term family. Arbitrary real coefficients
admit additional elements: the exact unit vector
`(e1+e10+e18-e25)/2` has nullity 16. The
[rank-polynomial record](../../results/hw_estimate/rank_polynomials.json)
certifies the witness independently of the maximal-annihilator lift in the
census record. The [BDI note](math-0511691.md) owns the published
all-dimensional bounds and maximal-stratum theorem.

[RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md)
gives exhaustive polynomial rank predicates for real coefficients, rational
kernel charts and overlap formulas, and a complete attachment model over a
specified polynomial path. The model extends by induction to that path's
zero-padding embeddings in every higher dimension. Full continuous base
decomposition, all attachments, and the topology of the complete `Z_5` remain
the roadmap's research obligations. A finite census or a restricted path
does not discharge those obligations.

## Sedenion counts refer to different objects

The [Reggiani note](2411.18881.md) owns the paper interpretation and
normalization. The following counts distinguish its table from the repository
corpus used by [designs.py](../../gororoba_quantum/designs.py):

| Object | Count |
| --- | ---: |
| Reggiani Table 1 pairs | 84 |
| Repository ordered signed pair rows | 336 |
| Corpus rows with first relative sign `+1` | 168 |
| Distinct canonical first operands | 84 |

Operand ordering, relative signs, and canonicalization define different
denominators. The finite rows sample the published normalized pair bundle
`SU(2) -> G_2 -> V_2(R^7)`; they supply neither a cellular decomposition nor
an independent proof of its topology.
