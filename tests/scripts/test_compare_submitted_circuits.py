"""A comparison successor reuses validated rows and retrieves only missing inputs."""

import copy
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import compare_submitted_circuits as comparison
import pytest


def fixture_rows(tmp_path, monkeypatch):
    from qiskit import QuantumCircuit, qpy

    circuit = QuantumCircuit(1, name="reference")
    circuit.x(0)
    path = tmp_path / "isa.qpy"
    with path.open("wb") as stream:
        qpy.dump([circuit], stream)
    jobs = [{"job_id": name, "run": f"results/live/{name}", "pub_count": 1} for name in ("seeded", "missing")]
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"jobs": jobs}))
    script = tmp_path / "scripts/compare_submitted_circuits.py"
    script.parent.mkdir()
    script.write_bytes(Path(comparison.__file__).read_bytes())
    repository = Path(comparison.__file__).resolve().parents[1]
    for name in comparison.DIRECT_DEPENDENCIES:
        destination = tmp_path / name
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes((repository / name).read_bytes())
    monkeypatch.setattr(comparison, "ROOT", tmp_path)
    monkeypatch.setattr(comparison, "AUDIT", audit)
    monkeypatch.setattr(comparison, "expected_order", lambda job: (path, ["reference"]))
    row = {
        "job_id": "seeded",
        "run": "results/live/seeded",
        "retained_file": "isa.qpy",
        "retained_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "order_source": "record.json submission.jobs[].pubs",
        "expected_pubs": ["reference"],
        "items": 1,
        "item_kinds": ["CircuitItem"],
        "positional_matches": 1,
        "submitted_qpy_sha256": [comparison.qpy_digest(circuit)],
    }
    seed = tmp_path / "seed.json"
    seed.write_text(json.dumps({"schema": comparison.SCHEMA, "jobs": [row]}))
    return seed, row, circuit


def test_existing_destination_refuses_before_service(tmp_path, monkeypatch) -> None:
    output = tmp_path / "comparison.json"
    output.write_text("retained")

    def forbidden(*args):
        raise RuntimeError("service construction must remain unreachable")

    monkeypatch.setattr(comparison.ibm_account, "open_service", forbidden)
    with pytest.raises(SystemExit, match="already exists"):
        comparison.write(output)
    if output.read_text() != "retained":
        raise RuntimeError("an occupied comparison path changed")


def test_successor_reuses_seed_and_binds_only_missing_reads(tmp_path, monkeypatch) -> None:
    from qiskit_ibm_runtime.quantum_program import CircuitItem

    seed, row, circuit = fixture_rows(tmp_path, monkeypatch)
    prior = seed.read_bytes()
    reads = []

    def job(job_id):
        reads.append(job_id)
        return SimpleNamespace(inputs={"quantum_program": SimpleNamespace(items=[CircuitItem(circuit)])})

    service = SimpleNamespace(job=job)
    monkeypatch.setattr(comparison.ibm_account, "open_service", lambda constructor: service)
    monkeypatch.setitem(sys.modules, "live_run", SimpleNamespace(_instance_hash=lambda service: "fixture"))
    output = tmp_path / "successor.json"
    comparison.write(output, seed)
    retained = json.loads(output.read_text())
    if reads != ["missing"] or retained["jobs"][0] != row or seed.read_bytes() != prior:
        raise RuntimeError("the successor must preserve its seed and retrieve only missing job inputs")
    comparison.check(output)
    retained["provenance"]["retrieved_job_ids"] = ["seeded"]
    output.write_text(json.dumps(retained))
    with pytest.raises(SystemExit, match="retrieved job identities"):
        comparison.check(output)


def test_bad_seed_stops_before_service(tmp_path, monkeypatch) -> None:
    seed, row, _ = fixture_rows(tmp_path, monkeypatch)
    row["submitted_qpy_sha256"] = ["0" * 64]
    seed.write_text(json.dumps({"schema": comparison.SCHEMA, "jobs": [row]}))

    def forbidden(*args):
        raise RuntimeError("a malformed seed must remain offline")

    monkeypatch.setattr(comparison.ibm_account, "open_service", forbidden)
    with pytest.raises(SystemExit, match="submitted items"):
        comparison.write(tmp_path / "successor.json", seed)


def test_publication_preserves_concurrently_occupied_path(tmp_path) -> None:
    output = tmp_path / "comparison.json"
    output.write_text("retained concurrent acquisition")
    with pytest.raises(FileExistsError):
        comparison._retain(output, {"jobs": []})
    if output.read_text() != "retained concurrent acquisition":
        raise RuntimeError("exclusive publication replaced concurrent retained bytes")


def test_pooled_validation_preserves_serial_results_and_first_failure(tmp_path, monkeypatch) -> None:
    _, row, _ = fixture_rows(tmp_path, monkeypatch)
    second = {**row, "job_id": "missing", "run": "results/live/missing"}
    rows = [row, second]
    audited = {job["job_id"]: job for job in comparison.audit_jobs()}
    for workers in ("1", "2"):
        monkeypatch.setenv("GOROROBA_WORKERS", workers)
        comparison._check_rows(rows, audited)
        broken = copy.deepcopy(rows)
        for entry in broken:
            entry["positional_matches"] = 0
        with pytest.raises(SystemExit, match="seeded: an item differs"):
            comparison._check_rows(broken, audited)


def test_offline_rebind_preserves_service_origin_and_checks_archived_collector(tmp_path, monkeypatch) -> None:
    from qiskit_ibm_runtime.quantum_program import CircuitItem

    seed, _, circuit = fixture_rows(tmp_path, monkeypatch)
    service = SimpleNamespace(
        job=lambda job_id: SimpleNamespace(inputs={"quantum_program": SimpleNamespace(items=[CircuitItem(circuit)])})
    )
    monkeypatch.setattr(comparison.ibm_account, "open_service", lambda constructor: service)
    monkeypatch.setitem(sys.modules, "live_run", SimpleNamespace(_instance_hash=lambda service: "fixture"))
    predecessor = tmp_path / "service-comparison.json"
    comparison.write(predecessor, seed)
    predecessor_bytes = predecessor.read_bytes()
    source = tmp_path / "scripts/compare_submitted_circuits.py"
    snapshot = tmp_path / "collector.txt"
    snapshot.write_bytes(source.read_bytes())
    source.write_text(source.read_text() + "\n# replaced fixture collector\n")

    def forbidden(*args):
        raise RuntimeError("offline validation must not open the service")

    monkeypatch.setattr(comparison.ibm_account, "open_service", forbidden)
    successor = tmp_path / "offline-comparison.json"
    comparison.rebind(successor, predecessor, snapshot)
    comparison.check(successor)
    old, new = json.loads(predecessor_bytes), json.loads(successor.read_text())
    if old["jobs"] != new["jobs"] or old["provenance"]["retrieved_utc"] != new["provenance"]["retrieved_utc"]:
        raise RuntimeError("offline validation must preserve real service rows and retrieval time")
    if predecessor.read_bytes() != predecessor_bytes:
        raise RuntimeError("offline validation changed its predecessor")
    retained = successor.read_bytes()
    new["provenance"]["sources_sha256"].pop("gororoba_quantum/parallel.py")
    successor.write_text(json.dumps(new))
    with pytest.raises(SystemExit, match="provenance source identities differ"):
        comparison.check(successor)
    successor.write_bytes(retained)
    dependency = tmp_path / "gororoba_quantum/parallel.py"
    dependency_bytes = dependency.read_bytes()
    dependency.write_text("changed repository dependency")
    with pytest.raises(SystemExit, match="provenance source changed"):
        comparison.check(successor)
    dependency.write_bytes(dependency_bytes)
    snapshot.write_text("wrong historical collector")
    with pytest.raises(SystemExit, match="provenance source changed"):
        comparison.check(successor)
