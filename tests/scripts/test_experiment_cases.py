"""Provider cases preserve operators, output labels, controls and acquisition boundaries."""

import hashlib
import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from experiment_cases import Budgets, _build_setting, _qd_cases, build, check, optical_seeds, self_test, settings
from hypercomplex_cases import qi_native, write_files


@pytest.fixture
def budgets() -> Budgets:
    return Budgets(1024, 1024, 1024, 2048, 60.0, 2.0)


def test_reference_settings_cover_all_inputs_and_controls() -> None:
    self_test()
    rows = settings("mub-six")
    if len({(row["preparation_basis"], row["measurement_basis"], row["input_column"]) for row in rows}) != 54:
        raise RuntimeError("MUB settings must cover all ordered basis pairs and six inputs")
    for row in settings("quarter-mass"):
        from qiskit.quantum_info import Operator

        np.testing.assert_allclose(Operator(row["source_circuit"]).data, row["matrix"], atol=1e-12)


def test_deterministic_native_compilation_retains_layout_and_rounded_operator() -> None:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    row = settings("mub-six")[7]
    first = qi_native(row["matrix"], row["name"], physical_qubits=(11, 13, 14), deterministic=True)
    second = qi_native(row["matrix"], row["name"], physical_qubits=(11, 13, 14), deterministic=True)
    if first != second or first["seed_source"] != "deterministic-no-randomized-passes":
        raise RuntimeError("fixed routing must reproduce source and operator without stochastic seeds")
    local = {physical: index for index, physical in enumerate(first["placement"])}
    reconstructed = QuantumCircuit(3)
    for line in first["source"].splitlines():
        match = re.fullmatch(r"(Rx|Ry|Rz)\(([^)]+)\) q\[(\d+)\]", line)
        if match:
            gate, value, physical = match.groups()
            angle = float(value)
            np.testing.assert_allclose(angle / (np.pi / 36), round(angle / (np.pi / 36)), atol=1e-12)
            getattr(reconstructed, gate.lower())(angle, local[int(physical)])
        match = re.fullmatch(r"CZ q\[(\d+)\], q\[(\d+)\]", line)
        if match:
            reconstructed.cz(*(local[int(value)] for value in match.groups()))
    final = [local[physical] for physical in first["measurement_mapping"]]
    order = [sum(((basis >> logical) & 1) << physical for logical, physical in enumerate(final)) for basis in range(8)]
    held = first["native_operator"]
    np.testing.assert_allclose(
        np.asarray(Operator(reconstructed).data)[order],
        np.asarray(held["real"]) + 1j * np.asarray(held["imaginary"]),
        atol=1e-12,
    )


def test_qi_twins_bind_registers_shots_and_payloads(budgets: Budgets) -> None:
    files = _build_setting((settings("quarter-mass")[1], budgets, ("tuna", "qx")))
    for name, text in files.items():
        if not name.endswith("/cases.json"):
            continue
        manifest = json.loads(text)
        if len(manifest["circuits"]) != 3:
            raise RuntimeError("each witness batch requires two readout controls")
        for row in manifest["circuits"]:
            payload = files[str(Path(name).parent / row["file"])]
            if hashlib.sha256(payload.encode()).hexdigest() != row["sha256"]:
                raise RuntimeError("circuit bytes must match the acquisition digest")
            if row["register_width"] != 2:
                raise RuntimeError("raw register width must match the declared compact classical destination")
        science = manifest["circuits"][0]
        payload = files[str(Path(name).parent / science["file"])]
        if payload.count("barrier q\n") < 3 or "barrier q[" in payload:
            raise RuntimeError("amplification stages require joint-register barriers")
        np.testing.assert_allclose(science["native_probabilities"], [0, 0, 0, 1], atol=1e-12)
        if name.startswith("tuna/"):
            if science["measurement_mapping"] != [11, 13] or science["register_kind"] != "classical":
                raise RuntimeError("Tuna measurement destinations must preserve the physical mapping")
        elif science["measurement_mapping"] != [0, 1] or science["register_kind"] != "qubit":
            raise RuntimeError("QX twin mapping must use compact physical qubit outcomes")


def test_optical_cases_keep_all_ports_and_registered_compilation_seed(budgets: Budgets) -> None:
    import qd_platform

    files = _qd_cases(settings("mub-six")[7], budgets)
    manifest = json.loads(next(value for name, value in files.items() if name.endswith("cases.json")))
    circuit = json.loads(next(value for name, value in files.items() if name.endswith("circuit.json")))
    if circuit["input_state"] != [1] + [0] * 11 or circuit["modes"] != 12:
        raise RuntimeError("a connected source and twelve-port readout must remain explicit")
    if manifest["seed_source"] != optical_seeds()[7]["reference"]:
        raise RuntimeError("each optical mesh must carry its reserved draw index")
    qd_platform.template_experiment(manifest, circuit)
    manifest["settings"][0]["operator"]["real"][11][11] += 0.1
    with pytest.raises(qd_platform.PlatformError, match="full operator"):
        qd_platform.template_experiment(manifest, circuit)


def test_seed_allocations_are_distinct_and_follow_declared_order() -> None:
    rows = optical_seeds()
    if len(rows) != 57 or [row["index"] for row in rows] != list(range(2, 59)):
        raise RuntimeError("57 optical settings must own consecutive unused draw indices")
    if len({(row["family"], row["setting"]) for row in rows}) != 57:
        raise RuntimeError("each allocation must belong to exactly one optical setting")


def test_serialized_seed_mapping_satisfies_reserved_provenance(
    tmp_path: Path, budgets: Budgets, monkeypatch: pytest.MonkeyPatch
) -> None:
    import seed_provenance

    files = build(budgets, ("sedenion-lcu",), ("ascella",))
    text = files["seeds.json"]
    held = json.loads(text)["allocations"]
    expected = [row for row in optical_seeds() if row["family"] == "sedenion-lcu"]
    if [(row["value"], row["source"], row["index"]) for row in held] != [
        (row["seed"], row["source"], row["index"]) for row in expected
    ]:
        raise RuntimeError("serialized provenance must preserve every reserved draw value and index")
    if any("seed" in row for row in held) or len({row["index"] for row in held}) != len(held):
        raise RuntimeError("reserved value mappings require distinct allocations outside seed-literal positions")
    if seed_provenance.text_literals("seeds.json", text) != ([], []):
        raise RuntimeError("reserved mappings must remain outside the seed-position literal scanner")
    (tmp_path / "seeds.json").write_text(text)
    monkeypatch.setattr(seed_provenance, "ROOT", tmp_path)
    if seed_provenance.reserved_file("seeds.json") != ("seeds.json", (text, frozenset())):
        raise RuntimeError("reserved-file admission must read the mapping without detectable seed literals")


@pytest.mark.parametrize("case_name", ["dark", "bright", "fixture"])
def test_all_optical_sedenion_cases_extend_the_full_witness_support(case_name: str, budgets: Budgets) -> None:
    import qd_platform

    from experiment_references import sedenion_operators

    row = next(row for row in settings("sedenion-lcu") if row["name"] == case_name)
    inputs = row["support_isometry"]["input_indices"]
    outputs = row["support_isometry"]["output_indices"]
    witness = sedenion_operators()["witness"]
    restriction = witness[np.ix_(outputs, inputs)]
    identity = np.eye(len(inputs))
    np.testing.assert_allclose(restriction.conj().T @ restriction, identity, atol=1e-12)
    np.testing.assert_allclose(restriction @ restriction.conj().T, identity, atol=1e-12)
    np.testing.assert_allclose(row["optical_matrix"].conj().T @ row["optical_matrix"], identity, atol=1e-12)
    np.testing.assert_allclose(
        witness[:, inputs][[index for index in range(32) if index not in outputs]], 0, atol=1e-12
    )
    np.testing.assert_allclose(
        np.abs(row["matrix"][outputs, 0]) ** 2, np.abs(row["optical_matrix"][:, 0]) ** 2, atol=1e-12
    )
    expected_size = 8 if case_name == "fixture" else 4
    if row["optical_matrix"].shape != (expected_size, expected_size):
        raise RuntimeError("the fixture must complete its eight-mode output support")
    files = _qd_cases(row, budgets)
    manifest = json.loads(next(text for name, text in files.items() if name.endswith("cases.json")))
    circuit = json.loads(next(text for name, text in files.items() if name.endswith("circuit.json")))
    qd_platform.template_experiment(manifest, circuit)


def test_sedenion_sequence_keeps_distinct_batches_and_mesh_reproduction(budgets: Budgets) -> None:
    rows = settings("sedenion-lcu")
    if [row["contrast_weight"] for row in rows] != [1, -1, -1, 1, 0]:
        raise RuntimeError("kernel-bright-bright-kernel contrast requires its ordered four arms and separate fixture")
    if len({row["name"] for row in rows}) != 5 or [row["acquisition_order"] for row in rows] != list(range(5)):
        raise RuntimeError("each scheduled acquisition requires a separate checkpoint directory")
    base = _qd_cases(rows[0], budgets)
    repeated = _qd_cases(rows[3], budgets)
    first = json.loads(next(text for name, text in base.items() if name.endswith("cases.json")))
    second = json.loads(next(text for name, text in repeated.items() if name.endswith("cases.json")))
    if (
        first["compilation_seed"] != second["compilation_seed"]
        or second["compilation_seed_role"] != "reproduce-base-mesh"
    ):
        raise RuntimeError("repeated optical arms must explicitly reproduce their base compiled mesh")
    if first["circuit"] != second["circuit"]:
        raise RuntimeError("repeated optical arms must submit the same circuit template")


def test_pending_optical_case_refuses_submission_but_allows_readonly_plan(
    tmp_path: Path, budgets: Budgets, monkeypatch: pytest.MonkeyPatch
) -> None:
    import qd_platform

    files = _qd_cases(settings("sedenion-lcu")[0], budgets)
    write_files(tmp_path, files)
    directory = tmp_path / "ascella/sedenion-lcu/dark"

    def forbid(*args: object, **kwargs: object) -> None:
        raise RuntimeError("a pending case reached a provider read")

    monkeypatch.setattr(qd_platform, "explorer_row", forbid)
    with pytest.raises(qd_platform.PlatformError, match="case ceiling"):
        qd_platform.plan(directory, "qpu:ascella", 3.0, 60.0, 1.0)
    with pytest.raises(qd_platform.PlatformError, match="acquisition admission"):
        qd_platform.submit(directory, "qpu:ascella", "test approval", 2.0, 60.0, 1.0)
    with pytest.raises(RuntimeError, match="provider read"):
        qd_platform.plan(directory, "qpu:ascella", 2.0, 60.0, 1.0)


def test_campaign_index_and_byte_replay_bind_every_case(tmp_path: Path, budgets: Budgets) -> None:
    files = build(budgets, ("quarter-mass",), ("qx",))
    manifest = json.loads(files["campaign.json"])
    if len(manifest["cases"]) != 5:
        raise RuntimeError("quarter-mass campaign needs preparation, amplification, both omissions and direct target")
    write_files(tmp_path, files)
    check(tmp_path, files)
    (tmp_path / "unregistered.json").write_text("{}")
    with pytest.raises(ValueError, match="inventory"):
        check(tmp_path, files)


@pytest.mark.parametrize(
    "changes",
    [{"qx_shots": 2049}, {"execution_seconds": 301.0}, {"photonic_samples": 2049}, {"photonic_credits": float("nan")}],
)
def test_budget_validation_rejects_unusable_envelopes(changes: dict[str, Any], budgets: Budgets) -> None:
    with pytest.raises(ValueError):
        replace(budgets, **changes).validate()


@pytest.mark.parametrize("families", [("quarter-mass",), ("mub-six", "quarter-mass")])
def test_every_requested_family_requires_an_admitted_route(families: tuple[str, ...], budgets: Budgets) -> None:
    with pytest.raises(ValueError, match="quarter-mass requires at least one admitted route"):
        build(budgets, families, ("ascella",))


def test_cli_rejects_an_uncovered_family_before_writing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import experiment_cases

    destination = tmp_path / "cases"
    monkeypatch.setattr(
        "sys.argv",
        [
            "experiment_cases.py",
            "--out",
            str(destination),
            "--families",
            "quarter-mass",
            "--routes",
            "ascella",
            "--tuna-shots",
            "1024",
            "--qx-shots",
            "1024",
            "--photonic-samples",
            "1024",
            "--photonic-shots",
            "2048",
            "--execution-seconds",
            "60",
            "--photonic-credits",
            "2",
        ],
    )
    with pytest.raises(ValueError, match="quarter-mass requires at least one admitted route"):
        experiment_cases.main()
    if destination.exists():
        raise RuntimeError("an unsupported route must fail before publishing any output")


@pytest.fixture
def historical_campaign(tmp_path: Path, budgets: Budgets) -> tuple[Path, dict[str, str]]:
    files = build(budgets, ("quarter-mass",), ("qx",))
    historical = dict(files)
    provenance = json.loads(historical["provenance.json"])
    provenance["sources"]["scripts/experiment_cases.py"] = "0" * 64
    historical["provenance.json"] = json.dumps(provenance, indent=1, sort_keys=True) + "\n"
    directory = tmp_path / "historical"
    write_files(directory, historical)
    return directory, files


def test_companion_receipt_preserves_history_and_keeps_default_check_strict(
    historical_campaign: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    from experiment_cases import attest_existing

    directory, files = historical_campaign
    before = {name: (directory / name).read_bytes() for name in files}
    with pytest.raises(ValueError, match="campaign bytes differ: provenance.json"):
        check(directory, files)
    receipt_path = tmp_path / "regeneration.json"
    attest_existing(directory, files, receipt_path)
    attest_existing(directory, files, receipt_path)
    check(directory, files, receipt_path)
    if before != {name: (directory / name).read_bytes() for name in files}:
        raise RuntimeError("a regeneration receipt must preserve every historical artifact byte")
    receipt = json.loads(receipt_path.read_bytes())
    versions = receipt["current_provenance"]["versions"]
    if "python" not in versions or "sympy" not in versions:
        raise RuntimeError("current regeneration must bind the Python and symbolic algebra runtimes")
    if receipt["generation"] != {
        key: json.loads(files["campaign.json"])[key] for key in ("budgets", "families", "routes")
    }:
        raise RuntimeError("the receipt must bind generation arguments")
    receipt_path.write_text("{}")
    with pytest.raises(ValueError, match="existing replay receipt differs"):
        attest_existing(directory, files, receipt_path)
    with pytest.raises(ValueError, match="outside the historical bundle"):
        attest_existing(directory, files, directory / "receipt.json")


@pytest.mark.parametrize(
    "mutation", ["source", "runtime", "arguments", "historical-provenance", "artifact", "inventory"]
)
def test_companion_receipt_rejects_stale_or_changed_inputs(
    mutation: str, historical_campaign: tuple[Path, dict[str, str]], tmp_path: Path
) -> None:
    from experiment_cases import attest_existing

    directory, files = historical_campaign
    receipt_path = tmp_path / "regeneration.json"
    attest_existing(directory, files, receipt_path)
    if mutation in {"source", "runtime"}:
        provenance = json.loads(files["provenance.json"])
        if mutation == "source":
            provenance["sources"]["scripts/experiment_cases.py"] = "1" * 64
        else:
            provenance["versions"]["python"] = "different-runtime"
        files["provenance.json"] = json.dumps(provenance)
    elif mutation == "arguments":
        campaign = json.loads(files["campaign.json"])
        campaign["budgets"]["qx_shots"] += 1
        files["campaign.json"] = json.dumps(campaign)
    elif mutation == "historical-provenance":
        path = directory / "provenance.json"
        path.write_bytes(path.read_bytes() + b" ")
    elif mutation == "artifact":
        path = directory / "campaign.json"
        path.write_bytes(path.read_bytes() + b" ")
    else:
        (directory / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="receipt differs|artifact digests|campaign bytes|inventory"):
        check(directory, files, receipt_path)
