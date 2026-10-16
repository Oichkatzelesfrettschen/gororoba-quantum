> Full piece: [https://www.quantum-inspire.com/kbase/software-development-kit/](https://www.quantum-inspire.com/kbase/software-development-kit/)
> Retrieved 2026-10-16T21:19Z by scripts/capture_qi_docs.py --site (urllib, pandoc);
> fetched HTML sha256 aade8826461914a8fafe8f0357a70887ca38323115dec1b005a0422c7b10ff86.

# Software Development Kit

Quantum Inspire offers a number of tools for programmatic access to the platform API. The suite consists of the following tools:

- A [QI tool](https://pypi.org/project/quantuminspire/) both for authentication and management of hybrid algorithms
- A [plugin](https://pypi.org/project/qiskit-quantuminspire) for for writing algorithms in the [Qiskit](https://qiskit.org/) quantum algorithm programming language
- A [plugin](https://pypi.org/project/pennylane-quantuminspire) for for writing algorithms in the [Pennylane](https://pennylane.ai/) quantum algorithm programming language

## QI tool

In order for the SDK's to communicate with the Quantum Inspire API, the user needs to log in via the QI tool. For this, a convenience command line interface can be used. To log in, the following commands should be used:

This command will log in the user and store the credentials in `~/.quantuminspire/config.json`. This configuration is automatically interpreted by both [qiskit-quantuminspire](#qiskit-plugin) and [pennylane-quantuminspire](#pennylane-plugin).

Next to authentication, the QI tool can also be used to upload cQASM or hybrid algorithms and fetch its results. This can either be done via the CLI

or via the Python API

More information can be found on: <https://github.com/QuTech-Delft/quantuminspire>.

## Qiskit plugin

The [qiskit plugin](https://pypi.org/project/qiskit-quantuminspire/) offers support for Quantum Inspire within the Qiskit framework. By using the snippet below users can leverage all functionalities both within a quantum circuit and hybrid algorithm.

More information can be found on: <https://qutech-delft.github.io/qiskit-quantuminspire>.

## Pennylane plugin

Quantum Inspire also offers support for Pennylane algorithms. The snippet below can be used in quantum circuits to connect to the Quantum Inspire backends.

More information can be found on: <https://qutech-delft.github.io/pennylane-quantuminspire2>.

[Previous](https://www.quantum-inspire.com/kbase/advanced-guide/) [Next](https://www.quantum-inspire.com/kbase/compilation/)
