> Full piece: [https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/)
> Retrieved 2026-10-16T22:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 018ce1be6fff7ea54ddb8b2d9dcc60e61d630d6e50feeae9260791e2e039e1bc.

# cQASM: Single Gate Multiple-Qubits

## Single Gate Multiple-Qubits (SGMQ notation)

Sometimes it is necessary to apply the same gate to multiple qubits. Instead of writing a single line for each of the qubits, cQASM allows multiple qubits to be addressed in a single statement.

The cQASM specification provides [detailed information about the semantics and syntax of the SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html). You can refer to a full qubit register, a slice thereof or pass a list of indices.

SGMQ notation works both for single-qubit instructions and multi-qubit instructions. For multi-qubit instructions the number of qubit indices must be the same for all arguments. Indices do not need to be unique as long as multi-qubit instructions do not refer to identical qubits (though they may not always be visualized correctly in the editor, since it will try to put SGMQ instructions all in the same 'column'.

Below a few examples of allowed constructions:

Close

## Export visualization

File format SVG PNG

Layout Horizontal Vertical

Theme Light Dark

Download

Export
