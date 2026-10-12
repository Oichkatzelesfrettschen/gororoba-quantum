"""Validate the extractor using labeled synthetic copies under temporary storage.

The copied QPY and family metadata supply realistic mappings. Generated bit
vectors are fixture data; every extracted payload retains synthetic_fixture.
The public CLI rejects those fixtures, and the tests never create hardware
results in the repository.
"""

from __future__ import annotations

import copy
import io
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import redirect_stderr
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import extract_measured_ripple as extractor
import numpy as np
from qiskit import qpy

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"ripple": "2026-10-12T062505.208379Z", "rank-sector": "2026-10-12T062505.552988Z"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    contents = extractor.canonical(value)
    path.write_bytes(contents)
    return extractor.digest(contents)


def fixture(directory: Path, family: str) -> Path:
    """Copy a retained submit-free archive and mark every generated result synthetic."""
    source = ROOT / "results/live" / SOURCES[family]
    directory.mkdir(parents=True)
    original = (source / "record.json").read_bytes()
    record = extractor.decode(original)
    shutil.copyfile(source / "isa.qpy", directory / "isa.qpy")
    qpy_bytes = (directory / "isa.qpy").read_bytes()
    qpy_digest = extractor.digest(qpy_bytes)
    circuits = {circuit.name: circuit for circuit in qpy.load(io.BytesIO(qpy_bytes))}
    tiers = (64, 128) if family == "ripple" else (600, 1200)
    allocation = {pub["name"]: tiers[index % 2] for index, pub in enumerate(record["execution_pubs"])}
    record.update(evidence_kind=extractor.FIXTURE_MARKER, state="submitted", shots=max(tiers), pub_shots=allocation)
    record["budget_plan"]["admitted"] = True
    record["approved_record"] = {
        "mismatches": [],
        "record_sha256": extractor.digest(original),
        "qpy_archive_sha256": qpy_digest,
    }
    record["approval_consumed"] = {"run": record["started"], "consumed_at": "2026-10-12T12:00:00+00:00"}
    submission: dict[str, Any] = {
        "started": record["started"],
        "planned_backends": [],
        "qpy_archive_sha256": qpy_digest,
        "planned_jobs": [],
        "jobs": [],
        "complete": True,
    }
    record["submission"] = submission
    members = {member["name"]: member for group in record["groups"] for member in group["members"]}
    calibration = record["groups"][0]["calibration"]
    header: dict[str, Any] = {"submission_complete": True, "jobs": {}, "family_measurements": {}}
    collection = [header]
    measured, executed = {}, {}
    for batch, shots in enumerate(tiers, 1):
        pubs = [pub for pub in record["execution_pubs"] if allocation[pub["name"]] == shots]
        backend = pubs[0]["backend"]
        submission["planned_backends"] = [backend]
        plan = {
            "backend": backend,
            "kind": "static",
            "batch_index": batch,
            "batch_count": len(tiers),
            "shots": shots,
            "members": [component["member"] for pub in pubs for component in pub["components"]],
            "pubs": pubs,
            "qpy_archive_sha256": qpy_digest,
            "calibrations": [calibration],
            "recovery_tags": extractor.runtime._recovery_tags(
                record["started"], backend, "static", batch, len(tiers), pubs, qpy_digest
            ),
            "options": {"default_shots": shots},
            "budget_before": {},
            "state": "accepted",
        }
        submission["planned_jobs"].append(plan)
        job_id = f"synthetic-{family}-{batch}"
        job = extractor.runtime._job_record(plan, job_id)
        submission["jobs"].append(job)
        raw_dir = directory / "raw" / job_id
        raw_dir.mkdir(parents=True)
        files = {}
        group_entries: dict[str, Any] = {}
        for position, pub in enumerate(pubs):
            registers = {}
            widths = {register.name: register.size for register in circuits[pub["name"]].cregs}
            for component_index, component in enumerate(pub["components"]):
                name = component["member"]
                require(len(component["registers_by_replica"]) == 1, "fixture needs one replica per lane")
                register_names = component["registers_by_replica"][0]
                values = (np.arange(shots) + component_index) % 2
                offset = 0
                for register_name in register_names:
                    width = widths[register_name]
                    registers[register_name] = {
                        "num_bits": width,
                        "num_shots": shots,
                        "bitstrings": [
                            format((int(value) >> offset) & ((1 << width) - 1), f"0{width}b") for value in values
                        ],
                    }
                    offset += width
                distribution = np.bincount(values, minlength=1 << offset) / shots
                measured[name] = [distribution]
                execution = {
                    "pub": pub["name"],
                    "shots": shots,
                    "start": "2026-10-12T12:00:00+00:00",
                    "stop": "2026-10-12T12:00:01+00:00",
                    "calibration": calibration,
                    "calibration_changed_during_shots": False,
                    "window_unavailable_reason": None,
                }
                executed[name] = execution
                header["family_measurements"][name] = {
                    "replica_probabilities": [distribution.tolist()],
                    "execution": execution,
                    "replayed_replica_probabilities": [members[name]["ideal"]],
                    "replay_status": "calibration_bound",
                }
                group = group_entries.setdefault(
                    component["group"], {"group": component["group"], "job_id": job_id, "measured": {}, "executed": {}}
                )
                group["measured"][name] = [[round(float(value), 6) for value in distribution]]
                group["executed"][name] = execution
            filename = f"pub_{position:02d}.json"
            files[filename] = write(
                raw_dir / filename,
                {
                    "pub_index": position,
                    "pub_name": pub["name"],
                    "registers": registers,
                    "metadata": {"evidence_kind": extractor.FIXTURE_MARKER},
                },
            )
        collection.extend(group_entries.values())
        files["result_metadata.json"] = write(
            raw_dir / "result_metadata.json", {"evidence_kind": extractor.FIXTURE_MARKER}
        )
        charge = batch * 1.25
        metrics_hash = write(
            raw_dir / "job_metrics.json", {"usage": {"status": "complete", "qpu_charge_time_seconds": charge}}
        )
        write(
            raw_dir / "index.json",
            {
                "job_id": job_id,
                "files": files,
                "metrics": ["job_metrics.json"],
                "metrics_sha256": [metrics_hash],
                "metrics_latest": "job_metrics.json",
            },
        )
        header["jobs"][job_id] = {
            "backend": backend,
            "kind": "static",
            "raw": {"directory": f"raw/{job_id}", "files": files},
            "usage": {
                "job_status": "DONE",
                "usage_status": "final",
                "submitted_pub_shots": len(pubs) * shots,
                "qpu_charge_time_seconds": str(charge),
            },
        }
    header["family_analysis"] = extractor.qpu_planning.measured_family(record, measured, executed, extractor.runtime)
    write(directory / "record.json", record)
    write(directory / "collect.json", collection)
    return directory


def snapshot(directory: Path) -> dict[str, tuple[Any, ...]]:
    result = {}
    for path in [directory, *sorted(directory.rglob("*"))]:
        stat = path.lstat()
        key = path.relative_to(directory).as_posix()
        if path.is_symlink():
            content: Any = os.readlink(path)
        else:
            content = extractor.digest(path.read_bytes()) if path.is_file() else None
        result[key] = (stat.st_dev, stat.st_ino, stat.st_nlink, stat.st_mtime_ns, content)
    return result


def rejected(call: Callable[[], Any], fragment: str) -> None:
    try:
        call()
    except (ValueError, KeyError, OSError, extractor.runtime.LiveRunError) as error:
        require(fragment in str(error), f"expected {fragment!r}, received {error}")
    else:
        raise RuntimeError(f"accepted mutant: {fragment}")


def change_json(directory: Path, name: str, mutate: Callable[[Any], None]) -> None:
    path = directory / name
    value = extractor.decode(path.read_bytes())
    mutate(value)
    write(path, value)


def raw_mutation(directory: Path, mutate: Callable[[Any], None], *, rehash: bool) -> None:
    record = extractor.decode((directory / "record.json").read_bytes())
    job = record["submission"]["jobs"][0]
    prefix = "raw/" + job["job_id"]
    change_json(directory, prefix + "/pub_00.json", mutate)
    if rehash:
        new_hash = extractor.digest((directory / prefix / "pub_00.json").read_bytes())
        change_json(
            directory, prefix + "/index.json", lambda index: index["files"].__setitem__("pub_00.json", new_hash)
        )
        change_json(
            directory,
            "collect.json",
            lambda collected: collected[0]["jobs"][job["job_id"]]["raw"]["files"].__setitem__("pub_00.json", new_hash),
        )


def verify_result(result: dict[str, Any], family: str) -> None:
    require(result["evidence_kind"] == extractor.FIXTURE_MARKER, "fixture acquired a hardware evidence label")
    expected = (929, 146) if family == "ripple" else (176, 36)
    require((len(result["members"]), len(result["pubs"])) == expected, "complete family membership differs")
    require(
        len(result["endpoint_analysis"]["observables"]) == (1138 if family == "ripple" else 196),
        "endpoint coverage differs",
    )
    for pub in result["pubs"]:
        matrix = np.asarray(pub["event_zero"]["covariance"])
        require(matrix.shape == (len(pub["event_zero"]["members"]),) * 2, "joint matrix dimension differs")
        require(np.all(np.diag(matrix) == 0.25), "known synthetic event variance differs")
        require(np.allclose(matrix, matrix.T), "joint matrix is asymmetric")
        require(matrix.shape[0] <= 10, "extractor built a cross-PUB all-member matrix")
    totals = result["throughput"]
    require(totals["physical_pub_shots"] == sum(pub["shots"] for pub in result["pubs"]), "PUB shot total differs")
    require(
        totals["unique_reserved_qubit_shots"]
        == sum(pub["shots"] * len(pub["reserved_physical_qubits"]) for pub in result["pubs"]),
        "unique occupancy total differs",
    )
    require(totals["retained_collector_charge_seconds"] == 3.75, "settled fixture charge differs")
    require(
        totals["covariance_adjusted_goodput"] is None and totals["fidelity_goodput"] is None,
        "undefined goodput inferred",
    )
    if family == "rank-sector":
        row = result["members"]["rank_sector_0_kernel_at_one_t3d2"]
        require(row["metadata"]["unit_probe_norm_factor_exact"] == "121/16", "LCU unit-probe normalization differs")
        require(row["metadata"]["unnormalized_probe_norm_factor_exact"] == "121/8", "unnormalized probe factor differs")
        require(len(row["shot_order_blocks"]) >= 2, "shot-order block diagnostic missing")


def main() -> int:
    rejected_mutants = 0
    with TemporaryDirectory(prefix="synthetic-measured-extractor-") as temporary:
        root = Path(temporary)
        sources = {family: fixture(root / family, family) for family in SOURCES}
        results = {}
        for family, source in sources.items():
            before = snapshot(source)
            result = extractor.extract_run(source, fixture_mode=True)
            verify_result(result, family)
            require(snapshot(source) == before, "extraction changed an input file or identity")
            results[family] = result
        source = sources["rank-sector"]
        result = results["rank-sector"]
        mutations: list[tuple[str, Callable[[Path], Any]]] = [
            (
                "not an admitted",
                lambda directory: change_json(
                    directory, "record.json", lambda record: record["budget_plan"].__setitem__("admitted", False)
                ),
            ),
            (
                "source is modified",
                lambda directory: change_json(
                    directory, "record.json", lambda record: record["code_commit"].__setitem__("sources_modified", True)
                ),
            ),
            (
                "approval consumption",
                lambda directory: change_json(
                    directory, "record.json", lambda record: record["approval_consumed"].__setitem__("run", "other")
                ),
            ),
            (
                "approved record has mismatches",
                lambda directory: change_json(
                    directory,
                    "record.json",
                    lambda record: record["approved_record"].__setitem__("mismatches", ["changed"]),
                ),
            ),
            (
                "submission is incomplete",
                lambda directory: change_json(
                    directory, "record.json", lambda record: record["submission"].__setitem__("complete", False)
                ),
            ),
            ("input hash mismatch", lambda directory: (directory / "isa.qpy").write_bytes(b"altered archive")),
            (
                "input hash mismatch",
                lambda directory: raw_mutation(
                    directory, lambda raw: raw.__setitem__("pub_name", "altered"), rehash=False
                ),
            ),
            (
                "raw PUB identity",
                lambda directory: raw_mutation(
                    directory, lambda raw: raw.__setitem__("pub_name", "altered"), rehash=True
                ),
            ),
            (
                "raw shot count",
                lambda directory: raw_mutation(
                    directory,
                    lambda raw: next(iter(raw["registers"].values())).__setitem__("num_shots", 1),
                    rehash=True,
                ),
            ),
            (
                "vector length",
                lambda directory: raw_mutation(
                    directory, lambda raw: next(iter(raw["registers"].values()))["bitstrings"].pop(), rehash=True
                ),
            ),
            (
                "invalid raw bits",
                lambda directory: raw_mutation(
                    directory,
                    lambda raw: next(iter(raw["registers"].values()))["bitstrings"].__setitem__(0, "x"),
                    rehash=True,
                ),
            ),
            (
                "raw register coverage",
                lambda directory: raw_mutation(
                    directory, lambda raw: raw["registers"].pop(next(iter(raw["registers"]))), rehash=True
                ),
            ),
            (
                "collected marginal differs",
                lambda directory: change_json(
                    directory,
                    "collect.json",
                    lambda collected: next(iter(collected[0]["family_measurements"].values())).__setitem__(
                        "replica_probabilities", [[1.0, 0.0, 0.0, 0.0]]
                    ),
                ),
            ),
            (
                "family header member coverage",
                lambda directory: change_json(
                    directory,
                    "collect.json",
                    lambda collected: collected[0]["family_measurements"].pop(
                        next(iter(collected[0]["family_measurements"]))
                    ),
                ),
            ),
            (
                "replay status differs",
                lambda directory: change_json(
                    directory,
                    "collect.json",
                    lambda collected: next(iter(collected[0]["family_measurements"].values())).__setitem__(
                        "replay_status", "execution_window_unavailable"
                    ),
                ),
            ),
            (
                "endpoint intervals",
                lambda directory: change_json(
                    directory,
                    "collect.json",
                    lambda collected: collected[0]["family_analysis"]["observables"][0].__setitem__("lo", -100),
                ),
            ),
            (
                "settled raw usage",
                lambda directory: change_json(
                    directory,
                    "collect.json",
                    lambda collected: next(iter(collected[0]["jobs"].values()))["usage"].__setitem__(
                        "qpu_charge_time_seconds", "999"
                    ),
                ),
            ),
        ]
        for index, (fragment, mutation) in enumerate(mutations):
            directory = root / f"mutant-{index}"
            shutil.copytree(source, directory)
            mutation(directory)
            before = snapshot(directory)
            rejected(partial(extractor.extract_run, directory, fixture_mode=True), fragment)
            require(snapshot(directory) == before, "rejected mutant changed its copied input")
            rejected_mutants += 1
        ripple_mutant = root / "mutant-sign"
        shutil.copytree(sources["ripple"], ripple_mutant)

        def wrong_sign(record: dict[str, Any]) -> None:
            item = next(item for item in record["family_configuration"]["members"].values() if item["role"] == "atlas")
            item["sign"] *= -1

        change_json(ripple_mutant, "record.json", wrong_sign)
        rejected(lambda: extractor.extract_run(ripple_mutant, fixture_mode=True), "certified box-kite sign")
        rejected_mutants += 1

        hidden_marker = root / "hidden-fixture-marker"
        shutil.copytree(source, hidden_marker)
        change_json(hidden_marker, "record.json", lambda record: record.pop("evidence_kind"))
        rejected(lambda: extractor.extract_run(hidden_marker), "acquisition marker differs")
        rejected_mutants += 1
        probe_mutant = root / "mutant-probe"
        shutil.copytree(source, probe_mutant)
        change_json(
            probe_mutant,
            "record.json",
            lambda record: record["family_configuration"]["sectors"][0]["probes"][0].__setitem__(
                "coordinates", [2, 0, 0, 0]
            ),
        )
        rejected(lambda: extractor.extract_run(probe_mutant, fixture_mode=True), "certified frame")
        rejected_mutants += 1
        straddled = root / "straddled-calibration"
        shutil.copytree(source, straddled)

        def straddle(collected: list[dict[str, Any]]) -> None:
            for item in collected[0]["family_measurements"].values():
                item["execution"]["calibration_changed_during_shots"] = True
                item.update(replay_status="calibration_changed_during_shots", replayed_replica_probabilities=None)
            for group in collected[1:]:
                for execution in group["executed"].values():
                    execution["calibration_changed_during_shots"] = True
            collected[0]["family_analysis"] = {"withheld": "the group's PUBs did not all run under one calibration"}

        change_json(straddled, "collect.json", straddle)
        straddled_result = extractor.extract_run(straddled, fixture_mode=True)
        require("withheld" in straddled_result["endpoint_analysis"], "straddled calibration acquired inference")
        require(
            all(row["hardware_minus_execution_replay"] is None for row in straddled_result["members"].values()),
            "straddled calibration acquired a replay residual",
        )
        unavailable = root / "missing-optional"
        shutil.copytree(source, unavailable)

        def remove_optional(collected: list[dict[str, Any]]) -> None:
            collected[0].pop("family_analysis")
            for item in collected[0]["family_measurements"].values():
                item["execution"].update(start=None, stop=None, calibration=None, calibration_changed_during_shots=None)
                item.update(replay_status="execution_window_unavailable", replayed_replica_probabilities=None)
            for group in collected[1:]:
                for execution in group["executed"].values():
                    execution.update(start=None, stop=None, calibration=None, calibration_changed_during_shots=None)
            for job in collected[0]["jobs"].values():
                job["usage"].update(usage_status="pending", qpu_charge_time_seconds=None)

        change_json(unavailable, "collect.json", remove_optional)
        absent = extractor.extract_run(unavailable, fixture_mode=True)
        require(absent["throughput"]["rates_per_charged_second"] is None, "unsettled charge produced a rate")
        require("withheld" in absent["endpoint_analysis"], "absent endpoint analysis was invented")
        require(
            all(row["hardware_minus_execution_replay"] is None for row in absent["members"].values()),
            "missing replay fabricated residuals",
        )

        output = root / "portable.json"
        extractor.validate_output(source, output)
        extractor.write_new(output, extractor.canonical(result))
        require(extractor.read_artifact(output) == result, "portable read differs")
        before_output = output.read_bytes()
        rejected(lambda: extractor.write_new(output, b"replacement"), "File exists")
        require(output.read_bytes() == before_output, "atomic new output replaced retained content")
        tampered = root / "tampered.json"
        payload = copy.deepcopy(result)
        payload["family"] = "altered"
        write(tampered, payload)
        rejected(lambda: extractor.read_artifact(tampered), "payload hash")
        aliases = [source, source / "record.json", source / "new.json"]
        symbolic = root / "symbolic-run"
        symbolic.symlink_to(source, target_is_directory=True)
        aliases.append(symbolic / "record.json")
        linked = root / "input-hardlink.json"
        linked.hardlink_to(source / "record.json")
        aliases.append(linked)
        for alias in aliases:
            for check in (False, True):
                before = snapshot(source)
                rejected(partial(extractor.validate_output, source, alias, check=check), "output")
                require(snapshot(source) == before, "alias rejection changed an input")
                arguments = ["extract", "--run", str(source), "--out", str(alias), *(["--check"] if check else [])]
                stderr = io.StringIO()
                with (
                    patch.object(sys, "argv", arguments),
                    patch.object(extractor, "extract_run", side_effect=RuntimeError("alias reached parsing")),
                    redirect_stderr(stderr),
                ):
                    require(extractor.main() == 1 and "output" in stderr.getvalue(), "CLI alias rejection failed")
                require(snapshot(source) == before, "CLI alias rejection changed an input")
        cli = subprocess.run(
            [sys.executable, str(Path(extractor.__file__)), "--run", str(source), "--out", str(root / "cli.json")],
            capture_output=True,
            text=True,
            check=False,
        )
        require(
            cli.returncode == 1 and "synthetic fixture" in cli.stderr and not (root / "cli.json").exists(),
            "public CLI admitted fixture data",
        )
        with patch.object(extractor, "extract_run", return_value=result):
            for _check in (True,):
                before = snapshot(root)
                with patch.object(sys, "argv", ["extract", "--run", str(source), "--out", str(output), "--check"]):
                    require(extractor.main() == 0, "CLI check failed")
                require(snapshot(root) == before, "check mode changed inputs or output")
            fresh = root / "new-portable.json"
            with patch.object(sys, "argv", ["extract", "--run", str(source), "--out", str(fresh)]):
                require(extractor.main() == 0 and fresh.read_bytes() == before_output, "CLI atomic write failed")
            fresh.write_bytes(b"different")
            with (
                patch.object(sys, "argv", ["extract", "--run", str(source), "--out", str(fresh), "--check"]),
                redirect_stderr(io.StringIO()),
            ):
                require(
                    extractor.main() == 1 and fresh.read_bytes() == b"different", "mismatching check rewrote output"
                )
        print(
            json.dumps(
                {
                    "status": "pass",
                    "evidence_kind": extractor.FIXTURE_MARKER,
                    "families": {family: len(value["members"]) for family, value in results.items()},
                    "rejected_mutants": rejected_mutants,
                    "physical_qpu_jobs": 0,
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
