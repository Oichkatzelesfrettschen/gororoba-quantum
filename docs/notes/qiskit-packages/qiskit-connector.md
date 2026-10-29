# qiskit-connector

qiskit-connector 2.4.6 (`python-qiskit-connector`) picks the least-busy
IBM Quantum backend and prints its processor image. Its Qiskit surface is
`QiskitRuntimeService` and `IBMBackend`: `least_busy`, `backends`, `status`
and `processor_type`. The shipped LICENSE carries the Apache-2.0 terms
under an "All Rights Reserved" header, and its trailing note restricts
nothing that the Apache grant allows. The Arch package therefore records
`license=('Apache-2.0')`.

## Hazards on this host

- **Import loads `.env` and overrides the environment.** Importing
  `qiskit_connector` loads `./.env`, or else `~/.env`, with
  `override=True`. Any variable in such a file then replaces the process
  environment, `GOROROBA_IBM_ACCOUNT` and `PYTHON` included. No repository
  module imports the package.
- **`save_account()` replaces the default account.** It passes
  `IQP_API_TOKEN` to `QiskitRuntimeService.save_account(...,
  set_as_default=True, overwrite=True)`, which writes it into
  `~/.qiskit/qiskit-ibm.json` as the default account. On this host that
  replaces the primary account that every script uses when
  `GOROROBA_IBM_ACCOUNT` is unset. Never call it here.

The token travels only to IBM's endpoints. `requests` is imported but unused.

## Connections

- The repository already chooses backends against the live Target, from
  `service.backends()` and fresh calibration in live_run.py, with
  `--exclude-qubits`. "Least busy" answers a queue question and does not
  replace that selection.
- Its dependency set (runtime, python-dotenv, pillow, IPython) overlaps the
  system stack; it adds no Qiskit pins.
