> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 1915745f4f06b7d95c78f078307a5df76ef73e9fddde3386d9cdfec48e62aec4;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Standard gate set

Find below an overview of [unitary instructions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html) that are explicitly defined in the language, *i.e.* the *named gates*, that comprise the cQASM ***standard gate set***. Click on the *Name* of the gate for a more detailed description.

| Name | Identifier | Operator | Example statement |
|----|----|----|----|
| [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) | H | $`H`$ | **`H q[0]`** |
| [Identity](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_I.html) | I | $`I`$ | **`I q[0]`** |
| [Pauli-X](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html) | X | $`X`$ | **`X q[0]`** |
| [Pauli-Y](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Y.html) | Y | $`Y`$ | **`Y q[0]`** |
| [Pauli-Z](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z.html) | Z | $`Z`$ | **`Z q[0]`** |
| [X90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X90.html) | X90 | $`X^{1/2}`$ | **`X90 q[0]`** |
| [minus-X90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mX90.html) | mX90 | $`X^{-1/2}`$ | **`mX90 q[0]`** |
| [Y90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X90.html) | Y90 | $`Y^{1/2}`$ | **`Y90 q[0]`** |
| [minus-Y90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mX90.html) | mY90 | $`Y^{-1/2}`$ | **`mY90 q[0]`** |
| [Z90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z90.html) | Z90 | $`Z^{1/2}`$ | **`Z90 q[0]`** |
| [minus-Z90](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mZ90.html) | mZ90 | $`Z^{-1/2}`$ | **`mZ90 q[0]`** |
| [S](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_S.html) | S | $`S`$ | **`S q[0]`** |
| [S-dagger](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Sdag.html) | Sdag | $`S^\dagger`$ | **`Sdag q[0]`** |
| [T](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_T.html) | T | $`T`$ | **`T q[0]`** |
| [T-dagger](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Tdag.html) | Tdag | $`T^\dagger`$ | **`Tdag q[0]`** |
| [Rx](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rx.html) | Rx | $`R_x(\theta)`$ | **`Rx(pi) q[0]`** |
| [Ry](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Ry.html) | Ry | $`R_y(\theta)`$ | **`Ry(pi) q[0]`** |
| [Rz](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rz.html) | Rz | $`R_z(\theta)`$ | **`Rz(pi) q[0]`** |
| [Rn](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html) | Rn | $`R_\hat{\mathbf{n}}(\hat{\mathbf{n}},\theta,\phi)`$ | **`Rn(1,0,0,pi,pi/2) q[0]`** |
| [U](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_U.html) | U | $`U(\theta, \phi, \lambda)`$ | **`U(pi/2,0,pi) q[0]`** |
| [Controlled-NOT](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html) | CNOT | $`CNOT`$ | **`CNOT q[0], q[1]`** |
| [C-Phase](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CZ.html) | CZ | $`CZ`$ | **`CZ q[0], q[1]`** |
| [CR](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CR.html) | CR | $`CR(\theta)`$ | **`CR(pi) q[0], q[1]`** |
| [CRk](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html) | CRk | $`CR_k(k)`$ | **`CRk(2) q[0], q[1]`** |
| [CV](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CV.html) | CV | $`CV`$ | **`CV q[0], q[1]`** |
| [CY](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CY.html) | CY | $`CY`$ | **`CY q[0], q[1]`** |
| [Double-CNOT](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_DCNOT.html) | DCNOT | $`DCNOT`$ | **`DCNOT q[0], q[1]`** |
| [Echoed Cross-Resonance](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ECR.html) | ECR | $`ECR`$ | **`ECR q[0], q[1]`** |
| [Inverse-square-root-SWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.html) | InvSqrtSWAP | $`\sqrt{SWAP}^\dagger`$ | **`InvSqrtSWAP q[0], q[1]`** |
| [iSWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ISWAP.html) | ISWAP | $`iSWAP`$ | **`ISWAP q[0], q[1]`** |
| [Magic](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_M.html) | M | $`M`$ | **`M q[0], q[1]`** |
| [Mølmer-Sørensen](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_MS.html) | MS | $`MS`$ | **`MS q[0], q[1]`** |
| [Square-root-iSWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SqrtISWAP.html) | SqrtISWAP | $`\sqrt{iSWAP}`$ | **`SqrtISWAP q[0], q[1]`** |
| [Square-root-SWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SqrtSWAP.html) | SqrtSWAP | $`\sqrt{SWAP}`$ | **`SqrtSWAP q[0], q[1]`** |
| [SWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SWAP.html) | SWAP | $`SWAP`$ | **`SWAP q[0], q[1]`** |
| [Toffoli](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CCX.html) | CCX | $`CCX`$ | **`CCX q[0], q[1], q[2]`** |
| [Fredkin](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CSWAP.html) | CSWAP | $`CSWAP`$ | **`CSWAP q[0], q[1], q[2]`** |
