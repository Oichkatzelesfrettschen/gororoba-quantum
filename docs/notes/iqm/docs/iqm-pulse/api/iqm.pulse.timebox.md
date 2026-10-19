> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 971730bad52cbc344bb2282decdfdb3f5baf4b5de9f04f1370dcfd37d87d4761.

# timebox

Full path: iqm.pulse.timebox

Reserving QPU resources in instruction scheduling.

Classes

|  |  |
|----|----|
| [`MeasureBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBox.html#iqm.pulse.timebox.MeasureBox "iqm.pulse.timebox.MeasureBox") | TimeBox associated with a measure implementation. |
| [`MeasureBoxes`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes") | Multiplexable list of TimeBoxes associated with a measure implementation. |
| [`MultiplexedProbeTimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MultiplexedProbeTimeBox.html#iqm.pulse.timebox.MultiplexedProbeTimeBox "iqm.pulse.timebox.MultiplexedProbeTimeBox") | A `MeasureBox` for multiplexing IQ pulses in probe channels. |
| [`SchedulingAlgorithm`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingAlgorithm.html#iqm.pulse.timebox.SchedulingAlgorithm "iqm.pulse.timebox.SchedulingAlgorithm") | Algorithms for resolving composite TimeBoxes into atomic ones. |
| [`SchedulingStrategy`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.SchedulingStrategy.html#iqm.pulse.timebox.SchedulingStrategy "iqm.pulse.timebox.SchedulingStrategy") | Different scheduling strategies for the contents of composite TimeBoxes. |
| [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") | Container for one or more instruction schedule fragments, to be scheduled according to a given strategy. |

Exceptions

|  |  |
|----|----|
| [`MeasureMultiplexingError`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureMultiplexingError.html#iqm.pulse.timebox.MeasureMultiplexingError "iqm.pulse.timebox.MeasureMultiplexingError") | Error in multiplexing two `MeasureBoxes` instances together. |

Inheritance

![Inheritance diagram of iqm.pulse.timebox](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-9502f39ebd77ebdde637f2dc608b638c0655fc68.png)
