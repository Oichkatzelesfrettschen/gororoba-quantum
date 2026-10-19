> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 69e3244db89ac640ec569388ccdef7dd19d3e7a35381c2a3188d3461b9ffa7ec.

# iqm.pulse.scheduler.extend_hard_boundary

iqm.pulse.scheduler.extend_hard_boundary(*schedule*, *child_schedule*, *child_components*, *neighborhood_components*, *component_durations*, *is_alap*)  
Merge two Schedules together such that the timebox boundary is respected.

This scheduling algorithm treats the Schedules as hard, rectangular boxes where any ragged edges will be padded with Waits, and the boxes are not allowed to overlap.

The algorithm is as follows:

1\. When adding `child_schedule` to `schedule`, the longest channel in `schedule` that overlaps with the channels present in child determines the earliest possible starting time for the `child_schedule`, and all other channels in `schedule` are padded with `Wait` to the aforementioned max length.

2\. An occupied channel in `schedule` will always occupy all channels of the corresponding component (qubit, coupler, …). This is handled by keeping track of occupied durations for each component (no unnecessary padding is added to channels which do not have an actual physical pulse).

3\. After the schedules are combined, all the common channels of `schedule` and `child_schedule` are blocked up to their common maximum length.

This algorithm should not be used with variable sampling rates in the schedule channels. In that case, use [`extend_hard_boundary_in_seconds()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary_in_seconds.html#iqm.pulse.scheduler.extend_hard_boundary_in_seconds "iqm.pulse.scheduler.extend_hard_boundary_in_seconds") instead.

Parameters:  
- **schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – Schedule that should be extended with `child_schedule`. Modified in place.

- **child_schedule** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – Child schedule to be added.

- **child_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Components (qubits, couplers, computational_resonators) that have at least one channel in `child_schedule`.

- **neighborhood_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – QPU components neighboring the `child_components` that should additionally be blocked in the scheduling.

- **component_durations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Blocked durations for each component used by `schedule`. These act as the earliest starting points for a new segment added to any of the channels of the component, but will also block the component even if it has no occupied channels in the schedule yet or ever (e.g. a computational resonator). Modified in place.

- **is_alap** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the scheduling strategy is ALAP (As Late As Possible).

Return type:  
*None*
