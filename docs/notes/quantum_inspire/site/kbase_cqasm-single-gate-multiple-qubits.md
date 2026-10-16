> Full piece: [https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 6e067abc8530ac1e8e7c477e1a66f7cc6c9c7035d61f7a5ecf0ecb7fcab16c95.

# cQASM: Single Gate Multiple-Qubits

## Single Gate Multiple-Qubits (SGMQ notation)

Sometimes it is necessary to apply the same gate to multiple qubits. Instead of writing a single line for each of the qubits, cQASM allows multiple qubits to be addressed in a single statement.

The cQASM specification provides [detailed information about the semantics and syntax of the SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html). You can refer to a full qubit register, a slice thereof or pass a list of indices.

SGMQ notation works both for single-qubit instructions and multi-qubit instructions. For multi-qubit instructions the number of qubit indices must be the same for all arguments. Indices do not need to be unique as long as multi-qubit instructions do not refer to identical qubits (though they may not always be visualized correctly in the editor, since it will try to put SGMQ instructions all in the same 'column'.

Below a few examples of allowed constructions:

```cqasm
version 3.0
qubit[8] q
bit[8] b

//The following SGMQ constructions are allowed

X q[0,2:3] //single-qubit unitary instructions
CRk(2) q[0,2,4,6],q[1,3,5,7] //...with parameters
Z q[0:3, 5:7] //slices
CNOT q[0,1],q[2,3] //two-qubit instructions

H q[0,0,0] //will unpack as 3 times H q[0], but not correctly visualized (overlap)
CNOT q[0,1,0], q[1,0,1] //will unpack as three CNOTs and is equivalent to a SWAP operation, but not correctly visualized (overlap)

b[0:7] = measure q[0:7] //non-unitary instructions
```
