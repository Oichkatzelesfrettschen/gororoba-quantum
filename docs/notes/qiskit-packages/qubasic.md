# qubasic

qubasic 0.34.0 (`python-qubasic`, console script `qubasic`, module
`qubasic_core`) is an interactive BASIC-dialect terminal that builds and
runs circuits on Aer. It offers statevector and density-matrix display,
noise models, LOCC protocols across separate registers, parameter sweeps,
and OpenQASM 2 and 3 import and export. Its runtime path calls Aer's
`SamplerV2`, `SetStatevector` and `quantum_info`, with an optional
qiskit-ibm-runtime backend.

## Hazards

The BASIC `SHELL` statement runs its argument with `subprocess.run(...,
shell=True)` outside agent mode, so a `.bas` program can run any command.
Run only programs written on this host. The other subprocess calls use
fixed argument lists: `nvidia-smi`, the clipboard tools, and an audio
player.

## Connections

- Executes on [qiskit-aer](qiskit-aer.md). Its GPU display reads
  `nvidia-smi`; Aer device selection follows
  [library-flags.md](../../runbooks/library-flags.md).
- OpenQASM 3 import uses qiskit-qasm3-import, as the core stack does.
