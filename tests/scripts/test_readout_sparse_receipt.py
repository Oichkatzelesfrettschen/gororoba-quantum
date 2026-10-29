"""Verify anchored sparse-projection receipts and QPY measurement wiring."""

import fcntl
import hashlib
import io
import json
import multiprocessing
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
import readout_sparse_receipt as verifier
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy

import live_run
from live_run import LiveRunError, snapshot_metrics, write_raw_result


def encode(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def test_collection_source_identity_accepts_legacy_and_rejects_mutations() -> None:
    sources = {"collector.py": "a" * 64}
    source_digest = digest((json.dumps(sources, sort_keys=True, indent=1) + "\n").encode())
    verifier.validate_collection_sources({})
    verifier.validate_collection_sources({"collection_source_sha256": sources, "collection_digest": source_digest})
    for invalid in (
        {"collection_source_sha256": sources},
        {"collection_digest": source_digest},
        {"collection_source_sha256": {}, "collection_digest": source_digest},
        {"collection_source_sha256": {"collector.py": "invalid"}, "collection_digest": source_digest},
        {"collection_source_sha256": sources, "collection_digest": "0" * 64},
    ):
        with pytest.raises(ValueError, match="collector source"):
            verifier.validate_collection_sources(invalid)


def fixture(width: int = 3, swapped: bool = False) -> tuple[dict[str, bytes], dict[str, object]]:
    quantum = QuantumRegister(width, "q")
    first = ClassicalRegister(width - 1, "a")
    second = ClassicalRegister(1, "b")
    circuit = QuantumCircuit(quantum, first, second, name="actor-active")
    for bit in range(width - 1):
        circuit.measure(quantum[bit], first[bit])
    circuit.measure(quantum[width - 1], second[0])
    if swapped:
        circuit = QuantumCircuit(quantum, first, second, name="actor-active")
        circuit.measure(quantum[2], first[0])
        circuit.measure(quantum[1], first[1])
        circuit.measure(quantum[0], second[0])
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    qpy_bytes = buffer.getvalue()
    manifest = {
        "schema": "readout-sparse-projection-v1",
        "condition": "active-ground",
        "pub_name": "actor-active",
        "pub_index": 0,
        "registers": {"a": width - 1, "b": 1},
        "bits": [
            {"register": "a", "index": bit, "logical": bit, "physical": bit, "prepared": 0} for bit in range(width - 1)
        ]
        + [{"register": "b", "index": 0, "logical": width - 1, "physical": width - 1, "prepared": 0}],
        "pairs": [[0, width - 1]],
        "groups": [[0, width - 1]],
    }
    raw = {
        "pub_index": 0,
        "pub_name": "actor-active",
        "registers": {
            "a": {"num_bits": width - 1, "num_shots": 2, "bitstrings": ["0" * (width - 1), "0" * (width - 2) + "1"]},
            "b": {"num_bits": 1, "num_shots": 2, "bitstrings": ["0", "1"]},
        },
    }
    raw_bytes, manifest_bytes = encode(raw), encode(manifest)
    index_bytes = encode({"job_id": "job-1", "files": {"pub_00.json": digest(raw_bytes)}})
    receipt = {
        "schema": "readout-sparse-receipt-v1",
        "family": "actor-reporter",
        "job_id": "job-1",
        "pub_index": 0,
        "pub_name": "actor-active",
        "circuit_name": "actor-active",
        "raw_pub_filename": "pub_00.json",
        "raw_pub_sha256": digest(raw_bytes),
        "raw_index_sha256": digest(index_bytes),
        "qpy_sha256": digest(qpy_bytes),
        "manifest_sha256": digest(manifest_bytes),
    }
    return {"raw": raw_bytes, "index": index_bytes, "qpy": qpy_bytes, "manifest": manifest_bytes}, receipt


def call(data: dict[str, bytes], receipt: dict[str, object], anchor: str | None = None) -> dict:
    receipt_bytes = encode(receipt)
    return verifier.verify_and_project(
        data["raw"], data["index"], data["qpy"], data["manifest"], receipt_bytes, anchor or digest(receipt_bytes)
    )


def test_anchored_receipt_checks_cross_register_measurement_wiring() -> None:
    data, receipt = fixture()
    result = call(data, receipt)
    if result["projection"]["pair_counts"][0]["error_cells_00_01_10_11"] != [1, 0, 0, 1]:
        raise AssertionError("the retained PUB must be projected using aligned measured registers")
    if "unverified" not in result["boundary"]:
        raise AssertionError("receipt consistency must retain its independent-provenance boundary")


def test_wide_single_pub_projection_avoids_dense_distribution() -> None:
    data, receipt = fixture(width=156)
    result = call(data, receipt)
    if result["projection"]["num_shots"] != 2 or result["verified_measurements"] != 156:
        raise AssertionError("the verifier must preserve the full measured register without an exponential array")


def test_manifest_byte_and_canonical_digests_have_distinct_meanings() -> None:
    data, receipt = fixture()
    result = call(data, receipt)
    if result["manifest_bytes_sha256"] != digest(data["manifest"]):
        raise AssertionError("the receipt must bind the original manifest bytes")
    if result["manifest_bytes_sha256"] == result["projection"]["manifest_canonical_sha256"]:
        raise AssertionError("the fixture's whitespace must distinguish the byte and canonical digests")


def test_actor_label_does_not_validate_preparation_or_intervention() -> None:
    data, receipt = fixture()
    result = call(data, receipt)
    if "preparation semantics" not in result["boundary"]:
        raise AssertionError("a measurement-only circuit cannot establish an active actor intervention")


def test_actual_raw_serializer_feeds_descriptive_verifier(tmp_path) -> None:
    data, receipt = fixture(width=156)
    raw = json.loads(data["raw"])

    class BitArray:
        def __init__(self, register: dict) -> None:
            self.num_bits = register["num_bits"]
            self.num_shots = register["num_shots"]
            self.bitstrings = register["bitstrings"]

        def get_bitstrings(self) -> list[str]:
            return self.bitstrings

    class Pub:
        def __init__(self) -> None:
            self.data = {name: BitArray(register) for name, register in raw["registers"].items()}
            self.metadata: dict = {}

    class Job:
        metrics_value: dict = {}

        def metrics(self) -> dict:
            return self.metrics_value

    job = Job()
    write_raw_result(tmp_path, "job-1", job, [Pub()], ["actor-active"])
    directory = tmp_path / "raw" / "job-1"
    acquisition_index = (directory / "acquisition-index.json").read_bytes()
    data["raw"] = (directory / "pub_00.json").read_bytes()
    data["index"] = (directory / "index.json").read_bytes()
    receipt["raw_pub_sha256"] = digest(data["raw"])
    receipt["raw_index_sha256"] = digest(data["index"])
    result = call(data, receipt)
    if result["projection"]["pair_counts"][0]["error_cells_00_01_10_11"] != [1, 0, 0, 1]:
        raise AssertionError("the serializer and verifier must preserve cross-register shot positions")
    job.metrics_value = {"usage": 1}
    snapshot_metrics(tmp_path, "job-1", job)
    if (directory / "acquisition-index.json").read_bytes() != acquisition_index:
        raise AssertionError("metrics updates must preserve the acquisition index bytes")
    receipt["raw_index_sha256"] = digest(acquisition_index)
    data["index"] = acquisition_index
    call(data, receipt)
    data["index"] = (directory / "index.json").read_bytes()
    with pytest.raises(ValueError, match="raw_index_sha256"):
        call(data, receipt)
    (directory / "acquisition-index.json").write_text("altered\n")
    with pytest.raises(LiveRunError, match="immutable acquisition snapshot"):
        write_raw_result(tmp_path, "job-1", job, [Pub()], ["actor-active"])


@pytest.mark.parametrize("same_bytes", [True, False])
def test_acquisition_index_concurrent_publish_is_write_once(tmp_path, monkeypatch, same_bytes: bool) -> None:
    target = tmp_path / "acquisition-index.json"
    synchronize = threading.Barrier(2)
    link = live_run.os.link

    def concurrent_link(source, destination) -> None:
        synchronize.wait(timeout=10)
        link(source, destination)

    monkeypatch.setattr(live_run.os, "link", concurrent_link)
    payloads = ("first\n", "first\n" if same_bytes else "second\n")
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(live_run._write_once_atomically, target, payload) for payload in payloads]
        errors = []
        for future in futures:
            try:
                future.result()
            except LiveRunError as error:
                errors.append(error)
    if len(errors) != (0 if same_bytes else 1) or target.read_text() not in payloads:
        raise AssertionError("concurrent publication must keep one complete value and reject conflicts")
    if sorted(path.name for path in tmp_path.iterdir()) != [target.name]:
        raise AssertionError("concurrent publication must remove temporary files")


def test_acquisition_index_interrupted_before_publish_leaves_no_target(tmp_path, monkeypatch) -> None:
    target = tmp_path / "acquisition-index.json"

    def interrupted_link(_source, _destination) -> None:
        raise OSError("interrupted before publication")

    monkeypatch.setattr(live_run.os, "link", interrupted_link)
    with pytest.raises(OSError, match="interrupted"):
        live_run._write_once_atomically(target, "complete\n")
    if list(tmp_path.iterdir()):
        raise AssertionError("failed publication must leave no target or temporary file")


def test_raw_collector_waits_for_existing_job_lock(tmp_path) -> None:
    directory = tmp_path / "raw" / "job-1"
    directory.mkdir(parents=True)
    entered = threading.Event()

    class BitArray:
        num_bits = 1
        num_shots = 1

        def get_bitstrings(self) -> list[str]:
            entered.set()
            return ["0"]

    class Pub:
        data = {"a": BitArray()}
        metadata: dict = {}

    class Job:
        def metrics(self) -> dict:
            return {}

    with (directory / ".collection.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(write_raw_result, tmp_path, "job-1", Job(), [Pub()], ["actor-active"])
            try:
                if entered.wait(timeout=0.2):
                    raise AssertionError("the collector read results while the job lock was held")
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)
            future.result(timeout=10)
    if not entered.is_set():
        raise AssertionError("the collector must resume when the job lock is released")


@pytest.mark.parametrize("same_bytes", [True, False])
def test_concurrent_raw_collectors_preserve_indexed_bytes(tmp_path, same_bytes: bool) -> None:
    class BitArray:
        num_bits = 1
        num_shots = 1

        def __init__(self, value: str) -> None:
            self.value = value

        def get_bitstrings(self) -> list[str]:
            return [self.value]

    class Pub:
        metadata: dict = {}

        def __init__(self, value: str) -> None:
            self.data = {"a": BitArray(value)}

    class Job:
        def metrics(self) -> dict:
            return {}

    values = ("0", "0" if same_bytes else "1")
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(write_raw_result, tmp_path, "job-1", Job(), [Pub(value)], ["actor-active"]) for value in values
        ]
        failures = []
        for future in futures:
            try:
                future.result()
            except LiveRunError as error:
                failures.append(error)
    if len(failures) != (0 if same_bytes else 1):
        raise AssertionError("identical concurrent collections must succeed and conflicting collections must refuse")
    directory = tmp_path / "raw" / "job-1"
    index = json.loads((directory / "acquisition-index.json").read_bytes())
    for name, expected in index["files"].items():
        if digest((directory / name).read_bytes()) != expected:
            raise AssertionError("a published acquisition index must match every retained result file")


def test_interrupted_raw_collection_replays_without_replacing_raw(tmp_path, monkeypatch) -> None:
    class Pub:
        data: dict = {}
        metadata: dict = {}

    class Job:
        def metrics(self) -> dict:
            return {}

    publish = live_run._write_once_atomically

    def interrupted(target, text) -> None:
        if target.name == "acquisition-index.json":
            raise OSError("interrupted before acquisition index")
        publish(target, text)

    with monkeypatch.context() as patch:
        patch.setattr(live_run, "_write_once_atomically", interrupted)
        with pytest.raises(OSError, match="interrupted"):
            write_raw_result(tmp_path, "job-1", Job(), [Pub()], ["actor-active"])
    directory = tmp_path / "raw" / "job-1"
    raw = (directory / "pub_00.json").read_bytes()
    if (directory / "acquisition-index.json").exists():
        raise AssertionError("interrupted publication must not leave a partial index")
    write_raw_result(tmp_path, "job-1", Job(), [Pub()], ["actor-active"])
    if (directory / "pub_00.json").read_bytes() != raw:
        raise AssertionError("recollection must preserve raw bytes written before interruption")


def test_killed_raw_collector_releases_lock_and_recovers(tmp_path, monkeypatch) -> None:
    class Pub:
        data: dict = {}
        metadata: dict = {}

    class Job:
        def metrics(self) -> dict:
            return {}

    publish = live_run._write_once_atomically

    def kill_before_index(target, text) -> None:
        if target.name == "acquisition-index.json":
            os._exit(73)
        publish(target, text)

    with monkeypatch.context() as patch:
        patch.setattr(live_run, "_write_once_atomically", kill_before_index)
        process = multiprocessing.get_context("fork").Process(
            target=write_raw_result, args=(tmp_path, "job-1", Job(), [Pub()], ["actor-active"])
        )
        process.start()
        process.join(timeout=10)
        if process.is_alive():
            process.kill()
            process.join()
            raise AssertionError("the interrupted collector must terminate")
        if process.exitcode != 73:
            raise AssertionError("the child must exit immediately before index publication")
    directory = tmp_path / "raw" / "job-1"
    raw = (directory / "pub_00.json").read_bytes()
    if (directory / "acquisition-index.json").exists():
        raise AssertionError("the killed process must not publish a partial index")
    write_raw_result(tmp_path, "job-1", Job(), [Pub()], ["actor-active"])
    index = json.loads((directory / "acquisition-index.json").read_bytes())
    if (directory / "pub_00.json").read_bytes() != raw or index["files"]["pub_00.json"] != digest(raw):
        raise AssertionError("recollection must release the abandoned lock and bind the original raw bytes")


@pytest.mark.parametrize("mutation", ["anchor", "raw", "index_digest", "manifest", "family", "missing_binding"])
def test_receipt_rejects_missing_or_corrupted_bindings(mutation: str) -> None:
    data, receipt = fixture()
    if mutation == "raw":
        data["raw"] += b" "
    elif mutation == "index_digest":
        index = json.loads(data["index"])
        index["files"]["pub_00.json"] = "0" * 64
        data["index"] = encode(index)
        receipt["raw_index_sha256"] = digest(data["index"])
    elif mutation == "manifest":
        data["manifest"] += b" "
    elif mutation == "family":
        receipt["family"] = "other"
    elif mutation == "missing_binding":
        del receipt["qpy_sha256"]
    with pytest.raises(ValueError):
        call(data, receipt, "0" * 64 if mutation == "anchor" else None)


def test_receipt_rejects_qpy_with_swapped_measurement_destinations() -> None:
    data, receipt = fixture(swapped=True)
    with pytest.raises(ValueError, match="measurement"):
        call(data, receipt)


@pytest.mark.parametrize("mutation", ["duplicate_name", "hidden_operation", "repeated_measurement"])
def test_receipt_rejects_ambiguous_or_unsupported_qpy(mutation: str) -> None:
    data, receipt = fixture()
    circuit = qpy.load(io.BytesIO(data["qpy"]))[0]
    circuits = [circuit]
    if mutation == "duplicate_name":
        circuits.append(circuit.copy())
    elif mutation == "hidden_operation":
        circuit.h(0)
    else:
        circuit.measure(0, 0)
    buffer = io.BytesIO()
    qpy.dump(circuits, buffer)
    data["qpy"] = buffer.getvalue()
    receipt["qpy_sha256"] = digest(data["qpy"])
    with pytest.raises(ValueError):
        call(data, receipt)


def test_receipt_rejects_duplicate_json_fields_even_if_digest_matches() -> None:
    data, receipt = fixture()
    data["manifest"] = data["manifest"].replace(b'"condition":', b'"condition":"other", "condition":', 1)
    receipt["manifest_sha256"] = digest(data["manifest"])
    with pytest.raises(ValueError, match="duplicate"):
        call(data, receipt)


def test_receipt_rejects_qpy_circuit_name_distinct_from_raw_pub_name() -> None:
    data, receipt = fixture()
    circuit = qpy.load(io.BytesIO(data["qpy"]))[0]
    circuit.name = "another-circuit"
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    data["qpy"] = buffer.getvalue()
    receipt["qpy_sha256"] = digest(data["qpy"])
    receipt["circuit_name"] = "another-circuit"
    with pytest.raises(ValueError, match="name"):
        call(data, receipt)
