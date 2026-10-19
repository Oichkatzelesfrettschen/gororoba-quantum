# ibm_kingston at rep_delay 0: two control jobs that never ran a shot loop

## Finding

A repetition delay of 0 us lies below the 20 us floor IBM's changelog sets
for Heron and Eagle QPUs, while `backend.configuration().rep_delay_range`
on ibm_kingston reads [0.0, 0.002] s. live_run.py admits a delay inside
that range, and the service's own range check (error 1602) accepted 0. Both
jobs then stayed in the running state for 129 s and 207 s, returned no
circuit execution time, and ended in error 1305, the service's "ran longer
than" timeout. The 20 us jobs of the same design at 100,000 shots under a
6 s ceiling also ended in 1305, so the retained jobs report 1305 for every
ceiling cancellation, and the code does not separate a stalled shot loop
from an overrun ceiling. The source pages and their digests are in
[ibm_heron_platform.md](../../docs/notes/ibm_heron_platform.md#repetition-delay-floor-and-timeout-codes).

## The runs

The case was the initialization control of the n21 program at a shorter
delay ([qpu_run_economy.md](../../docs/notes/qpu_run_economy.md)): prep0
and x_history, each its own job, one PUB fusing 148 one-qubit members over
every qubit the 2026-10-18T12:19:44-07:00 calibration admitted, 100,000
shots, `rep_delay` 0, `init_qubits` true, twirling and dynamical decoupling
off, `max_execution_time` 5 s. The planner charged each 2.52 s
(2.3 s job overhead plus shots times delay plus circuit).

| Arm | Approved dry run | record.json sha256 | Run | Job | Running for | Code |
|---|---|---|---|---|---|---|
| x_history | `2026-10-18T200330.601865Z` | `568143a34029df3eac662fa956b1d453ec7836595925a4bad730ad988fcc9175` | `2026-10-18T201601.788510Z` | `dbaii3gc77vs7382spag` | 20:16:15.6Z to 20:18:24.7Z, 129 s | 1305 |
| prep0 | `2026-10-18T200331.136533Z` | `20da4811995a160353d9cb692308d2cb245f3cf4bc9d80817aabeb4b74d6be91` | `2026-10-18T201618.987131Z` | `dbaii7c24mrc7385fjfg` | 20:16:33.0Z to 20:19:59.7Z, 207 s | 1305 |

Both jobs carry the decoded inputs `rep_delay=0.0`, `init_qubits=True`,
the service record `cost` 5, `circuits_execution_time_ns` 0, and the
message "Job %!v(MISSING) ran longer than %!v(MISSING)" with reason code
1305. qiskit-ibm-runtime 0.50.0 sends the value unchanged:
`ExecutionOptions.rep_delay` is `float | None` and the 2.0 executor
converter copies it, so no client-side substitution of a falsy 0 occurs.
The 50 us control jobs of the same design ran from running to finished in
11 to 14 s and billed the 4 s the planner charged
([N21_STATE_PREP_CONTROL_CASE.md](N21_STATE_PREP_CONTROL_CASE.md)).

## Explanations and their falsifiers

1. **Below the execution floor.** The control system accepts a delay down
   to the configuration's 0 but does not complete a shot loop below the
   changelog's 20 us, and the service's timeout ends the job. This fits
   the changelog, the absent circuit time and the code. It is falsified by
   a completed `rep_delay` 0 job on a Heron r2 backend.
2. **Readout timing or result buffer overrun at zero delay** (codes 8038
   and 8045, whose remedies name a larger `rep_delay`). 148 measurements
   per shot at zero delay is the regime those codes describe, but the
   jobs reported neither code. A 0 us job measuring one qubit that fails
   the same way would remove width as the cause.
3. **The default delay substituted for 0.** 100,000 shots at 250 us
   accumulate 25 s of QPU time and would overrun the 5 s ceiling with a
   nonzero circuit time; the jobs report none. The error code carries no
   weight here, since every retained ceiling cancellation reports 1305.
   This explanation is the weakest.

The static prep0 job failed as the dynamic x_history job did, so the
dynamic circuit is not the cause.

## Consequences

- A delay below 50 us is designed at 20 us or more. The configuration's
  `rep_delay_range` serves as the upper bound only, since its lower bound
  disagrees with the documented floor.
- At 20 us the n21 plan bills about 22 s against 28 s at 50 us: 200,000
  executions of about 98.6 us plus the job overhead. Its initialization
  control at 20 us costs about 5 s per arm at 100,000 shots, and it is a
  new case for approval.
- The n21 plan at the same calibration was infeasible at any delay:
  `2026-10-18T200421.028496Z` predicted a contrast difference of 0.0274
  against the 0.0288 that 100,000 shots detect at the declared alpha and
  power, so a short-delay n21 run waits for a calibration that restores
  the contrast.
