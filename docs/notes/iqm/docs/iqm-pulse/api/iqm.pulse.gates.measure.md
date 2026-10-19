> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 692467f0a6f107c9fa8831419057fe53dfd53bd0c950529692571476de73434f.

# measure

Full path: iqm.pulse.gates.measure

Projective measurement in the Z basis.

Functions

|  |  |
|----|----|
| [`multiplex`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.multiplex.html#iqm.pulse.gates.measure.multiplex "iqm.pulse.gates.measure.multiplex")(sequence_of_boxes) | Multiplex several :class:`MeasureBoxes` instances together. |

Classes

|  |  |
|----|----|
| [`Component_Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Component_Measure_Constant.html#iqm.pulse.gates.measure.Component_Measure_Constant "iqm.pulse.gates.measure.Component_Measure_Constant") | Implementation of a single-component projective, dispersive measurement in the Z basis. |
| [`Fast_Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Fast_Measure_Constant.html#iqm.pulse.gates.measure.Fast_Measure_Constant "iqm.pulse.gates.measure.Fast_Measure_Constant") | Implementation of a faster measure with constant i and q waveforms. |
| [`Fast_Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Fast_Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Fast_Measure_CustomWaveforms "iqm.pulse.gates.measure.Fast_Measure_CustomWaveforms") | Measure implementation that blocks locus qubits for a shorter duration than the probes. |
| [`Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Constant.html#iqm.pulse.gates.measure.Measure_Constant "iqm.pulse.gates.measure.Measure_Constant") | Implementation of a single-component projective, dispersive measurement in the Z basis. |
| [`Measure_Constant_Qnd`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Constant_Qnd.html#iqm.pulse.gates.measure.Measure_Constant_Qnd "iqm.pulse.gates.measure.Measure_Constant_Qnd") | Implementation of a single-qubit projective, non quantum demolition, dispersive measurements in the Z basis. |
| [`Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Measure_CustomWaveforms "iqm.pulse.gates.measure.Measure_CustomWaveforms") | Base class for implementing dispersive measurement operations with custom probe pulse waveforms. |
| [`Measure_Factorizable`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Measure_Factorizable.html#iqm.pulse.gates.measure.Measure_Factorizable "iqm.pulse.gates.measure.Measure_Factorizable") | Base class for implementing a factorizable measure. |
| [`Move_Measure_Composite`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Move_Measure_Composite.html#iqm.pulse.gates.measure.Move_Measure_Composite "iqm.pulse.gates.measure.Move_Measure_Composite") | Measure implementation intended for measuring components that have no probe line. |
| [`NoAcquisition_Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_Constant.html#iqm.pulse.gates.measure.NoAcquisition_Measure_Constant "iqm.pulse.gates.measure.NoAcquisition_Measure_Constant") | Implementation of a single-qubit projective, dispersive measurement in the Z basis. |
| [`NoAcquisition_Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms.html#iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms "iqm.pulse.gates.measure.NoAcquisition_Measure_CustomWaveforms") | Base class for `measure` with custom probe IQ waveforms without any integration or acquisition. |
| [`ProbePulse_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.ProbePulse_CustomWaveforms.html#iqm.pulse.gates.measure.ProbePulse_CustomWaveforms "iqm.pulse.gates.measure.ProbePulse_CustomWaveforms") | Base class for implementing a probe line measurement pulse with custom waveforms in the I and Q channels. |
| [`QBBias_Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.QBBias_Measure_Constant.html#iqm.pulse.gates.measure.QBBias_Measure_Constant "iqm.pulse.gates.measure.QBBias_Measure_Constant") | Implementation of a measure with an additional fast flux voltage pulse to bias the measured qubit. |
| [`QBBias_Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.QBBias_Measure_CustomWaveforms.html#iqm.pulse.gates.measure.QBBias_Measure_CustomWaveforms "iqm.pulse.gates.measure.QBBias_Measure_CustomWaveforms") | Base class of a measure with an additional fast flux voltage pulse to bias the measured qubit. |
| [`QBBias_Probe_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.QBBias_Probe_Constant.html#iqm.pulse.gates.measure.QBBias_Probe_Constant "iqm.pulse.gates.measure.QBBias_Probe_Constant") | Implementation of a measure like QBBias_Measure_Constant, but without obtaining data from it. |
| [`Shelved_Measure_Constant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Shelved_Measure_Constant.html#iqm.pulse.gates.measure.Shelved_Measure_Constant "iqm.pulse.gates.measure.Shelved_Measure_Constant") | Implementation of a shelved readout. |
| [`Shelved_Measure_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms.html#iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms "iqm.pulse.gates.measure.Shelved_Measure_CustomWaveforms") | Base class for shelved readout. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.measure](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-62e4ad3ac8ec7501718024901229c59e578a07a3.png)
