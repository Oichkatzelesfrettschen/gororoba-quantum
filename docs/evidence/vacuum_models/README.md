# Finite pair-field and device-noise model checks

The [CPU replay](probe.py) checks explicit finite matrices and conditional
symbolic models before a prospective field-simulation or noise-sensing case
is designed. The [retained result](result.json) separates finite reference
calculations from hardware measurements, physical coupling, and convergence
of a regulated model. The replay uses NumPy, SciPy and SymPy; the replay
invokes zero QPU services or jobs.

Run from the repository root with the pinned dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/vacuum_models/probe.py --check
GOROROBA_WORKERS=2 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/vacuum_models/probe.py --check
(cd docs/evidence/vacuum_models && sha256sum -c SHA256SUMS)
```

## Checked models

- **Pair-field sector.** At cutoffs 4 and 8, the embedding
  `|n> -> |n,n>` intertwines the full two-mode generator and the reduced
  equal-occupation generator. Matrix checks cover phases `0`, `pi` and
  `0.37`, with evolution strength `0.4`. The maximum measured intertwining
  residual is `9.94e-16`; the evolution residual is `6.67e-16`.
  The number-difference commutator checks the invariant sector. Those finite
  numerical checks do not establish a continuum-limit theorem or constrain
  hardware leakage out of the encoded subspace.
- **Coherence and cutoff.** Strengths `0.2`, `0.4` and `0.6` check equal
  occupations under phase reversal, odd pair coherence, general phase
  dependence, and zero pair coherence in an occupation-matched diagonal
  mixture. Four-level relative real-coherence errors against the infinite
  two-mode squeezed reference are `0.013669%`, `0.715296%` and `5.865244%`.
  The discarded infinite-reference probability and finite top-level
  occupation are different quantities. The truncated commutator
  `[a,a†]=I-cutoff*|top><top|` supplies a further observable-dependent bias
  diagnostic. A small discarded probability alone cannot certify accuracy
  of every observable.
- **Pauli observables and synthesis.** With left-to-right tensor labels
  `q1q0`, the four-level generator is
  `H/(hbar*g)=2 IY-XY+YX-ZY`, the real pair observable is
  `Re(ab)=IX+(XX+YY-ZX)/2`, and the pair occupation is
  `n=1.5 II-ZI-0.5 IZ`. Settings `ZZ, ZX, XX, YY` cover populations,
  top-level occupation and real pair coherence. Those settings leave some
  imaginary coherence unmeasured; full two-qubit tomography needs nine
  product settings. For the retained first-order term order at strength
  `0.4`, one step has operator-norm error `0.4445` and eight steps `0.05385`.
  Fresh routed circuits and complete workload pricing must qualify any
  conventional/fractional implementation comparison.
- **Thermal and shot examples.** The frequency/temperature examples compute
  the Bose occupation of an oscillator. A two-level excited-state population
  uses a different denominator. The zero-event binomial upper bound assumes
  independent Bernoulli trials; drift and correlated shots require a revised
  model.
- **Rate/SPAM ambiguity.** Two physical preparation/readout/population
  parameter sets produce indistinguishable observed paired decay curves at
  the six recorded delay values, with maximum residual `1.11e-16`.
  Analytically, the affine replacement `p'=offset+scale*p` can be offset by
  changing the readout intercept and slope while preserving every `q(t)`.
  The unchanged rate sum alone fails to identify the physical asymptotic
  population. Independent SPAM constraints must precede thermometry or
  reservoir attribution; additional shots leave the ambiguity intact.
- **Programmed bath.** For an exchange interaction at angle `0.3`, diagonal
  bath population `0.2` produces
  `p_next=cos(theta)^2*p_system+sin(theta)^2*p_bath` for three tested system
  populations. A coherent state with the same bath populations has a nonzero
  off-diagonal entry and induces system coherence. A coherent `RY` preparation
  therefore differs from the thermal mixture. These fixtures check selected
  channel actions; they leave arbitrary-input channel qualification and
  fresh-versus-reset bath engineering as separate gates.
- **Conditional force models.** Symbolic differentiation checks the ideal
  parallel-plate energy per area and a regulated oscillator's curvature at
  its crossing. The latter is `a^2*hbar*omega_star/(2*abs(epsilon))` for
  nonzero regulator. The length-chain-rule field records the required map;
  the replay supplies neither a physical `lambda(d)` nor a calibrated
  material or boundary response. The calculations do not establish a
  measured Casimir force or emitted radiation.

The [quantum-noise convention](../../notes/0810.4729.md),
[paired-rate interpretation](../../notes/cond-mat-0210247.md), and
[residual-population measurement](../../notes/1412.2772.md) notes supply
source assumptions for the sensing side. Encoded-field source notes and
prospective campaign admission supply separate model and hardware gates.

## Provenance and replay admission

Two user-supplied research proposals motivated the checked equations. The
retained identities are SHA-256
`5359c18f4f6c1e4381dc43a657033a872ccf37309f1a55addc51f03fc7f261ee`
(23807 bytes) and
`c090fac04fa1c40bbaa03509b7bd901e65c42d9c13d67996bab036675710924e`
(27194 bytes). The input records identify provenance; the executable
equations reside explicitly in `probe.py`. Replay neither retrieves nor
parses proposal prose, and the hashes do not prove that the prose implies
every encoded equation.

The separately reviewed original probe had SHA-256
`22c1c130a42440074b66aa93f990e0920ff91e08c7b04e9bb63df718d5a834a5`;
its result had SHA-256
`6147433302a506c33f5a9c9367b7f67b6d22d2398f82577a179bb503cdf7207b`.
Production normalization added typed functions, fixed provenance identities,
source binding, the exact six-delay list, shared process-pool execution and
replay admission. All original mathematical result fields matched exactly
after normalization. The retained environment was Python 3.14.7,
NumPy 2.5.4, SciPy 1.18.1 and SymPy 1.14.0.

`--check` recomputes every result and checks source hashes before and after
execution. Category values, field names, list lengths, ordering and numeric
types match exactly. Finite floating values use absolute tolerance `1e-12`
and relative tolerance `1e-10`. Version strings are reported separately so
numerical replay can identify a compatible environment without claiming
identical dependencies. Comparator rejection fixtures cover changed numeric
results, categories, types, structure, NaN and infinity, and run under `-O`.
`SHA256SUMS` binds the README, replay and result. Intentional source changes
require reviewed regeneration; running without `--check` emits a candidate
record to stdout and leaves the retained result untouched.
