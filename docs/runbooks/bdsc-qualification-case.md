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
3. A case builder emits one run directory per setting under
   `results/quandela/runs/`, with the processing policy written into the job
   body (`mitigations` absent for provider defaults, an empty list for the
   empty policy) and the completion's description recorded beside the chip
   column. `scripts/qd_platform.py` sets no mitigation policy per case, so
   this builder is the first implementation step.
4. A fresh `qd_platform.py snapshot` and a `plan` that passes for
   qpu:belenos, including `specs.architecture`.

## Order

1. Write the case: the eight cells, 22080 eligible trials per setting, the
   margin 0.05 at alpha 0.01, the two epochs, the 66.83-credit ceiling at
   one job per setting and max_shots = 2 x 22080, the ANU QRNG draw that
   fixes the order and seeds, the stop conditions below, and the
   interpretation of each outcome from the design. Wait for approval; the
   QRNG read is part of what it approves.
2. Draw the acquisition order of the 48 epoch-1 settings and the
   compilation seed of each with `scripts/anu_qrng.py draw`, and freeze both
   in the run directories before the first submission.
3. Run epoch 1 in the frozen order. After each job, `collect` and confirm
   that the returned processing matches the requested policy and that the
   server version and calibration identity are recorded.
4. Run epoch 2, the f and g references of every cell, separated in time
   from epoch 1 by at least one platform calibration cycle
   ([calibration.md](../notes/quandela/calibration.md)).
5. Read each cell through `bdsc.consistency_readout` at
   `alpha_per_cell`, only when the observation contract of the design holds
   for that policy; a result converted from probabilities gets the
   likelihood of its own object, never the binomial interval.

## Stop conditions

Execution stops, and the remaining settings stay unsent, when
`qd_platform.py plan` refuses the platform, a returned result's processing
differs from the requested policy, a job fails or returns fewer eligible
trials than the frozen n, or the per-run server version or calibration
identity cannot be recorded. No setting is added or repeated after viewing
outcomes; the stopping rule is fixed n.

## Records

Each run directory keeps the case, the job body, `submission.json` and
`raw/result.json` as the Quandela runner writes them
([README.md](../notes/quandela/README.md)), plus each job's returned
compiled circuit, without which a difference between the two preparation
descriptions cannot be split into preparation and compilation. The cell
readouts and their disposition land under `docs/evidence/bdsc/` with the
run digests they read.
