> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.apply_move_gate_phase_corrections.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.apply_move_gate_phase_corrections.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e94252718cab7e8670426be550334866f80b755f675ab52bfcb137a143d5fd9d.

# iqm.pulse.gates.move.apply_move_gate_phase_corrections

iqm.pulse.gates.move.apply_move_gate_phase_corrections(*schedule*, *builder*, *apply_detuning_corrections=True*)  
Schedule-level pass applying phase corrections for MOVE sandwiches to the first MOVE component.

Note

Assumes the MOVE gate implementation is based on [`MOVE_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CustomWaveforms.html#iqm.pulse.gates.move.MOVE_CustomWaveforms "iqm.pulse.gates.move.MOVE_CustomWaveforms").

Processes all the MOVE sandwiches in `schedule`, summing up the [`VirtualRZ`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.VirtualRZ.html#iqm.pulse.playlist.instructions.VirtualRZ "iqm.pulse.playlist.instructions.VirtualRZ") instructions on the (virtual) drive channels of the second MOVE component (either qubit or resonator), adding the phase difference resulting from detuning of the two MOVE components to the total, and applying it on the first MOVE component (has to be a qubit) at the end of each sandwich.

Parameters:  
- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – instruction schedule to process

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder")) – schedule builder that was used to build `schedule`

- **apply_detuning_corrections** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – if True, also apply detuning phase corrections

Returns:  
copy of `schedule` with the phase corrections applied

Return type:  
[*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")
