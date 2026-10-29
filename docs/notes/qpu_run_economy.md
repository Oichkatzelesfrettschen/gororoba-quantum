# QPU run economy: information per billed second

IBM bills QPU lock time, about 2 s per sub-job plus (rep_delay + circuit)
x executions (docs/notes/ibm_quantum/estimate-job-run-time.md), against a
600 s rolling 28-day window. This note collects the planning rules that the
n21-feedback-encoded program and the measurement-sequence envelope measured.
Each rule names the record, gate or document that carries its evidence.
Rules 1, 4, 7, 11, 12 and 13 apply to any family live_run.py plans, and
rules 14 to 16 to the measurement-sequence envelope. Rules 2, 3 and 5 to 10 rest on
`--model-method exact`, `--empirical-bernstein` and `--prep-excitation`,
which live_run.py accepts for the N21 families only, and on the
`state-prep-control` family that measures the excitation.

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
   (docs/notes/topics/numerics_best_practice.md).

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
   bounds the excitation a short-delay plan can absorb: a larger declared
   excitation flattens the exact law's contrast, the required tier rises,
   and once it passes the cap the plan records no feasible tier.

5. **The delay changes the price of a shot, not the number of shots.** The
   exact law depends on the declared excitation and the calibration; the
   repetition delay enters only the charge per execution. A plan at a
   longer delay and the same excitation needs the same shots at a higher
   price, so the fallback from a short delay is the default delay at zero
   excess excitation, where the calibration's `prob_meas1_prep0` already
   carries the default-delay excitation.

6. **Calibration moves the required shots as much as the excitation does.**
   The exact law reads every routed instruction's error and every measured
   qubit's readout, so a republish with moved values moves the feasible
   shot tier and the planner charge at a fixed excitation. An approvable
   record is therefore made minutes before the case, with the shot tiers
   narrowed to the expected region and one optimizer candidate, because the
   submission compares calibration with the approved record at the refresh
   and at each batch.

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
   end states are arbitrary. The static arms x_remeasure (x, measure,
   measure) and remeasure (init, measure, measure) read each shot twice, so
   the second read separates a population the first read found from a
   misassignment of the first read, and their row order in the shared job
   puts each remeasure shot after an x_remeasure read of `|1>`
   (`results/live/PRIMORIAL_Q147_REMEASURE_CASE.md`).

8. **The worst qubit's readout sets the control's resolution.** The
   binomial variance of an excited fraction grows with e10, and the excess
   compares two fractions over the readout contrast 1 - e01 - e10. On the
   n21 qubits q125 read e10 = 0.0159 and e01 = 0.0266 in the control's
   planning record (`results/live/2026-10-18T044724.343287Z`), which gives a
   3-sigma resolution of 0.0037 for 32,768 shots at 50 us against 16,384 at
   250 us, against a feasibility edge near 0.02. Shots go 2:1 toward the cheaper delay, since
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
    ([simulation-cost-levers.md](../runbooks/simulation-cost-levers.md)).

14. **An envelope adapts its knobs within approved ranges, and each knob
    has one owner.** The measurement-sequence envelope
    ([design](../design/measurement-sequence-adaptive-envelope.md)) bills
    about 2.3 s per job plus shots x (circuit + repetition delay + 9 us)
    summed over its PUBs. The 9 us is the measured gap between billed and
    planned charge per static shot on Kingston
    ([hardware-controls.md](ibm_quantum/hardware-controls.md), G3), and the
    width-32 run billed 38 s against 31.2 s planned plus 9 us per shot
    ([findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)).
    The successor's 101 PUBs at 8192 shots (827,392 executions) average
    27.5 us of circuit, so one microsecond of delay costs 0.83 s.

    | Knob | Range | Cost | Coupled to | Set by |
    |---|---|---|---|---|
    | Width (qubits per fused PUB) | tiers 16, 24, 32 | none (rule 11) | the null and the sparse detectable gap, both per width; the 45 MB record limit; the layout rule's packing (rule 16) | the case |
    | Shots per PUB | 8192, the null's tier; 4096 halves the charge at a wider settle gap (rule 15) | 47.5 us per PUB execution at 20 us (27.5 us circuit), plus the 9 us residual | the null's binomial counts (`msq_successor_null_batch.SHOTS`), so another tier needs its own null; the settle veto's detectable gap (rule 15) | the design |
    | Repetition delay | 20 to 60 us in 10 us steps, 20 us first | 0.83 s per us | nothing in the analysis: no verdict reads it, and the readers' in-circuit 20 us idle is a prefix of any longer delay; state preparation (rule 1) | the plan; a qualifying failure moves attempt 2 to the cheapest higher step that fits |
    | Ceiling per attempt | ceil(1.5 x expected) | the most an attempt can bill | the expected charge at its delay | derived |
    | Cap | 5 to 240 s, approved per case | the most the envelope can bill | attempt 2 runs only after an attempt 1 that billed at most 3 s, so the reachable spend is max(c1, 3 s + c2) | the owner |
    | Reserve | per case | quota left untouched | the account's other work | the owner |

    At width 24 or 32 the ladder's expected charges are 49.0, 57.3, 65.6,
    73.8 and 82.1 s at 20 to 60 us, and their ceilings 74, 86, 99, 111 and
    124 s. A run that can issue a verdict therefore needs at least 74 s
    spendable; a smaller budget buys no verdict for this family, and the
    plan refuses rather than cut shots.

15. **The settle veto sets the shots; the departure test does not.** The
    departure test's systematic is shared across qubits, so the minimum
    detectable N = 16 departure barely moves with shots: -0.0516, -0.0512,
    -0.0510, -0.0509 and -0.0508 at 1024, 2048, 4096, 8192 and 16384 shots
    on the rehearsal's 24 contexts (`measurement_sequence_analysis.minimum_detectable`,
    the planning row at the 0.018784 floor). The carryover readers need
    fewer than 900 shots on every one of those qubits (reader standard
    error 0.00014 to 0.00057 at 8192 shots, allocation coefficient near
    0.88, screen margin 0.0047 at z 2.955 for width 32). What shots buy is
    the settle veto's reach: its single-outlier detectable gap,
    (3 + 1.28) sqrt(s^2 + tau^2 + se^2) with the median settle standard
    error s at 0.0024 for 8192 shots and tau floored at 0.0019, is 0.0113,
    0.0135, 0.0172, 0.0228 and 0.0312 at 16384, 8192, 4096, 2048 and 1024
    shots for 24 qubits. 4096 shots keep it below the 0.0188 bound floor at
    half the charge; 2048 do not. A tier other than the null's 8192 needs
    its own null and sparse calibration.

16. **Pack the layout exactly.** The envelope's first layout rule scans
    eligible qubits by readout error and keeps each one at CZ distance 3
    or more from those kept, a greedy packing. On Kingston it kept 32 or
    more on all six retained 2026-10-27 snapshots and 28 and 30 on the two
    retained 2026-10-28 snapshots (`results/live/2026-10-28T163139.827337Z`,
    `2026-10-28T224031.317960Z`), and refused width 32 at 31 on the
    17:16 PDT calibration, while the exact maximum packing of the same
    eligible qubits is 35, 34 and 35 on `2026-10-27T205759.964796Z` and
    the two 2026-10-28 snapshots (`scipy.optimize.milp`). Since width costs nothing (rule
    11), the qubit count per billed second is the packing's size: a
    maximum packing chosen at the lowest summed readout error keeps width
    32 available where greedy loses it.

## The run as executed on ibm_kingston, 2026-10-18

The controls are `results/live/2026-10-18T083402.386701Z` to
`2026-10-18T083404.414317Z` and the n21 run is
`results/live/2026-10-18T090603.530638Z`, each with its raw archive and
collect.json; `results/live/qpu-job-inventory.json` binds their jobs to
the account's consumed seconds.

| Stage | Jobs | Shots | Billed | Predicted |
|---|---|---|---|---|
| initialization control, prep0 and x_history at 50 us | 2 | 32,768 per job | 4 s each | 4.01 s (prep0) |
| initialization control, prep0 and x_history at 250 us | 2 | 16,384 per job | 6 s each | 6.43 s (prep0) |
| n21-feedback-encoded at 50 us, eps 0.014393 | 1 | 100,000 per arm | 28 s | 28.17 s |

The n21 execution is 19,559 and 19,745 dt of scheduled circuit (78 to
79 us) plus the 50 us delay: 200,000 executions at about 128.6 us give
25.7 s, and the job overhead brings the total to the 28 s billed. The
circuit is 61 percent of the shot loop and the delay 39 percent.

The control's simultaneous Clopper-Pearson bound on the n21 placement
reads 0.0144 at 50 us and 0.0157 at 250 us, and the 50 us bound fits the
excitation the plan absorbs within `max_shots`; that is the preregistered
inference. The excited fractions over 149 qubits read medians of 0.0045 at
50 us and 0.0047 at 250 us for prep0, 0.0058 and 0.0051 for x_history.
`scripts/state_prep_excess.py` reports those delay differences as point
estimates outside the bound family, and x_history runs in a dynamic job
while prep0 runs in a static one, so they bound no difference between the
delays. The remaining levers on the n21 shot loop are:

- **A delay below 50 us.** IBM's changelog sets the Heron and Eagle
  repetition delay range at 20 to 2000 us, although `rep_delay_range`
  reads [0, 2 ms]; two control jobs at 0 us never completed their shot
  loop ([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md)).
  At the 20 us floor the n21 plan bills about 22 s. The excitation there
  is unmeasured, so the step carries its own control at that delay before
  any run relies on it; the falsifier is a Clopper-Pearson bound on the
  run's qubits above the eps the plan can absorb within `max_shots`.
- **Fewer routed CZ.** The unitary part holds 320 CX before routing on
  the 7-qubit tree, and routing roughly doubles it. IBM's local AI
  routing (qiskit-ibm-transpiler 0.18.0) routed it to 798 CZ against 786
  to 799 for qiskit's optimization level 3 over three seeds, while
  live_run's bounded search reaches 713. Neither tested router improved on
  713; no routing lower bound exists for the circuit, so the encoding, the
  placement graph and untested routers all remain candidates.

## What transfers from Tuna-17

Tuna-17 cannot run n21: its 737 routed CZ at r = 0.9654 per CZ leave a
contrast near 1e-12. Its runs still shape the IBM design.

- **Fill the job.** A Tuna-17 job takes up to 131,072 shots in 300 s, and
  the 126-job fit gives 2.92 s + 0.509 ms per shot, 69.6 s for a full job
  (docs/notes/quantum_inspire/tuna-17-run-design.md); a full job spends
  the fixed cost once. On IBM the same rule meets `max_shots` = 100,000
  per PUB and the per-job overhead. The optimizer's `minimum_charge`
  objective still takes the smallest feasible tier, since every shot past
  it adds delay and circuit time; the executed n21 run took 100,000 shots
  because its approved plan configured that single tier (`shot_tiers`
  [100000] in record.json), feasible at eps 0.014393.
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
docs/notes/algebra_circuit_rules.md); order finding for N = 21 has no Cayley-Dickson content, so
none of them enters its law. The Quantum Inspire QX emulator checks the
deferred-measurement form of the same circuits (gate core-499) and runs no
part of the IBM plan.
