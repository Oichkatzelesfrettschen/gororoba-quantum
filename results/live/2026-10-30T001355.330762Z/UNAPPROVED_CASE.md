# Unapproved QPU case: full-register actor preparation

Status: UNAPPROVED. This descriptive plan authorizes no submission.

The same full-register shots supply the declared reporter projections. The plan describes gate, preparation and readout behavior of the selected device; a noise simulator does not measure the device response.

- Record SHA-256: `93325cea9acd4317700823192bd18fa9c3d727b62298bda8f802c8acc52521f4`.
- QPY SHA-256: `e298b5b6bf28729f7cecf4982a083f576c6697b3f98efd2383036324977f4ee9`.
- Frozen operational case SHA-256: `8fc22338271bc15675fa4e7fd59f99f22d75a8cd0145d0806f7ca88542fd5cc5`.
- Source-closure digest: `cd1d672f9cf9925cf67f866c6e25787d85bf815ebcc42b70779880fec5eb75b8`.
- Backend: `ibm_fez`.
- Per-job ceiling: 6 seconds; total ceiling: 20 seconds; reserve: 48 seconds.
- Estimated job seconds: `[3.110704128, 3.766064128, 4.079916032]`.
- Inference: descriptive; physical shot alignment, carryover and statistical admission remain unverified.

## Frozen operational case

The case records measured width, reporter and actor roles, projections, per-PUB preparations, shot allocations, delays and stated controls.

```json
{
  "actors": [
    2
  ],
  "allocations": [
    {
      "arm": "idle",
      "input": 0,
      "name": "delay-30us-idle-input-0",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 1,
      "name": "delay-30us-idle-input-1",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 2,
      "name": "delay-30us-idle-input-2",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 3,
      "name": "delay-30us-idle-input-3",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 0,
      "name": "delay-30us-active-input-0",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 1,
      "name": "delay-30us-active-input-1",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 2,
      "name": "delay-30us-active-input-2",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 3,
      "name": "delay-30us-active-input-3",
      "rep_delay_seconds": 3e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 0,
      "name": "delay-50us-idle-input-0",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 1,
      "name": "delay-50us-idle-input-1",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 2,
      "name": "delay-50us-idle-input-2",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 3,
      "name": "delay-50us-idle-input-3",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 0,
      "name": "delay-50us-active-input-0",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 1,
      "name": "delay-50us-active-input-1",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 2,
      "name": "delay-50us-active-input-2",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "active",
      "input": 3,
      "name": "delay-50us-active-input-3",
      "rep_delay_seconds": 5e-05,
      "shots": 4096,
      "stage": "pilot"
    },
    {
      "arm": "idle",
      "input": 0,
      "name": "delay-250us-idle-input-0",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "idle",
      "input": 1,
      "name": "delay-250us-idle-input-1",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "idle",
      "input": 2,
      "name": "delay-250us-idle-input-2",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "idle",
      "input": 3,
      "name": "delay-250us-idle-input-3",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "active",
      "input": 0,
      "name": "delay-250us-active-input-0",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "active",
      "input": 1,
      "name": "delay-250us-active-input-1",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "active",
      "input": 2,
      "name": "delay-250us-active-input-2",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    },
    {
      "arm": "active",
      "input": 3,
      "name": "delay-250us-active-input-3",
      "rep_delay_seconds": 0.00025,
      "shots": 1024,
      "stage": "references"
    }
  ],
  "backend": "ibm_fez",
  "carryover_rule": "Retain within-PUB shot order, job and PUB identity and available timing. Cross-PUB order and immediate physical predecessors remain unavailable unless provider evidence establishes them. Report initialization and carryover qualification as unresolved; descriptive similarity never passes equivalence.",
  "groups": [
    [
      0
    ],
    [
      1
    ],
    [
      154
    ],
    [
      0,
      1
    ],
    [
      0,
      154
    ],
    [
      1,
      154
    ],
    [
      0,
      1,
      154
    ]
  ],
  "inference": "descriptive",
  "initialization_seconds": 2.212e-06,
  "job_overhead_seconds": 2,
  "max_execution_seconds": 6,
  "max_pending": 100,
  "max_total_execution_seconds": 20,
  "pairs": [
    [
      0,
      1
    ]
  ],
  "purpose": "Unapproved descriptive full-register delay-and-activity pilot on ibm_fez reporters 0 and 1 and actor 2. Retain all 156 bits from every shared PUB shot. The pilot characterizes this layout; it neither confirms parity superiority nor qualifies the array.",
  "reference_rule": "Acquire all four reporter preparations and both actor arms at 250 microseconds, 1024 shots each. This retained default-delay comparison is not a certified initialization baseline. Keep its acquisition period separate from the 30 and 50 microsecond pilot jobs.",
  "reporters": [
    0,
    1
  ],
  "reserve_seconds": 48,
  "schema": "readout-actor-case-v1",
  "selection_rule": "Freeze reporters 0 and 1, actor 2 and the declared projections before acquisition. Report every preparation, arm and delay without pair selection, pooling or outcome-dependent exclusions. Acquire all 24 PUBs at fixed counts. Freeze any later delay and confirmation design in a separately approved case. The pre-acquisition Fez calibration snapshot selects exploratory qubit 154 because qubit 155 is flagged for low T2; all 156 qubits remain measured.",
  "width": 156
}
```

A separately reviewed case, an independently retained approval and the binding dry-run checks are required before any provider submission.

After explicit case approval, run from the repository root:

```sh
sh scripts/approved_run.sh --check '"$PYTHON" qpu_cases.py --validate-actor "$RUN" --reviewed-record ../results/live/2026-10-30T001355.330762Z --reviewed-sha256 93325cea9acd4317700823192bd18fa9c3d727b62298bda8f802c8acc52521f4' -- --family readout-actor --actor-case ../results/live/2026-10-30T001355.330762Z/actor-case.json --actor-reviewed-record ../results/live/2026-10-30T001355.330762Z --actor-reviewed-sha256 93325cea9acd4317700823192bd18fa9c3d727b62298bda8f802c8acc52521f4 --out ../results/live --max-execution-seconds 6 --max-total-execution-seconds 20
```
