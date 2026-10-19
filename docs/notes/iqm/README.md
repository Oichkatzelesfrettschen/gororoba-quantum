# IQM Resonance

IQM Resonance is IQM Quantum Computers' cloud: superconducting transmon QPUs
(Emerald, Garnet, Sirius) and a mock twin of each, behind the IQM Server API
at https://resonance.iqm.tech. IQM moved from meetiqm.com to iqm.tech in May
2026; every meetiqm.com host redirects, and `cocos.resonance.*` URLs are
rejected by iqm-client 36. `iqm.com` and `developers.iqm.com` belong to an
unrelated advertising company and are no source for anything here. The live
pages stay the authority because they change; the captures below record what
they said when read.

| Path | Content |
|---|---|
| `docs/` | every std:doc page of the IQM OS 4.7 documentation at https://docs.iqm.tech/4.7/ for ten packages, 1925 pages, with each package's `objects.inv` (`scripts/capture_iqm_docs.py --docs`) |
| `pypi/` | release metadata and file sha256 of the fifteen pinned distributions (`--pypi`) |
| `changelog/iqm-client-36.0.0.md` | the CHANGELOG of the iqm-client 36.0.0 sdist (`--changelog`) |
| `constraints-iqm-qccsw-4.7.0.txt` | IQM's client constraints for IQM OS 4.7.0 plus the integration pins |
| `python-stack.md`, `python-stack-versions.json` | every distribution installed in the client stack, with version, license, imports and requirements |
| `../../evidence/iqm/` | the account snapshot: server, per-QC records, configuration artifacts, calibration sets, metrics, the update feed, `hardware.json` (`scripts/iqm_platform.py snapshot`) |

The unversioned https://docs.iqm.tech/PACKAGE/ still served IQM OS 4.6 on
2026-10-19 (byte-identical inventories); the capture pins `/4.7/`.

## IQM OS 4.7 upgrade (2026-10-19 and 2026-10-21)

The dashboard's update feed (`server/notifications.json`, created
2026-10-16T11:28Z, version 3) announces the major release IQM OS 4.7:

- Emerald upgrades Monday 2026-10-19; Garnet and Sirius Wednesday
  2026-10-21. Downtime runs from 02:00 UTC to about 15:00 UTC on those days.
  The availability calendar agrees: Emerald's pay-as-you-go window reopens
  2026-10-19T15:00Z, Garnet is closed 2026-10-21 01:30Z to 15:00Z and Sirius
  02:30Z to 16:00Z, against daily calibration gaps of about 1.5 h (Garnet),
  2.25 h (Emerald) and 3.5 h (Sirius).
- Python 3.12 and 3.13 are officially supported. Clients install into a new
  environment with `constraints-iqm-qccsw-4.7.0.txt`: iqm-client 36.0.0,
  iqm-data-definitions 3.1.0, iqm-exa-common 29.0.0,
  iqm-station-control-client 14.0.0, iqm-pulse 15.0.0, iqm-pulla 15.0.0,
  iqm-qaoa 3.0.0, iqm-qubit-selector 1.2.0, iqm-benchmarks 3.0.0,
  iqm-error-reduction-tools 0.3.0.
- Pulse-level access moves into `IQMClient` (`get_standard_compiler`,
  `get_chip_label`, `get_chip_topology`, `get_calibration_set_stash`,
  `submit_playlist`); iqm-pulla 15 now installs the compiler package
  `iqm.cpc` and no `iqm.pulla` module. QIR import is `iqm_client.qir_utils`.
- Removed: `Pulla`, `IQMClient.submit_run_request` and
  `create_run_request`, `IQMBackend.create_run_request` and
  `IQMSampler.create_run_request`. Use `IQMClient.submit_circuit_job` and
  `create_circuit_job_definition`; `RunRequest` survives as an alias of
  `CircuitJobDefinition`. `IQMClient(...)` now takes executor and storage
  objects; `IQMClient.from_url(url, quantum_computer=...)` is the old form,
  and `get_job` returns a `JobTracker`.
- The Qiskit transpiler keeps final RZ gates (`remove_final_rzs`,
  `drop_final_rz` default False), because Qiskit's Sampler appends
  basis-change gates after transpiling. Pass `remove_final_rzs=True` for the
  old behavior; Z-basis counts are unchanged either way. Every combination
  of final-RZ, barrier and MOVE handling has a scheduling plugin, and qubits
  without PRX are filtered out of the Target.
- Readout error mitigation: `REMResults.mitigated_counts` becomes
  `mitigated_distributions` (quasi-probabilities), with a fix for
  `strategy="NONE"` and runs without readout twirling; REMWorkflow reports
  the QPU job ids it submitted.

The retained snapshot was read at 2026-10-19T05:5xZ, inside Emerald's
announced window, while every station still reported IQM station control
49.0.3 and IQM Server 3.0.0. It is the pre-upgrade baseline; a snapshot after
2026-10-21T16:00Z records the 4.7 stations, and the difference between the
two is the measured upgrade.

## Account and credential

The account is PERSONAL with 30.00 credits that expire 2026-11-01. API
tokens are created on the profile page (https://resonance.iqm.tech/profile),
are personal and scoped to one workspace, and carry scopes:
`job_execution` (submit and manage own jobs, list timeslots; all of
iqm-client), `timeslot_management`, `account_management`,
`account_analytics`. A token's permissions are its owner's role intersected
with its scopes; this account's token holds `job_execution` alone and
expires 2027-01-19, and so does its refresh token. An account holds at most
10 active tokens.

The token pair lives in `~/.config/iqm/tokens.json` (directory 700, file
600) as `{"access_token", "refresh_token"}`, outside every checkout.
`IQM_TOKENS_FILE` names it to every consumer: iqm-client 36's
`TokensFileReader` reads `access_token` from it and rereads the file whenever
a token's lifetime is unknown, which holds for every opaque Resonance token,
so a refreshed file reaches running clients without a restart.

`"$PYTHON" scripts/iqm_platform.py refresh` renews the token through
`POST /api/v1/tokens/current/refresh` with the refresh token as Bearer. A
refresh with `activated` true invalidates the refresh token at once, so a
lost response would lose both; the script requests `activated: false`,
writes the new pair to `tokens.json.pending`, then calls
`POST /api/v1/tokens/current/activate` with `{"api_token": NEW}` and the
same refresh token, and only then replaces `tokens.json`. A rerun after a
failed activation resumes from the pending file. An flock on
`tokens.json.lock` serializes refreshes, and the script refreshes only when
the current token expires within `--min-days` (14) days; `--days` (90) sets
both new lifetimes, each between 3600 s and 31536000 s.

Rate limiting is per user: 3000 cost units per 10 s rolling window, a 30 s
block on excess with `Retry-After`, `RateLimit-Limit` and
`RateLimit-Remaining` on every success. Reads cost little, a refresh or
activation 100, a job submission 100 plus 100 per 10 MiB of payload.
Cloudflare answers the default `Python-urllib` User-Agent with error 1010,
so every client names its own.

## API surface

The REST API is versioned (`GET /api/versions` lists v1, released
2025-09-01); `/api/latest/` aliases the newest and is for testing only. A
deprecated version answers with `IQM-API-Deprecated: true` and a deprecated
operation with `IQM-API-Operation-Deprecated: true; breaking=VERSION`.
Clients ignore unknown response properties and send no unknown ones.
`server/openapi.json` is the general description and `qc/ALIAS/openapi.json`
(`GET /api/v1/openapi.json?qc=ALIAS`) the per-QC one that names job types
and artifact kinds.

| Method and path | Use |
|---|---|
| `GET /about` | server version (3.0.0), license mode |
| `GET /api/v1/quantum-computers`, `/{qc}` | aliases, status, health, queue length, limits, pricing, links |
| `GET /api/v1/quantum-computers/{qc}/health`, `/limits` | health flag; instructions per circuit, shots per circuit, circuits per job, executions per job, queued jobs per user |
| `GET /api/v1/quantum-computers/{qc}/queue-availability` | pay-as-you-go windows; gaps are calibration and maintenance |
| `GET`, `POST`, `DELETE /api/v1/quantum-computers/{qc}/timeslots` | list, book, cancel one-hour timeslots |
| `GET /api/v1/quantum-computers/{qc}/artifacts/{kind}` | about, static-architecture, static-quantum-architectures, chip-design-records, channel-properties, configuration, duts, settings |
| `GET /api/v1/calibration-sets/{qc}/{id or default}` and `/dynamic-quantum-architecture`, `/metrics` | full calibration set; gates, implementations and loci; quality metrics |
| `POST /api/v1/jobs/{qc}/circuit` (JSON), `/run` (protobuf RunDefinition), `/sweep` (protobuf SweepTaskRequest) | submit; query `use_timeslot`, `iteration_id`, `tag` |
| `GET /api/v1/jobs/{id}`, `/payload`, `/artifacts/{measurement_counts, measurements, runtime_estimates, sweep_results}` | job record and results |
| `POST /api/v1/jobs/{id}/cancel`, `DELETE /api/v1/jobs/{id}` | cancel, delete |
| `GET /api/v1/tokens`, `POST /tokens/current/refresh`, `/activate`, `/tokens/{id}/revoke` | token management |
| `POST /api/graphql` | accounts, organizations, teams, credit, jobs (schema `server/graphql-schema.json`) |
| `GET /webapp/api/cms/notification` | the update feed; session cookie only |

A circuit job body carries `circuits` (each `{name, instructions:
[{name, locus, args, implementation}]}`), `shots`, `qubit_mapping`,
`calibration_set_id`, `heralding_mode` (`none`, `zeros`),
`active_reset_cycles`, `dd_mode` (`disabled`, `enabled`) with an optional
`dd_strategy`, `move_gate_validation` (`strict`, `allow_prx`, `none`),
`move_gate_frame_tracking` (`full`, `no_detuning_correction`, `none`) and
`max_circuit_duration_over_t2`. A job's status runs `waiting`,
`processing`, then `completed`, `failed` or `cancelled`; its metrics hold
compilation, execution and runtime seconds and `billed_seconds`, the
runtime rounded up to whole seconds, on which credits are charged.

GraphQL serves `me`, `account`, `organization`, `team`, `teamDeletionPlan`,
`job`, `quantumComputers`, `quantumComputer` and `credit(accountId)`, and
the mutations `inviteAccountMembers`, `resendAccountInvitation`,
`createTeam`, `renameTeam`, `setAccountMemberRole`, `removeAccountMembers`,
`deleteTeam` and `transferCredits`. A `job_execution` token reads `me` and
`credit`.

## Hardware

`scripts/iqm_platform.py check` renders this table from
`docs/evidence/iqm/hardware.json` and fails when either changes alone:

<!-- iqm-facts:begin -->
| QC (alias) | type | QPU chip (mask, variant) | qubits | resonators | couplings | gates (default implementation) | shots / circuits / instructions max | PAYG credits/s | timeslot | IQM station control |
|---|---|---|---|---|---|---|---|---|---|---|
| IQM Emerald (`emerald`) | qpu | M216_F0W102525_H03_F08 (M216, H03) | 54 | - | 90 | cc_prx (prx_composite), cz (slepian_crf), measure (constant), measure_fidelity (shelved_constant), prx (drag_crf_sx), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 30000 | 0.75 | 2400.00 per PT1H | 49.0.3 |
| IQM Emerald (mock) (`emerald:mock`) | mock | M160_W0_H01_Z99 (M160, H01) | 54 | - | 90 | cc_prx (prx_composite), cz (tgss), measure (constant), measure_fidelity (constant), prx (drag_gaussian), reset_wait (reset_wait) | 200000 / 1000 / 10000 | 0.00 | - | 49.0.3 |
| IQM Garnet (`garnet`) | qpu | M194_F0W2114_P08_B15 (M194, P08) | 20 | - | 30 | cc_prx (prx_composite), cz (slepian_crf), measure (constant), measure_fidelity (constant), prx (drag_crf_sx), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 10000 | 0.50 | 1800.00 per PT1H | 49.0.3 |
| IQM Garnet (mock) (`garnet:mock`) | mock | M194_W0_P08_Z99 (M194, P08) | 20 | - | 30 | cc_prx (prx_composite), cz (crf_crf), measure (constant), measure_fidelity (constant), prx (drag_crf), reset_wait (reset_wait) | 20000 / 500 / 10000 | 0.00 | - | 49.0.3 |
| IQM Sirius (`sirius`) | qpu | M186_F0W2259_ND1_O12 (M186, ND1) | 16 | COMPR1 | 24 | cc_prx (prx_composite), cz (crf_crf), measure (constant), measure_fidelity (constant), move (crf_crf), prx (drag_crf), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 75000 | 0.30 | 1080.00 per PT1H | 49.0.3 |
| IQM Sirius (mock) (`sirius:mock`) | mock | M186_W0_ND1_Z99 (M186, ND1) | 24 | COMPR1 | 24 | cz (crf_crf), measure (constant), measure_fidelity (constant), move (crf_crf), prx (drag_crf), reset_wait (reset_wait) | 20000 / 200 / 20000 | 0.67 | - | 49.0.3 |

Account: PERSONAL with 30.00 credits expiring 2026-11-01T00:00:00+00:00; IQM Server 3.0.0, API v1; token scopes job_execution.
<!-- iqm-facts:end -->

All three QPUs are transmon chips with a drive line and a flux line per
qubit (`DL-QBn`, `FL-QBn` in the chip design record) and tunable couplers,
read out through multiplexed probe lines with a TWPA per line.
The single-qubit native gate is `prx(angle, phase)` (DRAG pulses), the
two-qubit gate CZ, `measure` the readout, and `cc_prx` a PRX conditioned on
a fast-feedback measurement result; `prx_12` drives the 1-2 transition and
`reset_wait` idles to thermal reset. Virtual RZ is a frame change. A gate's
implementation can differ per locus (the DQA's override map).

Medians of the default calibration sets read at the snapshot:

| QC | T1 | T2 (Ramsey) | T2 echo | PRX RB fidelity | readout fidelity | CZ IRB fidelity | PRX | CZ | measure |
|---|---|---|---|---|---|---|---|---|---|
| Emerald | 50 us | 15 us | 38 us | 0.99967 | 0.98848 | 0.99630 | 24 ns | 40 ns | 360 ns |
| Garnet | 42 us | 9 us | 22 us | 0.99934 | 0.97945 | 0.99425 | 16 ns | 40 ns | 480 ns |
| Sirius | 26 us | 10 us | 24 us | 0.99902 | 0.98335 | 0.97400 | 40 ns | 104 ns | 400 ns |

- **Emerald**: Crystal 54, chip M216 variant H03 (`M216_F0W102525_H03_F08`),
  station MX07_Aphrodite_CD3. 54 qubits on a square lattice, 90 tunable
  couplers, 8 probe lines, 214 launchers. Drive frequencies 3.802 to
  4.207 GHz, readout 5.101 to 6.053 GHz; T1 11 to 92 us. CZ uses
  `slepian_crf` on 83 pairs and `crf_acstarkcrf` on the four pairs around
  QB50 (QB44, QB49, QB51, QB54). Its `measure_fidelity` default is
  `shelved_constant`, a readout that shelves the excited state to level 2
  first. Weakest loci: CZ QB43-QB35 0.908 and QB6-QB7 0.918; readout QB10
  0.898 and QB6 0.910.
- **Garnet**: chip M194 variant P08 (`M194_F0W2114_P08_B15`), "Apollo
  station in XLD10.S1". 20 qubits, 30 couplers, 3 probe lines. Drive 4.488
  to 4.770 GHz, readout 5.062 to 6.098 GHz; T1 15 to 57 us. CZ
  `slepian_crf` on all 30 pairs; QB10's four couplings are its weakest
  (0.988 to 0.990). `measure` also offers `fast_constant`.
- **Sirius**: star architecture, chip M186 variant ND1
  (`M186_F0W2259_ND1_O12`), station Charon. 16 operational qubits (the
  static architecture names 24, of which 16 carry PRX), all coupled to one
  computational resonator COMPR1 through 24 couplers. CZ acts between a
  qubit and the resonator's 0-1 subspace (`crf_crf`, `tgss` on QB2 and
  QB10), and MOVE swaps a qubit's 0-1 occupation with the resonator's, so a
  two-qubit gate between qubits is MOVE, CZ, MOVE. Its quality metrics
  include `move_ncz_move` IRB, `xy_move_cz_move` Clifford RB and a
  16-qubit GHZ population and coherence bound. CZ to COMPR1 median 0.974,
  weakest QB11 0.923.
- **AWG channels** sample at 2 GS/s with an 8-sample (Emerald, Garnet) or
  16-sample (Sirius) instruction granularity, so every pulse duration is a
  multiple of 4 ns or 8 ns.
- **Mocks** (`emerald:mock`, `garnet:mock`, `sirius:mock`) run the same API
  against simulated chips (M160, M194, M186 Z99 variants) with their own
  gate implementations and limits (`garnet:mock`: 500 circuits per job;
  `emerald:mock`: 200000 shots). The emerald and garnet mocks are priced at
  0.00 credits/s and `sirius:mock` at 0.67 credits/s, as the server reports
  them. The `mock_url` each record carries points at the retired
  `cocos.resonance.meetiqm.com`; a mock is reached as
  `quantum_computer="garnet:mock"` on https://resonance.iqm.tech.

`hardware.json` holds the per-qubit rows (T1, T2, T2 echo, PRX fidelity,
readout fidelity and both assignment errors, drive and readout frequency,
PRX and measure duration), the per-pair CZ fidelity, duration and
implementation, every gate's implementations and locus counts, the chip
component counts and the AWG channel properties. The raw sources beside it
go deeper: `calibration/set.json` carries every controller and pulse
parameter (drive and readout frequencies, amplitudes, DRAG and Slepian
shape parameters, flux biases, coupler settings, TWPA pump frequency, power
and voltages), `artifacts/chip-design-records.json` every component with its
connections (drive line, flux line, probe line, couplers) and layout
coordinates, `artifacts/configuration.json` the station's instruments
(Athene readout, Hades and Oceanus channel controllers, TWPA pumps), and
`artifacts/channel-properties.json` each channel's sampling rate, duration
granularity, compatible instructions and fast-feedback sources.

## Cost

Pay-as-you-go jobs cost `billed_seconds` times the QC's price per second:
Emerald 0.75, Garnet 0.50, Sirius 0.30 credits/s. A one-hour timeslot costs
2400.00 (Emerald), 1800.00 (Garnet) or 1080.00 (Sirius) credits. The 30.00
credits of this account buy 40 s on Emerald, 60 s on Garnet or 100 s on
Sirius, and expire 2026-11-01.

## Installation

The client stack is the Arch package `iqm-resonance-stack` 4.7.0, from
`~/Github/PKGBUILDs/iqm-resonance-stack`. iqm-client 36.0.0 caps
`qiskit<2.2`, `pydantic<2.13` and `packaging<25`, below the system's
python-qiskit 2.5.2, python-pydantic 2.14.1 and python-packaging 26.3, so the
package installs a self-contained Python 3.13 environment under
`/opt/iqm-resonance-stack` on the `python313` package (3.13.15), exactly
IQM's 4.7.0 constraints plus the qiskit, cirq and qrisp extras.

- `requirements.lock` pins 184 distributions by sha256
  (`uv pip compile --python /usr/bin/python3.13 --generate-hashes -c
  constraints-iqm-qccsw-4.7.0.txt requirements.in`); build() installs it
  with `pip --require-hashes --no-deps`, mthree 3.0.0 from its sdist.
- check() runs `test_iqm_stack.py`, 22 offline tests: the interpreter, every
  constraint and lock pin installed exactly, `pip check`, every module
  import, a Garnet fake-backend Bell transpile to `r`, `cz`, `measure` with a
  2000-shot Aer run above 90 percent correlated, MOVE insertion on the Deneb
  star fake backend, the 4.7 final-RZ default, and the client's URL rules
  (HTTPS only, CoCoS rejected, the quantum computer named by parameter,
  never in the path).
- package() relocates the environment to `/opt` and installs
  `/usr/bin/iqm-python`. The tests ship in `/usr/share/iqm-resonance-stack/`
  and rerun against the installed tree:
  `cd /usr/share/iqm-resonance-stack && iqm-python -P -m pytest -q -p no:cacheprovider test_iqm_stack.py`.

Build and install: `makepkg -f` in the package directory, then
`sudo pacman -U iqm-resonance-stack-4.7.0-1-x86_64.pkg.tar.zst`. The package
holds 1.7 GB once installed. A new IQM OS release gets a new
constraints file, lock and pkgver.

## Qiskit

```python
import os
from iqm.qiskit_iqm import IQMProvider, transpile_to_IQM

provider = IQMProvider("https://resonance.iqm.tech/", quantum_computer="garnet",
                       tokens_file=os.environ["IQM_TOKENS_FILE"])
backend = provider.get_backend()
isa = transpile_to_IQM(circuit, backend, seed_transpiler=7)
```

- The URL is the server base; the quantum computer is a parameter
  (`garnet`, `emerald`, `sirius`, `garnet:mock`). A computer name or a
  `:timeslot` suffix in the URL raises, and `_normalize_url` tests the name
  rule first, so a `garnet:timeslot` URL gets the name message. Timeslot
  submission is `use_timeslot=True` on the job.
- `transpile_to_IQM` handles Crystal and Star; on Sirius it inserts MOVE
  gates, and a high `optimization_level` can place single-qubit gates on the
  resonator, which the Star QPU rejects. `IQMNaiveResonatorMoving` and the
  `move_routing*` scheduling plugins carry that routing.
- `iqm.qiskit_iqm.fake_backends` exports IQMFakeAdonis, IQMFakeAphrodite,
  IQMFakeApollo and IQMFakeDeneb; `IQMFakeGarnet` lives in
  `iqm.qiskit_iqm.fake_backends.fake_garnet` and is missing from the
  package's `__init__`.
- Resonance offers dynamical decoupling, heralding, active reset, readout
  error mitigation (iqm-error-reduction-tools REMWorkflow), Pauli twirling,
  classically controlled gates (`cc_prx`) and pulse-level access.

## MCP

`scripts/iqm_mcp_server.py` is registered at Claude Code user scope and in
`~/.codex/config.toml` as `iqm`: `/usr/bin/python3 -I
scripts/iqm_mcp_server.py` with `IQM_TOKENS_FILE`. It runs on the system
Python (mcp 1.29) and imports nothing from the client stack. Claude allows
and Codex approves the read tools; `iqm_cancel_job` asks every time.
`iqm_platform.py check` holds the tool set and annotations.

| tool | reads |
|---|---|
| `iqm_quantum_computers` | every QC: alias, status, health, queue, station control version |
| `iqm_quantum_computer` | one QC: limits, pricing, description |
| `iqm_queue_availability` | pay-as-you-go windows |
| `iqm_timeslots` | timeslots |
| `iqm_architecture` | dynamic quantum architecture of the default calibration set |
| `iqm_metrics` | quality metrics, optionally one locus |
| `iqm_artifact` | a configuration artifact |
| `iqm_credit` | account type, balance, expiry |
| `iqm_tokens` | token scopes and expiries |
| `iqm_job`, `iqm_job_artifact` | a job and its results |
| `iqm_cancel_job` | cancels a job (asks) |

## Submission

Every IQM job, mock or QPU, and every timeslot booking waits for the user's
approval of a written case, like an IBM, Quantum Inspire, Open Quantum or
Quandela run: what it measures, why a noise simulation cannot answer it, the
QC, shots, circuits, the expected billed seconds and credits, and the
calibration set it was planned against. The MCP server submits nothing. A
simulation of 14 qubits or fewer still runs on Kaggle or the build host.
