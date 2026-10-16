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
QI_ENV=${QI_ENV:-$HOME/.local/share/quantuminspire/venv}
QI_PYTHON=${QI_PYTHON:-$QI_ENV/bin/python}
uv venv --python 3.13 "$QI_ENV"
VIRTUAL_ENV="$QI_ENV" uv pip install -r docs/notes/quantum_inspire/requirements-qi.txt
"$QI_PYTHON" -c "import quantuminspire, qiskit_quantuminspire, qxelarator, mcp"
```

[requirements-qi.txt](requirements-qi.txt) is the full lock (Python 3.13.15,
uv 0.13.0, Linux x86_64). The direct packages and their roles are tabled in
the root AGENTS.md section "Quantum Inspire". CI never imports this stack;
gates core-325, core-326, core-327, core-330 and core-331 read retained files with the
standard library; core-329 and core-340 regenerate with the pinned Qiskit stack.

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
4. Tokens land in `~/.quantuminspire/config.json` under the host
   `https://api.quantum-inspire.com`: access token (3600 s), refresh token,
   `generated_at`, and `team_member_id`. The CLI writes the file mode 644;
   tighten it with `chmod 600 ~/.quantuminspire/config.json`. The file never
   enters the repository, a log or agent memory.

A login made in another OS user, container, WSL distribution or cloud VM
does not reach this environment. An agent that finds no login runs `qi
login` in the background, reads the URL and code from its output, and asks
the user to approve them in the browser; the code expires within minutes.
`qi logout` revokes the refresh token.

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
limit client-side. Its cQASM writer emits a multi-qubit barrier as per-qubit
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
the same in both orders.
