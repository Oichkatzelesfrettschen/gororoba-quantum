# Planck Technologies (Planck QSaaS)

Planck Technologies (<https://www.plancktechnologies.xyz>) offers a
"quantum software as a service" API with an open-source platform and Python
SDK (<https://github.com/HectorNaaa/Planck-QSaaS>, SDK under `sdk/python`).
The read-only probe of 2026-10-24 found two facts that bound its use: the
stored key is rejected, and the platform's simulator returns random bits.

## Environment and credential

`planck-sdk` is not on PyPI (404), contrary to its README, so the lock
installs it from the audited source commit:

```sh
PL_ENV=$HOME/.local/share/planck/venv
uv venv --python 3.13 "$PL_ENV"
VIRTUAL_ENV="$PL_ENV" uv pip install -r docs/notes/planck/requirements-planck.txt
```

The SDK (version 1.0.0, MIT) uses the standard library only and contacts
only its configured base URL. Pass `base_url="https://www.plancktechnologies.xyz"`:
the bare domain answers 308, which breaks the SDK's POST health check. The
key is one line in `~/.config/planck/api-key` (directory 700, file 600),
sent as `X-API-Key`. The SDK and server allow one request every 3 s.

## What the probe established

- **The key is rejected.** `GET /api/quantum/executions` and
  `/api/quantum/digital-twin` answer "Invalid API key". The health ping
  answers `authenticated: true` for any well-formed key without a lookup,
  so it proves nothing. The stored key is 67 characters, while the README
  documents a 64-character key; regenerating it at
  `https://www.plancktechnologies.xyz/qsaas/settings` is the next step.
- **The simulator ignores the circuit.** In the platform source at commit
  `d57e32e7`, `simulateQuantumCircuit()` in
  `app/api/quantum/simulate/route.ts` draws every bit with
  `Math.random() < 0.5`, skews it by up to 10 percent for the
  `quantum_qpu` backend name, and never reads the gates. Every backend name
  (`auto`, `quantum_inspired_gpu`, `hpc_gpu`, `quantum_qpu`) goes through
  that function. This is read from the source, not from a deployed call.
- **Pricing disagrees with itself.** The landing page lists Starter at EUR 0
  with up to 20 qubits; the in-app billing page lists Starter at $29 a month
  with 1,000 runs and up to 8 qubits. No balance or quota endpoint exists.
- **Data terms.** Execution data is stored in the vendor's database, with
  benchmark and execution metrics collected by default (an opt-out exists),
  a 50 MB per-user storage cap, and retention for the life of the account
  (`/terms`, `/privacy`).

## Use in this repository

No Planck result enters analysis: a backend that ignores the submitted gates
measures nothing about the circuit. The account stays configured so a later
source revision can be re-audited against this one; a re-audit that finds a
real simulator or device path, and a key the API accepts, is the condition
for any case.
