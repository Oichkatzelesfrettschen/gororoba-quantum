# Deprecated single-circuit Quantum Inspire cases

These directories retain the first generation of the crosstalk and
teleportation cases, schema `qi-crosstalk-teleport-cases-v1`, written by
`scripts/qi_crosstalk_teleport_cases.py --write` before the case generators
emitted series. Each backend directory holds one `cases.json` naming every
circuit of the experiment (up to five) and the cQASM files it digests. The
design is deprecated: `qi_platform.HARDWARE_BATCH_CIRCUITS` admits at most
three circuits per hardware batch, so a five-circuit manifest fails the
submit preflight, and the live generators now write `batch-NN/` series under
`results/quantum_inspire/cases/`. This tree sits outside that root, so the
case gates (`qi_crosstalk_teleport_cases.py --check`,
`qi_zero_divisor_cases.py --check`, `qi_coupler_zz_map.py --check` and
`check_qi_platform_retention.py`) never read it, and no script submits from
it.

| Backend | Circuits | Executed | Retained run |
|---|---|---|---|
| QXsinglenodesimulator | 5 (four additivity configurations, teleport) | yes | `results/quantum_inspire/runs/2026-10-16T211635Z-QXsinglenodesimulator/` |
| Rydberg | 1 (teleport) | yes, failed at execution with an empty log | `results/quantum_inspire/runs/2026-10-16T211635Z-Rydberg/` |
| tuna_17 | 5 (four additivity configurations, teleport) | yes | `results/quantum_inspire/runs/2026-10-16T211635Z-tuna_17/` |
| tuna_5 | 4 (four additivity configurations) | no | none |
| tuna_9 | 5 (four additivity configurations, teleport) | no | none |

Every file of an executed backend equals, byte for byte, the copy its run
directory carries beside the raw shots, so the run directories remain the
evidence of record and `docs/state/research_state.json` registers the runs,
not these cases. The tuna_5 and tuna_9 manifests were generated and never
submitted; they are kept so the executed design and its unexecuted siblings
stay readable together. A new case takes the series layout.
