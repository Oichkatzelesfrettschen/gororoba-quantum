> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 45d997cc8c96cce9f6188464185daae1d36236bfac69b9b6313144e852c50645.

# gates

Full path: iqm.pulse.gates

Implementations of quantum gates.

The [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") subclasses in this subpackage construct [`TimeBox`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") instances to implement specific native gates, using the calibration data that the class has been initialized with. Each GateImplementation instance encapsulates the calibration data for a specific implementation of a specific native gate acting on a specific locus.

Several different implementations and calibration schemes can be supported for a given gate, each represented by its own GateImplementation subclass. Likewise, a single GateImplementation subclass can be sometimes used to implement several different gates through different calibration data.

Functions

|  |  |
|----|----|
| [`expose_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.expose_implementation.html#iqm.pulse.gates.expose_implementation "iqm.pulse.gates.expose_implementation")(implementation\[, ...\]) | Add the given gate implementation to the list of known implementations. |
| [`get_implementation_class`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.get_implementation_class.html#iqm.pulse.gates.get_implementation_class "iqm.pulse.gates.get_implementation_class")(class_name) | Get gate implementation class by class name. |
| [`register_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_implementation.html#iqm.pulse.gates.register_implementation "iqm.pulse.gates.register_implementation")(operations, op_name, ...) | Register a new GateImplementation. |
| [`register_operation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.register_operation.html#iqm.pulse.gates.register_operation "iqm.pulse.gates.register_operation")(operations, op\[, overwrite\]) | Register a new QuantumOp to the given operations table. |

Subpackages and modules

|  |  |
|----|----|
| [`barrier`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.html#module-iqm.pulse.gates.barrier "iqm.pulse.gates.barrier") | Barrier metaoperation. |
| [`conditional`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.html#module-iqm.pulse.gates.conditional "iqm.pulse.gates.conditional") | Classically controlled gates. |
| [`coupler_move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.coupler_move.html#module-iqm.pulse.gates.coupler_move "iqm.pulse.gates.coupler_move") | Qubit-coupler move gate. |
| [`cz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.cz.html#module-iqm.pulse.gates.cz "iqm.pulse.gates.cz") | Two-qubit controlled-Z (CZ) gate. |
| [`default_gates`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.default_gates.html#module-iqm.pulse.gates.default_gates "iqm.pulse.gates.default_gates") | Canonical quantum operations and implementations provided by iqm-pulse. |
| [`delay`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.delay.html#module-iqm.pulse.gates.delay "iqm.pulse.gates.delay") | Force a delay between instructions on the control channels of specific locus components. |
| [`drive_crosstalk`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.drive_crosstalk.html#module-iqm.pulse.gates.drive_crosstalk "iqm.pulse.gates.drive_crosstalk") | GateImplementation that holds the drive crosstalk calibration matrix and builds compensation pulses. |
| [`enums`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.enums.html#module-iqm.pulse.gates.enums "iqm.pulse.gates.enums") | Enumerations for representing a set of important one- and two-qubit gates. |
| [`flux_multiplexer`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.flux_multiplexer.html#module-iqm.pulse.gates.flux_multiplexer "iqm.pulse.gates.flux_multiplexer") | GateImplementation for correcting flux crosstalk for a given set of flux-pulse TimeBoxes. |
| [`lru`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.lru.html#module-iqm.pulse.gates.lru "iqm.pulse.gates.lru") | Qubit leakage reduction unit. |
| [`measure`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.measure.html#module-iqm.pulse.gates.measure "iqm.pulse.gates.measure") | Projective measurement in the Z basis. |
| [`move`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.html#module-iqm.pulse.gates.move "iqm.pulse.gates.move") | Two-qubit MOVE gate. |
| [`prx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.html#module-iqm.pulse.gates.prx "iqm.pulse.gates.prx") | Single-qubit PRX gate. |
| [`reset`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html#module-iqm.pulse.gates.reset "iqm.pulse.gates.reset") | Qubit reset operations. |
| [`rz`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.rz.html#module-iqm.pulse.gates.rz "iqm.pulse.gates.rz") | Single-qubit RZ gate. |
| [`sx`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.sx.html#module-iqm.pulse.gates.sx "iqm.pulse.gates.sx") | Single-qubit sqrt(X) gate. |
| [`u`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html#module-iqm.pulse.gates.u "iqm.pulse.gates.u") | Single-qubit SU(2) gate. |
