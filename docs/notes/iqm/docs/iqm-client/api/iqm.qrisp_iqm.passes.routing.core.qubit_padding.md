> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b5cca8269458e1875bf0a670e059817e35718463ebd9e493ba547cb237ee8345.

# qubit_padding

Full path: iqm.qrisp_iqm.passes.routing.core.qubit_padding

Helpers for padding a circuit out to the device qubit count.

Layout passes map the circuit onto a device topology that usually holds more qubits than the circuit uses. The missing qubits are appended as *padding* qubits named `f"padding_qb_{counter}"`.

Because several passes can run one after another (e.g. `manual_layout` followed by `plasma_layout`), a pass must not restart the counter at zero: the incoming circuit may already carry padding qubits from an earlier pass, and reusing a name raises a ValueError. [`pad_qubits()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits.html#iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits "iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits") therefore continues the numbering where the incoming circuit left off.

Module Attributes

|  |  |
|----|----|
| [`PADDING_QUBIT_PREFIX`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.PADDING_QUBIT_PREFIX.html#iqm.qrisp_iqm.passes.routing.core.qubit_padding.PADDING_QUBIT_PREFIX "iqm.qrisp_iqm.passes.routing.core.qubit_padding.PADDING_QUBIT_PREFIX") | Name prefix of the qubits the layout passes append as padding. |

Functions

|  |  |
|----|----|
| [`next_padding_qubit_index`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index.html#iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index "iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index")(qc) | First padding-qubit counter value that is free in `qc`. |
| [`pad_qubits`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits.html#iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits "iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits")(qc, n_qubits) | Pad a quantum circuit in-place until it holds the given number of qubits. |
