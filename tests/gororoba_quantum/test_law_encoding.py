"""gororoba_quantum/law_encoding.py: short vectors stay lists, a wide law and a one-bit score take their short exact
forms, every form expands to the JSON text it encoded, and malformed forms raise.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict
from typing import Any

import numpy as np
import pytest

import experiment_optimizer
import law_encoding
import qpu_planning

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


def reference_encode(values: Sequence[float]) -> list[float] | dict[str, Any]:
    """The text-comparing encode that the bitwise fast acceptance must reproduce."""
    if len(values) <= law_encoding.DENSE_LIMIT:
        return list(values)
    length = len(values)
    width = length.bit_length() - 1
    if 1 << width != length:
        raise ValueError(f"an outcome vector of {length} entries spans no whole register")
    support: dict[str, Any] = {
        "encoding": "support",
        "length": length,
        "support": {str(index): values[index] for index in law_encoding._truthy_indices(values)},
    }
    bits = law_encoding._dependent_bits(values, width)
    table = [values[index] for index in law_encoding._gather_index(1 << len(bits), bits, forward=True)]
    junta: dict[str, Any] = {"encoding": "bits", "length": length, "bits": bits, "table": table}
    text = json.dumps(list(values))
    exact = [form for form in (support, junta) if json.dumps(law_encoding.dense(form)) == text]
    return min(exact, key=lambda form: len(json.dumps(form))) if exact else list(values)


def dense_vector(length: int) -> list[float]:
    return [float(v) for v in np.sin(np.arange(length) * 0.37) / 7.0]


def sparse_vector(length: int) -> list[float]:
    values = [0.0] * length
    for index in (1, length // 3, length - 2):
        values[index] = 0.125 * (index % 5 + 1)
    return values


def junta_vector(length: int) -> list[float]:
    return [float(((x >> 1) & 1) - 0.5 * ((x >> 4) & 1)) for x in range(length)]


def with_entries(values: list[float], entries: dict[int, Any]) -> list[Any]:
    out: list[Any] = list(values)
    for index, value in entries.items():
        out[index] = value
    return out


def nan_with_payload(payload: int) -> float:
    return float(np.array([0x7FF8000000000000 | payload], dtype=np.uint64).view(np.float64)[0])


def encode_cases() -> dict[str, Any]:
    n = 1 << 13
    return {
        "dense": dense_vector(n),
        "sparse": sparse_vector(n),
        "junta": junta_vector(n),
        "junta_negative_zero": with_entries(junta_vector(n), {4: -0.0}),
        "sparse_negative_zero": with_entries(sparse_vector(n), {7: -0.0, 100: -0.0}),
        "sparse_int_zero": with_entries(sparse_vector(n), {9: 0}),
        "junta_int_entries": [int(v) for v in junta_vector(n)],
        "sparse_np_float64": [np.float64(v) for v in sparse_vector(n)],
        "junta_np_float64": [np.float64(v) for v in junta_vector(n)],
        "sparse_nan": with_entries(sparse_vector(n), {5: float("nan")}),
        "junta_nan_payloads": with_entries(junta_vector(n), {3: nan_with_payload(1), 8: float("nan")}),
        "dense_infinities": with_entries(dense_vector(n), {2: float("inf"), 6: float("-inf")}),
        "all_zero": [0.0] * n,
        "all_negative_zero": [-0.0] * n,
        "tuple": tuple(junta_vector(n)),
        "ndarray": np.array(sparse_vector(n)),
        "short": sparse_vector(64),
        "at_dense_limit": sparse_vector(law_encoding.DENSE_LIMIT),
    }


@pytest.mark.parametrize("name", list(encode_cases()))
def test_encode_matches_the_text_comparing_reference(name: str) -> None:
    values = encode_cases()[name]
    new, old = law_encoding.encode(values), reference_encode(values)
    if json.dumps(new) != json.dumps(old):
        raise AssertionError(f"{name}: encode diverged from the text-comparing reference")
    if type(new) is not type(old):
        raise AssertionError(f"{name}: encode returned another container")


def test_encode_matches_the_reference_at_seventeen_bits() -> None:
    values = junta_vector(1 << 17)
    new, old = law_encoding.encode(values), reference_encode(values)
    if not isinstance(new, dict) or new["encoding"] != "bits" or json.dumps(new) != json.dumps(old):
        raise AssertionError("the 2^17-entry junta vector changed form")


def test_encode_keeps_the_shorter_of_two_accepted_forms() -> None:
    # An all-zero vector satisfies both forms; the support form is the shorter.
    stored = law_encoding.encode([0.0] * (1 << 13))
    if not isinstance(stored, dict) or stored["encoding"] != "support":
        raise AssertionError(stored)


def contract_cases() -> list[Any]:
    term = experiment_optimizer.ObservableTerm
    wide = tuple(junta_vector(1 << 17))
    odd = tuple(with_entries(sparse_vector(1 << 13), {7: -0.0, 9: float("nan"), 11: float("inf"), 12: float("-inf")}))
    return [
        experiment_optimizer.ObservableContract(
            "wide", (term("m0", wide, 1), term("m1", tuple(sparse_vector(1 << 13)), -1)), precision_half_width=0.5
        ),
        experiment_optimizer.ObservableContract("odd", (term("m2", odd, 1), term("m3", (0.0, -0.0, 1.0), -1))),
        experiment_optimizer.ObservableContract(
            "mixed",
            (
                term("m4", (1, 0, 2), 1),
                term("m5", tuple(np.float64(v) for v in sparse_vector(1 << 13)), 1),
                term("m6", tuple(junta_vector(1 << 13)), 1),
            ),
            null_value=0.25,
            minimum_effect=0.1,
        ),
    ]


def reference_contract_records(contracts: Any) -> list[dict[str, Any]]:
    records = json.loads(json.dumps([asdict(contract) for contract in contracts]))
    for record in records:
        for term in record["terms"]:
            term["values"] = reference_encode(term["values"])
    return records


def test_observable_contract_records_match_the_round_trip_reference() -> None:
    contracts = contract_cases()
    new = qpu_planning.observable_contract_records(contracts)
    old = reference_contract_records(contracts)
    if json.dumps(new) != json.dumps(old):
        raise AssertionError("observable_contract_records diverged from the round-trip reference")
    if contracts != contract_cases() and json.dumps([asdict(c) for c in contracts]) != json.dumps(
        [asdict(c) for c in contract_cases()]
    ):
        raise AssertionError("observable_contract_records mutated its contracts")
