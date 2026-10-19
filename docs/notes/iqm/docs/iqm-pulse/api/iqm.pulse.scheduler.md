> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 169ba0287308397b59d017dd4edc694af52400a54aee76b52fedeafe2a8b7f23.

# scheduler

Full path: iqm.pulse.scheduler

Tools for composing instruction schedules in time.

Under the idealized, noiseless, crosstalk-less computational model, the scheduling algorithms should preserve the effect of the schedules on the computational subspace, i.e. executing [`Schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") `A` immediately followed by `B` should be equivalent to executing the composed schedule `A+B`.

The composing is always done so that in `A+B` all the channels of `B` start their execution simultaneously, and remain in sync. [`Nothing`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Nothing.html#iqm.pulse.playlist.instructions.Nothing "iqm.pulse.playlist.instructions.Nothing") instructions can be added as spacers between the channels of `A` and `B` as necessary to make this happen.

Typically the scheduling algorithms also try to minimize the total duration of the composed schedule.

Module Attributes

|  |  |
|----|----|
| [`BLOCKING`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.BLOCKING.html#iqm.pulse.scheduler.BLOCKING "iqm.pulse.scheduler.BLOCKING") | Nonsolid Instructions that nevertheless block. |

Functions

|  |  |
|----|----|
| [`extend_hard_boundary`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary.html#iqm.pulse.scheduler.extend_hard_boundary "iqm.pulse.scheduler.extend_hard_boundary")(schedule, ...) | Merge two Schedules together such that the timebox boundary is respected. |
| [`extend_hard_boundary_in_seconds`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_hard_boundary_in_seconds.html#iqm.pulse.scheduler.extend_hard_boundary_in_seconds "iqm.pulse.scheduler.extend_hard_boundary_in_seconds")(schedule, ...) | The same as `extend_hard_boundary`, but the scheduling is done in seconds. |
| [`extend_schedule`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule.html#iqm.pulse.scheduler.extend_schedule "iqm.pulse.scheduler.extend_schedule")(A, B, channels, \*\[, TOL\]) | Extend a Schedule with another Schedule. |
| [`extend_schedule_new`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.extend_schedule_new.html#iqm.pulse.scheduler.extend_schedule_new "iqm.pulse.scheduler.extend_schedule_new")(A, B, channels, \*\[, TOL\]) | Extend a Schedule with another Schedule. |

Classes

|  |  |
|----|----|
| [`SegmentPointer`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.scheduler.SegmentPointer.html#iqm.pulse.scheduler.SegmentPointer "iqm.pulse.scheduler.SegmentPointer") | Tool for working with Segments. |

Inheritance

![Inheritance diagram of iqm.pulse.scheduler](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-aa5098cdba621f16ee5df7812f4b57a6cd092182.png)
