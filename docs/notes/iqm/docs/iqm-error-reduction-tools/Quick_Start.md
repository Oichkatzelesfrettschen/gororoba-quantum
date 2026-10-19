> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/Quick_Start.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/Quick_Start.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1573ca91bad6715a56ecdd0e6bc14936878f60f090b4c9ea817391885178d4c7.

# Quick Start Guide for IQM Error Reduction Tools

IQM Error Reduction Tools is a library providing techniques to avoid noise and mitigate errors in quantum computation. It operates by postprocessing measurement results after the execution to improve their accuracy. With this library, you can:

- apply readout error mitigation (REM) to correct measurement errors

- characterize readout noise and build calibration models

- use Pauli twirling to tailor noise into more tractable forms

- combine all steps into a unified workflow via the high-level `REMWorkflow` API

This notebook walks through the minimal steps to get started. For a deeper dive into each technique, see `tutorial_rem_workflow_highlevel.ipynb` and the other tutorials in this docs folder.

## Authentication

IQM uses bearer token authentication to manage access to quantum computers. Get your personal token from the web dashboard and pass it when constructing the backend objects:

``` python
server_url = "https://<your-station-url>"
api_token = "<YOUR TOKEN HERE>"
```

Alternatively, set the `IQM_TOKEN` environment variable and omit the `token` argument.

```
import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

from iqm.qiskit_iqm import IQMProvider

from iqm.error_reduction_tools.rem import REMWorkflow, WorkflowConfiguration
from iqm.error_reduction_tools.twirling.twirling_api import TwirlingConfiguration
from iqm.error_reduction_tools.utils.general_utils import total_variational_distance
```

```
provider = IQMProvider(url="your_server_url", token="your_api_token")
backend = provider.get_backend()
iqm_client = backend.client
```

```
def generate_circuit(
    num_qubits: int, scale: float = 2, seed: int = None
) -> tuple[QuantumCircuit, dict[str, float]]:
    """Generate a circuit with a single layer of random R gates."""
    rgen = np.random.default_rng(seed)
    rotations = (
        np.pi
        / 2
        * (1 + np.tanh(scale * (rgen.random(num_qubits) - 0.5) * 2) / np.tanh(scale))
    )
    qc = QuantumCircuit(num_qubits)
    for q, theta in enumerate(rotations):
        qc.r(theta, 0, q)
    probs = Statevector.from_instruction(qc).probabilities()
    ideal_counts = {
        f"{i:0{num_qubits}b}": float(p)
        for i, p in enumerate(probs)
        if p > 1e-15
    }
    qc.measure_all()
    return qc, ideal_counts


target_circuit, exact_counts = generate_circuit(num_qubits=4, seed=0)
transpiled_circ = transpile(
    target_circuit, backend=backend, initial_layout=np.arange(1, 5)
)
transpiled_circ.draw("mpl", fold=0)
```

## Run the REM Workflow

The simplest usage is a single call to `REMWorkflow.run()`. It automatically:

1.  Runs readout error characterization circuits on the QPU.

2.  Twirls and executes your circuits.

3.  Post-processes the counts to produce mitigated results in the form of mitigated distributions of probabilities (or quasi-probabilities if `nearest_prob_distribution` is `False` in `WorkflowConfiguration`).

For finer control (e.g. reusing a saved characterization, setting shot counts, or choosing a twirling strategy), see `tutorial_rem_workflow_highlevel.ipynb`.

```
# One-liner: characterization + twirled execution + mitigation in a single call
results = REMWorkflow(iqm_client).run([transpiled_circ])

print("Mitigated quasi-probabilities:")
print(dict(sorted(results.mitigated_distributions[0].items(), key=lambda x: -x[1])[:10]))
```

```
# Compare mitigated results against raw (unmitigated) execution
raw_counts = backend.run(transpiled_circ, shots=10_000).result().get_counts()

tvd_raw = total_variational_distance(raw_counts, exact_counts)
tvd_mitigated = total_variational_distance(results.mitigated_distributions[0], exact_counts)

labels = ["Raw (no REM)", "Twirled + REM"]
values = [tvd_raw, tvd_mitigated]
colors = ["tab:blue", "tab:green"]

plt.figure(figsize=(5, 4))
bars = plt.bar(labels, values, color=colors)
for bar, v in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{v:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )
plt.ylabel("Total Variational Distance (TVD)")
plt.title("Lower TVD = closer to ideal")
plt.ylim(0, max(values) * 1.4)
plt.tight_layout()
plt.show()
```

## Next Steps

- **`tutorial_rem_workflow_highlevel.ipynb`** — reusing characterization, observable estimation, workflow metadata

- **API reference** — full documentation of `REMWorkflow`, `WorkflowConfiguration`, and `TwirlingConfiguration`
