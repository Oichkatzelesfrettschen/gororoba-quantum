# Tuna-17 per-qubit characterization batch (draft case)

Status: draft. It is no written case in the sense of root AGENTS.md ("Hardware services"): no generator, circuit
file, prediction record or QX conformance run exists, nothing is approved and nothing is submitted. "Not built"
lists what precedes the owner's approval.

## Question

What are the readout assignment probabilities, the relaxation time T1 and the per-pulse error of the `X90` gate
on each of the 17 qubits of Tuna-17 on the day of the run?

## Why the retained data and a simulation cannot answer it

The provider's per-qubit series are withheld: the Tuna-17 dashboard's notice of 2026-10-22 says so, and its
calibration datasource failed to answer on 2026-10-27 and 2026-11-15
([status-source observations](../../evidence/quantum_inspire/status-sources-2026-11-15/README.md)). The
repository's own per-qubit figures
([retained context](../../evidence/qi-status-context/retained-context.json)) date from 2026-10-16 and
2026-10-17: readout pairs at 16,384 shots, and an implied T1 between 5.1 and 52.0 us that rests on one 2 us wait
and on the assumption that readout fidelity stayed the same between two runs. The device is tuned daily and its
readout duration changed twice since April, so those rows are a month-old reading. A noise simulation takes these
quantities as inputs and returns them unchanged.

## Circuits

Every circuit declares `qubit[17]` and measures all 17 qubits once at its end; delays are `wait(n)` in 20 ns
cycles, and every rotation is `X` or `X90`, which lie on the processor's pi/36 angle grid
([operational specifics](site/kbase_tuna-operational-specifics.md)). Fourteen circuits:

- `readout-0`, `readout-1`: no gate, and `X` on every qubit. Run at the start and at the end of the series, so
  the assignment probabilities bracket the other circuits.
- `t1-d`, six circuits: `X` on every qubit, then `wait(n)` on every qubit with n = 0, 250, 500, 1000, 2000 and
  4000 cycles (0, 5, 10, 20, 40 and 80 us). All 17 qubits relax at once, so a qubit's neighbors start in |1>;
  relaxation is read from populations and the static ZZ shift moves no population.
- `x90-k`, four circuits: 4k `X90` pulses on every qubit with k = 0, 8, 32 and 64 (0, 32, 128 and 256 pulses;
  5.12 us at k = 64), each sequence a whole number of full turns. The decay of P(0) with pulse count bounds the
  error per `X90` from above, coherent over-rotation and decoherence together. It is a repetition ladder, and a
  randomized benchmarking figure needs a separate case.

## Batches

Six batches of at most 3 circuits, one queued at a time, each after the pause `qi_platform.py` enforces:

| Batch | Circuits | Shots per circuit |
|---|---|---|
| 0 | readout-0, readout-1 | 16,384 |
| 1 | t1-0, t1-250, t1-500 | 8,192 |
| 2 | t1-1000, t1-2000, t1-4000 | 8,192 |
| 3 | x90-0, x90-8 | 8,192 |
| 4 | x90-32, x90-64 | 8,192 |
| 5 | readout-0, readout-1 | 16,384 |

Each qubit is measured once per shot, so the largest count per qubit per job is 16,384, under the provider's
500,000. Total: 14 jobs and 147,456 shots.

## Expected seconds and credits

Estimate: about 110 s of execution. Basis: retained Tuna-17 jobs of 16,384 shots executed in 9.9 to 12.6 s
([platform facts](platform-facts.md)), which gives 4 x 12 s for the readout circuits; the ten 8,192-shot
circuits take half of that plus their own wait (at most 80 us per shot, 0.7 s), about 6.5 s each. Every job sits
far below the 300 s job limit. Credits: 0; the account's ledger holds no charge after its retained jobs
([usage.md](usage.md)).

## Admission

- The backend instance reads `idle` in the compute API at submission (`scripts/qi_status.py`, `account`
  section), and the account's own queue on Tuna-17 is empty.
- No other series of the account is in flight: the pause and the one-queued-batch rule are account-wide, so this
  series runs before or after the bracketed wave series, never between its batches.

## Predictions and falsifiers

- Readout: P(1|0) and P(1|1) of each qubit within 0.03 of its 2026-10-17 row. A larger move on several qubits
  says the readout settings changed again, and the T1 fit then uses this run's own readout pair.
- T1: a single exponential fits each qubit's six points (chi-square probability above 0.01 after the
  assignment correction). Falsifier: a non-monotone or two-rate decay, which a spurious two-level system produces.
- hypothesis: the provider's tip that Q5, Q6 and Q7 sit away from their flux sweet spot shows as the lowest
  visibility in the retained map and need not lower T1; this run tests the T1 half.
- `X90` ladder: P(0) at 256 pulses stays above 0.5 on every qubit the retained crosstalk run did not flag.

## Record

The analysis writes one row per qubit with its run instant, and `scripts/qi_retained_context.py` then reads the
new rows, so the dashboard's "Our own Tuna-17 measurements" table shows the new date.

## Not built

The circuit generator and its 14 files, the QX conformance run of each circuit, the prediction record with its
decision thresholds, the analysis script, and the case directory under `results/quantum_inspire/cases/`.
