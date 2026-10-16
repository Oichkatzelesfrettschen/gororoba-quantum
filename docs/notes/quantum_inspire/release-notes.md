# Quantum Inspire release digest

Changes to the Quantum Inspire platform and the components it is built
from, newest first, kept to what changes how a user writes, submits or reads
a job. Platform events come from the site captures; component changes come
from the release histories retained under [releases/](releases/MANIFEST.json)
(GitHub REST releases API and the GitLab releases API, retrieved 2026-10-16
UTC, bodies verbatim in each `releases/<component>.md`). The platform's own
release-notes page ([capture](site/release-notes.md),
[live](https://www.quantum-inspire.com/release-notes/)) carries no dated
entries for QI 2.0: it warns that scheduled and unscheduled maintenance may
fail submitted jobs and points to the nine component release pages. Several
2025-2026 GitHub releases carry only a title ("Release 0.18.5"); for those
the change is read from the source at the tag, as stated in the row.

## Backend timeline

| Backend | Available | Source |
|---|---|---|
| Tuna-17 (17 transmons, 24 tunable couplers) | since April 2026 | [backends/transmons](site/backends_transmons.md) ([live](https://www.quantum-inspire.com/backends/transmons/)) |
| Tuna-9 (9 transmons, 12 tunable couplers) | since December 2025 | same |
| Tuna-5 (5 transmons, 4 tunable couplers) | since May 2025 | same |
| Starmon-7 (7 transmons, 8 fixed couplers) | February 2025 to December 2025 | same |
| Starmon-5 (5 transmons, 5 fixed couplers) | April 2020 to December 2025 | same |
| Spin-2+ (2 data qubits in a 6-dot array) | taken offline; no dates stated | [backends](site/backends.md) ([live](https://www.quantum-inspire.com/backends/)) |
| Spin-2 | QI launch, 20 April 2020; superseded by Spin-2+ | Spin-2+ fact sheet (site manifest `hosted_documents`) |
| Ry emulator (TU Eindhoven, 9 qubits) | listed as new; no date stated | [backends](site/backends.md) |
| QX emulator | since the first public release, 2018-09-04 | [release-notes-old](site/release-notes-old.md) |

The transmons page says Starmon-7 "replaced the original Starmon-5 in
February 2025" and that Starmon-5 "was available from April 2020 to
December 2025"; the two statements overlap for ten months and the page does
not say whether both ran in parallel. This account's catalogue
([catalogue.json](../../evidence/quantum_inspire/catalogue.json)) offers
backend types for Tuna-5, Tuna-9, Tuna-17, QX and the Ry emulator only;
Starmon-7 and Spin-2+ appear as offline backends without a type.

## Changes that affect usage, newest first

| Date | Component | Change | Effect on use |
|---|---|---|---|
| 2026-10-14 | libqasm 1.6.0 | Python 3.14 support. | None on the platform API. |
| 2026-10-05 | qiskit-quantuminspire 0.18.5, pennylane-quantuminspire 0.15.5 | Title-only releases; the docs at these tags are retained under [sdk/](sdk/MANIFEST.json). | PennyLane devices are `pennylane_quantuminspire.qi_device.QIDevice` built from a `qiskit_quantuminspire` `QIProvider` backend. |
| 2026-10-02 | libqasm 1.5.0 | `CCX`, `CCNOT`, `CSWAP`. | Spec-level only until QX or a compiler integrates libqasm 1.5; the QX catalogue gateset omits them. |
| 2026-09-25 | quantuminspire 4.1.0 | Title-only release; the README at this tag is [sdk/README.md](sdk/README.md). | Current CLI reference. |
| 2026-08-07 | quantuminspire 4.0.0 | Title-only release. The README at 4.0.0 replaces `qi files upload` and `qi results get` (last present at 3.5.3) with `qi run --file F --backend-type-id N`, `qi projects init/list/delete`, `qi algorithms init/status/logs/results/final-result`, `qi jobs inspect/status/logs/results/final-result`, `qi backends list/get`, `qi files compile` and `qi config get/set`. | The kbase software-development-kit and qi-tool pages still teach the removed commands. |
| 2026-07-30 | OpenSquirrel 0.9.1 | `SingleQubitGate.__mul__` fix. | None. |
| 2026-06-05 / 06-15 | libqasm 1.4.0, 1.4.1 | `CV`, `CY`, `DCNOT`, `ECR`, `ISWAP`, `InvSqrtSWAP`, `M`, `MS`, `SqrtISWAP`, `SqrtSWAP`; `measureX/Y/Z` aliases. | Spec-level; absent from every catalogue gateset. |
| 2026-05 | quantuminspire 3.5.2, 3.5.3; qiskit 0.17.x-0.18.x; pennylane 0.14.x-0.15.x | Title-only releases. | None documented. |
| 2026-04-14 | libqasm 1.3.0 | `U`, `Z90`, `mZ90`; `measure` takes three floats for the axis. | `U`, `Z90`, `mZ90` appear in the QX gateset; parameterized `measure` is unverified on the platform. |
| April 2026 | platform | Tuna-17 available. | 17-qubit register, ninja-star topology. |
| 2026-03-19 | quantify-scheduler v0.28.0 | Skippable measure acquisition delay, automatic RF switching for Qblox, APPEND acquisitions. | Tuna control stack only. |
| 2026-02-04 | pennylane-quantuminspire 0.13.0; quantify-scheduler v0.27.0 | PennyLane 0.44.0; Rz merging pass and Qblox QRC support. | Plugin dependency bump. |
| 2026-01-15 / 01-19 | quantuminspire 3.4.1, 3.5.1 | Title-only releases; `qi projects list` and `qi projects delete` are in the README by 3.5.3. | Project management from the CLI. |
| December 2025 | platform | Tuna-9 available; Starmon-5 and Starmon-7 end. | Transmon users move to Tuna. |
| 2025-12-19 | OpenSquirrel 0.9.0 | `U`, `Z90`, `mZ90` default gates; `QGymMapper`; cycle durations in the quantify exporter; `Circuit.export` takes an `Exporter` instance and `ExportFormat` is deprecated. | Local OpenSquirrel scripts change their export call. |
| 2025-11-06 | quantify-scheduler v0.26.0 | New acquisition framework with `coords` and unified `xarray` return data. | Tuna control stack only. |
| 2025-11-03 | OpenSquirrel 0.8.0 | `barrier` and `wait` reach the quantify-scheduler exporter. | Control instructions shape Tuna schedules. |
| 2025-10-22 | qiskit-quantuminspire 0.13.0; pennylane 0.8.0 | Qiskit 2.1.x. | Plugin requires Qiskit 2.1. |
| 2025-10-13 | OpenSquirrel 0.7.0 | Python 3.13 added, 3.9 dropped. | Local tooling. |
| 2025-10-03 | qiskit 0.12.1; pennylane 0.7.1 | Fix for assembly declarations in hybrid algorithms. | `asm` blocks work in hybrid jobs. |
| 2025-08-28 | qx-simulator 0.10.0; OpenSquirrel 0.6.0 | QX: `Rn`, libqasm 1.2.1. OpenSquirrel: `MIPMapper`, parameters normalized to (-pi, pi]. | `Rn` simulates on QX. |
| 2025-06-24 | qiskit 0.12.0; pennylane 0.7.0 | Assembly declarations (PennyLane `Asm` instruction). | Rydberg directives from the plugins. |
| 2025-05-28 | OpenSquirrel 0.5.0 | `asm_filter`; routing validator ignores `asm`. | |
| May 2025 | platform | Tuna-5 available. | First flux-tunable-coupler backend. |
| 2025-04-28 | OpenSquirrel 0.4.0 | `asm` declarations, `Rn`, `SWAP2CZDecomposer`, `CZDecomposer`, routers and mappers; libqasm 1.1.0. | The Tuna default passes (`SWAP2CZDecomposer`, `CZDecomposer`) exist from here. |
| 2025-04-08 | qx-simulator 0.9.0 | Fix: pi-half rotation gates were defined incorrectly. | QX results with `X90`-family gates before this release are suspect. |
| 2025-03-26 | qx-simulator 0.8.0 | `pow` modifier with fractional exponents. | |
| 2025-03-13 | libqasm 1.1.0 | Assembly declaration, `Rn`. | |
| 2025-02-18 | cQASM-spec 3.0-beta2 | `init`, `SWAP`, `barrier`, `wait`, gate modifiers `inv`, `pow`, `ctrl`. | Current language baseline. |
| 2025-02-05 / 02-06 | quantuminspire 3.0.0, 3.0.1, 3.1.0 | QI 2.0 SDK; 3.0.1 fixes the default API URL; 3.1.0 adds a backend-information command. | |
| February 2025 | platform | Starmon-7 replaces Starmon-5 (see the overlap note above). | |
| 2025-01-31 | libqasm 1.0.0 | Redeclaring a variable is an error. | |
| 2025-01-17 to 01-31 | qiskit-quantuminspire 0.5.0-0.8.2 | Hybrid jobs, `barrier`/`wait`, raw data, failed jobs raise errors, SWAP conversion fix. | |
| 2025-01-29 | qx-simulator 0.7.4 | `SWAP`, `barrier`, `wait`, `init`. | |
| 2024-11-22 | qx-simulator 0.7.2; libqasm 0.6.9 (11-14) | QX `reset` and bit-register awareness; libqasm `SWAP`, `init`, `barrier`, `wait`, operand-less `reset` removed. | |
| 2024-10-16 | cQASM-spec 3.0-beta1; qiskit-quantuminspire 0.1.0 | cQASM 3.0: case-sensitive, decoupled qubit and bit registers, declarations, measurement assignment, `//` comments, not backward compatible. | cQASM 1.0 programs and kbase pages stop applying. |
| 2024-05-27 | qx-simulator 0.7.1 | Several register declarations and mid-circuit measurement. | |
| 2024-04-17 | qx-simulator 0.7.0 | cQASM 1.x support removed. | |
| 2024-01-09 | OpenQL 0.12.2 | Last OpenQL release (Conan packaging, C++23). | OpenQL served Starmon-7 only. |
| 2021-05-26 | QI 1.0 | QX on SURF Lisa; range expressions and binary-controlled multi-qubit gates (cQASM 1.0). | Historical. |
| 2020-07-31 | QI 1.0 | Starmon-5: Rx/Ry/Rz, `measure_x/y/z`, 16384 shots max (8192 default), CZ 60 ns. | Historical. |
| 2020-04-20 | QI 1.0 | Public online access to Spin-2 and Starmon-5 (fact sheet; transmons page). | |
| 2018-12-17 | QI 1.0 | cQASM size limit raised to 1 MB. | Historical; the QI 2.0 limit is not documented. |
| 2018-09-04 | QI 1.0 | First public release. | |

QI 1.0 ran a maintenance window every Wednesday 08:00-12:00 CET
([release-notes-old](site/release-notes-old.md),
[live](https://www.quantum-inspire.com/release-notes-old/)); QI 2.0 states no
window.

## Component sources

| Component | Retained history | Live |
|---|---|---|
| quantuminspire (SDK and `qi` CLI) | [md](releases/quantuminspire.md), [json](releases/quantuminspire.json) | https://github.com/QuTech-Delft/quantuminspire/releases |
| cQASM-spec | [md](releases/cQASM-spec.md), [json](releases/cQASM-spec.json) | https://github.com/QuTech-Delft/cQASM-spec/releases |
| libqasm | [md](releases/libqasm.md), [json](releases/libqasm.json) | https://github.com/QuTech-Delft/libqasm/releases |
| OpenSquirrel | [md](releases/OpenSquirrel.md), [json](releases/OpenSquirrel.json) | https://github.com/QuTech-Delft/OpenSquirrel/releases |
| OpenQL | [md](releases/OpenQL.md), [json](releases/OpenQL.json) | https://github.com/QuTech-Delft/OpenQL/releases |
| qx-simulator | [md](releases/qx-simulator.md), [json](releases/qx-simulator.json) | https://github.com/QuTech-Delft/qx-simulator/releases |
| qiskit-quantuminspire | [md](releases/qiskit-quantuminspire.md), [json](releases/qiskit-quantuminspire.json) | https://github.com/QuTech-Delft/qiskit-quantuminspire/releases |
| pennylane-quantuminspire | [md](releases/pennylane-quantuminspire.md), [json](releases/pennylane-quantuminspire.json) | https://github.com/QuTech-Delft/pennylane-quantuminspire/releases |
| quantify-scheduler | [md](releases/quantify-scheduler.md), [json](releases/quantify-scheduler.json) | https://gitlab.com/quantify-os/quantify-scheduler/-/releases |

The 4.0.0 CLI change was established by comparing the quantuminspire README
at the tags 3.0.0, 3.3.1, 3.5.3, 4.0.0 and 4.1.0 (raw.githubusercontent.com,
2026-10-16); only the 4.1.0 README is retained.
