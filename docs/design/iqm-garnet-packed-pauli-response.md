# IQM Garnet packed Pauli response case

This case runs the packed Pauli density test of the [current-balance design](packed-pauli-response-current-balance.md)
on Garnet as one 68-circuit job: the 36 circuits of the proposal and 32 buffer circuits. The case directory is
[results/iqm/cases/packed-pauli-response-garnet](../../results/iqm/cases/packed-pauli-response-garnet/cases.json),
built by `scripts/iqm_packed_pauli_case.py build DIR --calibration SRC` from Garnet's default calibration set
`ea681de1-9661-41e5-bd6f-cb524fa056a6` (a live read on 2026-11-21, copied into the case's `calibration/`).
`prediction.json`, bound by digest into `cases.json`, holds the per-circuit predictions. The provider jobs so far are two
`garnet:mock` jobs, `01a1ff98` of the 36-circuit body and `01a1ffe7` of the 68-circuit body (admission items below),
and the paid Garnet job `01a20023` that the owner approved on 2026-11-21 ("Result").

## Question

Does preparing all five four-qubit cells of a twenty-qubit Garnet register, against preparing only the four sentinel
cells, change the sentinel Y-quadrature response B_Y - K_Y? The sentinel cells 2 and 3 (kernel and bright, read with
`Y3 X1 Y0` and the sector bit q2 in Z) have ideal mean scores 0 and 1. Sixteen pairs of one sparse and one dense
circuit, in randomized order, form the sharp-null test of the design; four product-state reference circuits bracket
the pairs. A rejection identifies a response to the compound density intervention (preparation load plus the shared
readout context), not a particular crosstalk, leakage or readout channel.

## Why a simulation cannot answer it

The noise model of `iqm_sim` treats cells as independent: the baseline prediction below is exactly the same for a dense
and a sparse circuit, so the model's dense-minus-sparse response is zero by construction. The question concerns
whatever the device adds beyond that model (pulse crosstalk between neighboring cells, shared control and readout
hardware, state-dependent leakage), and a twenty-qubit simulation of it needs the unknown coupling the experiment
measures. The mock twin returns random bits.

## Backend, circuits and shots

- **Backend:** `garnet` (20 qubits, native `prx` and `cz`), with `garnet:mock` listed for the free runtime estimate.
  The job pins calibration set `ea681de1`, one active-reset cycle and no heralding.
- **Circuits:** the 36 logical programs of
  [the proposal](../../results/iqm/proposals/packed-pauli-response-garnet/proposal.json), each verified by sha256
  before compilation: 2 + 32 + 2 circuits (zero and one product references, 16 randomized sparse/dense pairs, the
  references again). The proposal directory is unchanged byte for byte (`packed_pauli_probe.py --check` passes).
  The compiler is `transpile` onto the Garnet target (`r`, `cz`) with the proposal's physical map as the fixed initial
  layout and `routing_method="none"`. A SWAP, a gate outside `r`, `cz` and `measure`, a CZ off the calibration's loci,
  a final index layout that differs from the fixed initial layout, a two-qubit gate off the mapped qubits and a measured
  bit that reads another physical qubit than the map's each stop the build. The cells use 4 x 5 disjoint qubit sets, so
  no CZ crosses cells. The 32 science circuits are byte for byte the circuits of the earlier 36-circuit build.
- **Barrier and measure:** a program's two halves, preparation before its barrier and readout rotations after it, compile
  separately on the fixed layout and join at one IQM `barrier` instruction over all twenty qubits, so no preparation gate
  follows the barrier and no readout rotation precedes it by construction. The build also checks that each cell holds
  the logical preparation state at the barrier. A single joint `measure` over the twenty physical qubits in logical bit
  order ends each circuit, so shot bit `4c + b` is algebra bit b of cell c.
- **Buffers:** one fixed buffer circuit precedes every science circuit: a joint measure of the twenty qubits with no
  gate (`buffer-NNN`, NNN the number of the science circuit that follows; the 32 files hold the same instructions
  and differ in name). The native case adds the buffers, which the proposal did not have, because IQM runs a job's
  segments in order and repeats the whole sequence once per shot
  ([concepts](../notes/iqm/docs/iqm-pulse/concepts.md), line 83), so the dense and the sparse circuit of a pair run
  back to back inside every shot, and one active-reset cycle leaves measured initialization error (bare-zero P(1)
  0.0065 to 0.0680, `results/iqm/reset_billing_pilot_analysis.json`). With a buffer, both arms of a pair follow the
  same predecessor, a buffer. The four reference circuits keep their places and bytes; the job order is two references,
  32 buffer-and-science pairs of circuits in the proposal's randomized order, two references.
- **Shots:** 2000 per circuit, 136,000 register shots, one job.

## Cost

- **Expected time:** 5.111 s: 68 circuits x 2000 shots x 37.5 us (the unheralded active-reset shot of the reset pilot)
  is 5.100 s, and the gate critical path of the 36 original circuits adds 0.011 s.
- **Retained anchor:** the Garnet Grover job ran 1.27 s (0.098 s compilation, 1.175 s execution) for 80,000
  shots, 14.7 us per shot, and billed 2 s
  (`results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover`). The case uses the slower 37.5 us figure.
- **Ceiling:** the plan keeps 2 s of headroom under the cancel threshold, as `scripts/iqm_idle_schedule_probe.py` does
  (`PLAN_HEADROOM`). `iqm_jobs.collect` cancels a run 1.0 s below the seconds the credits buy, so the ceiling buys
  `ceil(1.6 + 5.111 + 2.0 + 1.0) = 10` s: 5.00 credits, recorded as `max_credits` (`garnet:mock` 0.0). The cancel threshold
  is 9.0 s against a planned 1.6 + 5.111 = 6.711 s, 2.289 s of headroom for server compilation of 68 twenty-qubit
  circuits and for runtimes that ran up to 1.5 s above their estimates. The design's planned maximum is 24 credits of the
  30 IQM credits. The earlier 2.50 credits cancelled at 4.0 s, below the 4.31 s plan.
- **What the ceiling guarantees:** cancellation is best effort. `collect` polls, an execution that has ended is never
  cancelled, and a refused cancellation is retried, so the cap bounds spending only while the job runs.

## Preregistered test

1. The analysis reads `raw/measurements.json` through `iqm_records`, a completed non-mock run of this case, and
   refuses any other.
2. Per shot and per cell it forms the 4-bit label (bit b on logical qubit b) and the score of
   `packed_pauli_probe.score`; 2g is an integer in {0, 1, 2}.
3. Per circuit the numerator is the sum over shots of 2g(cell 3) - 2g(cell 2). Per pair the statistic is the
   dense numerator minus the sparse numerator. Buffers enter no pair.
4. `packed_pauli_analysis.paired_pvalue` returns the exact two-sided assignment p-value of the 16 integers. The
   minimum is 2/2^16 = 1/32768; for equal magnitudes, 13 of 16 pairs with the same sign give p = 0.021 and 12 give
   0.077. The test rejects the sharp null at p <= 0.05.
5. Exploratory, deciding nothing: the X-quadrature response, per-cell dense-minus-sparse g, kernel-event fractions
   (q2 = 1 and even parity), product-reference assignment errors and their first-versus-last drift, and
   `carryover_after_dense_minus_sparse`.

The `carryover_after_dense_minus_sparse` output reads the buffers. A buffer's predecessor is the circuit before it in
the job (the first circuit's is the last circuit of the previous shot). For each sentinel cell and for the whole
register, each buffer contributes its excited population (the mean bit over its shots and the cell's qubits); the output
is the mean after a dense predecessor minus the mean after a sparse one, with Welch's standard error over the buffers of
each arm, and a buffer that follows a reference circuit joins neither arm and is listed apart. The first buffer follows
the second reference circuit, so 31 buffers have a science predecessor.

The buffer removes lag-one, treatment-dependent carryover into the science circuit: the circuit before a science
circuit is always a buffer. It leaves lag-two carryover, from the circuit before the buffer through the buffer into the
science circuit, and the diagnostic measures the part of it that reaches the buffer's own readings. A difference
different from zero there is a response of the buffer to its predecessor and bounds the lag-two path.

The baseline is an independent-cell gate and readout baseline: 0.823 per pair for B_Y - K_Y (ideal 1.0) in both
arms (cell 3 g = 0.918, cell 2 g = 0.095), and it predicts a pair statistic of 0. It is not a mean of the device. It
omits initialization error under active reset, relaxation, leakage, coherent error, coupling between cells and
carryover; `prediction.json` lists these omissions.

`--self-test` and the pytest module run model devices without a random generator (cell distributions rounded to whole
shots): a null device reads p = 1 and a zero buffer difference, balanced pair differences do not reject, a planted
dense-only loss of the bright response reads p = 1/32768, a planted lag-one carryover into the buffers reads a nonzero
buffer difference and leaves the primary p-value at 1, and a mock run, a SWAP, an off-locus CZ, a program that needs
routing, an off-map layout, a drifted final layout and a gate that crossed the barrier are refused. The full-build
tests carry `audit` and the unmarked tests cover one pair circuit, one buffer and the diagnostic on small inputs.

## Admission items

| Item | State | Evidence |
|---|---|---|
| Native ISA and map conformance | closed for the client compile | `build` and `check` verify every circuit; each cell's noiseless native distribution equals the logical cell's within 1e-9, and each cell's state at the barrier equals the logical preparation state |
| IQM `barrier` in the job body | closed on the mock | `garnet:mock` job `01a1ff98` (owner AskUserQuestion 2026-11-21T19:31Z) completed the 36-circuit body at 2000 shots with the barrier; run record `results/iqm/runs/2026-11-21T193252Z-garnet_mock-packed-pauli-response-garnet-packed`; its bits are random and are not analyzed. The dynamic architecture lists no `barrier` gate, and acceptance on the mock station is the evidence; Garnet runs the same station-control release |
| Buffer circuits in the job body | closed on the mock | `garnet:mock` job `01a1ffe7` (owner AskUserQuestion 2026-11-21T20:53Z) completed the 68-circuit body (36 proposal circuits and 32 buffers) at 2000 shots, execution estimate 2.807 s (sweep) and 1.207 s (QPU); run record `results/iqm/runs/2026-11-21T205843Z-garnet_mock-packed-pauli-response-garnet-packed`; its bits are random and are not analyzed |
| Served order of a job's circuits | closed by documentation | the repository's mirror of iqm-pulse "Concepts and classes" (`docs/notes/iqm/docs/iqm-pulse/concepts.md`, line 83) states that segments run in order and the whole sequence repeats once per shot; the mock estimate of the 36-circuit body reports `playlist_repeats` 2000. The circuits of one job therefore interleave shot by shot, and the buffers make each science circuit's predecessor a buffer |
| Carryover | open, measured by the diagnostic | the buffer removes lag-one treatment-dependent carryover and leaves lag-two carryover through the buffer; `carryover_after_dense_minus_sparse` reads it per sentinel cell and for the register, and the post-hoc readout split reads the load cell and single qubits ("Result"). The reset pilot measured initialization error after one active-reset cycle |
| Execution timing and reset | closed by the run | job `01a20023` executed the 68-circuit body in 1.636 s, against the 68-circuit mock estimate of 2.807 s (sweep) and 1.207 s (QPU) and Garnet's compiled estimate of 2.231 s (`raw/runtime_estimates.json`); reset residue in "Result" |
| Enforceable cost | open, best effort | ceiling 5.00 credits, cancel threshold 9.0 s; the job billed 2 s, 1.0 credit, below the threshold, so the run measured the cost and did not exercise cancellation |
| Server compilation of 68 twenty-qubit circuits | closed by the run | 0.196 s |
| Result identity and raw joint outcomes | closed for the record format | one 20-bit row per shot per circuit, read in locus order; the circuit order of `cases.json` and `prediction.json` is checked by the analysis |
| Statistical assumptions | open | sharp null, randomization of the generator (seed 20261022, an identifier of the proposal) and carryover limited to the lag the diagnostic reads must hold; shot serial dependence is not tested by the primary test |
| Current-head review | closed for the case | PR 972 reviewed the case and its analyzer (local reviewers, the Advisor and hosted Codex, no findings on 94fa284a2); the retained run, its analysis and this Result carry their own review record, `docs/archive/reviews/iqm-packed-pauli-garnet-run/README.md` |
| Owner approval | closed | owner AskUserQuestion 2026-11-21T22:00Z, "Approve run" |

## Result

Run `results/iqm/runs/2026-11-21T220346Z-garnet-packed-pauli-response-garnet-packed`, job
`01a20023-1aa1-7001-9806-28b92b115b96` (owner AskUserQuestion 2026-11-21T22:00Z, cases.json sha256
12a17407ac83c02762c3cb90b6e3bfe5a80a8f59f50ca323ad109a78e13b153e), compiled on calibration set ea681de1, the set the
case pins and the default the IQM service returned at 21:43 UTC, 20 minutes before submission. Analysis:
`results/iqm/packed_pauli_response_garnet_analysis.json` (`scripts/iqm_packed_pauli_case.py analyze`); post-hoc
readout split: `docs/evidence/iqm-garnet-packed-pauli-run/readout_split.json` from `readout_split.py` beside it. Gate
`core-iqm-packed-pauli-run-replay` replays both byte for byte.

- Preregistered test: the sharp null is not rejected. The 16 pair statistics 2(B_Y - K_Y), dense minus sparse, are
  -229, -74, 49, 64, 28, -9, 149, -60, -21, 85, 115, -51, 45, 116, -57 and 7; the exact paired p-value is
  22553/32768 = 0.688. The arms differ by 0.0025 (dense 0.6924, sparse 0.6900), a point estimate the test does not
  separate from zero; a non-rejection is not evidence that the response is unchanged.
- Descriptive, deciding nothing: both arms read about 0.69 against the independent-cell baseline of 0.823. The
  shortfall of 0.13 appears in both arms, so the load cell cannot be its sole source; the record does not apportion it
  among the errors the baseline omits (initialization under active reset, relaxation, leakage, coherent error,
  coupling between cells and carryover). The X-quadrature response reads -0.110 dense and -0.120 sparse.
- Carryover, descriptive: the buffer's excited population after a dense predecessor minus after a sparse one reads,
  per cell (readout split, Welch standard errors over 16 and 15 buffers), 0.0010 +- 0.0011, 0.0028 +- 0.0017,
  0.0006 +- 0.0014 and 0.0001 +- 0.0012 on sentinel cells 0 to 3, and 0.0118 +- 0.0016 on the load cell 4, which the
  dense arm alone prepares. Lag-one carryover is resolved on the load cell; on the sentinel cells each estimate lies
  within 1.7 standard errors of zero, and cell 1 holds QB12 (below). The buffer after the all-ones reference reads
  0.102 on the register against 0.068 after a sparse predecessor: one all-ones predecessor leaves 0.033 more excited
  population after one active-reset cycle than a sparse science predecessor does.
- Reference drift, descriptive: the record's `drift_first_vs_last_reference_error` lists 0.095 for the first all-zero
  reference (`circuit-000`) and 0.069 for the last (`circuit-034`). The playlist repeats once per shot, so
  `circuit-000` follows the all-ones `circuit-035` of the previous shot; the difference of 0.026 matches the 0.033
  all-ones carryover above and reads as carryover, not drift over the job's 1.6 s.
- QB12, measured (readout split): QB12 reads 1 in 36.2 and 38.8 percent of the all-zero reference shots and 54.8 and
  52.5 percent of the all-ones ones, against 2.6 to 15.3 percent and 91.9 to 98.8 percent on the other nineteen
  qubits. Behind the sentinel cell-1 buffer level of 0.13 (against 0.05 to 0.07 on cells 0, 2 and 3) sits QB12 at
  0.39 after either kind of predecessor. Calibration ea681de1 lists QB12's `metrics.ssro.measure_fidelity.constant` errors as 0.0182 (0 to 1) and
  0.0142 (1 to 0). QB12 is bit 0 of sentinel cell 1, outside cells 2 and 3 that form the primary statistic, so the
  primary test does not read it; its own buffer carryover reads 0.0046 +- 0.0051. The same hour's Grover and sedenion
  jobs are retained separately with their own reading of QB12.
- Cost: compilation 0.196 s and execution 1.636 s, billed as 2 whole seconds, 1.0 credit (balance 25.75 afterwards).
  The case planned 5.111 s from 37.5 us per shot (`ACTIVE_SHOT_SECONDS`, measured by the reset and billing pilot on a
  two-circuit job with one active-reset cycle and no heralding, `results/iqm/cases/reset-billing-pilot`) plus each
  circuit's path; the job ran 12.0 us per circuit-shot (1.636 s over 68 circuits of 2000 shots). The same hour's
  heralded Garnet jobs ran 13.9 us (36 circuits of 4000 shots in 1.999 s) and 18.4 us (28 circuits of 1000 shots in
  0.514 s) per circuit-shot.

Open hypotheses:

- hypothesis: part of the time behind `ACTIVE_SHOT_SECONDS` is paid once per shot of the playlist or once per job,
  not once per circuit, so 37.5 us per circuit-shot overestimates a many-circuit job. Test: a fit of execution seconds
  against circuits, shots and heralding over the retained Garnet jobs (the pilot, this job and the Grover and sedenion
  jobs) before the remaining credits are sized.
- hypothesis: the lag-two path through a buffer into a science circuit is smaller than the lag-one carryover the
  sentinel cells show, since it crosses a second reset. Test: a job that places two buffers before each science
  circuit.
- The low response of the first science circuit after the all-ones reference (`circuit-002`, pair 0's -229) is fixed
  across the shots. The post-hoc [settling reading](../evidence/iqm-garnet-packed-pauli-run/settling.json)
  (`settling.py` beside it) puts circuit-002 -0.09112 below the mean of its arm's other circuits (z -6.86), alike in
  the first and the second half of the shots (z -5.22 and -4.55); the next five science circuits read
  -0.02743, -0.01677, -0.03912, -0.02418, -0.03463, not monotone, and from the seventh on the residuals scatter about
  zero. Each place after the reference holds one circuit, so place, circuit identity and pair are confounded in this
  job, and circuit-002 also follows two all-ones references across the wrap from one shot to the next
  (`circuit-035`, `circuit-000`, `circuit-001`). hypothesis: the deficit is carryover from the all-ones references
  that outlasts one buffer, a step at the first science circuit with a lower plateau after it; a playlist that repeats
  one science circuit at early and late places, with the order rotated across copies, separates place from identity.

## Procedure

```sh
export PYTHON="${PYTHON:-python3}" IQM_TOKENS_FILE=TOKENS.json
C=results/iqm/cases/packed-pauli-response-garnet
"$PYTHON" scripts/iqm_packed_pauli_case.py check $C
D=$(sha256sum $C/cases.json | cut -d' ' -f1)
"$PYTHON" scripts/iqm_jobs.py submit $C packed --qc garnet:mock --approval QUOTE --approved-cases-sha256 $D --max-credits 0.0
"$PYTHON" scripts/iqm_jobs.py submit $C packed --qc garnet --approval QUOTE --approved-cases-sha256 $D --max-credits 5.0
"$PYTHON" scripts/iqm_jobs.py collect RUN_DIR
"$PYTHON" scripts/iqm_packed_pauli_case.py analyze RUN_DIR --out results/iqm/packed_pauli_response_garnet_analysis.json
"$PYTHON" scripts/iqm_packed_pauli_case.py analyze RUN_DIR --out results/iqm/packed_pauli_response_garnet_analysis.json --replay
```

Every command above ran: the two mock submissions and the Garnet submission under the owner's quoted approvals, then
the collection and the analysis on the compute host; `--replay` is the form gate `core-iqm-packed-pauli-run-replay` runs.
