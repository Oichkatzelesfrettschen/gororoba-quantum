# Walk controls execute the full CZ scaffold of the shared walk template

The ripple walk members, the `readout0` controls included, compile from one
symbolic template whose angles stay unbound for shared routing.
`ripple_experiments._native_walk_circuit` lowers every `p` and `mcphase`
into Gray-code parity cycles of SX and CZ whatever the bound angle, and only
virtual RZ angles carry the parameters. A member bound to zero angles is
logically the identity before measurement, yet it executes the whole
scaffold. The walk discrepancy against calibrated replay is therefore a
physical-noise measurement on a deep identity-equivalent circuit, not a
disagreement about walk dynamics.

`scripts/scaffolding_exposure.py --check` (gate core-276) re-derives the
counts and tables below from the retained `record.json`, `isa.qpy` and
`collect.json` into [exposure.json](exposure.json).

## Compiled load per member kind

Every walk member executes 252 CZ on its own four qubits, in both ripple
runs: at every depth and for the readout controls. A noiseless statevector
of the executed lane-0 and lane-1 readout components gives P(0000) = 1 to
4e-15.

The other families execute far less:

| Family | CZ per member |
| --- | --- |
| atlas edges | median 42 (33 to 53) |
| atlas readouts | 0 |
| rank sectors | 21 to 38 |
| coherence window | 23 |
| correction | 70 |
| corner baseline | 0 |
| zero-divisor fringe | 42 per replica |

A fringe component reads 336 CZ (mirror 320) because eight replicas of 42
(mirror 40) run in parallel in it. No CZ crosses a component boundary in any
retained run.

## Walk readout controls

| Run | Backend | Qubits | CZ | Hardware P(0000) | Replay P(0000) | Retention per CZ, hardware / replay |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 2026-10-13T025444.603480Z | ibm_fez | 1, 2, 3, 4 | 252 | 0.064 | 0.540 | 0.9892 / 0.9976 |
| 2026-10-13T025444.603480Z | ibm_fez | 13, 14, 15, 19 | 252 | 0.131 | 0.587 | 0.9920 / 0.9979 |
| 2026-10-15T031229.371738Z | ibm_kingston | 80, 81, 82, 83 | 252 | 0.336 | 0.544 | 0.9957 / 0.9976 |
| 2026-10-15T031229.371738Z | ibm_kingston | 59, 73, 74, 75 | 252 | 0.251 | 0.666 | 0.9945 / 0.9984 |

Retention per CZ is `P(0000)^(1/252)`. It is a descriptive, load-normalized
figure that assumes exponential loss, not a gate error. Read that way, the
per-CZ loss `1 - r` on hardware is 1.8 and 3.4 times the calibrated model's on
the Kingston lanes and 4.4 and 3.8 times on the Fez lanes. The worst lane, Fez 1-4, overlaps Fez's weak
rank-sector tile (2, 3, 4, 16), so device and tile both enter the gap.

## Hypotheses and their status

1. **The scaffold sets the floor** (confirmed). The executed readout
   circuit is the identity, so its loss is physical noise. The depth members
   share the same CZ and SX scaffold, and their bound angles change the
   implemented walk and its ideal law. The hardware's flat P(0000) across
   depths is therefore a depth dependence suppressed under a constant
   252-CZ load, not evidence about walk dynamics either way.
2. **An effective CZ error eight times the calibration** (not supported as
   stated). The figure came from a depolarizing fit to Fez lane 0, a model
   that hypothesis 3 rejects. The load-normalized loss also varies by lane
   and by device.
3. **Structured, non-depolarizing loss** (supported; mechanism open). The
   lane-0 outcome distribution concentrates on a few outcomes, and a uniform
   law is rejected (chi-square p ~ 1e-259). Coherent over-rotation
   accumulated over 252 CZ, leakage and crosstalk remain candidates.
   [walk_scaffold_channels](../walk_scaffold_channels/README.md) fits six
   single channels (end-of-circuit flips, SX over-rotation, CZ local and
   conditional phase, extra damping, extra depolarizing) on readout0 and
   scores them on the depth members: none reproduces the floor and
   transfers in any of the four lanes, so the mechanism is not one of these
   alone.
4. **Readout misassignment as the driver** (excluded). Misassignment below 8
   percent per qubit keeps P(all four correct) above 0.72.
5. **Crosstalk from packed neighbours** (not supported). No CZ crosses a
   component boundary.

## Consequences

- The walk readout controls measure the scaffold's noise floor, so they are
  not SPAM controls. The 84 box-kite contrasts and the depth-4 class return
  (`hw-fez-ripple`, `hw-kingston-ripple-transfer`) come from the atlas
  members, at 33 to 53 CZ, not from the walk template.
- An identity-equivalent deep circuit is a usable per-tile gate-quality
  probe. The four lanes already rank Kingston above Fez, with Fez lane 0
  lowest.

## Proposed controls

- **Scaffold A/B on one tile under one calibration.** Run readout0 from the
  shared template (252 CZ) against a measure-only circuit (0 CZ). If the
  scaffold carries the loss, the measure-only arm reads near 0.95 and the
  template arm stays at the table's floor.

## Local-member conformance

`scripts/local_member_cz_conformance.py --check` (gate core-289) enumerates
every member live_run can plan, the registered groups and the family groups
rebuilt from each distinct retained `family_configuration`, and recomputes
[local_member_conformance.json](local_member_conformance.json). Two kinds of
member have a unitary whose law needs no two-qubit gate:

- A **local unitary** has operator Schmidt rank 1 across every single-qubit
  cut. Its circuit object is lowered as live_run compiles it, unbound for a
  shared template and without routing; the DAG is cut at every barrier,
  delay and measurement on the wires each touches and split into connected
  components, and CZ inside a component whose own unitary is local is
  scaffold. Cancellation across a barrier or an idle is what Design A,
  Design C, the conditional-Ramsey Bell arms, the star-Ramsey Bell and GHZ
  arms and the spectator wavefront ask the device to perform, and it passes.
- A **product output** has an entangling unitary that maps its prepared
  input to a product state, so every CZ it executes is optional for its law.

A member with mid-circuit measurement, reset or control flow has no unitary.
Its ideal law over its classical bits is enumerated exactly, one statevector
per measurement and reset branch with `if_else` selecting its block
(`qpe_diagnostics.ideal_branch_probabilities`), and labeled a point mass, a
product of its single-bit marginals, or correlated. A point-mass or product
law has no cross-bit correlation. A correlated law that stays unchanged
once every multi-qubit unitary is removed from the bound circuit,
control-flow blocks included, comes from measurement and classical
feed-forward alone. A dynamic member with either law that executes any CZ
needs a declaration (`DYNAMIC_LAW_PROBES`) naming the measurement its CZ
serves; a correlation its multi-qubit gates produce passes. The audit
cannot prove a dynamic member's CZ unnecessary, only that its law carries
no correlation a CZ would be needed to produce. The member digest includes
each control-flow condition and block, so members that differ only inside a
branch stay distinct.

Of 1793 distinct members, 585 are local unitaries, 20 product outputs, 238
dynamic and 950 entangling; none is unchecked. Of the 238 dynamic members, 183
execute no CZ, 31 have a correlated law that their multi-qubit gates
produce (the N=21 feedback, encoded and orbit pairs, the patch orbit pairs
and the XX, YY and ZZ coherence arms) and 24 execute CZ under a point-mass or product law. Fifty-four members execute
CZ their law does not need, and each matches a declaration naming what it
measures. Ten local
unitaries carry 144 scaffold CZ each before routing (`SCAFFOLD_CONTROLS`):
the four walk readout controls, the four depth-0 walk points and the two
template arms of the scaffold A/B campaign. Twenty product outputs execute
17 to 24 CZ, or 144 for walk points (`PRODUCT_OUTPUT_PROBES`): the sixteen
rank-sector endpoint probes at parameter one with their references, and the
four depth-1 walk points, where the walk sends its input to a product
state. Twenty-four dynamic members execute 6 to 41 CZ: the folded QPE,
archived, delay and feed-forward-off rungs and the odd-label correction
pair, whose one-hot or product eigenphase readout is the phase the
controlled rotations kick onto the control; `folded_qpe_null`, which keeps
the eigenstate preparation's 6 CZ so the contrast with the folded members
isolates the controlled rotation; `hybrid_shor_N15_a2` (35 CZ); and the XY
and YX coherence arms, which read the imaginary part of the branch-signed
coherence after the orbit prefix's controlled swaps. A new member that
executes CZ its law does not need fails the gate until it states why.
`--check-dynamic` (gate core-409) rebuilds the planned groups and recomputes
the dynamic rows against the record without the static classification.
`--self-test` (gate core-406) classifies synthetic dynamic circuits of every
law and unchecked reason, a feed-forward copy beside a spectator CZ among
them, `--self-test-undeclared` (core-407) requires the
stored census to fail naming `folded_qpe_null` once its declaration is
removed, and `--cross-check-n21` (core-408) rebuilds the 28 correlated N=21
members and requires their enumerated law to equal the Fraction law
`qpe_diagnostics.n21_labeled_law`, lifted onto the all-zero herald bits
(`qpe_diagnostics.lift_phase_law`) for a heralded member.

## Files

- `analyze.py --run DIR` prints total-variation distances and the chi-square
  test for the walk members of one run.
- `figures.py --run DIR --out DIR` draws figures 1 and 2 from a run, plus
  figure 3. Figure 3 plots an Aer depolarizing sweep whose generating script
  was not retained, so `figures.py` tabulates its points. The retained
  figures come from the 2026-10-13 Fez ripple run.
