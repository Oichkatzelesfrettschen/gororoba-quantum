"""gororoba_quantum/law_encoding.py: short vectors stay lists, a wide law and a one-bit score take their short exact
forms, every form expands to the JSON text it encoded, and malformed forms raise.
"""

from __future__ import annotations

import json

import pytest

import law_encoding

WIDE = 1 << 15


def test_short_vector_stays_a_list() -> None:
    values = [0.25, 0.0, 0.75, 0.0]
    if law_encoding.encode(values) != values or law_encoding.dense(values) is not values:
        raise AssertionError("a short vector changed form")


def test_wide_law_keeps_its_support() -> None:
    law = [0.0] * WIDE
    for index, value in ((3, 0.5), (16387, 0.25), (32767, 0.25)):
        law[index] = value
    stored = law_encoding.encode(law)
    if not isinstance(stored, dict) or stored["encoding"] != "support" or len(stored["support"]) != 3:
        raise AssertionError(stored)
    if json.dumps(law_encoding.dense(stored)) != json.dumps(law):
        raise AssertionError("the support form expands to another law")


def test_one_bit_score_takes_a_two_entry_table() -> None:
    score = [float((x >> 4) & 1) for x in range(WIDE)]
    stored = law_encoding.encode(score)
    if not isinstance(stored, dict) or stored["encoding"] != "bits" or stored["bits"] != [4]:
        raise AssertionError(stored)
    if stored["table"] != [0.0, 1.0] or law_encoding.dense(stored) != score:
        raise AssertionError(stored)


def test_mixed_zero_spellings_round_trip_as_text() -> None:
    # 0, 0.0 and -0.0 compare equal and serialize apart.
    values: list[float] = [0.0] * WIDE
    values[1] = -0.0
    values[2] = 0
    values[5] = 0.5
    stored = law_encoding.encode(values)
    if json.dumps(law_encoding.dense(stored)) != json.dumps(values):
        raise AssertionError("an encoded form lost a zero's spelling")


@pytest.mark.parametrize(
    "stored",
    [
        {"encoding": "support", "length": 8, "support": {"8": 1.0}},
        {"encoding": "bits", "length": 8, "bits": [3], "table": [0.0, 1.0]},
        {"encoding": "bits", "length": 8, "bits": [0], "table": [0.0]},
        {"encoding": "runs", "length": 8},
        "0.5",
    ],
)
def test_malformed_forms_raise(stored: object) -> None:
    with pytest.raises(ValueError):
        law_encoding.dense(stored)


class Flips:
    """Asymmetric readout channel per qubit, as backend properties report it."""

    def qubit_property(self, qubit: int, name: str) -> tuple[float, None]:
        return (0.01 + 0.003 * qubit, None) if name == "prob_meas1_prep0" else (0.02 + 0.002 * qubit, None)


@pytest.mark.parametrize("symmetric", [False, True])
def test_axis_readout_inverse_is_the_dense_product(symmetric: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    import numpy as np
    from qiskit import QuantumCircuit

    import live_run

    width = 6
    circuit = QuantumCircuit(width + 1, width + 1)
    # Clbit k reads qubit (k + 2) mod 7: the channel follows the writing qubit; clbit 6 stays unwritten.
    for clbit in range(width):
        circuit.measure((clbit + 2) % (width + 1), clbit)
    dist = np.random.default_rng(5).dirichlet(np.ones(1 << (width + 1)))
    dense = live_run.readout_inverse(circuit, Flips(), symmetric) @ dist
    monkeypatch.setattr(law_encoding, "DENSE_LIMIT", 4)
    axis = live_run.readout_corrected(dist, circuit, Flips(), symmetric)
    if not np.allclose(axis, dense, rtol=0.0, atol=1e-14):
        raise AssertionError(float(np.abs(axis - dense).max()))
