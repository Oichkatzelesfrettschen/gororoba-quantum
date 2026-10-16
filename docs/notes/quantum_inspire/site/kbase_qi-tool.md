> Full piece: [https://www.quantum-inspire.com/kbase/qi-tool/](https://www.quantum-inspire.com/kbase/qi-tool/)
> Retrieved 2026-10-16T22:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 a15c7b93725e5604dc01736a21b82a136abc10bffafa41bdee5c076f47e728f0.

# QI Tool

Quantum Inspire offers a number of tools for programmatic access to the platform API. The suite consists of the following tools:

- A [QI tool](https://pypi.org/project/quantuminspire/) both for authentication and management of hybrid algorithms
- A [plugin](https://pypi.org/project/qiskit-quantuminspire) for for writing algorithms in the [Qiskit](https://qiskit.org/) quantum algorithm programming language
- A [plugin](https://pypi.org/project/pennylane-quantuminspire) for for writing algorithms in the [Pennylane](https://pennylane.ai/) quantum algorithm programming language

## QI tool

The [QI tool](https://pypi.org/project/quantuminspire/) is required both for authentication and management of hybrid algorithms.

In order for the SDK's to communicate with the Quantum Inspire API, the user needs to log in via the QI tool. For this, a convenience command line interface can be used.

To log in, the following commands should be used:

This command will log in the user and store the credentials in `~/.quantuminspire/config.json`. This configuration is automatically interpreted by both [qiskit-quantuminspire](#qiskit-plugin) and [pennylane-quantuminspire](#pennylane-plugin).

Next to authentication, the QI tool can also be used to upload cQASM or hybrid algorithms and fetch its results. This can either be done via the CLI:

or via the Python API:

More information can be found on: <https://github.com/QuTech-Delft/quantuminspire>.
