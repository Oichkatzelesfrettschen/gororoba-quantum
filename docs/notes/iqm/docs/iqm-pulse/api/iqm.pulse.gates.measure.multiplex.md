> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.multiplex.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.multiplex.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a2ef8a98f4db3d854e3b65123c63d71848a4336403c41baf153cf875b749d772.

# iqm.pulse.gates.measure.multiplex

iqm.pulse.gates.measure.multiplex(*sequence_of_boxes*)  
Multiplex several :class:`MeasureBoxes` instances together.

Iterates through `sequence_of_boxes` and reduces them into a single `MeasureBoxes` instance via `MeasureBoxes.multiplex()`. Implements an as soon as possible (ASAP) algorithm for creating the minimal length `MeasureBoxes` instance while adhering to multiplexing rules.

Starting from the `sequence_of_boxes`, denoted with `[S0, S1, ..., Sm]`, we try to multiplex `S0` and `S1` together, then add `S2` and so on. Continuing like this, the multiplexed result is denoted as `M0`. If some member `Sk` of `sequence_of_boxes` cannot be multiplexed into `M0`, we keep it as is and denote it with `M1`. We then try to multiplex the next member of `sequence_of_boxes`, `Sk+1`, with `M0` and if that is not possible, with `M1`, and if that also fails, we store it as `M2`. Iterating over `sequence_of_boxes`, we thus obtain a new sequence of `MeasureBoxes`, `[M0, M1, ... Mn]`, where each member of the original sequence is executed ASAP. In the optimal case, this is just a single `MeasureBoxes` instance `M0` and in the worst case, the exact same sequence as in `sequence_of_boxes` is retained. The new sequence is then squeezed into a single `MeasureBoxes` instance by combining the last auxiliary box of `Mk` into the first auxiliary box of `Mk+1`.

Parameters:  
**sequence_of_boxes** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*MeasureBoxes*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")*\]*) – Sequence of :class:`MeasureBoxes` instances to be multiplexed together.

Returns:  
A single :class:`MeasureBoxes` instance where each member of `sequence_of_boxes` is executed ASAP.

Return type:  
[*MeasureBoxes*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.MeasureBoxes.html#iqm.pulse.timebox.MeasureBoxes "iqm.pulse.timebox.MeasureBoxes")
