"""Compare unassigned IQM alternatives with the logical circuit catalogue."""

import math

import pytest
from readout_information_circuits import alternatives as logical_alternatives
from readout_information_iqm import alternatives


def test_iqm_preparations_match_logical_alternatives_and_measure_every_qubit() -> None:
    names = ("QB1", "QB2", "QB3", "QB4")
    circuits = alternatives(names, ("QB1", "QB3"))
    logical = logical_alternatives(4, (0, 2))
    if set(circuits) != set(logical):
        raise AssertionError("IQM and logical catalogues have different input/context alternatives")
    for key, circuit in circuits.items():
        instructions = circuit["instructions"]
        measured = instructions[-1]
        if measured != {"name": "measure", "locus": list(names), "args": {"key": "c"}}:
            raise AssertionError("IQM source must measure the same complete ordered locus")
        actual = [item["locus"][0] for item in instructions[:-1]]
        expected = [
            names[logical[key].find_bit(item.qubits[0]).index]
            for item in logical[key].data
            if item.operation.name == "x"
        ]
        if actual != expected or any(
            item["name"] != "prx" or item["args"] != {"angle": math.pi, "phase": 0.0} for item in instructions[:-1]
        ):
            raise AssertionError("IQM source differs from the logical preparation")


@pytest.mark.parametrize(
    "qubits, targets",
    [(("QB1", "QB1"), ("QB1", "QB1")), (("QB1", "QB2"), ("QB1", "QB3")), (("QB1", ""), ("QB1", ""))],
)
def test_invalid_iqm_qubit_sets_refuse(qubits: tuple[str, ...], targets: tuple[str, str]) -> None:
    with pytest.raises(ValueError):
        alternatives(qubits, targets)
