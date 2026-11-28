# A5-242 orientation-bit case, merged diagonal on ibm_kingston

Status: written case with its binding dry run on the tile-template pin; the admission check admits the plan (exit 0), and
nothing was submitted. The unpinned dry run of the first round failed the check on the swap members and is kept as the
comparison. Parent case: [pathion-kernel-map-orientation-bit.md](pathion-kernel-map-orientation-bit.md)
(question, falsifiers, decision rule, analysis). Redesign: [pathion-kernel-map-orientation-architecture.md](pathion-kernel-map-orientation-architecture.md),
section 3(b) b1. Owner decision of 2026-11-28: merged diagonal, e1 + e26 primary, MIN_REGIONS 11 at replica floor 0.5,
ibm_kingston only.

Evidence classes: "record" is the pinned dry run results/live/2026-11-28T041415.297826Z (code commit 84b0ee5ca, tree unmodified) and
"unpinned record" the first-round dry run results/live/2026-11-28T035012.386370Z (code commit a2104903d); "exact" is an Operator or Statevector equality; "model" is the architecture document's placement model.

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
- Charge of the pinned dry-run plan (2 s + shots x sum of (rep delay + scheduled duration) over the 17 PUBs): 11.17 s,
  against 11.2 s from the model (the unpinned plan read 10.99 s). At the retained case's measured-to-expected ratio of
  1.14 (12.0 s over 10.5 s) the charge reads 12.7 s. Ceiling 16.8 s, which is 1.5 times the model charge as the retained 18 s ceiling is 1.5 times its 12.0 s
  expected charge; `--max-execution-seconds 17`. Credits: IBM Open plan quantum seconds only.

## Dry run against the design

| Quantity | Design (model) | Unpinned record | Record (tile-template pin) |
|---|---|---|---|
| Regions placed at floor 0.5 | 11 | 11 | 11 |
| Best and worst region score | 0.562, 0.357 | 0.529, 0.346 | 0.532, 0.343 |
| CZ per unit, e1 + e26: ctrl, move, xtwin, swap | 99, 95, 99, 102 | 100, 102, 100, 171 | 99, 95, 99, 102 |
| CZ per unit, e1 + e18: ctrl, move, xtwin, swap | 93, 93, 93, 92 | 96, 98, 96, 119 | 93, 93, 93, 92 |
| Swap ratio to control | 1.03, 0.99 | 1.71, 1.24 | 1.03, 0.99 |
| xtwin non-rz sequence equals ctrl (both operands, both arms) | required | differs at e1 + e26 | equal (check exit 0) |
| Charge | 11.2 s | 10.99 s | 11.17 s |

Layout [7, 6, 8, 17, 5, 9] on the primary compile, transpiler seed 64202 (the best of eight consecutive seeds from index
33). The CZ counts equal the design table (model) exactly, the region count and scores match it within 0.03, and the
admission check exits 0 on the record. At the retained case's measured-to-expected ratio of 1.14 the charge reads
12.7 s, inside the 16.8 s ceiling.

### Pin of the layout

`TILE_TEMPLATES` in `gororoba_quantum/live_run.py` names the logical-edge template of the group, the spider(2,2,1) of
the SELECT diagonal with edges (0,1), (0,2), (0,3), (1,4), (2,5), so logical wires 1 and 4 are adjacent. The pin takes no
flag, so the approved command below stays flag-identical. `select_candidates` embeds the template into the admitted
coupler graph minus the excluded qubits by subgraph isomorphism (`tile_template_layout`, the lexicographically least
embedding, a function of the coupler graph and the exclusions only), compiles every seed from that layout through the
existing `pinned` branch, and rejects a seed whose compiled circuits leave a template coupler undriven
(`tile_missing_edges`). Replica placement then moves the compiled pattern onto every region by the existing embedding
search, so each region keeps the template's couplers; a graph with no embedding rejects the backend. The group record
carries `tile_template`: the edges and, per region, the wire layout and `template_on_couplers` (true for all 11
regions of the record). Other groups compile and record as before (the new key and trace entries exist only for a group in
`TILE_TEMPLATES`). Evidence: tests/gororoba_quantum/test_live_run_tile_template.py, the red-team probe of the unpinned
record and the dry run above.

### Gate order of the exchange member

On the unpinned compile the non-rz gate sequence of xtwin differed from the control's for e1 + e26 (PUBs 1 and 6, 3 and
7) and matched for e1 + e18. The admission check now compares the non-rz sequence of the packed xtwin and control
circuits, read from the archive that `isa.qpy.sha256` names, for both operands and both arms. It refuses the unpinned
record on e1 + e26 and admits the pinned record: the falsifier of the first round (a pinned layout compiles both members
to one sequence) holds on this compile.

## Power

Noncentral-t power for G16 of the control (alpha 0.05 over 16 tests, retained scatter and effects, one job), recomputed at
the 11 placed regions: 0.926 for e1 + e26 and 0.644 for e1 + e18 (diff_cm: 0.585 and 0.323). A shorter circuit may
shrink the scatter; no measurement supports that, so the power rests on the retained scatter (inference).

## Falsifiers

- A fresh plan on the calibration in force places fewer than 11 regions, exceeds 16.8 s, or touches an excluded qubit:
  the check refuses and nothing is sent.
- Any swap or moved member routes more than 20 percent from its control, or an xtwin member compiles to another non-rz
  sequence than its control: the check refuses (the state of the unpinned record).
- The measured gap reading is decided by the parent case's rule; this case changes the circuit's cost, not the rule.

## Seeds

`seed_transpiler` is index 33 and `seed_simulator` index 34 of
docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json (values 64202 and 53470), recorded in
docs/evidence/qrng_seeds/allocations.json (runtime rows of the dry run); `ci/seed_provenance.py --check` passes.

## Command the parent runs after approval

From the repository root, with the account unset (primary):

```sh
GOROROBA_IBM_ACCOUNT= sh scripts/approved_run.sh --check '"$PYTHON" ../scripts/pathion_kernel_map_orientation_merged_check.py' -- \
  --backends ibm_kingston --groups pathion_kernel_map_orientation_merged --shots 16384 \
  --exclude-qubits ibm_kingston:0-4,16 --replica-floor 0.5 --rep-delay 2e-5 --max-pending 100 \
  --min-remaining-seconds 20 --max-execution-seconds 17 \
  --seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json#33 \
  --seed-simulator qrng:docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json#34 --out ../results/live
```

The wrapper plans afresh and submits at once; a plan that differs from the approved record writes `approval_required`
and sends nothing. The case still waits for the owner's approval of this written case.

## Open decisions

- Owner approval of the written case (backend, 16,384 shots, expected 11.2 to 12.7 s of quantum time) before the
  command above runs. No other decision is open: the swap placement is resolved by the pin, and the source manifest now
  lists the merged module.
- The `results/live/archives/*.qpy` files (the isa.qpy of this and the earlier dry runs) stay untracked as in the earlier
  dry-run commit; `isa.qpy.sha256` of each record names its file.

## Residual risk: dead-region attrition

The dead-region rule (visibility below 0.05 removes a region; more than a third dead reads the live-only verdict beside
the full one) can cut the surviving regions. Noncentral-t power of the case's rule (orientation_architecture.power_cells,
one job, retained scatter and effects, alpha 0.05/16) by surviving regions, from the 2026-11-28 red team and its rerun:

| Surviving regions | ctrl G16, e1 + e26 | ctrl G16, e1 + e18 | diff_cm, e1 + e26 | diff_cm, e1 + e18 |
|---:|---:|---:|---:|---:|
| 11 | 0.926 | 0.644 | 0.585 | 0.323 |
| 10 | 0.869 | 0.552 | 0.495 | 0.262 |
| 9 | 0.782 | 0.451 | 0.400 | 0.205 |
| 8 | 0.659 | 0.346 | 0.304 | 0.153 |
| 7 | 0.505 | 0.245 | 0.214 | 0.108 |

The predecessor run lost two of five regions at scores 0.25 to 0.35; four of the eleven placed regions here score 0.34 to
0.38. A shorter merged circuit may lower the scatter (no measurement supports it), so the table uses the retained scatter.
