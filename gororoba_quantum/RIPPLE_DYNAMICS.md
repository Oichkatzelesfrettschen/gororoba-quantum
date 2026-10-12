# Cayley-Dickson interference and recurrence

The ripple protocol gives one algebraic source three visible consequences:
probability redistributes under repeated associator phases, a state returns
after a finite exact cycle, and signed zero-divisor edges become dark or bright
LCU fringes. The common source is the Cayley-Dickson multiplication sign table.
The connecting mechanism is interference; the geometric drawing supplies a
readable coordinate system.

`ripple_dynamics.py` certifies the bounded ideal predictions with integer
arithmetic and checks their circuits locally with core Qiskit. The
[retained evidence and explorer](../results/ripple/README.md) reproduce those
predictions. Hardware observations remain a future experiment.

## Four-qubit associator dynamics

For dimension-32 pairs A = (25, 31) and B = (9, 22), the associator phase has
the form `diag(D, -D)`: an independent Z on bit 4 times a four-qubit diagonal
core D. The protocol removes that independent factor and initializes the
core in `|0000>`. Both cores contain two Z, three CZ and two CCZ ANF terms.
Equal logical term counts permit different native routing costs.

Define `U = M D`, with `M = Rx(pi/2)` on each of the four qubits. A frame at
depth t represents the distribution of `U^t |0000>`. The circuit builder
retains the first D so its full operator equals `U^t`; only the specified
initial state permits omitting that first D in a future state-preparation
optimization. With w[x] the diagonal sign of D,

```
U[y,x] = (-i)^popcount(y XOR x) * w[x] / 4.
```

Gaussian-integer matrix numerators over `4^t` establish exact probabilities,
column norms and recurrences. The verifier checks the one-step Gram matrix
and every positive exponent through the first scalar operator return. The
independent Qiskit construction composes signed left-multiplication gates;
operator and statevector comparisons check the mapping to the circuit.

| Depth | Return A | Return B | Collision A | Collision B |
| --- | --- | --- | --- | --- |
| 0 | 1 | 1 | 1 | 1 |
| 1 | 1/16 | 1/16 | 1/16 | 1/16 |
| 2 | 1/16 | 1/16 | 11/32 | 5/32 |
| 3 | 1/4 | 0 | 5/32 | 5/32 |
| 4 | 9/16 | 1/4 | 11/32 | 5/32 |

Return means `P(0000)`; collision means `sum_x P(x)^2`. At depth 2 the
distribution equals the existing associator Walsh spectrum after XORing the
output with 15. The early prefixes therefore extend a known observable into
a repeatable dynamical protocol. The primary proposed contrast at depth 4
is `9/16 - 1/4 = 5/16`.

| Pair | First state return | First projective operator return | Exact operator identity |
| --- | --- | --- | --- |
| A | 24 | 24 | `U_A^24 = I` |
| B | 30 | 120 | `U_B^120 = I` |

A state return concerns the chosen initial ray. A projective operator return
requires a common scalar on every basis state; here the first scalar is +1.
The smaller state-return period of B illustrates why one prepared state
cannot certify an entire operator. The calculations establish these finite
identities for the specified protocol. They establish neither literature
novelty nor computational advantage. Hardware depths 0 through 4 cannot
verify the long periods.

## Signed box-kite fringes

For each strut constant S from 1 through 7, take assessors `(a,A)` with
`a in {1,...,7} except S` and `A = a XOR (8 XOR S)`. Opposite assessors
satisfy `a XOR b = S`; the other pairs form the twelve edges of an octahedron.
For an edge joining `(a,A)` and `(b,B)`, set

```
r = -cd_sign(16,a,b) * cd_sign(16,A,B)
(e_a + e_A) * (e_b + r*e_B) = 0.
```

The seven graphs contain 42 unsigned assessor vertices and 84 undirected
edges. Including both compatible sign choices and both operand orders
recovers all 336 ordered signed zero-product rows in the repository corpus.
Direct multiplication checks every row. The counts reproduce existing
mathematics; see the [prior-work ledger](../literature/notes/prior_work_synthesis.md).

Every one of the 56 triangular faces has edge-sign product -1. A common
assignment of real vertex signs would give +1 around a triangle, so a face
cannot have all three edges dark under one shared sign assignment. Each edge
is a separate experiment with its own input preparation.

The existing `design_d_phase_sweep` yields
`P(ancilla=0) = (1 - r*cos(phi))/2`. The verifier checks eight phases on each
of 84 edges: 672 circuits. Cancellation occurs in the selected LCU branch;
the full quantum state retains norm one. Intermediate complex phases leave
the real zero-product variety. A smooth fringe depicts a phase sweep, while
the appropriate real endpoint represents the zero-product witness.

## One-job implementation and timing

The [packed algebra protocol](PACKED_ALGEBRA.md) supersedes the initial
116-row illustration. The implemented ripple family uses 55 logical qubits
and 146 sparse execution rows: the full box-kite phase atlas, matched walk
crossovers, the original Design C spectrum ladder, isolated representatives,
and readout controls on every atlas template's actual physical output wire.
The [portable proposal](../results/ripple/single-job-proposal.json) records
the design; only a fresh runner record can qualify hardware execution.

A repetition delay of 250 microseconds would alone cost 149.504 seconds for
146 rows at 4,096 shots. Fresh routing, gate duration, readout, initialization,
statistical admission, and service scheduling determine the actual proposal.
The earlier approximately 35-second illustration applied to fewer controls
and fewer shots and does not price the implemented family.

The primary outcome is the depth-four return contrast after exchanging
physical tiles under identical atlas neighbor activity. The contract retains
phase-probability precision, directional bright/dark effects, ladder spectra,
representative packing comparisons, and template-specific readout controls.
Fringe fits and collision statistics remain descriptive unless separately
qualified. A fully dephased model stays uniform after each mixer; that
reference is modeled unless an actual dephasing protocol is included.

The runner retains joint shot ordering and per-component registers. Follow the
[parallel-experiment evidence requirements](../literature/notes/quantum_experiment_parallelism.md)
and [design sources](../literature/notes/quantum_experiment_design_sources.md).
A fresh calibration, submit-free dry run, digest-bound written case and
explicit owner approval under [AGENTS.md](../AGENTS.md) precede submission.
Native server mock timing is separate evidence and supplies randomized
outcomes that cannot enter measured visualizations.

## Visual and philosophical interpretation

A ripple makes a disturbance legible through relationships. Here a fixed
phase rule repeatedly changes where probability concentrates, while a dark
edge makes algebraic cancellation visible through an outcome frequency.
Recurrence supplies a second rhythm: a distribution can return before the
whole transformation returns. The artwork can juxtapose these rhythms with
the imperfect hardware residuals instead of hiding those residuals.

The explorer labels exact probabilities, schematic Hamming-shell geometry
and signed octahedra. The proposal separately records the single-job plan.
A future measured rendering should
map node area to measured probabilities, show intervals on fringes, and
retain hardware-minus-model residuals. Computational-basis counts provide
probabilities; complex phase needs additional observables. Animated frames
represent separately prepared circuit prefixes. Interpolation is artistic
playback, not continuous observation of one state. Physical timing art should
use retained scheduler events and physical qubit labels.

The physical effect is the preparation and interference of quantum states
inside the processor. "Make reality ripple" names the artistic ambition of
making that bounded physical process visible; the experiment does not test
a disturbance propagating into the surrounding world.
