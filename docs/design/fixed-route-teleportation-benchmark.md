# Fixed-route six-state teleportation benchmark

This is a prospective, unsubmitted design. Its generator and estimator are
implemented; the design reports no new QPU acquisition, compiled-native-channel
certificate or surviving-output demonstration.

## Question and falsifier

The [historical Tuna-17 experiment](../notes/quantum_inspire/experiments.md)
assigns one of four inputs to each of four routes. Those observations do not
separate input, analyzer and route effects. The successor crosses all six
Pauli eigenstates with every selected four-qubit route in every acquisition
block. A result that depends on input or route is retained at that cell;
no cross-route average is promoted to a single-channel fidelity.

The [contract module](../../gororoba_quantum/teleportation_contract.py) owns
input preparation, basis alignment, frame parity, topology admission and the
conditional finite-count estimator. The
[CLI](../../scripts/qi_teleportation_design.py) emits complete cQASM batches
and consumes acquisitions through `qi_records`, rather than implementing a
second provider-record reader. The historical generator and retained bytes
remain unchanged.

## Circuit and parity

Time order is preparation on I; H(P1); CX(P1,P2); SWAP(P2,D);
CX(I,P1); H(I); basis alignment on D; full-register terminal readout.
Barriers mark preparation/channel/readout boundaries. They do not certify
that a compiler implements the same native channel in every input circuit.

With a=m(I), b=m(P1), and d=m(D), the frame is X^b Z^a. Decode Z
as d XOR b, X as d XOR a, and Y as d XOR a XOR b. Expected decoded bits
are 0 for |0>, |+>, |+i>, and 1 for |1>, |->, |-i>. There is no extra Y
inversion. Basis alignment is identity, H, or S-dagger then H, respectively;
it is not inverse state preparation. Every Bell branch contributes. P2 is
read but is not a selection condition. This is not a live-output protocol.

## Design and admission

The operator selects ordered I-P1-P2-D routes from an explicitly supplied
catalogue. Each block permutes all route-by-input cells using a new seed
admitted by `qrng_seeds`; the complete order and seed-source record survive
in `plan.json`. Seed allocation follows the existing QRNG ledger. The
bounded tests use deliberately constructed permutations and no random draw.
One route is active per circuit; simultaneous-route crosstalk is not quietly
introduced as another varying factor. Batches respect the provider module's
`HARDWARE_BATCH_CIRCUITS`, and partial final batches remain valid.

Before submission, retain a written approved case, fresh provider admission,
native core-circuit/timing comparison (including provider-compiler acceptance of
the barriers between preparation, channel and readout), preparation/analyzer controls and a
calibration receipt. Conceal input labels from the candidate channel and
account for compiler optimizations or other label side information. A
matching route identifier is necessary, not sufficient, to establish a
common physical instrument. Cost, queue limits, account selection and
provider submission remain with the existing runners. This CLI has no
submission mode and authorizes no provider job.

## Estimator and uncertainty

For six input rows on one route and one declared calibration, report

    F_hat = (1/6) sum_i k_i / n_i
    epsilon = sqrt(log(1/alpha) sum_i(1/n_i) / 72)
    lower = max(0, F_hat - epsilon)

The bound follows [Hoeffding's inequality](../notes/papers/hoeffding-1963.md) for fixed, independent bounded
trials with weights 1/(6 n_i). It is one-sided and sampling-only. The CLI
allocates family alpha by Bonferroni over every preplanned block/route
report. It reports all groups and does not select the best path or pool
blocks. Increasing n_i cannot certify stationarity, eliminate drift, or
remove SPAM and label leakage.

The 2/3 comparison (the classical bound for six input states, as used in
[Anderson et al.](../notes/papers/1901.02260.md) and
[Ma et al.](../notes/papers/1210.1282.md)) is conditional on a common input-independent instrument,
trusted six-state preparation/readout, fixed stopping and the stated
sampling assumptions. A `lower_exceeds_classical_bound` field records only
that numerical comparison; `instrument_admission` remains uncertified by
this analyzer. The supplied calibration file is digest-bound evidence, not
an automatically verified assertion of stationarity. A batch with missing
shots, missing states, repeated job IDs, mismatched plan hashes, or accepted-
only selection is rejected rather than renormalized.

For postselected instruments, unequal priors or other ensembles, use the
existing [classical benchmark solver](../../scripts/qd_classical_benchmark.py)
and its stated instrument assumptions; this estimator does not substitute
an unconditional bound for that problem. A full output tomography protocol,
reference-output entanglement test and surviving-output dynamic protocol
remain separate acquisitions.

## Commands

Use a fresh retained QRNG reference and its allocation, not a hand-picked
integer. The argument is supplied by the operator; this example draws none.

```sh
python scripts/qi_teleportation_design.py prepare \
  --catalogue docs/evidence/quantum_inspire/catalogue.json \
  --backend tuna_17 --route 1 0 2 4 --route 5 3 6 9 \
  --blocks 6 --shots 16384 --experiment tuna-fixed-route-six-state \
  --seed "$QRNG_REFERENCE" --out "$NEW_CASE_DIRECTORY"

python scripts/qi_teleportation_design.py analyze \
  --plan "$CASE/plan.json" --calibration-record "$CALIBRATION_RECORD" \
  --alpha 0.05 "$CASE"/batch-*/ > "$ANALYSIS_OUTPUT"
```

The analysis command requires collected run directories in the existing
`qi_records` format, not merely the generated circuit directories. A
provider adapter may retain them elsewhere; name those directories instead.

The companion [publication contract](../evidence/teleportation-publication/README.md)
keeps the October evidence snapshot separate from this unexecuted design.

Work status and acquisition holds: [plan record](../state/plans/teleportation-publication-and-fixed-route.json).
