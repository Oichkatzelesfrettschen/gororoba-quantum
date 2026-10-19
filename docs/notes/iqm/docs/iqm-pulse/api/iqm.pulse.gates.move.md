> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 22e62e92edc28d24d49cd94d7537d2eed1bd3ea32133e86681c52260e2ece78f.

# move

Full path: iqm.pulse.gates.move

Two-qubit MOVE gate.

The MOVE gate is a population exchange operation between two components, mediated by a coupler, that has the following properties:

- MOVE is unitary.

- The effect of MOVE is only defined in the invariant subspace \\S = \text{span}\\\|00\rangle, \|01\rangle, \|10\rangle\\\\, where it swaps the populations of the states \\\|01\rangle\\ and \\\|10\rangle\\. Anything may happen in the orthogonal subspace as long as it is unitary and invariant.

- In the subspace where it is defined, MOVE is an involution: \\\text{MOVE}\_S^2 = I_S\\.

Thus MOVE has the following presentation in the subspace \\S\\:

\\\text{MOVE}\_S = \|00\rangle \langle 00\| + a \|10\rangle \langle 01\| + a^{-1} \|01\rangle \langle 10\|,\\

where \\a\\ is an undefined complex phase. This degree of freedom (in addition to the undefined effect of the gate in the orthogonal subspace) means there is a continuum of different MOVE gates, all equally valid. The phase \\a\\ is canceled when the MOVE gate is applied a second time due to the involution property.

Functions

|  |  |
|----|----|
| [`apply_move_gate_phase_corrections`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.apply_move_gate_phase_corrections.html#iqm.pulse.gates.move.apply_move_gate_phase_corrections "iqm.pulse.gates.move.apply_move_gate_phase_corrections")(schedule, ...) | Schedule-level pass applying phase corrections for MOVE sandwiches to the first MOVE component. |
| [`validate_move_instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.validate_move_instructions.html#iqm.pulse.gates.move.validate_move_instructions "iqm.pulse.gates.move.validate_move_instructions")(instructions, builder) | Circuit-level pass to prepare a circuit containing MOVE gates for compilation. |

Classes

|  |  |
|----|----|
| [`MOVE_CRF_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CRF_CRF.html#iqm.pulse.gates.move.MOVE_CRF_CRF "iqm.pulse.gates.move.MOVE_CRF_CRF") | MOVE gate using CRF waveform for the coupler and the qubit flux pulses. |
| [`MOVE_CustomWaveforms`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_CustomWaveforms.html#iqm.pulse.gates.move.MOVE_CustomWaveforms "iqm.pulse.gates.move.MOVE_CustomWaveforms") | Qubit-resonator or qubit-qubit MOVE gate using flux pulses both on a qubit and the coupler. |
| [`MOVE_SLEPIAN_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_SLEPIAN_CRF.html#iqm.pulse.gates.move.MOVE_SLEPIAN_CRF "iqm.pulse.gates.move.MOVE_SLEPIAN_CRF") | MOVE gate using Slepian waveform for the coupler flux pulse and CRF waveform for the qubit flux pulse. |
| [`MOVE_TGSS_CRF`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MOVE_TGSS_CRF.html#iqm.pulse.gates.move.MOVE_TGSS_CRF "iqm.pulse.gates.move.MOVE_TGSS_CRF") | MOVE gate using TGSS waveform for the coupler flux pulse and CRF waveform for the qubit flux pulse. |
| [`MoveMarker`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.MoveMarker.html#iqm.pulse.gates.move.MoveMarker "iqm.pulse.gates.move.MoveMarker") | Special annotation instruction to indicate the beginning and ending of MOVE gates. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.move](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-37d65bafbaf1d8ca2bf6cb6fb7df0413c6b10c03.png)
