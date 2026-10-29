"""Independent projector oracle and deterministic circuit/shot contracts."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from qi_projector_geometry import analyze_shots, build_batches, circuit, ideal_moments, validate_backend, write_fresh


def backend() -> dict:
    evidence = Path(__file__).resolve().parents[2] / "docs/evidence/tuna-projector-geometry"
    tuna = json.loads((evidence / "backend-observation.json").read_text())
    qx = json.loads((evidence / "qx-backend-observation.json").read_text())
    return {
        "name": tuna["name"],
        "identifier": tuna["identifier"],
        "id": tuna["id"],
        "qx_identifier": qx["identifier"],
        "qx_backend_type_id": qx["id"],
        "nqubits": tuna["nqubits"],
        "gates": tuna["gateset"],
        "coupling_map": tuna["topology"],
    }


def test_retained_backend_rejects_absent_edge() -> None:
    validate_backend(backend())
    with pytest.raises(ValueError, match="supported CZ edges"):
        validate_backend(backend(), ((1, 4, 8), (10, 11, 14), (3, 6, 9)))


@pytest.mark.parametrize("angle", [-45, 0, 45, 90])
@pytest.mark.parametrize("mutation", [False, True])
def test_independent_projector(angle: int, mutation: bool) -> None:
    identity = np.eye(2)
    pauli_z = np.diag([1, -1])
    pauli_x = np.array([[0, 1], [1, 0]])
    radians = np.deg2rad(0 if mutation else angle)
    axis = np.cos(radians) * pauli_z + np.sin(radians) * pauli_x
    projector = (np.eye(4) + np.kron(axis, pauli_z)) / 2
    input_state = np.array([1, 1, 0, 0]) / np.sqrt(2)
    # Append an ancilla basis vector to make the herald subspace explicit.
    state = np.kron(projector @ input_state, np.array([1, 0]))
    z_accept = np.kron(np.kron(np.diag([1, 0]), identity), identity)
    x_observable = np.kron(np.kron(pauli_x, identity), identity)
    actual = [state @ state, state @ z_accept @ state, state @ x_observable @ state]
    expected = ideal_moments(angle, mutation=mutation)
    np.testing.assert_allclose(
        actual, [expected["herald"], expected["z_joint"], expected["x_signed_joint"]], atol=1e-15
    )


def test_batches_and_fresh_output(tmp_path: Path) -> None:
    files = build_batches(backend())
    if files != build_batches(backend()):
        raise AssertionError("generation changed")
    for name in ("tuna-qualification", "qx-terminal"):
        manifest = json.loads(files[f"{name}/cases.json"])
        for entry in manifest["circuits"]:
            digest = hashlib.sha256(files[f"{name}/{entry['file']}"].encode()).hexdigest()
            if digest != entry["sha256"]:
                raise AssertionError("hash mismatch")
    destination = tmp_path / "cases"
    write_fresh(destination, files)
    with pytest.raises(FileExistsError):
        write_fresh(destination, files)


def test_circuit_modes() -> None:
    early = circuit(wait_cycles=3)
    if "b[17] = measure q[4]" not in early or "wait(3) q" not in early:
        raise AssertionError("early context missing")
    if "b[17]" in circuit(mode="sequential"):
        raise AssertionError("deferred circuit contains early measurement")
    with pytest.raises(ValueError):
        circuit(compact=True)
    with pytest.raises(ValueError):
        circuit(angles=(0, 43, 90))
    with pytest.raises(ValueError):
        circuit(wait_cycles=-1)
    invalid = backend()
    invalid["coupling_map"] = []
    with pytest.raises(ValueError):
        validate_backend(invalid)


def metadata() -> dict:
    return {
        "width": 4,
        "replicas": [{"data": 0, "herald": 1, "final_herald": 1}, {"data": 2, "herald": 3, "final_herald": 3}],
    }


def test_joint_moments_and_empty_herald() -> None:
    correlated = analyze_shots(["0000", "1010"], metadata(), block_size=1)
    opposite = analyze_shots(["0010", "1000"], metadata())
    if correlated["replicas"] != opposite["replicas"]:
        raise AssertionError("first moments should agree")
    if correlated["cross_replica_joint_moments"] == opposite["cross_replica_joint_moments"]:
        raise AssertionError("second moments should differ")
    empty = analyze_shots(["1111"], metadata())
    if empty["replicas"][0]["conditional_zero"] is not None:
        raise AssertionError("empty herald conditional is undefined")
    if correlated["blocks"][0]["joint_zero"] != [1.0, 1.0]:
        raise AssertionError("contiguous block summary differs")


@pytest.mark.parametrize("shots", [[], ["2"], ["000"], ["000x"]])
def test_bad_shots(shots: list[str]) -> None:
    with pytest.raises(ValueError):
        analyze_shots(shots, metadata())


def test_bad_metadata() -> None:
    invalid = metadata()
    invalid["replicas"][0]["data"] = 9
    with pytest.raises(ValueError):
        analyze_shots(["0000"], invalid)


@pytest.mark.parametrize("angle", [-45, 0, 45, 90])
def test_full_three_qubit_unitary(angle: int) -> None:
    radians = np.deg2rad(angle)
    identity = np.eye(2)
    rotation = np.array([[np.cos(radians / 2), -np.sin(radians / 2)], [np.sin(radians / 2), np.cos(radians / 2)]])
    # Tensor order is A, B, C; parity toggles C conditioned on each data bit.
    parity = np.zeros((8, 8))
    for basis in range(8):
        a, b, c = (basis >> 2) & 1, (basis >> 1) & 1, basis & 1
        parity[(a << 2) | (b << 1) | (c ^ a ^ b), basis] = 1
    input_state = np.array([1, 0, 1, 0, 0, 0, 0, 0]) / np.sqrt(2)
    state = (
        np.kron(np.kron(rotation, identity), identity)
        @ parity
        @ np.kron(np.kron(rotation.T, identity), identity)
        @ input_state
    )
    herald_projector = np.kron(np.eye(4), np.diag([1, 0]))
    heralded = herald_projector @ state
    z_accept = np.kron(np.diag([1, 0]), np.eye(4))
    x_observable = np.kron(np.array([[0, 1], [1, 0]]), np.eye(4))
    expected = ideal_moments(angle)
    np.testing.assert_allclose(
        [heralded @ heralded, heralded @ z_accept @ heralded, heralded @ x_observable @ heralded],
        [expected["herald"], expected["z_joint"], expected["x_signed_joint"]],
        atol=1e-15,
    )


def test_signed_endpoint_and_disagreement() -> None:
    config = {"width": 3, "replicas": [{"data": 0, "herald": 1, "final_herald": 2, "endpoint": "x"}]}
    result = analyze_shots(["000", "101", "110"], config)["replicas"][0]
    np.testing.assert_allclose(
        [result["herald"], result["joint_zero"], result["signed_joint"], result["herald_disagreement"]],
        [2 / 3, 1 / 3, 0, 2 / 3],
    )


def test_manifest_bit_order_and_provenance(tmp_path: Path) -> None:
    from qi_projector_geometry import analyze_case

    files = build_batches(backend())
    write_fresh(tmp_path / "bundle", files)
    case = tmp_path / "bundle" / "tuna-qualification"
    manifest = json.loads((case / "cases.json").read_text())
    if manifest["backend_snapshot"]["sha256"] != hashlib.sha256((case / "backend.json").read_bytes()).hexdigest():
        raise AssertionError("backend snapshot digest mismatch")
    (case / "raw").mkdir()
    for entry in manifest["circuits"]:
        metadata = entry["analysis_metadata"]
        # b[17]=0 heralds replica zero; b[1]=1 gives its negative X outcome.
        bits = ["0"] * 20
        bits[19 - 1] = "1"
        bits[19 - 18] = "1"
        shot = "".join(bits)
        summary = analyze_shots([shot], metadata)
        if summary["replicas"][0]["signed_joint_sum"] != -1:
            raise AssertionError("data bit was decoded in the wrong order")
        if summary["replicas"][1]["herald_count"] != 0:
            raise AssertionError("early herald bit was decoded in the wrong order")
        (case / "raw" / f"{entry['file']}.json").write_text(json.dumps([shot] * manifest["shots"]))
    outputs = analyze_case(case, case / "raw")
    if len(outputs) != 3:
        raise AssertionError("collection analysis omitted a circuit")
    report = json.loads(outputs["geometry.cq.analysis.json"])
    if report["replicas"][0]["joint_zero_count"] != 0 or report["replicas"][2]["joint_zero_count"] != manifest["shots"]:
        raise AssertionError("exact joint counts differ")
    (case / "geometry.cq").write_text("changed")
    with pytest.raises(ValueError, match="digest differs"):
        analyze_case(case, case / "raw")


def test_initialization_and_compact_metadata() -> None:
    from qi_projector_geometry import shot_metadata

    text = circuit()
    if text.index("init q") > text.index("H q"):
        raise AssertionError("initialization follows data preparation")
    metadata = shot_metadata(compact=True, endpoint="x")
    shot = "000000001"
    report = analyze_shots([shot], metadata)
    if report["replicas"][0]["signed_joint_sum"] != -1:
        raise AssertionError("QX bit zero must address the rightmost character")


def test_collection_requires_manifest_shot_count(tmp_path: Path) -> None:
    from qi_projector_geometry import analyze_case

    write_fresh(tmp_path / "bundle", build_batches(backend()))
    case = tmp_path / "bundle" / "tuna-qualification"
    (case / "raw").mkdir()
    manifest = json.loads((case / "cases.json").read_text())
    for entry in manifest["circuits"]:
        (case / "raw" / f"{entry['file']}.json").write_text(json.dumps(["0" * 20]))
    with pytest.raises(ValueError, match="raw shot count differs"):
        analyze_case(case, case / "raw")
