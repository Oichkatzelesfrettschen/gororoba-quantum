# Step 3 written case: dynamic job on ibm_kingston

- Source commit: `c82d5e89321398fb574db80d1ed62e0d3b1a2be0` (sources_modified=false). Record `2026-10-11T121402.617901Z`, SHA-256 `807f1856b54abc7aaec1a311a999d0c6f8fd197ccf385488bc153531432c447b`; QPY SHA-256 `69f085f5319a19578aff823ec30d98c0029b83de156d515f909bd53fe6413a24`.
- Experiment digest: `0d5e840440fe89cc51053f848f5a2ecddc8e3532cb83362389f20c5e843c40f2`.
- Instance: recorded at submission as the 12-hex sha256 of the CRN in each planned job's budget_before; a dry run records none.
- Calibration: 2026-10-11T03:48:01-07:00 fetched 2026-10-11T12:14:04+00:00; excluded qubits 9, excluded CZ edges 24.
- PUBs (6, all dynamic, 4096 shots each, 24576 submitted PUB shots):
  - `ibm_kingston_dynamic_pub_01`: streams 9, stages 1, Target bound 3334 dt; folded_qpe_mod15:folded_qpe_s1, hybrid_shor_mod15:hybrid_shor_N15_a2
  - `ibm_kingston_dynamic_pub_02`: streams 2, stages 1, Target bound 3295 dt; folded_qpe_mod15:folded_qpe_s1_isolated, hybrid_shor_mod15:hybrid_shor_N15_a2_isolated
  - `ibm_kingston_dynamic_pub_03`: streams 9, stages 1, Target bound 3334 dt; folded_qpe_mod15:folded_qpe_s0, hybrid_shor_mod15:hybrid_shor_N15_a2_null
  - `ibm_kingston_dynamic_pub_04`: streams 3, stages 1, Target bound 3334 dt; folded_qpe_mod15:folded_qpe_s2
  - `ibm_kingston_dynamic_pub_05`: streams 3, stages 1, Target bound 3334 dt; folded_qpe_mod15:folded_qpe_s3
  - `ibm_kingston_dynamic_pub_06`: streams 3, stages 1, Target bound 1659 dt; folded_qpe_mod15:folded_qpe_null
- folded_qpe_mod15: backend ibm_kingston, seed 20261012, layout [153, 152, 151, 138, 150], replicas 3, joint score 0.6693
  - noise-model packing comparison: scope global, verdict equivalent_within_0.03, 95% interval [-0.020131142358006608, 0.007431616779095278]
- hybrid_shor_mod15: backend ibm_kingston, seed 20261010, layout [59, 54, 74, 55, 75], replicas 6, joint score 0.7225
  - noise-model packing comparison: scope global, verdict equivalent_within_0.03, 95% interval [-0.029867520601405344, 0.01376500005896722]
- Hybrid Shor admission (noise model), complete:

```json
{
  "factorable_probability": {
    "admitted": true,
    "identity_null": {
      "hi": 0.01055750046058344,
      "lo": 0.0002660672477498944,
      "mean": 0.005411783854166667,
      "method": "student_t_over_6_replicas_union_wilson_over_24576_shots"
    },
    "primary": {
      "hi": 0.5043658473202968,
      "lo": 0.4851361058047032,
      "mean": 0.4947509765625,
      "method": "student_t_over_6_replicas_union_wilson_over_24576_shots"
    },
    "uniform_null": 0.296875
  },
  "order_recovery_probability": {
    "admitted": true,
    "identity_null": {
      "hi": 0.01055750046058344,
      "lo": 0.0002660672477498944,
      "mean": 0.005411783854166667,
      "method": "student_t_over_6_replicas_union_wilson_over_24576_shots"
    },
    "primary": {
      "hi": 0.5043658473202968,
      "lo": 0.4851361058047032,
      "mean": 0.4947509765625,
      "method": "student_t_over_6_replicas_union_wilson_over_24576_shots"
    },
    "uniform_null": 0.296875
  }
}
```

- Requested scheduler fields: execution.scheduler_timing=True on the job; per PUB scheduled_circuit_duration_dt, scheduler_residual_dt against the execution-time Target, parallel/sequential stream counts; per job qpu_charge_time_seconds and pub_shots_per_qpu_second.
- Expected QPU seconds: 24576 PUB shots at the literature bounds of 1,000 to 4,900 shots/s give 5.0 to 24.6 s plus job overhead; the measured rate replaces this for the dynamic workload only.
- Why the noise simulation cannot answer the questions this run asks:
  - Hybrid-Shor admission: the simulated admission above comes from a
    Target-derived Aer noise model whose channels are independent per qubit
    and per gate; it carries no crosstalk, no mid-circuit measurement
    back-action on neighbors, no classical feed-forward latency, and no drift,
    and it is built from the same calibration snapshot it is judged against.
    Whether the factor yield's lower bound clears the uniform null on the
    device is a property of the device.
  - Packing equivalence: the simulation sets every cross-replica interaction
    to zero by construction, so its packed-versus-reference verdict is the
    statistic's null behavior, never evidence about packing cost; only shots
    from co-scheduled replicas on hardware test it.
  - Scheduler residuals: the Target omits classical feed-forward, alignment,
    measurement, and reset scheduling, so the residual is undefined in
    simulation; only the backend scheduler's circuit_duration on a submitted
    job supplies it.
  - Throughput: QPU charge per submitted PUB shot is a service quantity that
    exists only for an executed job.
- Failure and recollection: a failed or cancelled job is retained with its charge and no throughput; a pending usage is polled for 120 s and otherwise left pending with a reason; any resubmission needs a new case.

## Exact command

Run from a clean checkout at the source commit above, in gororoba_quantum/,
after the owner approves this case:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" live_run.py \
  --backends ibm_kingston \
  --groups folded_qpe_mod15,hybrid_shor_mod15 \
  --seeds 8 \
  --max-pending 25 \
  --shots 4096 \
  --isolated-reference \
  --min-remaining-seconds 60 \
  --out ../results/live \
  --submit
```

The run re-reads the live calibration, recompiles, and stops before Sampler
construction with an approval_required record if the backend, calibration,
exclusions, layouts, replicas, capabilities, experiment digest, or QPY differ
from this case. This case authorizes nothing by itself; the static job
(57,344 submitted PUB shots) and the feed-forward timing ladder each need a
case of their own.
