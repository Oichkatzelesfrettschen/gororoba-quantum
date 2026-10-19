> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/tutorial_rem_workflow_highlevel.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/tutorial_rem_workflow_highlevel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 40f515987dae688386d0618b0dff07de4203257b64026f3ae8ff8221754752fd.

# Tutorial: REM Workflow (High-Level API)

This tutorial demonstrates the high-level `REMWorkflow` API, which combines readout error characterization, circuit twirling, and postprocessing into a single, easy-to-use interface.

The workflow consists of three phases that happen automatically:

1.  **Readout error characterization** — calibration circuits are submitted to characterize qubit readout errors.

2.  **Twirled circuit execution** — input circuits are randomized (twirled) and submitted.

3.  **Postprocessing** — counts are untwirled, mitigated using the characterization data, and packaged into mitigated probability distributions.

The `REMWorkflow` class handles all three steps behind a clean API.

```
import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit.result import sampled_expectation_value

from iqm.qiskit_iqm import IQMProvider

# High-level REM API
from iqm.error_reduction_tools.rem import REMWorkflow, WorkflowConfiguration
from iqm.error_reduction_tools.twirling.twirling_api import TwirlingConfiguration
from iqm.error_reduction_tools.readout_characterization import RECConfiguration

# For comparison
from iqm.error_reduction_tools.utils.general_utils import total_variational_distance
```

## 1. Backend and target circuit

We connect to the QC and create a simple circuit dominated by readout errors.

```
server_url = "https://resonance.iqm.tech"
quantum_computer = "garnet"
api_token = ""

if not api_token:
    raise RuntimeError("Set IQM_TOKEN in the environment before running this notebook.")

provider = IQMProvider(url=server_url, token=api_token,quantum_computer=quantum_computer)
backend = provider.get_backend()

iqm_client = backend.client
```

```
def generate_circuit(num_qubits, scale=2, seed=None):
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
        format(i, f"0{num_qubits}b"): float(p) for i, p in enumerate(probs) if p > 1e-15
    }

    qc.measure_all()
    return qc, ideal_counts


target_circuit, exact_counts = generate_circuit(num_qubits=4, seed=0)
transpiled_circ = transpile(
    target_circuit, backend=backend, initial_layout=np.arange(1, 5)
)
transpiled_circ.draw("mpl", fold=0)
```

## 2. Option A: Full run (no previous characterization)

The simplest usage: create a workflow, submit circuit(s), and get mitigated results. Readout error characterization is run automatically.

```
# Configure the workflow
config = WorkflowConfiguration(
    shots=20_000,
    twirling=TwirlingConfiguration(readout_twirl_strategy="LOCAL", seed=42),
)

workflow = REMWorkflow(iqm_client, config=config)
workflow.submit([transpiled_circ])

# Job ids are available right after submit(), before results are retrieved.
print(f"Submitted job ids: {workflow.get_job_ids()}")

results = workflow.get_results()

print("Mitigated quasi-probabilities (first circuit):")
print(dict(sorted(results.mitigated_distributions[0].items(), key=lambda x: -x[1])[:10]))
print(f"\nCharacterization reused: {results.metadata.characterization_reused}")
```

### Save characterization for later reuse

The characterization data can be saved and loaded to avoid re-running calibration.

```
# Path for saving/loading characterization data
charact_file = "charact.json"
results.characterization.save(charact_file)
print("Characterization saved to "+ charact_file)
```

## 3. Option B: Reuse previous characterization

Pass the saved characterization file to skip the REC step entirely.

```
results_reused = REMWorkflow(iqm_client, config=config, characterization=charact_file).run([transpiled_circ])

print("Mitigated quasi-probabilities (reused characterization):")
print(dict(sorted(results_reused.mitigated_distributions[0].items(), key=lambda x: -x[1])[:10]))
print(f"\nCharacterization reused: {results_reused.metadata.characterization_reused}")
```

## 4. Option C: Notebook one-liner

For quick experiments, the entire workflow fits in a single line.

```
results_oneliner = REMWorkflow(iqm_client).run([transpiled_circ])

print("One-liner mitigated quasi-probabilities:")
print(dict(sorted(results_oneliner.mitigated_distributions[0].items(), key=lambda x: -x[1])[:10]))
```

## 5. Observable estimation

Pass Pauli-string observables to get expectation values directly.

```
observables = ["ZZII", "IZZI", "IIZZ"]

results_obs = REMWorkflow(
    iqm_client, config=config, characterization=charact_file
).run([transpiled_circ], observables=observables)

print("Expectation values:")
for obs, val in zip(observables, results_obs.expectation_values[0]):
    print(f"  {obs}: {val:.4f}")
```

## 6. Comparison with unmitigated results

We compare the high-level REM workflow against raw (unmitigated) results to demonstrate the improvement.

```
# Run the circuit without REM for comparison
standard_counts = backend.run(transpiled_circ, shots=20_000).result().get_counts()

tvd_standard = total_variational_distance(standard_counts, exact_counts)
tvd_mitigated = total_variational_distance(results.mitigated_distributions[0], exact_counts)
tvd_raw_twirled = total_variational_distance(results.raw_counts[0], exact_counts)

labels = ["Raw (no twirl)", "Twirled raw", "Twirled REM"]
values = [tvd_standard, tvd_raw_twirled, tvd_mitigated]
colors = ["tab:blue", "tab:orange", "tab:purple"]

plt.figure(figsize=(7, 4))
bars = plt.bar(labels, values)
for bar, v, color in zip(bars, values, colors):
    bar.set_color(color)
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{v:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.ylabel("Total Variational Distance (TVD)")
plt.title("Sampling task: lower is better")
plt.ylim(0, max(values) * 1.3)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()
```

## 7. Metadata inspection

All workflow metadata is available on the results object.

```
meta = results.metadata
print(f"Timestamp:               {meta.timestamp}")
print(f"Shots:                   {meta.shots}")
print(f"Twirling strategy:       {meta.twirling_strategy}")
print(f"Characterization reused: {meta.characterization_reused}")
print(f"Characterization job id: {meta.characterization_job_id}")
print(f"Twirling job id:         {meta.twirling_job_id}")
print(f"REC config:              {meta.rec_config}")
print(f"Twirling config:         {meta.twirling_config}")
```
