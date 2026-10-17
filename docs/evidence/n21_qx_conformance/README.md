# Encoded N=21 feedback pair through cQASM export and QX semantics

The question: once the two dynamic circuits of
`results/live/2026-10-17T003834.987727Z/isa.qpy` (n21_encoded_feedback and
n21_encoded_no_feedback, seven active qubits on ibm_kingston) are written in a
form the QX emulator runs, do they keep their ideal recorded law? cQASM 3.0
has no binary-controlled gate, so the feedback arm's `if_else` runs on QX only
after deferral. Every law here is ideal (no noise model); nothing in this
directory says anything about Kingston or any other hardware.

`scripts/n21_qx_conformance.py` builds the programs, `result.json` retains
the record, and the three `.cq` files are the exact programs qxelarator ran.
Gate core-499 runs `--check` and `--self-test` in normal and optimized Python.
Its first `--check` carries `--live 0`: under the Quantum Inspire stack
(`$QI_PYTHON`) it reruns every reset probe, deferred state and native branch
run on qxelarator and requires the retained results; `--live N` adds N of the
24 sample jobs, each 2048 shots of a program of about 6000 lines and minutes of
qxelarator time. Without the stack the check replays the record.

## Method

- **Reference.** `dynamic_density.probabilities` with an empty noise model on
  each circuit restricted by `snapshot_laws.restrict_circuit` (physical qubits
  104, 105, 117, 124, 125, 126, 127 on QX q[0] to q[6], in that order).
  Feedback arm: 3/8, 1/4, 1/8, 1/4. No-feedback arm: 3/8, 1/8, 1/8, 3/8.
  Index r = c0 + 2 c1, clbit 0 least significant. Signed score
  P(r = 1) - P(r = 3): 0 and -1/4, so the contrast is +1/4.
- **Deferred form**, for both arms. Each arm measures q[5] into c0, resets
  q[5] and reuses it.
  - The measure becomes CNOT q[5] -> q[7], where q[7] is a fresh ancilla.
  - The reset becomes CNOT q[7] -> q[5], which returns q[5] to |0> because
    both qubits agree in Z after the copy.
  - The feedback arm's `if_else` body Rz(-pi/2) on q[1] becomes a controlled
    Rz from q[7]: Rz(-pi/4), CNOT, Rz(pi/4), CNOT.
  - Measurements move to the end: `b[0] = measure q[7]`, `b[1] = measure q[1]`.

  No native `reset` remains, so each deferred program is unitary until its
  final measurements.
- **Native form**, no-feedback arm only: `b[0] = measure q[5]`,
  `reset q[5]`, final `b[1] = measure q[1]`.
- **Lowering and export.** Explicit substitution to the qx gate map of
  `box_kite_cases.DIALECTS`:
  - SX = H S H exactly;
  - CRZ as above;
  - X, CZ, CNOT and Rz unchanged.

  The resulting programs declare `qubit[10]`, with q[8] and q[9] idle.
- **Stage laws.** The deferred circuit and the lowered circuit go through
  Statevector, a different engine from the reference. The parsed `.cq` text
  is re-read with `box_kite_cases.parse_cqasm` for its gate runs, while
  measure and reset lines are handled in the script. Every stage law equals
  the reference within 2e-13 (the 1e-9 tolerance is the gate's).
- **QX runs** (qxelarator 0.10.0, libqasm 1.2.1, Python 3.13.15, called
  through `$QI_PYTHON`; OpenSquirrel unused):
  - the exact final `state` of each deferred program without its measure
    lines;
  - 12 seeds of 2048 shots (24576 per program) for all three programs, with
    seed base + 1000 p + n;
  - eight single-shot runs of the native program without its final measure,
    each returning one mid-circuit branch state;
  - reset probes.

## Bit order

A QX key has one character per declared qubit, with qubit 0 rightmost, and
each character is that qubit's last measured outcome. A `reset` leaves the
character unchanged; the retained register probe reads q[0] = 1 in all 64
shots after `X`, `measure`, `reset`. The deferred programs read c0 from q[7]
and c1 from q[1]; the native program reads c0 from q[5] and c1 from q[1].

## Results

| Comparison | max probability gap | radius or tolerance | verdict |
| --- | --- | --- | --- |
| deferred feedback, QX exact state | 1.95e-13 | 1e-9 | equal |
| deferred no-feedback, QX exact state | 1.95e-13 | 1e-9 | equal |
| deferred pair, pooled QX counts vs reference | 0.00313, 0.00423 | Hoeffding 0.01403 | pass |
| native no-feedback, pooled QX counts vs reference | 0.15377 | Hoeffding 0.01403 | refuted |
| native no-feedback, pooled QX counts vs qxelarator reset model | 0.00432 | Hoeffding 0.01403 | pass |

| Score (P(01) - P(11)) | reference | QX deferred, exact | QX deferred, pooled (radius) | QX native, pooled |
| --- | --- | --- | --- | --- |
| feedback arm | 0 | 0 (2e-15) | -0.00525 (0.01905) | |
| no-feedback arm | -0.25 | -0.25 | -0.24984 (0.01789) | +0.05383 (model +0.05877) |
| contrast | +0.25 | +0.25 (1.3e-13 gap) | +0.24459 (0.03694) | -0.05908 |

Each pooled comparison is `n21_exact_model_validation.compare` at total tail
1e-3, which covers the simultaneous Hoeffding radius over 8 probabilities and
the Bernstein radii of both arm scores and the contrast. The probability
radius and the score checks each spend 1e-3, so one comparison rejects a true
law with probability at most 2e-3, and the two comparisons that must pass
(the deferred pair, and the native counts against the reset model) at most
4e-3 together. Each deferred QX state also has fidelity 1
(to 1e-9) with Aer's statevector of the same parsed program, global phase
aside.

## Finding: qxelarator 0.10.0 `reset` drops the register's phases

When the reset qubit carries weight on |1>, qxelarator's `reset` replaces
every amplitude pair (a0x, a1x) by the nonnegative real
sqrt(|a0x|^2 + |a1x|^2). This discards the phase of every other qubit, even in
a product state. When the qubit has no weight on |1>, the state is unchanged.
Three retained final-state probes pin the map:

| Probe | QX result | ideal reset |
| --- | --- | --- |
| `phase_minus`: q[0] = 1 beside q[1] = \|->, then reset | q[1] in \|+> | q[1] in \|-> (fidelity 0) |
| `already_zero`: q[1] = (\|0> + i\|1>)/sqrt2, reset q[0] = 0 | unchanged | unchanged |
| `general`: an entangled 3-qubit state | each pair's sqrt-merge, to 1e-15 | a mixture; no pure state |

The native no-feedback arm resets q[5] right after measuring it. In the
c0 = 1 branch, QX's state has fidelity 0 with the ideal branch state and
fidelity 1 with the model's, over the 4 single-shot runs that read c0 = 1;
the c0 = 0 runs match both. Under the model the native law is 3/8, 0.27938,
1/8, 0.22062, and the pooled counts sit within 0.0043 of it. The defect
therefore lies in the simulator's `reset`; the export, lowering and bit order
are excluded:

- the parsed native program's law equals the reference, which clears export
  and lowering;
- the c0 = 0 branch and both deferred programs match exactly;
- reading c0 from q[5] is confirmed by the register probe.

No QX dry-run case in the repository's Quantum Inspire generators writes
`reset`. The remote QX emulator's `reset` was not run, since this check
submits nothing.

## Angle grid

`box_kite_cases.emit` snaps every Rz to multiples of pi/64
(`ANGLE_GRID = 64`, tolerance 1e-9) in every dialect, and raises off that
grid. The lowered programs carry 878 Rz in the feedback arm (215 off-grid)
and 864 in the no-feedback arm (210 off-grid), with 126 distinct off-grid
values. `result.json` `angle_grid.rows` lists each failing Rz: its circuit,
instruction index, QX and physical qubit, and `repr` value.

The programs are therefore written with
`box_kite_cases.emit(circuit, place, dialect="qx", angle_grid=None)`, which
prints each Rz from its float with `.15f` in the qx dialect's gate names and
line formats. The self-test holds that export to the snapped one byte for
byte on an on-grid circuit.

## What this establishes

- The deferred-measurement form of each arm survives cQASM export and QX
  execution with its ideal law intact. This holds exactly from qxelarator's
  state and in sample (24576 shots per arm), and so does the +1/4 contrast.
- On qxelarator 0.10.0, a native mid-circuit `reset` before phase-sensitive
  gates does not implement the cQASM reset. Any QX reference for such a
  circuit is wrong unless the reset is replaced by a coherent uncompute, as
  the deferred form does.

It does not establish noise behavior, compiled timing, Tuna or Kingston
performance, or how the remote QX emulator behaves.
