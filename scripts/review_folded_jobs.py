"""Independently replay retained folded-QPE shots, contrasts, and timing.

The decoder imports no collector analysis function. Output preserves immutable
raw-file identities and the distinction between measured, ideal, and replayed
probabilities. The check mode exercises the retained audit without writing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from qiskit import qpy


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def _require(condition: bool, message: object) -> None:
    if not condition:
        raise ValueError(str(message))


def audit(run: Path) -> tuple[dict[str, Any], str]:
    jobs = ("db67fqsvf2bc73d0pk4g", "db67frimb58s738bci4g")
    source_paths = [run / name for name in ("record.json", "collect.json", "isa.qpy", "settled-account-usage.json")]
    source_paths += sorted((run / "raw").glob("*/*.json"))
    source_hashes = {str(path.relative_to(run)): digest(path) for path in source_paths}
    record = read(run / "record.json")
    collection = read(run / "collect.json")
    _require(
        isinstance(collection, list) and len(collection) == 3,
        "Audit requirement failed: isinstance(collection, list) and len(collection) == 3",
    )
    _require(collection[0]["submission_complete"], "Audit requirement failed: collection[0]['submission_complete']")
    _require(
        record["approved_record"]["mismatches"] == [],
        "Audit requirement failed: record['approved_record']['mismatches'] == []",
    )
    shots = record["shots"]
    _require(shots == 8192, "Audit requirement failed: shots == 8192")
    pubs = {pub["name"]: pub for pub in record["execution_pubs"]}
    _require(len(pubs) == 16, "Audit requirement failed: len(pubs) == 16")
    with (run / "isa.qpy").open("rb") as stream:
        circuits = {circuit.name: circuit for circuit in qpy.load(stream)}
    _require(set(circuits) == set(pubs), "Audit requirement failed: set(circuits) == set(pubs)")
    collected_groups = {group["group"]: group for group in collection[1:]}
    recorded_members = {member["name"]: member for group in record["groups"] for member in group["members"]}
    rows = {}
    job_rows = []
    indexed_file_count = 0
    for job in jobs:
        directory = run / "raw" / job
        index = read(directory / "index.json")
        _require(index["job_id"] == job, "Audit requirement failed: index['job_id'] == job")
        for filename, expected in index["files"].items():
            _require(digest(directory / filename) == expected, filename)
            indexed_file_count += 1
        _require(
            len(index["metrics"]) == len(index["metrics_sha256"]),
            "Audit requirement failed: len(index['metrics']) == len(index['metrics_sha256'])",
        )
        for filename, expected in zip(index["metrics"], index["metrics_sha256"], strict=True):
            _require(digest(directory / filename) == expected, filename)
            indexed_file_count += 1
        metrics = read(directory / index["metrics_latest"])
        metadata = read(directory / "result_metadata.json")
        rep_delay = metadata["options"]["execution"]["rep_delay"]
        _require(
            metadata["shots"] == shots and rep_delay == 0.00025,
            "Audit requirement failed: metadata['shots'] == shots and rep_delay == 0.00025",
        )
        _require(
            metadata["options"]["twirling"]["enable_gates"] is False,
            "Audit requirement failed: metadata['options']['twirling']['enable_gates'] is False",
        )
        _require(
            metadata["options"]["dynamical_decoupling"]["enable"] is False,
            "Audit requirement failed: metadata['options']['dynamical_decoupling']['enable'] is False",
        )
        scheduled_ns = 0
        pub_paths = sorted(directory.glob("pub_*.json"))
        expected_indices = list(range(len(pub_paths)))
        _require(
            [read(path)["pub_index"] for path in pub_paths] == expected_indices,
            "Audit requirement failed: [read(path)['pub_index'] for path in pub_paths] == expected_indices",
        )
        for path in pub_paths:
            pub = read(path)
            manifest = pubs[pub["pub_name"]]
            _require(len(manifest["components"]) == 1, "Audit requirement failed: len(manifest['components']) == 1")
            component = manifest["components"][0]
            name = component["member"]
            _require(name not in rows, "Audit requirement failed: name not in rows")
            registers = component["registers_by_replica"]
            _require(
                len(registers) == 1 and len(registers[0]) == 1,
                "Audit requirement failed: len(registers) == 1 and len(registers[0]) == 1",
            )
            _require(
                set(pub["registers"]) == set(registers[0]),
                "Audit requirement failed: set(pub['registers']) == set(registers[0])",
            )
            register = pub["registers"][registers[0][0]]
            strings = register["bitstrings"]
            bits = register["num_bits"]
            _require(
                register["num_shots"] == shots and len(strings) == shots,
                "Audit requirement failed: register['num_shots'] == shots and len(strings) == shots",
            )
            _require(
                all(len(value) == bits and set(value) <= {"0", "1"} for value in strings),
                (
                    "Audit requirement failed: all((len(value) == bits and set(value) <= {'0', '1'} for "
                    "value in strings))"
                ),
            )
            values = [int(value, 2) for value in strings]
            counts = Counter(values)
            phase_label = int(name.rsplit("_s", 1)[1])
            rung = name[4:].rsplit("_s", 1)[0]
            _require(
                bits == (1 if rung == "delay" else 2), "Audit requirement failed: bits == (1 if rung == 'delay' else 2)"
            )
            terminal_bit = 0 if rung == "delay" else 1
            successes = [int(value >> terminal_bit == phase_label >> 1) for value in values]
            successes_count = sum(successes)
            probability = successes_count / shots
            group = collected_groups[component["group"]]
            key = name + "_terminal_correct"
            _require(
                probability == group["measured_statistics"]["summary"][key],
                "Audit requirement failed: probability == group['measured_statistics']['summary'][key]",
            )
            measured = group["measured"][name][0]
            _require(
                all(abs(measured[value] - counts[value] / shots) <= 5e-07 for value in range(1 << bits)),
                (
                    "Audit requirement failed: all((abs(measured[value] - counts[value] / shots) <= 5e-07 "
                    "for value in range(1 << bits)))"
                ),
            )
            replay_probability = group["replayed_statistics"]["summary"][key]
            noisy = recorded_members[name]["replicas"][0]["noisy"]
            recovered_noisy_counts = [round(p * shots) for p in noisy]
            _require(
                sum(recovered_noisy_counts) == shots, "Audit requirement failed: sum(recovered_noisy_counts) == shots"
            )
            _require(
                all((abs(count / shots - p) <= 5e-07 for count, p in zip(recovered_noisy_counts, noisy, strict=True))),
                (
                    "Audit requirement failed: all((abs(count / shots - p) <= 5e-07 for count, p in "
                    "zip(recovered_noisy_counts, noisy, strict=True)))"
                ),
            )
            decoded_replay_probability = (
                sum(
                    (
                        count
                        for value, count in enumerate(recovered_noisy_counts)
                        if value >> terminal_bit == phase_label >> 1
                    )
                )
                / shots
            )
            _require(
                decoded_replay_probability == replay_probability,
                "Audit requirement failed: decoded_replay_probability == replay_probability",
            )
            circuit = circuits[pub["pub_name"]]
            sites = [
                (circuit.find_bit(instruction.qubits[0]).index, circuit.find_bit(instruction.clbits[0]).index)
                for instruction in circuit.data
                if instruction.operation.name == "measure"
            ]
            _require(
                [[q] for q, _ in sorted(sites, key=lambda item: item[1])]
                == record["family_configuration"]["measurement_sites"][name],
                (
                    "Audit requirement failed: [[q] for q, _ in sorted(sites, key=lambda item: item[1])] "
                    "== record['family_configuration']['measurement_sites'][name]"
                ),
            )
            timing = pub["metadata"]["compilation"]["scheduler_timing"]
            duration_dt = timing["circuit_duration"]
            scheduled_ns += shots * (duration_dt * 4 + 250000)
            half = shots // 2
            mean_left, mean_right = (sum(successes[:half]) / half, sum(successes[half:]) / half)
            lag_left, lag_right = (sum(successes[:-1]) / (shots - 1), sum(successes[1:]) / (shots - 1))
            variance_product = lag_left * (1 - lag_left) * lag_right * (1 - lag_right)
            covariance = (
                sum((a * b for a, b in zip(successes[:-1], successes[1:], strict=True))) / (shots - 1)
                - lag_left * lag_right
            )
            execution = group["executed"][name]
            _require(
                execution["window_unavailable_reason"] is None,
                "Audit requirement failed: execution['window_unavailable_reason'] is None",
            )
            _require(
                execution["calibration_changed_during_shots"] is False,
                "Audit requirement failed: execution['calibration_changed_during_shots'] is False",
            )
            ideal = [0.0] * (1 << bits)
            if rung == "delay":
                ideal[phase_label >> 1] = 1.0
            elif rung == "no_feed_forward" and phase_label % 2:
                ideal[phase_label] = ideal[phase_label ^ 2] = 0.5
            else:
                ideal[phase_label] = 1.0
            _require(
                ideal == recorded_members[name]["ideal"],
                "Audit requirement failed: ideal == recorded_members[name]['ideal']",
            )
            row = {
                "job_id": job,
                "pub": pub["pub_name"],
                "member": name,
                "phase_label": phase_label,
                "rung": rung,
                "shots": shots,
                "bit_counts_integer_order": [counts[value] for value in range(1 << bits)],
                "terminal_successes": successes_count,
                "terminal_probability": probability,
                "measured_probabilities_integer_order": [counts[value] / shots for value in range(1 << bits)],
                "exact_ideal_probabilities_integer_order": ideal,
                "replay_probabilities_integer_order": [count / shots for count in recovered_noisy_counts],
                "replay_reconstructed_counts_integer_order": recovered_noisy_counts,
                "replay_terminal_probability": replay_probability,
                "hardware_minus_replay": probability - replay_probability,
                "ideal_terminal_probability": 0.5 if rung == "no_feed_forward" and phase_label % 2 else 1.0,
                "measurement_sites": sites,
                "cz": circuit.count_ops().get("cz", 0),
                "scheduler_duration_dt": duration_dt,
                "scheduled_seconds": duration_dt * 4e-09,
                "lower_bound_dt": manifest["target_gate_lower_bound_dt"],
                "halfshot_descriptive_change": mean_right - mean_left,
                "lag1_descriptive_correlation": covariance / math.sqrt(variance_product),
                "executor_chunk_start": execution["start"],
                "executor_chunk_stop": execution["stop"],
                "calibration": execution["calibration"],
            }
            if bits == 2:
                first_errors = [int(value & 1 != phase_label & 1) for value in values]
                terminal_errors = [1 - success for success in successes]
                first_error = sum(first_errors) / shots
                terminal_error = sum(terminal_errors) / shots
                joint_error = sum((a * b for a, b in zip(first_errors, terminal_errors, strict=True))) / shots
                row["within_shot_error_statistics_descriptive"] = {
                    "first_error_probability": first_error,
                    "terminal_error_probability": terminal_error,
                    "joint_error_probability": joint_error,
                    "joint_error_minus_independent_marginals": joint_error - first_error * terminal_error,
                }
            rows[name] = row
        cost = next(
            cost
            for cost in record["execution_contract"]["selected_job_costs"]
            if f"/{manifest['kind']}/" in cost["name"]
        )
        execution_ns = metrics["circuits_execution_time_ns"]
        charge = metrics["usage"]["qpu_charge_time_seconds"]
        _require(
            metrics["usage"]["status"] == "complete",
            "Audit requirement failed: metrics['usage']['status'] == 'complete'",
        )
        _require(
            collection[0]["jobs"][job]["usage"]["job_status"] == "DONE",
            "Audit requirement failed: collection[0]['jobs'][job]['usage']['job_status'] == 'DONE'",
        )
        windows = metadata["executor"]["chunk_timing"]
        chunk_seconds = sum(
            (datetime.fromisoformat(window["stop"]) - datetime.fromisoformat(window["start"])).total_seconds()
            for window in windows
        )
        job_rows.append(
            {
                "job_id": job,
                "pubs": len(pub_paths),
                "shots_per_pub": shots,
                "charge_seconds": charge,
                "prediction_seconds": cost["estimated_charge_seconds"],
                "service_circuits_execution_ns": execution_ns,
                "scheduler_plus_repetition_ns": scheduled_ns,
                "scheduler_minus_service_ns": scheduled_ns - execution_ns,
                "charge_minus_service_seconds": charge - execution_ns / 1000000000.0,
                "executor_chunk_seconds": chunk_seconds,
                "prediction_execution_seconds": sum(pub["estimated_execution_seconds"] for pub in cost["pubs"]),
                "prediction_overhead_seconds": cost["overhead_seconds"],
            }
        )
    _require(len(rows) == 16, "Audit requirement failed: len(rows) == 16")
    contracts = record["observable_contracts"]
    _require(len(contracts) == 12, "Audit requirement failed: len(contracts) == 12")
    contrasts = []
    for contract in contracts:
        terms = contract["terms"]
        _require(
            len(terms) == 2 and terms[0]["sign"] == 1 and (terms[1]["sign"] == -1),
            "Audit requirement failed: len(terms) == 2 and terms[0]['sign'] == 1 and (terms[1]['sign'] == -1)",
        )
        left, right = [rows[term["member"]] for term in terms]
        _require(left["pub"] != right["pub"], "Audit requirement failed: left['pub'] != right['pub']")
        estimate = left["terminal_probability"] - right["terminal_probability"]
        _require(contract["alpha"] == 0.05 / 12, "Audit requirement failed: contract['alpha'] == 0.05 / 12")
        radius = 2 * math.sqrt(math.log(4 / contract["alpha"]) / (2 * shots))
        retained = next(
            item for item in collection[0]["family_analysis"]["observables"] if item["name"] == contract["name"]
        )
        _require(
            retained["estimate"] == estimate and retained["confidence_half_width"] == radius,
            (
                "Audit requirement failed: retained['estimate'] == estimate and "
                "retained['confidence_half_width'] == radius"
            ),
        )
        _require(
            retained["lo"] == estimate - radius and retained["hi"] == estimate + radius,
            ("Audit requirement failed: retained['lo'] == estimate - radius and retained['hi'] == estimate + radius"),
        )
        _require(retained["reject_null"] is None, "Audit requirement failed: retained['reject_null'] is None")
        contrasts.append(
            {
                "name": contract["name"],
                "difference": estimate,
                "simultaneous_interval": [estimate - radius, estimate + radius],
                "half_width": radius,
                "excludes_zero": abs(estimate) > radius,
                "ideal_difference": left["ideal_terminal_probability"] - right["ideal_terminal_probability"],
                "retained_reject_null": None,
            }
        )
    _require(
        source_hashes == {str(path.relative_to(run)): digest(path) for path in source_paths},
        (
            "Audit requirement failed: source_hashes == {str(path.relative_to(run)): digest(path) "
            "for path in source_paths}"
        ),
    )
    totals = {
        "charged_seconds": sum(job["charge_seconds"] for job in job_rows),
        "predicted_seconds": sum(job["prediction_seconds"] for job in job_rows),
        "service_execution_seconds": sum(job["service_circuits_execution_ns"] for job in job_rows) / 1000000000.0,
        "scheduler_plus_repetition_seconds": sum(job["scheduler_plus_repetition_ns"] for job in job_rows)
        / 1000000000.0,
        "scheduler_minus_service_seconds": sum(job["scheduler_minus_service_ns"] for job in job_rows) / 1000000000.0,
    }
    totals["charge_prediction_residual_seconds"] = totals["charged_seconds"] - totals["predicted_seconds"]
    totals["charge_minus_service_seconds"] = totals["charged_seconds"] - totals["service_execution_seconds"]
    confounds = [
        (
            "Coherent circuits use 69 CZ gates and terminal physical qubit 94; the dynamic "
            "circuits use 72 CZ gates and terminal qubit 93. Extra control and routing differ."
        ),
        (
            "The dynamic job and coherent job occupy adjacent but separate executor windows. "
            "Shared calibration timestamp does not establish stationary hardware noise."
        ),
        (
            "The delay arm replaces the first measurement and conditional feedback with a "
            "calibrated delay and a known-label unconditional phase correction, while retaining "
            "reset. It changes several mechanisms."
        ),
        (
            "Odd-label no-feed-forward ideal terminal success equals 0.5, while archived ideal "
            "success equals 1.0. The measured difference cannot isolate a noise-only controller "
            "effect."
        ),
        (
            "Each PUB carries one member and one replica. Matching numerical shot indices across "
            "distinct PUBs does not create paired observations."
        ),
        (
            "The displayed 95 percent simultaneous intervals require independent stationary "
            "repetitions within each PUB. Dependence within a shot or across PUBs is unrestricted "
            "by the union-bound construction."
        ),
        (
            "All delay confidence intervals include zero. The intervals establish bounded "
            "uncertainty; an equivalence claim needs a declared equivalence margin."
        ),
        (
            "Replay residuals compare hardware with retained finite-sample simulation results. "
            "Residuals identify model discrepancies but do not identify their physical cause."
        ),
    ]
    opportunities = [
        (
            "Keep hardware-minus-ideal, hardware-minus-noise-model, and packed-minus-isolated "
            "views separate. Odd no-feed-forward residuals reverse the sign found in all other "
            "arms, defeating a uniform subtractive success penalty."
        ),
        (
            "Preserve complete joint shot vectors within each ripple PUB; draw joint-error or "
            "covariance panels from those vectors and resample those vectors as indivisible units."
        ),
        (
            "Retain physical terminal-writer controls and matched routed templates. The coherent "
            "versus dynamic routing difference demonstrates why shared logical geometry alone is "
            "insufficient for causal comparisons."
        ),
        (
            "Use contrasts with declared thresholds and familywise uncertainty for inference. "
            "Label additional harmonics, kites, correlations, and phase portraits as descriptive "
            "until their multiplicity is qualified."
        ),
        (
            "Retain scheduler duration, repetition delay, service execution metric, and charged "
            "time separately. Forecast accuracy for these 16 PUBs does not bound denser ripple "
            "schedules."
        ),
        (
            "Render finite-shot uncertainty as an explicit data layer. A dark algebraic sector "
            "should show its exact predicted null and its measured leakage interval separately."
        ),
    ]
    report = {
        "schema": "independent-folded-raw-audit-v1",
        "run": run.name,
        "audit_method": (
            "Independent integer bitstring decode and stdlib Hoeffding recomputation; QPY "
            "inspected through Qiskit; collector analysis functions were not imported."
        ),
        "audit_script_sha256": digest(Path(__file__)),
        "source_sha256": source_hashes,
        "hash_verified_indexed_files": indexed_file_count,
        "source_hashes_unchanged_during_audit": True,
        "raw_register_count": 16,
        "raw_pub_shots": 16 * shots,
        "shared_shot_pairing_scope": "within one PUB only",
        "contract_checks": {
            "all12_contrasts_match": True,
            "all16_terminal_estimates_match": True,
            "all16_measurement_site_maps_match_qpy": True,
            "all16_replay_quantized_count_estimates_match": True,
            "all_declared_shot_counts_match": True,
            "approval_mismatches_empty": True,
        },
        "jobs": job_rows,
        "timing_totals": totals,
        "members": list(rows.values()),
        "contrasts": contrasts,
        "confidence": {
            "family_alpha": 0.05,
            "comparisons": 12,
            "per_contrast_alpha": 0.05 / 12,
            "half_width": contrasts[0]["half_width"],
            "formula": "2*sqrt(log(4/(0.05/12))/(2*8192))",
            "raw_unpaired_pub_identity_preserved": True,
            "precision_contract_reject_null_remains_null": True,
        },
        "confounds": confounds,
        "opportunities": opportunities,
        "defects": [],
        "wording_correction": (
            "Delay replaces feedback with known-label unconditional correction; saying that it "
            "simply removes correction is inaccurate."
        ),
    }
    lines = [
        "# Independent folded-QPE raw audit",
        "",
        (
            "The retained evidence reproduces all 16 terminal-success estimates and all 12 "
            "recorded simultaneous intervals. Both raw job indexes verify every indexed file hash "
            "(20 files), and all 26 source-file hashes remain identical across the audit. QPY "
            "measurement mappings match the record. The audit found zero integrity or numerical "
            "defects in the tested surfaces."
        ),
        "",
        (
            "Each of 16 PUBs contains 8,192 shots. The two jobs charge 29 s and 11 s. Raw shot "
            "indices are paired only within their own PUB."
        ),
        "",
        "| Contrast versus archived | s0 | s1 | s2 | s3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for rung in ("delay", "no_feed_forward", "coherent"):
        selected = [c for c in contrasts if c["name"].startswith("qpe_" + rung + "_minus")]
        lines.append("| " + rung + " | " + " | ".join(f"{100 * c['difference']:+.3f} pp" for c in selected) + " |")
    lines += [
        "",
        (
            "Each contrast has a simultaneous-family half-width of "
            f"{100 * contrasts[0]['half_width']:.6f} percentage points. "
            "The four coherent intervals exclude zero positively; the odd no-feed-forward "
            "intervals exclude zero negatively. The other six intervals contain zero. The 12 "
            "precision contracts retain `reject_null=null`."
        ),
        "",
        (
            "The bound uses alpha = 0.05 / 12 per contrast and alpha / 2 per separate PUB: `2 "
            "sqrt(log(4 / alpha) / (2 N))`. The claim assumes independent stationary repetitions "
            "within each PUB and permits arbitrary within-shot and cross-PUB dependence. "
            "Descriptive lag and half-shot checks do not prove stationarity."
        ),
        "",
        "| Timing surface | Seconds |",
        "|---|---:|",
    ]
    lines += [f"| {name} | {value:.12f} |" for name, value in totals.items()]
    lines += [
        "",
        (
            "The forecast residual is +0.367600128 s (about 0.93 percent), with compensating "
            "execution and overhead errors. The scheduler-plus-repetition total exceeds the "
            "service metric by 0.000539904 s; the retained records do not attribute that residual. "
            "Charge minus the service metric totals 4.428385536 s. These observations validate "
            "timing accounting for the executed schedules only."
        ),
        "",
        "## Interpretation boundaries",
        "",
    ]
    lines += ["- " + item for item in confounds]
    lines += ["", "## Ripple opportunities", ""] + ["- " + item for item in opportunities]
    lines += [
        "",
        (
            "The odd no-feed-forward hardware-minus-replay residuals are +13.464355 and +10.424805 "
            "percentage points. The other 14 residuals are negative. These are model-discrepancy "
            "observations; the 12-family intervals above cover rung contrasts, not these "
            "exploratory residuals."
        ),
        "",
        "## Source hashes",
        "",
        "| Source | SHA-256 |",
        "|---|---|",
    ]
    lines += [
        f"| `{name}` | `{value}` |"
        for name, value in source_hashes.items()
        if "/" not in name or name.endswith("/index.json")
    ]
    lines += [
        "",
        (
            "The JSON companion retains all raw-file hashes, integer counts, bit-level joint "
            "errors, exact contrast endpoints, scheduler durations, measurement sites, and job "
            "metrics. The audit script reads the retained run and writes only its selected output "
            "pair; `--check` compares the retained audit without writing files."
        ),
        "",
    ]
    return (report, "\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=Path("results/live/2026-10-12T055624.091217Z"),
        help="retained run containing record.json, collect.json, isa.qpy, and raw/",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/ripple/folded-job-review"),
        help="output stem for .json and .md; paths are relative to the working directory",
    )
    parser.add_argument("--check", action="store_true", help="compare existing outputs without writing")
    args = parser.parse_args()
    report, markdown = audit(args.run_dir)
    outputs = {
        args.out.with_suffix(".json"): json.dumps(report, indent=2) + "\n",
        args.out.with_suffix(".md"): markdown,
    }
    if args.check:
        for path, content in outputs.items():
            _require(path.read_text() == content, f"Retained audit differs: {path.name}")
        print("Folded-job review: raw hashes, counts, intervals, timing, and retained outputs match")
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        print("Folded-job review: wrote JSON and Markdown audit")


if __name__ == "__main__":
    main()
