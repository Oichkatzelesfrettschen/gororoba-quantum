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
| `hardware-pre-4.7.md` | the pre-upgrade specifications of all six targets, from the 06:08Z snapshot at commit 2009f0f |
| `os-4.7.md` | what IQM OS 4.7 changed on Emerald, Garnet and Sirius: versions, `measure_012`, API, settings, calibration, client |
| `python-stack.md`, `python-stack-versions.json` | every distribution installed in the client stack, with version, license, imports and requirements |
| `../../evidence/iqm/` | the account snapshot: server, per-QC records, configuration artifacts, calibration sets, metrics, the update feed, `hardware.json` (`scripts/iqm_platform.py snapshot`) |

The unversioned https://docs.iqm.tech/PACKAGE/ still served IQM OS 4.6 on
2026-10-19, before and after Emerald's upgrade (iqm-client 35.0.3); the capture pins `/4.7/`.

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

The retained snapshot was read at 2026-10-22T20:48Z, after both windows:
all three QPUs and their mocks report IQM station control 50.0.0 under
IQM Server 3.0.1. What the upgrade changed is in [os-4.7.md](os-4.7.md): a
`measure_012` three-state readout, the job route `sweep_results_streaming`,
a `flat_width` field on Slepian pulses and new settings parameters, with the
native ISA, limits and prices unchanged. The baseline's specifications are
in [hardware-pre-4.7.md](hardware-pre-4.7.md).

## Account and credential

The account is PERSONAL with 30.00 credits that expire 2026-11-01. The
Starter plan on https://www.iqm.tech/products/iqm-resonance (read
2026-10-24) grants "Up to 30 credits per month, based on availability" and
states no reset date; the account's expiry at 00:00 UTC on the first of the
next month fits a calendar-month grant, so a fresh balance after
2026-11-01 is expected but unconfirmed until `iqm_credit` reads it.
Purchased pay-as-you-go credits "don't expire" (same page). API
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
`IQM_TOKENS_FILE` names it to scripts/iqm_platform.py and the MCP server,
which reread it on every call, so a refreshed file reaches them without a
restart. iqm-client takes the access token as `token=` read from that file
(see [Qiskit](#qiskit)): iqm-client 36's `TokensFileReader` passes the token
to `TokenManager.time_left_seconds`, which decodes a JWT `exp` claim, and an
opaque Resonance token has none, so the reader raises "Access token in file
has expired or is not valid" for a token the API accepts.

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
| IQM Emerald (`emerald`) | qpu | M216_F0W102525_H03_F08 (M216, H03) | 54 | - | 90 | cc_prx (prx_composite), cz (slepian_crf), measure (constant), measure_012 (constant), measure_fidelity (shelved_constant), prx (drag_crf_sx), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 30000 | 0.75 | 2400.00 per PT1H | 50.0.0 |
| IQM Emerald (mock) (`emerald:mock`) | mock | M160_W0_H01_Z99 (M160, H01) | 54 | - | 90 | cc_prx (prx_composite), cz (tgss), measure (constant), measure_012 (constant), measure_fidelity (constant), prx (drag_gaussian), reset_wait (reset_wait) | 200000 / 1000 / 10000 | 0.00 | - | 50.0.0 |
| IQM Garnet (`garnet`) | qpu | M194_F0W2114_P08_B15 (M194, P08) | 20 | - | 30 | cc_prx (prx_composite), cz (slepian_crf), measure (constant), measure_012 (constant), measure_fidelity (constant), prx (drag_crf_sx), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 10000 | 0.50 | 1800.00 per PT1H | 50.0.0 |
| IQM Garnet (mock) (`garnet:mock`) | mock | M194_W0_P08_Z99 (M194, P08) | 20 | - | 30 | cc_prx (prx_composite), cz (crf_crf), measure (constant), measure_012 (constant), measure_fidelity (constant), prx (drag_crf), reset_wait (reset_wait) | 20000 / 500 / 10000 | 0.00 | - | 50.0.0 |
| IQM Sirius (`sirius`) | qpu | M186_F0W2259_ND1_O12 (M186, ND1) | 16 | COMPR1 | 24 | cc_prx (prx_composite), cz (crf_crf), measure (constant), measure_012 (constant), measure_fidelity (constant), move (crf_crf), prx (drag_crf), prx_12 (modulated_drag_crf), reset_wait (reset_wait) | 20000 / 100 / 75000 | 0.30 | 1080.00 per PT1H | 50.0.0 |
| IQM Sirius (mock) (`sirius:mock`) | mock | M186_W0_ND1_Z99 (M186, ND1) | 24 | COMPR1 | 24 | cz (crf_crf), measure (constant), measure_012 (constant), measure_fidelity (constant), move (crf_crf), prx (drag_crf), reset_wait (reset_wait) | 20000 / 200 / 20000 | 0.67 | - | 50.0.0 |

Account: PERSONAL with 30.00 credits expiring 2026-11-01T00:00:00+00:00; IQM Server 3.0.1.20261019072700, API v1; token scopes job_execution.
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
| Emerald | 49 us | 15 us | 39 us | 0.99967 | 0.9879 | 0.99722 | 24 ns | 40 ns | 360 ns |
| Garnet | 39 us | 9 us | 22 us | 0.99930 | 0.9804 | 0.99407 | 16 ns | 40 ns | 480 ns |
| Sirius | 28 us | 10 us | 23 us | 0.99880 | 0.9820 | 0.97090 | 40 ns | 104 ns | 400 ns |

- **Emerald**: Crystal 54, chip M216 variant H03 (`M216_F0W102525_H03_F08`),
  station MX07_Aphrodite_CD3. 54 qubits on a square lattice, 90 tunable
  couplers, 8 probe lines, 214 launchers. Drive frequencies 3.802 to
  4.207 GHz, readout 5.101 to 6.053 GHz; per-qubit T1 fits span 2.9 us to
  2.0 ms. CZ is calibrated
  on 85 of the 90 couplings: `slepian_crf` on 83 and `crf_acstarkcrf` on
  QB44-QB50 and QB50-QB51. The DQA override map also names QB49-QB50 and
  QB54-QB50, which no CZ implementation lists as a locus, so the transpiler
  routes around them; QB6-QB7 carries an IRB metric but no CZ locus either.
  Its `measure_fidelity` default is `shelved_constant`, a readout that
  shelves the excited state to level 2 first. Since station control 50.0.0
  it also offers `measure_012` (`constant`), a three-state readout, on QB43
  alone (all 54 qubits of emerald:mock). Weakest operational loci: CZ
  QB43-QB35 0.941, QB50-QB51 0.964 and QB16-QB8 0.976; readout QB6 0.925
  and QB35 0.961.
- **Garnet**: chip M194 variant P08 (`M194_F0W2114_P08_B15`), "Apollo
  station in XLD10.S1". 20 qubits, 30 couplers, 3 probe lines. Drive 4.488
  to 4.770 GHz, readout 5.062 to 6.098 GHz; T1 16 to 67 us. CZ
  `slepian_crf` on all 30 pairs; QB15's couplings are its weakest, QB19-QB15
  0.886 and QB14-QB15 0.942, and QB15 also reads out worst (0.893).
  `measure` also offers `fast_constant`.
- **Sirius**: star architecture, chip M186 variant ND1
  (`M186_F0W2259_ND1_O12`), station Charon. 16 operational qubits (the
  static architecture names 24, of which 16 carry PRX), all coupled to one
  computational resonator COMPR1 through 24 couplers. CZ acts between a
  qubit and the resonator's 0-1 subspace (`crf_crf`, `tgss` on QB2 and
  QB10), and MOVE swaps a qubit's 0-1 occupation with the resonator's, so a
  two-qubit gate between qubits is MOVE, CZ, MOVE. Its quality metrics
  include `move_ncz_move` IRB, `xy_move_cz_move` Clifford RB and a
  16-qubit GHZ population and coherence bound. CZ to COMPR1 median 0.971,
  weakest QB11 0.943.
- **AWG channels** that drive and flux the qubits sample at 2 GS/s with an
  8-sample (Emerald, Garnet) or 16-sample (Sirius) instruction granularity,
  so every pulse duration is a multiple of 4 ns or 8 ns; Sirius also lists a
  10 MS/s channel with single-sample granularity
  (`artifacts/channel-properties.json`).
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

The [read-only API audit](../../evidence/provider-api-audit/README.md) refreshes those rates and balances
on 22 October 2026. `runtime_seconds` includes compilation plus execution; `billed_seconds` rounds that
sum upward separately for each job. The balance therefore buys billed runtime, not pure pulse execution.
Client-side transpilation does not establish zero server compilation. Circuit batching can amortize
compilation and rounding, but reset/readout/repetition time, failure exposure and acquisition ordering
also constrain a useful batch. Request rate-limit units are separate from compute credits.

The live limits are 100 circuits/job, 20000 shots/circuit and 2000000 executions/job for these QPUs.
Those are structural ceilings rather than an affordable acquisition. The
[current-balance case](../../design/packed-pauli-response-current-balance.md) reserves six IQM credits
and compares maximal connected-cell layouts without assuming independent replicas. Slot prices exceed
the current balance; the token's `job_execution` scope also leaves booking unavailable.

## Installation

The client stack is the Arch package `iqm-resonance-stack` 4.7.0, from
`~/Github/PKGBUILDs/iqm-resonance-stack`. iqm-client 36.0.0 caps
`qiskit<2.2`, `pydantic<2.13` and `packaging<25`, below the system's
python-qiskit 2.5.2, python-pydantic 2.14.1 and python-packaging 26.3, so the
package installs a self-contained Python 3.13 environment under
`/opt/iqm-resonance-stack` on the `python313` package (3.13.15), exactly
IQM's 4.7.0 constraints plus the qiskit, cirq and qrisp extras.

- `requirements.lock` pins 184 distributions by sha256
  (`uv pip compile --python /usr/bin/python3.13 --python-platform
  x86_64-manylinux_2_28 --generate-hashes -c constraints-iqm-qccsw-4.7.0.txt
  requirements.in`); build() installs it
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
import json
import os
from iqm.qiskit_iqm import IQMProvider, transpile_to_IQM

with open(os.environ["IQM_TOKENS_FILE"], encoding="utf-8") as handle:
    token = json.load(handle)["access_token"]
provider = IQMProvider("https://resonance.iqm.tech/", quantum_computer="garnet", token=token)
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
`iqm_platform.py check` holds the tool set and annotations. The server
submits nothing and books no timeslot.

Dictionary GET responses retain `_observation` with the exact request path and subsecond UTC start/end
times. The interval belongs to that GET, rather than the calibration's creation timestamp or an atomic
multi-tool snapshot. `iqm_architecture(alias, calibration_set_id=None)` resolves the default identity before
reading the architecture. Pass the returned `calibration_set_id` to `iqm_metrics` or back to architecture
to keep related reads on one set; returned identity mismatches raise MCP errors. Default resolution can
change between separate tool calls, so callers must pass the identity for a coherent comparison.
The server rebuilds the SDK settings model after import to resolve its lifespan forward reference before
settings sources inspect it; the strict warning-as-error import regression exercises that path.

| tool | reads |
|---|---|
| `iqm_quantum_computers` | every QC: alias, status, health, queue, station control version |
| `iqm_quantum_computer` | one QC: limits, pricing, description |
| `iqm_queue_availability` | pay-as-you-go windows |
| `iqm_timeslots` | timeslots |
| `iqm_architecture` | dynamic architecture of an explicit or resolved-default calibration identity |
| `iqm_metrics` | metrics of an explicit or resolved-default identity, optionally one locus |
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

`scripts/iqm_jobs.py` is the submission path: `build` and `check` write and
regenerate a case, `submit` posts one job of it to `/api/v1/jobs/{qc}/circuit`
only for the approved cases.json digest, an online and healthy QC and the
credit ceiling that cases.json records for that QC (`max_credits`, which the
command line repeats), after an exclusive `submission-state.json`, and
`collect` keeps the job record and the measurements and counts artifacts byte
for byte under a lock on the run directory. `--dry` runs every refusal and
sends nothing. One run directory is admitted per quantum computer, case, job
and cases.json digest, so a rebuilt case takes its own mock run. The timing,
reset-billing and signed-probe cases predate `max_credits`; their retained
bytes stay as approved, so a charged resubmission of them refuses and a rerun
goes through a new case. The first case is the
[Garnet timing pilot](../../design/iqm-garnet-timing-pilot.md), which prices
later cases from measured billing.

## What the Garnet runs measured

Facts a Garnet case design starts from, each with the record that carries it:

- **Billing.** Garnet bills ceil(runtime) per job, not ceil(estimate); the
  estimate is a fixed 1.60 s plus each shot's schedule and bounded runtime
  within -0.63 s to +1.50 s on the retained jobs, so a ceiling adds 1.60 s to
  a case's shot schedule ([timing pilot](../../design/iqm-garnet-timing-pilot.md)).
  The job body carries no runtime or credit cap, which IQM does not offer, so
  `max_credits` bounds the predicted bill; a runtime beyond the expected
  schedule plus 1.60 s bills more, and a case sizes its shot schedule from an
  upper per-shot time and the free mock twin's estimate.
  Extra circuits cost no time beyond their shots, so replicas, randomized
  compilations and readout calibrations belong in the same job.
- **Reset.** One active-reset cycle shortens a shot from 316 us to 37.5 us
  and leaves QB1 6.8 % excited against 0.65 % passive; all-zeros heralding
  removes that excitation and returns only kept shots, 55.9 % on the
  seven-qubit probe, with no top-up. A heralded job's runtime exceeded its
  estimate by 0.63 s.
- **Coherent error dominates first-order observables.** An observable read
  near the equator of the measured qubit (an interference or Hadamard-test
  readout) moves at first order with gate over-rotation, axis error,
  residual Z after CZ and CZ conditional phase, which randomized
  benchmarking sees at second order. The 199-CZ signed probe read even
  offsets of -0.022 and -0.012 against +0.029 from the calibration-built
  depolarizing and relaxation model; its readout alone predicts +0.031
  (heralded QB7 errors 0.003 and 0.034), so the circuit moved the reading by
  about -0.045. Through the calibration noise model the even part's
  response to each stationary coherent error is 5 to 10 % of the noiseless
  one (QB11 over-rotation -0.43 per unit against -8.0), so QB11 alone would
  need a 10.5 % over-rotation, three times what its randomized-benchmarking
  infidelity allows, and all 29 error terms aligned at that bound reach
  only 0.032: the offset lies outside the stationary coherent model, and
  leakage read as 1, crosstalk and readout under heralding are untested
  ([coherent response](../../design/iqm-garnet-signed-kernel-probe.md#adversarial-audit)).
  The offsets reproduce under set `68b0f1d0` (-0.0195 and -0.0175), and the
  kernel cancellation run measured QB11 over-rotating by only
  +0.15 +- 0.07 % ([results](../../design/iqm-garnet-kernel-cancellation-probe.md#garnet-results-2026-10-23)).
  A prediction from `scripts/iqm_sim.py` therefore bounds incoherent loss
  and readout only; a case that reads a first-order observable measures the
  coherent errors of its own qubits in the same job (error-amplifying
  repetitions) or randomizes them.
- **Batch order.** A job's circuits run under one calibration, so the arms
  of a +-parameter contrast interleave in the circuit list (+, -, -, +)
  rather than block, keeping drift along the batch out of the odd part.
- **Calibration lifetime.** Set `9069c4ef` served from the snapshot of
  2026-10-22T20:48Z to at least 2026-10-23T00:50Z and was replaced by
  2026-10-23T05:30Z; set `68b0f1d0` served from then to at least 07:33Z. A
  case pinned with `calibration_set_id` pools only with jobs of its set, and
  a retired set refuses the job, so a case built against the live set (the
  `--live` builds) is rebuilt when the set changes.
- **Visibility and depth.** The 37-CZ kernel cancellation probe kept a
  visibility of 0.36 (model 0.48); the 199-CZ signed probe kept 0.058 once
  its null offset is subtracted (model 0.05 to 0.09)
  ([null re-test](../../design/iqm-garnet-signed-kernel-probe.md#null-re-test-results-2026-10-23)).
- **Null offset.** On the 199-CZ compile the calibration model gives the
  signed probe's odd part +0.0136 at t = 0, where the ideal is zero, because
  the +0 and -0 circuits differ in their rotation angles; Garnet read
  +0.0025 +- 0.0031 there.
- **Readout.** `measure_012` (three-state readout) is offered on QB1, QB3,
  QB7, QB9 and QB14; the Qiskit Target omits it, so a leakage readout goes
  through the circuit JSON directly.

## Gates and snapshot state

CI never imports the stack: its gates read retained JSON with the standard
library.

**IQM OS 4.7.** The update feed announced the major release for Emerald on
2026-10-19 and for Garnet and Sirius on 2026-10-21, with downtime from 02:00
to about 15:00 UTC. The client pins already match it (iqm-client 36.0.0,
final RZ gates kept by default, Pulla folded into IQMClient,
`submit_circuit_job`). The retained snapshot (2026-10-22T20:48Z) holds all
three QPUs and their mocks at station control 50.0.0 under IQM Server 3.0.1;
each gained `measure_012` and the job route `sweep_results_streaming` with an
unchanged ISA ([os-4.7.md](os-4.7.md)). iqm-client 36.0.0 transpiled for all
three QPUs on 2026-10-19, with Garnet and Sirius still on 49.0.3. The
all-49.0.3 baseline is [hardware-pre-4.7.md](hardware-pre-4.7.md).

Gates `core-record-check-05` (`tests/test_cli_record_checks.py`) (`capture_iqm_docs.py --check`) and core-590 (`iqm_platform.py check docs/evidence/iqm --agents
docs/notes/iqm/README.md`, which also holds the MCP tool set) and the
`--self-test` of both scripts in gates `core-self-test-06` and `core-self-test-07` (`tests/test_cli_self_tests.py`) (the two-phase
refresh on a stubbed transport included).
