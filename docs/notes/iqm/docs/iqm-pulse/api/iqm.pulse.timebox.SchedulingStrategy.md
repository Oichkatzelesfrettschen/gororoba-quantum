> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 416ad65c2f8eb9295545dc624bab2f3227b2cc89f08effdf29b7b655e32bcc80.

# SchedulingStrategy

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.SchedulingStrategy(*value*)  
Bases: [`Enum`](https://docs.python.org/3.11/library/enum.html#enum.Enum "(in Python v3.11)")

Different scheduling strategies for the contents of composite TimeBoxes.

Attributes

|  |  |
|----|----|
| [`ASAP`](#iqm.pulse.timebox.SchedulingStrategy.ASAP "iqm.pulse.timebox.SchedulingStrategy.ASAP") | TimeBox contents are scheduled as soon as possible within the box. |
| [`ALAP`](#iqm.pulse.timebox.SchedulingStrategy.ALAP "iqm.pulse.timebox.SchedulingStrategy.ALAP") | TimeBox contents are scheduled as late as possible within the box. |

Methods

ASAP *= 'ASAP'*  
TimeBox contents are scheduled as soon as possible within the box.

ALAP *= 'ALAP'*  
TimeBox contents are scheduled as late as possible within the box.

Inheritance

![Inheritance diagram of iqm.pulse.timebox.SchedulingStrategy](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-54c3637e8497f77ecd7e1bac50d757a88b021b7f.png)
