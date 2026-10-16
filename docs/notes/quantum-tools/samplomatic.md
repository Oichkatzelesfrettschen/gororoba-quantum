# samplomatic

## NAME

samplomatic 0.21.0 -- boxed circuits to a template plus a samplex that draws
randomizations (Pauli twirling, basis changes, noise injection) at sampling
time.

## SYNOPSIS

```python
from samplomatic import build, Twirl
with qc.box([Twirl()]):
    qc.cz(0, 1)
template, samplex = build(qc)
out = samplex.sample(num_randomizations=3, rng=1)   # SamplexOutput
```

| Substrate | Status |
| --- | --- |
| Build host | python-samplomatic 0.21.0 (Arch) |
| Kaggle | not pinned by name; `samplomatic>=0.21.0` is a hard requirement of `qiskit-ibm-runtime` (host package metadata), so the `quantum-tools` group pulls it in through pip; not measured on a kernel |

## CAPABILITIES IN THIS REPOSITORY

- The client-side `Sampler` of qiskit-ibm-runtime 0.50 twirls through
  samplomatic; the package is the 0.50 floor in `requirements.txt` and the
  root AGENTS.md. A boxed circuit builds into a template with one `rz`/`sx`
  parameter group per twirled gate and a samplex that fills the parameters
  and the measurement bit-flip corrections.
- Understanding twirl overhead: the example shows `parameter_values` of
  shape (randomizations, 12) and `measurement_flips.c` of shape
  (randomizations, 1, 2) for one `cz` plus a measurement box.
- Annotations: `Twirl`, `ChangeBasis`, `InjectNoise`, `Tag`.
- Not covered: running anything on hardware, and dynamic circuits (the root
  AGENTS.md records that boxing rejects `if_else`; a minimal `if_test` inside
  a box attempted here failed on an unterminated virtual gate, which does not
  isolate `if_else` as the cause, so the AGENTS.md statement is cited, not
  reproduced).

## API ENTRY POINTS

`samplomatic` public names (28), by introspection:

classes:

```text
  ChangeBasis, InjectNoise, Tag, Twirl
```

functions:

```text
  build
```

modules:

```text
  aliases, annotations, builders, constants, distributions, exceptions,
  graph_utils, optionals, partition, pre_samplex, quantum_program, samplex,
  serializable, serialization, ssv, synths, tables, tensor_interface,
  trace_info, transpiler, utils, virtual_registers, visualization
```

## EXAMPLES

```python
import importlib.metadata as md
import samplomatic
from samplomatic import Twirl, build
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
with qc.box([Twirl()]):
    qc.cz(0, 1)
with qc.box([Twirl()]):
    qc.measure([0, 1], [0, 1])
template, samplex = build(qc)
print("samplomatic", md.version("samplomatic"))
print("template ops:", dict(template.count_ops()))
print("samplex inputs: ", samplex.inputs())
out = samplex.sample(num_randomizations=3, rng=1)
print("parameter_values shape:", out["parameter_values"].shape, " measurement_flips.c shape:", out["measurement_flips.c"].shape)
```

Output:

```text
samplomatic 0.21.0
template ops: {'rz': 12, 'sx': 8, 'barrier': 6, 'measure': 2, 'cz': 1}
samplex inputs:  TensorInterface(<>)
parameter_values shape: (3, 12)  measurement_flips.c shape: (3, 1, 2)
```

## INTEROP WITH QISKIT

Input is a `QuantumCircuit` with `box` contexts annotated by samplomatic
annotations; output is a template `QuantumCircuit` (the template's
`global_phase` is zero, per the `build` docstring) and a `Samplex`.

## CPU AND GPU

CPU (NumPy sampling; `max_workers` parameter on `sample`).

## TRAPS

- A twirl box on a gate needs a collector later in the circuit: boxing only a
  `cz` raised `SamplexBuildError: There are unterminated virtual gates travelling
  to the right on qubit indices [0, 1]. Did you forget to add collectors?` and
  adding a box that holds the measurement fixed it.
- The template drops the input `global_phase`.
- `max_workers` and `rng` control the sampling; pass `rng=<int>` to replay.

## LICENSE

Apache-2.0.
