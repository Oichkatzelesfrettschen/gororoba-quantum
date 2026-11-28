# A5-242 orientation-bit case, merged diagonal on ibm_kingston

Status: written case with its binding dry run; the dry run fails the case's own ratio bound (swap members), so the case
is not admitted and nothing was submitted. Parent case: [pathion-kernel-map-orientation-bit.md](pathion-kernel-map-orientation-bit.md)
(question, falsifiers, decision rule, analysis). Redesign: [pathion-kernel-map-orientation-architecture.md](pathion-kernel-map-orientation-architecture.md),
section 3(b) b1. Owner decision of 2026-11-28: merged diagonal, e1 + e26 primary, MIN_REGIONS 11 at replica floor 0.5,
ibm_kingston only.

Evidence classes: "record" is the retained dry run results/live/2026-11-28T035012.386370Z (code commit a2104903d, tree
unmodified); "exact" is an Operator or Statevector equality; "model" is the architecture document's placement model.

## What it measures

The question of the parent case: whether the character gap lambda_16 - lambda_0 of the retained map follows the
orientation qubit, the compiled SELECT or the physical qubit, and whether a state-dependent error of that qubit
contributes. The circuits are the parent case's sixteen members (roles ctrl, move, xtwin and swap, operands e1 + e26 and
e1 + e18, two arms each, same names and order) with the five-qubit oracle diagonal folded into the six-qubit SELECT
diagonal (`gororoba_quantum/pathion_kernel_map_orientation_merged.py`, group `pathion_kernel_map_orientation_merged`).
The operator of every member equals the retained member's on both arms (exact, 16 of 16,
tests/gororoba_quantum/test_pathion_kernel_map_orientation_merged.py), so the ideal outcome laws, the analysis and the
decision rule carry over unchanged. The mutation test of the algebra rules holds on the merged diagonal (honest half-sum
equals N; the cocycle-free diagonal and one negated joint sign move it).

## Why Aer cannot answer it

The parent case's reason holds unchanged: no modeled combination of depolarizing error, relaxation and asymmetric
readout predicts the retained positive gap at nullity 12 or the full nullity-4 gap, so the residue belongs to an effect
the noise models omit, and only the device measures it.

## Backend, shots, expected seconds

- Backend ibm_kingston only; exclusions ibm_kingston:0-4,16; replica floor 0.5; 17 PUBs (16 members and the isolated
  reference); 16,384 shots per PUB; repetition delay 20 us; seeds from the ANU draw below.
- Charge of the dry-run plan (2 s + shots x sum of (rep delay + scheduled duration) over the 17 PUBs): 10.99 s, against
  11.2 s from the model. At the retained case's measured-to-expected ratio of 1.14 (12.0 s over 10.5 s) the charge reads
  12.6 s. Ceiling 16.8 s, which is 1.5 times the model charge as the retained 18 s ceiling is 1.5 times its 12.0 s
  expected charge; `--max-execution-seconds 17`. Credits: IBM Open plan quantum seconds only.

## Dry run against the design

| Quantity | Design (model) | Dry run (record) |
|---|---|---|
| Regions placed at floor 0.5 | 11 | 11 |
| Best and worst region score | 0.562, 0.357 | 0.529, 0.346 |
| CZ per unit, e1 + e26: ctrl, move, xtwin, swap | 99, 95, 99, 102 | 100, 102, 100, 171 |
| CZ per unit, e1 + e18: ctrl, move, xtwin, swap | 93, 93, 93, 92 | 96, 98, 96, 119 |
| Swap ratio to control | 1.03, 0.99 | 1.71, 1.24 |
| Charge | 11.2 s | 10.99 s |

Layout [73, 79, 72, 74, 71, 93], transpiler seed 64203 (the best of eight consecutive seeds from index 33).
Regions, scores, seconds and the ctrl, move and xtwin counts match the design within 1 to 5 CZ. The swap members miss by
a layout effect: live_run.py leaves the layout to the transpiler search, which does not hold the spider(2,2,1) tile and
the assignment of the design, and the swap member exchanges logical wires 1 and 4, so its cost depends on whether those
wires sit adjacent. The admission check refuses the plan on four lines (both arms of both swap units); the other rules
pass (backend, floor, 11 regions, exclusions, equal arms, charge). The deviation is reported, not tuned.

### Pin of the layout

`--pin-layout` is not available to this group: `live_run.py` accepts it only for the pinned campaigns
(PINNED_CAMPAIGNS: coherence_probes, primorial_gap88), the idle campaigns and the n21 families, and its replicas are
the pinned paths themselves. For a standalone group it carries neither a per-region tile shape nor a logical-to-physical
assignment. Missing: a pin that takes the tile shape and assignment of one region and maps it onto every placed region
(`pinned_replicas` maps the first path onto the others and could do this once a standalone group may name a pin). The
dry run ran without a pin; `live_run.py` is unchanged in this round.

### Gate order of the exchange member

On the dry-run compile the non-rz gate sequence of xtwin equals the control's for e1 + e18 (PUBs 10 and 14, 11 and 15)
and differs for e1 + e26 (PUBs 1 and 6, 3 and 7), with equal CZ, sx, x and measure counts (inference from PUB order in
`isa.qpy`). Over ten transpiler seeds on one tile the merged members agree in five or six of ten, the retained members
in ten of ten. The statistic D (control minus exchange) is zero under errors that act before the frame only when the
compiled gate sequences agree, so D at e1 + e26 carries a compile difference besides the frame. Falsifier: a pinned
layout compiles both members to one sequence.

## Power

Noncentral-t power for G16 of the control (alpha 0.05 over 16 tests, retained scatter and effects, one job), recomputed at
the 11 placed regions: 0.926 for e1 + e26 and 0.644 for e1 + e18 (diff_cm: 0.585 and 0.323). A shorter circuit may
shrink the scatter; no measurement supports that, so the power rests on the retained scatter (inference).

## Falsifiers

- A fresh plan on the calibration in force places fewer than 11 regions, exceeds 16.8 s, or touches an excluded qubit:
  the check refuses and nothing is sent.
- Any swap or moved member routes more than 20 percent from its control: the check refuses (the state of the record
  above).
- The measured gap reading is decided by the parent case's rule; this case changes the circuit's cost, not the rule.

## Seeds

`seed_transpiler` is index 33 and `seed_simulator` index 34 of
docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json (values 64202 and 53470), recorded in
docs/evidence/qrng_seeds/allocations.json (runtime rows of the dry run); `ci/seed_provenance.py --check` passes.

## Command the parent runs after approval

From the repository root, with the account unset (primary), once the swap placement is resolved by the owner:

```sh
GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh --check '"$PYTHON" ../scripts/pathion_kernel_map_orientation_merged_check.py' -- \
  --backends ibm_kingston --groups pathion_kernel_map_orientation_merged --shots 16384 \
  --exclude-qubits ibm_kingston:0-4,16 --replica-floor 0.5 --rep-delay 2e-5 --max-pending 100 \
  --min-remaining-seconds 20 --max-execution-seconds 17 \
  --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json#33 \
  --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json#34 --out ../results/live
```

With the layout of the record above the check exits 1 on the swap units and nothing is submitted.

## Open decisions

- Swap units: pin the layout (a change to `live_run.py`), drop the two swap units (the check's ratio rule then needs the
  roles list changed), or accept a swap cost the check refuses.
- `experiments.py` registers the group; `EXPERIMENT_SOURCE_MANIFEST` in `live_run.py` lists
  `pathion_kernel_map_orientation.py` and not the successor module, so the experiment digest does not bind the merged
  module's bytes. Adding the entry is a one-line change to `live_run.py`.
- The four `results/live/archives/*.qpy` files (the isa.qpy of this and the three earlier dry runs) stay untracked as in
  the earlier dry-run commit; `isa.qpy.sha256` of each record names its file.
