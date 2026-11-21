# IQM Garnet packed Pauli response case

This case runs the packed Pauli density test of the [current-balance design](packed-pauli-response-current-balance.md)
on Garnet as one 68-circuit job: the 36 circuits of the proposal and 32 buffer circuits. The case directory is
[results/iqm/cases/packed-pauli-response-garnet](../../results/iqm/cases/packed-pauli-response-garnet/cases.json),
built by `scripts/iqm_packed_pauli_case.py build DIR --calibration SRC` from Garnet's default calibration set
`ea681de1-9661-41e5-bd6f-cb524fa056a6` (a live read on 2026-11-21, copied into the case's `calibration/`).
`prediction.json`, bound by digest into `cases.json`, holds the per-circuit predictions. The provider jobs so far are two
`garnet:mock` jobs, `01a1ff98` of the 36-circuit body and `01a1ffe7` of the 68-circuit body (admission items below);
no paid job is submitted, and it waits for the owner's approval.

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
| Carryover | open, measured by the diagnostic | the buffer removes lag-one treatment-dependent carryover and leaves lag-two carryover through the buffer; `carryover_after_dense_minus_sparse` reads it per sentinel cell and for the register. The reset pilot measured initialization error after one active-reset cycle |
| Execution timing and reset | open | the mock execution estimate of the 36-circuit body is 2.251 s (sweep) and 0.651 s (QPU); the real runtime of the 68-circuit job is unmeasured |
| Enforceable cost | open, best effort | ceiling 5.00 credits against the 24-credit plan, cancel threshold 9.0 s against a 6.711 s plan; cancellation is best effort and bounds spending only while the job runs |
| Server compilation of 68 twenty-qubit circuits | open | the retained 20-circuit job compiled in 0.098 s; this size is unmeasured and sits inside the 2.289 s of headroom |
| Result identity and raw joint outcomes | closed for the record format | one 20-bit row per shot per circuit, read in locus order; the circuit order of `cases.json` and `prediction.json` is checked by the analysis |
| Statistical assumptions | open | sharp null, randomization of the generator (seed 20261022, an identifier of the proposal) and carryover limited to the lag the diagnostic reads must hold; shot serial dependence is not tested by the primary test |
| Current-head review | open | pull request review and resolution |
| Owner approval | open | the written case above |

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
```

Every command above is not run; the submissions wait for the owner's quoted approval.
