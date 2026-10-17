> Full piece: [https://www.quantum-inspire.com/kbase/software-development-kit/](https://www.quantum-inspire.com/kbase/software-development-kit/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 8845806457ac10d1e8bfd018f955fe26aff35018c34ea8c8c94a1c3ea0b6c353.

# Software Development Kit

Quantum Inspire offers a number of tools for programmatic access to the platform API. The suite consists of the following tools:

- A [QI tool](https://pypi.org/project/quantuminspire/) both for authentication and management of hybrid algorithms
- A [plugin](https://pypi.org/project/qiskit-quantuminspire) for for writing algorithms in the [Qiskit](https://qiskit.org/) quantum algorithm programming language
- A [plugin](https://pypi.org/project/pennylane-quantuminspire) for for writing algorithms in the [Pennylane](https://pennylane.ai/) quantum algorithm programming language

## QI tool

In order for the SDK's to communicate with the Quantum Inspire API, the user needs to log in via the QI tool. For this, a convenience command line interface can be used. To log in, the following commands should be used:

```shell
qi login
```

This command will log in the user and store the credentials in `~/.quantuminspire/config.json`. This configuration is automatically interpreted by both [qiskit-quantuminspire](#qiskit-plugin) and [pennylane-quantuminspire](#pennylane-plugin).

Next to authentication, the QI tool can also be used to upload cQASM or hybrid algorithms and fetch its results. This can either be done via the CLI

```shell
qi files upload examples/hqca_script.py 3
qi results get <job_id>
```

or via the Python API

```python
from quantuminspire.sdk.models.file_algorithm import FileAlgorithm
from quantuminspire.sdk.models.hybrid_algorithm import HybridAlgorithm
from quantuminspire.sdk.models.job_options import JobOptions
from quantuminspire.util.api.remote_backend import RemoteBackend

backend = RemoteBackend()
program: FileAlgorithm = HybridAlgorithm("", Path(name))
program.read_file(Path(name))
job_options = JobOptions(number_of_shots=1024, raw_data_enabled=true)
job_id = backend.run(program, backend_type_id=3, options=job_options)

sleep(10)

results = backend.get_results(job_id)
```

More information can be found on: <https://github.com/QuTech-Delft/quantuminspire>.

## Qiskit plugin

The [qiskit plugin](https://pypi.org/project/qiskit-quantuminspire/) offers support for Quantum Inspire within the Qiskit framework. By using the snippet below users can leverage all functionalities both within a quantum circuit and hybrid algorithm.

```python
from qiskit_quantuminspire.qi_provider import QIProvider

provider = QIProvider()

# Show all current supported backends:
print(provider.backends())

# Get Quantum Inspire's simulator backend:
backend = provider.get_backend("QX emulator")
```

More information can be found on: <https://qutech-delft.github.io/qiskit-quantuminspire>.

## Pennylane plugin

Quantum Inspire also offers support for Pennylane algorithms. The snippet below can be used in quantum circuits to connect to the Quantum Inspire backends.

```python
from pennylane_quantuminspire2.qi_device import QI2Device

# Show all current supported backends:
for backend in QI2Device.backends():
    print(f"{backend.name}")

# Get Quantum Inspire's simulator backend:
emulator_backend = QI2Device.get_backend("QX emulator")

# Instantiate a Pennylane device based on chosen backend
demo_device = QI2Device(emulator_backend)
```

More information can be found on: <https://qutech-delft.github.io/pennylane-quantuminspire2>.

[Previous](https://www.quantum-inspire.com/kbase/advanced-guide/) [Next](https://www.quantum-inspire.com/kbase/compilation/)
