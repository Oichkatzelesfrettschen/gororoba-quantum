> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c408cec26d0a01e20bcb153b76a191041163df95527d4e90fee5243e9ffa1a2f.

# coupler_move

Full path: iqm.pulse.gates.coupler_move

Qubit-coupler move gate.

Population exchange operation between a qubit and a coupler directly.

- COUPLER_MOVE is unitary.

- COUPLER_MOVE is an involution up to a phase on the target subspace \\S = \text{Span}(\|00\rangle,\|01\rangle,\|10\rangle)\\, and introduces a relative phase to the ground state.

In the target subspace, COUPLER_MOVE can be represented as

\\\text{COUPLER_MOVE}\_{S} = \|00\rangle \langle 00\| + e^{i\phi} \|10\rangle \langle 01\| + e^{i\phi}\|01\rangle \langle 10\|\\

Behaviour in the subspace orthogonal to the target subspace S (including the \\\|11\rangle\\ state) is not defined, although is excitation number preserving. The phase \\\phi\\ is *not* cancelled when applied a second time and is left uncontrolled. For applications where this is important it should be determined by sweeping the phase of the final pulses.

Functions

|  |  |
|----|----|
| [`coupler_flux_locus_mapping`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.coupler_flux_locus_mapping.html#iqm.pulse.gates.coupler_move.coupler_flux_locus_mapping "iqm.pulse.gates.coupler_move.coupler_flux_locus_mapping")(sp) | Get custom locus mapping for this GateImplementation. |
| [`coupler_qubit_flux_locus_mapping`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping.html#iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping "iqm.pulse.gates.coupler_move.coupler_qubit_flux_locus_mapping")(sp) | Get custom locus mapping for this GateImplementation. |

Classes

|  |  |
|----|----|
| [`CouplerMOVEGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVEGate.html#iqm.pulse.gates.coupler_move.CouplerMOVEGate "iqm.pulse.gates.coupler_move.CouplerMOVEGate") | Two component coupler_move gate implemented using flux pulse and the interaction mediated by the coupler. |
| [`CouplerMOVE_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVE_CRF.html#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF") | COUPLER_MOVE gate using CRF on coupler only. |
| [`CouplerMOVE_CRF_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.CouplerMOVE_CRF_CRF.html#iqm.pulse.gates.coupler_move.CouplerMOVE_CRF_CRF "iqm.pulse.gates.coupler_move.CouplerMOVE_CRF_CRF") | COUPLER_MOVE gate using CRF on both qubit and coupler. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.coupler_move](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-2665e6b1b99c36fd888bbcdc530c72e977134798.png)
