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
for q14, equal within the sampling error. q11 is selected because it was measured as a selector in two retained
circuits and because its layout reproduces the retained data roles.

## Certification scope

The producer calls `qi_zero_divisor_cases.certify()`: every product of the three cases from `cd_core` and the four
retained packages, the dark pair's membership in the sedenion zero-divisor corpus, and SELECT equal to
`cd_sign(16, m, q)|m XOR q>` on all 32 inputs. The earlier producer's build adds the exact split-real ideals 0, 1
and 1/2 and compares the routed selector probability of every case against them. Routing and these checks
establish software conformance only.

## Predicted residual (hypothesis)

Model: each region's endpoint contrast decays by a factor `r` per CZ, anchored at the retained region contrasts
0.0504 +- 0.0055 at 75 CZ and -0.0100 +- 0.0055 at 87 CZ, with `r` from 0.913 to 0.962. For the new routes
(81 and 96 CZ) the contrasts are `0.0504 r^6` and `-0.0100 r^9`, and the residual is half their difference.

| r | region 1 contrast | region 2 contrast | residual |
|---|---|---|---|
| 0.913 | 0.0292 | -0.0044 | -0.0168 |
| 0.962 | 0.0399 | -0.0071 | -0.0235 |

The retained uncertainties add 0.0020 to 0.0029 to each residual. The binomial standard error of the residual at
16384 shots and readout factor 0.933 is about 0.0084, so the predicted residual is z of about -2.0 to -2.8: below
the rejection threshold and close to it. A rejection remains plausible from depth alone, and the contrast
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
