> Full piece: [https://www.quantum-inspire.com/kbase/tuna-operational-specifics/](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 afe0a9be22eb5065a01d78c190993381f13ce1588e4d011c542e2ca658e0c2e4.

# Tuna backends: Operational specifics

## Tuna backends : Topology and allowed gate set

Each of the quantum processors has a specific topology (the way the qubits are connected) and a specific allowed gate set (supported qubit operations).

Tuna-5 consists of five qubits (Q0-Q4) in a starfish configuration with Q2 at the center. ![](https://www.datocms-assets.com/119587/1766393003-tuna-5_schematic.svg)

Tuna-9 consists of nine qubits (Q0-Q8) in a diamond-like configuration, with Q4 at the center. ![](https://www.datocms-assets.com/119587/1766393015-tuna-9_schematic.svg)

Tuna-17 consists of 17 qubits (Q0-Q16) in a ninja-star configuration. ![](https://www.datocms-assets.com/119587/1772648307-tuna-17_schematic-svg.svg)

You can execute the following operations on Tuna backends. Native operations - that is, operations that require a single instruction on control hardware - are given in **bold**, while other allowed operations are decomposed using specific decomposition rules for this quantum processor:

- Single-qubit gates:

  - **`Rx(angle)`**, **`Ry(angle)`**, **`Rz(angle)`**, `Rn(angle)`
  - **`X90`**, **`Y90`**, **`mX90`**, **`mY90`**
  - **`X`**, **`Y`**, **`Z`**, **`I`**
  - `H`
  - **`S`**, **`Sdag`**, **`T`**, **`Tdag`**

  Note: The angles of single-qubit x, y, and z rotations are quantized to the nearest multiple of pi/36.

- Two-qubit gates:

  - **`CZ`**,
  - `CNOT`,
  - `CR`, `CRk`
  - `SWAP`

- Non-unitary operations:

  - **`init`**, **`measure`**, **`reset`**

  Note: the Tuna backends allow mid-circuit measurements.

The following operations and commands are *not* allowed on Tuna backends:

- `Display`
- `Display_binary`
- `Not`
- Binary controlled operations `c-`
- `Toffoli`

## Scheduling user programs: wait/barrier instructions

Programs submitted to Tuna backends undergo a step of scheduling upon compilation using QuTech’s OpenSquirrel. During scheduling, the operations defined in the user program are rearranged in time according to an as-late-as-possible (ALAP) strategy, in such a way as to execute gates on qubits as late in the sequence of instructions specified by the user, as possible. Scheduling takes into account the duration of operations (20 ns native single-qubit gates, 60 ns for CZ gates, 800 ns for measurements, and 500 or 200 µs for initialization), and hardware constraints such as qubit-qubit connectivity.

Users can influence the scheduling of a program through the `barrier` and `wait` instructions. The `wait` is a control instruction that allows a user to constrain the optimization of a scheduler by delaying subsequent instructions on the specified qubit(s) by a given time. The instruction takes as arguments a qubit target (q\[4\] or q\[0:4\], for example) and the number of cycles (in steps of 20 ns) that the target should idle. Please note that `wait` instructions applied on multiple qubits are scheduled independently for each qubit. For further details on the `wait` instruction in cQASM, the user is referred to [cQASM documentation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html).

The `barrier` instruction is a control instruction that allows a user to constrain optimization of a scheduler by preventing scheduling of instructions on specified qubit(s) across the barrier. Therefore, the instruction can be used to define a scheduling domain within which ALAP scheduling will also take place. For further details on the `barrier` instruction in cQASM, the user is referred to [cQASM documentation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html).

For more details on scheduling within OpenSquirrel, please refer to [OpenSquirrel](https://qutech-delft.github.io/OpenSquirrel/)

## Compiling user programs: gate decomposition

Programs submitted to Tuna backends undergo a step of gate decomposition upon compilation using OpenSquirrel. Non-native gate operations are decomposed, affecting their overall duration. Furthermore, native gate operations resulting from decomposition are scheduled using [quantify](https://quantify-os.org/) scheduler. For a detailed description of the non-native operations supported in the backend, and their respective decompositions, please refer to the factsheet for specific processors. Finally, single-qubit arbitrary rotations are quantized to the nearest multiple of π/36 radians (5°).

## Result format: parallel and sequential measurements

The result format strictly depends on the structure of measurements programmed by the user. Therefore, results are organized in a 2-dimensional array where the outer-most dimension encodes the various shots of a circuit requested by the user, and the second dimension encodes the qubit measurement outcomes with the same order as specified in the classical bit register. The user has full control on the mapping of qubits measurements to classical bits in the register.

Measurements performed on multiple-qubit targets (q\[0:4\], for example) are still subject to scheduling. Therefore, the `barrier` instructions should be used when trying to ensure that measurements are performed in parallel.

[Previous](https://www.quantum-inspire.com/kbase/hardware-backends/) [Next](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/)
