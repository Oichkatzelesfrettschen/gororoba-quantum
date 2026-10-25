# Quafu (BAQIS ScQ cloud)

Quafu (<https://quafu.baqis.ac.cn/>), run by the Beijing Academy of Quantum
Information Sciences, serves superconducting QPUs and a 10-qubit simulator to
public users through the `pyquafu` SDK (docs <https://scq-cloud.github.io/>,
source <https://github.com/ScQ-Cloud/pyquafu>). Every fact below comes from
the read-only probe of 2026-10-24 unless another source is named; the live
service stays the authority.

## Environment and credential

```sh
QF_ENV=$HOME/.local/share/quafu/venv
QF_PYTHON=${QF_PYTHON:-$QF_ENV/bin/python}
uv venv --python 3.12 "$QF_ENV"
VIRTUAL_ENV="$QF_ENV" uv pip install -r docs/notes/quafu/requirements-quafu.txt
```

On the build host the Arch package `quafu-stack` from the local PKGBUILD tree
(`~/Github/PKGBUILDs/quafu-stack`) installs the same SDK as a hash-locked Python
3.11 environment under `/opt/quafu-stack` and the interpreter `/usr/bin/quafu-python`
(pyquafu 0.4.5 with numpy 1.26.4); its `check()` runs an offline test, kept at
`/usr/share/quafu-stack/test_quafu_stack.py`. A case sets `QF_PYTHON=/usr/bin/quafu-python`; the venv
above serves a machine without the package. pyquafu still pins `numpy<2` on its master branch, and upstream issue ScQ-Cloud/pyquafu#179 records the import failure under numpy 2, so the package runs Python 3.11, where every pin installs from a published wheel.

The lock pins `pyquafu` 0.4.5, which requires `numpy<2` (1.26.4 here).
NumPy 1.26.4 ships wheels for CPython 3.9 to 3.12 only, so the environment
runs Python 3.12; on 3.13 the install falls back to a source build. The
API token is one line in `~/.config/quafu/api-token` (directory 700, file
600), read inside Python and sent as the header `api_token: <token>`.
`User(api_token=...)` writes no token file when the token is passed in; the
SDK's own token directory stays unused.

## API surface

| Call | Returns |
|---|---|
| `POST qbackend/get_backends/` | every backend: name, id, qubits, status, queue length, valid gates |
| `POST qbackend/scq_get_chip_info/` (form `system_name`) | qubit and coupler calibration, topology, basis gates, calibration time |

Submission (`scq_kit`, `scq_kit_asyc`) and recall (`scq_task_recall`) are
the only other token routes. The per-user quota, task list and profile live
behind the website's browser session (`/web/user/userInfo/` and others) and
are not readable with the token.

## Backends (2026-10-24)

| Backend | Kind | Qubits | Status | Queue | Latest calibration |
|---|---|---|---|---|---|
| ScQ-Sim10 | simulator | 10 | Online | 0 | 2023-11-15 |
| ScQ-P5 | QPU | 5 | Online | 1752 | 2026-02-27 |
| Baihua | QPU | 119 (156 in chip info) | Online | 475 | 2024-10-30 |
| ScQ-P10, ScQ-P21, ScQ-P3, ScQ-TEST, Dongling, Haituo | QPU | 10, 11, 3, 3, 105, 105 | Offline | | 2024 to 2025 |
| ScQ-P18, Baiwang, ScQ-P102, Miaofeng, Yunmeng, Xiang, ScQ-Sim | QPU or simulator | | Obsolete | | |

Native gates on the online QPUs include `cx`, `cz`, `rx`, `ry`, `rz` and
the Paulis; the API returns Baihua's gate list as malformed string
fragments, and `QV` and `clops` read 0 or null everywhere.

## Allotment and limits

The token API exposes no balance, quota or reset cycle, and no page
publishes a daily limit, a shot maximum, a runtime limit or a price. The
service describes itself as open access ("shares open access to
super-conducting quantum (ScQ) computing resources with public users from
all around the world", <https://scq-cloud.github.io/>), and the web app
directs requests for more quota to quafu-support@baqis.ac.cn. The SDK
defaults to 1000 shots. The account's quota is read in the browser.

## Data terms

No terms, privacy policy, retention statement or license for submitted
circuits was found; the site renders its pages after login. Nothing
confidential is submitted.

## Use in this repository

The online devices are a 5-qubit chip with a queue above 1700 jobs and a
119-qubit chip whose calibration predates this probe by two years, so a
Quafu run answers a question about one of those devices itself and states
the queue and calibration age in its case. It waits for the owner's approval
of a written case (root AGENTS.md, "Hardware services"). No adapter exists
yet; a first run adds one with its retained-run directory under
`results/quafu/`.
