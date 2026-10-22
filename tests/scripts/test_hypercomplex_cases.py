"""Hardware cases retain native errors, budgets and existing submission boundaries."""

import json
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
