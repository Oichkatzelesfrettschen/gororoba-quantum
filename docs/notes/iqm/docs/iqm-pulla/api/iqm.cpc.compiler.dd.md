> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1dbd04eb70fc1d663ad6aeaebba9021401428d81d1281f94c2b3309c1a1586fa.

# dd

Full path: iqm.cpc.compiler.dd

Dynamical decoupling utilities.

Module Attributes

|  |  |
|----|----|
| [`STANDARD_DD_STRATEGY`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY.html#iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY "iqm.cpc.compiler.dd.STANDARD_DD_STRATEGY") | The default DD strategy uses the following gate sequences: |

Functions

|  |  |
|----|----|
| [`generate_phases_of_urn_sequence`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.generate_phases_of_urn_sequence.html#iqm.cpc.compiler.dd.generate_phases_of_urn_sequence "iqm.cpc.compiler.dd.generate_phases_of_urn_sequence")(n) | Generate PRX gate phases for the URn sequence. |
| [`insert_dd_sequences`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.insert_dd_sequences.html#iqm.cpc.compiler.dd.insert_dd_sequences "iqm.cpc.compiler.dd.insert_dd_sequences")(builder, schedule, strategy) | Insert dynamical decoupling sequences into the given schedule. |
| [`merge_wait_instructions_in_schedule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule.html#iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule "iqm.cpc.compiler.dd.merge_wait_instructions_in_schedule")(builder, ...) | Merge adjacent `Wait` instructions in the drive channels of the given schedule. |

Exceptions

|  |  |
|----|----|
| [`DDError`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.DDError.html#iqm.cpc.compiler.dd.DDError "iqm.cpc.compiler.dd.DDError") | Something was wrong in user input for dynamical decoupling. |
