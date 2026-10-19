> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary_in_seconds.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary_in_seconds.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 434a761ca56f6aadfe658334fc8e138a0fa9f899c2bea635b910986c4056ac49.

# iqm.pulse.scheduler.extend_hard_boundary_in_seconds

iqm.pulse.scheduler.extend_hard_boundary_in_seconds(*schedule*, *child_schedule*, *child_components*, *neighborhood_components*, *component_durations*, *is_alap*, *channel_properties*)  
The same as `extend_hard_boundary`, but the scheduling is done in seconds.

Used when the probe channel sampling rate differs from the other channels’ rate. The incoming schedules measure Instruction durations in samples, but `component_durations` is in seconds.

Parameters:  
- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – Schedule that should be extended with `child_schedule`. Modified in place.

- **child_schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – Child schedule to be added.

- **child_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Components (qubits, couplers, computational_resonators) that have at least one channel in `child_schedule`.

- **neighborhood_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Components neighboring the `child_components` that should additionally be blocked in the scheduling.

- **component_durations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Blocked durations for each component in `schedule`. These act as the earliest starting points for new segment added to any of the channels of a given component, but will also block the component even if it has no occupied channels in the schedule yet or ever (e.g. a computational resonator). The durations are in seconds. Modified in place.

- **is_alap** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the scheduling strategy is ALAP (As Late As Possible).

- **channel_properties** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – Mapping from channel name to its properties (e.g. the sample rates and granularities).

Return type:  
*None*
