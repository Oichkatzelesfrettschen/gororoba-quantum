"""Hardware cases retain native errors, budgets and existing submission boundaries."""

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from hypercomplex_cases import (
    photonic_template,
    qd_cases,
    qi_cases,
    setting_operator,
    transform_settings,
    wave_settings,
)

from hypercomplex_operators import order_interferometer
from parallel import ordered_map


def test_photonic_successor_retains_leakage_and_repeat_identity() -> None:
    from hypercomplex_photonic_cases import campaign_cases

    files = campaign_cases("belenos", repeats=3)
    manifests = [json.loads(text) for name, text in files.items() if name.endswith("/cases.json")]
    if len(manifests) != 5:
        raise RuntimeError("three repeat blocks need one order, three wave and one Fourier job")
    for manifest in manifests:
        circuit = json.loads(files[manifest["job"] + "/circuit.json"])
        if circuit["modes"] != 24 or len(circuit["input_state"]) != 24:
            raise RuntimeError("every physical output must remain observable")
        if manifest["platforms"] != ["qpu:belenos"] or manifest["mitigations"] != []:
            raise RuntimeError("the physical backend and observation policy must be explicit")
        import qd_platform

        qd_platform.template_experiment(manifest, circuit)
        if len({setting["name"] for setting in manifest["settings"]}) != manifest["iterations"]:
            raise RuntimeError("repeated settings must retain distinct acquisition identities")
    if sum(m["iterations"] for m in manifests) != 120:
        raise RuntimeError("the design must retain three observations of each of forty settings")


def test_ascella_readiness_uses_static_native_computation() -> None:
    import qd_platform
    from hypercomplex_photonic_cases import readiness_case

    files = readiness_case()
    manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
    if qd_platform.iteration_form(manifest) != "single":
        raise RuntimeError("readiness must test the static computation path")
    experiment = qd_platform.experiment(manifest, circuit)
    matrix = np.asarray(experiment.unitary_circuit().compute_unitary())
    np.testing.assert_allclose(np.abs(matrix[:, 0]) ** 2, [0.5, 0.5] + [0.0] * 10, atol=1e-12)
    if manifest["max_samples"] != 1024 or manifest["max_shots"] != 2048:
        raise RuntimeError("readiness must remain bounded before the eight-setting pilot")


def test_single_template_payload_binds_angles_before_serialization(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    import perceval as pcvl
    import qd_platform
    from perceval.providers.quandela.rpc_handler import RPCHandler

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"]["qpu:ascella"]
    monkeypatch.setattr(RPCHandler, "fetch_platform_details", lambda self: processor)
    monkeypatch.setattr(qd_platform, "token", lambda: "offline-test-token")
    files = qd_cases([transform_settings()[2]], "single-template")
    manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
    built = qd_platform.payload(root, manifest, circuit, "qpu:ascella")
    # The payload is produced locally by the SDK, rather than deserialized from a service response.
    computation = pcvl.serialization.deserialize(built["body"]["payload"]["computation"])
    if isinstance(computation, pcvl.ComputationIterator):
        raise RuntimeError("one template setting must remain a static computation")
    matrix = np.asarray(computation.experiment.unitary_circuit().compute_unitary())
    expected = manifest["settings"][0]["operator"]
    np.testing.assert_allclose(
        matrix, np.asarray(expected["real"]) + 1j * np.asarray(expected["imaginary"]), atol=1e-12
    )


def test_native_ascella_readiness_matches_calibrated_architecture() -> None:
    from pathlib import Path

    import qd_platform
    from hypercomplex_photonic_cases import native_readiness_case

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"]["qpu:ascella"]
    files = native_readiness_case(processor)
    manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
    qd_platform.live_mesh(processor, circuit, "qpu:ascella")
    qd_platform.template_experiment(manifest, circuit)
    circuit["architecture"]["couplers"][0][1] += 0.01
    with pytest.raises(qd_platform.PlatformError, match="architecture differs"):
        qd_platform.live_mesh(processor, circuit, "qpu:ascella")


def test_full_source_readiness_uses_only_published_input_modes() -> None:
    from pathlib import Path

    import qd_platform
    from hypercomplex_photonic_cases import native_readiness_case

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"]["qpu:ascella"]
    files = native_readiness_case(processor, all_sources=True)
    manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
    if circuit["input_state"] != [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]:
        raise RuntimeError("full-source readiness must occupy all six connected sources exactly once")
    if "ideal_probabilities" in manifest["preregistered"]:
        raise RuntimeError("a six-photon readiness case must not carry a one-photon probability law")
    qd_platform.template_experiment(manifest, circuit)


@pytest.mark.parametrize("phase_index", [1, 2, 3, 4])
def test_native_readiness_rejects_recalibrated_coupler_phases(phase_index: int) -> None:
    import perceval as pcvl
    import qd_platform
    from hypercomplex_photonic_cases import native_readiness_case
    from qd_belenos_mesh import decode

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"]["qpu:ascella"]
    files = native_readiness_case(processor)
    circuit = json.loads(files["circuit.json"])
    chip = pcvl.Circuit(12)
    changed = False
    for kind, mode, value in decode(processor["specs"]["architecture"]):
        if kind == "bs":
            parameters = list(value)
            if not changed:
                parameters[phase_index] = 0.125
                changed = True
            chip.add(mode, pcvl.BS(*parameters))
        else:
            chip.add(mode, pcvl.PS(pcvl.P(value)))
    processor["specs"]["architecture"] = pcvl.serialization.serialize(chip)
    with pytest.raises(qd_platform.PlatformError, match="architecture differs"):
        qd_platform.live_mesh(processor, circuit, "qpu:ascella")


def test_frozen_case_replay_rejects_sub_tolerance_coupler_change(tmp_path: Path) -> None:
    from hypercomplex_cases import write_files
    from hypercomplex_photonic_cases import check_files, native_readiness_case

    root = Path(__file__).resolve().parents[2]
    processor = json.loads((root / "docs/evidence/quandela/catalogue.json").read_text())["processors"]["qpu:ascella"]
    files = native_readiness_case(processor)
    write_files(tmp_path, files)
    circuit = json.loads(files["circuit.json"])
    circuit["architecture"]["couplers"][0][1] += 1e-12
    (tmp_path / "circuit.json").write_text(json.dumps(circuit, indent=1) + "\n")
    with pytest.raises(ValueError):
        check_files(tmp_path, files)


def test_retained_successor_replay_rejects_a_changed_budget(tmp_path: Path) -> None:
    from hypercomplex_cases import write_files
    from hypercomplex_photonic_cases import check_files, readiness_case

    files = readiness_case()
    write_files(tmp_path, files)
    check_files(tmp_path, files)
    manifest = json.loads((tmp_path / "cases.json").read_text())
    manifest["max_shots"] += 1
    (tmp_path / "cases.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        check_files(tmp_path, files)


def test_frozen_campaign_replay_accepts_equivalent_phase_branch(tmp_path: Path) -> None:
    import copy

    from hypercomplex_cases import write_files
    from hypercomplex_photonic_cases import campaign_cases, check_campaign_files

    frozen = campaign_cases("ascella")
    write_files(tmp_path, frozen)
    regenerated = copy.deepcopy(frozen)
    name = "order-repeat-block-0/cases.json"
    manifest = json.loads(regenerated[name])
    manifest["settings"][0]["circuit_params"]["x0"] += 2 * np.pi
    regenerated[name] = json.dumps(manifest)
    check_campaign_files(tmp_path, regenerated)
    manifest["max_shots"] += 1
    regenerated[name] = json.dumps(manifest)
    with pytest.raises(ValueError, match="metadata"):
        check_campaign_files(tmp_path, regenerated)


def test_frozen_successor_identity_rejects_one_byte_change(tmp_path: Path) -> None:
    import shutil

    from hypercomplex_photonic_cases import check_frozen_identity

    root = Path(__file__).resolve().parents[2] / "results/hypercomplex/photonic-successors"
    shutil.copytree(root, tmp_path, dirs_exist_ok=True)
    check_frozen_identity(tmp_path)
    manifest = tmp_path / "belenos/wave-repeat-block-0/cases.json"
    manifest.write_bytes(manifest.read_bytes() + b" ")
    with pytest.raises(ValueError, match="identity"):
        check_frozen_identity(tmp_path)


@pytest.mark.parametrize("mutation", ["inventory", "missing", "extra"])
def test_frozen_successor_identity_binds_inventory_and_file_set(tmp_path: Path, mutation: str) -> None:
    import shutil

    from hypercomplex_photonic_cases import check_frozen_identity

    root = Path(__file__).resolve().parents[2] / "results/hypercomplex/photonic-successors"
    shutil.copytree(root, tmp_path, dirs_exist_ok=True)
    if mutation == "inventory":
        inventory = tmp_path / "frozen-file-sha256.json"
        inventory.write_bytes(inventory.read_bytes() + b" ")
    elif mutation == "missing":
        (tmp_path / "ascella-readiness/cases.json").unlink()
    else:
        (tmp_path / "extra.json").write_text("{}")
    with pytest.raises(ValueError, match="identity"):
        check_frozen_identity(tmp_path)


def test_frozen_campaign_replay_checks_full_operator(tmp_path: Path) -> None:
    from hypercomplex_cases import write_files
    from hypercomplex_photonic_cases import campaign_cases, check_campaign_files

    files = campaign_cases("ascella")
    write_files(tmp_path, files)
    path = tmp_path / "order-repeat-block-0/cases.json"
    manifest = json.loads(path.read_text())
    manifest["settings"][0]["circuit_params"]["x0"] += 0.1
    path.write_text(json.dumps(manifest))
    import qd_platform

    with pytest.raises(qd_platform.PlatformError, match="operator|column"):
        check_campaign_files(tmp_path, files)


def test_frozen_campaign_replay_checks_unprepared_operator_columns(tmp_path: Path) -> None:
    import qd_platform
    from hypercomplex_cases import write_files
    from hypercomplex_photonic_cases import campaign_cases, check_campaign_files

    files = campaign_cases("ascella")
    write_files(tmp_path, files)
    path = tmp_path / "order-repeat-block-0/cases.json"
    manifest = json.loads(path.read_text())
    manifest["settings"][0]["operator"]["real"][1][1] += 0.1
    path.write_text(json.dumps(manifest))
    with pytest.raises(qd_platform.PlatformError, match="full operator"):
        check_campaign_files(tmp_path, files)


def test_ascella_frontier_covers_all_connected_ports_pairs_and_quadratures() -> None:
    from hypercomplex_photonic_cases import characterization_frontier

    record = characterization_frontier()
    rows = record["settings"]
    ports = [row for row in rows if row["mechanism"] == "transfer"]
    phases = [row for row in rows if row["mechanism"] == "recombined-phase"]
    if len(ports) != 72 or len(phases) != 1584 or len({row["name"] for row in rows}) != 1656:
        raise RuntimeError("the finite frontier must contain every 6x12 transfer and 6x66x4 recombined-phase setting")
    if set(row["source"] for row in rows) != {0, 2, 4, 6, 8, 10}:
        raise RuntimeError("the frontier must use each physically connected input")
    if any(row["state"] != "awaiting-instrument-and-timing-admission" for row in rows):
        raise RuntimeError("a planned setting must never masquerade as a hardware acquisition")


def test_photonic_mesh_reconstructs_the_entire_operator() -> None:
    import perceval as pcvl

    unitary = order_interferometer(np.pi / 4, np.pi / 4)
    circuit, parameters = photonic_template(unitary)
    chip = pcvl.Circuit(4)
    for kind, mode, index in circuit["ops"]:
        value = parameters[f"x{index}"]
        chip.add(mode, pcvl.BS.Rx(theta=value) if kind == "BS" else pcvl.PS(value))
    np.testing.assert_allclose(np.asarray(chip.compute_unitary()), unitary, atol=1e-12)


def test_qi_batches_bind_native_probabilities_and_calibration(monkeypatch: pytest.MonkeyPatch) -> None:
    with patch("hypercomplex_cases.ordered_map", wraps=ordered_map) as compilation_map:
        files = qi_cases(16384)
    if compilation_map.call_args.kwargs.get("min_items") != 1:
        raise RuntimeError("native compilation must use the process pool for the eight-setting pilot")
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    if files != qi_cases(16384):
        raise RuntimeError("pooled and serial native compilation must emit identical case bytes")
    manifests = [json.loads(text) for name, text in files.items() if name.endswith("/cases.json")]
    if len(manifests) != 8:
        raise RuntimeError("the order pilot needs eight calibrated batches")
    for manifest in manifests:
        if len(manifest["circuits"]) != 3 or manifest["hardware_pause_seconds"] != 120:
            raise RuntimeError("a batch must contain two readout references and one science circuit")
        science = manifest["circuits"][2]
        if "native_probabilities" not in science or "operator_error" not in science:
            raise RuntimeError("the native approximation must be retained")
    with pytest.raises(ValueError):
        qi_cases(131073)


def test_wave_campaign_has_all_requested_observations() -> None:
    if len(wave_settings()) != 24:
        raise RuntimeError("the wave campaign needs 17 frames, five references and two ray checks")


def test_transform_controls_expose_phase_and_identity_boundary() -> None:
    settings = transform_settings()
    if len(settings) != 8:
        raise RuntimeError("transform controls need four input/operator settings and two ray representatives")
    real = next(s for s in settings if s["operation"] == "forward-real-superposition" and s["representative"] == 0)
    imaginary = {**real, "operation": "forward-imaginary-superposition"}
    first = np.abs(setting_operator(real)[:, 0]) ** 2
    second = np.abs(setting_operator(imaginary)[:, 0]) ** 2
    if np.allclose(first, second):
        raise RuntimeError("phase-sensitive input controls must distinguish Fourier output laws")


def test_photonic_runner_checks_unprepared_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    import qd_platform

    with patch("hypercomplex_cases.ordered_map", wraps=ordered_map) as compilation_map:
        files = qd_cases(transform_settings(), "transform")
    if compilation_map.call_args.kwargs.get("min_items") != 1:
        raise RuntimeError("photonic setting compilation must use the process pool for small campaigns")
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    if files != qd_cases(transform_settings(), "transform"):
        raise RuntimeError("pooled and serial photonic compilation must emit identical case bytes")
    manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
    qd_platform.template_experiment(manifest, circuit)
    manifest["settings"][0]["operator"]["real"][0][1] += 0.1
    with pytest.raises(qd_platform.PlatformError, match="full operator"):
        qd_platform.template_experiment(manifest, circuit)
