"""Offline collection contracts with real circuit histories and synthetic raw shots."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
from collections import defaultdict
from collections.abc import Callable
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from qiskit import qpy, transpile
from qiskit.primitives.containers import BitArray, DataBin, PrimitiveResult, SamplerPubResult
from qiskit_ibm_runtime.fake_provider import FakeKingston

import correction_collection as collection
import live_run
import packing
import qpu_planning
from correction_circuits import bind_correction_template, correction_template, validate_correction_pair
from correction_schedule_contracts import _fixture as schedule_fixture
from correction_statistics import MEMBERS


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _reject(action: Callable[[], Any], description: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise RuntimeError(f"accepted invalid {description}")


class _Fixture:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        routed = transpile(
            correction_template(),
            backend=FakeKingston(),
            initial_layout=[95, 79, 93, 92, 94],
            optimization_level=3,
            seed_transpiler=20261010,
        )
        self.raw_record: dict[str, Any] = {"directory": "raw/fixture_job", "files": {}}
        raw_dir = directory / "raw" / "fixture_job"
        raw_dir.mkdir(parents=True)
        self.pub_payloads: list[dict[str, Any]] = []
        self.evidence: list[dict[str, Any]] = []
        self.executed: dict[str, Any] = {}
        self.histograms: list[dict[str, int]] = []
        for index, (name, label, arm) in enumerate(
            zip(
                MEMBERS,
                (1, 1, 3, 3),
                ("measured_feedback", "recorded_bit_independent", "recorded_bit_independent", "measured_feedback"),
                strict=True,
            )
        ):
            feedback = bind_correction_template(routed, label, "measured_feedback")
            independent = bind_correction_template(routed, label, "recorded_bit_independent")
            pair = validate_correction_pair(routed, feedback, independent, label)
            bound = feedback if arm == "measured_feedback" else independent
            pub_name = f"fixture_dynamic_pub_{index + 1:02d}"
            circuit = packing.fuse([bound], ["g0_"], pub_name)
            manifest = {
                "name": pub_name,
                "backend": "fixture_backend",
                "kind": "dynamic",
                "components": [
                    {
                        "group": "folded_correction",
                        "member": name,
                        "reference": False,
                        "register_prefix": "g0_",
                        "physical_qubits": sorted(live_run._physical(circuit)),
                        "registers_by_replica": [[circuit.cregs[0].name]],
                    }
                ],
            }
            success = 8100 if arm == "recorded_bit_independent" else 6500
            correct = format(label, "02b")
            wrong = format(label ^ 2, "02b")
            histogram = {correct: success, wrong: 8192 - success}
            self.histograms.append(histogram)
            payload = {
                "pub_index": index,
                "pub_name": pub_name,
                "registers": {
                    circuit.cregs[0].name: {
                        "num_bits": 2,
                        "num_shots": 8192,
                        "bitstrings": [correct] * success + [wrong] * (8192 - success),
                    }
                },
                "metadata": {"compilation": {"scheduler_timing": schedule_fixture(pair)}},
            }
            self.pub_payloads.append(payload)
            self.write_raw(index)
            self.evidence.append(
                collection.retained_member(
                    directory,
                    self.raw_record,
                    job_id="fixture_job",
                    pub_index=index,
                    pub_manifest=manifest,
                    member=name,
                    circuit=circuit,
                    histogram=histogram,
                    dt_seconds=4e-9,
                )
            )
            self.executed[name] = {
                "pub": pub_name,
                "calibration": "fixture_calibration",
                "calibration_changed_during_shots": False,
            }
        pubs = [row["pub_manifest"] for row in self.evidence]
        planned = {"backend": "fixture_backend", "kind": "dynamic", "members": list(MEMBERS), "pubs": pubs}
        self.record: dict[str, Any] = {
            "family_configuration": {"name": "folded-correction"},
            "shots": 8192,
            "submission": {
                "complete": True,
                "planned_jobs": [copy.deepcopy(planned)],
                "jobs": [{**copy.deepcopy(planned), "job_id": "fixture_job"}],
            },
        }

    def write_raw(self, index: int) -> None:
        data = (json.dumps(self.pub_payloads[index], sort_keys=True) + "\n").encode()
        filename = f"pub_{index:02d}.json"
        (self.directory / "raw" / "fixture_job" / filename).write_bytes(data)
        self.raw_record["files"][filename] = hashlib.sha256(data).hexdigest()

    def read_first(self, histogram: dict[str, int] | None = None) -> dict[str, Any]:
        row = self.evidence[0]
        return collection.retained_member(
            self.directory,
            self.raw_record,
            job_id="fixture_job",
            pub_index=0,
            pub_manifest=row["pub_manifest"],
            member=row["name"],
            circuit=row["circuit"],
            histogram=self.histograms[0] if histogram is None else histogram,
            dt_seconds=4e-9,
        )


def _verify_collection_pipeline(fixture: _Fixture) -> None:
    """Exercise archive loading, raw persistence, integer decoding and final dispatch."""
    directory = fixture.directory / "pipeline"
    directory.mkdir()
    archive = io.BytesIO()
    qpy.dump([row["circuit"] for row in fixture.evidence], archive)
    (directory / "isa.qpy").write_bytes(archive.getvalue())
    record = copy.deepcopy(fixture.record)
    record.update(
        experiment_digest=live_run.experiment_digest(),
        schema_version=live_run.RECORD_SCHEMA_VERSION,
        schema_contract=live_run.RECORD_SCHEMA_CONTRACT,
        seed_simulator=20261011,
        observable_contracts=[],
        groups=[
            {
                "group": "folded_correction",
                "members": [
                    {
                        "name": row["name"],
                        "replica_qubits": [row["pub_manifest"]["components"][0]["physical_qubits"]],
                        "replica_prefixes": [""],
                        "reference": False,
                        "ideal": [float(index == label) for index in range(4)],
                    }
                    for row, label in zip(fixture.evidence, (1, 1, 3, 3), strict=True)
                ],
            }
        ],
    )
    record["submission"]["qpy_archive_sha256"] = hashlib.sha256(archive.getvalue()).hexdigest()
    (directory / "record.json").write_text(json.dumps(record))
    result = PrimitiveResult(
        [
            SamplerPubResult(
                DataBin(
                    **{
                        name: BitArray.from_samples(register["bitstrings"], num_bits=2)
                        for name, register in payload["registers"].items()
                    }
                ),
                metadata=copy.deepcopy(payload["metadata"]),
            )
            for payload in fixture.pub_payloads
        ],
        metadata={},
    )
    job = SimpleNamespace(result=lambda: result, metrics=lambda: {}, status=lambda: "DONE")
    start = datetime(2026, 10, 12, tzinfo=UTC)
    target = SimpleNamespace(dt=4e-9)
    # BackendProperties lists per-qubit Nduv values under qubits; the
    # fixture's qubits report none.
    properties = SimpleNamespace(last_update_date=start, qubits=defaultdict(list))
    backend = SimpleNamespace(
        name="fixture_backend", properties=lambda **_kwargs: properties, target_history=lambda **_kwargs: target
    )
    service = SimpleNamespace(job=lambda _identity: job, backend=lambda _name: backend)
    windows = SimpleNamespace(windows=[(start, start + timedelta(seconds=1))] * 4, source="fixture", reason=None)
    original_distribution = live_run._distribution
    normalized = 0
    with ExitStack() as stack, redirect_stdout(io.StringIO()):
        retained = stack.enter_context(patch.object(collection, "retained_member", wraps=collection.retained_member))

        def normalize(counts: dict[str, int], clbits: int) -> Any:
            nonlocal normalized
            _require(retained.call_count == normalized + 1, "normalization preceded retained integer-count capture")
            normalized += 1
            return original_distribution(counts, clbits)

        substitutions = {
            "submission_gaps": lambda _submission: ([], [], []),
            "reconcile_attempted_jobs": lambda *_args: False,
            "job_usage_record": lambda *_args: {"usage_status": "final", "qpu_charge_time_seconds": "12"},
            "pub_windows": lambda *_args: windows,
            "noise_simulator": lambda *_args: object(),
            "check_target_matches_properties": lambda *_args: None,
            "target_duration_dt": lambda *_args: 0,
            "replay_entries": lambda *_args: {},
            "invocation_usage": lambda *_args: {"scope": "fixture"},
            "_distribution": normalize,
        }
        for name, replacement in substitutions.items():
            stack.enter_context(patch.object(live_run, name, side_effect=replacement))
        live_run.collect(service, directory)
    collected = json.loads((directory / "collect.json").read_bytes())
    _require(normalized == 4, "collection omitted a PUB")
    _require(collected[0]["family_analysis"]["decision_available"] is True, "collection failed correction dispatch")
    _require(
        collected[1]["integer_counts"] == {row["name"]: row["counts"] for row in fixture.evidence},
        "integer counts changed",
    )
    _require("measured_summary_readout_corrected" not in collected[1], "collector substituted corrected inference")
    _require((directory / "raw" / "fixture_job" / "index.json").exists(), "collection failed raw preservation")


def verify() -> dict[str, int]:
    invalid_histograms: tuple[dict[str, Any], ...] = (
        {"01": True},
        {"01": 8192.0},
        {"01": -1},
        {"01": 8191},
        {"1": 8192},
        {"02": 8192},
    )
    for histogram in invalid_histograms:
        _reject(partial(collection.integer_counts, histogram), "histogram")
    _require(collection.integer_counts({"00": 1, "01": 2, "10": 3, "11": 8186}) == [1, 2, 3, 8186], "bit order changed")
    with tempfile.TemporaryDirectory(prefix="correction-collection-") as directory:
        fixture = _Fixture(Path(directory))
        result = collection.analyze(fixture.record, fixture.evidence, fixture.executed, live_run)
        _require(result["decision_available"] is True, f"valid synthetic evidence rejected: {result}")
        _require(result["statistical_decision"]["admit_known_correction"] is True, "strong known-label gain rejected")
        _require(set(result["integer_counts"]) == set(MEMBERS), "integer histograms were lost")
        _require(all(pair["qualified"] for pair in result["schedule_pairs"].values()), "schedule gate bypassed")
        fixture.record["observable_contracts"] = []
        dispatched = qpu_planning.measured_family(
            fixture.record, {}, fixture.executed, live_run, correction_evidence=fixture.evidence
        )
        _require(dispatched == result, "empty generic contracts bypassed correction collection")
        unavailable = qpu_planning.measured_family(fixture.record, {}, fixture.executed, live_run)
        _require(
            unavailable["decision_available"] is False and "withheld" in unavailable, "missing raw evidence admitted"
        )
        _verify_collection_pipeline(fixture)
        json.dumps(result, allow_nan=False)
        original_raw = (fixture.directory / "raw" / "fixture_job" / "pub_00.json").read_bytes()
        raw_path = fixture.directory / "raw" / "fixture_job" / "pub_00.json"
        raw_path.write_bytes(original_raw + b" ")
        _reject(fixture.read_first, "changed retained raw digest")
        raw_path.write_bytes(original_raw)
        _reject(lambda: fixture.read_first({"01": 6501, "11": 1691}), "counts differing from retained shots")
        for mutation in ("register_width", "shot_count", "missing_bits", "wrong_pub", "invalid_bit"):
            payload = copy.deepcopy(fixture.pub_payloads[0])
            register = next(iter(fixture.pub_payloads[0]["registers"].values()))
            if mutation == "register_width":
                register["num_bits"] = True
            elif mutation == "shot_count":
                register["num_shots"] = 8191
            elif mutation == "missing_bits":
                register["bitstrings"].pop()
            elif mutation == "wrong_pub":
                fixture.pub_payloads[0]["pub_name"] = "another_pub"
            else:
                register["bitstrings"][0] = "2x"
            fixture.write_raw(0)
            _reject(fixture.read_first, mutation)
            fixture.pub_payloads[0] = payload
            fixture.write_raw(0)

        mutations = (
            "retention_error",
            "missing_member",
            "reordered_member",
            "duplicate_member",
            "float_count",
            "wrong_shots",
            "missing_calibration",
            "calibration_drift",
            "different_calibration",
            "unknown_drift",
            "missing_timing",
            "mismatched_schedule",
            "missing_independent_else",
            "wrong_circuit",
            "wrong_pub",
            "wrong_job",
            "extra_replica",
            "missing_dt",
            "changed_dt",
            "incomplete_job",
        )
        for mutation in mutations:
            record = copy.deepcopy(fixture.record)
            evidence = copy.deepcopy(fixture.evidence)
            executed = copy.deepcopy(fixture.executed)
            if mutation == "retention_error":
                evidence[0] = {"name": MEMBERS[0], "error": "retained PUB digest changed"}
            elif mutation == "missing_member":
                evidence.pop()
            elif mutation == "reordered_member":
                evidence.reverse()
            elif mutation == "duplicate_member":
                evidence[1]["name"] = evidence[0]["name"]
            elif mutation == "float_count":
                evidence[0]["counts"][0] = 0.0
            elif mutation == "wrong_shots":
                record["shots"] = 4096
            elif mutation == "missing_calibration":
                executed[MEMBERS[0]]["calibration"] = None
            elif mutation == "calibration_drift":
                executed[MEMBERS[0]]["calibration_changed_during_shots"] = True
            elif mutation == "different_calibration":
                executed[MEMBERS[0]]["calibration"] = "another_calibration"
            elif mutation == "unknown_drift":
                executed[MEMBERS[0]]["calibration_changed_during_shots"] = None
            elif mutation == "missing_timing":
                evidence[0]["timing"] = None
            elif mutation == "mismatched_schedule":
                evidence[1]["timing"]["timing"] = evidence[1]["timing"]["timing"].replace(",42,4,play", ",43,4,play")
            elif mutation == "missing_independent_else":
                evidence[1]["timing"]["timing"] = "\n".join(
                    row for row in evidence[1]["timing"]["timing"].splitlines() if not row.startswith("else,")
                )
            elif mutation == "wrong_circuit":
                evidence[1]["circuit"].x(evidence[1]["pub_manifest"]["components"][0]["physical_qubits"][0])
            elif mutation == "wrong_pub":
                executed[MEMBERS[0]]["pub"] = "another_pub"
            elif mutation == "wrong_job":
                evidence[0]["job_id"] = "another_job"
            elif mutation == "extra_replica":
                evidence[0]["pub_manifest"]["components"][0]["registers_by_replica"].append(["extra"])
            elif mutation == "missing_dt":
                evidence[0]["dt_seconds"] = None
            elif mutation == "changed_dt":
                evidence[1]["dt_seconds"] = 8e-9
            else:
                record["submission"]["complete"] = False
            result = collection.analyze(record, evidence, executed, live_run)
            _require(result["decision_available"] is False and "withheld" in result, f"accepted {mutation}")
            _require("statistical_decision" not in result, f"{mutation} produced a scientific decision")
            if mutation == "retention_error":
                _require(result["evidence_errors"][MEMBERS[0]] == evidence[0]["error"], "retention failure detail lost")
        with patch.object(collection.correction_schedule, "qualify_pair", return_value={"qualified": False}):
            result = collection.analyze(fixture.record, fixture.evidence, fixture.executed, live_run)
            _require(result["decision_available"] is False, "explicitly unqualified schedule was admitted")
    return {"successful_synthetic_acquisitions": 1, "withheld_mutations": len(mutations) + 1, "raw_rejections": 13}


def verify_cli() -> None:
    base = [
        "--family",
        "folded-correction",
        "--shots",
        "8192",
        "--max-execution-seconds",
        "30",
        "--max-total-execution-seconds",
        "30",
        "--cost-scenario",
        "controller-stress:4.6:40",
    ]
    invalid = (
        ["--native-dry-run", "--out", "/tmp/correction-cli-contract-unused"],
        ["--shots", "4096"],
        ["--alpha", "0.1"],
        ["--power", "0.9"],
        ["--max-replicas", "2"],
        ["--optimize"],
        ["--backends", "ibm_fez"],
        ["--backends", "ibm_fez,ibm_fez,ibm_marrakesh"],
        ["--max-execution-seconds", "29"],
        ["--max-execution-seconds", "31"],
        ["--max-total-execution-seconds", "29"],
        ["--max-total-execution-seconds", "31"],
        ["--cost-scenario", "lower-overhead:1:40"],
        ["--cost-scenario", "lower-latency:4.6:10"],
        ["--job-overhead-seconds", "5"],
        ["--classical-latency-us", "50"],
    )
    with patch.object(live_run, "QiskitRuntimeService") as service, redirect_stderr(io.StringIO()):
        for arguments in [base[:-2], *(base + options for options in invalid)]:
            try:
                live_run.main(arguments)
            except SystemExit as error:
                _require(error.code == 2, f"invalid CLI returned another status: {arguments}")
            else:
                raise RuntimeError(f"invalid CLI accepted: {arguments}")
        _require(service.call_count == 0, "invalid correction CLI constructed a service")
    captured = []

    def stop_at_plan(_service: Any, args: Any) -> Any:
        captured.append(args)
        raise live_run.LiveRunError("offline CLI contract reached plan")

    with (
        patch.object(live_run, "QiskitRuntimeService", return_value=object()),
        patch.object(live_run, "plan", side_effect=stop_at_plan),
        patch.object(live_run.local_compute, "validate"),
        redirect_stderr(io.StringIO()),
        redirect_stdout(io.StringIO()),
    ):
        _require(live_run.main(base) == 1, "CLI plan boundary was bypassed")
    _require(len(captured) == 1, "valid correction CLI failed to reach planning")
    args = captured[0]
    _require(args.backends == ["ibm_fez", "ibm_kingston", "ibm_marrakesh"], "CLI omitted a candidate device")
    _require(args.max_replicas == 1 and args.isolated_reference is False, "CLI added a replica or reference PUB")
    _require(args.shot_tiers == [8192] and args.replica_tiers == [1], "inactive CLI tiers misstate the fixed protocol")


if __name__ == "__main__":
    verify_cli()
    print(json.dumps(verify(), sort_keys=True))
