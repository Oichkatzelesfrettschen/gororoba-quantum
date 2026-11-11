# Quantum-state ontology: operational falsifiers and claim boundaries

## Scope

The wavefunction is a mathematical representation of a quantum state. The
existence of a Hilbert or configuration space does not establish a
nonphysical realm. Classical N-body mechanics already uses a 6N-dimensional
phase space. The ontology of the quantum state is interpretation-dependent.

## Reproducible finite witnesses

`gororoba_quantum/psi_foundations.py` enumerates all 16 deterministic
local CHSH assignments, obtaining S in {-2,2}. It separately evaluates the
singlet prediction |S|=2 sqrt(2). When experiment supports the quantum
correlations, this excludes the conjunction of three assumptions: outcomes
fixed by a shared variable and the local setting alone (local response
factorization), settings statistically independent of that variable
(measurement independence), and one definite outcome per run. It does not
exclude every physical ontology or imply superluminal signalling.

The module also computes the classical overlap omega=sum min(p,q) of two
finite ontic distributions and omega squared under independent product
preparation. This is a preparatory toy calculation, not an implementation
or proof of the Pusey-Barrett-Rudolph theorem. The theorem additionally
requires a measurement with quantum-forbidden outcomes and carefully stated
preparation-independence assumptions. No inference from overlap alone to
psi-ontology is permitted.

The Bell, Clauser-Horne-Shimony-Holt and Pusey-Barrett-Rudolph papers are
not registered in `docs/SOURCES.json`, and no statement here rests on a
reading of them: the sentences above summarize the standard hypotheses, and
the computations are self-contained.

Run: `python -m unittest discover -s tests -p 'test_psi_foundations.py'`.

## Hypothesis ledger

| Claim | Status | Discriminating test |
|---|---|---|
| Quantum state spaces need not be ordinary 3-space | Mathematical fact | Define N-particle Hilbert tensor product |
| Local deterministic assignments satisfy CHSH <= 2 | Proved by exhaustive enumeration | 16 assignments |
| Singlet predicts 2 sqrt(2) | Operational quantum prediction | Correlation calculation |
| Quantum state is ontic | Interpretation-dependent | State-model assumptions and no-go theorems |
| Hilbert-space dimensionality proves transcendence | Rejected inference | Classical phase-space counterexample |
| Psi accesses a nonphysical realm | Unsupported | Requires novel operational prediction |
| Cayley-Dickson A5 structure changes Born probabilities | Not established | Specify a normalized observable map and baseline |

## Research integration boundaries

Do not interpret algebraic nonassociativity, zero divisors, exceptional
structures, or high-dimensional representations as evidence of a new
physical interaction without a normalized state preparation, observable,
measurement protocol, error budget, and baseline quantum prediction.

Further work: implement a separately audited two-copy PBR measurement,
check the precise theorem hypotheses, and register individual claims in the
repository's research-state ledger only after reviewing its schema and gate
rules. The numerical identity tests below are not a Rocq proof or a new
hardware acquisition.

## Coherent apparatus and classical records

[measurement_models.py](../../../gororoba_quantum/measurement_models.py)
represents a trace-preserving instrument by its Kraus operators and
classical outcome labels. Multiple Kraus maps may share a label. Conditional
states remain subnormalized, including impossible outcomes. The coherent
isometry retains a quantum environment index; the classical record retains
only block-diagonal outcome states. These are different objects.

The deterministic tests establish the following finite-matrix identities:

- Tracing the coherent apparatus gives the same system density matrix as
  discarding the instrument outcome.
- A coherent Z record of |+> and its classical-record counterpart have the
  same reduced system but trace distance 1/2 globally. Uncomputing the
  coherent record restores |+>; the classical record gives return 1/2.
- For D_p(rho)=(1-p)rho+p diag(rho), the return probability is 1-p/2.
  A unitary dilation realizes the same reduced channel. This identity
  prevents interpreting fitted dephasing alone as objective collapse.
- GHZ records give mutual information one bit for a proper one-record
  fragment and two bits for the full complementary environment. Mutual
  information is not automatically accessible classical information.
- Arbitrary subsystem traces, tensor-factor reordering, mixed-radix
  systems and the |0> tensor Bell counterexample use actual tensor factors,
  not a maximum-index cut.

[The tests](../../../tests/gororoba_quantum/test_measurement_models.py)
reject malformed states, non-complete instruments, repeated subsystem
indices and unbounded outcome labels. They introduce no random seed.

## Covariance-aware operational identifiability

[measurement_identifiability.py](../../../gororoba_quantum/measurement_identifiability.py)
whitens the target and nuisance derivatives by the same positive-definite
covariance before an SVD projection. Nuisance columns are normalized before
rank determination so a change of parameter units does not change the
admitted span. Empty and rank-deficient nuisance families are valid.
A zero target has zero information and no defined angle; a singular
covariance requires an explicit contrast map instead of an implicit
pseudoinverse that could discard known information.

The local residual r defines I_eff=r.r. The linear Gaussian amplitude fit
profiles unrestricted nuisance coordinates and refuses an unidentifiable
target. Its standard error conditions on the supplied covariance and local
forward model. It is not a calibrated nonlinear model-selection test.
The reusable Rust calibrated-discrimination library in gororoba-open owns
bounded nuisance profiling; this module supplies the finite measurement
adapter and checks, not a replacement for that library.

The Ramsey adapter uses C(t)=A exp(-gamma t) exp(i(omega t+phase)), with
seconds, inverse seconds and radians stated in its API. The derivative for
an additional exponential dephasing rate is exactly the ordinary gamma
column. The tests therefore require zero distinguishable information and
refusal to estimate the two rates separately. An independently derived
collapse model needs a different observable signature or independent
constraints on the ordinary rate before a physical test becomes possible.

[The identifiability tests](../../../tests/gororoba_quantum/test_measurement_identifiability.py)
cover correlated covariance against a Schur complement, exact GLS recovery,
unit changes, finite differences, simplex contrasts, rank deficiency,
zero targets, nonpositive covariance and overflow. All inputs are fixed
analytic fixtures; no acquisition is reclassified.

## Remaining dependencies

Archive-wide residual passes already have their own owner in PR #819.
This implementation neither duplicates their scans nor treats their leads
as confirmed mechanisms. Provider record readers, pinned producer bytes,
raw outcomes and the canonical claim registry remain unchanged here.

Physical discrimination still needs a declared alternative model, validated
calibration and covariance, qualified chronology and independent controls.
A reversal circuit, a local-friendliness analogue or a redundant-record
experiment requires its own written hardware case. A collapse parameter,
extra spatial coordinate or cosmological region is not inferred from these
software tests. General nonlinear nuisance profiling, physical sky-map
likelihoods and provider analog-record retrieval remain separate tasks.
