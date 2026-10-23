# Ascella approved order-pilot retry: instrument input-map error

The user explicitly resumed the single authorized retry of the original
eight-setting order pilot. Its manifest SHA-256 is
`1d1b9abfe727d92f6af1c81002b3e41e056b1b16330d3b8ae9746303bc3968fa`.
The regular account `eirikr` (UID 1000) ran the acquisition without sudo.
Private run directories used mode 700 and data files used mode 600.

The read-only plan initially refused Ascella's `calibration` status. A
bounded watcher checked again every 30 seconds and submitted once after both
live status records reported `available`, token occupancy was empty, and
the original resource and cost checks passed. The
[preflight](preflight.json) and [submission receipt](submission.json) record
the live tariff, performance metadata, software versions and approval.

| Observation | Result |
|---|---|
| Job | `3f707140-4413-40ed-bc31-58e09238926f` |
| Submitted | 2026-10-23 06:56:37 UTC |
| Collected | 2026-10-23 06:56:51 UTC |
| Approved settings | 8 |
| Approved sample / shot caps | 65,536 / 131,072 total |
| Approved execution / credit ceilings | 180 seconds / 1.016384 credits |
| Terminal status | `error`, `RUNTIME ERROR` |
| Provider execution duration | 1 second |
| Shots / detected samples | 0 / 0 |
| Observed credit debit | 0 credits and 0 free credits |

The exact diagnostic is
`RuntimeError: hardware_info.circuit_input_ports must be defined in the hardware_configto use Instruments.set_pic_input().`
The [lossless raw answer](raw/result.json), [parsed result](results.json),
[sent body](job-body.json), [checkpoint](submission-state.json),
[case manifest](cases.json) and [circuit](circuit.json) retain the acquisition.
The usage reports before and after submission increase from 56 to 57 jobs;
Ascella's job count and cumulative duration increase from 5 to 6. Both credit
counters remain unchanged. Token consumption reports establish that debit,
rather than an account-wide remaining balance.

The error consumes the single retry and triggers its stopping rule. Hardware
operator probabilities, loss and drift remain unmeasured. The acquisition
supports a continuing failure of the tested sampling path despite public
availability; the private deployed instrument configuration remains unobserved.
The [instrument-readiness design](../../../../docs/design/ascella-instrument-readiness-and-packed-tests.md)
owns the causal boundary, prior attempts and further-execution conditions.
