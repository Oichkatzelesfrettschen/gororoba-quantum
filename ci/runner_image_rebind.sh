#!/bin/sh
# Rewrite every record that ci/runner_image_records.json binds, in the runner image, then bind them with one `add`.
#   PYTHON=/path/to/pin-venv/bin/python sh ci/runner_image_rebind.sh
# Run from the repository root. Each producer below is the write form of the command that a gate in ci/gates.json
# verifies with --check, --replay or `| cmp -`; `ci/runner_image_records.py write` runs it through ci/runner_image.sh
# (podman) over a snapshot of the tree and receipts each file it wrote. The Qiskit campaign of
# docs/evidence/quantum-experiment-conformance records its Qiskit version, so a new pin writes a successor directory
# beside the earlier one, and the successor's rows replace the earlier directory's rows in the ledger.
set -eu

: "${PYTHON:?set PYTHON to the interpreter of the pin venv}"
export PYTHON

records=ci/runner_image_records.py
ledger=ci/runner_image_records.json
conformance=docs/evidence/quantum-experiment-conformance
retired=$conformance/runner-scalar-operators-qiskit-2-6-1
successor=$conformance/runner-scalar-operators-qiskit-2-6-2

for path in "$records" "$ledger"; do
    [ -f "$path" ] || {
        echo "runner_image_rebind: run from the repository root; $path is missing" >&2
        exit 2
    }
done

list=$(mktemp)
trap 'rm -f "$list"' EXIT

# bind NAME COMMAND: write the records of one gate's producer in the runner image.
bind() {
    echo "runner_image_rebind: $1" >&2
    "$PYTHON" "$records" write sh -c "$2"
}

bind core-017 'PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error results/live/folded_raw_analysis.py results/live/2026-10-12T055624.091217Z > results/live/2026-10-12T055624.091217Z/supplemental-shot-order.json'

# core-026 and core-051 replay the same page.
bind core-026-051 '"$PYTHON" -B -W error scripts/render_ripple_visualization.py --evidence results/ripple/evidence.json --out results/ripple/cayley-dickson-ripples.html'

# The measured-ripple renderer refuses an existing output, so the snapshot's copy leaves first.
bind core-207 'rm -f results/ripple/measured-cayley-dickson-ripples.html && "$PYTHON" -B -W error scripts/render_measured_ripple.py --evidence results/ripple/measured-ripple.json --evidence results/ripple/measured-rank-sector.json --out results/ripple/measured-cayley-dickson-ripples.html'

bind core-617 '"$PYTHON" -B -W error scripts/n21_q143_line_switching.py results/live/2026-10-21T064222.721454Z results/live/2026-10-21T064222.721454Z/segmented-sweep-759d82d74c57.json --out results/live/2026-10-21T064222.721454Z/line-switching-759d82d74c57.json'

bind sources-240 '"$PYTHON" -I -W error docs/evidence/reviewer_associator_audit/audit.py > docs/evidence/reviewer_associator_audit/audit_results.json'

bind core-287 '"$PYTHON" -B -W error scripts/ghost_run.py --report docs/evidence/ghost_runs/result.json > docs/evidence/ghost_runs/report.json'

bind core-338 'k=results/kaggle; o=output/output/repo/results/kaggle_out; "$PYTHON" -B -W error scripts/linear_conjugation_search.py --merge $k/2026-10-16T215953Z-gororoba-linear-conjugation-shard-0/$o/linear_conjugation_shard_0.json $k/2026-10-16T215956Z-gororoba-linear-conjugation-shard-1/$o/linear_conjugation_shard_1.json $k/2026-10-16T215959Z-gororoba-linear-conjugation-shard-2/$o/linear_conjugation_shard_2.json $k/2026-10-16T221042Z-gororoba-linear-conjugation-shard-3/$o/linear_conjugation_shard_3.json $k/2026-10-16T221044Z-gororoba-linear-conjugation-shard-4/$o/linear_conjugation_shard_4.json --out docs/evidence/linear_conjugation/search.json > /dev/null && "$PYTHON" -B -W error scripts/n21_conjugation_noise.py --merge $k/2026-10-16T223545Z-gororoba-n21-encoded-noise-kingston/$o/n21_conjugation_noise_kingston.json $k/2026-10-16T223549Z-gororoba-n21-encoded-noise-fez/$o/n21_conjugation_noise_fez.json $k/2026-10-16T223552Z-gororoba-n21-encoded-noise-marrakesh/$o/n21_conjugation_noise_marrakesh.json --out docs/evidence/linear_conjugation/noise.json'

bind core-639 '"$PYTHON" -B -W error scripts/iqm_jobs.py analyze results/iqm/runs/2026-10-22T212227Z-garnet_mock-reset-billing-pilot-p-2x2000-passive results/iqm/runs/2026-10-22T212237Z-garnet_mock-reset-billing-pilot-a-2x2000-active1 results/iqm/runs/2026-10-22T212723Z-garnet-reset-billing-pilot-p-2x2000-passive results/iqm/runs/2026-10-22T212742Z-garnet-reset-billing-pilot-a-2x2000-active1 --out results/iqm/reset_billing_pilot_analysis.json'

bind core-637 '"$PYTHON" -B -W error scripts/iqm_signed_probe.py analyze results/iqm/runs/2026-10-23T003708Z-garnet-signed-kernel-probe-strong results/iqm/runs/2026-10-23T003738Z-garnet-signed-kernel-probe-weak --out results/iqm/signed_kernel_probe_analysis.json'

bind core-641 '"$PYTHON" -B -W error scripts/iqm_cancellation_probe.py analyze results/iqm/runs/2026-10-23T073147Z-garnet-kernel-cancellation-probe-cancellation --out results/iqm/kernel_cancellation_probe_analysis-runner-image.json'

bind core-684 '"$PYTHON" -B -W error scripts/iqm_idle_schedule_probe.py analyze results/iqm/runs/2026-10-25T003916Z-garnet-idle-schedule-train-readout-probe --out results/iqm/idle_schedule_probe_analysis-runner-image.json'

bind core-643 '"$PYTHON" -B -W error scripts/iqm_signed_resolve.py analyze results/iqm/runs/2026-10-23T073222Z-garnet-signed-kernel-null-retest-probe-0 results/iqm/runs/2026-10-23T073227Z-garnet-signed-kernel-null-retest-calibrate --out results/iqm/signed_kernel_null_retest_analysis.json'

bind core-645 'r=results/quantum_inspire/runs/2026-10-23T; "$PYTHON" -B -W error scripts/qi_cancellation_cases.py --analyze ${r}075103Z-kernel_cancellation_qx-batch-00 ${r}075235Z-kernel_cancellation_qx-batch-01 ${r}075308Z-kernel_cancellation_qx-batch-02 ${r}075342Z-kernel_cancellation_qx-batch-03 ${r}075417Z-kernel_cancellation_qx-batch-04 ${r}075450Z-kernel_cancellation_qx-batch-05 --out results/quantum_inspire/kernel_cancellation_qx_analysis.json && "$PYTHON" -B -W error scripts/qi_cancellation_cases.py --analyze ${r}075543Z-kernel_cancellation_tuna_17-batch-00 ${r}080006Z-kernel_cancellation_tuna_17-batch-01 ${r}080624Z-kernel_cancellation_tuna_17-batch-02 ${r}081101Z-kernel_cancellation_tuna_17-batch-03 ${r}081536Z-kernel_cancellation_tuna_17-batch-04 ${r}082011Z-kernel_cancellation_tuna_17-batch-05 --out results/quantum_inspire/kernel_cancellation_tuna_17_analysis.json'

bind core-647 '"$PYTHON" -B -W error scripts/bdsc_diagnostic.py --readout results/quandela/runs/2026-10-22T160023Z-qpu_belenos-bdsc_diagnostic-b1-j1 results/quandela/runs/2026-10-22T160340Z-qpu_belenos-bdsc_diagnostic-b1-j2 results/quandela/runs/2026-10-23T073329Z-qpu_belenos-bdsc_diagnostic-b2-j1 results/quandela/runs/2026-10-23T081314Z-qpu_belenos-bdsc_diagnostic-b2-j2 > results/quandela/bdsc_diagnostic_readout-runner-image.json'

# The producer's own `--out` rewrites the ascella and belenos campaigns too, whose angle files hold the frozen bytes the
# gate verifies by digest, so the write calls the four readiness and frontier builders that the ledger binds.
bind core-650 '"$PYTHON" -B -W error - <<"PY"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
import hypercomplex_photonic_cases as photonic

out = Path("results/hypercomplex/photonic-successors")
processor = json.loads((out / "native-target-catalogue.json").read_text())["processors"]["qpu:ascella"]
photonic.write_files(out / "ascella-readiness", photonic.readiness_case())
frontier = {"frontier.json": json.dumps(photonic.characterization_frontier(), indent=1) + "\n"}
photonic.write_files(out / "ascella-capability-frontier", frontier)
photonic.write_files(out / "ascella-native-readiness", photonic.native_readiness_case(processor))
photonic.write_files(out / "ascella-full-source-readiness", photonic.native_readiness_case(processor, all_sources=True))
PY'

bind core-ascella-signed-coherence-acquisition-replay '"$PYTHON" -B -W error scripts/ascella_coherence_run.py --run results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00 --out results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/analysis-runner-image.json'

bind core-667 '"$PYTHON" -B -W error scripts/bdsc_stray_mode_veto.py --write --out results/quandela/bdsc_stray_mode_veto-runner-image.json'

bind core-675 's=results/quandela/runs/2026-10-23T; "$PYTHON" -B -W error scripts/bdsc_stationarity.py --write > /dev/null && "$PYTHON" -B -W error scripts/bdsc_stationarity.py --readout ${s}201808Z-qpu_belenos-bdsc_stationarity-b1-j1-repeat ${s}202212Z-qpu_belenos-bdsc_stationarity-b1-j2 ${s}213050Z-qpu_belenos-bdsc_stationarity-b2-j1 ${s}213450Z-qpu_belenos-bdsc_stationarity-b2-j2 > results/quandela/bdsc_stationarity_readout_pinned.json && "$PYTHON" -B -W error scripts/bdsc_stationarity.py --calibration-contrast ${s}195000Z-qpu_belenos-bdsc_stationarity-b1-j1 ${s}201808Z-qpu_belenos-bdsc_stationarity-b1-j1-repeat > results/quandela/bdsc_stationarity_calibration_contrast_pinned.json'

bind core-679 '"$PYTHON" -B -W error scripts/bdsc_drift_series.py --write > /dev/null && "$PYTHON" -B -W error scripts/bdsc_drift_series.py --write-diagnostic > /dev/null'

bind core-688 'cd gororoba_quantum && "$PYTHON" -B -W error primorial_cover.py --out ../docs/evidence/primorial_cover/certificates.json'

bind core-ibm-fez-actor-pilot-replay 'OPENBLAS_NUM_THREADS=1 "$PYTHON" -B -W error -O docs/evidence/ibm-fez-actor-pilot/analyze.py'

bind core-msq-envelope-exploratory-replay '"$PYTHON" -B -W error scripts/msq_envelope_exploratory.py results/live/2026-10-27T014422.881898Z --out docs/evidence/measurement_sequence/envelope-run-exploratory.json'

bind core-msq-envelope-raw-diagnostics-replay '"$PYTHON" -B -W error scripts/msq_envelope_raw_diagnostics.py results/live/2026-10-27T014422.881898Z --out docs/evidence/measurement_sequence/envelope-run-raw-diagnostics.json'

bind core-msq-reset-persistence-replay '"$PYTHON" -B -W error scripts/msq_reset_persistence.py results/live/2026-10-27T014422.881898Z results/live/2026-10-30T010826.175789Z --out docs/evidence/measurement_sequence/reset-persistence.json'

bind core-msq-successor-replay '"$PYTHON" -B -W error scripts/msq_successor_replay.py results/live/2026-10-27T014422.881898Z --out docs/evidence/measurement_sequence/successor-replay.json'

bind core-n21-detuning-sign-replay '"$PYTHON" -B -W error scripts/n21_detuning_sign.py results/live/2026-10-27T173602.753176Z --out results/live/2026-10-27T173602.753176Z/detuning-sign-decisions.json'

bind core-n21-dose-decisions-replay '"$PYTHON" -B -W error scripts/n21_dose_decisions.py results/live/2026-10-27T014354.701394Z --out results/live/2026-10-27T014354.701394Z/dose-decisions.json'

bind core-707 '"$PYTHON" -B -W error scripts/iqm_measurement_diagnostic.py analyze results/iqm/runs/2026-10-25T224718Z-garnet-measurement-sequence-diagnostic-diagnostic --out results/iqm/measurement_sequence_diagnostic_analysis.json'

bind core-708 '"$PYTHON" -B -W error scripts/iqm_measurement_preflight.py analyze results/iqm/runs/2026-10-26T004628Z-garnet-measurement-sequence-pinching-probe-probe --out results/iqm/measurement_sequence_pinching_preflight.json'

bind core-709 '"$PYTHON" -B -W error scripts/iqm_measurement_sequence.py analyze results/iqm/runs/2026-10-26T004701Z-garnet-measurement-sequence-pinching-pinching --out results/iqm/measurement_sequence_pinching_analysis.json'

bind core-710 '"$PYTHON" -B -W error scripts/iqm_measurement_sequence.py analyze results/iqm/runs/2026-10-26T004701Z-garnet-measurement-sequence-pinching-pinching --gate-model sign-pooled --out results/iqm/measurement_sequence_pinching_sign_pooled_analysis.json'

bind core-712 '"$PYTHON" -B -W error scripts/iqm_measurement_sequence_aer_check.py run results/iqm/cases/measurement-sequence-pinching --calibration-dir results/iqm/calibration-sets/garnet/be070414-7624-4943-ac7e-1e2678f05684 > results/iqm/measurement_sequence_pinching_aer_check.json'

# The campaign `--out` writes a fresh directory and refuses different bytes under an existing one.
bind core-quantum-experiment-cases "PYTHONHASHSEED=0 \"\$PYTHON\" -B -W error scripts/experiment_cases.py --out $successor --tuna-shots 1575 --qx-shots 1575 --photonic-samples 1575 --photonic-shots 3150 --execution-seconds 300 --photonic-credits 1.00315"

# `add` binds every record or none: it refuses a path set that leaves a bound record out, so the retired
# directory's rows leave the ledger first, and the successor's files take their place.
"$PYTHON" -c '
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
ledger = json.loads(path.read_text())
ledger["records"] = {name: digest for name, digest in ledger["records"].items() if not name.startswith(sys.argv[2] + "/")}
path.write_text(json.dumps(ledger, indent=1) + "\n")
for name in ledger["records"]:
    print(name)
' "$ledger" "$retired" > "$list"
find "$successor" -type f | LC_ALL=C sort >> "$list"
set --
while IFS= read -r name; do
    set -- "$@" "$name"
done < "$list"
"$PYTHON" "$records" add "$@"
echo "runner_image_rebind: bound $# records" >&2
