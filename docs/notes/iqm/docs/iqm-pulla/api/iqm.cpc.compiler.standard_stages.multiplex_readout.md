> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.multiplex_readout.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.multiplex_readout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 962bf880fe8c6b67c2255a9b0ec37ecf83dd8a90188190784718fbbfd7b43502.

# iqm.cpc.compiler.standard_stages.multiplex_readout

iqm.cpc.compiler.standard_stages.multiplex_readout(*timeboxes*, *timebox_input*)  
Merge any MultiplexedProbeTimeBoxes inside a TimeBox representing a circuit.

This pass optimizes a situation where multiple “measure” gates on disjoint set of loci exist sequentially in the circuit. Without optimization, each gate would result in a separate trigger event, which results in worse performance. For example, with the measurement instructions \[M(QB1), M(QB2), M(QB3)\], we’d first measure QB1, then QB2, then QB3. This optimization merges the measurement timeboxes, so that we’ll measure QB1, QB2, and QB3 at the same time (if the hardware channel configuration allows it), corresponding to M(QB1, QB2, QB3).

Goes through the children of circuit_box, and places them in the same temporal order. Whenever a MultiplexedProbeTimeBox is encountered (i.e. from a measure gate), it is merged with the previous pending MultiplexedProbeTimeBox and left pending. If any other box type with colliding loci is encountered, first places the pending MultiplexedProbeTimeBox. This essentially delays all measurements until the last possible moment.

This stage pass is skipped if the circuits to be compiled were given in the TimeBox-level, as the logic within does not work for deep recursive TimeBoxes.

Parameters:  
- **timeboxes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")*\]*) – Timeboxes representing circuits.

- **timebox_input** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the circuits were inputted already in the TimeBox format.

Returns:  
New TimeBoxes with the same content, except with some MultiplexedProbeTimeBoxes merged.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")\]
