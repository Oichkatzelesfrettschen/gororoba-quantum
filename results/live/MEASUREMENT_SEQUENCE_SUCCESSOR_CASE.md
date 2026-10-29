# Case: the measurement-sequence successor on ibm_kingston, width 32 at 5600 shots

Status: written, not approved. Plan record
[measurement-sequence-pinching-device](../../docs/state/plans/measurement-sequence-pinching-device.json), step
`successor-case`. Design v4.0:
[measurement-sequence-envelope-successor.md](../../docs/design/measurement-sequence-envelope-successor.md), under the
envelope contract `msq-envelope-v2` of
[measurement-sequence-adaptive-envelope.md](../../docs/design/measurement-sequence-adaptive-envelope.md).

## What it measures and why simulation cannot answer it

The run measures the per-measurement departure from ideal pinching on Heron r2: N steps of RX(8 pi / 9 / N), each
followed by a mid-circuit measurement whose outcome is discarded, read against the ideal P0 = (1 + cos(theta / N)^N) / 2,
a unitary N = 16 arm, a duration-matched delay arm and a settle-gap arm. The quantity is the extra transition a real
readout drives per measurement (residual resonator photons, measurement-induced state transitions, leakage), which no
calibration field reports. The Aer noise model applies each measurement as an ideal projector plus the reported
assignment error and idle relaxation, so it predicts zero departure by construction; only the device answers.

The width-32 envelope run of 2026-10-27 (job `dbg08t9j4t8s73abaghg`, billed 38 s) returned no device verdict: its
reset screen withheld all 32 qubits
([findings](MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)). Its raw shot-ordered bits then showed that the screen
guarded a bias the device does not have: carryover through the terminal reset, the 20 us repetition delay and
`init_qubits` is +0.00020 +- 0.00006, and the analysis's (T1, q) fit, not the device, produced half the +0.0185 N = 16
residual ([raw diagnostics](../../docs/evidence/measurement_sequence/envelope-run-raw-diagnostics.json)). The
successor reads relaxation through a gamma-rate fit at q = 1, measures q with a 400 us equilibrium row, bounds
carryover with twelve in-circuit readers, and vetoes q inconsistency with the settle gap.

## Proposed run

One dynamic job of 109 PUBs on ibm_kingston, 32 layout qubits, 5600 shots per PUB, repetition delay 20 us, no
twirling and no dynamical decoupling (the job carries mid-circuit measurement and reset). Every layout qubit runs in
parallel in each circuit, and the executor runs shot j of every PUB before shot j + 1
([repetition-rate-execution.md](../../docs/notes/ibm_quantum/repetition-rate-execution.md)), so the shot after a
circuit belongs to the next circuit; the in-circuit readers and `pattern_crosscheck` measure what one shot leaves for
the next. The layout rule (`layout_rule_v2`, maximum packing at the lowest summed readout error) solves each width
separately; the width-24 alternative below is not a subset of the width-32 layout (qubits 21, 38 and 149 appear only
at width 24).

The width-24 rehearsal (101 PUBs, attempt-1 ceiling 52 s) is the alternative at nearly the same price; width 32 costs
2 s more of ceiling for 8 more qubits, which raise the per-qubit sample and the sparse settle arm's pool.

## Shots: why 5600

The planner admits a design only when every per-qubit planning endpoint reaches its declared confidence half-width
simultaneously: 0.03 on P0 endpoints and 0.055 on contrasts (`MSQ_PRECISION`, from the pinching design), 17 endpoints
per qubit, Bonferroni over 544 endpoints at width 32 (408 at width 24). The binding endpoint is a single-member T1
point near P1 = 0.48 (`msq_p1_t1_d4`): at 4096 shots its exact Clopper-Pearson half-width is 0.0307 at width 32
(0.0302 at width 24), so no valid bound admits 4096 at 0.03, and both 4096 rehearsals of 2026-10-29 (not
retained) ended `design_infeasible`. Under the planner's Hoeffding
union bound the eight-member Zeno contrast endpoint needed about 7990 shots, which set the earlier 8192 floor.

The relaxation family declares every PUB of its job one independent block (`qpu_planning.pub_independence`, the
optimizer's existing independent-block radius). The assumption: the executor runs every circuit once per shot round,
so shots of different PUBs alternate exactly as shots of one PUB do, and the per-PUB Hoeffding radius already assumes
independent shots; the in-circuit readers measure the adjacent-shot dependence. Under it the pooled and contrast
endpoints tighten and the single-member T1 points bind at 5549 shots (width 32) and 5389 (width 24); a test runs the
optimizer at 5548 (refused) and 5549 (admitted). The run uses 5600: the selected candidate's normalized precision
radius is 0.995, every T1 point's half-width 0.0299, the Zeno contrast 0.0211.

## What the run can detect

`measurement_sequence_analysis.minimum_detectable` on the planning row of each rehearsal at 5600 shots, with the
registered scatter floor, finds the pooled departure z reaching -3 at a per-step loss of 0.00439 at width 32, an
N = 16 P0 departure of -0.0491 (mean departure standard error 0.0173), and at 0.00441 at width 24 (-0.0493, 0.0174).
The width-24 rehearsal of 2026-10-28 (`2026-10-28T163139.827337Z`, another calibration) gave -0.0509 at 8192 shots
and -0.0510 at 4096: the per-qubit gate-model systematic enters `pooled_z` as a shared
term, so neither width nor shots move the limit by more than a few percent. The expected outcome is `consistent`
unless the measurement-induced loss exceeds about 0.0044 per step; a run that reads `consistent` bounds it there.

## What the null establishes, and the two readings it leaves

PENDING: the null over both 5600-shot rehearsals, one invocation
(`scripts/msq_successor_null.py REC32 REC24 --calibrate-sparse --arms all`), with per-calibration sparse scales.

The v4.1 null at width 24 and 8192 shots
([successor-null.json](../../docs/evidence/measurement_sequence/successor-null.json)) gave 0 false fires on every arm
and described two devices this run may meet:

- gamma (healthy relaxation, q = 1, gamma-distributed rates): 396 of 400 replicates issue a device verdict (99 %).
- plateau-retained (each qubit draws a (T1, q) pair of the retained width-32 run, q from 0.28 to 1.02): 299 of
  15,710 replicates issue a verdict (1.9 %); the equilibrium screen withholds 84 % and the common settle veto 16 %.

If the device is the gamma device, the run issues a departure verdict. If it is the device the retained (T1, q) fit
described, the equilibrium row and the settle veto withhold it, and the run reports per-qubit q_hat, the settle gaps
and the carryover bounds instead. Both outcomes answer whether q = 1 holds on Kingston, which the retained run could
not; neither can fire a false departure at more than 0.01.

## Assumptions the case states

- Carryover readers ([design](../../docs/design/measurement-sequence-envelope-successor.md#carryover-readers)): the
  qubit's evolution from the terminal reset to the next shot is Markovian; the executor's repetition delay starts
  after the terminal reset completes, so the in-circuit 20 us idle is a prefix of the cross-shot sequence; excitation
  and leakage do not cancel between predecessor classes (the reader reads |2> as 1). `pattern_crosscheck` reads the
  cross-shot carryover under the submitted order and can only refute these.
- One-sign carryover: the vertex allocation bounds every allocation whose carryover keeps one sign across predecessor
  classes; a sign that differs between classes can reach 1.6 to 1.8 times the bound.
- PUB independence (above): the planner's precision guarantee holds for independent shots across PUBs; the qubits of
  one fused PUB may depend within a shot.
- Coverage: the binding run executes inside the calibration domain the null sampled (below).

## Coverage of the null

A replicate of the null gives each slot a calibration drawn with replacement from the rehearsal layout's qubits, at
the rehearsal's shots, so the binding run must plan the rehearsal's family, width and shots, and its layout's
calibration must lie in that pool. `scripts/msq_successor_coverage.py REHEARSAL RUN --factor 1.5` refuses a run when
a live T1, T2 or sx error lies outside the pool's range widened by 1.5, a readout error above 1.5 times the pool's
largest, or the live layout's median of a quantity beyond a factor 1.5 of the pool's (both ways except readout).
The owner chose F = 1.5 and, on 2026-10-28, this pool rule over the earlier per-qubit ratio.

Measured on Kingston record pairs at F = 1.5, the later record as the rehearsal:

| Stand-in run | Rehearsal | Apart | Layout overlap | Per-qubit ratio rule | Pool rule (calibration) |
|---|---|---|---|---|---|
| 2026-10-29T005449.339992Z | 2026-10-29T012554.415581Z | 31 min, width 32 | 32/32 | 11 sx refusals | passes |
| 2026-10-29T010313.262887Z | 2026-10-29T013110.359249Z | 28 min, width 24 | 24/24 | 9 sx refusals | passes |
| 2026-10-28T224031.317960Z | 2026-10-29T013110.359249Z | 2.8 h, width 24 | 11/24 | 21 refusals | q122 sx error 9.9e-4 above the widened maximum 8.2e-4 |
| 2026-10-28T163139.827337Z | 2026-10-29T013110.359249Z | 8.9 h, width 24 | 8/24 | 20 refusals | q122 sx error, as above |

Across the 31-minute recalibration T1, T2 and both readout errors held on every qubit while per-qubit sx error moved
by factors 0.46 to 2.7. The stand-ins run at 4096 or 8192 shots, so the script also refuses each on shots; the table
reports the calibration rule alone. A joint (T1, T2, readout, sx) combination the pool never held stays uncovered.

## Records

Both rehearsals ran at code commit `99ff7d3` (sources unmodified), experiment digest `a078afc16bdad2cc...`, on the
backup account (instance `f59f9992321c`):

| Record | Width | PUBs | Snapshot | record.json sha256 | Planner charge at 20 us | Attempt-1 ceiling |
|---|---|---|---|---|---|---|
| 2026-10-29T012554.415581Z | 32 | 109 | `277a1f8b04db2b3a...` | `a8559c3e01146614...` | 30.33 s | 54 s |
| 2026-10-29T013110.359249Z | 24 | 101 | `e77b74e8c6d03f18...` | `35ad8cc0d93d2b83...` | 29.15 s | 52 s |

Width-32 layout: 0, 5, 11, 15, 17, 20, 23, 29, 33, 42, 45, 50, 55, 57, 61, 64, 71, 74, 82, 89, 93, 98, 105, 109, 123,
126, 134, 140, 144, 148, 151, 154. Each dry run took 317 s (width 32) and 223 s (width 24) wall at
`--simulation-threads 12` on the 6-core build host.

## Cost and account

The envelope's ceiling rule is ceil(1.5 x (planner charge + 9 us x total shots)); the expected charge is the bracket,
35.8 s at width 32 (30.33 s + 9 us x 5600 x 109) and 34.2 s at width 24. The repetition-delay ladder and its
ceilings at width 32: 20 us 54 s, 30 us 63 s, 40 us 73 s, 50 us 82 s, 60 us 91 s (width 24: 52, 60, 69, 77, 86 s).
Attempt 1 runs at 20 us, the Heron r2 floor; a later attempt steps up the ladder only on the delay error codes 1602
or 8030, or a timeout (1305) billed at most 3 s, and the envelope replans at most 3 times.

The backup account `backup-ibm-quantum-platform` read 160 s remaining at the dry run; the primary holds 68 s, below a
54 s ceiling plus its 60 s reserve. The case proposes the approved cap C = 100 s (the backup's 160 s less its 60 s
reserve), inside the owner's 5 to 240 s range; attempt 1 reserves only its own 54 s ceiling.

## Owner decisions

Taken on 2026-10-28:

- Endpoint precision stays 0.03 with the Hoeffding bound, and the relaxation family declares PUB independence; shots
  5600.
- Repetition delay adapts on the 20 to 60 us ladder, preferring 20 us.
- Coverage factor F = 1.5 under the pool rule.
- Width 32, with researched dry-run flags (`--simulation-threads 12`).

Requested for approval: the rule and bounds of the run above (width 32, 5600 shots, the 20 to 60 us ladder, cap C =
100 s on the backup account, coverage at F = 1.5 against the width-32 rehearsal), executed by the commands below.

## Commands

From the repository root, after the null lands:

```sh
export PYTHON=$HOME/.cache/gororoba-quantum/ci-py3.14.7/bin/python3
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
REHEARSAL=results/live/2026-10-29T012554.415581Z
sh scripts/wait_calibration.sh --deadline 86400 -- ibm_kingston --baseline docs/local/kingston-baseline.json \
    --qubits 0,5,11,15,17,20,23,29,33,42,45,50,55,57,61,64,71,74,82,89,93,98,105,109,123,126,134,140,144,148,151,154 \
  && sh scripts/approved_run.sh \
    --check "\"\$PYTHON\" ../scripts/msq_successor_coverage.py ../$REHEARSAL \"\$RUN\" --factor 1.5" \
    -- --family measurement-sequence-relaxation --layout-width 32 --rep-delay 2e-05 --shot-allocation uniform \
    --objective minimum_charge --local-compute auto --local-compute-method density_matrix_dynamic_statevector \
    --simulation-threads 12 --simulation-memory-mb 2048 --optimize --backends ibm_kingston --shots 5600 --seeds 8 \
    --max-pending 200 --min-remaining-seconds 60.0 --no-isolated-reference --cross-group-buffer --shot-tiers 5600 \
    --replica-tiers 1 --optimizer-candidates 1 --model-shots 8192 --precision 0.08 --alpha 0.05 --power 0.8 \
    --simulation-alpha 0.01 --job-overhead-seconds 2.3 --classical-latency-us 20.0 --reserve-seconds 60.0 \
    --max-total-execution-seconds 100 --out ../results/live
```

The binding table (the binding dry run, its sha256, the job id and the billed seconds) is filled from the records
after the submit.
