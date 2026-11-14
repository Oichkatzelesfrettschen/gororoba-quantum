# Quandela successor acquisition pairs: simulator rehearsal plan

Status: written case, unsubmitted and unapproved. No job in this document has run, and no command below sends one
until the owner approves the case it names.

A new acquisition of the Ascella target-slot request or of the Belenos diagnostic request builds with a successor
builder and reads with its paired analyzer. Each pair states the billing rule of
[`scripts/billing_rule_v2.py`](../../scripts/billing_rule_v2.py), carries `acquisition_admission: ready`, binds its own
sources into the request, and admits a run only against that request's sha256
([billing-rule successor record](../evidence/quandela-billing-rule-successor/README.md)). A simulator run rehearses the
whole path (build, plan, review packet, submit, collect, analyze) on a platform whose charge is the per-job price, so
the pair meets provider data before a QPU job depends on it.

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
| sim:ascella, sim:belenos | the price per shot is 0 on every simulator: [credit optimization runbook](../runbooks/quandela-credit-optimization.md), "The billing rule" (lines 34 to 42) and "Simulator jobs are not free" | 1 credit |
| qpu:ascella, qpu:belenos | 1 credit plus 1e-6 per billed shot | 1 + 1e-6 times the smaller of the shots used and the largest iteration's `max_shots` |

Simulator jobs are billed. A retained sim:ascella run of the frozen target-slot request used 8 iterations of 32768
events and charged 1.0 credit (`qd_platform.run_facts` of
`results/quandela/runs/2026-10-30T010726Z-sim_ascella-ascella_predecessor-source-compatible`, `charge` 1.0). The
platform note [platform-specifications.md](../notes/quandela/platform-specifications.md) records the simulator tariff
as unresolved and asks a case to budget at least 1.0 credit per job; this plan budgets 1.0 and reads the usage report
before and after each job as the check.

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
the build argument `--platform qpu:ascella`, and `--admit-status running` on `plan`, `review` and `submit`, because
qpu:ascella accepts a job while the chip reads `running` and the token queue holds a free slot
(`qd_platform.require_token_capacity`).

The rehearsal passes when the analyzer prints `"verdict": "descriptive-only"` with `"platform": "sim:ascella"`, every
iteration returns 32768 events in total, and the usage report moved by one job and 1.0 credit. An iteration may hold
fewer eligible single-photon events than that total, as the retained run's `eligible_counts` 32767 and 32766 did, and
the analyzer reads the eligible count it finds.
