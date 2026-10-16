> Full piece: [https://github.com/QuTech-Delft/OpenSquirrel/releases](https://github.com/QuTech-Delft/OpenSquirrel/releases)
> Retrieved 2026-10-16T22:00Z by scripts/capture_qi_docs.py --releases (urllib, REST API);
> 12 releases, newest first, bodies verbatim; data in [OpenSquirrel.json](OpenSquirrel.json).

# OpenSquirrel releases

## Bug fix release 0.9.1

Tag `0.9.1`, 2026-07-30T15:52:07Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.9.1>

### Fixed

- `SingleQubitGate.__mul__` tries to match and replace with a default gate

## Feature release 0.9.0

Tag `0.9.0`, 2025-12-19T17:08:45Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.9.0>

### Added

- `QGymMapper` mapper pass
- `U`(theta, phi, lambda) gate to default single-qubit gates
- `Z90` and `mZ90` pi-half rotation gates (equivalent to `S` and `Sdag` gates)
- Operation duration in terms of execution cycles can be specified for the `QuantifySchedulerExporter`
- `measurement_to_bit_map` property added to the Circuit class

### Changed

- `Circuit.export` expects an `Exporter` instance as input argument (instead of an `ExportFormat`)
- Moved Bloch sphere rotation composition from the merger pass interface to Bloch sphere rotation semantic module
- Refactor gate semantics as attributes of gates

### Removed

- The `QuantifySchedulerExporter` no longer returns a `bit_register_mapping`
(use `Circuit.measurement_to_bit_map` property instead), it only returns a quantify-scheduler `Schedule`
- The `ExportFormat` has been deprecated
(exporters can be specified by providing an instance as input argument to `Circuit.export`)

## Feature release 0.8.0

Tag `0.8.0`, 2025-11-03T07:13:07Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.8.0>

### Added

- Processing of control instructions (Barrier, Wait) added to quantify-scheduler exporter

### Changed

- Refactor of visitor functionality of IR components and implementations
- Improved SWAP placement and refactor of common functionalities in existing router passes

## Feature release 0.7.0

Tag `0.7.0`, 2025-10-13T12:20:13Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.7.0>

### Added

- Support for Python 3.13 added.

### Removed

- Support for Python 3.9 dropped.

## Bug fix release 0.6.1

Tag `0.6.1`, 2025-10-06T11:12:56Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.6.1>

### Added

- `instruction_count` property to `Circuit`

### Fixed

- Autocompletion for `CircuitBuilder` gates
- Re-mapper properly handles remapping of target qubits

## Feature release 0.6.0

Tag `0.6.0`, 2025-08-28T12:33:41Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.6.0>

### Added

- `MIPMapper` mapper pass
- OpenSquirrel's `__version__` attribute exposed

### Changed

- `RoutingValidator` changed to `InteractionValidator`

### Fixed

- `ShortestPathRouter` and `AStarRouter` now correctly propagate SWAP gate insertion effects throughout the circuit
- The values for parameters `theta` and `phi` stay within the domain `(-pi, pi]` throughout parse- and compile-time
(_note_: gate modifiers have precedence over normalization)
- Mapping of the target qubits of controlled gates

## Feature release 0.5.0

Tag `0.5.0`, 2025-05-28T09:32:48Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.5.0>

### Added

- `asm_filter` method to the `Circuit` class to filter-out assembly declarations by backend name

### Changed

- Default gate identification check refactored (now including check for phase)
- `McKayDecomposer` checks `X90` on BSR semantic instead of name

### Fixed

- `RoutingValidator` ignores assembly declarations

## Feature release 0.4.0

Tag `0.4.0`, 2025-04-28T12:39:00Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.4.0>

### Added

- Assembly declaration
- `Rn` unitary instruction
- `SWAP2CZDecomposer` decomposer pass
- `CZDecomposer` decomposer pass
- `ShortestPathRouter` router pass
- `RandomMapper` mapper pass
- `AStarRouter` router pass

### Changed

- libQASM 1.1.0 integrated (updated from 0.6.9)
- Refactor: removed generators
- Changed the `RoutingChecker` pass to a `RoutingValidator` pass
- Changed use of `native` to `primitive`, e.g. `NativeGateValidator` is now `PrimitiveGateValidator`
- Compilation passes accept `kwargs` as input

## Bug fix release 0.3.1

Tag `0.3.1`, 2025-01-31T13:54:44Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.3.1>

### Fixed

- Bug in the writing of SWAP instructions

## Feature release 0.3.0

Tag `0.3.0`, 2025-01-30T13:05:33Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.3.0>

### Added

- `NativeGateValidator` validator pass

### Changed

- Relaxed NumPy version requirement to `>=1.26` for all supported Python versions

### Fixed

- Fixed order of merging Bloch sphere rotations

## Feature release 0.2.0

Tag `0.2.0`, 2025-01-21T14:24:33Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.2.0>

### Added

- `init` non-unitary instruction
- `SWAP` two-qubit unitary instruction
- `barrier` and `wait` control instructions
- `SingleQubitGatesMerger` merger pass
- `SWAP2CNOTDecomposer` decomposer pass
- `CNOT2CZDecomposer` decomposer pass
- `RoutingChecker`routing pass
- Restore barrier groups in cQASMv1 Exporter

### Changed

- Importing modules, classes, and functionalities simplified
- `merge_single_qubit_gates` method of `Circuit` class,
changed to general `merge` method that accepts custom merger passes
- libQASM 0.6.9 integrated (updated from 0.6.7)
- Refactor: code base adheres to the PEP8 style guide
- Refactor: instruction library simplified
- Refactor: comment nodes removed from IR

### Fixed

- Bug in ABA-decomposer
- Bug in McKay-decomposer (all single-qubit Clifford gates are verified)

## Feature release 0.1.0

Tag `0.1.0`, 2024-10-10T14:05:02Z: <https://github.com/QuTech-Delft/OpenSquirrel/releases/tag/0.1.0>
