# Unapproved QPU case: folded-correction

Status: UNAPPROVED. The saved record describes a feasible submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.

The selected bounded-search candidate is `ibm_fez-seed-20261014-shots-8192` at 8192 shots per PUB. Global optimality remains outside the claim.

## Artifact and source binding

- Saved run: `results/live/2026-10-12T163354.247043Z`.
- [record.json](record.json) SHA-256: `0ee3146cccce74abdd580380cca3d684106036d4fdc27bdc2bb4ccf340991a8a`.
- [isa.qpy](isa.qpy) SHA-256: `51db305d47a0cff4664e1135390ee1cd807bde2cc105439669ea795108bd83b4`.
- Experiment source digest: `38487fe3aecb92eb237ef0c803d11df35198bbaec829a770b513b603a9a711fe`.
- Source commit: `f1b9830ac5ff76c7d3fdeeffab69abf9aa2f28ed`; sources_modified=`false`.
- Simulator seed: `20261011`; the source digest binds the simulator implementation.

Recorded dependency versions:

| Dependency | Version |
|---|---|
| numpy | 2.5.4 |
| qiskit | 2.5.2 |
| qiskit-aer | 0.17.2 |
| qiskit-ibm-runtime | 0.50.0 |
| rustworkx | 0.18.1 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |

## Scientific question and interpretation

The pilot compares measured-bit correction F with recorded-bit-independent correction U for the known odd eigenstate labels s1 and s3. One routed symbolic template produces four PUBs in order F1/U1/U3/F3, one replica, one dynamic job, and 8192 shots per PUB. Every arm retains the classical dispatch, first measurement, reset, physical history, and terminal readout. U applies -pi/2 in both dispatch branches; F applies -pi/2 only when the recorded first bit equals 1. The archived circuit pair proof permits only the false-branch phase and associated global-phase difference.

The experiment tests dependence of the correction on the recorded first bit for supplied labels. Classical dispatch removal, general unknown-eigenstate QPE, and unique attribution to a controller or readout mechanism remain outside its scope. The fixed arm order can retain time and drift confounds.

Fresh Target/properties supply placement and conditional noise predictions. A future hardware acquisition measures the terminal-success contrast and model residual. Raw shot order, all classical registers, actual returned schedules, calibration windows, and completed usage must be retained before the scientific decision.

## Archived ideal laws and placement

The ideal arrays below come from the retained record. Their label order stays intact; sorting probabilities would discard the specified outcome labels.

| Member | Labeled ideal probabilities |
|---|---|
| correction_measured_s1 | `[0.0, 1.0, 0.0, 0.0]` |
| correction_known_s1 | `[0.0, 1.0, 0.0, 0.0]` |
| correction_known_s3 | `[0.0, 0.0, 0.0, 1.0]` |
| correction_measured_s3 | `[0.0, 0.0, 0.0, 1.0]` |

| Group | Backend | Calibration | Transpiler seed | Initial layout |
|---|---|---|---:|---|
| folded_correction | ibm_fez | 2026-10-12T08:24:52-07:00 | 20261014 | `[24, 23, 16, 22, 3]` |

Calibration-bound family and replica mapping:

```json
{
  "replica_cap": 1,
  "shared_initial_layout": [
    24,
    23,
    16,
    22,
    3
  ],
  "dt_seconds": 4e-09,
  "group_replica_mappings": {
    "folded_correction": [
      {
        "3": 3,
        "16": 16,
        "22": 22,
        "23": 23,
        "24": 24
      }
    ]
  }
}
```

## Preregistered endpoints

The primary estimand is unconditional terminal-bit success, using every raw shot. Outcome labels are y = first_bit + 2*terminal_bit. Success is terminal_bit=0 for s1 and terminal_bit=1 for s3. Each F and U arm must supply exactly 8192 integer-count observations; missing members or shots withhold the scientific decision.

Four one-sided Clopper-Pearson bounds allocate family alpha=0.05 as 0.0125 per bound. Select U only when both labels satisfy `lower_U - upper_F > 0.01` and the post-execution circuit, schedule, count, and calibration checks qualify. Failure retains F and establishes neither equivalence nor a causal mechanism. Recorded B=0/B=1 strata remain descriptive; the decision uses zero conditional postselection.

The observation bounds allow arbitrary dependence between PUBs through a union bound. Independent stationary Bernoulli repetitions within each PUB remain an assumption. Exact-binomial describes the interval construction; SciPy evaluates quantiles and tails in floating point without interval-certified rounding.

### Hypothetical sensitivity scenario

The fixed reference F rates are 6433/8192 for s1 and 6241/8192 for s3. A hypothetical U improvement of 0.04 gives the joint-power lower bound 0.880600784412 against the required 0.8. The finite-binomial sum adds independence between F and U counts within each label; the union bound across labels requires no independence between labels. The reference rates are scenario constants, with no stationarity or transfer claim to fresh calibration. Hypothetical power supplies neither a current model prediction nor measured advantage.

### Frozen calibration-model predictions

The selected layout uses 32768 finite simulation shots per member and seed 20261011. The four labeled distributions and gains are frozen before hardware acquisition. Controller and instrument errors remain incomplete in the model; sampling error and hardware-model discrepancy remain separate from the hypothetical sensitivity calculation.

| Member | Labeled modeled probabilities | Terminal success |
|---|---|---:|
| correction_measured_s1 | `[0.029022216796875, 0.87274169921875, 0.0247802734375, 0.073455810546875]` | 0.901763916016 |
| correction_known_s1 | `[0.030242919921875, 0.872589111328125, 0.02325439453125, 0.07391357421875]` | 0.90283203125 |
| correction_known_s3 | `[0.02423095703125, 0.076904296875, 0.02911376953125, 0.8697509765625]` | 0.898864746094 |
| correction_measured_s3 | `[0.03009033203125, 0.076934814453125, 0.024322509765625, 0.86865234375]` | 0.892974853516 |

| Label | Modeled U minus F |
|---|---:|
| s1 | 0.00106811523438 |
| s3 | 0.00588989257812 |

The modeled gains may be small or negative; the hypothetical 0.04 gain stays separately labeled.

## Selection objective and sensitivity assumptions

The dedicated correction objective maximizes the weakest of four calibrated arm scores (ESP times exp(-T*sum(1/T2))). Ties use lower Target-plus-repetition charge with zero added controller latency, then total CZ count, seed, and backend name. The generic objective flag remains recorded for CLI replay; the dedicated family ranker defines selection. Calibration proxies establish neither measured fidelity nor global optimality.

The selected candidate's worst-arm quality proxy is 0.588330635301. The finite search includes fresh snapshots of Fez, Kingston, and Marrakesh; every recorded rejection stays in the retained search trace.

| Backend | Calibration | Family eligible | Compiled candidates | Admitted candidates |
|---|---|---|---:|---:|
| ibm_fez | 2026-10-12T08:24:52-07:00 | true | 6 | 6 |
| ibm_kingston | 2026-10-12T07:55:47-07:00 | true | 6 | 6 |
| ibm_marrakesh | 2026-10-12T09:04:44-07:00 | true | 6 | 6 |

Every listed cost scenario passes the same per-job and aggregate ceilings. Scenario values are explicit assumptions, with no claimed confidence coverage.

| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |
|---|---:|---:|---:|
| controller-stress | 4.6 | 40 | 14.474571264 |

The largest nominal/scenario charge is 14.474571264 seconds. The complete scenario PUB ledgers remain in record.json.

## Expected charge and service ceilings

| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |
|---|---:|---:|---:|---:|
| ibm_fez/dynamic/1 | 4 | 32768 | 11.519211264 | 30 |

The cost model predicts 11.519211264 seconds. The per-job service ceilings sum to 30 seconds against an invocation cap of 30 seconds. The global reserve is 60 seconds; the saved quota reports 551 seconds remaining.

Every PUB cost includes its Target duration, explicit repetition delay, and declared reset/classical-latency additions. Each job also includes its declared fixed overhead. Those model assumptions estimate charge; the ceilings bound service execution instead. The ledger retains accepted and attempted jobs' reservations while their charges remain unsettled. External submissions can still change the shared quota. Dynamic Target duration omits classical scheduler latency; the declared addition remains a planning assumption. Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost remains unseparated unless a native server timing artifact qualifies that accounting boundary.

| PUB | Shots | Target duration (s) | Repetition delay (s) | Reset addition (s) | Classical latency addition (s) |
|---|---:|---:|---:|---:|---:|
| ibm_fez_dynamic_pub_01 | 8192 | 1.1348e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_02 | 8192 | 1.1348e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_03 | 8192 | 1.1348e-05 | 0.00025 | 0 | 2e-05 |
| ibm_fez_dynamic_pub_04 | 8192 | 1.1348e-05 | 0.00025 | 0 | 2e-05 |

Job `ibm_fez/dynamic/1` adds 2.3 seconds of modeled overhead.

## Post-execution schedule qualification

The authorized preparation route skips unavailable native mock scheduling. Fresh Target timing and explicit overhead/controller-latency scenarios supply local planning estimates. The actual native schedule remains unknown before execution; the estimate supplies neither native timing proof nor a final-charge guarantee.

Returned scheduler tables must qualify each archived F/U pair's exposed protected events, measurement/reset/dispatch history, correction slot, and timing. Circuit validation supplies phase and condition semantics omitted by the timing table. Missing or mismatched tables, incomplete counts, or ambiguous calibration withhold the CP scientific decision while retaining raw and descriptive results. Exposed schedule agreement leaves undisclosed controller behavior and per-shot timing uncertified.

The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace each job's execution ceiling. Actual charge comes from completed job usage.

## Reproduce the dry run

Run from the repository root with the recorded dependency versions and source digest. The command pins every backend in the saved discovery inventory, preserving the known candidate universe. The runner refreshes calibration and queue admission, so a changed backend can produce a different case. The transpiler seed count and simulator seed retain their recorded meanings.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family folded-correction \
  --shot-allocation uniform \
  --objective minimum_charge \
  --cost-scenario controller-stress:4.6:40.0 \
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 8192 \
  --seeds 6 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 30.0 \
  --out ../results/live
```

## Approval-only submission template

Execute the following command only after the owner explicitly approves this concrete case and its ceilings. Keep the complete saved run at the repository-relative location above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence with the approved record, consumes its approval once, and stops for renewed approval when the comparison changes.

```sh
cd gororoba_quantum
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" live_run.py \
  --family folded-correction \
  --shot-allocation uniform \
  --objective minimum_charge \
  --cost-scenario controller-stress:4.6:40.0 \
  --local-compute cpu \
  --simulation-threads 2 \
  --simulation-memory-mb 512 \
  --backends ibm_fez,ibm_kingston,ibm_marrakesh \
  --shots 8192 \
  --seeds 6 \
  --max-pending 25 \
  --min-remaining-seconds 60.0 \
  --max-execution-seconds 30 \
  --max-replicas 1 \
  --no-isolated-reference \
  --cross-group-buffer \
  --shot-tiers 8192 \
  --replica-tiers 1 \
  --optimizer-candidates 6 \
  --model-shots 32768 \
  --precision 0.08 \
  --alpha 0.05 \
  --power 0.8 \
  --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 \
  --classical-latency-us 20.0 \
  --reserve-seconds 60.0 \
  --max-total-execution-seconds 30.0 \
  --out ../results/live \
  --approved-record ../results/live/2026-10-12T163354.247043Z \
  --approved-record-sha256 0ee3146cccce74abdd580380cca3d684106036d4fdc27bdc2bb4ccf340991a8a \
  --submit
```
