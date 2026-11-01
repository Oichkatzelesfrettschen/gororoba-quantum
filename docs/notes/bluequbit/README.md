# BlueQubit

BlueQubit (<https://www.bluequbit.io>) serves CPU and GPU simulators and one
QPU route through `https://app.bluequbit.io/api/v1` and the `bluequbit`
SDK (platform docs <https://app.bluequbit.io/docs>, SDK reference
<https://app.bluequbit.io/sdk-docs/>). Every fact below comes from the
read-only probe of 2026-10-24 unless another source is named; the live pages
stay the authority.

## Environment and credential

The pinned SDK (`bluequbit` 0.19.0b1) installs from `requirements-bluequbit.txt` into the interpreter that `BQ_PYTHON` names. Every release on PyPI is a beta, and the SDK prints a beta warning and checks PyPI for a newer version at import. `bluequbit.init` sends `GET /jobs?limit=1` to validate the key. `bq.search()` raises `TypeError` on an account with no jobs, because `/jobs` returns `data: null`; read `/jobs` directly until a job exists. This account's credential location, MCP registration and access limits are recorded in the private gororoba-infrastructure repository.

## API surface

| Call | Returns |
|---|---|
| `GET /users/me` | profile and SDK token state (the token comes back in clear to its holder) |
| `GET /balance` | balance in USD and a promo flag |
| `GET /usage` | costs and payments by month |
| `GET /jobs` | job list; `data` is `null` on an empty account, which makes `bq.search()` raise `TypeError` |

No device, plan or quota endpoint exists; the devices are the SDK's fixed
set. `bq.estimate()` is a `POST /jobs` with `estimate_only`, so it counts
as a submission here and waits for approval.

## Devices and allotment

| Device | Kind | Qubits |
|---|---|---|
| `cpu` | statevector (qsim) | 34 |
| `mps.cpu` | matrix product state (quimb) | 96 |
| `pauli-path` | Pauli-path simulator | 192 |
| `gpu`, `mps.gpu`, `pauli-path.gpu` | GPU simulators | 34, 96, 192 |
| `quantum` | QPU; the docs name Rigetti Cepheus-1-108Q, the pricing page IBM Fez and Quantinuum H2 | 108 |

The QPU runs "9:00 AM to 7:00 PM and 9:00 PM to 7:00 AM, every day" (time zone
not stated).

SDK limits: 100,000 shots per job (1,000,000 on the MPS devices), batches of
up to 500 circuits, 10 queued CPU jobs, MPS bond dimension up to 2048 on
CPU.

The free-plan job counts and prices per device, the account's balance and the research-credit request path are recorded in the private gororoba-infrastructure repository.

## Data terms

No terms or privacy text is reachable: the app's `/terms` and `/privacy`
answer "Page Not Found" and the website footer links point to `#`. Nothing
confidential is submitted, and a run's circuits are treated as disclosed.

## Use in this repository

The 34-qubit statevector and the 96- and 192-qubit approximate simulators
reach past the build host's 31-qubit statevector, so a BlueQubit job is
warranted for a noiseless reference too wide for the host or Kaggle. It
waits for the owner's approval of a written case (root AGENTS.md, "Hardware
services"). No adapter exists yet; a first run adds one with its retained-run
directory under `results/bluequbit/`.
