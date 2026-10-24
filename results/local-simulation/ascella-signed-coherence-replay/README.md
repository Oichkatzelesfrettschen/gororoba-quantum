# Ascella signed-coherence request replay

The [producer](producer.py) executes the frozen
[job body](../../quandela/cases/ascella_signed_coherence/job-00/job-body.json)
of the [signed-coherence plan](../../../docs/design/ascella-signed-coherence-conformance.md)
on local Perceval SLOS and Naive backends with network connections forbidden,
then runs the registered estimators of
[`ascella_coherence_analysis.py`](../../../scripts/ascella_coherence_analysis.py).
Every one of the 64 entries returns only single-photon states spanning all
twelve output modes, with no probability outside modes 0 to 3; both backends
match the manifest column squared within 1e-12 and agree with each other within
1.2e-16. Both iterators return 8,192 samples per entry, 524,288 in total.

The estimators run on expected counts at 8,192 eligible events per iteration
and on the sampled SLOS counts. The synthetic responses use the prepared
states and analyzers read back from the request's own operators. Their radii,
coefficients and named endpoints must equal
[`derivation.json`](../../../docs/evidence/ascella-order-coefficients/derivation.json).

| Response | Disposition over the 27 primary endpoints |
|---|---|
| Ideal (SLOS probabilities) | 27 qualify; no interval excludes its ideal |
| Sampled SLOS iterator, seed 20261024 | 27 qualify; no interval excludes its ideal |
| Equal contrast: target dark 0.252746, mutation dark 0.08 | mutation difference qualifies; mutation closure falsified |
| Sign-even twist 0.2 | the 15 sign-odd and dark coefficients stay exactly ideal; X_even sin(2 theta), Y_even constant and Y_even cos(2 theta) falsified |
| Sign-even twist 0.05 | 27 qualify; the same three intervals exclude the exact ideal zero |
| Diagonal bright/dark mixture | X_odd constant, X_odd cos(2 theta) and Y_odd sin(2 theta) falsified; dark coefficients qualify |
| Complex conjugation | Y_odd sin(2 theta) falsified |
| Exchanged X and Y readouts | the constant, cos(2 theta) and sin(2 theta) coefficients of X_odd and Y_odd falsified |
| One iteration missing | no complete inference; no decisions issued |
| One iteration without eligible events | no complete inference; no decisions issued |

The dispositions come from expected counts and the declared Hoeffding radius;
they are not measured rejection probabilities. Aliasing on the five-point grid
is a property of the transform itself, which
[the derivation](../../../docs/evidence/ascella-order-coefficients/README.md)
records, so no replay case exercises it. The replay tests the request's
semantics and the analysis; the hardware instrument and its configuration lie
outside its execution boundary.

Run from the repository root with the pinned Perceval 1.3.1 and exqalibur 1.4.2
environment:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" results/local-simulation/ascella-signed-coherence-replay/producer.py --check
```

`--check` recomputes the report and compares it with the retained
[`replay.json`](replay.json), floats within 1e-9 and tool versions aside.
