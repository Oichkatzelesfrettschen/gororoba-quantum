> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26f78ba01fe2366551d54dd769997204d7bd70bdd6efc8e5f9a9324367c28a20.

# iqm.pulse.scheduler.extend_schedule

iqm.pulse.scheduler.extend_schedule(*A*, *B*, *channels*, *\**, *TOL=1e-12*)  
Extend a Schedule with another Schedule.

Extends `A` with `B`, modifying both. The extension can add new channels to `A`.

If `B` has a ragged left side, i.e. some of its channels begin with [`Nothing`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html#iqm.pulse.playlist.instructions.Nothing "iqm.pulse.playlist.instructions.Nothing") instructions, this algorithm will not always produce an optimally short schedule.

Parameters:  
- **A** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – schedule to be extended

- **B** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule")) – schedule to extend `A` with

- **channels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*ChannelProperties*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.channel.ChannelProperties.html#iqm.pulse.playlist.channel.ChannelProperties "iqm.pulse.playlist.channel.ChannelProperties")*\]*) – properties of the control channels

- **TOL** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – time durations equal or smaller than this are considered zero (in seconds)

Return type:  
*None*
