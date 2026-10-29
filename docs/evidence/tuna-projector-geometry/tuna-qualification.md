# Tuna projector register qualification refused

The reviewed three-circuit qualification completed on Tuna-17 on 27 October 2026.
All 12,288 requested shots were collected, with 14.989993 seconds of reported execution
and zero recorded transaction charges. The frozen screen refused qualification:
four of twelve required assignment contrasts and all nine early/final disagreement
checks failed. The terminal disposition is **protocol inadmissible** for the intended hardware geometry
inference. The refusal stops successor hardware acquisition under this case.

The [run](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/qualification.json)
retains batch 895407, jobs 1616329 (prepared zero), 1616330 (prepared one), and 1616331
(geometry), with 4096 shots each. Provider timestamps place execution in that order
between 17:21:52 and 17:22:08 UTC, following roughly 17 minutes waiting after submission.
Per-job execution durations are 4.948185, 4.896220 and 5.145588 seconds. The 14.31264-second
planning estimate was 0.677353 seconds below the observed total; each job remained below
the 300-second provider ceiling.

[Approval](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/approval.json),
[passing live admission](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/live-admission.json),
[submission](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/submission.json),
[collection](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/results.json),
and the [execution method](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/execution-method.json)
bind the unchanged manifest, source programs, analyzer and reviewed acquisition boundary.
The [peer review](../../archive/reviews/tuna-projector-admission-review.md) used
`gpt-daybreak-blue-latest` at high effort in tmux. The digest-bound Python submission API
satisfied its remaining handoff condition. Local compiler replay reproduced all six
proposal outputs before acquisition. Hardware pulse scheduling remained outside that replay.

## Observed failure

Each raw file contains exactly 4096 binary strings of width 20 and reconstructs its
provider histogram exactly. Raw-byte digests bind retained order; the unsorted sequences
and histogram checks alone cannot establish hardware shot timestamps or independence.
Classical bit zero is the rightmost character. Early bits 17,18,19 correspond to q4,q11,q6;
terminal bits use their physical qubit indices.

| Required channel | Prepared-zero ones | Prepared-one ones | Contrast | Screen |
|---|---:|---:|---:|---|
| Terminal q6 | 2470 | 3858 | 0.338867 | below 0.5 |
| Early q4, bit 17 | 1694 | 3246 | 0.378906 | below 0.5 |
| Early q11, bit 18 | 4039 | 1510 | -0.617432 | below 0.5 |
| Early q6, bit 19 | 3353 | 2845 | -0.124023 | below 0.5 |

Every count has denominator 4096 per preparation arm. The other eight required terminal
channels pass their contrast screen. Terminal q6's prepared-zero one rate is 60.302734%;
early q11's corresponding rate is 98.608398%. These are measured instrument outcomes,
not isolated estimates of detector assignment error.

| Circuit | q4 early/final disagreement | q11 | q6 |
|---|---:|---:|---:|
| Prepared zero | 1699/4096 (41.48%) | 3948/4096 (96.39%) | 1773/4096 (43.29%) |
| Prepared one | 919/4096 (22.44%) | 2639/4096 (64.43%) | 1377/4096 (33.62%) |
| Geometry | 1370/4096 (33.45%) | 3307/4096 (80.74%) | 1565/4096 (38.21%) |

All exceed the frozen 10% maximum. A permutation of the three early bits preserves
the contrast magnitudes, two of which remain below 0.5 even after arbitrary polarity
inversion. Inverting early q11 alone leaves geometry disagreement 789/4096 (19.26%).
A simple early-bit permutation or polarity repair therefore cannot rescue qualification.

## Diagnosis boundary

The [Tuna register note](../../notes/quantum_inspire/tuna-17.md#result-registers)
and retained earlier acquisitions support classical-register readout and the documented
bit order. The local source and compiled programs preserve every destination, including
both measurements of each ancilla. The SDK's local compiler result is therefore compatible
with the intended mapping, while the served downstream acquisition reconstruction remains
unobserved. OpenSquirrel 0.9.1's `Circuit.measurement_to_bit_map` gives q4:[17,4],
q11:[18,11], q6:[19,6], and qi:[i] for every other qubit. Its writer serializes
`Measure.bit`; the Quantify exporter instead emits physical-qubit acquisition channels
and per-qubit acquisition indices. Those interfaces separate acquisition from classical
reconstruction. The installed source does not expose the provider consumer of the map,
so omission of a bit destination in the exporter alone is not a demonstrated defect.

Historical batch 870041, the readout-ringdown P case `tau000-x-d002.cq`, retained 8192
width-34 shots with early q4/q6/q11 one counts 113/225/108 and terminal counts
6975/7197/6923. That case contains Ramsey gates and a 100-cycle settling interval.
It supports historical distinct early/final storage under a different register layout;
it does not qualify compact bits 17/18/19 or immediate repeated readout.

The existing repeated-readout builder, `scripts/qi_readout_ringdown_cases.py`, inserts a
2 microsecond settling interval to avoid residual-photon assignment bias. The qualification
program instead uses a barrier and zero explicit wait between measurement layers. Repeated
readout context is consequently a source-grounded candidate cause. Preparation error,
calibration drift, spectator/readout coupling, served scheduling and acquisition reconstruction
remain alternatives. The unavailable live calibration datasource and unresolved served
readout duration prevent attribution. A historical settling choice does not measure current
hardware timing or prove that adding the same delay would repair this failure.

The failed register/readout admission prevents treating the geometry counts as a test of
projector identities or a causal measurement-backaction mechanism. The exact algebra and
successful QX conformance remain separate evidence. Descriptive geometry outputs are retained
under the run's `analysis/` directory for diagnosis, without a hardware geometry claim.

## Replay and next obligation

The frozen analyzer deliberately exits with refusal after writing a failed screen:

```sh
"$PYTHON" scripts/qi_tuna_qualification.py \
  results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna \
  --check results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/qualification.json
```

Gate `core-qi-tuna-projector-qualification` instead checks that the retained refusal
reproduces exactly, so an observed scientific failure is distinct from a broken evidence
replay. Its focused test is:

```sh
"$PYTHON" -m pytest -q tests/scripts/test_qi_tuna_qualification.py \
  -k retained_hardware_refusal_replays
```

A successor must first isolate readout context and served bit reconstruction, define matched
single/repeated-readout controls and settling conditions from verified sources, and bind its
own explicit acquisition case. The present authorization supplies neither a retry nor the
larger causal campaign. Raw results and the failed qualification remain retained.
