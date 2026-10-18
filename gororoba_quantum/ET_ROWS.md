# ET-row device experiment

`--family et-row` owns the complete D32 experiment. Dense S1/row2, sparse
S9/row2 and hub S9/row8 each carry fixed-plus/minus Z readout and fixed-plus
X readout with marker zero/one. SELECT derives from `cd_core`, rather than
loading ET occupancy into the prepared fixed-sign state.

## Planning and reconstruction

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" live_run.py --family et-row --optimize \
  --shot-allocation per-pub --shots 8192 --shot-tiers 32,64,128,2048 \
  --max-replicas 1 --replica-tiers 1 --no-isolated-reference \
  --optimizer-candidates 1 --seeds 1 --simulation-threads 1 \
  --backends ibm_kingston,ibm_fez,ibm_marrakesh \
  --max-execution-seconds 90 --max-total-execution-seconds 600 \
  --reserve-seconds 10 --out ../results/et_rows
```

The command reads current backend information and plans locally. Per-job
ceilings and retained reserve can make the complete design infeasible;
the runner records the reasons instead of deleting controls. A resulting
unapproved case binds the actual allocation, calibration and circuit bytes.
The QPU hold continues until the user approves that concrete case.

Four blocks divide 8192 total shots per signal into 2048-shot PUBs. The
record's `shots` field holds the maximum PUB allocation, 2048, so reproduction
also accepts that value; the family manifest always binds the same signal
total. Every readout, held-out, null and decoder PUB has its own denominator.
The complete design has 4656 PUBs and 466944 executions, including:

| Kind | Executions |
|---|---:|
| Signals | 98304 |
| Balanced complete-dephasing ensembles | 49152 |
| Full-register training and held-out readout | 245760 |
| Decoder basis and phase-transfer probes | 73728 |

Block labels describe randomized acquisition cohorts. PUB order supplies
no physical chronology. Collection checks the supplied execution windows
and calibration epochs through the existing runner.

## Compiler and physical contexts

The family configuration binds `arbitrary-input-unitary-v1`. Production
compilation passes `qubits_initially_zero=False` for this contract. Unrelated
families keep their prior compile options. Shared parameterized templates
hold each row/basis decoder and measurement suffix fixed across signs and
phase masks. The native adapter records final physical measurement roles.

Readout controls prepare the actual final measurement sites. Decoder
controls prepare inputs at the compiled decoder barrier and execute its
actual remaining instruction stream. The routed-line regression checks
every sparse-row control and mask against the independent logical law.

## Inference and limitations

The collector retains raw integer histograms. Calibration uses designated
training samples; held-out readout and decoder probes test residuals.
The full response matrix captures correlated readout across the six bits.
An ill-conditioned response or incompatible physical/execution context
withholds scientific admission.

Six endpoints measure signed multiplication contrast and paired marker
response. Coherence subtracts the marker difference of a complete Z-mask
dephasing ensemble through the matched physical decoder. Identical raw
marker distributions therefore carry zero paired marker response even
when an aligned average has positive template overlap.

Calibration fits are shared across endpoint terms. Simultaneous binomial
lower bounds on every response diagonal bound each response column's L1
error. Independent endpoint shots within each fixed-response block permit
weighted Hoeffding bounds; a union bound permits endpoint dependence between
blocks. Training observations are assumed independent of all endpoint
observations. Complete balanced dephasing ensembles contain identical
native programs across markers, so shared response error is charged once
per block. Half of family alpha 0.05 covers
calibration uncertainty; Holm uses the other half for primary endpoints.
Control residual diagnostics have a separate stated tail. The resulting
bounds can be conservative. The planner additionally evaluates the
collector's calibrated rule on plug-in model histograms at the complete
allocation. Failure makes the design infeasible. That screen supplements
the optimizer's raw-observable power calculation; it supplies no guarantee
of calibrated power under unknown physical errors.

The raw power calculation declares the same independent-shot blocks and
uses a union bound between blocks. Each block combines all of its signal
and null PUB shot proxies before the bound. A separate union bound for every
mask PUB would discard the declared independence and reject even the perfect
complete design. The simulation allowance retains the full search's comparison
count when calibrated screening removes candidates.

The report includes calibrated and raw effects, confidence intervals,
control residuals and detection decisions. A bit-zero marker signal can
survive dephasing of other column bits; the regression retains that
counterexample. Detection establishes the specified alternative to complete
dephasing. Full-row fidelity and coherence of every column bit require
additional observations.

D64/D128 ideal contracts and signed child fixtures run offline. Their
native coherence/control suites and hardware cases require separate
qualification. Fixed S15 and moving `S=G/2+1` retain separate trajectory
identities. Whole-table graph operators, Tuna angle-grid synthesis and
Belenos transformation conformance remain separately tracked experiments.
