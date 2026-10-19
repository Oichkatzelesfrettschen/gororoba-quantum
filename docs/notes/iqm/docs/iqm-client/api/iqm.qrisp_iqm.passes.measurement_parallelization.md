> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.measurement_parallelization.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.measurement_parallelization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 31c9bd2ca75dade97aa89af3017824fa8db9f2784324fa6263df62647cedeb4d.

# measurement_parallelization

Full path: iqm.qrisp_iqm.passes.measurement_parallelization

Measurement Parallelization Pass.

This module provides a transpilation pass that combines consecutive measurement operations into a single multi-qubit measurement. This optimization is more efficient on IQM hardware because:

1.  Multiple single-qubit measurements can be performed simultaneously

2.  Reduces the overhead of multiple measurement calls

3.  The hardware can execute parallel readout on all specified qubits at once

The pass scans through the circuit and collects consecutive measurement instructions. When a non-measurement instruction is encountered (or at the end of the circuit), all collected measurements are flushed as a single combined multi-qubit measurement operation.

Example:

```
>>> from qrisp import QuantumCircuit
>>> from iqm.qrisp_iqm import measurement_parallelization
>>>
>>> qc = QuantumCircuit(3)
>>> qc.h(0)
>>> qc.measure([0, 1, 2])  # Three separate measurements
>>>
>>> # After parallelization, measurements become one multi-qubit operation
>>> qc_optimized = measurement_parallelization(qc)
```
