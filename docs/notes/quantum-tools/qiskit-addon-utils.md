# qiskit-addon-utils

## NAME

qiskit-addon-utils 0.4.0 -- helpers shared by the Qiskit addons: edge
coloring of coupling maps, circuit slicing, expectation-value and
noise-management utilities.

## SYNOPSIS

```python
from qiskit_addon_utils.coloring import auto_color_edges
from qiskit_addon_utils.slicing import slice_by_depth
```

| Substrate | Status |
| --- | --- |
| Build host | python-qiskit-addon-utils 0.4.0 (Arch) |
| Kaggle | not installed by the repository |

## CAPABILITIES IN THIS REPOSITORY

- Edge coloring of the CZ coupling graph: layers of parallel CZ gates for
  layered-gate and layer-fidelity style benchmarks. The 176 Kingston couplers
  color with 3 colors (example); `is_valid_edge_coloring` checks a coloring.
- Circuit slicing (`slice_by_depth`, `slice_by_barriers`, `slice_by_gate_types`,
  `slice_by_coloring`, `combine_slices`), the primitive behind per-layer noise
  learning and layer-wise fidelity reports.
- Submodules `exp_vals`, `noise_management`, `problem_generators` are present
  (not run).
- Not used by any repository module at present (`grep` finds no import in
  `gororoba_quantum/`).

## API ENTRY POINTS

`qiskit_addon_utils.coloring` public names (4), by introspection:

functions:

```text
  auto_color_edges, is_valid_edge_coloring
```

modules:

```text
  automatic_coloring, validation
```

`qiskit_addon_utils.slicing` public names (6), by introspection:

functions:

```text
  combine_slices, slice_by_barriers, slice_by_coloring, slice_by_depth,
  slice_by_gate_types
```

modules:

```text
  transpiler
```

## EXAMPLES

```python
import importlib.metadata as md
import json
from qiskit import QuantumCircuit
from qiskit_addon_utils.coloring import auto_color_edges, is_valid_edge_coloring
from qiskit_addon_utils.slicing import slice_by_depth

print("qiskit-addon-utils", md.version("qiskit-addon-utils"))
snap = json.load(open("docs/evidence/calibration/ibm_kingston.json"))
edges = sorted({tuple(sorted(r["qargs"])) for r in snap["instructions"]["cz"]})
coloring = auto_color_edges(edges)
print(len(edges), "couplers need", len(set(coloring.values())), "colors; valid:", is_valid_edge_coloring(coloring))

qc = QuantumCircuit(3)
qc.h(0); qc.cx(0, 1); qc.cx(1, 2); qc.h(2)
print("slices by depth 1:", [dict(s.count_ops()) for s in slice_by_depth(qc, 1)])
```

Output:

```text
qiskit-addon-utils 0.4.0
176 couplers need 3 colors; valid: True
slices by depth 1: [{'h': 1}, {'cx': 1}, {'cx': 1}, {'h': 1}]
```

## INTEROP WITH QISKIT

Takes `QuantumCircuit` objects and edge lists (verified in the example).

## CPU AND GPU

CPU.

## TRAPS

- The package metadata lists `pytest`, `jupyter-sphinx` and `ipywidgets` as
  hard requirements, so a pip install of it on a kernel pulls development
  packages.
- Coloring minimizes colors greedily; a coloring is valid, not unique.

## LICENSE

Apache-2.0.
