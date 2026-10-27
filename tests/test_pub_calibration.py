"""Per-PUB execution calibration: written once per PUB, restricted per member, read in both record forms."""

from __future__ import annotations

import copy
from types import SimpleNamespace
from typing import Any

import live_run
import measurement_sequence_analysis as msa
import msq_envelope_analysis as ea
import pub_calibration


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


class FakeProperties:
    """BackendProperties stand-in: per-qubit coherence items and per-qubit gate and readout values."""

    def __init__(self, qubits: list[int]) -> None:
        self.qubits = {
            q: [
                SimpleNamespace(name="T1", value=100.0 + q),
                SimpleNamespace(name="T2", value=50.0 + q),
                SimpleNamespace(name="readout_error", value=0.01 + q / 1e4),
                SimpleNamespace(name="prob_meas1_prep0", value=0.004),
                SimpleNamespace(name="prob_meas0_prep1", value=0.02),
            ]
            for q in qubits
        }

    def gate_error(self, _gate: str, qubit: int) -> float:
        return 2e-4 + qubit / 1e7

    def gate_length(self, _gate: str, qubit: int) -> float:
        return 3.2e-8 + qubit / 1e12

    def readout_length(self, qubit: int) -> float:
        return 2.2e-6 + qubit / 1e12


WIDTH = 6
QUBITS = list(range(10, 10 + WIDTH))
PUB: dict[str, Any] = {
    "name": "pub_fused",
    "components": [{"member": msa.ro0_name(q), "physical_qubits": [q]} for q in QUBITS],
}


def collect_members(with_gates: bool) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """The writer's per-PUB values and the members' executed entries, as live_run.collect builds them."""
    full = live_run.pub_execution_calibration(FakeProperties(QUBITS), PUB, with_gates=with_gates)
    executed = {
        component["member"]: {"pub": PUB["name"]}
        | pub_calibration.split_pub_calibration(full, component["physical_qubits"])
        for component in PUB["components"]
    }
    return full, executed


def test_pub_values_are_written_once_and_members_keep_their_own_qubits() -> None:
    full, executed = collect_members(with_gates=True)
    check(sorted(full) == ["placed_gate_calibration", "placed_qubit_calibration"])
    check(
        all(sorted(table, key=int) == [str(q) for q in QUBITS] for table in full.values()), "the PUB holds every qubit"
    )
    for component in PUB["components"]:
        own = {str(q) for q in component["physical_qubits"]}
        entry = executed[component["member"]]
        check(entry["pub"] == PUB["name"])
        check(set(entry["placed_qubit_calibration"]) == own and set(entry["placed_gate_calibration"]) == own)
        for field in pub_calibration_fields():
            check(all(entry[field][q] == full[field][q] for q in own), "a member copies the PUB's values")
    union: dict[str, Any] = {}
    for entry in executed.values():
        union |= entry["placed_qubit_calibration"]
    check(union == full["placed_qubit_calibration"], "the members' union is the PUB's qubit set")


def pub_calibration_fields() -> tuple[str, str]:
    return ("placed_qubit_calibration", "placed_gate_calibration")


def test_gate_calibration_is_absent_outside_the_measurement_sequence_families() -> None:
    full, executed = collect_members(with_gates=False)
    check(list(full) == ["placed_qubit_calibration"])
    check(all("placed_gate_calibration" not in entry for entry in executed.values()))


def record_for(qubits: list[int]) -> dict[str, Any]:
    delay = {str(q): 0 for q in qubits}
    return {
        "family_configuration": {
            "dt_seconds": 4e-9,
            "qubits": qubits,
            "measurement_delay_dt": delay,
            "settle_delay_dt": delay,
            "prereadout_delay_dt": {str(q): 100 for q in qubits},
            "t1_delays_dt": [0, 1000],
        }
    }


def test_context_reader_accepts_both_forms() -> None:
    full, restricted = collect_members(with_gates=True)
    legacy = {name: copy.deepcopy(full) | {"pub": PUB["name"]} for name in restricted}
    record = record_for(QUBITS)
    new = msa.contexts_from_record(record, {msa.ro0_name(q): restricted[msa.ro0_name(q)] for q in QUBITS})
    old = msa.contexts_from_record(record, {msa.ro0_name(q): legacy[msa.ro0_name(q)] for q in QUBITS})
    check(new == old and sorted(new) == QUBITS, "both forms give the same per-qubit contexts")


def test_envelope_eligibility_reads_both_forms() -> None:
    full, restricted = collect_members(with_gates=True)
    names = [msa.ro0_name(QUBITS[0])]
    legacy = {name: copy.deepcopy(full) for name in names}
    new = {name: restricted[name] for name in names}
    a = ea.execution_eligibility(legacy, QUBITS[0], names)
    b = ea.execution_eligibility(new, QUBITS[0], names)
    check(a == b, f"eligibility differs between forms: {a} against {b}")
    check(ea.execution_eligibility({names[0]: {}}, QUBITS[0], names) is not None, "a member without values fails")
