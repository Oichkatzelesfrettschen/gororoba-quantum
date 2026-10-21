# BDSC six-state qualification case

This runbook orders the consistency case that
`docs/evidence/bdsc/qualification_case.json` defines and
[bdsc-qualification.md](../design/bdsc-qualification.md) motivates. The case
tests whether returned observations behave as one fixed linear effect on
independently prepared states; it certifies no subspace. A pass supports
proposing the 160-setting run in its own written case and never starts it.
No step here is authorized until its written case is approved
([AGENTS.md](../../AGENTS.md#hardware-services)).

## Prerequisites

1. `"$PYTHON" scripts/bdsc_certificate.py --check docs/evidence/bdsc` passes
   on the revision that builds the case, so the cells, margin, trials and
   cost ceiling are the frozen ones.
2. `docs/evidence/bdsc/provider_contract.json` carries a provider answer for
   `uncorrected_observations`, `count_provenance` and
   `preparation_control`. A capability still `unresolved` is either answered
   first or named in the written case as the question this run tests.
3. `"$PYTHON" scripts/bdsc_cases.py --write results/quandela/cases/bdsc_qualification`
   builds one case directory per observation: a numeric 24-mode unitary
   (`qd-numeric-circuit-v1`) and a manifest whose `mitigations` is null for
   provider defaults or `[]` to disable them. `--check` rebuilds and
   compares, and `--local` requires Perceval SLOS on each runner-built
   experiment to reproduce the case's ideal selected probability.
   `qd_platform.py` refuses a policy case whose body lacks the policy, and
   refuses the version-1 body Perceval 1.3.1 builds when the processor
   record lacks `specs.commands`, as every qpu:belenos record since
   2026-10-20 does ([calibration.md](../notes/quandela/calibration.md)
   open item 1). Without `--draw` the cases are drafts that plan and do
   not submit.
4. A fresh `qd_platform.py snapshot` and a `plan` that passes for
   qpu:belenos, including `specs.architecture`.

## Order

1. Run `qd_platform.py plan` on every run directory and read from it the
   live price per shot, the per-job duration limit and Perceval's shot
   estimate.
2. Write the case: the 96 settings, 45000 eligible trials and
   max_shots = 90000 per setting (8640000 shots in all), the three contrast
   families with their 0.05 margins at alpha 0.01, the power of 0.939 under
   E0, the two epochs, the credit and seconds ceilings restated from step 1
   (104.64 credits and 1656 s estimated at 17.25 s per single job, 28800 s
   capped), the QRNG read with its own fields from `qrng` in the case
   record (the keyed ANU Quantum Numbers service, one request of 192 uint16
   values, about 2 s, no credits, one of the 100 monthly requests, and why
   a pseudorandom stream does not serve), the stop conditions below, and
   the interpretation of each outcome from the design. Wait for approval;
   the QRNG read is part of what it approves.
3. Draw one ANU QRNG record of 192 uint16 values with
   `scripts/anu_qrng.py draw`, rebuild with `scripts/bdsc_cases.py --write
   DIR --draw FILE`, which seeds each observation and ranks it within its
   epoch, and freeze the cases before the first submission.
4. Run epoch 1 in the frozen order. After each job, `collect` and confirm
   that the returned processing matches the requested policy and that the
   server version and calibration identity are recorded.
5. Run epoch 2, all six states of every cell again, separated in time
   from epoch 1 by at least one platform calibration cycle
   ([calibration.md](../notes/quandela/calibration.md)).
6. Read every contrast through `bdsc.contrast_readout` on the one
   simultaneous event, with each policy's observations admitted only when
   the observation contract of the design holds for it; a result converted
   from probabilities gets the likelihood of its own object, never the
   binomial interval.

## Stop conditions

Execution stops, and the remaining settings stay unsent, when
`qd_platform.py plan` refuses the platform, a returned result's processing
differs from the requested policy, a job fails or returns fewer eligible
trials than the frozen n, the per-run server version or calibration
identity cannot be recorded, or spent credits or seconds reach the approved
ceiling. No setting is added or repeated after viewing
outcomes; the stopping rule is fixed n.

## Records

Each run directory keeps the case, the job body, `submission.json` and
`raw/result.json` as the Quandela runner writes them
([README.md](../notes/quandela/README.md)), plus each job's returned
compiled circuit, without which a difference between the two preparation
descriptions cannot be split into preparation and compilation. The cell
readouts and their disposition land under `docs/evidence/bdsc/` with the
run digests they read.
