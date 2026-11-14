# Quandela successor acquisition pairs: simulator rehearsal plan

Status: written case, unsubmitted and unapproved. No job in this document has run, and no command below sends one
until the owner approves the case it names.

A new acquisition of the Ascella target-slot request or of the Belenos diagnostic request builds with a successor
builder and reads with its paired analyzer. Each pair states the billing rule of
[`scripts/billing_rule_v2.py`](../../scripts/billing_rule_v2.py), carries `acquisition_admission: ready`, binds the digests of its
sources into the request, and admits a run only against that request's sha256
([billing-rule successor record](../evidence/quandela-billing-rule-successor/README.md)). A simulator run rehearses the
whole path (build, plan, review packet, submit, collect, analyze) on a platform whose charge is the per-job price, so
the pair meets provider data before a QPU job depends on it.

## Why a provider simulator job

A local Perceval run (`bdsc_cases.py --local`) and the offline tests of each pair cover the circuit, the request digest
and the analyzer on synthetic counts. Only a provider job returns the receipt, the collected result fields
(`computed_circuit`, `physical_perf`, `nb_shots_used`) and the usage movement that the integrity checks of
`qd_platform.run_facts` and `bdsc_diagnostic.admit_run` read, so the first such job is the one that exercises them on
service data. The retained sim:belenos `bdsc_qualification` run `tc-none-e1` returns `physical_perf` (0.0601 on its
first iteration), `computed_circuit` and `samples` equal to `max_samples`, the fields `bdsc_diagnostic.observations`
requires.

## What a simulator run establishes

- Build, receipt, collection and analyzer agree on one request digest, and the analyzer refuses a run of another
  request or platform.
- The returned `computed_circuit` and `computed_input` identities are reported. A simulator need not reproduce the QPU's
  compilation (the retained sim:ascella qualification returned another `computed_circuit` for all eight iterations and
  the same `computed_input`), so the Ascella pair reads them as a report on sim:ascella and as a stop condition on
  qpu:ascella.
- The measured seconds and credits of the rehearsal replace the estimates below in the QPU case.

A simulator run establishes nothing about the QPU's counts, compiled meshes or drift, and no scientific claim of the
QPU case rests on it.

## Billing

| Platform | Source of the charge | Charge per completed job |
|---|---|---|
| sim:ascella, sim:belenos | the price per shot is 0 on every simulator: [credit optimization runbook](../runbooks/quandela-credit-optimization.md), "The billing rule" (lines 34 to 42) and "Simulator jobs are not free" | 1 credit, the observed charge of a completed simulator job; falsifier: an isolated completed simulator job whose usage counter moves by another amount |
| qpu:ascella, qpu:belenos | 1 credit plus 1e-6 per billed shot | 1 + 1e-6 times the smaller of the shots used and the largest iteration's `max_shots` |

Simulator jobs are billed. The 1 credit is an observed charge, not a resolved tariff. A retained sim:ascella run of the frozen target-slot request used 8 iterations of 32768
events and charged 1.0 credit (`qd_platform.run_facts` of
`results/quandela/runs/2026-10-30T010726Z-sim_ascella-ascella_predecessor-source-compatible`, `charge` 1.0). The
platform note [platform-specifications.md](../notes/quandela/platform-specifications.md) records the simulator tariff
as unresolved and asks a case to budget at least 1.0 credit per job; this plan budgets 1.0 and reads the usage report
before and after each job as the check.

## Rebinding and source binding

Each analyzer rebinds a frozen function with `gororoba_quantum/rebound.py`. The helper overrides the global names that
the copied code looks up directly; a callee it calls keeps its own module's globals, so every call site passes each
nested callee that must see the successor record or platform as its own override. The tests plant a defect in the
frozen readout and require the hand-computed expectations to reject it.

Source binding differs by family. The Ascella request records the digests of its builder, analyzer and shared modules in
`preregistered.current_case_sources`; `qd_platform.acquisition_sources` verifies them at `review` and `submit`, and the
analyzer rebuilds the request from the tree it runs in. `plan` and `collect` do not verify them. The Belenos manifests
record the sha256 of every repository module the readout imports as `successor_sources`; `qd_platform.load_case`
verifies them before `plan`, `review`, `submit` and `collect`, and the analyzer verifies them before it reads a run.
Both bindings include `scripts/qd_platform.py`, so a built request is valid in one source tree and is rebuilt after a
change to any bound file.

## Ascella target-slot request

Pair: [`scripts/ascella_predecessor_acquisition_case.py`](../../scripts/ascella_predecessor_acquisition_case.py) and
[`scripts/ascella_predecessor_acquisition_analysis.py`](../../scripts/ascella_predecessor_acquisition_analysis.py).
The request is the frozen eight-iteration template job (32768 samples and shots per iteration, 12 modes, the three
retained seed-0 settings in both orders) with the job named `sim-ascella-billing-rule` or `qpu-ascella-billing-rule`.
The compilation seeds are the retained seed-0 values of the frozen request, so the pair draws no new seed.

| Platform | Shots | Expected seconds | Expected credits | Source |
|---|---|---|---|---|
| sim:ascella | 8 x 32768 | 7 measured; 40 as the case ceiling | 1.0 | retained run above: `results.json` status `duration` 7, receipt `expected_seconds` 40 |
| qpu:ascella | 8 x 32768 | 40 | at most 1.032768 | frozen case `expected_seconds` and `max_credits` |

Rehearsal on sim:ascella, from the repository root at one commit (the request binds the digest of
`scripts/qd_platform.py`, so every command runs in that tree):

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="${QUANDELA_TOKEN_FILE:?set to the token file}"
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-sim_ascella-ascella_predecessor-sim-ascella-billing-rule
"$PYTHON" scripts/ascella_predecessor_acquisition_case.py --build --platform sim:ascella --out "$RUN"
"$PYTHON" scripts/qd_platform.py plan "$RUN" --platform sim:ascella \
  --max-credits 1.032768 --expected-seconds 40 --per-job-credits 1
"$PYTHON" scripts/qd_platform.py review "$RUN" --platform sim:ascella \
  --max-credits 1.032768 --expected-seconds 40 --per-job-credits 1 --out "$RUN.review.json"
# retain the packet digest outside the run directory, then, after the owner's approval of this case:
"$PYTHON" scripts/qd_platform.py submit "$RUN" --platform sim:ascella \
  --max-credits 1.032768 --expected-seconds 40 --per-job-credits 1 \
  --approval "APPROVAL TEXT" --reviewed-packet "$RUN.review.json" --reviewed-sha256 "$PACKET_SHA256"
"$PYTHON" scripts/qd_platform.py collect "$RUN"
"$PYTHON" scripts/ascella_predecessor_acquisition_analysis.py "$RUN" \
  --submission-sha256 "$(sha256sum "$RUN/submission.json" | cut -d' ' -f1)" \
  --results-sha256 "$(sha256sum "$RUN/results.json" | cut -d' ' -f1)"
```

The QPU job repeats the commands with `--platform qpu:ascella`, the job directory `...-qpu_ascella-...-qpu-ascella-billing-rule`,
the build argument `--platform qpu:ascella`, and `--admit-status running` on `plan`, `review` and `submit`, because the
request's `admitted_platform_statuses` lists `running` and qpu:ascella may read `running` while it serves its queue.
The token-capacity gate (`qd_platform.require_token_capacity`) is separate: it refuses a submission while the token holds
a running or queued job, and its queue-slot exception belongs to the `current-schema` job alone.

The rehearsal passes when the analyzer prints `"verdict": "descriptive-only"` with `"platform": "sim:ascella"`, every
iteration returns 32768 events in total, and the usage report moved by one job and 1.0 credit. An iteration may hold
fewer eligible single-photon events than that total, as the retained run's `eligible_counts` 32767 and 32766 did, and
the analyzer reads the eligible count it finds.

## Belenos diagnostic request

Pair: [`scripts/bdsc_diagnostic_acquisition_case.py`](../../scripts/bdsc_diagnostic_acquisition_case.py) and
[`scripts/bdsc_diagnostic_acquisition_analysis.py`](../../scripts/bdsc_diagnostic_acquisition_analysis.py). The request
is the 96-instance crossed design of `scripts/bdsc_diagnostic.py` (four jobs of 24 iterations, 40000 eligible trials and
an 80000-shot cap per iteration, empty mitigation list, 24-mode ladder-union circuit) under a successor case record
that states the current billing rule and names its platform. The 24-mode circuit does not fit sim:ascella (12 modes,
[platform-specifications.md](../notes/quandela/platform-specifications.md)), so the pair admits qpu:belenos and
sim:belenos only.

Each tree takes its own ANU draw. The draw seeds four compilation slots and orders the instances, and
`draw_claims` refuses a draw that a manifest of any other case record names, so a sim:belenos tree and a qpu:belenos
tree (two case records) cannot share one. The rehearsal draw is a free ANU read (`docs/notes/qrng/README.md`) and the
QPU tree takes a second.

| Platform | Shots | Expected seconds | Expected credits | Source |
|---|---|---|---|---|
| sim:belenos, four jobs | 4 x 24 x 80000 cap | at most 176.16 per job, 704.64 in all, plus the one-hour block gap | 4.0 (1.0 per job) | case record `resources.seconds_per_job_estimate` from the QPU timing rule as the ceiling; billing table above |
| qpu:belenos, four jobs | 4 x 24 x 80000 cap | 176.16 per job, 704.64 in all | at most 4.32 (1.08 per job) | case record `resources` |

No retained sim:belenos job has this shape. The nearest ran 148 s for 12 iterations of 300000 samples
(`docs/notes/quandela/strategy.md`, run log of 2026-10-21 06:44), so the rehearsal budgets the QPU estimate as its
ceiling, below the 300 s per-job limit, and reads the measured duration back into the QPU case.

Rehearsal of one job, which exercises the build, plan, submit, collect and admission path for 1 credit:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="${QUANDELA_TOKEN_FILE:?set to the token file}"
"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng --length 100 --type uint16
DRAW=docs/evidence/anu_qrng/DRAW_FILE_NAMED_BY_THE_COMMAND_ABOVE.json
TREE=results/quandela/cases/bdsc_diagnostic_billing_rule_sim_belenos
"$PYTHON" scripts/bdsc_diagnostic_acquisition_case.py --build --platform sim:belenos --out "$TREE" --draw "$DRAW"
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-sim_belenos-bdsc_diagnostic-b1-j1
mkdir -p "$RUN" && cp "$TREE"/b1-j1/cases.json "$TREE"/b1-j1/circuit.json "$RUN"/
"$PYTHON" scripts/qd_platform.py plan "$RUN" --platform sim:belenos \
  --max-credits 1.08 --expected-seconds 176.16 --per-job-credits 1
# after the owner's approval of this case:
"$PYTHON" scripts/qd_platform.py submit "$RUN" --platform sim:belenos \
  --max-credits 1.08 --expected-seconds 176.16 --per-job-credits 1 --approval "APPROVAL TEXT"
"$PYTHON" scripts/qd_platform.py collect "$RUN"
"$PYTHON" scripts/bdsc_diagnostic_acquisition_analysis.py --case "$TREE"/case.json --admit-only "$RUN"
```

The full rehearsal repeats the run block for b1-j2, then b2-j1 at least one hour after block 1 ends, runs
`--matched-check B1J2_RUN B2J1_RUN` after b2-j1 is collected and before b2-j2 is submitted, and ends with
`scripts/bdsc_diagnostic_acquisition_analysis.py --case "$TREE"/case.json RUN...` over the four runs, which reads
the branch and applies the schedule rules of `bdsc_diagnostic.require_schedule`. The qpu:belenos request repeats the
commands with `--platform qpu:belenos`, a second draw, the tree `bdsc_diagnostic_billing_rule_qpu_belenos` and the
run-directory platform tag `qpu_belenos`.

The offline tests run the readout with `validate=False`, because a synthetic run carries no raw result; the first
`validate=True` read of a successor run, which adds `qd_records.validate_run`, is the rehearsal's.

The rehearsal passes when `--admit-only` prints `b1-j1`, the run's `platform_name` is sim:belenos, the usage report
moved by one job and 1.0 credit, and, for the full rehearsal, the analyzer prints a `branch`. A simulator's branch
describes the simulator and carries no claim about the QPU.
