# Origin Quantum Cloud

Origin Quantum (<https://qcloud.originqc.com.cn>) serves the Wukong
superconducting QPUs and four simulators through the `pyqpanda3` SDK. The
website and the API sit on different hosts: the API is
`https://pyqanda-admin.qpanda.cn`. Documentation:
<https://qcloud.originqc.com.cn/document/usermanual-en/index.html> (user
manual) and <https://qcloud.originqc.com.cn/document/> (index). Every fact
below comes from the read-only probe of 2026-10-24 unless another source is
named; the live service stays the authority.

## Environment and credential

```sh
OG_ENV=$HOME/.local/share/originquantum/venv
OG_PYTHON=${OG_PYTHON:-$OG_ENV/bin/python}
uv venv --python 3.13 "$OG_ENV"
VIRTUAL_ENV="$OG_ENV" uv pip install -r docs/notes/originquantum/requirements-originquantum.txt
```

On the build host the Arch package `originquantum-stack` from the local PKGBUILD tree
(`~/Github/PKGBUILDs/originquantum-stack`) installs the same SDK as a hash-locked Python
3.13 environment under `/opt/originquantum-stack` and the interpreter `/usr/bin/originquantum-python`
(pyqpanda3 0.5.0); its `check()` runs an offline test, kept at
`/usr/share/originquantum-stack/test_originquantum_stack.py`. A case sets `OG_PYTHON=/usr/bin/originquantum-python`; the venv
above serves a machine without the package. pyqpanda3 0.5.0 also publishes cp314 wheels; its runtime dependencies (matplotlib, scipy, mypy, Cython, networkx) make the environment large. OriginQ publishes an agent skill (OriginQ/pyqpanda3-skill, 5.9 MB) whose installer writes rule files into the working directory and global commands; it stays uninstalled until reviewed in full.

The lock pins `pyqpanda3` 0.5.0, a compiled wheel. The API key is one line
in `~/.config/originquantum/api-key` (directory 700, file 600), read inside
Python. `QCloudService` defaults to the cleartext
`http://pyqanda-admin.qpanda.cn`, so every call passes the HTTPS URL:

```python
from pyqpanda3 import qcloud
svc = qcloud.QCloudService(api_key=key, url="https://pyqanda-admin.qpanda.cn")
```

The website host answers the SDK with HTML (`RuntimeError: Invalid value.`).
Updating a key in the console invalidates every tool using the old one.

## API surface

`QCloudService.backends()` returns each backend name with an availability
flag, and `backend(name).chip_info()` returns a QPU's qubits, basic gates,
gate timings, topology and per-qubit and per-pair calibration. No call reads
the balance or the job list.

## Backends (2026-10-24)

| Backend | Kind | Qubits | Available | Calibration means |
|---|---|---|---|---|
| `WK_C180` | Wukong 180 QPU, gates `RPhi`, `CZ` | 166 usable of 180, 336 CZ pairs | yes | CZ 0.978, 1Q 0.993, readout 0.873, T1 35 |
| `WK_C180_2` | 17-qubit region of the same chip | 17 | yes | CZ 0.976, readout 0.954 |
| `WK_C180_3` | 30-qubit region | 30 | yes | CZ 0.973, readout 0.931 |
| `PQPUMESH8` | 3-qubit device (the docs' optical prototype, inferred) | 3 | yes | CZ 0.959 |
| `HanYuan_01` | 100-qubit QPU | 100 | no | single-qubit data only |
| `full_amplitude`, `partial_amplitude`, `single_amplitude` | simulators | 35, 68, 200 | yes | |

A noise simulator of 34 qubits appears in the docs but not in `backends()`.

## Allotment and limits

| Item | Value | Source |
|---|---|---|
| Registration grant | 60 s of Wukong machine time | user manual 3.1, Usage and machine time |
| Invitation grant | 30 s each to inviter and invitee, no cap on invitees | same |
| Order | free machine time is consumed first; each grant reads Active, Exhausted or Expired | same |
| Reset | none stated; no expiry length for the 60 s grant | same |
| Usage formula | usage = 0.3 s fixed overhead times the device multiplier (1 for Wukong 180) plus QPU runtime; a batch job pays the overhead once | same |
| Paid machine time | CNY 600 a minute below 30 min, falling to 360 a minute at 1500 to 3000 min; non-refundable | user manual 3.3, Buying machine time |
| Simulators | free: full-amplitude 35 qubits noise-free, noise 34, partial-amplitude 68, single-amplitude 200 | user manual 2.8 |
| Shots, depth | per-device values shown in the console, not in the docs | user manual 4.3 |

This key's remaining free seconds are unreadable through the SDK; the
console shows them.

## Data terms

The site footer links a Service Agreement and a Privacy Policy whose text
renders client-side and was not read. Nothing confidential is submitted.

## Use in this repository

The 60 s grant buys about 50 jobs of one second each under the usage
formula, so a Wukong run is a short, device-specific case: a question about
a 180-qubit square-type CZ lattice that the repository's other devices
cannot answer. It waits for the owner's approval of a written case (root
AGENTS.md, "Hardware services") that states its expected machine seconds by
the formula above. No adapter exists yet; a first run adds one with its
retained-run directory under `results/originquantum/`.
