# Tuna repeated-readout mechanism identifiability

The [retained joint-response replay](../evidence/tuna-projector-geometry/joint-response-analysis.md)
measures returned binary labels. The [provider artifact audit](../notes/quantum_inspire/destination-response-upstream-request.md)
finds no job-specific served acquisition map, discriminator or IQ in the inspected routes.
The following counterexample shows why more binary shots of the same circuit cannot, by
themselves, locate the cause. It is a mathematical construction, not a fitted physical
model or an assertion that either construction describes Tuna.

## Two exact explanations for one measured table

In the nominal-one baseline-before job 1620359, marginalizing the six-bit histogram to
its declared early and terminal q11 labels gives the following counts. Rows are early
labels and columns are terminal labels; every cell has denominator 4096.

| Early label | Terminal 0 | Terminal 1 | Row total |
|---|---:|---:|---:|
| 0 | 145 | 2631 | 2776 |
| 1 | 157 | 1163 | 1320 |

Two incompatible stage descriptions reproduce every cell exactly:

1. **Classical response model.** The physical qubit starts and remains in state 1. Two
   ideal nondisturbing reads each carry the hidden label 1. A joint classical response
   kernel maps that pair to `(0,0)`, `(0,1)`, `(1,0)`, `(1,1)` with probabilities
   `145/4096`, `2631/4096`, `157/4096`, `1163/4096`. The kernel may represent correlated
   discrimination, association or packing errors. It need not be a permutation.
2. **State-transition model.** The physical qubit starts in state 1. A stochastic
   pre-readout process sets it to 0 with probability `2776/4096`, otherwise 1. The first
   readout is perfect and leaves the state unchanged. Before the second perfect readout,
   the qubit transitions to 1 with probability `2631/2776` from state 0 and `1163/1320`
   from state 1. The four joint probabilities equal the same table by multiplication.

The first construction assigns the entire discrepancy to the classical response; the
second assigns it to physical state changes under perfect readout. Neither mechanism is
established, and the exact first-readout state and the relevant stochastic processes were
not independently observed. Both constructions obey the same observed early and terminal
label law, so any statistic computed only from those two labels has the same distribution
under them. The constructed transition probabilities are conditional model parameters,
not measured Tuna transition rates, calibration values or QND estimates.

For any binary table `P(e,f | c)` in a fixed context `c`, the same construction uses
`P(e | c)` and `P(f | e,c)` for a physical transition model, and `P(e,f | c)` as a
context-dependent classical response kernel. A zero-probability row may use any conditional
transition because it is never reached. Extending this argument across contexts requires
allowing the kernels or hidden apparatus memory to depend on context; the construction
therefore does not defeat a separately justified, restrictive common-mechanism assumption.
Conversely, a fitted common kernel or a model with independent label errors would be an
additional assumption requiring its own validation. The table is a post-acquisition empirical
law, rather than a claim that the true device law is stationary.

The same factorization applies to the complete six-bit table by replacing `e` and `f`
with three-bit vectors. A physical construction jointly samples the first three-bit
state from its observed marginal, reads it perfectly, then uses a joint transition
kernel for the terminal three-bit vector. A classical construction keeps the three
physical bits fixed and samples the same six returned labels jointly. Both reproduce
every cell, parity and cross-qubit correlation of that context. Joint transitions or
a shared apparatus memory are allowed; the construction does not establish that Tuna
has either. The other 14 terminal bits require their own joint extension, and the
six-bit equivalence alone makes no claim about those bits.

## What can falsify the explanations

| Observation or intervention | What it can distinguish | What remains required |
|---|---|---|
| Job-bound pre-packing labels plus acquisition-event-to-destination trace | Compare the same shot's pre-packing label with the returned declared bit; a mismatch falsifies that trace's claimed reconstruction rule. | Verify event, channel, shot identity and trace authenticity; agreement does not establish physical state or discriminator correctness. |
| Integrated IQ with the served discriminator rotation and threshold | Recompute labels from the same integrated samples; a mismatch falsifies the stated discriminator/reconstruction composition. | Verify sample and configuration identity; integrated IQ alone does not isolate integration, physical transitions or preparation error. |
| Served timing, integration kernels and acquisition windows | Check whether proposed pulse-overlap or later-pulse explanations are compatible with the recorded ordering. | Calibrated timing and a fixed first pre-packing label before the later pulse exclude a later-only influence on that pre-packing label; later processing may still alter the returned bit. |
| Destination renaming with identical served physical operation and independently assigned blocks | A reproducible decoded response change can reject a specified invariance null. | Establish served operation equivalence, actual job ordering, drift and uncertainty; the test does not locate the failing subsystem. |
| Independently qualified preparation and state-sensitive readout, including repeated-readout and control schedules | Compare predicted response and state-transition laws under explicit instrument assumptions. | Independent calibrations, informationally complete controls and validated timing are needed to attribute a physical transition. |

The [destination-invariance design](tuna-readout-destination-invariance.md) states the
local compiler comparison; matching submitted instructions does not establish matching
served analog operations. A provider association trace can be repacked under every
permutation without another acquisition, but that replay requires an actual trace and
cannot determine whether its own acquisition channel names are physically correct without
an independent anchor. The existing draft [private support request](../notes/quantum_inspire/destination-response-upstream-request.md)
asks for the necessary artifacts and remains unsent.

A successor case must prespecify the exact null, permitted model class and outcome that
would reject it; the possible outcomes include inconclusive. Even a successful destination
invariance test cannot rule out a defect common to every destination or establish a
Cayley-Dickson physical claim. New acquisition and circuit upload require approval of the
exact reviewed case and fresh admission.
