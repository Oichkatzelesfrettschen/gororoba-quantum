# IQM Garnet packed Pauli response case

This case runs the packed Pauli density test of the [current-balance design](packed-pauli-response-current-balance.md)
on Garnet as one 36-circuit job. The case directory is
[results/iqm/cases/packed-pauli-response-garnet](../../results/iqm/cases/packed-pauli-response-garnet/cases.json),
built by `scripts/iqm_packed_pauli_case.py build DIR --calibration SRC` from Garnet's default calibration set
`ea681de1-9661-41e5-bd6f-cb524fa056a6` (a live read, copied into the case's `calibration/`). `prediction.json`,
bound by digest into `cases.json`, holds the per-circuit predictions. Nothing is submitted: the case waits for the
owner's approval, and no mock job has run.

## Question

Does preparing all five four-qubit cells of a twenty-qubit Garnet register, against preparing only the four sentinel
cells, change the sentinel Y-quadrature response B_Y - K_Y? The sentinel cells 2 and 3 (kernel and bright, read with
`Y3 X1 Y0` and the sector bit q2 in Z) have ideal mean scores 0 and 1. Sixteen pairs of one sparse and one dense
circuit, in randomized order, form the sharp-null test of the design; four product-state reference circuits bracket
the pairs. A rejection identifies a response to the compound density intervention (preparation load plus the shared
readout context), not a particular crosstalk, leakage or readout channel.

## Why a simulation cannot answer it

The noise model of `iqm_sim` treats cells as independent: the noisy prediction below is exactly the same for a dense
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
  references again). The compiler is `transpile` onto the Garnet target (`r`, `cz`) with the proposal's physical map
  as the fixed initial layout and `routing_method="none"`. A SWAP, a gate outside `r`, `cz`, `barrier` and
  `measure`, a CZ off the calibration's loci, a changed layout and a measured bit that reads another physical qubit
  than the map's each stop the build. The cells use 4 x 5 disjoint qubit sets, so no CZ crosses cells.
- **Barrier and measure:** the preparation/readout barrier is one IQM `barrier` instruction over all twenty qubits;
  a single joint `measure` over the twenty physical qubits in logical bit order ends each circuit, so shot bit
  `4c + b` is algebra bit b of cell c.
- **Shots:** 2000 per circuit, 72,000 register shots, one job.

## Cost

- **Expected time:** 2.711 s, 36 circuits x 2000 shots x (37.5 us, the unheralded active-reset shot of the reset
  pilot, plus the gate critical path of the circuit, at most about 0.2 us).
- **Retained anchor:** the Garnet Grover job ran 1.27 s (0.098 s compilation, 1.175 s execution) for 80,000
  shots, 14.7 us per shot, and billed 2 s
  (`results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover`). The case uses the slower 37.5 us figure.
- **Ceiling:** `ceiling_credits(2.711, 0.50)` adds the 1.6 s fixed job cost and rounds up to 5 s: 2.50 credits,
  recorded as `max_credits` (`garnet:mock` 0.0). The design's planned maximum is 24 credits of the 30 IQM credits, so
  the ceiling leaves a 9.6-fold margin for server compilation of 36 twenty-qubit circuits.

## Preregistered test

1. The analysis reads `raw/measurements.json` through `iqm_records`, a completed non-mock run of this case, and
   refuses any other.
2. Per shot and per cell it forms the 4-bit label (bit b on logical qubit b) and the score of
   `packed_pauli_probe.score`; 2g is an integer in {0, 1, 2}.
3. Per circuit the numerator is the sum over shots of 2g(cell 3) - 2g(cell 2). Per pair the statistic is the
   dense numerator minus the sparse numerator.
4. `packed_pauli_analysis.paired_pvalue` returns the exact two-sided assignment p-value of the 16 integers. The
   minimum is 2/2^16 = 1/32768; for equal magnitudes, 13 of 16 pairs with the same sign give p = 0.021 and 12 give
   0.077. The test rejects the sharp null at p <= 0.05.
5. Exploratory, deciding nothing: the X-quadrature response, per-cell dense-minus-sparse g, kernel-event fractions
   (q2 = 1 and even parity), product-reference assignment errors and their first-versus-last drift.

The modeled response is 0.823 per pair for B_Y - K_Y (ideal 1.0) in both arms. The sentinel scores read the modeled
readout error (cell 3 g = 0.918, cell 2 g = 0.095) and the model predicts a pair statistic of 0.

`--self-test` and the pytest module run model devices without a random generator (cell distributions rounded to whole
shots): a null device reads p = 1, balanced pair differences do not reject, a planted dense-only loss of the bright
response reads p = 1/32768, and a mock run, a SWAP, an off-locus CZ, a program that needs routing and an off-map
layout are refused.

## Admission items

| Item | State | Evidence |
|---|---|---|
| Native ISA and map conformance | closed for the client compile | `build` and `check` verify every circuit; each cell's noiseless native distribution equals the logical cell's within 1e-9 |
| IQM `barrier` in the job body | closed | `garnet:mock` job `01a1ff98` (owner AskUserQuestion 2026-11-21T19:31Z) completed all 36 circuits at 2000 shots with the barrier, execution estimate 2.251 s (sweep) and 0.651 s (QPU); run record `results/iqm/runs/2026-11-21T193252Z-garnet_mock-packed-pauli-response-garnet-packed`; its bits are random and are not analyzed. Acceptance on the mock station is the evidence; Garnet itself runs the same station-control release |
| Served order of a job's circuits | open | IQM documents that a playlist's segments run in order and the whole sequence repeats once per shot (`docs/notes/iqm/docs/iqm-pulse/concepts.md`, the repository's mirror of iqm-pulse "Concepts and classes"), so the circuits of one job interleave shot by shot; the Garnet mock estimate of this case reports `playlist_repeats` 2000. The exact test's validity rests on the randomized assignment of dense and sparse to each pair's two circuits, the sharp null and the absence of carryover between circuits, not on wall-clock order: back-to-back execution exposes a pair to drift between its two acquisitions, which the randomized order turns into noise; per-shot interleaving puts both arms in every time window and makes carryover from the preceding circuit's shot the assumption to check (the reference circuits' assignment error at each end bounds it) |
| Execution timing and reset | open | the timing is an estimate; the mock runtime estimate and the real runtime are unmeasured for this case |
| Enforceable cost | closed | ceiling 2.50 credits against the 24-credit plan; `iqm_jobs collect` cancels a run within 1.0 s of the ceiling |
| Server compilation of 36 twenty-qubit circuits | open | the retained 20-circuit job compiled in 0.098 s; this size is unmeasured |
| Result identity and raw joint outcomes | closed for the record format | one 20-bit row per shot per circuit, read in locus order; the circuit order of `cases.json` and `prediction.json` is checked by the analysis |
| Statistical assumptions | open | no carryover between adjacent circuits, sharp null, and randomization of the generator (seed 20261022, an identifier of the proposal) must hold; shot serial dependence is not tested by the primary test |
| Current-head review | open | pull request review and resolution |
| Owner approval | open | the written case above |

## Procedure

```sh
export PYTHON="${PYTHON:-python3}" IQM_TOKENS_FILE=~/.config/iqm/tokens.json
C=results/iqm/cases/packed-pauli-response-garnet
"$PYTHON" scripts/iqm_packed_pauli_case.py check $C
D=$(sha256sum $C/cases.json | cut -d' ' -f1)
"$PYTHON" scripts/iqm_jobs.py submit $C packed --qc garnet:mock --approval QUOTE --approved-cases-sha256 $D --max-credits 0.0
"$PYTHON" scripts/iqm_jobs.py submit $C packed --qc garnet --approval QUOTE --approved-cases-sha256 $D --max-credits 2.5
"$PYTHON" scripts/iqm_jobs.py collect RUN_DIR
"$PYTHON" scripts/iqm_packed_pauli_case.py analyze RUN_DIR --out results/iqm/packed_pauli_response_garnet_analysis.json
```

Every command above is not run; the submissions wait for the owner's quoted approval.
