# The 84 box-kite contrasts are not a compilation artifact

**Question.** Could the transpiler have optimized the bright arm (phase 0) and
the dark arm (phase 4) of a box-kite contrast differently, so that the 84
registered contrasts measure two different circuits?

**Answer.** No. In both ripple runs, all 84 bright and dark pairs executed
the same gates on the same qubits. The executed circuits differ in exactly
one parameter, an RZ angle.

## Evidence

`scripts/scaffolding_exposure.py --check` (gate core-276) reads the
`isa.qpy` and `record.json` of each run into the `atlas_pair_structure`
section of
[exposure.json](../walk-control-scaffolding/exposure.json):

| Run | Pairs | Identical executed gate and qubit sequence | Parameters that differ |
| --- | ---: | ---: | --- |
| 2026-10-13T025444.603480Z (ibm_fez) | 84 | 84 | one `rz` per pair |
| 2026-10-15T031229.371738Z (ibm_kingston) | 84 | 84 | one `rz` per pair |

The pipeline explains this. `live_run.select_candidates` compiles each shared
circuit object once, with its parameters unbound, and `live_run._bind`
assigns every member's binding to that compiled circuit without
re-optimization. Both arms of a pair bind the one `atlas_phase` parameter of
one template: 0 for the bright arm and pi for the dark arm.

## What can still differ between the arms

- **The bound angle enters only a virtual RZ.** On Heron an RZ is a frame
  update with no pulse, so it carries no angle-dependent pulse error. The
  frame change does rotate the axis of every later SX on that qubit. An
  over-rotation of those SX pulses therefore acts about different axes in
  the two arms, a second-order effect that this check does not bound.
- **Readout.** The two arms put most of their weight on different outcomes.
  A state-dependent assignment error scales the contrast by
  `1 - e01 - e10`, but it cannot make a zero contrast nonzero. The contrasts
  are 0.28 to 0.73.
- **Interpretation.** A parameterized circuit shows the dependence on its
  parameter that its construction gives it. The contrasts show that the
  compiled circuits implement the predicted interference on hardware. They
  remain implementation evidence for the box-kite construction, not a
  hardware proof of an algebraic statement (`hw-fez-ripple`).

## Notebook

`falsify-84-84.ipynb` works through angle-dependent coherent errors and
readout asymmetry on a two-parameter model `O(theta) = a + b cos(theta)`.
Its readout argument stands. Its coherent-error argument does not: it says
unital errors cannot create population contrast, which is not true in
general, since a unitary error changes populations. The argument that
applies is the virtual-RZ one above. The notebook's executed outputs come
from its own environment and are not replayed in CI.
