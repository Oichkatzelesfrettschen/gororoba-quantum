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
3. `scripts/bdsc_cases.py --check results/quandela/cases/bdsc_qualification`
   passes: the 8 case directories, one per pair, policy and epoch, carry
   each job's processing policy (`mitigations` null for provider defaults,
   an empty list for the empty policy), which `qd_platform.py` writes into
   the job body, and each setting's template beside its chip column.
4. A fresh `qd_platform.py snapshot` and a `plan` that passes for
   qpu:belenos. The cases submit parameterized templates, which `plan`
   checks without `specs.architecture`; it reads the architecture only for
   mesh and seeded cases.

## Order

1. Run `qd_platform.py plan` on every run directory and read from it the
   live price per shot, the per-job duration limit and Perceval's shot
   estimate.
2. Write the case: the 96 settings in 8 jobs of 12 iterations (one per
   pair, policy and epoch on the union circuit), 300000
   eligible trials and max_shots = 600000 per iteration (57600000 shots in
   all), the three contrast families with their 0.02 margins at alpha
   0.01, the power of 0.9845 under E0, the two epochs, the credit and
   seconds ceilings restated from step 1 (12.8 credits and about 1354 s
   estimated, 2400 s capped), the QRNG read with its own fields from
   `qrng` in the case record (the keyed ANU Quantum Numbers service, one
   request of 192 uint16 values, about 2 s, no credits, one of the 100
   monthly requests, and why a pseudorandom stream does not serve), the
   stop conditions below, and the interpretation of each outcome from the
   design. Wait for approval; the QRNG read is part of what it approves.
3. Draw one ANU QRNG record of 192 uint16 values with
   `"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng --length 192 --type uint16 --source aqn`;
   it fixes each iteration's compilation seed and each job's iteration
   order. Rebuild the run directories with `scripts/bdsc_cases.py --write
   DIR --draw RECORD`, which writes the record's repository path, its
   sha256 and every setting's seed and order index into each manifest and
   refuses a record another case already names; pass `--check DIR --draw
   RECORD`, and commit the record and the manifests before the first
   submission.
4. Run epoch 1 in the frozen order. After each job, `collect` and confirm
   that the retained job body carries the requested policy, that the
   result is an integer BSCount, and that the server version and
   calibration identity are recorded. A returned iteration names no applied
   mitigation, so what the default policy received is a provider-contract
   answer, never read from the result.
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
`qd_platform.py plan` refuses the platform, a retained job body differs
from the requested policy or a result is not an integer BSCount, a job
fails, an iteration returns fewer samples than the frozen n or the
one-click eligibility rule excludes more than 1 % of its samples, the
per-run server version or calibration identity cannot be recorded, or spent
credits or seconds reach the approved ceiling. No setting is added or repeated after viewing
outcomes; the stopping rule is fixed n.

## Records

Each run directory keeps the case, the job body, `submission.json` and
`raw/result.json` as the Quandela runner writes them
([README.md](../notes/quandela/README.md)), plus each job's returned
compiled circuit, without which a difference between the two preparation
descriptions cannot be split into preparation and compilation. The cell
readouts and their disposition land under `docs/evidence/bdsc/` with the
run digests they read.

## Amendment of 2026-10-22: tc-def-e2 as an engineering run

Step 5 is amended for one job. tc-def-e2 is submitted before a completed
platform calibration cycle since epoch 1 is documented, as an engineering
validation of the live path at the reviewed collector revision: the
freshly built body carries the requested policy, and the result, its
iterations and any partial failure are retained and read correctly. qpu:belenos
read `running` at plan time, and its published figures had moved from epoch
1's (HOM 80.4 % against 87.3 to 87.8 %, transmittance 5.25 % against 6.05 to
6.13 %, g2 0.9 % against 1.0 %). That movement shows a changed characterization,
and it does not establish a calibration cycle, so tc-def-e2 keeps its case
identifier while its epoch contrasts carry no claim of reproducibility across
a calibration change until a calibration boundary between its acquisition and
epoch 1 is documented. The job's manifest, seeds, policy, iteration order and
1.6-credit ceiling stay those of the approved case. tc-none-e2, mm-def-e2 and
mm-none-e2 stay unsent until the calibration boundary is documented, and
their submission then follows Step 5 unamended. Every returned result is
retained whatever it shows, and the stop conditions above still govern.
