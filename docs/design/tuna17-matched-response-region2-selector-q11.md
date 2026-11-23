# Tuna-17 matched-response successor with the region-2 selector on q11

The [first matched-response proposal](tuna17-zero-divisor-matched-response.md) routes region 2 so that the
selector lands on q13. Retained readout data show q13's |1> misassignment depends on the neighbors'
prepared state (e10 0.090 with all qubits excited against 0.044 with q1, q13 and q14 alone;
[readout context](../notes/quantum_inspire/tuna-17.md)). Retained zero-divisor runs measured the region-2
selectors q11 and q14 instead. The successor keeps the design (three batches of witness, readout-0 and
readout-1 circuits, 16384 shots per circuit, the dark, bright and quadrature-fixture witnesses, weights
`(0, 0, -1, 1, 1, -1)` and rejection at `abs(z) >= 3`) and moves the region-2 selector to q11. The first
proposal and its receipts keep their bytes. Nothing is submitted.

## Proposal and producer

- `results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11/` holds the nine
  circuits and manifests.
- `scripts/qi_matched_zero_divisor_selector_q11.py` generates and checks it by calling the digest-bound
  `scripts/qi_matched_zero_divisor.py` with region 2 and the catalogue digest of this producer; the earlier
  producer keeps its bytes.
- `docs/evidence/quantum_inspire/matched-zero-divisor-toolchain-region2-selector-q11.json` is the compiler
  receipt, and holds the sha256 of each of the nine circuit files.
- The catalogue digest is that of the retained `docs/evidence/quantum_inspire/catalogue.json`
  (`d717a785...`). The catalogue was not refreshed from the provider; a refresh at submission time may need one
  more successor.

## Roles and routes

| Region | Layout (initial placement, logical qubit 0 to 4) | Selector | d0, d1, d2, d3 | CZ | T |
|---|---|---|---|---|---|
| 1 | 1, 2, 4, 8, 12 | q4 | q8, q2, q12, q1 | 81 | 28 |
| 2 | 11, 13, 16, 14, 10 | q11 | q13, q16, q10, q14 | 96 | 28 |

Region 1 is unchanged. The first proposal routed region 2 with 105 CZ and the selector on q13. Of the 120
initial layouts of {10, 11, 13, 14, 16}, 87 leave the selector on q11 or q14; the layout above is the first of
the 96-CZ layouts that give the data roles of the retained runs (d0 q13, d1 q16, d2 q10, d3 q14 with
selector q11, as in the retained circuits `latin-1` and `latin-3`). It routes with 8.6 percent fewer CZ than
before, inside the 20 percent bound the producer enforces.

## Selector choice

From `results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json` (`replicas`, region
{10,11,13,14,16}): q11 read e01 0.0200 and e10 0.0472 in `latin-1` and 0.0176 and 0.0486 in `latin-3`; q14 read
e01 0.0368 and e10 0.0306 in `latin-2`. The readout factor 1 - e01 - e10 is 0.9328 and 0.9338 for q11 and 0.9326
for q14, equal within the sampling error. q14 is one of the two qubits (with q1) measured to read alike in
isolated and all-excited contexts ([readout context](../notes/quantum_inspire/tuna-17.md)), while q11 has no
retained context probe. q11 was chosen because only the q11-selector layout has retained dark and bright
measurements (`latin-3` and `latin-1`) to anchor region 2, and because it reproduces the retained data roles. The
unprobed readout context of q11 stays an open risk; the readout-context gap between batches is the leading
alternative below.

## Certification scope

The producer calls `qi_zero_divisor_cases.certify()`: every product of the three cases from `cd_core` and the four
retained packages, the dark pair's membership in the sedenion zero-divisor corpus, and SELECT equal to
`cd_sign(16, m, q)|m XOR q>` on all 32 inputs. The earlier producer's build adds the exact split-real ideals 0, 1
and 1/2 and compares the routed selector probability of every case against them. Routing and these checks
establish software conformance only.

## Predicted residual (hypothesis)

Anchors. The region contrasts come from the `replicas` rows of
`results/quantum_inspire/zero_divisor_tuna_17_visibility_floor_analysis.json`: bright minus dark of region 1
({1,2,4,8,12}, selector q4, 75 CZ; `latin-2` and `latin-1`) and of region 2 ({10,11,13,14,16}, selector q11,
87 CZ; `latin-1` and `latin-3`). The raw (uncorrected) selector-zero contrasts are 0.0504 and -0.0100
(standard error 0.0055 each); the readout-corrected contrasts of the same rows are 0.0528 and -0.0088. The
region-1 anchor was measured under roles d0 = 1, d1 = 8, d2 = 12, d3 = 2, while this proposal routes region 1
with d0 = 8, d1 = 2, d2 = 12, d3 = 1; the prediction assumes the contrast is role-neutral. The region-2 anchor
used the roles of this proposal.

Decay. The retained per-CZ retention is r = 0.9654 with a 99 percent interval [0.9638, 0.9671]
(`docs/notes/quantum_inspire/tuna-17.md`, box-kite T0 depth ladder). The earlier band 0.913 to 0.962 has no
retained source and is dropped. For the new routes (81 and 96 CZ) the contrasts are anchor times `r^6` and
`r^9`, and the residual is half their difference.

| anchors | r | region 1 contrast | region 2 contrast | residual | P(abs(z) >= 3) |
|---|---|---|---|---|---|
| corrected | 0.9654 | 0.0427 | -0.0064 | -0.0246 | 0.47 |
| raw | 0.9654 | 0.0408 | -0.0073 | -0.0240 | 0.45 |

Over the 99 percent interval of r the residual spans -0.0238 to -0.0249 and the probability 0.44 to 0.49. The
probability treats the observed residual as normal about the predicted one, with the binomial standard error
0.0084 (16384 shots, readout factor 0.933) and the anchor uncertainty 0.003 added in quadrature, and rejects at
abs(residual) >= 3 x 0.0084. The prediction is a rejection of the common-affine response with probability near
one half, so the case does not expect a non-rejection. When the residual rejects, the leading alternative to a
region-dependent visibility is a readout-context gap that drifts between batch-01 and batch-02 (the all-excited
readout-1 circuit differs from the context of the witness, and q11 has no context probe); the contrast
identifies no mechanism (see the [analysis record](tuna17-matched-response-analysis.md)).

## Submission settings and budget

- Pause between batches: `QI_HARDWARE_PAUSE_SECONDS=120` for each of the three submit calls (a step of
  `HARDWARE_PAUSE_LADDER` in `scripts/qi_platform.py`).
- Nine jobs on `tuna_17`, 16384 shots each, 147456 shots; 101.55168 device seconds from the retained
  2.6 s per job plus 0.53 ms per shot; 0 metered credits under the recorded service terms. Refresh availability,
  terms and queue limits before presenting an execution approval.

## Checks

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON
"$PYTHON" scripts/qi_matched_zero_divisor_selector_q11.py --check results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11
"$PYTHON" scripts/qi_matched_zero_divisor_selector_q11.py --check-toolchain results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11
```

Both commands ran on the remote host with the replay runtime (Qiskit 2.5.2) and the Quantum Inspire interpreter
named by `QI_PYTHON`; neither contacts a provider.
