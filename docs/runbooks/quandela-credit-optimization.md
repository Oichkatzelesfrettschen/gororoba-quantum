# Quandela credit and billing optimization

Quandela Cloud bills per job, not per sample. A job costs 1 credit plus 1e-6
per shot of its largest iteration, so a case's credits are set by its job
count; packing settings into the iterations of a few jobs costs an order of
magnitude less than one job per setting. This runbook states the measured
rule, the limits that bound packing, the pitfalls that change what a job
does, and the arithmetic for planning a case. The price figures are the
Explorer offer on this account; the live `qd_platforms` row and the portal
stay the authority, and every written case restates them from
`qd_platform.py plan`.

## Vocabulary

| Term | Meaning in Perceval 1.3 and on the service |
|---|---|
| job | one POST to `/api/jobs`: one experiment, one mitigation list, one or more iterations |
| iteration | one `ComputationIterator` entry: its own circuit parameters, input state, compilation seed and sample and shot budgets |
| sample | one returned outcome that passes the experiment's photon filter |
| shot | one detection event of at least one photon; with one input photon and `min_detected_photons` 1, shots and samples nearly coincide |
| `max_samples`, `max_shots` | the per-iteration stopping budgets; the job stops an iteration at whichever it reaches first |
| credit | the account's billing unit; the Explorer allowance is shared by every platform |

## The billing rule

Charge per job = 1 + price_per_shot x S, with price_per_shot = 1e-6 on
qpu:belenos and qpu:ascella and 0 on the simulators, and

- S = the shots the job actually used, for a one-computation job;
- S = the largest iteration's `max_shots`, used or not, for an iterated job.

A simulator job costs 1 credit whatever it samples.

Evidence: every retained run under `results/quandela/runs/` holds the usage
report before submission (`submission.json`) and after collection
(`results.json`). Their difference on the job's platform is the charge:

| Job | Form | Iterations | Shots used | Largest iteration max_shots | Charge |
|---|---|---|---|---|---|
| 7af74302, 8d28f121, a5f0a8a4, c0db42f6, 3d95587b | single | 1 | 10000 | 20000 | 1.01 |
| aa4218f1 | single | 1 | 1500 | 3000 | 1.0015 |
| f945a01d, fa847dfd, 0f0f242b, 445e0482, 4e208d22, f9e13312 | iterated | 16 | 1500 per iteration | 3000 | 1.003 |
| b8e2ec0c | iterated | 32 | 1500 per iteration | 3000 | 1.003 |
| c2eea262 | iterated | 24 | 1500 per iteration | 3000 | 1.003 |
| 46b810ae | iterated | 24 | 10000 per iteration | 20000 | 1.02 |
| c1eb1cbb | iterated | 9 | up to 60000 | 120000 | 1.12 |
| every sim:belenos job | single or iterated | 1 to 16 | any | any | 1.0 |

The 16 measured qpu:belenos charges and 1.01 for job 7419efb8, whose
before-report predates retention, sum to 17.2255, the qpu:belenos total of
the usage report read on 2026-10-21. The rule reproduces every credit spent
on that platform. strategy.md section 1 and
[form-dwell-decomposition.md](../notes/quandela/form-dwell-decomposition.md)
record the same rule from the first iterated jobs.

## What bounds packing

| Limit | Value | Source |
|---|---|---|
| Duration of one job | 300 s (`max_duration` of the Explorer row) | `qd_platforms`, `plan` refuses a longer case |
| Time per iteration on qpu:belenos | 6.3 s plus 26 us per sample | c1eb1cbb: 9 iterations, 166000 samples, 61 s predicted and measured; 46b810ae: 157 s predicted, 149 s measured |
| Time per one-computation job | 13 to 15 s whatever its samples | aa4218f1, a5f0a8a4 |
| Time per iteration on sim:belenos | about 13 to 14 s | 1d7160c1 and 32b28fe8, 16 iterations in 212 and 230 s |
| Transmittance behind the rates | 2.69 to 2.95 % | `perfs_at_plan` of the retained runs; the rate scales with it |
| Jobs in flight | 1 running and 1 queued | `qd_availability` |
| What one job shares | one experiment (circuit structure and photon filter) and one mitigation list | Perceval `RemoteComputer.prepare_payload` |

An iteration can change only parameters, the input state, the compilation
seed and its budgets. Settings that need different circuit structures, or
different mitigation lists, go in different jobs; settings that differ only
in parameter values share one. A fixed circuit with free phase and splitter
parameters therefore turns many settings into one job.

## Planning arithmetic

For a case of N settings, k iterations per job and n samples per iteration,
with max_shots = h n per iteration (h = 2 leaves room for shots that miss the
photon filter):

- jobs J = ceil(N / k), and k (6.3 + 26e-6 n) stays within a fraction of
  300 s that leaves room for a slower acquisition (0.6 in the BDSC case);
- credits = J (1 + 1e-6 h n) on a QPU, J on a simulator;
- seconds = J k (6.3 + 26e-6 n) on qpu:belenos.

Because the per-shot term is small next to the 1 credit per job, the
optimum fills each job with as many iterations as the duration allows and
then spends the remaining seconds on samples, which buy statistical power
at 2e-6 credits per sample.

## Worked case: the BDSC six-state qualification

`docs/evidence/bdsc/qualification_case.json` has 96 settings: two
preparation templates, two processing policies, two epochs, two pairs and
six states.

| Plan | Jobs | Trials per setting | Credits | Seconds | Power (all 128 contrasts) |
|---|---|---|---|---|---|
| one job per setting, margin 0.05 | 96 | 45000 | 104.64 | 1656 | 0.939 |
| one job per setting, margin 0.02 | 96 | 300000 | 153.6 | | 0.9845 |
| 8 jobs of 12 iterations, margin 0.02 | 8 | 300000 | 12.8 | 1354 | 0.9845 |

Each job fixes a circuit and a mitigation list, so the two policies need
separate jobs; the two templates do not, because both are parameter
settings of one union circuit. The eight jobs are one per pair, policy and
epoch, which keeps every cross-template comparison inside one job. Each 12-iteration job takes
about 169 s, and the tighter margin costs 1.2 credits more than the same
jobs at 45000 trials.

## Pitfalls that change what a job does

- **Payload version.** Perceval 1.3.1 builds a version-2 body only when the
  processor record carries `specs.commands` (`RPCBasedCommunicationLayer.send`).
  Without it the body is version 1, and the round trip back to version 2
  drops an explicit empty mitigation list, so the job runs under the
  server's default. `qd_platform.payload_version_basis` decides the version
  from the record's `pcvl_version` and records the basis in the plan
  ([calibration.md](../notes/quandela/calibration.md), "Record fields
  Perceval reads").
- **Mitigation default.** `mitigations = None` applies whatever default the
  server holds: DetectorBalancing on sim:belenos, none on qpu:ascella, and
  undeclared on qpu:belenos since its record lost `default_mitigations`.
  An explicit `[]` is the only policy the request fixes.
- **Converted results.** DetectorBalancing and PhotonRecycling return
  corrected probability estimates; a count drawn from one is not a Bernoulli
  trial ([bdsc.md](../notes/quandela/bdsc.md), M3). PhotonRecycling needs a
  fixed input of at least three photons, and every one-photon case disables
  it.
- **Requested mitigations on qpu:belenos.** With `known_mitigations` absent
  from the record, Perceval treats any requested mitigation as unknown to
  the server and runs its correction on the client, splitting the job into
  sub-computations.
- **Simulator jobs are not free.** A sim:belenos job costs 1 credit; a
  local Perceval SLOS run of the same experiment costs nothing and checks
  the circuit's ideal output.
- **Unused shot budget is billed on iterated jobs.** A max_shots far above
  the samples an iteration needs is charged in full; set it from the
  expected filter pass rate.

## Before a submission

1. Compute J, credits and seconds with the arithmetic above from the live
   price and duration limit.
2. Run the circuits locally (`bdsc_cases.py --local` for the BDSC case) so
   no credit is spent finding a construction error.
3. Run `qd_platform.py plan` and read its credit ceiling, payload version
   basis and body before the written case.
4. Read `qd_usage` before and after each job; a charge that departs from
   1 + 1e-6 S is a change in the rule, and this runbook takes the new
   evidence.
