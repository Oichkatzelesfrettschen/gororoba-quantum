> Full piece: [https://www.quantum-inspire.com/kbase/qi-tool/](https://www.quantum-inspire.com/kbase/qi-tool/)
> Retrieved 2026-10-16T22:24Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 8d08ce042c38c2d93d4866335baf56347d5dcdb74a925de227418bd6d3c5e7ad.

# QI Tool

Quantum Inspire offers a number of tools for programmatic access to the platform API. The suite consists of the following tools:

- A [QI tool](https://pypi.org/project/quantuminspire/) both for authentication and management of hybrid algorithms
- A [plugin](https://pypi.org/project/qiskit-quantuminspire) for for writing algorithms in the [Qiskit](https://qiskit.org/) quantum algorithm programming language
- A [plugin](https://pypi.org/project/pennylane-quantuminspire) for for writing algorithms in the [Pennylane](https://pennylane.ai/) quantum algorithm programming language

## QI tool

The [QI tool](https://pypi.org/project/quantuminspire/) is required both for authentication and management of hybrid algorithms.

In order for the SDK's to communicate with the Quantum Inspire API, the user needs to log in via the QI tool. For this, a convenience command line interface can be used.

To log in, the following commands should be used:

```shell
qi login
```

This command will log in the user and store the credentials in `~/.quantuminspire/config.json`. This configuration is automatically interpreted by both [qiskit-quantuminspire](#qiskit-plugin) and [pennylane-quantuminspire](#pennylane-plugin).

Next to authentication, the QI tool can also be used to upload cQASM or hybrid algorithms and fetch its results. This can either be done via the CLI:

```shell
qi files upload examples/hqca_script.py 3
qi results get <job_id>
```

or via the Python API:

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
