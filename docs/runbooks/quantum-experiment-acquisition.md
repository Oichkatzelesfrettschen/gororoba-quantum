# Quantum experiment acquisition review

The [corrected design](../design/quantum-experiment-conformance.md) defines the mathematical targets and
claim boundaries. The [evidence bundle](../evidence/quantum-experiment-conformance/README.md) supplies the
exact payloads, complete setting inventory, seed assignments, shot design and aggregate credit ceilings.
This procedure turns those prospective cases into separately approved provider acquisitions.

## Questions and controls

| Family and execution surface | Device or implementation question | Controls and reported outcome |
|---|---|---|
| Dimension-six transitions on Tuna-17 | How much of each observed overlap residual remains after accounting for the routed, angle-quantized operator? | All 54 transitions, identity-transition settings, two batch readout references, leakage labels, per-setting native residuals |
| Dimension-six transitions on QX | Does the provider emulator reproduce the exact rounded Tuna payload and recorded measurement map? | The same 54 compact twins and register fixtures; compare with the compiled probability law |
| Dimension-six transitions on Ascella | How accurately does the device realize the six-mode transition templates and the returned native mesh? | All 54 transitions, identity-transition settings, every native output port; distinguish template and returned-mesh predictions |
| Sedenion heralds on Tuna-17 | How accurately does the device realize the certified cancellation and bright laws at the admitted routed depth? | Kernel, bright, repeated bright, repeated kernel and fixture; batch readout references; unconditional selector probabilities |
| Sedenion heralds on QX | Does the emulator preserve the full five-qubit signed operator and output-register interpretation? | Compact twins of the same five science settings and their readout references |
| Sedenion heralds on Ascella | How accurately does the device realize the certified restricted dilation and reproduce its repeated meshes? | Four-mode kernel/bright and eight-mode fixture restrictions, repeated arms and all twelve outputs |
| Quarter-mass amplification on Tuna-17 | How does the staged preparation/oracle/reflection circuit compare with direct preparation of the same target state? | Initial quarter-mass, amplified, omitted oracle, omitted reflection and direct-target settings with batch readout references |
| Quarter-mass amplification on QX | Does the emulator reproduce the complete staged circuit operators and their success probabilities? | The five compact twins; full target-state matrix checks remain the deterministic reference |

Exact arithmetic answers whether the mathematical identities hold. A noise simulator cannot determine a
device's realized readout, leakage, compiled optical mesh, drift or coherent gate error. The QX case asks
about the provider emulator's executable payload and result interface; local matrix identities establish
its expected law but do not exercise that remote interface. Neither case constitutes a new mathematical
proof, a physical wormhole measurement, a protection experiment, an infinite-group projection, or factoring.

## Freeze the approved acquisition

1. Select the provider and scientific family prospectively. Retain a campaign inventory containing every
   selected case and its digest. A reduced pilot gets its own scope and precision calculation; it cannot
   inherit the full family's conclusion from a selected set of favorable outcomes.
2. Copy the canonical `runner-cases` cases into the provider's normal run area. The earlier build-host
   manifests are historical candidates and stay outside acquisition admission. Keep their payload and case-manifest bytes
   identical. Planning, checkpoint and raw collection files belong beside the copied cases, outside the
   deterministic evidence inventory.
3. Run read-only provider admission against the exact copied cases. Refresh backend identity, native
   resources, catalogue limits, current offer, occupancy and source routing. Ascella `plan` captures the
   serialized job with creation intercepted. The retained representative preflight covers one dimension-six
   setting; its scope does not establish admission of the whole campaign.
4. Record the runtime forecast and its provenance. The generated 300-second value is a per-job stop ceiling.
   The representative preflight supplied that ceiling as its conservative envelope input; the provider
   operation measured neither circuit runtime nor throughput. A forecast for the proposed acquisition
   must identify the retained timing evidence or provider planning estimate that supports it, along with
   uncertainty. A missing forecast keeps the case outside submission admission.
5. Restate the selected case count, per-setting sample and shot bounds, summed execution ceilings, pauses,
   expected credits and maximum credits. The generated manifests mechanically bound shots and per-job
   optical credits. The retained one-credit base charge and observed per-shot offer explain the planning
   arithmetic; refresh the offer before approval.
6. Freeze the scientific decision rule. Report requested, compiled/template and observed laws separately.
   Readout correction remains a sensitivity analysis. The empirical QI readout-contrast threshold is 0.2;
   failed or incomplete controls keep acquisition interpretation inconclusive. Ascella instrument
   qualification remains explicitly unassessed until a separately justified criterion is registered.
7. Obtain approval naming the written case, backend, payload identity, shots, expected seconds, ceilings
   and credits. Replace Ascella's `awaiting-live-budget-review` admission state only in a digest-bound
   successor case carrying the completed review. The original generated manifest keeps its bytes.

The generated bundle records prospective acquisitions: the software supplies complete
payloads and mechanical validation while acquisition forecasts and instrument qualification retain their
own evidence requirements. A provider catalogue or a captured payload supplies neither a measured result
nor permission to spend credits.

## Submit and collect

Use `scripts/qi_platform.py` or `scripts/qd_platform.py` with the approved successor case. Both runners
retain their existing approval, checkpoint and lossless collection behavior. The Quantum Inspire runner
obeys the three-circuit hardware batch policy and its interbatch pauses. An account-wide queue observation
grants cancellation authority over the jobs named by the approval only.

The sedenion schedule lists kernel, bright, bright-repeat and kernel-repeat with contrast coefficients
`+, -, -, +`. Read actual execution bounds from each job, establish non-overlapping intervals in that order,
and verify repeated payload identity. Ascella additionally requires matching returned native meshes and
inputs. Queue order and requested scheduling remain separate observations. The analyzer withholds an
admitted contrast when order, identity or controls remain unestablished.

Retain every raw outcome and result metadata before analysis. Run `scripts/experiment_analysis.py` against
the collected directories and their prospectively frozen campaign. The report binds case digests and raw
hashes and identifies missing settings, short jobs, failed controls, model-conditional precision and the
availability of provider-native predictions. An inventory-complete report alone establishes inventory
completion. Register each retained acquisition and its ledger entry through the existing research-state
procedure in the change that retains its results.
