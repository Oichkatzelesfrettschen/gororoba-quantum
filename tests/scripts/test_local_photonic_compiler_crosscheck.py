"""Protect the boundary between terminal measurement samples and unitary probabilities."""

import pytest
from local_photonic_compiler_crosscheck import photonic, terminal_unitary


def test_terminal_measurement_removal_keeps_unitary_gates() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nH q[0]\nb[0] = measure q[0]\n"
    expected = "version 3.0\nqubit[1] q\nbit[1] b\nH q[0]\n"
    if terminal_unitary(source) != expected:
        raise RuntimeError("unitary probe must preserve source gates")


def test_intermediate_measurement_rejects_unitary_probe() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nb[0] = measure q[0]\nX q[0]\n"
    with pytest.raises(ValueError, match="terminal"):
        terminal_unitary(source)


def test_physical_experiment_api_retains_twelve_mode_distribution() -> None:
    pytest.importorskip("perceval")
    row = photonic(("results/hypercomplex/photonic-successors/ascella/order-repeat-block-0", 0))
    if not row["passed"] or row["modes"] != 12 or len(row["probabilities"]["Naive"]) != 12:
        raise RuntimeError(f"physical single-photon experiment must retain all twelve outputs: {row}")


def test_inline_measurement_comment_preserves_terminal_guard() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] b\nb[0] = measure q[0] // terminal\nX q[0]\n"
    with pytest.raises(ValueError, match="terminal"):
        terminal_unitary(source)


def test_unsupported_measurement_assignment_fails_closed() -> None:
    source = "version 3.0\nqubit[1] q\nbit[1] c\nc[0] = measure q[0]\n"
    with pytest.raises(ValueError, match="supported terminal"):
        terminal_unitary(source)
