> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3d39df4aa41d3d66ee96819a892367f669791f437ed9415a0b7678116928a0cf.

# prx

Full path: iqm.pulse.gates.prx

Single-qubit PRX gate.

The phased x rotation (PRX) gate is defined as

\\R\_\phi(\theta) = e^{-i (X \cos \phi + Y \sin \phi) \\ \theta/2} = R_z(\phi) R_x(\theta) R_z^\dagger(\phi),\\

where the rotation angle \\\theta\\ and the phase angle \\\phi\\ are in radians.

It rotates the qubit state around an axis that lies in the XY plane of the Bloch sphere.

Functions

|  |  |
|----|----|
| [`get_unitary_prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.get_unitary_prx.html#iqm.pulse.gates.prx.get_unitary_prx "iqm.pulse.gates.prx.get_unitary_prx")(angle, phase) | Unitary for a PRX gate. |

Classes

|  |  |
|----|----|
| [`ABC_Constant_smooth`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.ABC_Constant_smooth.html#iqm.pulse.gates.prx.ABC_Constant_smooth "iqm.pulse.gates.prx.ABC_Constant_smooth") | Base class for creating gates with an arbitrarily long Constant pulses with smooth rise and fall. |
| [`Constant_PRX_with_smooth_rise_fall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall.html#iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall "iqm.pulse.gates.prx.Constant_PRX_with_smooth_rise_fall") | Constant PRX pulse with cosine rise and fall padding. |
| [`PRX_Cosine`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_Cosine.html#iqm.pulse.gates.prx.PRX_Cosine "iqm.pulse.gates.prx.PRX_Cosine") | Special modulated pulse resulting in two frequency sidebands. |
| [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms") | Base class for PRX gates implemented using a single IQ pulse and hot-swappable waveforms. |
| [`PRX_CustomWaveformsSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveformsSX.html#iqm.pulse.gates.prx.PRX_CustomWaveformsSX "iqm.pulse.gates.prx.PRX_CustomWaveformsSX") | Base class for PRX gates implemented using SX gate, hot-swappable waveforms and phase manipulation. |
| [`PRX_DRAGCosineRiseFall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall.html#iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall "iqm.pulse.gates.prx.PRX_DRAGCosineRiseFall") | PRX gate, DRAG / CosineRiseFall IQ pulse implementation. |
| [`PRX_DRAGCosineRiseFallSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGCosineRiseFallSX.html#iqm.pulse.gates.prx.PRX_DRAGCosineRiseFallSX "iqm.pulse.gates.prx.PRX_DRAGCosineRiseFallSX") | PRX gate, DRAG / CosineRiseFall IQ pulse with VZ implementation. |
| [`PRX_DRAGGaussian`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGGaussian.html#iqm.pulse.gates.prx.PRX_DRAGGaussian "iqm.pulse.gates.prx.PRX_DRAGGaussian") | PRX gate, DRAG / TruncatedGaussian IQ pulse implementation. |
| [`PRX_DRAGGaussianSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_DRAGGaussianSX.html#iqm.pulse.gates.prx.PRX_DRAGGaussianSX "iqm.pulse.gates.prx.PRX_DRAGGaussianSX") | PRX gate, DRAG / Gaussian IQ pulse with VZ implementation. |
| [`PRX_FastDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDrag.html#iqm.pulse.gates.prx.PRX_FastDrag "iqm.pulse.gates.prx.PRX_FastDrag") | PRX gate, FAST DRAG IQ pulse based on amplitude scaling. |
| [`PRX_FastDragSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_FastDragSX.html#iqm.pulse.gates.prx.PRX_FastDragSX "iqm.pulse.gates.prx.PRX_FastDragSX") | PRX gate, FAST DRAG IQ pulse with VZ-based SX-implementation. |
| [`PRX_HdDrag`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDrag.html#iqm.pulse.gates.prx.PRX_HdDrag "iqm.pulse.gates.prx.PRX_HdDrag") | PRX gate, HD DRAG IQ pulse based on amplitude scaling. |
| [`PRX_HdDragSX`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_HdDragSX.html#iqm.pulse.gates.prx.PRX_HdDragSX "iqm.pulse.gates.prx.PRX_HdDragSX") | PRX gate, HD DRAG IQ pulse with VZ-based SX-implementation. |
| [`PRX_ModulatedCustomWaveForms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_ModulatedCustomWaveForms.html#iqm.pulse.gates.prx.PRX_ModulatedCustomWaveForms "iqm.pulse.gates.prx.PRX_ModulatedCustomWaveForms") | Base class for PRX gates with modulated frequency, hot-swappable waveforms. |
| [`PRX_ModulatedDRAGCosineRiseFall`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_ModulatedDRAGCosineRiseFall.html#iqm.pulse.gates.prx.PRX_ModulatedDRAGCosineRiseFall "iqm.pulse.gates.prx.PRX_ModulatedDRAGCosineRiseFall") | Modulated PRX pulse with cosine rise fall waveform. |
| [`PRX_Samples`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_Samples.html#iqm.pulse.gates.prx.PRX_Samples "iqm.pulse.gates.prx.PRX_Samples") | See [`PRX_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_CustomWaveforms.html#iqm.pulse.gates.prx.PRX_CustomWaveforms "iqm.pulse.gates.prx.PRX_CustomWaveforms"). |
| [`PRX_SinglePulse_GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation.html#iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation "iqm.pulse.gates.prx.PRX_SinglePulse_GateImplementation") | Base class for PRX gates implemented using a single IQ pulse. |
| [`PrxGateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.PrxGateImplementation.html#iqm.pulse.gates.prx.PrxGateImplementation "iqm.pulse.gates.prx.PrxGateImplementation") | ABC for different implementations of the PRX gate. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.prx](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e7f7aa18035a6bd8159b51f72b0591555cb22674.png)
