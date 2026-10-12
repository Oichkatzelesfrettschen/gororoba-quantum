# Local simulation and precision under a QPU budget

Local computation prepares and compares circuits before a QPU submission.
`local_compute.py` controls Aer execution, records ordered batches, and
rejects unsupported policies. `experiment_optimizer.py` ranks a finite set
of admitted designs by estimated charge or statistical precision. Additional
shots narrow sampling intervals around the hardware outcome distribution;
those intervals can measure hardware bias more precisely without reducing
that bias. CPU or GPU acceleration cannot supply missing physical mechanisms.

## Implemented execution boundary

The enabled policy uses CPU density matrices with double precision. The
CLI accepts `--local-compute cpu`, `--simulation-threads` (default 2), and
`--simulation-memory-mb` (default 512). Aer experiment parallelism is one;
its shot-thread limit equals the declared thread limit. Both
`shot_branching_enable` and `shot_branching_sampling_enable` remain false.
The comparison described below rejects branch sharing from qualification.

`--local-compute gpu` and `--local-compute hybrid` name explicit capability
requests. The runner checks those requests before constructing the IBM
service, writes `state="local_compute_unavailable"` with the policy and
reason, and exits with an error. Even an installed Aer GPU device requires
separate workload and memory qualification before admission. CPU retries
must not replace an explicitly requested GPU or hybrid policy.

Every executed simulation batch records its policy, ordered circuit names,
QPY digest, serialized-noise-channel digest, shots, seed, wall time, and each Aer
experiment's device/method metadata. Family planning retains
`local_simulation_batches`; subsequent evaluation retains
`evaluation_simulation_batches`. The approval policy binds the local
compute settings. Result metadata must identify the admitted CPU device
and density-matrix method. The wall time measures simulator execution
through result retrieval; the field does not measure whole-command time,
CPU time, or peak resident memory.

Qiskit's noise-compilation process pool and Aer's thread pool have separate
limits. Set `QISKIT_NUM_PROCS` together with `GOROROBA_WORKERS` when running
bounded local qualification. `parallel.py` preserves item order using spawned
workers; unrestricted nested pools can oversubscribe the workstation.

## Measured workload and devices

The submit-free folded record
[2026-10-12T011109.792785Z](../results/live/2026-10-12T011109.792785Z/record.json)
records source `55cbe9a5335682406476c4b91392be5c1615f7ca`, two routed
candidates, four shot tiers, and sixteen PUBs across one dynamic and one
static Kingston job. Its selected route gives the following cost/precision
frontier under its retained calibration and nominal cost assumptions:

| Shots per PUB | Estimated total QPU charge, seconds | Worst endpoint half-width | Admission at target 0.08 |
|---:|---:|---:|---|
| 2048 | 13.356002816 | 0.081890106 | Precision fails |
| 4096 | 22.112005632 | 0.057905050 | Feasible; minimum-charge choice |
| 8192 | 39.624011264 | 0.040945053 | Feasible |
| 16384 | 74.648022528 | 0.028952525 | Feasible |

At 16384 shots, the dynamic estimate is 55.354013440 seconds and the static
estimate is 19.294009088 seconds. Each fits a 60-second ceiling. The
combined ceiling is 120 seconds, reserve is 60 seconds, and recorded
remaining quota is 591 seconds. Those historical values establish modeled
admission for that record; future dry runs use fresh calibration and quota.

The separate
[general dry run](../results/live/2026-10-12T011110.481425Z/record.json)
contains 147 member-replica simulation circuits: 54 use three active qubits,
10 use four, and 83 use five. A double-precision density matrix alone takes
`16 * 4**n` bytes, respectively 1, 4, and 16 KiB. Branch states, shot
repetition, noise construction, and batch overhead add costs beyond that
state-size lower bound. A measured workload crossover must justify GPU use.

The [retained inventory](../results/local_compute/GPU_INVENTORY_OBSERVATIONS.json)
is an explicit transcription of local command observations, with versions
and limitations. The inventory separates compute and management interfaces:

| Interface | Observation | Established boundary |
|---|---|---|
| CUDA / CuPy | RTX 4070 Ti, compute capability 8.9; CUDA driver API 13040; CuPy FP64 arithmetic passes NumPy comparison | Small local CUDA computations work |
| Aer 0.17.2 | `available_devices()` returns `["CPU"]` | Installed Aer supplies CPU simulation |
| NVML | Loaded module 615.71.09 and userspace 615.78.08 differ; `nvidia-smi` fails | Management telemetry requires driver reconciliation |
| Torch 2.14.1 | Import raises a deprecated-`pynvml` warning under warnings-as-errors | Torch GPU arithmetic remains unreached |

The CuPy elementwise test over 4096 values has zero maximum absolute error;
the 32 by 32 matrix product has maximum absolute error approximately
`1.07e-14`. The probe records 12513574912 total device bytes and 787808256
free bytes, about 0.73 GiB free at that instant. A new GPU batch needs a
fresh memory reading. Those small probes establish neither Aer GPU parity
nor a speed improvement. Existing GPU processes retain ownership of their
allocations.

The PyPI metadata survey reports `qiskit-aer-gpu` latest version 0.15.1,
with CPython 3.8 through 3.12 wheels; version 0.17.2 returns HTTP 404. The
tested CPU environment uses CPython 3.14.7 and Aer 0.17.2. GPU admission
therefore needs a pinned compatible build and separate qualification. An
older wheel changes the tested numerical contract. Installed kernels with
615.78.08 modules provide a driver-maintenance route through a separately
scheduled matching-kernel boot; the inventory performs zero driver changes.

## Failed CPU branching qualification

The [qualification bundle](../results/local_compute/README.md) retains
compiled QPY, sampled distributions, complete Aer metadata, the
reconstructed serialized noise channels, scripts, provenance, and integrity checks.
FakeFez supplies the archived calibration. Credential service and Sampler
constructors are replaced by failure guards during the local benchmark.

The paired comparison holds density matrices, double precision, two CPU
threads, experiment parallelism one, shot parallelism two, and terminal
sampling disabled. The 2048-shot folded-QPE comparison yields a maximum
labeled-bin difference of `0.404296875` in `qpe_archived_s1`; the simultaneous
compatibility radius is `0.14211860914345206`. The completed qualification
records `state="failed"`. All eighteen compiled noiseless laws pass the
separate sampled exact-oracle check. A successful noiseless check therefore
does not qualify execution with noise. The observed discrepancy establishes
failed compatibility between configurations; the comparison alone does not
identify the incorrect implementation or its internal cause.

The retained follow-up replay creates a fresh simulator for each of ten
2048-shot cases and varies isolated/mixed/reversed batch order and thread
limits. The replay preserves the archived circuit and canonically sorted
serialized channels and produces non-reproduction of the large discrepancy.
The original benchmark reuses simulator objects across warm-ups and shot
tiers. The fresh-instance result leaves history-dependent behavior unresolved
and preserves the failed qualification as the admission boundary.

The broader fifteen-case replay checks every family label and falsifies
fresh-instance construction as a repair. At 32768 shots,
`qpe_no_feed_forward_s3` differs across fresh trials by `0.2327880859375`
against a simultaneous bin bound of `0.036897112495406385`. A second pair
differs by `0.23284912109375`. The reused 2048-shot batch differs from its
retained branch-off baseline by `0.23583984375`, above
`0.14758844998162554`. All count totals and before/after QPY hashes match.
Dynamic members report branching and eligible static members report
measurement sampling. The complete replay therefore adds an independently
observed failure on a second member while the internal cause remains open.
Branch sharing stays disabled.

The initial benchmark is deliberately interrupted during the optional
2048-shot N=21 baseline. Its checkpoint retains `state="running"`; that
field describes an incomplete historical checkpoint. The follow-up report
records the interruption and completes the stated comparisons. The
32768-shot N=21 branch-enabled timing has an unmatched baseline and cannot
establish a speedup. Every timing is a single observation with concurrent
host work uncontrolled, rather than a repeated performance benchmark.

The initial noise hash includes generated quantum-error UUIDs. The follow-up
reconstructs a UUID-free model from the pinned FakeFez fixture and checks two
independent constructions in that process. The error-record list itself
can reorder between processes. The archived legacy digest therefore binds
its exact serialized order; a future semantic comparison must sort complete
channel records while preserving each channel's instruction/probability
ordering. The manifest preserves the original evidence and names that
provenance limitation.

`NoiseModel.to_dict()` omits custom noise passes, including the delay
`RelaxationNoisePass`. The batch field `noise_serialized_channels_sha256`
therefore identifies serialized channels and carries an explicit scope
string. The digest alone cannot replay delay relaxation. The live runner
binds the selected Target/calibration inputs, including T1, T2, and dt;
the archived qualification reconstructs the pass from its pinned FakeFez
fixture and code. The complete delay model needs those inputs together
with the serialized channels and circuits.

## Precision and cost scenarios

`--objective minimum_charge` remains the default. The objective minimizes
the largest estimated charge over nominal inputs and the explicitly supplied
cost scenarios, after every statistical and budget constraint passes.
Without extra scenarios, the objective uses the nominal estimate.

`--objective precision_at_budget` accepts precision-only contracts. The
family CLI restricts that objective to folded QPE. The optimizer minimizes
`max(endpoint.confidence_half_width / endpoint.precision_half_width)`, then
worst-case estimated charge, then candidate name. Every endpoint retains
its own scientific precision target. The finite candidate table and Pareto
frontier remain visible; the selected score establishes a bounded design
choice rather than a global optimum or hardware accuracy.

Each repeatable `--cost-scenario NAME:OVERHEAD_SECONDS:LATENCY_US` adds a
cost-sensitivity assumption. Every declared scenario passes the same
per-job ceiling, invocation ceiling, and reserve gates. Sequential
feed-forward stage counts determine the latency contribution. The record
retains nominal and worst-case costs, scenario identities, and rejection
reasons. A scenario set has explicit finite coverage, without a statistical
confidence claim about unknown hardware costs.

For the historical frontier above, nominal precision ranking favors 16384
shots. An illustrative scenario with overhead 4.6 seconds and latency 60
microseconds per stage raises that candidate's dynamic estimate to
60.275453440 seconds, above its 60-second ceiling. The 8192-shot dynamic and
static estimates are 32.437726720 and 13.097004544 seconds under that scenario.
Requiring nominal and those stress inputs favors 8192 among the retained
tiers. Those calculations replay historical cost inputs; a fresh command
can select a different route or reject the design.

Run the following submit-free command from the repository root to plan the
precision objective with an explicit finite cost scenario:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  export QISKIT_NUM_PROCS=2 GOROROBA_WORKERS=1
  export PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1
  cd gororoba_quantum
  "$PYTHON" live_run.py --family folded-qpe --optimize \
    --objective precision_at_budget --cost-scenario overhead_latency:4.6:60 \
    --local-compute cpu --simulation-threads 2 --simulation-memory-mb 512 \
    --backends ibm_kingston --seeds 2 --optimizer-candidates 2 \
    --shot-tiers 2048,4096,8192,16384 --model-shots 32768 \
    --max-execution-seconds 60 --max-total-execution-seconds 120 \
    --reserve-seconds 60 --out ../results/live
)
```

The command reads backend metadata and performs local work. The command
submits zero QPU jobs. An admitted record produces an unapproved written
case. Owner approval, the record digest, exact QPY, fresh calibration,
execution-cost binding, and single-use approval remain mandatory for a
separate submission. A changed compute policy or objective needs a fresh
case even when the selected QPY bytes match an earlier archive.

## Delay/reset identifiability and independent sentinels

The folded delay control applies local relaxation immediately before reset
on the same control qubit. A local trace-preserving channel leaves the work
register's reduced state invariant:

```text
Tr_control[(E_control tensor Identity_work)(rho)] = Tr_control(rho)
Reset_control[(E_control tensor Identity_work)(rho)]
    = |0><0|_control tensor Tr_control(rho)
```

For Kraus operators `K_j`, cyclicity of the partial trace and
`sum_j K_j^dagger K_j = I` prove the first identity. Reset prepares its fixed
control state and discards the former control, proving the second identity.
The identities hold even when control and work start entangled. They assume
the delay channel acts only on the reset control, preserves trace, and
supplies no retained environment record; reset is unconditional. Work-qubit
idle noise, correlated cross-talk, scheduler effects, and hardware reset
error lie beyond that channel identity.

Consequently, matching all family distributions cannot validate the delay
noise implementation: omitting local relaxation before that reset can leave
the same outputs. The observation applies a standard quantum-channel
identity to the qualification design; it establishes no new topology or
quantum-information theorem.

Future deterministic-density or GPU qualification includes independent
`|1> -> delay(t) -> measure` T1 sentinels and
`H -> delay(t) -> H -> measure` Ramsey T2 sentinels. With zero-temperature
relaxation, ideal preparation/readout, and zero detuning, their laws are
`P_T1(1) = exp(-t/T1)` and `P_Ramsey(0) = (1 + exp(-t/T2))/2`.
Finite-temperature T1 checks use
`P(1,t) = p_equilibrium + (P(1,0) - p_equilibrium) * exp(-t/T1)`.
The probes bind physical-qubit identity, delay units, dt, T1, T2, equilibrium
population, and the materialized relaxation channel. Isolated channel
checks disable unrelated SPAM noise or propagate its declared channels
explicitly. The channel uses `T2 <= 2*T1`, or records Aer's effective T2
when the model adjusts it. Checks include zero delay, several positive
dt-derived delays, omitted-delay mutations, and wrong-dt mutations.
Deterministic probabilities use a declared numerical tolerance; sampled
comparisons retain finite-shot bounds. Those sentinels expose omitted delay
noise that the family alone cannot identify.

A separate deterministic noisy-density evaluator remains under qualification.
The active planner samples Aer on the admitted CPU policy. The deterministic
design propagates unnormalized density matrices indexed by reported
classical memory and sums branches with identical memory by linearity.
Qualification covers measurement quantum noise, asymmetric readout,
reported-bit feed-forward, reset noise, physical-wire mapping, delay passes,
and trace/positivity/probability residuals. Passing those gates can remove
Monte Carlo prediction uncertainty; floating-point error and hardware-model
discrepancy remain separate residuals. The optimizer/evidence integration
retains its own review boundary while evaluator qualification proceeds.

## Remaining acceleration gates

1. Isolate the noisy branching discrepancy using retained inputs: individual,
   mixed, and reversed batches; one and multiple threads; noise-channel
   decomposition; seed and shot-count sweeps. The gate retains failures and
   admits only a configuration whose scientific distributions pass.
2. Qualify a pinned Aer GPU build compatible with the tested Python/Qiskit
   environment. Require actual GPU result metadata for measurement, reset,
   conditional branches, gate noise, readout noise, independent T1/T2 delay
   sentinels, and mixed one-bit/two-bit batches. Keep density matrices and double precision fixed.
3. Establish sampled compatibility and numerical equivalence separately.
   For `K` bins and two independent-within-run `N`-shot estimates, use
   `epsilon = sqrt(log(4*K/delta)/(2*N))`; the simultaneous difference
   threshold is `2*epsilon`. Cross-device independence is unnecessary for
   the union/triangle argument. Include every device, tier, and repetition
   in the comparison count. Equivalence within margin `tau` requires
   `abs(observed_difference) + 2*epsilon <= tau`, or a deterministic
   probability oracle with a declared numerical tolerance.
4. Measure cold and warm end-to-end time, CPU time, peak host memory, and
   CUDA free memory. Use a separate warm-up and at least three measured
   repetitions, including serialization and transfers. A predeclared
   material improvement, such as 10 percent, supplies an engineering
   acceptance criterion. Report local preparation cost separately from
   IBM charged QPU seconds.
5. Admit GPU batching only with live memory headroom and workload parity.
   Density-state size underestimates concurrent branch/workspace allocation.
   A proposed initial headroom rule uses the smaller of an explicit cap and
   half the live free-memory reading. Test allocation failure and reduced
   caps. `batched_shots_gpu` and `cuStateVec_enable` have incompatible Aer
   option combinations and require separate qualification.
6. Admit hybrid scheduling only after the GPU path passes. Freeze workload
   assignment using circuit width, dynamic-operation count, shots, and batch
   size before observing sampled outcomes. Reserve separate CPU budgets and
   record ordered device assignments. Device failure rejects the policy.

A faster simulator can expand a declared finite search, but its statistical
comparison allowance must expand with that search. Adaptive simulation-shot
allocation needs an explicit total error budget or an independent
confirmation batch for a frozen selection. Extra model shots can reduce
finite-simulation uncertainty in the N=21 directional effect; they cannot
reduce unmodeled hardware error. A small declared sensitivity grid can test
readout, gate, T1/T2, latency, and overhead assumptions, with measured ranges
and unmeasured stress assumptions labeled separately.

Tighter replica precision needs a valid upper bound on complete same-shot
score covariance, including cross-member terms and selection uncertainty,
or a justified direct bound on the complete score. A positive-semidefinite
sample covariance alone supplies neither a population upper bound nor
independence. Hardware observations used to train a layout or noise model
need independent validation for prediction-quality claims.

## Primary references

- [AerSimulator API](https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html):
  device/method support, precision, parallelism, GPU batching, branching, and
  random-number changes in terminal sampling. Installed Aer 0.17.2 source
  supplies the tested option contracts.
- Aer 0.17.2 [delay-pass installation](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/qiskit_aer/noise/noise_model.py#L429-L449),
  [channel serialization](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/qiskit_aer/noise/noise_model.py#L921-L963),
  [delay units and relaxation](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/qiskit_aer/noise/passes/relaxation_noise_pass.py#L64-L126),
  and [custom-pass execution](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/qiskit_aer/backends/aerbackend.py#L548-L565)
  ground the serialized-channel boundary and independent delay sentinels.
- [Qiskit Aer source](https://github.com/Qiskit/qiskit-aer) and
  [GPU package metadata](https://pypi.org/pypi/qiskit-aer-gpu/json): build and
  interpreter compatibility require version-specific verification.
- [Qiskit multiprocessing source](https://github.com/Qiskit/qiskit/blob/main/qiskit/utils/parallel.py):
  `QISKIT_NUM_PROCS` controls Qiskit's separate process pool.
- [CUDA memory API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__MEMORY.html)
  and [NVML API](https://docs.nvidia.com/deploy/nvml-api/index.html): compute
  memory queries and management telemetry use separate interfaces.
- [IBM runtime estimation](https://quantum.cloud.ibm.com/docs/guides/estimate-job-run-time),
  [execution options](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/options-models-execution-options),
  and [maximum execution time](https://quantum.cloud.ibm.com/docs/guides/max-execution-time):
  circuit duration, repetition settings, and service ceilings govern QPU cost.
- [Hoeffding 1963, Theorem 2](https://doi.org/10.1080/01621459.1963.10500830):
  bounded independent repetitions support the stated finite-comparison
  allowances; the theorem supplies no hardware-model guarantee.
