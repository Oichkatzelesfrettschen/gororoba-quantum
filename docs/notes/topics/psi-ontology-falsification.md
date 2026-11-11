# Quantum-state ontology: operational falsifiers and claim boundaries

## Scope

The wavefunction is a mathematical representation of a quantum state. The
existence of a Hilbert or configuration space does **not** establish a
nonphysical realm. Classical N-body mechanics already uses a 6N-dimensional
phase space. The ontology of the quantum state is interpretation-dependent.

## Reproducible finite witnesses

`gororoba_quantum/psi_foundations.py` enumerates all 16 deterministic
local CHSH assignments, obtaining S in {-2,2}. It separately evaluates the
singlet prediction |S|=2 sqrt(2). This excludes the conjunction of local
response factorization, measurement independence, and the other usual Bell
assumptions when experiment supports the quantum correlations; it does not
exclude every physical ontology or imply superluminal signalling.

The module also computes the classical overlap omega=sum min(p,q) of two
finite ontic distributions and omega squared under independent product
preparation. This is a **preparatory toy calculation**, not an implementation
or proof of the Pusey-Barrett-Rudolph theorem. The theorem additionally
requires a measurement with quantum-forbidden outcomes and carefully stated
preparation-independence assumptions. No inference from overlap alone to
psi-ontology is permitted.

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
check the precise theorem hypotheses, add density-operator/Born-rule
cross-checks, and register individual claims in the repository's
research-state ledger only after reviewing its schema and gate rules.
