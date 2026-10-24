# IonQ Quantum Cloud

IonQ serves trapped-ion QPUs (Forte) and a cloud simulator with IonQ noise
models through one REST API, `https://api.ionq.co/v0.4`
(<https://docs.ionq.com>; page index <https://docs.ionq.com/llms.txt>). The
account holds a simulator-only key: it has no QPU credit, so this guide
covers the simulator and the read-only surface. Every fact below comes from
the read-only probe of 2026-10-24 unless another source is named; the live
API and docs stay the authority.

## Environment and credential

```sh
IONQ_ENV=$HOME/.local/share/ionq/venv
IONQ_PYTHON=${IONQ_PYTHON:-$IONQ_ENV/bin/python}
uv venv --python 3.13 "$IONQ_ENV"
VIRTUAL_ENV="$IONQ_ENV" uv pip install -r docs/notes/ionq/requirements-ionq.txt
```

The lock pins `qiskit-ionq` 1.1.1 with Qiskit 2.6.1. The key is one line in
`~/.config/ionq/api-key` (directory 700, file 600), read inside Python and
sent as `Authorization: apiKey <key>`; it never enters a command line, a
log or a commit.

## API surface

| Call | Returns |
|---|---|
| `GET /whoami` | key id and name, project id |
| `GET /backends`, `GET /backends/{id}` | status, qubits, queue time, native gates, error mitigations, noise models (simulator) |
| `GET /backends/{id}/characterizations` | dated SPAM, 1Q and 2Q fidelity, timings, connectivity (213 pages of history for Forte-1) |
| `GET /jobs` | job list (empty) |
| `GET /jobs/estimate?backend=..&qubits=..&shots=..&1q_gates=..&2q_gates=..` | a cost estimate in credits; creates nothing |

Organization usage (`/organizations/{organization_id}/usage`) needs the
full organization id, which the key does not return, and credit balances
are visible only to organization admins in the console. Responses carry
`ratelimit-limit: 500` per second.

## Backends (2026-10-24)

| Backend | Kind | Qubits | Status | Use by this account |
|---|---|---|---|---|
| `simulator` | cloud simulator; noise models `ideal`, `aria-1`, `aria-2`, `forte-1`, `forte-enterprise-1` | 29 (25 with the Aria models) | available | yes, free |
| `qpu.forte-1` | trapped-ion QPU, all-to-all (630 pairs), native `gpi`, `gpi2`, `zz` | 36 | available | no QPU credit |
| `qpu.forte-enterprise-1`, `qpu.forte-enterprise-3` | QPU | 36 | unavailable | no |
| `qpu.aria-1`, `qpu.aria-2`, `qpu.harmony` | QPU | 25, 25, 11 | retired | no |

The docs list `qpu.forte-enterprise-1` as available and omit
`qpu.forte-enterprise-3`; the API is the authority for status.

## Allotment and limits

| Item | Value | Source |
|---|---|---|
| Simulator | free to every account up to 29 qubits, noise models included; no reset cycle, since it is not metered | docs `user-manual/accounts.md` |
| QPU | needs organization credit; a project budget of 0 blocks QPU jobs and still admits simulator jobs | docs `user-manual/projects.md` |
| QPU price | rate card `forte_on_demand`, 0.249 credits per compute second; a 5-qubit, 100-shot, 15-gate estimate on Forte-1 reads 0.731 credits | `GET /jobs/estimate` |
| Shots | at most 1,000,000 per job | OpenAPI `CircuitJobCreationPayload.shots` |
| Circuits | at most 5,000 per multicircuit job | OpenAPI `JsonMultiCircuitInput` |
| Runtime | a single-job timeout per backend (`TooLongPredictedExecutionTime`), no number published | docs v0.4 error codes |
| Inactivity | the account suspends after 180 days without login or API use | docs `accounts.md` |

## Data terms

The public terms (<https://ionq.com/terms>, revised 2019-08-06) govern the
website only, and the Cloud Console terms render client-side and were not
read. The privacy policy retains information "for so long as it may be
relevant" and reserves de-identified data for any purpose. Simulators run
on Google Cloud. Export: terms section 8.3 binds US export law. A job is
deletable (`DELETE /jobs/{id}`). Nothing confidential is submitted.

## Use in this repository

The cloud simulator is a noise-model simulator; the repository's routing
sends a simulation of 14 qubits or fewer to Kaggle or the build host (root
AGENTS.md, "QPU time and calibration"). An IonQ simulator job is warranted
when its question is IonQ's own noise model, and it waits for the owner's
approval of a written case like every provider job (root AGENTS.md,
"Hardware services"). No adapter or MCP server exists yet; a first run adds
one with its retained-run directory under `results/ionq/`.
