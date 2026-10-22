"""Returned mesh propagation stays distinct from detector observations."""

import json
import math

import numpy as np
import pytest
from photonic_compilation_audit import compiled_probabilities


def test_pooled_compilation_audit_preserves_retained_scientific_rows() -> None:
    from photonic_repeat_readout import ROOT

    base = ROOT / "results/hypercomplex"
    serial = json.loads((base / "belenos-compilation-measurement-audit.json").read_text())
    pooled = json.loads((base / "belenos-compilation-measurement-audit-pooled.json").read_text())
    for key in ("rows", "max_compiled_vs_requested_tvd", "max_measured_vs_compiled_tvd", "boundary"):
        if pooled[key] != serial[key]:
            raise RuntimeError(f"pooled compilation audit changed retained scientific results: {key}")


def test_compiled_rx_column_uses_the_returned_source_and_numeric_phases() -> None:
    import perceval as pcvl

    chip = pcvl.Circuit(24).add(0, pcvl.BS.Rx(theta=math.pi / 2))
    circuit = pcvl.serialization.serialize(chip)
    result = compiled_probabilities(circuit, ":PCVL:BasicState:|1," + ",".join(["0"] * 23) + ">")
    np.testing.assert_allclose(result, [0.5, 0.5] + [0.0] * 22, atol=1e-12)
    with pytest.raises(ValueError, match="one-photon"):
        compiled_probabilities(circuit, ":PCVL:BasicState:|1,1," + ",".join(["0"] * 22) + ">")
