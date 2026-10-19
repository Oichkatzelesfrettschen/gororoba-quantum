> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eb6e7d0b78ff11450c7b26ef781dbe47406fd40f2a36ebac3bcf3ec601d62755.

# cz

Full path: iqm.pulse.gates.cz

Two-qubit controlled-Z (CZ) gate.

The CZ gate flips the relative phase of the \\\|11⟩\\ state. It can be represented by the unitary matrix

\\\begin{split}\text{CZ} = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & -1 \end{pmatrix}\end{split}\\

Functions

|  |  |
|----|----|
| [`round_to_granularity`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.round_to_granularity.html#iqm.pulse.gates.cz.round_to_granularity "iqm.pulse.gates.cz.round_to_granularity")(value, granularity\[, ...\]) | Round a value to the nearest multiple of granularity. |
| [`split_flat_top_part_into_granular_parts`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts.html#iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts "iqm.pulse.gates.cz.split_flat_top_part_into_granular_parts")(...) | Split a flat-top pulse into three consecutive parts (rise, flat, and fall) to save waveform memory. |

Classes

|  |  |
|----|----|
| [`CZ_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_CRF.html#iqm.pulse.gates.cz.CZ_CRF "iqm.pulse.gates.cz.CZ_CRF") | CZ gate using a CosineRiseFall flux pulse on the coupler. |
| [`CZ_CRF_ACStarkCRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF.html#iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF "iqm.pulse.gates.cz.CZ_CRF_ACStarkCRF") | Controlled-Z two-qubit gate. |
| [`CZ_GaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare.html#iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare "iqm.pulse.gates.cz.CZ_GaussianSmoothedSquare") | CZ gate using a GaussianSmoothedSquare flux pulse on the coupler. |
| [`CZ_Slepian`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_Slepian.html#iqm.pulse.gates.cz.CZ_Slepian "iqm.pulse.gates.cz.CZ_Slepian") | CZ gate using a Slepian flux pulse on the coupler. |
| [`CZ_Slepian_ACStarkCRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_Slepian_ACStarkCRF.html#iqm.pulse.gates.cz.CZ_Slepian_ACStarkCRF "iqm.pulse.gates.cz.CZ_Slepian_ACStarkCRF") | Controlled-Z two-qubit gate. |
| [`CZ_Slepian_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_Slepian_CRF.html#iqm.pulse.gates.cz.CZ_Slepian_CRF "iqm.pulse.gates.cz.CZ_Slepian_CRF") | CZ gate using a Slepian flux pulse on the coupler and a CosineRiseFall flux pulse on the qubit. |
| [`CZ_TruncatedGaussianSmoothedSquare`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CZ_TruncatedGaussianSmoothedSquare.html#iqm.pulse.gates.cz.CZ_TruncatedGaussianSmoothedSquare "iqm.pulse.gates.cz.CZ_TruncatedGaussianSmoothedSquare") | CZ gate using a TruncatedGaussianSmoothedSquare flux pulse on the coupler. |
| [`CouplerFluxPulseQubitACStarkPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate.html#iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate "iqm.pulse.gates.cz.CouplerFluxPulseQubitACStarkPulseGate") | Base class for CZ gates with coupler flux pulse and a qubit AC Stark pulse. |
| [`FluxPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate.html#iqm.pulse.gates.cz.FluxPulseGate "iqm.pulse.gates.cz.FluxPulseGate") | Base class for flux pulse gate implementations that have a flux pulse for at most one locus component. |
| [`FluxPulseGateBase`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGateBase.html#iqm.pulse.gates.cz.FluxPulseGateBase "iqm.pulse.gates.cz.FluxPulseGateBase") | Discrete arity-2 gate implemented using flux pulses, virtual RZs, and the interaction mediated by the coupler. |
| [`FluxPulseGate_CRF_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_CRF_CRF.html#iqm.pulse.gates.cz.FluxPulseGate_CRF_CRF "iqm.pulse.gates.cz.FluxPulseGate_CRF_CRF") | CZ gate using a CosineRiseFall flux pulse on the coupler and on the qubit. |
| [`FluxPulseGate_SmoothConstant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant.html#iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant "iqm.pulse.gates.cz.FluxPulseGate_SmoothConstant") | Flux pulse gate implementation which uses a 3-part pulse sequence (cosine rise, constant, cosine fall). |
| [`FluxPulseGate_TGSS_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulseGate_TGSS_CRF.html#iqm.pulse.gates.cz.FluxPulseGate_TGSS_CRF "iqm.pulse.gates.cz.FluxPulseGate_TGSS_CRF") | CZ gate using a TGSS flux pulse on the coupler and a CosineRiseFall flux pulse on the qubit. |
| [`FluxPulse_SmoothConstant_SmoothConstant`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant.html#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_SmoothConstant") | Constant flux pulse on both qubit and coupler with smooth rise/fall. |
| [`FluxPulse_SmoothConstant_coupler`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulse_SmoothConstant_coupler.html#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_coupler "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_coupler") | Constant flux pulse on coupler with smooth rise/fall. |
| [`FluxPulse_SmoothConstant_qubit`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.FluxPulse_SmoothConstant_qubit.html#iqm.pulse.gates.cz.FluxPulse_SmoothConstant_qubit "iqm.pulse.gates.cz.FluxPulse_SmoothConstant_qubit") | Constant flux pulse on qubit with smooth rise/fall. |
| [`TripleFluxPulseGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.TripleFluxPulseGate.html#iqm.pulse.gates.cz.TripleFluxPulseGate "iqm.pulse.gates.cz.TripleFluxPulseGate") | Base class for flux pulse gate implementations that have flux pulses for both locus components. |
| [`TripleFluxPulseGate_CRF_CRF_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.TripleFluxPulseGate_CRF_CRF_CRF.html#iqm.pulse.gates.cz.TripleFluxPulseGate_CRF_CRF_CRF "iqm.pulse.gates.cz.TripleFluxPulseGate_CRF_CRF_CRF") | CZ gate using a CosineRiseFall flux pulse on the coupler and on both qubits. |
| [`TripleFluxPulseGate_Slepian_CRF_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.TripleFluxPulseGate_Slepian_CRF_CRF.html#iqm.pulse.gates.cz.TripleFluxPulseGate_Slepian_CRF_CRF "iqm.pulse.gates.cz.TripleFluxPulseGate_Slepian_CRF_CRF") | CZ gate using a Slepian flux pulse on the coupler and CosineRiseFall flux pulse on both qubits. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.cz](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-7b3a63fc5499aab3a9ec5973ee37878ef2121a54.png)
