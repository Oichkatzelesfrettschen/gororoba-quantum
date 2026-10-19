> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/Example%20-%20Executing%20QIR%20programs.html](https://docs.iqm.tech/4.7/iqm-pulla/Example%20-%20Executing%20QIR%20programs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f35fc7b9d15f7dfdf548eb9f1e639c9627c478d7b1f4999d9b5fba6025a1bc74.

# Executing QIR programs

If you have a QIR string or bitcode, you can start by converting it to an IQM-compatible circuit representation. You can also generate a QIR string or bitcode from a Qiskit circuit using IQM’s fork of `qiskit_qir`, available as the package `iqm-qiskit-qir`.

```
from qiskit import QuantumCircuit, visualization
from qiskit.compiler import transpile
from qiskit_qir import to_qir_module

from iqm.cpc.qir_utils import qir_to_iqm
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.pulse_level_utils import sweep_job_to_qiskit
from iqm.qiskit_iqm.qir_utils import generate_qiskit_qir_qubit_mapping
from iqm.iqm_client.util import print_env_vars
from iqm.station_control.interface.models import MoveGateFrameTrackingMode
```

```
# Create a qiskit-iqm backend for accessing the quantum computer.
print_env_vars()

provider = IQMProvider()
backend = provider.get_backend()
client = backend.client
compiler = client.get_standard_compiler()
```

```
# Define a quantum circuit (for visualization).
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure_all()
qc.draw(output='mpl')
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/e610f434a3c8bbe9ab19c09262bd84f466437f79a042080cee16bd8d6d1930f0.png)

```
# Transpile the circuit using Qiskit
qc_transpiled = transpile(qc, backend=backend, layout_method='sabre', optimization_level=3)
print(qc_transpiled.draw(output='text'))

#Generate the QIR
module, _ = to_qir_module(qc_transpiled, "BasicExecution")
qir = str(module)
```

```
               ┌─────────────┐                  ┌─────────────┐ ░       ┌─┐
      q_0 -> 2 ┤ R(π/2,3π/2) ├──────────■───────┤ R(π/2,5π/2) ├─░───────┤M├
               ├─────────────┤          │       └─────────────┘ ░ ┌─┐   └╥┘
      q_2 -> 0 ┤ R(π/2,3π/2) ├─■────────■───────────────────────░─┤M├────╫─
               ├─────────────┤ │ ┌─────────────┐                ░ └╥┘┌─┐ ║ 
ancilla_0 -> 1 ┤ R(π/2,3π/2) ├─■─┤ R(π/2,5π/2) ├────────────────░──╫─┤M├─╫─
               └─────────────┘   └─────────────┘                ░  ║ └╥┘ ║ 
       meas: 3/════════════════════════════════════════════════════╩══╩══╩═
                                                                   0  1  2 
```

```
# qiskit-qir has a bug, which causes qubit pointers to not be generated correctly
qubit_mapping = generate_qiskit_qir_qubit_mapping(qc_transpiled, backend)
```

## Executing QIR

```
# Pass qubit mapping to the qir_to_iqm converter to correctly interpret opaque qubit pointer indices in QIR
# and convert them to physical IQM qubit names.
circuits, _ = qir_to_iqm(compiler, qir, qubit_mapping)

# Get settings from the compiler
settings = compiler.get_settings(circuits=circuits)

# Configure settings as in other notebooks
settings.stages.timebox_stage.prepend_heralding.add_heralding = False
settings.stages.circuit_resolution.resolve_circuits.scheduling_strategy = "ASAP"
settings.stages.circuit_stage.subscribe_and_probe.convert_terminal_measurements = True
settings.stages.schedule_stage.apply_move_gate_phase_corrections.move_gate_frame_tracking_mode = MoveGateFrameTrackingMode.FULL
settings.stages.circuit_stage.subscribe_and_probe.probe_all = False

shots = 5000
settings.set_shots(shots)

# Compile and submit
job_definition, context = compiler.compile(circuits=circuits, settings=settings)
job_tracker = client.submit_playlist(job_definition, context=context)
job_tracker.wait_for_completion()

# Retrieve results using qiskit-iqm integration
qiskit_result = sweep_job_to_qiskit(job_tracker, shots=shots)
print(f"Qiskit result counts: {qiskit_result.get_counts()}")
visualization.plot_histogram(qiskit_result.get_counts())
```
