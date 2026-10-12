# Finite endpoint information and covariance

The [typed CPU replay](probe.py) compares eight ideal cutoff-four arms at
strengths `r=0.2,0.4`: phase zero, phase pi, occupation-matched diagonal mixture
and zero interaction, with zero controls retained separately for each strength.
The [result](result.json) preserves all 72 product-measurement laws and all
reviewed mathematical fields. The replay performs zero service or QPU calls.

Every design receives 36000 shots per arm, totaling 288000 shots across eight
arms. Uniform four-setting allocation uses 9000 shots per setting; uniform
nine-setting allocation uses 4000. The phase-zero real-coherence variance ratio
**nine over four** is `2.215418334884854` at `r=0.2` and
`2.16022464218317` at `r=0.4`. Those ratios concern the recorded fixed estimators,
known finite states and ideal readout. They establish neither unknown-state
optimality nor hardware cost, billing or submission authority. The workload
excludes full-encoding references, independent calibration, packing/time controls,
implementation variants, job floors and job splits.

## Observable and covariance contracts

The left-to-right tensor convention is `q1q0`. For the truncated pair operator,

```text
Re(ab) = IX + (XX + YY - ZX)/2
Im(ab) = IY + (-XY + YX - ZY)/2
n      = 1.5 II - ZI - 0.5 IZ.
```

For setting outcomes `(s1,s0,s1*s0)`, the replay retains
`mu=(m1,m0,m12)` and

```text
P(s1,s0) = (1+s1*m1+s0*m0+s1*s0*m12)/4
Cov = [[1,m12,m0],[m12,1,m1],[m0,m1,1]] - mu mu.T.
```

A within-setting linear estimator has variance `w.T Cov w/n_setting`.
The three outcomes share shots; dropping their off-diagonal covariance changes
the precision calculation. The four-setting estimator obtains IX in XX and ZX
with equal weights. The nine-setting estimator averages IX in XX, YX and ZX.
The retained result names every weight, setting mean, covariance and per-shot
variance. Different setting and arm samples are independent by assumption.
For a general odd phase contrast, `Var((Re_plus-Re_minus)/2)` is
`(Var_plus+Var_minus-2 Cov_plus_minus)/4`. Drift or shared calibration can introduce
cross-arm covariance and requires an expanded model.

The Neyman row reserves `N/4` for ZZ and allocates the remaining shots
proportionally to square roots of the known finite-state group variances.
The row conditions on fixed estimator weights and oracle variances. A
zero-variance allocation group qualifies only under that known-state assumption;
unknown-state pilot uncertainty, integer allocations and diagnostic floors need
separate admission. The population and cutoff constraints remain explicit.

## Product-Pauli completeness boundary

Settings `ZZ,ZX,XX,YY` recover populations and real pair coherence. The physical
states `diag(p_n)+t XY` have nonzero imaginary pair coherence while reproducing
all four product-measurement laws. Adding XY alone still leaves the physical
states `diag(p_n)+t YX` invisible. Positive eigenvalues and identical outcome
laws witness both failures; this evidence concerns physical density matrices.

The unique minimal product-Pauli cover for full populations and both pair
quadratures is `ZZ,ZX,XX,YY,XY,YX,ZY`. The supplemental replay enumerates every
subset of the nine product-Pauli settings through size seven. Required
correlations force each of those seven settings. Full two-qubit state tomography
uses all nine product-Pauli settings. General rotated local bases, alternative
collective measurements, adaptive estimators and hardware-optimal designs lie
outside the declared cover space.

## Immutable provenance and normalized output

[provenance.json](provenance.json) records bounded identities and the independent
review's 812 comparisons, maximum error `1.78e-15`. The archival inputs preserve
156469 original bytes across five exact regular files:

- `inputs/reviewed_probe.py.txt`: reviewed endpoint source, SHA256
  `88bc49cf92deadba0e2ee4360825844a7c9b561647f5a76feefde8900f431029`.
- `inputs/reviewed_result.json`: reviewed endpoint result, SHA256
  `e29459a8958cc5c8ee462d2ea023b15373602d333028219e390d00635f041028`.
- The original predecessor probe/result and motivating note retain their exact
  identities in provenance. Text archival suffixes retain original source/prose
  bytes as data; typed executable normalization resides in `probe.py`.

The normalized result is a separate artifact. The replay compares all reviewed
mathematical fields, verifies the eight-arm/72-law denominator, and adds the
seven-setting cover, YX witness, provenance and source-binding receipts.
Source hashes cover the replay, rejection tests, provenance and all archival
inputs before and after computation. Regular-file, byte-size and fixed input
identity checks reject drift before numerical execution. Proposal/note hashes
establish provenance; the replay does not infer source support from prose.

Comparison requires exact keys, types, categorical values, lengths and ordering.
Finite floating values use absolute tolerance `1e-12` and relative tolerance
`1e-10`. Python/NumPy/SciPy versions are separately reported, including differences,
while numerical and structural gates retain their scope. The retained environment
is Python 3.14.7, NumPy 2.5.4 and SciPy 1.18.1. The version-aware comparator rejects
missing/empty version fields; version tolerance never excuses changed mathematics.

Nine test groups reject numeric/category/type/structure corruption, nonfinite
numbers, duplicate JSON keys, invalid schema types, missing/modified input
identities, source drift, missing/duplicate arms, missing laws and changed total
shots. Runtime checks and unittest checks remain active under Python `-O`.
Intentional replay changes require reviewed regeneration of the normalized
result and checksums. Running without `--check` emits a candidate to stdout and
leaves retained files untouched unless the caller redirects output.

## Replay

Run from the repository root using the pinned requirements:

```sh
set -eu
PYTHON="${PYTHON:-$(command -v python3)}"
ruff check --no-cache docs/evidence/vacuum_endpoint_information
ruff format --check --no-cache docs/evidence/vacuum_endpoint_information
mypy --strict docs/evidence/vacuum_endpoint_information/probe.py \
  docs/evidence/vacuum_endpoint_information/check_probe.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error \
  docs/evidence/vacuum_endpoint_information/probe.py --check
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error \
  docs/evidence/vacuum_endpoint_information/probe.py --check
(cd docs/evidence/vacuum_endpoint_information
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error -m unittest check_probe
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error -m unittest check_probe
  sha256sum -c SHA256SUMS)
```

The [field opportunity note](../../notes/vacuum_field_run_opportunities.md)
places these finite ideal-readout precision statements behind separate source,
cutoff/synthesis, identifiable calibration and complete workload admission gates.
More settings or fewer settings alone cannot establish charged-time savings.
