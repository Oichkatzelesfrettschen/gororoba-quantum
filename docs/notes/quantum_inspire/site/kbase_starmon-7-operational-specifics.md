> Full piece: [https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 503459e2f7709c0ad799a82ffc47b52b76d6f403118073054583983c501103a2.

# Starmon-7: Operational specifics

## Starmon-7 : Topology and allowed gate set

Each of the quantum processors has a specific topology (the way the qubits are connected) and a specific allowed gate set (supported qubit operations).

Starmon-7 consists of seven qubits (Q0-Q6). This device connectivity resembles two rhombi with qubits on all vertices and qubit couplers on all edges. The two rhombi share a common vertex, the central qubit (Q3).

![](https://www.datocms-assets.com/119587/1766432737-starmon-7_schematic.svg)

You can execute the following operaitons on this system (native operations are given in **bold**, other operations are decomposed using decomposition rules specific for this quantum processor):

- Single-qubit gates:

  - **`X`**, **`Y`**, **`Z`**, **`I`**
  - **`Rx(angle)`**, **`Ry(angle)`**, `Rz(angle)`
  - **`X90`**, **`Y90`**, **`mX90`**, **`mY90`**
  - `H`
  - **`S`**, **`Sdag`**, **`T`**, **`Tdag`**

  Note: The angles of single-qubit x, y, and z rotations are quantized to the nearest multiple of pi/28.

- Two-qubit gates:

  - **`CZ`**, `CNOT`, `SWAP`

- Non-unitary operations:

  - **`init`**, **`measure`**, **`reset`**

  Note: the Tuna backends allow mid-circuit measurements.

The following operations and commands are *not* allowed:

- `CR`, `CRk`
- `Display`
- `Display_binary`
- `Not`
- Binary controlled operations `c-`
- `Toffoli`\*

The angles of single-qubit arbitrary rotations are quantized to the nearest multiple of pi/28.

The Starmon-7 allows mid-circuit measurements.

## Scheduling user programs: wait/barrier instructions

Programs submitted to Starmon-7 undergo a step of scheduling upon compilation using QuTech’s OpenQL. During scheduling, the operations defined in the user program are rearranged in time according to an as-late-as-possible (ALAP) strategy, in such a way as to execute gates on qubits as late in the sequence of instructions specified by the user, as possible. Scheduling takes into account the duration of various native operations (20 ns for single-qubit gates, 60 ns for CZ gates, 1 us for measurements, and 150 us for initialization) and various other hardware constraints that are detailed in the factsheet of Starmon-7.

Users can influence the scheduling of a program through the `barrier` and `wait` instructions. The `wait` instruction allows a user to specify how many cycles a qubit should be idled. The instruction takes as arguments a qubit target (q\[6\] or q\[0:6\], for example) and the number of cycles (in steps of 20 ns) that the target should be left idling. Please note that `wait` instructions applied on multiple qubits are scheduled independently for each qubit.

The `barrier` instruction is an operation that prevents any optimization or commutation through. Therefore, the instruction can be used to define a scheduling domain within which ALAP scheduling will also take place. The barrier acts as an *n*-qubit identity gate with zero duration that only applies to the qubits it operates on.

## Compiling user programs: gate decomposition and quantization

Programs submitted to Starmon-7 undergo a step of gate decomposition and quantization u using QuTech’s [OpenQL](https://openql.readthedocs.io/en/latest/gen/reference_passes.html#list-scheduler) compiler. Non-native gate operations are decomposed, affecting their overall duration. Furthermore, native gate operations resulting from decomposition are still subject to scheduling according to the rules detailed above. For a detailed description of the non-native operations supported in the backend, and their respective decompositions, please refer to the factsheet for Starmon-7.

## Result format: parallel and sequential measurements

The result format strictly depends on the structure of measurements programmed by the user. Therefore, results are organized in a 2-dimensional array where the outer-most dimension encodes the various shots of a circuit requested by the user, the second dimension encodes the qubit measurement outcomes in the order specified in the classical bit register.

Measurements performed on multiple-qubit targets (q\[0:6\], for example) are still subject to scheduling. Therefore, `barrier` instructions should be used when trying to ensure that measurements are performed in parallel.

[Previous](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/) [Next](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/)
