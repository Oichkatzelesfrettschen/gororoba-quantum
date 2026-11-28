# Machine routing and the cross-machine layer

The routing table names the substrate that answers each question class. Three tools and one reader check the
records that follow from a routing choice: [check_case_contract.py](../../scripts/check_case_contract.py) validates a written
case, [preflight_check.py](../../scripts/preflight_check.py) applies six universal gates, and
[run_records.py](../../gororoba_quantum/run_records.py) returns one provider-neutral envelope per retained run. Every number in
the table lives in its home document and is linked, never copied.

## Routing table

The rule each row follows is the routing paragraph of
[AGENTS.md](../../AGENTS.md#qpu-time-and-calibration) and the approval rule of
[AGENTS.md](../../AGENTS.md#hardware-services). A row names a substrate; the written case still names the backend and the
reason a cheaper substrate fails.

| Question class | Substrate | Why this substrate | Cost per answer | Rule followed |
|---|---|---|---|---|
| exact rank, nullity, ideal distribution, unitarity | local exact code, Aer or Perceval SLOS | the answer is exact classically, so a QPU adds no algebraic truth | none; [local compute](../runbooks/compute-flags.md) | simulation of 14 qubits or fewer runs on Kaggle |
| noise simulation of 14 qubits or fewer | Kaggle kernel through `scripts/kaggle_run.py` | free session inside the standing approval | [Kaggle notes](kaggle/README.md) | routing rule, first sentence |
| 15-qubit simulation against hardware | the owner's choice among Aer on the build host, Kaggle T4 x2 and Tuna-17 | the case names the substrate and why it answers | [qpu-submission](ibm_quantum/qpu-submission.md) | 15 qubits wait for the written case |
| 16 qubits or more, or a question about the device itself on IBM | `ibm_fez`, `ibm_kingston` or `ibm_marrakesh` | only Heron r2 reaches the width or the device property; the case states why Aer cannot answer | [QPU time](ibm_quantum/qpu-submission.md), [platform](ibm_heron_platform.md) | IBM serves 16 or more qubits |
| zero-credit hardware replication, raw per-shot order, small shallow circuits | `tuna_17` through Quantum Inspire, QX twin first | free hardware with raw data; the scarce resource is the batch queue | [Tuna-17](quantum_inspire/tuna-17.md) | 15-qubit choice of Tuna-17 |
| photonic linear optics, mesh, heater, detector and Hong-Ou-Mandel physics | `qpu:belenos`, local SLOS first | the only photonic substrate; one job packs the settings | [Quandela](quandela/README.md), [credit optimization](../runbooks/quandela-credit-optimization.md) | approval of a written case for every provider job |
| gate-model circuit on a second vendor's chip | IQM `garnet` or `emerald` through Resonance | an independent superconducting device with a pinned calibration set | [IQM notes](iqm/README.md) | approval of a written case for every provider job |
| cross-device replication of a Heron result | the other Heron r2 device | separates a device effect from an algebra effect | [QPU time](ibm_quantum/qpu-submission.md) | IBM serves 16 or more qubits, or the device itself |

The per-device capability notes (timing, qubit health, per-job seconds and credits) are `docs/notes/ibm_quantum/machine-capabilities.md`
on branch `machine-capabilities`, `docs/notes/quandela/belenos-capabilities.md` on branch `quandela-belenos-capabilities` and
the Tuna-17 characterization notes under [quantum_inspire](quantum_inspire/README.md). The two branch notes are open
pull requests at the time of writing; link each section here when it lands on main.

## Case contract

A written case adds `case_meta.json` beside its `CASE.md`. [check_case_contract.py](../../scripts/check_case_contract.py)
holds the schema as data (`COMMON` and `PROVIDER_BLOCKS`) and reads it with
`"$PYTHON" scripts/check_case_contract.py --check CASE_DIR [--require-approval]`; exit 0 admits the case, 1 lists each
violation, 2 reports a missing or unparsable file.

- Top level: `schema` (`case-contract-v1`), `provider` (`ibm`, `quandela`, `quantum_inspire` or `iqm`), the common fields
  and one object named after the provider.
- Common fields, all required: `case_id`, `hypothesis`, `observable_primary_source`, `falsifier`,
  `why_cheaper_substrate_fails`, `backend`, `shots`, `expected_seconds`, `expected_cost` (an object with `unit` and
  `value`), `qrng_seed_refs` (each `qrng:<draw path>#<index>`), `preregistered_readings`, `void_rules`, `stopping_rule`
  and `approval_quote` (null until the owner approves).
- `ibm` block: `account`, `family`, `rep_delay_s`, `max_execution_seconds`, `max_total_execution_seconds`,
  `reserve_seconds`, `exclude_qubits`, `pin_layout`, `readout_pair_in_job` (true) and `check_cmd`.
- `quandela` block: `platform`, `max_credits`, `per_job_credits`, `mitigations` (an explicit list, empty when none),
  `source_modes`, `routing_health_floor`, `architecture_policy`.
- `quantum_inspire` block: `backend_type_id`, `qx_twin_run`, `queue_policy`, `readout_pair_per_batch` (true) and
  `sanity_script`.
- `iqm` block (this note adds it; the red-team template covers three providers): `qc`, `max_credits`, `price_per_second`,
  `calibration_set_id`, `prediction_sha256`, the fields `iqm_records` and the IQM receipt already bind.
- Relations: the cost unit follows the provider (seconds for IBM, credits elsewhere), the expected cost and seconds stay
  inside the ceilings of the provider block, and the Belenos `platform` equals `backend`.

## Pre-flight gates

`"$PYTHON" scripts/preflight_check.py --provider {ibm,quandela,iqm,qi} RUN_OR_CASE_DIR` prints one PASS or FAIL line per gate
and exits 0, 1 or 2 (no record). The gates read files only; the live reads they require are the ones the plan record
already holds.

| Gate | IBM | Quandela | IQM | Quantum Inspire |
|---|---|---|---|---|
| 1 baseline | `compiled_ideal_validation` passed | an ideal, census or certificate entry in `cases.json`, digest-checked when it names a file | `prediction.json` matches the digest `cases.json` binds | an ideal or certificate entry in `cases.json` |
| 2 fresh live read | backend read, revalidation and usage in `record.json`, within an hour of the plan | availability, platform and performance reads in the receipt | credit balance in the receipt | backend status and own-queue read in the receipt |
| 3 seed provenance | every seed value is a QRNG draw value or sits in the seed ledgers ([AGENTS.md](../../AGENTS.md#seeds)) | same | same | same |
| 4 budget and ceiling | `budget_plan` admitted, total inside remaining less reserve | credit ceiling inside `max_credits`, seconds inside the platform limit | expected seconds priced inside `max_credits` and the balance | own queue below the limit |
| 5 health control | layout avoids every excluded qubit | preregistered readings, and the mitigations list for a hypercomplex case | pinned calibration set equals the compiled one | readout pair in the batch or a declared guard |
| 6 approval and recovery | approval record consumed, collected job ids | quoted approval, job id in the receipt | quoted approval, job id in the receipt | quoted approval, batch job in the receipt |

A directory that holds `case_meta.json` adds the contract verdict. A case awaiting approval fails gate 6 by design.
Gate 3 reads `seed`-named keys of the plan files (`record.json`, or `cases.json` and `submission.json`); a run whose seeds
sit only inside circuit files shows zero accounted values, and `ci/seed_provenance.py` remains the ledger check.

## Run envelope

[run_records.py](../../gororoba_quantum/run_records.py) returns one `RunEnvelope` per retained run through
`read_envelope(provider, run_dir)` and `envelopes(provider)`. The Quandela, IQM and Quantum Inspire facts come through
`qd_records`, `iqm_records` and `qi_records`; the IBM facts come from `record.json`, `collect.json` and the raw
`index.json` digests, since `live_run.py` needs Qiskit. `validate()` returns every reason the run fails: a reader
rejection, a missing approval, a missing job id or raw file, a void health verdict, or executed shots above requested ones.

Health verdicts: `ok`, `unread` (records that predate the field), `live-differ` (an IBM plan that differs from the approved
record, or Belenos `couplers_checked`), `compiled-differ` (a failed IBM ideal validation, or Belenos
`compiled_couplers_checked`) and `routing_collapsed` (the `routing_collapsed_jobs` of a Belenos `analysis.json`). The three
differ and collapse verdicts void the run. The Belenos fields come from the offcone-mechanisms branch; a main-branch run
reads `unread` until that branch lands.

## Limits

- Gate 1 for Quandela and Quantum Inspire matches key names (`ideal`, `prediction`, `census`, `certificate`, `twin`), so it
  proves a baseline was declared, not that the baseline matched the result.
- Gate 6 accepts the recorded job id as the recovery handle; it does not run `qd_platform.py recover` or
  `qi_platform.py reconcile`.
- The billed cost of Quandela and Quantum Inspire runs reads `None`: the credit charge is an account fact outside the run
  directory.
