"""Complete single-placement ET acquisition, including every physical null and calibration shot."""

import math
import random
from functools import lru_cache
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import Statevector

from et_reference import ETSpec
from et_rows import COMPILATION_CONTRACT, decode_circuit, direct_state, row_template
from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member

ROWS = ((32, 9, 2), (32, 1, 2), (32, 9, 8))
BLOCKS = 4
FAMILY = "et-row"


def row_name(spec: ETSpec) -> str:
    return f"d{spec.dimension}_s{spec.strut}_r{spec.row}"


def configuration() -> dict[str, Any]:
    """The immutable allocation has total signal shots, not shots per repeated block."""
    members: dict[str, dict[str, Any]] = {}

    def add(spec: ETSpec, block: int, suffix: str, kind: str, basis: str, shots: int, **extra: Any) -> None:
        name = f"et_{row_name(spec)}_b{block}_{suffix}"
        members[name] = {
            "spec": [spec.dimension, spec.strut, spec.row],
            "block": block,
            "kind": kind,
            "basis": basis,
            "shots": shots,
            "execution_row": len(members),
            **extra,
        }

    for block in range(BLOCKS):
        for dimensions in ROWS:
            spec = ETSpec(*dimensions)
            # The demanding coherence template seeds the placement search.
            for basis, sign, marker in (("X", 1, 0), ("X", 1, 1), ("Z", 1, 0), ("Z", -1, 0)):
                suffix = f"{basis}_t{sign}_m{marker}"
                add(spec, block, suffix, "signal", basis, 2048, sign=sign, mask=marker)
            for marker in (0, 1):
                for mask in range(spec.generator):
                    add(
                        spec,
                        block,
                        f"null_m{marker}_z{mask}",
                        "dephased",
                        "X",
                        128,
                        sign=1,
                        mask=mask ^ marker,
                        marker=marker,
                    )
            for basis in ("Z", "X"):
                for value in range(2 * spec.dimension):
                    for held_out, shots in ((False, 128), (True, 32)):
                        add(
                            spec,
                            block,
                            f"{basis}_read_{value}_{int(held_out)}",
                            "readout",
                            basis,
                            shots,
                            value=value,
                            held_out=held_out,
                        )
            # Probe each decoder input sector and each column bit's phase transfer.
            probes = [(column, -1, 0) for column in range(spec.generator)]
            probes += [(0, bit, phase) for bit in range(spec.bits - 1) for phase in (0, 1)]
            for sector in range(4):
                for column, bit, phase in probes:
                    add(
                        spec,
                        block,
                        f"decoder_{sector}_{column}_{bit}_{phase}",
                        "decoder",
                        "X",
                        64,
                        sector=sector,
                        column=column,
                        bit=bit,
                        phase=phase,
                    )
    schedule = list(members)
    random.Random(230).shuffle(schedule)
    for execution_row, name in enumerate(schedule):
        members[name]["execution_row"] = execution_row
    return {
        "name": FAMILY,
        "schema": 1,
        "dimension": 32,
        "blocks": BLOCKS,
        "replica_cap": 1,
        "compilation_contract": COMPILATION_CONTRACT,
        "members": members,
        "signal_shots": 98304,
        "alpha": 0.05,
        "randomization_seed": 230,
        "physical_null": "balanced complete input-column Z-mask ensemble, matched native suffix",
        "inference": "paired bounded-score differences with Holm; physical-control gates",
        "sampling_assumption": (
            "independent training and endpoint observations; independent endpoint shots within each fixed-response "
            "block; cross-block endpoint dependence allowed"
        ),
        "interpretation": "detection against complete dephasing; full-row fidelity remains unmeasured",
    }


def validate_configuration(config: dict[str, Any]) -> None:
    reference = configuration()
    for key, value in reference.items():
        if config.get(key) != value:
            raise ValueError(f"ET configuration differs in {key}")


@lru_cache(maxsize=2048)
def control_circuit(
    spec: ETSpec, kind: str, basis: str, value: int = 0, sector: int = 0, column: int = 0, bit: int = -1, phase: int = 0
) -> QuantumCircuit:
    circuit = QuantumCircuit(spec.bits + 1)
    prepared = value if kind == "readout" else sector * spec.generator + column
    for index in range(spec.bits + 1):
        if prepared & (1 << index):
            circuit.x(index)
    if kind == "decoder":
        if bit >= 0:
            circuit.h(bit)
            if phase:
                circuit.z(bit)
        circuit.barrier()
        circuit.compose(decode_circuit(spec, basis), inplace=True)
    circuit.metadata = {"compilation_contract": COMPILATION_CONTRACT}
    circuit.add_register(ClassicalRegister(spec.bits + 1, "et_out"))
    circuit.measure(range(spec.bits + 1), range(spec.bits + 1))
    return circuit


@lru_cache(maxsize=2048)
def _control_ideal(
    spec: ETSpec, kind: str, basis: str, value: int, sector: int, column: int, bit: int, phase: int
) -> np.ndarray:
    circuit = control_circuit(spec, kind, basis, value, sector, column, bit, phase)
    return Statevector.from_instruction(circuit.remove_final_measurements(inplace=False)).probabilities()


def et_group(config: dict[str, Any] | None = None) -> Group:
    config = configuration() if config is None else config
    validate_configuration(config)
    templates = {}
    members = []
    for name, item in configuration()["members"].items():
        spec = ETSpec(*item["spec"])
        binding = None
        if item["kind"] in ("signal", "dephased"):
            key = (spec, item["basis"])
            if key not in templates:
                template, phases = row_template(*key)
                template.add_register(ClassicalRegister(spec.bits + 1, "et_out"))
                template.measure(range(spec.bits + 1), range(spec.bits + 1))
                templates[key] = (template, phases)
            circuit, phases = templates[key]
            angles = [math.pi if item["mask"] & (1 << bit) else 0.0 for bit in range(spec.bits - 1)]
            angles.append(math.pi if item["sign"] == -1 else 0.0)
            binding = dict(zip(phases, angles, strict=True))
            ideal = abs(direct_state(spec, item["sign"], item["basis"], item["mask"])) ** 2
        else:
            circuit = control_circuit(
                spec,
                item["kind"],
                item["basis"],
                **{key: item[key] for key in ("value", "sector", "column", "bit", "phase") if key in item},
            )
            ideal = _control_ideal(
                spec,
                item["kind"],
                item["basis"],
                *(
                    item.get(key, default)
                    for key, default in (("value", 0), ("sector", 0), ("column", 0), ("bit", -1), ("phase", 0))
                ),
            )
        members.append(Member(name, circuit, ideal, binding))

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        return {
            member.name + "_tvd": float(abs(distributions[member.name] - member.ideal).sum() / 2) for member in members
        }

    return Group(
        "et_row_campaign",
        tuple(members),
        summarize,
        execution_rows=tuple(config["members"][member.name]["execution_row"] for member in members),
        replica_floor=0.0,
    )


def endpoint_terms(config: dict[str, Any], spec: ETSpec, kind: str) -> list[tuple[str, np.ndarray, float]]:
    """Raw bounded weights retain all channels and use equal block/mask averaging."""
    metadata = config["members"]
    if kind == "coherence":
        weights = abs(direct_state(spec, 1, "X", 0)) ** 2 - abs(direct_state(spec, 1, "X", 1)) ** 2
        weights /= max(abs(weights))
    else:
        weights = np.array(
            [
                (spec.cell(outcome % spec.generator).sign or 0) * (1 if outcome < spec.dimension else -1)
                for outcome in range(2 * spec.dimension)
            ],
            float,
        )
    terms = []
    for name, item in metadata.items():
        if tuple(item["spec"]) != (spec.dimension, spec.strut, spec.row):
            continue
        if kind == "signed" and item["kind"] == "signal" and item["basis"] == "Z":
            terms.append((name, weights, item["sign"] / BLOCKS))
        if kind == "coherence" and item["basis"] == "X":
            if item["kind"] == "signal":
                terms.append((name, weights, (1 if item["mask"] == 0 else -1) / BLOCKS))
            elif item["kind"] == "dephased":
                terms.append((name, weights, (-1 if item["marker"] == 0 else 1) / (BLOCKS * spec.generator)))
    return terms


def contracts(precision: float, alpha: float, power: float) -> tuple[ObservableContract, ...]:
    config = configuration()
    return tuple(
        ObservableContract(
            f"et_{row_name(spec)}_{kind}",
            tuple(
                ObservableTerm(name, tuple(weights * coefficient))
                for name, weights, coefficient in endpoint_terms(config, spec, kind)
            ),
            minimum_effect=0.0,
            alpha=alpha / 6,
            power=power,
        )
        for dimensions in ROWS
        for spec in [ETSpec(*dimensions)]
        for kind in ("signed", "coherence")
    )
