# Cross-experiment exposure and the next diagnostic set

Every retained acquisition placed its groups on physical tiles, and later
runs flagged some of those qubits. This note reads the exposure matrix of
[exposure.json](../evidence/walk-control-scaffolding/exposure.json)
(`scripts/scaffolding_exposure.py`, gate core-276) against the registered
claims in `docs/state/research_state.json`. It then scopes the diagnostics
that separate the open mechanisms. Everything below comes from retained data
and needs no QPU time unless it says so.

## Flagged qubits and the runs that touched them

| Flag | Qubits | Source | Runs whose replicas include them |
| --- | --- | --- | --- |
| Kingston readout fault | 0, 1 | corner baseline (`hw-corner-readout-fault`) | pilot hybrid Shor replica 0 (2026-10-11), rank sector 4 and ripple atlas lane 6 (2026-10-15), corner baseline |
| Kingston short relaxation | 2, 3, 16 | corner baseline | same runs |
| Kingston first-bit correlation | 79 | correction strata (`hw-first-bit-disagreement`) | pilot folded-QPE replica 2, folded-QPE ladder (both arms), both correction runs |
| Fez weak rank tile | 2, 3, 4, 16 | endpoint decomposition | Fez rank sector 2, Fez walk lane 0 |
| Fez walk lane 0 | 1, 2, 3, 4 | walk audit | Fez walk lane 0, Fez rank sector 2 |

## Cross-result findings from retained data

1. **The Kingston readout fault was present four days before it was found.**
   - On 2026-10-11 the pilot's hybrid Shor replica 0 measured an output bit on
     qubit 0. That bit reads 1 with probability 0.618.
   - The same bit reads 0.448 to 0.491 on the five other replicas, which share
     one ideal law, while the replica's qubit-2 bit reads a normal 0.512.
   - The corner baseline's flips for qubit 0 on 2026-10-15
     (P(1|0) = 0.388, P(0|1) = 0.144) predict
     0.5 (1 - 0.144) + 0.5 (0.388) = 0.622 for an ideal marginal of 0.5.
   - So the fault persisted for at least four days, through repeated
     recalibrations that never reported it.
   - The pilot's factorable yield on that replica (0.5125) stayed among the
     best, because factorability does not depend on that bit.
2. **The correction decision and the first-bit correlation share qubit 79.**
   - The measured-bit arm follows the recorded first bit. The known-label arm
     ignores it.
   - Independent, state-preserving assignment error is excluded
     ([novel-insights](../evidence/novel-insights/REPORT.md), section 2).
   - Where the recorded 0 reflects a real state change of qubit 79, following
     the recorded bit corrects the actual state, so that part of the defect
     favors measured correction. A common cause behind both the misread and
     the terminal loss is not excluded.
   - `retain_measured_correction` therefore stands as the registered decision,
     but it was taken on a qubit whose recorded bit is correlated with the
     terminal outcome.
   - A known-label gain on a clean writer qubit remains untested.
3. **The walk controls are a per-tile gate-quality probe.** The
   identity-equivalent 252-CZ readout controls retain about 0.996 per CZ on
   Kingston against 0.989 to 0.992 on Fez, where the calibrated model predicts
   0.998. The worst Fez lane sits on the Fez weak rank tile, so the weak lanes
   on both devices coincide with low-numbered corner qubits.
4. **Coherent phases vary by tile.**
   - Across the eight fringe replicas the fitted phase spreads from -0.26 to
     +0.50 rad on a 42-CZ circuit.
   - The coherence window's -1.130 rad is a 40.9 kHz detuning difference
     between work qubits 68 and 66, or that plus whole turns.
   - The N21 orbit phase on Fez is of the same order.
   - These fit a recurring scale of quasi-static detuning differences of tens
     of kHz, which backend properties do not report.
5. **The scaffolding is confined to the walk template.** The 84 box-kite
   contrasts and every rank-sector contrast come from builders at 21 to 53 CZ
   per member. Contrasts difference two arms of one template on one tile, so
   load-proportional loss largely cancels in them while it sets the floor of
   absolute probabilities.

## Hybrid classical-quantum families

The families that combine a mid-circuit measurement or classical
post-processing with the quantum circuit carry the flagged qubits in the
places that matter most:

- **Folded correction.** The recorded first bit is written on qubit 79, the
  qubit whose recorded bit correlates with the terminal outcome. A rerun on
  a clean writer separates the
  algorithm from the defect.
- **Folded-QPE ladder.** The archived arm reads its terminal bit on qubit 93,
  which shares 28 CZ with 79 in the correction circuit, while the coherent arm
  reads 95. The coherent advantage remains confounded with the terminal
  readout qubit, as recorded.
- **N21 orbit feed-forward.** The fitted kickback phase is the same order as
  the detuning differences above. A Ramsey reference of the work pair under
  the orbit's calibration would separate frame detuning from feed-forward
  phase.
- **Hybrid Shor pilot.** Its classical decode is insensitive to the corrupted
  bit, so its yield claim stands. Its packed-against-isolated equivalence
  compared two runs on the same corner qubits, so it is unaffected by the
  fault.

## A same-calibration diagnostic set

These measurements answer the open mechanisms. Each exists as a written or
proposed case, and run together they would share one calibration:

| Diagnostic | Question | Qubits | Cost class |
| --- | --- | --- | --- |
| Conditional Ramsey on (68, 67) and (66, 67) | Is the window rotation the work pair's detuning difference with the spectator in \|0>? | coherence patch | about 16 s each |
| Qubit 79 readout, immediate and delayed | preparation against relaxation against back-action | 79 | 0 CZ, a few seconds |
| Scaffold A/B | does the 252-CZ template, not the tile, set the walk floor? | one Fez or Kingston walk tile | 0 CZ against 252 CZ, a few seconds |
| Crossed tile x template | does the weak-lane loss follow the tile? | Kingston 0-3 and 104-107 | about 8 s |
| Corner re-baseline | is the qubit 0/1 fault still present? | Kingston 0-4, 16 | about 4 s |

`plan()` refuses to co-run standalone campaigns, so a single job needs a
bundle mode in `live_run.py`. It would take disjoint tiles at least one hop
apart, no dynamical decoupling, a shared shot count and one approval for the
set. That feature is scoped here, not built. Separate jobs remain the default.
Each separate job adds about 2.3 s of overhead and may execute under a
different calibration, and the latter matters more for comparing detunings
than the seconds do.

## Proposed implementation checks

- A conformance check on the compiled CZ count of every member whose bound
  law is a point mass on its input would have flagged the walk controls
  before submission.
- A census test reads `P(c = 1) = 1/2 - V (1/2 - 231/512)` on uniformly
  sampled sedenion triples. With bright and dark references to fix V, it
  tests how faithfully the hardware carries the sign function. It needs
  per-triple circuits outside the shared walk template.
