# Quantum Inspire setup: environment, login, CLI and Python routes

## Environment

The Quantum Inspire stack lives in its own interpreter because its pins
conflict with the repository's:

- quantuminspire 4.1.0, qi-compute-api-client 0.63.0 and
  qiskit-quantuminspire 0.18.5 declare `Requires-Python >= 3.10, < 3.14`;
  the repository and CI run Python 3.14.
- qiskit-quantuminspire 0.18.5 requires `qiskit >= 2.0, < 2.4` and resolves
  qiskit 2.3.1; the repository pins qiskit 2.5.2.
- pennylane-quantuminspire 0.15.5 requires Python >= 3.11 and
  PennyLane >= 0.43, < 0.46 (not installed here).
- No Arch package or local PKGBUILD carries quantuminspire.

```sh
uv venv --python 3.13 "$QI_ENV"
VIRTUAL_ENV="$QI_ENV" uv pip install -r docs/notes/quantum_inspire/requirements-qi.txt
"$QI_PYTHON" -c "import quantuminspire, qiskit_quantuminspire, qxelarator, mcp"
```

`QI_ENV` names the venv and `QI_PYTHON` its interpreter; their default locations are recorded in the private gororoba-infrastructure repository.

[requirements-qi.txt](requirements-qi.txt) is the full lock (Python 3.13.15,
uv 0.13.0, Linux x86_64). The direct packages and their roles are tabled in
the README section "Binding rules". The hosted gates never import
this stack: gates `core-record-check-05` (`capture_qi_docs.py` and `qi_crosstalk_teleport_cases.py` in
`tests/test_cli_record_checks.py`), core-347, core-330 and core-331 read
retained files with the standard library, and core-348 and core-340
regenerate with the pinned Qiskit stack. A venv that installs this
lock under Python 3.13.15 and exports `QI_PYTHON` runs the gates tagged
`"requires": ["qi"]` (core-368, core-423, core-527) over their live
paths, which recompile and re-emulate against the retained records, and
`GOROROBA_QI_REQUIRED=1` makes a gate that cannot take its live path fail,
since gororoba_quantum/qi_stack.py reads the environment alone.

On the pinned Linux x86-64 Python 3.13.15 environment, importing
OpenSquirrel 0.9.1 loads libqasm 1.2.1's SWIG extension. A local probe on
2026-10-28 UTC found that Python's `-W error` makes that import terminate with
signal 11; the Python fault trace ends in native extension creation. With
`-W default`, Python reports three missing-`__module__` deprecations for
`SwigPyPacked`, `SwigPyObject` and `swigvarlink`. The documented compiler
replay passes without `-W error`. The same replay also passes with warnings
treated as errors except for those three named deprecations:

```sh
"$QI_PYTHON" -B -W error \
  -W 'ignore:builtin type SwigPyPacked has no __module__ attribute:DeprecationWarning' \
  -W 'ignore:builtin type SwigPyObject has no __module__ attribute:DeprecationWarning' \
  -W 'ignore:builtin type swigvarlink has no __module__ attribute:DeprecationWarning' \
  scripts/qi_tuna_destination_sequential_cases.py --check
```

The debugger's main-thread backtrace reaches `SWIG_Python_NewPointerObj` from
`PyInit__libqasm` and faults in `_PyObject_New`. The host's system debug files
reported CRC mismatches, so that stack identifies a native call boundary rather
than an exact source statement. The probe ran `ulimit -c 0` followed by
`gdb -batch -ex run -ex 'thread apply all bt 12' --args "$QI_PYTHON" -B -W error -c 'import opensquirrel'`.
An instruction-level repeat on x86-64 showed `_PyObject_New` dereferencing
`0x20(%rdi)` with `rdi=0`, consistent with a null type argument at the fault;
the probe does not establish why the SWIG initializer passed it. The targeted filter isolates an observed
warning interaction; it does not identify the underlying native defect or
establish that other stack versions behave the same way. The existing
`qi_stack` probe already filters this SWIG warning family. The frozen compiler
producer remains unchanged. Provider execution and served scheduling are
outside the local replay.

## Login (OAuth device authorization)

```sh
"$QI_ENV/bin/qi" login
```

1. The CLI fetches the authorization settings from
   `https://api.quantum-inspire.com/auth_config` (client id, audience
   `compute-job-manager`, scopes `api-access openid profile email
   offline_access`, PKCE S256, the OpenID configuration at
   `https://auth.quantum-inspire.com/.well-known/openid-configuration`).
2. It prints `https://auth.quantum-inspire.com/activate?user_code=XXXX-XXXX`
   and the code, tries to open the browser, and polls; no localhost callback
   port is needed, so it works over ssh.
3. The user signs in (e-mail or a listed identity provider) and confirms the
   code; the CLI prints `Login successful! Using member ID N`.
4. The tokens land in the CLI's token store: access token (3600 s), refresh token, `generated_at`, and `team_member_id`. The CLI writes the file mode 644. The file never enters the repository, a log or agent memory. Its location is recorded in the private gororoba-infrastructure repository.

A login made in another OS user, container, WSL distribution or cloud VM
does not reach this environment. An agent that finds no login runs `qi
login` in the background, reads the URL and code from its output, and asks
the user to approve them in the browser; the code expires within minutes.
`qi logout` revokes the refresh token.

## Login failures

Every repository call, the MCP tools included, authenticates through
`Client` in `scripts/qi_platform.py`, so the error text identifies the
failure:

| Error text | Meaning | Action |
|---|---|---|
| `403 {"detail":"Signature has expired"}` | the request carried an expired access token; the API answers it with 403, not 401 | `Client` refreshes once and retries; from any other caller (curl, an SDK object), repeat the read through `qi_platform.py` or an MCP tool |
| `refresh token is no longer valid (invalid_grant)`, or the SDK's `403 {"error":"invalid_grant","error_description":"Unknown or invalid refresh token."}` | the login is dead for every process on the account | `"$QI_ENV/bin/qi" login --force`, approve the code, tighten the token file to mode 600 |
| `no Quantum Inspire login` | no tokens are stored | `"$QI_ENV/bin/qi" login` |
| an MCP tool outlives the client's wait | `qi_usage` pages every job of the account and takes minutes; authentication is fine | wait for the backgrounded result |

Plain `qi login` never recovers an invalid_grant. With tokens stored,
`Api.login` (quantuminspire/api.py) calls `AuthManager.refresh_tokens`,
which presents the stored refresh token again and keeps any rotated token
in memory without saving it. On a live login with an expired access token,
that call spends the refresh token and leaves the spent one in the file for
the next process. `--force` runs the device flow and writes fresh tokens.
A running MCP server needs no restart afterwards: `Client.refresh` rereads
the token file under the lock at every renewal, and `client()` in
`scripts/qi_mcp_server.py` keeps no client until one constructs.

**Renewal.** The access token lives 3600 s (`expires_in`), and without a
renewal every process would need a new device login each hour. `Client`
renews lazily: a request within `REFRESH_MARGIN` (120 s) of expiry calls
`Client.refresh`, which exchanges only once the stored access token is
within 5 s of expiry, so an idle process renews nothing. Every holder rereads
the file under the lock first, so all processes on the host share one
exchange per expiry, at most one an hour. Each exchange rotates the refresh
token, and a holder that presents the predecessor of the current one
presents a token the server has already retired. Through the lock one holder
exchanges and every other adopts the result, so a loss by reuse needs one of
the paths that skip the lock below; a short tenant lifetime would end the
login whatever the renewal path, and the exchange log tells the two apart.

**What spends a login.** The authorization server, auth.quantum-inspire.com
(an Auth0 tenant by its OpenID configuration), rotates the refresh token at
every exchange. `Client.refresh` holds the token-file lock,
rereads the file and writes the rotated pair back. Three paths exchange
outside that lock:

- `qi login` without `--force`, which saves nothing (above);
- qiskit-quantuminspire, `quantuminspire.api` and the `qi` remote commands,
  which refresh through `qi2_shared.authentication.OauthDeviceSession` and
  write the file in place (`ApiSettings.store_tokens`) without the lock or a
  reread, so a long-lived SDK object can present a token another process
  already spent;
- a copy of the token file on another host, container or sandbox.

The recorded refresh-token deaths, the exchange log (its fields and how to read it at the next invalid_grant) and the per-session server copies are recorded in the private gororoba-infrastructure repository.

Project-local settings (algorithm names, backend ids, shots) live in
`PROJECT_ROOT/.quantuminspire/config.json`, found relative to the working
directory; `qi files compile` and `qi algorithms init` create it.

## CLI (quantuminspire 4.1.0)

[cli-reference.md](cli-reference.md) holds the `--help` of every command.
The installed signatures, which differ from several website examples:

| Task | Command | Notes |
|---|---|---|
| list backend types | `qi backends list` | table output; no `--json` |
| one backend type | `qi backends get ID` | |
| queue | `qi backends queue ID [--user-only]` | |
| projects | `qi projects init NAME [DESCRIPTION]`, `qi projects list [--name T --exact --quiet]`, `qi projects delete IDS...` | |
| register an algorithm | `qi algorithms init NAME PATH BACKEND_TYPE_ID [--num-shots N] [--store-raw-data]` | NAME, PATH and the id are positional |
| submit | `qi run --file FILE --backend-type-id ID [--num-shots N] [--store-raw-data] [--persist]` or `qi run --name NAME` | submits a remote job; raw shots only with `--store-raw-data`; `--persist` keeps local settings |
| job state | `qi jobs inspect ID`, `qi jobs status ID [--wait --timeout S]`, `qi jobs logs ID` | `--timeout` default 60 s |
| results | `qi jobs results ID [--save]`, `qi jobs final-result ID [--save]` | plural `results`; boolean flags take no value |
| per algorithm | `qi algorithms status|logs|results|final-result NAME` | |
| remote compile | `qi files compile --file FILE --backend-type-id ID --compile-stage none|decomposition|mapping|optimization|routing` | runs the platform compiler and writes `<file>_compiled_<stage>.cq`; creates remote project, algorithm, commit and file; executes nothing |
| settings | `qi config get KEY [--algorithm NAME]`, `qi config set KEY VALUE [--algorithm NAME] [--user]` | |

Website and tutorial pages that use `qi files upload`, `qi results get`,
`qi algorithms init --name/--path` or `--save True` describe older CLI
generations.

## Python routes

**Compute job manager REST** (what this repository uses): the
[OpenAPI description](api/openapi.json) lists 77 operations on 53 paths.
`scripts/qi_platform.py` drives it with the stored bearer token:
project, algorithm, commit, file (`compile_stage` names the stage the
source already reached, `none` for raw cQASM), batch job, one job per
circuit (`number_of_shots`, `raw_data_enabled`), then
`PATCH /batch_jobs/{id}/enqueue`. Results: `GET /results/job/{job_id}`
(`results` counts, `raw_data` shot strings, `execution_time_in_seconds`,
`shots_requested`, `shots_done`); logs: `GET /jobs/{id}/logs`; compile:
`POST /commits/{id}/compile` with `{compile_stage, backend_type_id}`
(answers 204). The same field `compile_stage` means "stage reached" on a
file and "stage to reach" in a compile request.

**SDK Api**: `from quantuminspire.api import Api`; `Api().get_backend_types()`,
`get_backend_type(id)`, `get_queue(id)`, `get_job(job_id=)`,
`get_job_status`, `get_job_logs`, `get_results`, `get_final_result`,
`execute_algorithm(file_path=, backend_type_id=, num_shots=)`,
`compile_file(...)`. Models are pydantic; `model_dump(mode="json")`
serializes them.

**Qiskit provider**: `from qiskit_quantuminspire.qi_provider import QIProvider`;
`QIProvider().backends()` builds a Qiskit Target from each backend type's
gate set and topology; `backend.run(circuits, shots=N, memory=True)` submits
up to `max_jobs_per_batch_job` circuits as one batch job, after checking the
limit client-side. That is the API's ceiling of 5, not the FAQ's 3 queued
jobs per hardware backend, and the route carries neither the hardware pause
nor the token lock, so runs go through `qi_platform.py submit`
([usage.md](usage.md#queue-rules-the-faq-governs)). Its cQASM writer emits a multi-qubit barrier as per-qubit
barriers and accepts delays only in `dt`, so timing-sensitive cases here write
cQASM directly.

**PennyLane**: `pennylane_quantuminspire.qi_device.QIDevice` wraps a provider
backend for a QNode (current module name; the website still links the
retired `quantuminspire2` documentation).

**Hybrid jobs**: a submitted Python file defines `execute(qi)` and
`finalize(measurements)`; classical and quantum parts run on the platform
(language `Python 3.11` in `/languages`); the final aggregate comes from
`qi jobs final-result`.

## Result bit order

QX and Tuna return strings whose rightmost character is qubit 0, as the cQASM
specification states; the Ry emulator returns qubit 0 at the leftmost
character (measured, [backends.md](backends.md)). Validate a new backend
with an asymmetric preparation (X on q[0] only), since a Bell state reads
the same in both orders. A QX string has one character per qubit (its
measurement register), not one per declared bit, so a mid-circuit outcome
or a bit assigned from another qubit's index does not appear in it
([qx-runs.md](qx-runs.md)).
