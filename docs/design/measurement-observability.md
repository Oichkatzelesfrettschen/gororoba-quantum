# Measurement observability and uncertainty contracts

This subsystem turns the reusable measurement arithmetic from the algebra/device synthesis into library functions,
strict offline JSON analysis and bounded tests. Its unit is a declared observation law with provenance. It does not
acquire provider data or promote a count anomaly into an exotic-physics claim.

## Scope reconciliation

The implementation audit uses quantum base `d5ff68e283ca26b12dc07bf95a48cc515a3c6145` and
gororoba-open base `b73ca1050ace1c5c6f8a25564879f70bacdbf80b`. These are source snapshots, not assertions about future main.

| Discussion item | Existing implementation or evidence | Remaining software boundary addressed here |
|---|---|---|
| Independent, shared and conditional outcome statistics | `variance.py`, `conditional_ramsey.py`, `provider_counters.py`, and specialized BDSC/Ascella scripts | A generic vector-score estimate preserves all outcomes and complete covariance; acceptance analysis binds genuine attempted populations. |
| Prediction uncertainty | Ascella physical-model and compilation-reading scripts already propagate a fit covariance in specific independent-holdout analyses | A reusable joint-covariance API includes shared-data cross terms, rejects an impossible joint covariance, and checks residual support. |
| Identifiability and nuisance directions | gororoba-open `stats_core::calibrated_discrimination` already implements whitened nuisance projection, Fisher information and bounded profiling | No duplicate inverse/Fisher engine is introduced. These scores provide its observation covariance inputs. |
| Single-projector and sequential geometry | `bdsc.py`, `qi_projector_geometry.py`, exact kernel contracts and gororoba-open Grassmannian primitives | Repeated normal-herald moments and a complete Hermitian coefficient bank become reusable APIs. |
| Full atlas-span and Lie-envelope certificates | The synthesis archive retains standalone exact atlas and Lie-envelope checks | The new basis construction does not claim to re-certify the acquired bank's span or the archived 28/49 census. |
| QET, passivity and energy accounting | `qet_ladder.py`, QET control scripts, and gororoba-open quantum-core passivity/energy modules already exist | Acquisition, energy calibration and a physically identified model remain separate. |
| Temporal residual structure | The independent hardware-residuals work in quantum PR 819 owns the retrospective IBM/Tuna/Quandela passes | Acquisition-order indices do not become physical timestamps. That work is not duplicated here. |
| Proper time, Casimir forces, wormholes and extracted work | Existing synthesis and vacuum-model notes state the physical and instrument requirements | A finite algebra encoding supplies no spacetime metric, force calibration or energy ledger by itself. Software cannot reconstruct absent observables from bitstrings. |

The corresponding native Rust score primitive lives in gororoba-open
`crates/stats_core/src/measurement_scores.rs`. Both languages share the exact-count boundary and the named finite-sample
estimators. Provider counter interpretation remains owned by this repository.

## Outcome scores and covariance

For mutually exclusive outcomes with counts `n_j`, total `N`, probabilities `p_j = n_j/N`, and score columns `s_j`,

\[
\widehat\mu=\sum_j p_j s_j,\qquad
M=\sum_j p_j(s_j-\widehat\mu)(s_j-\widehat\mu)^T.
\]

`measurement_statistics.multinomial_scores` returns `M/N` for `estimator="plugin"`, or `M/(N-1)` for
`estimator="unbiased"`. The latter requires `N >= 2`. The sampling model is independent trials with a fixed attempt
count. An accepted-only histogram describes a conditional population unless rejected outcomes also appear.
Every zero-score outcome remains in `N`. The function neither infers sampling independence nor recovers absent trials.

Counts `[2,3,5]` and score rows `[[1,0,-1],[0,1,1]]` give

\[
\widehat\mu=(-0.3,0.8)^T,\qquad
\widehat V=\begin{pmatrix}0.061&-0.026\\-0.026&0.016\end{pmatrix}.
\]

The off-diagonal term follows independently from `E[XY]=-0.5` and `E[X]E[Y]=-0.24`, divided by ten trials.
For four equiprobable outcomes scored `(1,0,0,-1)`, the mean variance is `1/(2N)`. Dropping the two zero-score outcomes
changes both the population and the uncertainty.

Totals above `2**53` are rejected rather than rounded. Scores must be finite even in zero-count categories. Offset
centering protects small variations beside a large common offset. Weighted square roots apply the sample-size
reduction before forming a covariance Gram matrix. Unrepresentable nonzero variance raises rather than becoming a
claim of certainty. A one-trial or boundary plug-in covariance can still equal zero; it is not a confidence bound.

## Acceptance-aware six-state linearity

For orthogonal states `f,g`, the real and imaginary superposition pairs satisfy

\[
\rho_++\rho_-=\rho_f+\rho_g=\rho_{+i}+\rho_{-i}.
\]

A fixed linear effect `E` therefore gives zero contrasts of unconditional event rates `u_s=Tr(E rho_s)`:

\[
\Delta=Mu,\quad
M=\begin{pmatrix}-1&-1&1&1&0&0\\-1&-1&0&0&1&1\end{pmatrix},\quad
V_\Delta=MV_uM^T.
\]

`acceptance_statistics.AcceptanceCounts` retains selected count `k`, accepted count `a`, and the existing
`provider_counters.Counter`. Its source, scope, status, population and stopping metadata remain in the output.
Only observed source-trigger or circuit-execution populations qualify as attempted trials `N`. Requested caps,
detection events, filtered samples, billing quantities, modeled exposure and unavailable counters do not.

The conditional rate is `k/a`; the unconditional rate is `k/N`. At `a=0`, the conditional rate is unavailable while
the unconditional rate remains defined when genuine positive attempts are present. A descriptive observed `k/N`
survives a stopping rule, but ordinary fixed-N covariance does not follow from independent trials alone.

`analyze_six_state` requires both `independent_trials=True` and `fixed_attempts=True`, with no recorded stopping,
before producing the binomial plug-in covariance. Alternatively, the caller supplies the joint covariance of the
six unconditional rate estimates in canonical `f,g,+,-,+i,-i` order. Absent statistical qualification produces
`None` and a reason. Shared `f,g` controls retain their covariance across the two contrasts.

The bounded counterexample uses ten attempts per state. Here `k` is the selected count and `a` the accepted count:
`(k,a)=(4,4)` for `f`, `(0,6)` for `g`, and `(2,5)` for each of `+`, `-`, `+i` and `-i`. Both conditional contrasts are `-0.2`; both unconditional contrasts are zero. The contrast covariance
is `[[0.056,0.024],[0.024,0.056]]`. A conditional residual alone therefore fails as a fixed-effect linearity test.

## Predictive residuals and support

Let `r=y-g(theta_hat)`, `J=dg/dtheta`, `V_y=Cov(y)`, `C_theta=Cov(theta_hat)` and `C_ytheta=Cov(y,theta_hat)`. Then

\[
V_r=V_y+JC_\theta J^T-C_{y\theta}J^T-JC_{y\theta}^T
=\begin{pmatrix}I&-J\end{pmatrix}
\begin{pmatrix}V_y&C_{y\theta}\\C_{y\theta}^T&C_\theta\end{pmatrix}
\begin{pmatrix}I\\-J^T\end{pmatrix}.
\]

This is exact for an affine predictor and a first-order delta approximation otherwise.
`measurement_statistics.predictive_residual` requires either `dependence="independent"` or
`dependence="supplied_cross_covariance"` with the cross block. Missing parameter covariance never becomes zero. The
full joint covariance receives a positive-semidefinite admission check; positivity of the final residual covariance
alone does not establish a possible joint observation law. The residual covariance itself is the congruence of that
joint covariance and is admitted to an entrywise tolerance of `64 * eps * n * |S||C||S|^T` (hypothesis: this dominates
the roundoff of the two products; no error analysis is retained), where `S` is `(I,-J)` scaled by the joint standard
deviations, `C` the joint correlation and `n` the number of coordinates with positive variance, so a small residual
covariance that is a difference of large terms keeps its sign and symmetry tests at the scale of the cancellation.
A coordinate whose variance lies within the tolerance is deterministic and other entries keep their values: a fit that
reuses an observation exactly yields the zero residual covariance, and `covariance_score` then decides support from
the residual alone.

Covariance admission standardizes by positive diagonal scales before checking symmetry and eigenvalues. Large
units cannot hide an invalid small-unit block. A zero diagonal requires an exactly zero row and column. The
documented numerical rank threshold uses `64 * machine_epsilon * dimension` times the correlation spectral scale.

`covariance_score` checks that the residual lies in covariance support before evaluating its quadratic form.
A residual outside covariance support beyond the declared numerical tolerance returns `supported=False` and
`value=None`. A nonzero residual on a coordinate with exactly zero variance always fails support admission.
The relative unsupported norm is computed after standardizing coordinates and normalizing their largest
absolute magnitude. That diagnostic is not a significance or sigma count. The result contains no chi-squared
reference distribution. Selection on the same observations, unknown training covariance and group leakage need
independent design qualification before inferential use.

## Repeated normal-herald moments

`kernel_observability.certify_equal_weight_pair` constructs `L=L_ei +/- L_ej` through `cd_core` exact coefficients.
It checks normality, `G=L^T L`, `G(G-2I)(G-4I)=0`, `Tr(G)=2D`, and the integral multiplicities at eigenvalues
`0,2,4`. With nullity `z`, the multiplicities are `z,D-2z,z`; the normalized Kraus operator is `K=L/2`.

For a maximally mixed input and positive depth `m`, normality gives

\[
p_m=\frac1D\operatorname{Tr}((K^\dagger K)^m)
=\frac zD+\left(1-\frac{2z}D\right)2^{-m}.
\]

Depth zero has `p_0=1` and is handled separately. Known uniform per-stage retention `eta` gives `q_m=eta^m p_m` and

\[
\eta^2q_m-3\eta q_{m+1}+2q_{m+2}=0,\quad m\ge1.
\]

Since `p_1=1/2`, the uniform-retention ratio obeys

\[
z=\frac D2\left(\frac{q_2}{q_1^2}-1\right).
\]

The nondecaying ideal plateau comes from the Gram eigenvalue-four sector, whose normalized success eigenvalue is
one. Its multiplicity equals the kernel nullity because the certified trace identity forces those two multiplicities
to agree. The kernel itself contributes zero survival at positive depth.

`uniform_retention_nullity` retains nonintegral or out-of-range results as model diagnostics rather than rounding
them into a rank. State-dependent retention, a different input state and nonnormal evolution invalidate this
particular model. A fitted retention requires its parameter and cross-covariance uncertainty.

For nested successes `N1 >= N2 >= ... >= Nm` from the same `N` independent attempts, the exclusive histogram is
`[N-N1,N1-N2,...,Nm]`. Triangular indicator scores recover cumulative probabilities and

\[
\operatorname{Cov}(\widehat p_i,\widehat p_j)
=\frac{p_{\max(i,j)}-p_ip_j}{N}
\]

under the plug-in convention. `nested_herald_statistics` reuses the common score engine and propagates the full
matrix through the recurrence contrasts. Independently acquired depth banks do not satisfy this same-attempt
contract. The API rejects missing, requested, detected-event and censored attempt denominators.

## Completing the Hermitian observable space

On dimension `2m`, write `J=[[0,I],[-I,0]]`. The real symmetric matrices commuting with `J` have form
`[[A,B],[-B,A]]`, where `A` is symmetric and `B` skew-symmetric. Their dimension is `m**2`.
The real symmetric anticommutant has form `[[A,B],[B,-A]]`, where both blocks are symmetric, and dimension
`m*(m+1)`. Pure imaginary skew-symmetric Hermitian matrices contribute `m*(2m-1)` independent directions.

These three mutually Hilbert-Schmidt orthogonal spaces sum to `(2m)**2`. At `m=7`, the dimensions are
`49+56+91=196`. `tomography_completion` constructs the integer coefficient bank and its actual squared norms.
`reconstruct_hermitian` performs linear inversion with those norms. It does not silently force a noisy estimate
to be positive or trace one. The binary effects `(I +/- T)/2` are mathematical effects; acquisition still requires
a physical instrument that realizes them.

## Offline interface and reproducible checks

The [bounded input](../../tests/fixtures/measurement-observability.json) is labeled as analytic test data. It exercises
all five analysis kinds. Each item has `id`, `kind`, `source` and `input`; unknown keys, duplicate IDs, duplicate JSON
keys and nonfinite JSON constants reject. Every counter carries the existing provider-counter fields. The result
binds input bytes and producer files by SHA-256 and records Python/NumPy versions. It preserves unavailable values
as JSON null, uses order-preserving batch dispatch and cannot overwrite its input path.
Tomography checks its `32*m**4` real/imaginary integer entries before allocation. The default
`coefficient_entry_budget` is one million entries; a larger explicit budget requires accounting for at least eight
bytes per entry, intermediate arrays and substantially larger JSON output. The output retains the chosen budget.
`kernel_observability.tomography_completion` applies the same budget through its `entry_budget` argument before
allocating, so a library caller cannot request an unbounded bank.
The on-demand gate `core-measurement-observability` of `ci/gates.json` replays the retained
[analytic result](../evidence/measurement-observability/analytic-result.json) byte for byte on a CPU that takes the
same native numeric path as the record's producer; the record names Python and NumPy versions but not that path.

```sh
export PYTHON=/path/to/pinned/python
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/measurement_observability.py tests/fixtures/measurement-observability.json \
  --output /tmp/measurement-observability-result.json
"$PYTHON" -B -m pytest -q \
  tests/gororoba_quantum/test_measurement_statistics.py \
  tests/gororoba_quantum/test_acceptance_statistics.py \
  tests/gororoba_quantum/test_kernel_observability.py \
  tests/scripts/test_measurement_observability.py
```

The library tests use exact identities, rational coefficients, direct shot-indicator matrices and independent
covariance oracles. Boundary tests cover singular support, mismatched provenance, subnormal variances, large
offsets, nonfinite arithmetic, stopping rules and impossible joint covariance. Existing specialized retained-data
producers retain their source-bound historical bytes; a later analysis selects the new API deliberately and names
its changed estimand and statistical assumptions.

The [validation record](../evidence/measurement-observability/validation.json) binds the checked source revision,
commands, versions and scope. The [analytic result](../evidence/measurement-observability/analytic-result.json)
retains the five-kind fixture output. The [completion record](../state/plans/measurement-observability-contracts.json)
closes the bounded software obligation and leaves physical acquisition, hosted review and merge separate.
