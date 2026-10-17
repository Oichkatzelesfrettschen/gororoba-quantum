# cQASM 3.0 on Quantum Inspire

Quantum Inspire accepts cQASM 3.0 programs only: the API catalogue lists the
languages cQASM 3.0 and Python 3.11 (hybrid files)
([catalogue.json](../../evidence/quantum_inspire/catalogue.json),
`languages`). The language rules below come from the specification capture
in [cqasm-spec/](cqasm-spec/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/index.html)) (live:
https://qutech-delft.github.io/cQASM-spec/latest/, MkDocs build of gh-pages
commit `91cff84b22553062cdb2aeebd968a1dd2a6a3ef6`, retrieved 2026-10-16
UTC). The backend columns come from the operational-specifics pages under
[site/](site/kbase.md) ([live](https://www.quantum-inspire.com/kbase/)), the catalogue gatesets and the runs retained under
[results/quantum_inspire/runs/](../../../results/quantum_inspire/runs/).
Contradiction labels (C1 ...) refer to
[knowledge-base.md](knowledge-base.md#contradictions-and-their-reconciliation).

The `latest` specification is ahead of the platform. libqasm, the parser QX
and OpenSquirrel share, added `U`, `Z90`, `mZ90` and parameterized `measure`
in 1.3.0 (2026-04-14), ten two-qubit gates and the `measureX/Y/Z` aliases in
1.4.0, and `CCX`/`CSWAP` in 1.5.0 (2026-10-02), while the newest qx-simulator
release, 0.10.0, integrates libqasm 1.2.1
([releases/libqasm.md](releases/libqasm.md) ([live](https://github.com/QuTech-Delft/libqasm/releases)),
[releases/qx-simulator.md](releases/qx-simulator.md) ([live](https://github.com/QuTech-Delft/qx-simulator/releases))). A feature that only the
specification names is unverified on the platform until a run accepts it; the
catalogue gateset and retained runs are what a submission may rely on (C8).

## Program structure

```cqasm
version 3.0          // first statement; only comments may precede it

qubit[3] q           // QubitArray; qubits start in |0>
bit[3] b             // BitArray; measure needs a declared bit target

init q               // optional; only before any non-control instruction on q
H q[0]
CNOT q[0], q[1]
ctrl.X q[1], q[2]    // gate modifier on a single-qubit gate
barrier q            // scheduler may not move instructions across it
wait(5) q[0]         // delay of 5 execution cycles, also a barrier
b = measure q        // register-wide SGMQ measurement
```

| Rule | Source |
|---|---|
| `version 3.0` (or `version 3`, minor defaults to 0) appears once, first; only comments precede it. | [version statement](cqasm-spec/language_specification/statements/version_statement.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/version_statement.html)) |
| A newline or `;` ends a statement; spaces and tabs are free between tokens. | [newlines](cqasm-spec/language_specification/tokens/newlines.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/newlines.html)), [whitespace and comments](cqasm-spec/language_specification/tokens/whitespace_and_comments.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/whitespace_and_comments.html)) |
| Comments: `// ...` to end of line, `/* ... */` anywhere between tokens. cQASM 1.0 `#` comments are gone (the Spin-2+ appendix still accepts `#`). | [whitespace and comments](cqasm-spec/language_specification/tokens/whitespace_and_comments.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/whitespace_and_comments.html)), [spin_2plus](cqasm-spec/appendices/spin_2plus.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/appendices/spin_2plus.html)) |
| Everything is case-sensitive: `H q[0]` and `h Q[0]` differ. cQASM 1.0 was case-insensitive. | [language specification](cqasm-spec/language_specification/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html)), [site/kbase_cqasm.md](site/kbase_cqasm.md) ([live](https://www.quantum-inspire.com/kbase/cqasm/)) |
| Identifiers: ASCII letters, digits and `_`, no leading digit, not a keyword. | [identifiers](cqasm-spec/language_specification/tokens/identifiers.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html)) |
| Keywords: `asm`, `barrier`, `bit`, `ctrl`, `init`, `inv`, `measure`, `pow`, `qubit`, `reset`, `version`, `wait`. Gate names are identifiers, not keywords. | [keywords](cqasm-spec/language_specification/tokens/keywords.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html)) |
| Literals: 64-bit signed integers and IEEE 754 doubles; constants `pi`, `tau` (2 pi), `eu` (e); functions `sqrt`, `exp`, `log`, `abs`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` on real arguments, combined with arithmetic operators. | [literals](cqasm-spec/language_specification/tokens/literals.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html)), [constants](cqasm-spec/language_specification/expressions/predefined_constants.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html)), [functions](cqasm-spec/language_specification/expressions/builtin_functions.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html)) |
| Preferred file extension `.cq`; the web editor names a new algorithm `source.cq`. | [language specification](cqasm-spec/language_specification/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html)), [site/kbase_creating-a-new-project.md](site/kbase_creating-a-new-project.md) ([live](https://www.quantum-inspire.com/kbase/creating-a-new-project/)) |
| The cQASM 1.0 constructs `qubits N`, sub-circuits, static loops, curly-brace parallel bundles, `prep_*`, `measure_*`, `measure_all`, `c-` binary control, `not`, `display` and `error_model` do not exist in 3.0. | [site/kbase_cqasm.md](site/kbase_cqasm.md) ([live](https://www.quantum-inspire.com/kbase/cqasm/)), [cQASM-spec 3.0-beta1 notes](releases/cQASM-spec.md) ([live](https://github.com/QuTech-Delft/cQASM-spec/releases)) |

## Types, registers and indices

The four types are Qubit (`qubit q`), QubitArray (`qubit[N] q`), Bit
(`bit b`) and BitArray (`bit[N] b`), with the size in brackets before the
name ([types](cqasm-spec/language_specification/types.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html))). Declaring
`qubit north[2]`, as the kbase qubit-register page shows, is not cQASM 3.0
syntax ([site/kbase_qubit-register.md](site/kbase_qubit-register.md) ([live](https://www.quantum-inspire.com/kbase/qubit-register/))).

- Indices start at 0. An index list mixes single entries and inclusive
  ranges: `q[1, 3:5]` is qubits 1, 3, 4, 5
  ([indices](cqasm-spec/language_specification/expressions/indices.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/indices.html))).
- Several qubit registers may be declared. On a backend, QI concatenates
  them in declaration order onto physical qubits: declaring `qubit[2] a`
  then `qubit c` maps `a[0], a[1], c` onto `q[0], q[1], q[2]`
  ([site/kbase_qubit-register.md](site/kbase_qubit-register.md) ([live](https://www.quantum-inspire.com/kbase/qubit-register/))). Bit
  registers concatenate the same way and start at zero
  ([site/kbase_binary-register.md](site/kbase_binary-register.md) ([live](https://www.quantum-inspire.com/kbase/binary-register/))).
- Register width on hardware: the executing page requires the declared
  qubit count to equal the chip's; every retained Tuna-17 run declared
  `qubit[17]`, so narrower declarations are untested there (C15). QX accepts
  at most `nqubits` 10 for this account, the Ry emulator 9 (catalogue).

## Bit and qubit order

Ket vectors and bit strings list indices decreasing from left to right:
for `qubit[3] q` in state `|110>`, `q[2] = 1`, `q[1] = 1`, `q[0] = 0`, and
the measured bit string reads `110` with `b[0]` rightmost
([language specification, ordering](cqasm-spec/language_specification/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html))).
Matrices in the gate pages use the reversed textbook order, so in a
controlled gate's matrix `q0` is the control written first in the tensor
product. The QI histogram follows the bit-string convention: the
measurement of `q[0]` (stored in `b[0]`) is the rightmost character
([site/kbase_hello-quantum-world.md](site/kbase_hello-quantum-world.md) ([live](https://www.quantum-inspire.com/kbase/hello-quantum-world/)));
`b[3]` is the fourth character from the right, not the third the kbase
pages say (C14). Downloaded histogram keys and raw data are the decimal
value of that bit string
([site/kbase_displaying-and-downloading-your-results.md](site/kbase_displaying-and-downloading-your-results.md) ([live](https://www.quantum-inspire.com/kbase/displaying-and-downloading-your-results/))).
On Tuna, results are a shots x bits array in bit-register order
([site/kbase_tuna-operational-specifics.md](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/))).

## Gates

A unitary instruction is a named gate, optionally with parameters in
parentheses, followed by comma-separated qubit operands:
`CRk(2) q[1], q[0]`, `Rx(pi/2) q[0]`
([unitary instructions](cqasm-spec/language_specification/statements/instructions/unitary_instructions.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html))).
The standard gate set has 20 single-qubit and 17 multi-qubit named gates
([standard gate set](cqasm-spec/standard_gate_set/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html))); each gate page
under [cqasm-spec/standard_gate_set/](cqasm-spec/standard_gate_set/index.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html))
gives its matrix, properties and examples. Parameters: `Rx/Ry/Rz(theta)`,
`Rn(nx, ny, nz, theta, phi)`, `U(theta, phi, lambda)`, `CR(theta)`, `CRk(k)`.

Gate modifiers transform a gate into a gate and are applied right to left:

| Modifier | Meaning | Example |
|---|---|---|
| `inv.` | U to its adjoint | `inv.X q[0]` |
| `pow(a).` | U to the power a (a float) | `pow(2).T q[0]` |
| `ctrl.` | U to controlled-U; the control qubit is prepended | `ctrl.pow(1/2).inv.X q[0], q[1]` |

Modifiers act on single-qubit gates only: `inv.CRk(2) q[0], q[1]` and
`inv.ctrl.X q[0], q[1]` are invalid, `ctrl.inv.X q[0], q[1]` is valid.
qx-simulator applies `pow` with integer exponents from 0.7.3 and fractional
exponents from 0.8.0 ([releases/qx-simulator.md](releases/qx-simulator.md) ([live](https://github.com/QuTech-Delft/qx-simulator/releases))).
The kbase full-adder example uses `ctrl.X90` and `ctrl.mX90`
([site/kbase_full-adder.md](site/kbase_full-adder.md) ([live](https://www.quantum-inspire.com/kbase/full-adder/))).

SGMQ notation applies one instruction to several qubits and is syntactic
sugar, not a promise of simultaneity: `X q[0,2,4]` is three statements;
`CNOT q[0:2], q[3:5]` pairs operands element by element, and every operand
must hold the same number of qubits
([SGMQ](cqasm-spec/language_specification/statements/instructions/single-gate-multiple-qubit-notation.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html)),
[site/kbase_cqasm-single-gate-multiple-qubits.md](site/kbase_cqasm-single-gate-multiple-qubits.md) ([live](https://www.quantum-inspire.com/kbase/cqasm-single-gate-multiple-qubits/))).

## Non-unitary and control instructions

| Instruction | Semantics | Source |
|---|---|---|
| `init q` | Puts qubits in `|0>` explicitly; legal only before any non-control instruction on that qubit (a preceding `barrier` is allowed). Use `reset` mid-circuit. | [init](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/init_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html)) |
| `b = measure q` | Z-basis measurement into a declared bit; SGMQ needs equal bit and qubit counts (`b[0, 2, 1] = measure q[3:5]` is valid, `b[0:1] = measure q[2]` is not). Latest spec also defines `measure(x, y, z)` with an axis and `measureX/Y/Z` aliases (libqasm 1.3-1.4, unverified on the platform). | [measure](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html)) |
| `reset q` | Measures and flips on outcome 1, so the qubit ends in `|0>` and leaves entanglement; the bit register is unchanged. | [reset](cqasm-spec/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html)) |
| `barrier q` | The scheduler may not move instructions on these qubits across it; consecutive barriers may merge into one uniform barrier on some backends. | [barrier](cqasm-spec/language_specification/statements/instructions/control_instructions/barrier_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html)) |
| `wait(n) q` | Delays later instructions on each listed qubit by n execution cycles, scheduled per qubit, and acts as a barrier; successive waits on one qubit may fuse. On Tuna and Starmon-7 a cycle is 20 ns. | [wait](cqasm-spec/language_specification/statements/instructions/control_instructions/wait_instruction.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html)), [site/kbase_tuna-operational-specifics.md](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)) |
| `asm(Backend) '''...'''` | Passes the raw text verbatim to the named backend; other consumers ignore it; no statement moves across it. The Ry emulator reads `asm(Rydberg)` blocks. | [assembly declaration](cqasm-spec/language_specification/statements/assembly_declaration.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/assembly_declaration.html)), [raw text](cqasm-spec/language_specification/tokens/raw_text_string.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html)) |

The kbase Tuna and Starmon-7 pages write `wait q[0:4], 11`; the
specification form `wait(11) q[0:4]` is correct, and the retained Tuna-17
runs submitted `wait(40) q[0]` and completed (C6).

Measurement on the backends:

- QX and Tuna allow mid-circuit measurement and several measurements into
  different bits ([site/kbase_tuna-operational-specifics.md](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)),
  [releases/qx-simulator.md](releases/qx-simulator.md) ([live](https://github.com/QuTech-Delft/qx-simulator/releases)) 0.7.1).
- On hardware every qubit is physically initialized at each shot start and
  measured at each shot end; the program's measure statements select what
  is returned ([site/kbase_hardware-backends.md](site/kbase_hardware-backends.md) ([live](https://www.quantum-inspire.com/kbase/hardware-backends/))).
- The Ry emulator allows no mid-circuit measurement and needs no measure
  statement: every qubit is measured at the end
  ([site/kbase_ry-emulator-operational-specifics.md](site/kbase_ry-emulator-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/ry-emulator-operational-specifics/))).
- Measurements on a multi-qubit target are still scheduled; a `barrier`
  before them keeps them parallel on Tuna. The retained Tuna-17 runs end with
  `barrier q` then `b = measure q`.

## Ry emulator directives

Inside `asm(Rydberg) '''...'''` the Ry emulator reads two directives
([site/kbase_code-example-getting-started-with-the-neutral-atom-platform.md](site/kbase_code-example-getting-started-with-the-neutral-atom-platform.md) ([live](https://www.quantum-inspire.com/kbase/code-example-getting-started-with-the-neutral-atom-platform/))):

- `INIT(x, y) q[i]` places atom `q[i]` at lattice position (x, y). Only
  before any operation; an `INIT` after an operation is an error; atoms
  without `INIT` are placed by the backend. At most 9 atoms.
- `RYD(rabi_freq, detuning, dt)` applies one step of the global Rydberg
  pulse, in units normalized to a reference Rabi frequency of 1.0; a pulse
  is a sequence of such steps.

## Backend support

Legend: `G` the gate is in the backend type's catalogue `gateset` (OpenAPI:
"the primary gatesets supported by the backend"); `N` native (bold) on the
operational-specifics page; `D` accepted and decomposed per that page; `x`
listed as not allowed; `E` exercised in a retained run that completed; `F`
present in a retained run that failed; blank where no source states support.
Starmon-7 and Spin-2+ have no backend type in this account's catalogue
(offline, retired), so their columns are historical. Tuna-5, Tuna-9 and
Tuna-17 share one gateset and one page.

| Instruction | QX emulator | Tuna-5/9/17 | Ry emulator | Starmon-7 (retired) | Spin-2+ (offline) |
|---|---|---|---|---|---|
| `H` | G E | G D E | G F | D | D |
| `I` | G | G N | | N | D |
| `X`, `Y`, `Z` | G (X: E) | G N (X: E) | X, Z: G (X: E) | N | D |
| `X90`, `Y90` | G E | G N E | | N | N |
| `mX90`, `mY90` | G | G N | | N | N |
| `Z90`, `mZ90` | G | | | | |
| `S`, `Sdag`, `T`, `Tdag` | G | G N (S, Sdag: E) | S, T: G | N | D |
| `Rx`, `Ry` | G | G N | Rx: G | N | D |
| `Rz` | G | G N | G | D | N (virtual, zero time) |
| `Rn` | G | D | | | D |
| `U` | G | | | | |
| `CNOT` | G E | D E | G F | D | D |
| `CZ` | G | G N | | N | N |
| `CR`, `CRk` | G | D | | x | D |
| `SWAP` | G E | D E | | D | D |
| `CV`, `CY`, `DCNOT`, `ECR`, `ISWAP`, `InvSqrtSWAP`, `M`, `MS`, `SqrtISWAP`, `SqrtSWAP` | | | | | |
| `CCX`, `CSWAP` (Toffoli, Fredkin) | | x | | x | |
| gate modifiers `inv`, `pow`, `ctrl` | | | | | |
| `init` | G | G N | | N | implicit |
| `measure` | G E | G N E | implied at end | N | accepted and ignored; all measured at end |
| `reset` | G | G N | | N | x |
| `barrier` | G E | G E | | described | |
| `wait` | G E | G E (20 ns cycles) | | described (20 ns cycles) | |
| `asm` | | | `asm(Rydberg)` `INIT`, `RYD` | | accepted and ignored |
| Mid-circuit measurement | yes (qx-simulator 0.7.1) | yes | no | yes | no |

Catalogue limits per backend type (retrieved 2026-10-16, this account):

| Backend type (id, identifier) | Qubits | Shots max (default) | Job time limit | Default compiler passes | Primary gateset |
|---|---|---|---|---|---|
| QX emulator (1, `QXsinglenodesimulator`) | 10 | 2048 (1024) | 3600 s | none | H, I, S, Sdag, T, Tdag, X, X90, Y, Y90, Z, Z90, mX90, mY90, mZ90, Rx, Ry, Rz, U, Rn, CNOT, CR, CRk, CZ, SWAP, Hadamard, Identity, init, measure, reset, barrier, wait |
| Tuna-5 (4, `tuna_5`), Tuna-9 (6, `tuna_9`), Tuna-17 (7, `tuna_17`) | 5, 9, 17 | 131072 (8192) | 300 s | SWAP2CZDecomposer, CZDecomposer | I, Rx, X, X90, mX90, Ry, Y, Y90, mY90, Rz, Z, S, T, Sdag, Tdag, H, CZ, init, measure, reset, barrier, wait |
| Ry emulator (5, `Rydberg`) | 9 | 1024 (1024) | 3600 s | CNOTDecomposer, XZXDecomposer | X, Z, Rx, Rz, T, S, H, CNOT |

Every backend type carries `batchjobs_per_queue_limit` 5 and
`max_jobs_per_batch_job` 5 (C1).

Observations that bound the table:

- Tuna accepts gates outside its catalogue gateset: the retained Tuna-17
  teleport job used `CNOT`, `SWAP` and `H` and completed at 16384 shots
  (C5).
- The Ry emulator rejected a 9-qubit `H`/`CNOT` circuit with a `bit[9]`
  register ("error interpreting cQASM script") and accepted a 2-qubit
  `X`-only circuit without a bit register; which difference caused the
  rejection is open (C4).
- Rotation angles quantize on hardware: Tuna to multiples of pi/36 (5
  degrees), Starmon-7 to pi/28. Tuna native durations: 20 ns single-qubit
  gates, 60 ns `CZ`, 800 ns measurement, 500 or 200 us initialization;
  Starmon-7: 20 ns, 60 ns, 1 us, 150 us
  ([Tuna](site/kbase_tuna-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)),
  [Starmon-7](site/kbase_starmon-7-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/starmon-7-operational-specifics/))).
- Spin-2+ compiles every program to `X90`, `Rz` and `CZ` with McKay's
  method (at most three `Rz` and two `X90` per single-qubit sequence),
  accepts `qubit[1-4]` in a single declaration, SGMQ only for single-qubit
  gates, no `reset`
  ([site/kbase_spin-2-plus-operational-specifics.md](site/kbase_spin-2-plus-operational-specifics.md) ([live](https://www.quantum-inspire.com/kbase/spin-2-plus-operational-specifics/)),
  [spin_2plus](cqasm-spec/appendices/spin_2plus.md) ([live](https://qutech-delft.github.io/cQASM-spec/latest/appendices/spin_2plus.html))).

## Compilation

`RUN` in the web editor sends a program through every compile stage:
verification, decomposition, mapping, optimization, routing, scheduling
(unused), exporting and validation; verification and validation cannot be
skipped ([site/kbase_opensquirrel.md](site/kbase_opensquirrel.md) ([live](https://www.quantum-inspire.com/kbase/opensquirrel/))). The SDK
compiles without running through `qi files compile --file F
--backend-type-id N`, up to `--compile-stage` (default Decomposition)
([sdk/README.md](sdk/README.md) ([live](https://raw.githubusercontent.com/QuTech-Delft/quantuminspire/054a4f0be22983a5d515c31a24881bc0d875463d/README.md))). The passes each backend runs by default
are the catalogue's `default_compiler_config` (table above), not the
per-page lists the opensquirrel page points to (C18).
