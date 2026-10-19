> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ef5c5b9a0739e7edd8a9e21858a62c85bab978bd3693f3a05dd7e01addbf5f5a.

# SchedulingAlgorithm

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.SchedulingAlgorithm(*value*)  
Bases: [`Enum`](https://docs.python.org/3.11/library/enum.html#enum.Enum "(in Python v3.11)")

Algorithms for resolving composite TimeBoxes into atomic ones.

Attributes

|  |  |
|----|----|
| [`HARD_BOUNDARY`](#iqm.pulse.timebox.SchedulingAlgorithm.HARD_BOUNDARY "iqm.pulse.timebox.SchedulingAlgorithm.HARD_BOUNDARY") | Respects the `TimeBox` boundary such that the longest channel with a box defines its boundary and all other channels are padded to this length (using the specified `SchedulingStrategy`). |
| [`TETRIS`](#iqm.pulse.timebox.SchedulingAlgorithm.TETRIS "iqm.pulse.timebox.SchedulingAlgorithm.TETRIS") | Will pack the schedule as tightly as possible while respecting the defined scheduling neighborhood. |

Methods

HARD_BOUNDARY *= 'HARD_BOUNDARY'*  
Respects the `TimeBox` boundary such that the longest channel with a box defines its boundary and all other channels are padded to this length (using the specified `SchedulingStrategy`).

TETRIS *= 'TETRIS'*  
Will pack the schedule as tightly as possible while respecting the defined scheduling neighborhood.

Inheritance

![Inheritance diagram of iqm.pulse.timebox.SchedulingAlgorithm](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-38c292c92b2cbf86937c5a4155abf186df6965cf.png)
