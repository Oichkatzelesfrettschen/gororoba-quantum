> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.insert_dd_sequences.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.dd.insert_dd_sequences.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 618fbda4dc8ec6a57e07e5ea6982b3b0940bef4337d4b516ee5bf35140492a53.

# iqm.cpc.compiler.dd.insert_dd_sequences

iqm.cpc.compiler.dd.insert_dd_sequences(*builder*, *schedule*, *strategy*)  
Insert dynamical decoupling sequences into the given schedule.

Note

Modifies `schedule` in-place.

Note

Assumes that the PRX implementation used only applies non-wait instructions on a single drive channel, and that the PRX duration does not depend on its arguments.

Parameters:  
- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – Schedule builder used to build `schedule`, containing channel information.

- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "(in iqm.pulse v15.0.0)")) – Schedule to modify.

- **strategy** ([*DDStrategy*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "(in iqm-station-control-client v14.0.0)")) – Dynamical decoupling strategy to use.

Return type:  
None
