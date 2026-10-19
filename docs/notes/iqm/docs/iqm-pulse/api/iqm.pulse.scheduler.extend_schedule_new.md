> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule_new.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule_new.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 18978637a5d21985ffdc862bd7d5e72520b3c0a83332206baae6cfef729594fa.

# iqm.pulse.scheduler.extend_schedule_new

iqm.pulse.scheduler.extend_schedule_new(*A*, *B*, *channels*, *\**, *TOL=1e-12*)  
Extend a Schedule with another Schedule.

Extends `A` with `B`, modifying `A`. The extension can add new channels to `A`.

Can also handle cases where `B` has a ragged left side, i.e. some of its channels begin with [`Nothing`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html#iqm.pulse.playlist.instructions.Nothing "iqm.pulse.playlist.instructions.Nothing") instructions.

Parameters:  
- **A** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – schedule to be extended

- **B** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – schedule to extend `A` with

- **channels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – properties of the control channels

- **TOL** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time durations equal or smaller than this are considered zero (in seconds)

Return type:  
*None*
