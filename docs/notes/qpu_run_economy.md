# QPU run economy: information per billed second

IBM bills QPU lock time, about 2 s per sub-job plus (rep_delay + circuit)
x executions (docs/notes/ibm_quantum/estimate-job-run-time.md), against a
600 s rolling 28-day window. This note collects the planning rules that the
n21-feedback-encoded program measured. Each rule names the record, gate or
document that carries its evidence. The rules apply to any family that
live_run.py plans.

## The run, from 83.1 s to 25.5 s

| Plan | Repetition delay | Inference | Replicas x shots per arm | Planner charge | Record |
|---|---|---|---|---|---|
| reference | 250 us | Hoeffding detection, Cantelli power through the variance UCL | 2 x 122,880 | 83.1 s | `results/live/2026-10-17T130242.718497Z` |
| shorter delay | 50 us | same | 1 x 98,304 | 27.73 s | `results/live/2026-10-17T203941.331080Z` |
| empirical Bernstein | 50 us | Hoeffding or empirical Bernstein per PUB, split alpha | 1 x 90,112 | 25.48 s | `results/live/2026-10-17T214153.170495Z` |

The same calibration under Hoeffding alone needs the 106,496 tier and
29.695 s (that record's CASE_ADDENDUM.md). The exact model, the delay and
the bound each contribute; none of them changes the circuit.

## Rules

1. **Price the shot loop before the circuit.** At the 250 us default the
   repetition delay is 78 percent of every n21 execution
   (gororoba_quantum/N21_USAGE_BUDGET.md, usage model). `--rep-delay`
   sets it within `backend.configuration().rep_delay_range`, and the policy
   and execution contract bind it. A shorter delay raises preparation error
   (repetition-rate-execution.md), so a delay below the default carries a
   state-preparation control on the run's own qubits.

2. **Plan on the exact law.** The sampled model leaves a simulation
   allowance that made n21 infeasible at any shot count at 65,536 model
   shots; `dynamic_density` gives the branch-resolved law with no allowance
   (`--model-method exact`). Gate core-487 holds it to Aer's density-matrix
   simulation within 1.2e-15 on the cleaned noise model. float64 suffices:
   an x87 80-bit run of the same law moved it by at most 4.4e-16
   (docs/notes/numerics_best_practice.md).

3. **Read the tighter bound per PUB.** For a directional endpoint planned
   on an exact law, `--empirical-bernstein` splits each PUB's tail between
   Hoeffding and the Maurer-Pontil radius and reads the smaller
   (QPU_OPTIMIZATION.md; gates core-529 to core-532). At low score variance
   the detection radius falls to 0.447 times Hoeffding's; at the maximal
   variance it costs 1.09 times. Precision-only endpoints and sampled laws
   are refused, and collection withholds a record whose preregistered rule
   differs from the code's.

4. **`max_shots` caps every PUB.** `configuration().max_shots` reads 100,000
   on ibm_fez, ibm_kingston and ibm_marrakesh
   (docs/notes/ibm_quantum/hardware-controls.md). The planner drops shot
   tiers above it and records them under `selection_trace.shot_ceiling`, and
   each batch rechecks the fresh configuration (gate core-524). The cap
   bounds the excitation a short-delay plan can absorb: in the sweep below,
   50 us at the 15:37 calibration stays feasible at an excess excitation of
   0.02 only at the 98,304 tier, and 0.03 has no tier at or below the cap.

5. **The delay changes the price of a shot, not the number of shots.** The
   exact law depends on the declared excitation and the calibration; the
   repetition delay enters only the charge per execution. A plan at a
   longer delay and the same excitation needs the same shots at a higher
   price, so the fallback from a short delay is the default delay at zero
   excess excitation, where the calibration's `prob_meas1_prep0` already
   carries the default-delay excitation.

6. **Calibration moves the required shots as much as the excitation does.**
   Submit-free n21 dry runs on ibm_kingston, single replica, empirical
   Bernstein, tiers up to 98,304 (records not retained):

   | Calibration | Delay | Excitation | Shots per arm | Planner charge |
   |---|---|---|---|---|
   | 15:07 | 50 us | 0.005 | 81,920 | 23.49 s |
   | 15:07 | 50 us | 0.01 | 90,112 | 25.48 s |
   | 15:37 | 50 us | 0.02 | 98,304 | 27.73 s |
   | 15:37 | 50 us | 0.03 | infeasible | - |
   | 16:04 | 100 us | 0.005 | 81,920 | 31.58 s |
   | 16:04 | 100 us | 0.01 | 81,920 | 31.58 s |
   | 16:04 | 100 us | 0.02 | 90,112 | 34.50 s |
   | 16:35 | 250 us | 0 | 73,728 | 50.77 s |

   At 0.01 the 50 us plan needs 90,112 shots at 15:07, and the 100 us plan
   81,920 at 16:04. An approvable record is therefore made minutes before
   the case, with the shot tiers narrowed to the expected region and one
   optimizer candidate, because the submission compares calibration with
   the approved record at the refresh and at each batch.

7. **Each job costs its overhead, and a job's arms share one shot
   history.** Every job carries about 2.3 s of non-circuit charge, and
   live_run sends dynamic circuits in their own job. The service
   interleaves the shots of one job's circuits in an unspecified order, so
   the state one arm leaves is the history the next shot of any arm starts
   from. A control whose arms answer different history questions therefore
   pays one job per arm and delay: prep0 (init, measure) reads the
   excitation after shots that end near `|0>`, and x_history (init,
   measure, x) after shots that end near `|1>`, the worst case an n21 shot
   can leave. prep0 alone underestimates n21's excitation, because n21's
   end states are arbitrary.

8. **The worst qubit's readout sets the control's resolution.** The
   binomial variance of an excited fraction grows with e10, and the excess
   compares two fractions over the readout contrast 1 - e01 - e10. On the
   n21 qubits q125 reads e10 = 0.0266, which gives a 3-sigma resolution of
   0.0049 for 32,768 shots at 50 us against 16,384 at 250 us, against a
   feasibility edge near 0.02. Shots go 2:1 toward the cheaper delay, since
   a 250 us execution costs about 5 times a 50 us one.

9. **A control measures the device, never the simulator.** The
   calibration noise model starts every qubit in |0>, so a simulated
   state-prep control predicts zero excess by construction; its dry-run
   excited fractions are readout error. The measured bound enters the run's
   plan through `--prep-excitation`.

10. **Approve in two stages bound to digests, with a preregistered
    fixed point.** The control's digests and the decision rule form the
    first case; the run is re-planned after collection, and its fresh
    digest is the second. `scripts/state_prep_excess.py` holds the rule:
    simultaneous Clopper-Pearson bounds over every controlled qubit (three
    per qubit), the readout envelope of the model's and each execution
    calibration's reported values (`--fetch-readout`), and the end-state
    correction eps = u / ((1 - u)(1 - delta)) for x_history's near-`|1>`
    history. Placement and excitation depend on each other, so the plan
    iterates from eps 0 until the bound on the chosen placement no longer
    exceeds the eps it was planned with; simultaneity over the controlled
    set keeps every look covered. The verdict is a planner outcome: the
    short delay if a tier at or below `max_shots` is feasible within its
    ceiling, otherwise the default delay within its ceiling, otherwise
    stop.

11. **Width inside one PUB costs nothing.** The charge is shots times
    (repetition delay plus circuit duration) per job, independent of how
    many qubits the PUB measures in parallel. A one-qubit control fused
    over all 151 admitted ibm_kingston qubits costs what seven qubits
    cost, and it covers any placement the re-plan picks after the
    calibration moves.

12. **Bind approval to calibration values, not timestamps.** Calibration
    republishes every 30 to 40 minutes, often with every value unchanged,
    and the submission re-plans before it compares: about 9.5 minutes for
    151 groups, most of it in Aer noise-model construction. Two approved
    151-qubit records refused at submission with no job sent, because the
    timestamp had moved four times in the 2.5 hours between the dry run
    and the approval. live_run binds each group to the values its circuits
    read (target timing, the error and duration of every routed
    instruction, T1 and T2 of every touched qubit, the readout of every
    measured one), accepts a republish whose values are equal, and refuses
    a moved value before re-planning, against the approved ISA.

13. **Make the submit a check, not a re-plan.** A submission whose planning
    inputs all equal the approved record's reuses the record's predictions
    (`live_run.reuse_approved_predictions`, gate core-549), and a re-plan
    that does run serializes each noise model once and restricts it per
    batch (gate core-548): a 146-qubit ibm_kingston dry run takes 45 s of
    wall time. A submit therefore lands inside the calibration window its
    approval was written against
    ([simulation-cost-levers.md](build_host/simulation-cost-levers.md)).

## The run as executed on ibm_kingston, 2026-10-18

| Stage | Jobs | Shots | Billed | Predicted |
|---|---|---|---|---|
| initialization control, prep0 and x_history at 50 us | 2 | 32,768 per job | 4 s each | 4.01 s (prep0) |
| initialization control, prep0 and x_history at 250 us | 2 | 16,384 per job | 6 s each | 6.43 s (prep0) |
| n21-feedback-encoded at 50 us, eps 0.014393 | 1 | 100,000 per arm | 28 s | 28.17 s |

The n21 execution is 19,559 and 19,745 dt of scheduled circuit (78 to
79 us) plus the 50 us delay: 200,000 executions at about 128.6 us give
25.7 s, and the job overhead brings the total to the 28 s billed. The
circuit is 61 percent of the shot loop and the delay 39 percent.

The control's excited fractions over 149 qubits match at both delays
(median 0.0045 at 50 us and 0.0047 at 250 us for prep0; 0.0058 and 0.0051
for x_history), and the bound on the n21 placement reads 0.0144 at 50 us
against 0.0157 at 250 us. A 50 us delay therefore cost no measurable
initialization error on this device. The remaining levers on the n21 shot
loop are:

- **A delay below 50 us.** `rep_delay_range` admits 0, and at 0 the same
  plan bills about 18 s. The excitation there is unmeasured, so the step
  carries its own control at the shorter delay before any run relies on
  it; the falsifier is a Clopper-Pearson bound on the run's qubits above
  the eps the plan can absorb within `max_shots`.
- **Fewer routed CZ.** The unitary part holds 320 CX before routing on
  the 7-qubit tree, and routing roughly doubles it. IBM's local AI
  routing (qiskit-ibm-transpiler 0.18.0) routed it to 798 CZ against 786
  to 799 for qiskit's optimization level 3, while live_run's search
  reaches 713, so the next reduction has to come from the encoding or the
  placement graph, not from a router.

## What transfers from Tuna-17

Tuna-17 cannot run n21: its 737 routed CZ at r = 0.9654 per CZ leave a
contrast near 1e-12. Its runs still shape the IBM design.

- **Fill the job.** A Tuna-17 job takes up to 131,072 shots in 300 s, and
  the 126-job fit gives 2.92 s + 0.509 ms per shot, 69.6 s for a full job
  (docs/notes/quantum_inspire/tuna-17-run-design.md); a full job spends
  the fixed cost once. On IBM the same rule meets `max_shots` = 100,000
  per PUB and the per-job overhead, so the n21 plan takes the 100,000-shot
  tier when it is feasible within the ceiling.
- **Compare inside one job where history allows.** Tuna batches scatter
  between jobs, so arms compared against each other share a job. On IBM
  that holds for arms with a common end state; arms that set different
  histories cannot share a job (rule 7), and their comparison carries
  bounds that hold across jobs.
- **Read readout where it ran.** Tuna-17 readout faults appear on named
  qubits between runs (docs/notes/quantum_inspire/experiments.md lists the
  excluded ones), so a readout value describes the run that measured it.
  The IBM rule reads the readout in force when each control PUB ran
  beside the planning calibration's.

## Where the local libraries enter

The n21 plan runs on qiskit 2.5.2 (transpilation onto the live Target),
qiskit-aer 0.17.2 (density-matrix replay of the noise model, linked to AMD
AOCL BLAS on the build host), qiskit-ibm-runtime 0.50.0 (Target,
properties, the dry-run Sampler), numpy (the exact law in
`dynamic_density` and the batched estimators) and parallel.py's spawn pool
with one BLAS thread per worker. python-flint, the p-adic and wheel
arithmetic, and the hypercomplex packages validate least-squares
conditioning and the Cayley-Dickson algebra (numerics_best_practice.md,
AGENTS.md); order finding for N = 21 has no Cayley-Dickson content, so
none of them enters its law. The Quantum Inspire QX emulator checks the
deferred-measurement form of the same circuits (gate core-499) and runs no
part of the IBM plan.
