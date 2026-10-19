> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3a7edba04564cc468abd51ebdad7ac29255cb810c325fd67ee5a9728cd70fd41.

# MeasureBox

Module: [`iqm.pulse.timebox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html#module-iqm.pulse.timebox "iqm.pulse.timebox")

*class* iqm.pulse.timebox.MeasureBox(*label*, *locus_components*, *atom*, *children=\<factory\>*, *scheduling=SchedulingStrategy.ASAP*, *scheduling_algorithm=SchedulingAlgorithm.HARD_BOUNDARY*, *neighborhood_components=\<factory\>*, *boxes_length=0*, *measure_components=\<factory\>*, *additional_components=\<factory\>*)  
Bases: [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")

TimeBox associated with a measure implementation.

Supports [`multiplex()`](#iqm.pulse.timebox.MeasureBox.multiplex "iqm.pulse.timebox.MeasureBox.multiplex") between two class instances. Contains [`boxes_length`](#iqm.pulse.timebox.MeasureBox.boxes_length "iqm.pulse.timebox.MeasureBox.boxes_length") and [`measure_components`](#iqm.pulse.timebox.MeasureBox.measure_components "iqm.pulse.timebox.MeasureBox.measure_components") for identifying all class instances associated with a specific measure call.

The purpose of this class is to 1) denote that a TimeBox is associated with a measure implementation 2) identify all the MeasureBox instances associated with a given measure call via the boxes_length. Both of these features are needed in the circuit-level multiplexing pass (some client-side libraries like Qiskit do not support multiplexed measurements out-of-the-box, requiring a dedicated compiler pass on the IQM-side).

Attributes

|  |  |
|----|----|
| [`boxes_length`](#iqm.pulse.timebox.MeasureBox.boxes_length "iqm.pulse.timebox.MeasureBox.boxes_length") | How many MeasureBox instances the MeasureBoxes instance this MeasureBox belongs to has (used in circuit-level multiplexing). |
| [`measure_components`](#iqm.pulse.timebox.MeasureBox.measure_components "iqm.pulse.timebox.MeasureBox.measure_components") | The `MeasureBoxes.measure_components` of the MeasureBoxes `self` belongs to. |
| [`additional_components`](#iqm.pulse.timebox.MeasureBox.additional_components "iqm.pulse.timebox.MeasureBox.additional_components") | The `MeasureBoxes.additional_components` of the MeasureBoxes `self` belongs to. |
| `label` | Description the contents of the box for users' convenience. |
| `locus_components` | Names of the QPU components on which this timebox operates. |
| `atom` | Resolved contents of the TimeBox, or None if not resolved. |
| `children` | Further Timeboxes inside this TimeBox. |
| `neighborhood_components` | Dict of neighborhood range integers mapped to sets of components neighboring the locus of this `TimeBox`. |

Methods

|  |  |
|----|----|
| [`multiplex`](#iqm.pulse.timebox.MeasureBox.multiplex "iqm.pulse.timebox.MeasureBox.multiplex") | Multiplex two MeasureBox instances together. |

Parameters:  
- **label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **atom** ([*Schedule*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule") *\|* *None*)

- **children** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")*,* *...\]*)

- **scheduling** ([*SchedulingStrategy*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy"))

- **scheduling_algorithm** ([*SchedulingAlgorithm*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm"))

- **neighborhood_components** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

- **boxes_length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **measure_components** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **additional_components** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

boxes_length*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 0*  
How many MeasureBox instances the MeasureBoxes instance this MeasureBox belongs to has (used in circuit-level multiplexing).

measure_components*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The `MeasureBoxes.measure_components` of the MeasureBoxes `self` belongs to.

additional_components*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
The `MeasureBoxes.additional_components` of the MeasureBoxes `self` belongs to.

multiplex(*other*)  
Multiplex two MeasureBox instances together.

The same as `self + other` with the neighborhood components combined.

Parameters:  
**other** ([*MeasureBox*](#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox"))

Return type:  
[*MeasureBox*](#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox")

Inheritance

![Inheritance diagram of iqm.pulse.timebox.MeasureBox](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-cdc617dcee68b0f03d0eb520afa14162e48fd0d7.png)
