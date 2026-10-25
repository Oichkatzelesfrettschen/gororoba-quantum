# BlueQubit

BlueQubit (<https://www.bluequbit.io>) serves CPU and GPU simulators and one
QPU route through `https://app.bluequbit.io/api/v1` and the `bluequbit`
SDK (platform docs <https://app.bluequbit.io/docs>, SDK reference
<https://app.bluequbit.io/sdk-docs/>). Every fact below comes from the
read-only probe of 2026-10-24 unless another source is named; the live pages
stay the authority.

## Environment and credential

```sh
BQ_ENV=$HOME/.local/share/bluequbit/venv
BQ_PYTHON=${BQ_PYTHON:-$BQ_ENV/bin/python}
uv venv --python 3.13 "$BQ_ENV"
VIRTUAL_ENV="$BQ_ENV" uv pip install -r docs/notes/bluequbit/requirements-bluequbit.txt
```

On the build host the Arch package `bluequbit-stack` from the local PKGBUILD tree
(`~/Github/PKGBUILDs/bluequbit-stack`) installs the same SDK as a hash-locked Python
3.13 environment under `/opt/bluequbit-stack` and the interpreter `/usr/bin/bluequbit-python`
(bluequbit 0.19.0b1); its `check()` runs an offline test, kept at
`/usr/share/bluequbit-stack/test_bluequbit_stack.py`. A case sets `BQ_PYTHON=/usr/bin/bluequbit-python`; the venv
above serves a machine without the package. Its isolation exists for the pinned pre-release alone; the SDK's requests and python-dateutil caps are satisfied by the system packages. `bq.search()` raises `TypeError` on an account with no jobs, because `/jobs` returns `data: null`; read `/jobs` directly until a job exists.

The lock pins `bluequbit` 0.19.0b1; every release on PyPI is a beta, and the
SDK prints a beta warning and checks PyPI for a newer version at import. The
key is one line in `~/.config/bluequbit/api-key` (directory 700, file 600),
read inside Python and passed to `bluequbit.init(key)`, which sends
`Authorization: SDK <key>`. The SDK also reads `BLUEQUBIT_API_TOKEN` and its
own `~/.config/bluequbit/config.json`; the repository uses neither.
`bluequbit.init` itself sends `GET /jobs?limit=1` to validate the key.

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

| Device | Kind | Qubits | Free plan | Price beyond |
|---|---|---|---|---|
| `cpu` | statevector (qsim) | 34 | 50,000 jobs a day, 60 min per job | free |
| `mps.cpu` | matrix product state (quimb) | 96 | 1,000 jobs a day, 15 min per job | $1 an hour, $0.20 minimum |
| `pauli-path` | Pauli-path simulator | 192 | 1,000 jobs a day, 15 min per job | $1 an hour, $0.20 minimum |
| `gpu`, `mps.gpu`, `pauli-path.gpu` | GPU simulators | 34, 96, 192 | credit only | $3 an hour |
| `quantum` | QPU; the docs name Rigetti Cepheus-1-108Q, the pricing page IBM Fez and Quantinuum H2 | 108 | credit only | $0.30 per job plus $0.000425 per shot |

Sources: the pricing page plan table and the platform docs' device table.
The daily job counts reset daily; neither page names the reset time or time
zone. The account reads balance $0, no promo and no spend, so it holds the
Free plan by inference, and only the three CPU simulators are usable. The
QPU runs "9:00 AM to 7:00 PM and 9:00 PM to 7:00 AM, every day" (time zone
not stated). Research credits are requested at credits@bluequbit.io.

SDK limits: 100,000 shots per job (1,000,000 on the MPS devices), batches of
up to 500 circuits, 10 queued CPU jobs, MPS bond dimension up to 2048 on
CPU.

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
