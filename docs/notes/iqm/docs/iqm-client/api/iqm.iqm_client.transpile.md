> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 24d9bd0895c1fcbd5e47be4086a275a74f78bbaa225a3c92d283d8803436bf53.

# transpile

Full path: iqm.iqm_client.transpile

Transpiling circuits to IQM devices involving computational resonators.

In the IQM Star architecture, computational resonators are connected to multiple qubits. A MOVE gate can be used to move the state of a qubit to a connected, empty computational resonator, and back *to the same qubit*. Additionally, two-component gates like CZ can be applied between a qubit and a connected resonator, so that effectively the qubit can be made to interact with other qubits connected to the resonator. However, the resonators cannot be measured, and no single-qubit gates can be applied on them.

To enable third-party transpilers to work on the IQM Star architecture, we may abstract away the resonators and replace the real dynamic quantum architecture with a *simplified architecture*. Specifically, this happens by removing the resonators from the architecture, and for each resonator `r`, and for each pair of supported native qubit-resonator (QR) gates `(G(q1, r), MOVE(q2, r))` adding the *fictional* gate `G(q1, q2)` to the simplified architecture. This works since the fictional gate can be implemented as the QR gate sequence

```
G(q1, q2) = [MOVE(q2, r), G(q1, r), MOVE(q2, r)].
```

This sequence is called a *resolution* of `G(q1, q2)`. Currently we assume all the QR gates (other than MOVE) are symmetric in the sense that

```
[MOVE(q2, r), G(q1, r), MOVE(q2, r)] = G(q1, q2) = G(q2, q1) = [MOVE(q1, r), G(q2, r), MOVE(q1, r)]
```

holds. This has the effect of doubling the number of possible resolutions for `G(q1, q2)` since you can reverse the roles of the qubits.

Before a circuit transpiled to a simplified architecture can be executed it must be further transpiled to the real Star architecture using [`transpile_insert_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html#iqm.iqm_client.transpile.transpile_insert_moves "iqm.iqm_client.transpile.transpile_insert_moves"), which will introduce the resonators, add MOVE gates as necessary to move the states, and convert the fictional two-qubit gates into real native gates acting on qubit-resonator pairs.

Likewise [`transpile_remove_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html#iqm.iqm_client.transpile.transpile_remove_moves "iqm.iqm_client.transpile.transpile_remove_moves") can be used to perform the opposite transformation, converting a circuit valid for the real Star architecture into an equivalent circuit for the corresponding simplified architecture, e.g. so that the circuit can be retranspiled or optimized using third-party tools that do not support the MOVE gate.

Given a `DynamicQuantumArchitecture` for a Star architecture, the corresponding simplified version can be obtained using [`simplify_architecture()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.simplify_architecture.html#iqm.iqm_client.transpile.simplify_architecture "iqm.iqm_client.transpile.simplify_architecture").

Module Attributes

|  |  |
|----|----|
| [`Resolution`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.Resolution.html#iqm.iqm_client.transpile.Resolution "iqm.iqm_client.transpile.Resolution") | A (gate qubit, move qubit, resonator) triple that represents a resolution of a fictional qubit-qubit gate. |

Functions

|  |  |
|----|----|
| [`simplify_architecture`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.simplify_architecture.html#iqm.iqm_client.transpile.simplify_architecture "iqm.iqm_client.transpile.simplify_architecture")(arch, \*\[, ...\]) | Converts the given IQM Star quantum architecture into the equivalent simplified quantum architecture. |
| [`transpile_insert_moves`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html#iqm.iqm_client.transpile.transpile_insert_moves "iqm.iqm_client.transpile.transpile_insert_moves")(circuit, arch, \*\[, ...\]) | Convert a simplified architecture circuit into an equivalent Star architecture circuit. |
| [`transpile_remove_moves`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html#iqm.iqm_client.transpile.transpile_remove_moves "iqm.iqm_client.transpile.transpile_remove_moves")(circuit) | Convert a Star architecture circuit into an equivalent simplified architecture circuit. |

Classes

|  |  |
|----|----|
| [`ExistingMoveHandlingOptions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") | Options for how [`transpile_insert_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html#iqm.iqm_client.transpile.transpile_insert_moves "iqm.iqm_client.transpile.transpile_insert_moves") should handle existing MOVE instructions in the circuit. |

Inheritance

![Inheritance diagram of iqm.iqm_client.transpile](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-32c3ffa4a69fc2d9c3b86ed597d75b8120c79d22.png)
