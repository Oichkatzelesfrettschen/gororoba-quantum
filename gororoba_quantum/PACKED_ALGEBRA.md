# Packed algebra experiments and independent admission

The campaign prepares three independently admitted families: the static ripple
and box-kite acquisition, the four-qubit rank-path sectors, and the complete
4,096-shot folded-QPE diagnostic. Each family keeps its scientific controls,
precision contract, calibration, compiled circuits, and written approval case.
The ripple acquisition targets one static job on one backend. The folded
diagnostic retains twelve dynamic and four coherent PUBs in two jobs.

## Ripple acquisition

`ripple_experiments.py` constructs twelve lanes using 55 logical qubits before
routing: seven five-qubit box-kite lanes, two four-qubit walk lanes, and the
three original Design C ladder lanes of three, four, and five qubits.

The 146 explicit execution rows contain:

- 96 atlas rows, each containing one edge from each of seven box kites.
  Twelve edge blocks carry eight phases each. Edge blocks rotate across lanes;
  every edge's phase sweep binds one routed circuit object on one patch.
- Five companion duplicates that support matched A/B walk exchanges at
  depths zero through four. Each exchange preserves identical atlas neighbors.
- Eighteen isolated representative walk/edge endpoint rows.
- Twenty-four readout rows, one zero/one pair for every edge template in each
  atlas lane. The planner prepares and measures each template's actual final
  physical writer. Initial layout alone cannot determine that writer.
- Three isolated Design C primary rows. The nine original true/flip/omit
  ladder circuits share three existing atlas rows.

The fixed schedule seed shuffles matched bundles reproducibly. Sparse rows
omit inactive experiments entirely. An idle measured placeholder would alter
the neighboring workload and invalidate an isolated reference.

All walk conditions use one parameterized four-layer union template. Disabled
layers bind to zero after compilation, preserving routing and readout sites.
The shallow prefixes therefore retain the compiled template's native overhead;
their cost comes from the actual bound ISA, rather than an assumed depth ratio.
Design C retains its original builders and independent ideal laws. Distinct
ladder templates can route differently, so control comparisons retain routing
and final-readout confounds.

The contract covers the depth-four A/B crossover, individual phase
probabilities, directional bright-minus-dark effects, walk returns, labeled
ladder spectra, representative packing differences, and readout correctness.
Fringe fits and collision statistics remain descriptive. The acquisition
retains the whole shot-ordered distribution for later visualization.

Representative isolated controls measure packing residuals for their named
conditions. Their intervals cannot certify every edge or every possible
hardware crosstalk mechanism. The shared shot index permits joint-error
analysis; separate physical patches do not establish statistical independence.

## Four-qubit rank sectors

The specified dimension-32 multiplication path is

```
a(t) = e1 + (t-1)^2 e10 + t(3-t)/2 e18 - t(t-1)/2 e25.
H = (0, 11, 19, 24).
input(r,j) = r XOR H[j].
output(r,j) = 1 XOR r XOR H[j].
```

Two data qubits identify a basis state inside one four-dimensional sector.
Two selector qubits implement the four signed-permutation terms. PREPARE,
SELECT and inverse PREPARE produce selector-success probability
`||L_a(t) v||^2 / (alpha(t)^2 ||v||^2)`, with
`alpha(t) = sum_s abs(a_s(t))`. The reduction preserves sector-resolved norm
observables. Cross-sector coherent observables require the larger register.

Eight four-qubit lanes evaluate four fixed probes at
`t = 0, 1/2, 1, 3/2, 2`, yielding 160 science members in twenty packed rows.
Sixteen individually isolated dark/bright reference rows bring the total to
36. Every condition in a sector binds one common seven-parameter template.
The 196 contracts cover 160 success means, sixteen packing differences, and
twenty directional effects.

The first four sectors have noncommuting Gram matrices at different parameter
values, which rules out a fixed common orthonormal singular frame. The last
four admit a constant orthonormal frame with squared-norm numerators
`0`, `4*t^2*(t-2)^2`, `(t-2)^2*(t-1)^2`, and `(t^2-t+2)^2`.
Every success prediction divides its numerator by `alpha(t)^2`.

`rank_sector_contracts.py` checks all 1,024 dimension-32 basis products against
an independent recursion, the full symbolic block identity, forty selected
four-by-four operators, all 160 bound science circuits, row occupancy, and
negative controls. Exact algebra establishes the rank statements. Finite noisy
frequencies test specified norm predictions within uncertainty; they cannot
certify an exact zero, exact rank, or the topology of the zero-divisor space.

## Time, precision, and provenance

The planner first checks compiled labeled ideal laws and predicts each
component under fresh calibration. The optimizer admits all required
endpoints together, accounting conservatively for arbitrary dependence
inside one shot and a search-wide finite-simulation allowance. Independent
stationary repetitions remain an assumption. A rejected endpoint rejects the
family; adding qubits cannot repair an unresolved statistical contrast.

The old 116-row, 1,024-shot, approximately 35-second illustration is superseded.
At the historical 250-microsecond repetition delay, 146 rows at 4,096 shots
already require 149.504 seconds of repetition delay alone. Gates,
initialization, readout, and job overhead add time. Fresh backend configuration,
compiled duration, native scheduling, and admission determine the proposed
seconds. Queue time and local preparation remain separate from QPU usage.

`--native-dry-run` reads the archived QPY circuits and calls the client-side
Runtime Sampler with `dry_run=True` for every batch. The adapter preserves the
job split, shot counts, mitigation policy, repetition delay, and execution
ceiling. Separate mock tags prevent confusion with real submission recovery.
The adapter binds record/QPY/source hashes, rechecks fresh calibration, stores
job identities before waiting, and retains native estimates and schedule CSVs.
An unavailable mock backend leaves an explicit unqualified sidecar. Randomized
mock outcomes never become physical measurements or visual data.

Native schedule duration, server usage estimate, local cost model, and final
charged usage are distinct evidence. The native report preserves total timing;
initialization and fixed-overhead components remain unseparated. Native dry
runs leave `record.json`, `isa.qpy`, and the approval marker unchanged.

All three families share the account allowance. Independently admitted cases
must also fit together with the retained campaign reserve. Every actual
submission still requires approval of its exact written case under
[AGENTS.md](../AGENTS.md), including per-job and aggregate ceilings.

## Visual interpretation

The [offline explorer](../results/ripple/cayley-dickson-ripples.html) depicts
exact local predictions. A future measured rendering can show probability
flow, phase-dependent edge darkness, exceptional-point norm suppression,
and hardware-minus-model residuals from the same retained records.
Computational-basis counts do not determine complex amplitudes. Interpolated
frames are artistic playback of separately prepared prefixes. The physical
ripple is controlled interference in the processor; mathematical geometry
and philosophical interpretation remain explicitly labeled layers.
