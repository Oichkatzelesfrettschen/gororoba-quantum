> Full piece: [https://github.com/QuTech-Delft/qx-simulator/releases](https://github.com/QuTech-Delft/qx-simulator/releases)
> Retrieved 2026-10-16T22:27Z by scripts/capture_qi_docs.py --releases (urllib, REST API);
> 30 releases, newest first, bodies verbatim; data in [qx-simulator.json](qx-simulator.json).

# qx-simulator releases

## Release 0.10.0

Tag `0.10.0`, 2025-08-28T13:21:48Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.10.0>

### Added
- Rn gate to instruction library.
- Support for Python 3.13.
- Integrate with libqasm 1.2.1 release.

## Release 0.9.0

Tag `0.9.0`, 2025-04-08T15:30:33Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.9.0>

### Added
- Integrate with libqasm 1.2.0 release.

### Fixed
- Pi-half rotation gates defined incorrectly.
- Bug in SparseComplex::operator=, which was not always performing the assignment.

## Release 0.8.0

Tag `0.8.0`, 2025-03-26T10:52:08Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.8.0>

### Added
- Integrate with libqasm 1.1.0 release.
- `pow` gate modifier now works with fractional exponents.

## Release 0.7.5

Tag `0.7.5`, 2025-03-17T17:23:28Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.5>

### Added
- Integrate with libqasm 1.0.0 release.
- Documentation: GitHub Actions `doc` workflow.

### Changed
- Allow move constructing a `DenseUnitaryMatrix`.
- Change SimulationIterationAccumulator to keep `shots_done` and receive `shots_requested` in `get_simulation_result()`.
- Update `cpp-linux-x64` and `cpp-linux-arm64` jobs to use `ubuntu-latest` and `ubuntu-24.04-arm` respectively.
- Update to `mkdocs-material/9.6.5` and `mkdocstrings/0.28.2` versions in `requirements.txt`.

### Removed
- Support for 'reset all'.

## Release 0.7.4

Tag `0.7.4`, 2025-01-29T14:49:38Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.4>

### Added
- Integrate with libqasm 0.6.9 release:
  - Add `SWAP` gate instruction.
  - Add `barrier`, `wait`, and `ìnit` non-gate instructions.
- The register manager now holds a 'dirty bitset' for virtual qubit and bit indices.

## Release 0.7.3

Tag `0.7.3`, 2025-01-27T12:30:10Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.3>

### Added
- Documentation: GitHub pages.
- Linters: `.clang-format` and `.clang-tidy`.
- Integrate with libqasm 0.6.8 release:
  - Add gate modifiers. Notice though that `pow` only works with integer exponents.

### Changed
- Implement instructions as a hierarchy.
- Implement `GateConvertor` as a `CircuitBuilder`.
- Implement `BasisVector` as a `boost::dynamic_bitset<uint32_t>`.
- Implement `RegisterManager` as a singleton.
- Change `QuantumState` by taking the measurement register out of it.
- Change `Circuit::execute` to return a `SimulationIterationContext`.
- Change `Matrix` and `DenseUnitaryMatrix` to use `std::vector` instead of `std::array`.
- Change file, functions, and variable names.

### Removed
- `abseil` library dependency.

## Release 0.7.2

Tag `0.7.2`, 2024-11-22T17:09:26Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.2>

### Added

- Integrate with libqasm 0.6.7 release.
- Add `reset` instruction.
- Make QX simulator aware of bit (register) variables.
- Update `test` and `assets` workflows.

### Changed

### Removed

## Release 0.7.1

Tag `0.7.1`, 2024-05-27T14:24:48Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.1>

### Added

- Integrate with libqasm 0.6.6 release.
- Allow multiple qubit/bit (register) definitions and mid-circuit measurements.

### Changed

- Update `conanfile.py` to request `libqasm/0.6.6` and use `tools.build.skip_test`.
- Update GitHub workflows with some improvements taken from `libqasm`.

### Removed

## Release 0.7.0

Tag `0.7.0`, 2024-04-17T11:34:06Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/0.7.0>

### Added

- Integrate with libqasm 0.6.3 release.

### Changed

- Rename `tests` folder to `test`.
- Update GitHub workflows.

### Removed

- cQasm 1.x support.
- `circuits` folder.

## Release 0.6.5: Conan, ARM on Linux

Tag `v0.6.5`, 2023-12-04T12:36:31Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.5>

**Added**

- Python 3.12 support

**Changed**
- Uses Conan
- New Github workflows
- Working ARM runners in the CI

## Release 0.6.4: error messages

Tag `v0.6.4`, 2023-09-21T10:57:28Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.4>

Added
Meaningful error message when parsing or simulation fails

Changed
Does not crash when too many qubits asked

## Release 0.6.3: bugfix and misc

Tag `v0.6.3`, 2023-09-21T02:06:38Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.3>

### Added

- Address sanitizer CMake mode

### Changed

- Removed submodules and deps/ folder, replaced with CMake FetchContent
- C++23
- gtest instead of doctest
- Various fixes to Github actions
- Fixed bug in bitset due to bool automatic casting to 32 bits
- Documentation formatting fixes
- Doc chapter about internals

### Removed

-

## 0.6.2: depolarizing channel error model, constant seeds

Tag `v0.6.2`, 2023-02-27T12:31:39Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.2>

# Added
depolarizing_channel error model and docs
ability to pass constant seed for deterministic simulation
RandomTest doing Kolmogorov-Smirnov statistical test to match random numbers with their ideal probability distribution

# Changed
fixed docs
source files use .hpp/.cpp extensions
random number distributions (integer min/max and real 0-1) are done in-house for portability and consistency of results

# Removed
nothing

## 0.6.1 beta: ARM compat, classical not and more controlled gates, integers in "results" and new Python API

Tag `v0.6.1`, 2023-02-10T10:34:48Z (pre-release): <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.1>

**Added**
Linux arm64 Python wheel and Linux arm64 test workflow (GCC-Release)
"classical not" gate is back
"state" section in JSON now contains a new entry "norm" which is the square of the modulus of the complex number
C++ integration test
All gates can be controlled (including prep, measure). This is not new but was accidentally removed in 0.6.0.
New Python API execute_string and execute_file without having to create qxelarator.QX() and returning user-friendly Python type
**Changed**
Fixed README
"results" section in JSON contains integers instead of floats (those integers being the number of occurences)
In relation to previous point, "results" only relates to measurement register averaging, and no longer to quantum state when doing a single shot. For that, use the "state" section in the JSON.
Output float precision is 8 decimals instead of 6
**Removed**
Most Python tests - already covered in C++ integration test, and they didn't check much anyway

## Version 0.6.0: performance improvement, modern C++20 and matrices

Tag `v0.6.0`, 2023-01-23T15:58:30Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.6.0>

Almost a complete rewrite. No functional change except:
- error models don't work anymore :( they will come better and stronger later on
- classical not gate doesn't work anymore :( it's just an omission, will be fixed soon
- get_measurement_outcome and get_state don't exist anymore :( they've been superseeded by json output
- it's faster and using a single core \o/ and less memory on average

### Added

- Ability to easily implement any quantum gate by simply giving an arbitrary unitary matrix in Gates.h
- Performance speedup using a single thread
- Some proper linear algebra primitives using template metaprogramming
- Abseil-cpp dependency for flat_hash_map
- Ability to compile the simulator with an set maximum number of qubits - in the future this will
be using templates as well to switch data structures based on the input quantum circuit

### Changed

- Quantum state is stored as a sparse array implemented using a flat_hash_map from Abseil-cpp
- C++20 in place of C++14,
- Code style: camel case

### Removed
- OpenMP and multithreading.
- SSE, AVX and other intrinsics.
- get_measurement_outcome and get_state methods. Now accessible via JSON output.

## Release 0.5.5: output state complex amplitudes and set_string

Tag `v0.5.5`, 2023-01-12T16:05:14Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.5.5>

Added:
- set_string method to parse a cqasm string directly instead of a cqasm file


Changed:
- Fixed issue #118: quantum state is always displayed, as well as measurement register averaging

## Release 0.5.4: 2 bugfixes and some cleanups

Tag `v0.5.4`, 2023-01-06T13:17:04Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.5.4>

## Added
- Tests for measure gate

## Changed
- Fixed issues #91 and #114
- As part of #114, switch to sequential/simple measure gate

## Removed
- QFT implementation (never instantiated, so no functional change)
- qx-server no longer exists, together with the network libraries
- "Microcode" generation functions (never used either)
- Parallel gates in gate.h (they were executed sequentially)
- Some non-needed and/or obsolete code

## Release 0.5.3: Python 3.11 support

Tag `v0.5.3`, 2023-01-02T09:22:57Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.5.3>

Adds Python 3.11 support, and that's it

## Release 0.5.2: better documentation, tidy tests and fixed Python version

Tag `v0.5.2`, 2022-12-07T09:07:32Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.5.2>

**Added**
- Readthedocs documentation

**Changed**
- Fixed Python versions on Linux
- Updated README with new API functions
- Tidy tests and circuits folder

**Removed**
- Python 3.6 support

## Release 0.5: new UI, JSON output and improved code

Tag `v0.5.0`, 2022-11-17T08:39:31Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.5.0>

A long-needed cleanup and modernization of the code and some better output features.
Watch-out: the output format is changed. If you were parsing the output, this new release will break your code. JSON output is added, so parsing of raw stdout is no longer needed.

### Added
- "-j <filename>" CLI option to output JSON to a file
- Possible to use the simulator without OpenMP.

### Changed
- Measure_all gate added; does no longer measure each qubit separately.
- Move to C++11: smart pointers, etc.
- Format of output has been changed. You no longer need to add a "display" gate to
output the quantum state at the end of the circuit.
- Now uses the new Libqasm API instead of the old one.
- Output complex amplitudes when not averaging measurement register.
- Do not add automatically a measure_all when doing measurement averaging;
average the measurement register only.

### Removed
- Most preprocessor macros. E.g. for gate creation.
- A lot of old and useless code was removed. A lot of dead code removed.

### Fixed
- Close input file when done.
- Code style has been completely fixed automatically with clang-format.
- Headers no longer include .cc file.
- Moved implementations to .cc files instead of headers.

## CPU compatibility fix

Tag `v0.4.2`, 2021-06-01T10:38:01Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.4.2>

This fixes a problem where the PyPI wheels for qxelarator were being built using whatever CPU extensions the github runner happened to have, resulting in unnecessary compatibility issues/illegal instruction faults. The wheels now only require up to SSE3.

### Fixed
- Wheels no longer require exotic CPU extensions to work

## Build system update

Tag `v0.4.1`, 2021-05-20T23:55:32Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.4.1>

This update doesn't change anything functionally, but completely overhauls the build system.

### Added
- Continuous integration for as far as automated tests exist
- Automated release build and distribution logic for PyPI
- Installation logic in build system
- qxelarator wheels include qx-simulator binary (and friends)

### Fixed
- Build on MacOS
- Build on Windows using MSVC
- Python build process on various platforms

## Stability update

Tag `v0.4.0`, 2021-05-20T16:12:25Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.4.0>

XPU-based threading was removed in favor of OpenMP to solve pthread-related stability issues in XPU.

## cQASM v1.0 support in qxelerator

Tag `v0.3.0`, 2019-05-01T06:00:01Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.3.0>

- updated qxelerator to support cqasm v1.0
- updated setup instructions in README.md

## Bugfix release: Fixed issue with correct merging of libqasm 0.1.3

Tag `v0.2.5`, 2018-12-21T06:12:54Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.5>

Release Notes:
- Fixed issue with libqasm submodule, this release is now with the correct version

## Bugfix release: fixing issue with integer arguments for qubit operations

Tag `v0.2.4`, 2018-12-14T13:16:24Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.4>

Release Notes:

- Removed -u 0 in Jenkinsfile again
- Single qubit operations now accept integers as arguments, previously it required floats.

## QX Rise v0.2.3

Tag `v0.2.3`, 2018-11-04T20:53:41Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.3>

Release notes:
- Fixed pthread mutex locking bug in XPU worker.
- Updated the libqasm to get the hotfix.

## QX Rise v0.2.2

Tag `v0.2.2`, 2018-09-25T09:34:52Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.2>

Release notes:
* Fixed bug in measurement and preparation implementation for large number of qubits.
* Fixed verbose GNU Compiler warnings under Linux.

## QX Rise v0.2.1

Tag `v0.2.1`, 2018-09-04T09:26:56Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.1>

Release notes:
* Enabled quantum noise simulation using the **Depolarizing Error Model**
* Added multishot simulation mode to save simulation time on the Quantum Inspire web platform.
* Enabled **Identity** gate support

The **Depolarizing Error Model** can be enabled by adding the following line o your cQASM code:
**error_model depolarizing_channel,0.001** (where 0.001 is the error rate).

For more information on the depolarizing error model implementation please refer to the following paper:
N. Khammassi, I. Ashraf, X. Fu, C. G. Almudever and K. Bertels, "**QX: A High-performance Quantum Computer Simulation Platform**", *Design, Automation & Test in Europe Conference & Exhibition (DATE)*, 2017, Lausanne, 2017, pp. 464-469. doi: 10.23919/DATE.2017.7927034

## QX Rise v0.2.0

Tag `v0.2.0`, 2018-08-23T11:29:22Z: <https://github.com/QuTech-Delft/qx-simulator/releases/tag/v0.2.0>

Release notes:
- Initial **cQASM 1.0** support.
- Integrated with **libqasm 0.1.1** release.
- Added support for new quantum gates:  
  - Flexible controlled phase shift (*CR* and *CRK*)
  - Measurement and Preparation in X/Y/Z basis: added *measure_x*, *measure_y*, *prep_x* and *prep_y*.
- Re-implemented classical *NOT* gate for full binary-controlled gate support.
- Added support for **Single Gate Multiple Qubits** (**SGMQ**).
- Fixed overflow bug when simulating more than 31 qubits.
- Fixed bug in qubit register measurement ("measure_all" instruction).
- Added a new set of unit tests.

For more information on the cQASM language, please refer to the following paper: https://arxiv.org/abs/1805.09607
