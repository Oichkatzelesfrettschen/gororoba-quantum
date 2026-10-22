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
   qpu:belenos with `--admit-status running`. The cases submit parameterized templates, which `plan`
   checks without `specs.architecture`; it reads the architecture only for
   mesh and seeded cases.

## Order

1. Run `qd_platform.py plan --admit-status running` on every run directory and read from it the
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

## Amendment of 2026-10-22: one second-epoch job runs before a documented recalibration

The case acquires every setting twice. The first acquisition (epoch 1) ran on
2026-10-21 as four jobs, one per combination of state pair and processing
policy. The second (epoch 2) repeats the same four jobs, and Step 5 requires
it to follow a platform calibration cycle, so that the cross-epoch
contrasts test whether the response reproduces across a recalibration. Each
job's name encodes its state pair (`tc` for target-complement, `mm` for
middle-middle), its processing policy (`def` for the provider's default
mitigations, `none` for an empty mitigation list) and its epoch.

This amendment sends one epoch-2 job, the target-complement pair under the
provider's default mitigations (`tc-def-e2`), before any calibration cycle
since epoch 1 is documented. The job validates the live submission and
collection path at the reviewed collector revision: the freshly built job
body carries the requested policy, and the result, its iterations and any
partial failure are retained and read correctly. At plan time qpu:belenos
reported status `running`, and its published source figures had moved from
their epoch-1 values: HOM visibility 80.4 % against 87.3 to 87.8 %,
transmittance 5.25 % against 6.05 to 6.13 %, g2 0.9 % against 1.0 %. That
movement shows a changed device characterization and does not establish a
recalibration. The job therefore keeps its case name, and its cross-epoch
contrasts carry no claim of reproducibility across a recalibration until
retained evidence places a calibration cycle between it and epoch 1. Its
manifest, compilation seeds, policy, iteration order and 1.6-credit ceiling
stay those of the approved case.

The other three epoch-2 jobs -- target-complement with an empty mitigation
list (`tc-none-e2`) and the middle-middle pair under both policies
(`mm-def-e2`, `mm-none-e2`) -- stay unsent; the amendment below, which
suspends the confirmation design, leaves whether they run to a later
amendment. Every returned result is retained whatever
it shows, and the stop conditions above still govern.

## Amendment of 2026-10-22: a crossed diagnostic replaces the confirmation plan

The [forensic reconstruction](../notes/quandela/bdsc-acceptance-diagnostics.md#forensic-reconstruction-of-the-retained-belenos-runs)
of the five retained jobs shows three things. Superposition settings that
request one output intensity spread far beyond counting noise. The returned
circuits leave the relative phase of the occupied column free. A matched
compilation seed with matched parameters reproduces the returned circuit.
The [design](../design/bdsc-qualification.md#confirmation-design-and-its-falsified-premise)
therefore suspends the confirmation case, and this amendment orders the
diagnostic case that identifies the response components first.

- The three held second-epoch jobs stay unsent: target-complement with an
  empty mitigation list (`tc-none-e2`) and middle-middle under both policies
  (`mm-def-e2`, `mm-none-e2`). Their role as confirmation evidence lapses
  with the suspended design. A later amendment, written after the diagnostic
  readout, decides whether they run. A comparison across a recalibration
  still needs retained evidence that a calibration falls between the two
  executions.
- No separate default-policy repeat of `tc-def-e1` is planned. The
  diagnostic's second block repeats its first block's requests at matched
  seeds under the empty mitigation list. That reproduces the returned
  circuits while the compiler's component model holds, and it keeps provider
  processing out of the comparison.
- Three labels stay separate. An engineering repeat repeats a request. A
  repeated reference under documented conditions also matches the returned
  circuit and the beam-splitter digest. A comparison across a calibration
  intervention needs retained evidence of the calibration between the two
  executions.

### Order of the diagnostic case

[case.json](../evidence/bdsc/diagnostic/case.json) holds the case, built by
`scripts/bdsc_diagnostic.py`. It covers the six target-complement states
under both templates, each compiled with four seeds, in two time blocks: 96
instances of 40000 eligible trials under an explicit empty mitigation list,
in four jobs of 24 iterations. Each template-and-seed group of six states
runs inside one job.

1. `"$PYTHON" scripts/bdsc_diagnostic.py --check` passes. `qd_platform.py
   plan` passes on each of the four directories under
   `results/quandela/cases/bdsc_diagnostic/` for qpu:belenos with
   `--max-credits 1.08 --expected-seconds 176.16 --per-job-credits 1.0
   --admit-status running`.
2. The written case restates the plan output: 1.08 credits per job and 4.32
   in all, about 176 s per job and 705 s in all, and Perceval's shot estimate
   within the 80000 max_shots per iteration. It also covers one ANU Quantum
   Numbers request of 100 uint16 values (about 2 s, no credits), the stop
   conditions of the case record and the branch each readout selects. Wait
   for approval.
3. Draw with
   `"$PYTHON" scripts/anu_qrng.py draw --out docs/evidence/anu_qrng --length 100 --type uint16 --source aqn`.
   Rebuild with `scripts/bdsc_diagnostic.py --write --draw RECORD`, pass
   `--check --draw RECORD`, and commit the record and the manifests before
   the first submission.
4. Block 1: submit and collect `b1-j1`, then `b1-j2`; the readout refuses
   a block whose second job started before its first ended. After each
   collection, confirm the empty policy in the retained body, an integer
   BSCount, 40000 samples per iteration, and a returned compiled circuit and a
   positive `physical_perf` per iteration.
5. Block 2 (`b2-j1`, then `b2-j2`) starts at least one hour after block 1's
   last execution ends. No scheduled maintenance window may overlap the
   span from block 1's first execution to block 2's last, a window already
   open when block 1 starts included; the window on the latest receipt is
   2026-10-22 07:30 to 11:00 UTC.
   `b2-j1` repeats exactly the groups of `b1-j2`. After collecting `b2-j1`
   and before submitting `b2-j2`, run
   `"$PYTHON" scripts/bdsc_diagnostic.py --matched-check B1J2_RUN B2J1_RUN`.
   It compares the returned-circuit hash of each of the 24 matched
   instances and exits nonzero on any difference. A difference means the
   compiler's model changed between the blocks: the case stops, `b2-j2` is
   not submitted (one job's 1.08 credits and about 3 minutes saved), and
   the amendment that follows decides the rerun.
6. `"$PYTHON" scripts/bdsc_diagnostic.py --readout RUN_DIR...` reads the four
   runs. The runs enter `docs/state/research_state.json` with their claim,
   and the readout's branch names the next amendment. The readout's
   branches, in the order it reads them, are `recompiled`, `leak` (an
   instance put more than 0.20 of its one-click samples outside the target
   support), `stationarity`, `seed-common` or `seed-interaction`,
   `common-effect`, `inconclusive` and `ensemble-candidate`. It also reports,
   with no branch reading them:
   - `perf_ratio`: r-hat = perf_g / (perf_f + perf_g) of each group and each
     superposition's deviation from it. physical_perf moves with the sample
     budget and DetectorBalancing rescales it
     ([strategy.md](../notes/quandela/strategy.md)), so the ratio is an
     uninterpreted provider diagnostic, not a qualified output acceptance;
   - `calibration_shift`, the common block-to-block change of the
     superpositions, of f and of g (f and g drift apart in physical_perf),
     apart from the heterogeneity
     test the `stationarity` branch reads;
   - `seed_basis`, the seed dispersion of f and g, apart from
     `seed_superposition`, which the seed branches read;
   - whether the outward and reverse returned circuits of a seed alias, how
     many distinct circuits the four superpositions of a group returned, and
     the rank correlation of the deviation with position in the job.

No certification decision is available from this case or from the
retained runs.
