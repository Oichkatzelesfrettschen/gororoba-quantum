> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e55d2c78e0d5cdd27baadce901b33b55de81d78bbd278e0b559bfe9f27b6956f.

# standard_stages

Full path: iqm.cpc.compiler.standard_stages

Standard compilation stages, their constituent compiler passes, and functions for implementing them.

There are 6 standard compilation stages:

1.  Circuit-to-circuit.

2.  Circuit-to-timebox.

3.  Timebox-to-timebox.

4.  Timebox-to-schedule.

5.  Schedule-to-schedule.

6.  Schedule-to-playlist.

Breakdown of compiler passes of each stage:

## 1. Circuit-to-circuit

1.  Map the logical QPU components to physical QPU components. Provided mapping is used, if any. Otherwise, identity mapping is used.

2.  Choose implementations for circuit operations based on the calibration set.

3.  Add additional terminal measurements and/or convert the terminal measurements to the measure_fidelity QuantumOp.

## 2. Circuit-to-timebox

1.  Resolve the circuits to timeboxes using `ScheduleBuilder.circuit_to_timebox()`.

## 3. Timebox-to-timebox

1.  Merge any MultiplexedProbeTimeBoxes inside each TimeBox using `TimeBox.composite()`.

2.  Add the heralding measurement timebox to all circuits if `HeraldingMode` in circuit execution options requires it.

3.  Add a reset timebox to all circuits.

## 4. Timebox-to-schedule

1.  Resolve the timeboxes to schedules using `ScheduleBuilder.resolve_timebox()`.

## 5. Schedule-to-schedule

1.  Apply dynamical decoupling sequences to the schedule if requested.

2.  Apply resonator-related phase corrections if MOVE gates are used.

3.  Remove non-functional instructions from schedules using `ScheduleBuilder._finish_schedule()`.

4.  Apply drive crosstalk compensation pulses to the schedules, if requested (disabled by default). This is the last schedule-level pass so the compensation pulses are not modified by any later pass.

## 6. Schedule-to-playlist

1.  Build the playlist from the schedules using `ScheduleBuilder.build_playlist()`.

Module Attributes

|  |  |
|----|----|
| [`BUFFER_AFTER_MEASUREMENT_PROBE`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.BUFFER_AFTER_MEASUREMENT_PROBE.html#iqm.cpc.compiler.standard_stages.BUFFER_AFTER_MEASUREMENT_PROBE "iqm.cpc.compiler.standard_stages.BUFFER_AFTER_MEASUREMENT_PROBE") | Buffer that allows the readout resonator and qubit state to stabilize after a probe pulse, in s. |
| [`DRIVE_CROSSTALK_OP_NAME`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.DRIVE_CROSSTALK_OP_NAME.html#iqm.cpc.compiler.standard_stages.DRIVE_CROSSTALK_OP_NAME "iqm.cpc.compiler.standard_stages.DRIVE_CROSSTALK_OP_NAME") | Name of the (optional) quantum operation that carries the drive crosstalk calibration matrix. |

Functions

|  |  |
|----|----|
| [`apply_dd_strategy`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_dd_strategy.html#iqm.cpc.compiler.standard_stages.apply_dd_strategy "iqm.cpc.compiler.standard_stages.apply_dd_strategy")(schedules, builder, context) | Insert dynamical decoupling sequences into the schedules, if dynamical decoupling is enabled. |
| [`apply_drive_crosstalk`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_drive_crosstalk.html#iqm.cpc.compiler.standard_stages.apply_drive_crosstalk "iqm.cpc.compiler.standard_stages.apply_drive_crosstalk")(schedules, builder, ...) | Add drive-crosstalk compensation pulses to the schedules. |
| [`apply_move_gate_phase_corrections`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections.html#iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections "iqm.cpc.compiler.standard_stages.apply_move_gate_phase_corrections")(schedules, ...) | Apply calibrated phase corrections if MOVE gates are used. |
| [`build_playlist_and_merge_contexts`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts.html#iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts "iqm.cpc.compiler.standard_stages.build_playlist_and_merge_contexts")(schedules, ...) | Build the playlist from the schedules and merge the contexts for individual sweep spots. |
| [`clean_schedule`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.clean_schedule.html#iqm.cpc.compiler.standard_stages.clean_schedule "iqm.cpc.compiler.standard_stages.clean_schedule")(schedules, builder) | Remove non-functional instructions from schedules. |
| [`create_run_definition`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.create_run_definition.html#iqm.cpc.compiler.standard_stages.create_run_definition "iqm.cpc.compiler.standard_stages.create_run_definition")(playlist, context\[, ...\]) | Create MQE-style RunDefinition. |
| [`map_components`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.map_components.html#iqm.cpc.compiler.standard_stages.map_components "iqm.cpc.compiler.standard_stages.map_components")(circuits, component_mapping, ...) | Maps the logical component names in a sequence of instructions to the corresponding physical component names. |
| [`multiplex_readout`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.multiplex_readout.html#iqm.cpc.compiler.standard_stages.multiplex_readout "iqm.cpc.compiler.standard_stages.multiplex_readout")(timeboxes, timebox_input) | Merge any MultiplexedProbeTimeBoxes inside a TimeBox representing a circuit. |
| [`prepend_heralding`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.prepend_heralding.html#iqm.cpc.compiler.standard_stages.prepend_heralding "iqm.cpc.compiler.standard_stages.prepend_heralding")(timeboxes, builder, context) | Add the heralding measurement TimeBox to all circuits (locus: active components that can be measured). |
| [`prepend_reset`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.prepend_reset.html#iqm.cpc.compiler.standard_stages.prepend_reset "iqm.cpc.compiler.standard_stages.prepend_reset")(timeboxes, builder, context\[, ...\]) | Add a reset timebox to all circuits for all active components. |
| [`resolve_circuits`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_circuits.html#iqm.cpc.compiler.standard_stages.resolve_circuits "iqm.cpc.compiler.standard_stages.resolve_circuits")(circuits, builder\[, ...\]) | Resolve the circuits to timeboxes. |
| [`resolve_timeboxes`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.resolve_timeboxes.html#iqm.cpc.compiler.standard_stages.resolve_timeboxes "iqm.cpc.compiler.standard_stages.resolve_timeboxes")(timeboxes, builder\[, ...\]) | Resolve the timeboxes to schedules. |
| [`subscribe_and_probe`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.subscribe_and_probe.html#iqm.cpc.compiler.standard_stages.subscribe_and_probe "iqm.cpc.compiler.standard_stages.subscribe_and_probe")(circuits, settings, ...) | Add additional terminal measurements to the circuit and modify measurement instruction arguments. |
| [`validate_circuits`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_circuits.html#iqm.cpc.compiler.standard_stages.validate_circuits "iqm.cpc.compiler.standard_stages.validate_circuits")(circuits, builder, context) | Validate circuits and aggerate metrics data from them. |
| [`validate_settings`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_settings.html#iqm.cpc.compiler.standard_stages.validate_settings "iqm.cpc.compiler.standard_stages.validate_settings")(circuits, settings) | Validate the settings for circuit execution options (only some combinations make sense). |
