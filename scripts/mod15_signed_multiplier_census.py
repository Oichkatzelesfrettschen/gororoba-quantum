"""Signed modulo-15 multiplier census over every nonidentity unit.

The seven nonidentity units of (Z/15)^x are 2, 4, 8 (positive powers of two)
and 7 = -8, 11 = -4, 13 = -2, 14 = -1 (negated powers). modular_arithmetic
synthesizes each as a cyclic rotation of the four work wires, followed for a
negated power by one's-complement inversion. Inversion maps the all-zero and
all-one strings onto each other, so the nonzero-residue domain used by order
finding leaves the endpoints exchanged, and the full-register domain appends a
controlled Gray-path transposition of 0 and 15 that restores them.

The census verifies every circuit as a 32-state unitary (control qubit 0, work
qubits 1..4) on both input domains, derives the ideal order-finding yield under
the decoder in factoring.py at the phase-bit count order_finding uses for
N = 15, and compiles one controlled multiplier per base on the static FakeFez
target. Base 14 = -1 has order 2 and a^(r/2) = -1, so the factor extractor
rejects it: it is the arithmetic negative control, executable and
factor-useless. The module submits no quantum work and exits nonzero on any
failed check.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "gororoba_quantum"))

MODULUS = 15
WIDTH = 4
CONTROL_QUBIT = 0
WORK_QUBITS = [1, 2, 3, 4]
BASES = (2, 4, 7, 8, 11, 13, 14)
NEGATIVE_CONTROL_BASE = 14
FACTOR_USEFUL_BASES = tuple(base for base in BASES if base != NEGATIVE_CONTROL_BASE)
DEFAULT_SEEDS = tuple(range(8))
TOLERANCE = 1e-12
SOURCE_PATHS = (
    "gororoba_quantum/compile_evidence.py",
    "gororoba_quantum/factoring.py",
    "gororoba_quantum/modular_arithmetic.py",
    "gororoba_quantum/order_finding.py",
    "scripts/mod15_signed_multiplier_census.py",
)


class CensusError(Exception):
    """A census invariant failed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CensusError(message)


def _packed(control: int, data: int) -> int:
    return control | (data << 1)


def _rotate_left(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (WIDTH - shift))) & ((1 << WIDTH) - 1)


def _signed_form(shift: int, negative: bool) -> str:
    return f"{'-' if negative else '+'}2^{shift}"


def _multiplier_circuit(base: int, input_domain: Any) -> Any:
    from qiskit import QuantumCircuit

    from modular_arithmetic import append_controlled_modular_multiply

    circuit = QuantumCircuit(1 + WIDTH)
    append_controlled_modular_multiply(
        circuit, CONTROL_QUBIT, WORK_QUBITS, [], MODULUS, base, input_domain=input_domain
    )
    return circuit


def _basis_map(circuit: Any) -> tuple[int, ...]:
    """Return the basis permutation of a circuit, rejecting any non-permutation unitary."""
    from qiskit.quantum_info import Operator

    matrix = Operator(circuit).data
    images: list[int] = []
    for column in range(matrix.shape[1]):
        magnitudes = np.abs(matrix[:, column])
        row = int(np.argmax(magnitudes))
        _require(
            abs(matrix[row, column] - 1.0) <= TOLERANCE and int(np.count_nonzero(magnitudes > TOLERANCE)) == 1,
            f"column {column} is not a unit-phase basis image",
        )
        images.append(row)
    _require(sorted(images) == list(range(len(images))), "operator is not a basis permutation")
    return tuple(images)


def _expected_map(base: int, input_domain: str, negative: bool, shift: int) -> tuple[int, ...]:
    """Reference map: control 0 is the identity; control 1 follows the documented domain rule."""
    from modular_arithmetic import FULL_REGISTER

    images = [0] * (2 << WIDTH)
    for data in range(1 << WIDTH):
        images[_packed(0, data)] = _packed(0, data)
        if input_domain == FULL_REGISTER:
            target = base * data % MODULUS if data < MODULUS else data
        else:
            rotated = _rotate_left(data, shift)
            target = rotated ^ ((1 << WIDTH) - 1) if negative else rotated
        images[_packed(1, data)] = _packed(1, target)
    return tuple(images)


def _circuit_gate_counts(circuit: Any) -> dict[str, int]:
    swaps = controlled_x = edges = maximum_controls = 0
    for instruction in circuit.data:
        name = instruction.operation.name
        if name == "cswap":
            swaps += 1
            maximum_controls = max(maximum_controls, 1)
        elif name == "cx":
            controlled_x += 1
            maximum_controls = max(maximum_controls, 1)
        elif name == "mcx" or name.startswith("mcx_o"):
            edges += 1
            maximum_controls = max(maximum_controls, int(instruction.operation.num_ctrl_qubits))
        else:
            raise CensusError(f"unexpected source operation {name!r}")
    return {
        "controlled_swaps": swaps,
        "controlled_x": controlled_x,
        "basis_edges": edges,
        "maximum_control_count": maximum_controls,
    }


def _domain_record(base: int, input_domain: str, negative: bool, shift: int) -> dict[str, Any]:
    from modular_arithmetic import _verify_multiplier, multiplier_profile

    profile = multiplier_profile(MODULUS, base, input_domain=input_domain)  # type: ignore[arg-type]
    circuit = _multiplier_circuit(base, input_domain)
    inverse_circuit = _multiplier_circuit(pow(base, -1, MODULUS), input_domain)
    context = f"base {base} domain {input_domain}"

    _require(profile.scratch_qubits == 0, f"{context}: profile claims scratch qubits")
    _require(circuit.num_qubits == 1 + WIDTH, f"{context}: circuit width {circuit.num_qubits}")
    logical = {
        "controlled_swaps": profile.controlled_swap_count,
        "controlled_x": profile.controlled_x_count,
        "basis_edges": profile.basis_edge_gate_count,
        "maximum_control_count": profile.maximum_control_count,
    }
    _require(_circuit_gate_counts(circuit) == logical, f"{context}: circuit census differs from profile {logical}")

    _verify_multiplier(MODULUS, base, input_domain=input_domain)  # type: ignore[arg-type]
    observed = _basis_map(circuit)
    _require(observed == _expected_map(base, input_domain, negative, shift), f"{context}: 32-state map mismatch")

    _require(
        all(observed[_packed(1, data)] == _packed(1, base * data % MODULUS) for data in range(1, MODULUS)),
        f"{context}: control 1 does not multiply residues 1..14 by the base",
    )
    identity = tuple(range(1 << (1 + WIDTH)))
    forward_then_inverse = _basis_map(circuit.compose(inverse_circuit))
    inverse_then_forward = _basis_map(inverse_circuit.compose(circuit))
    on_declared = [
        state
        for state in range(1 << (1 + WIDTH))
        if state & 1 == 0 or input_domain == "full_register" or 1 <= state >> 1 <= MODULUS - 1
    ]
    for label, composed in (("a then a^-1", forward_then_inverse), ("a^-1 then a", inverse_then_forward)):
        _require(
            all(composed[state] == state for state in on_declared),
            f"{context}: {label} is not the identity on the declared domain",
        )
    endpoint_outputs = {str(data): observed[_packed(1, data)] >> 1 for data in (0, MODULUS)}
    return {
        "input_domain": input_domain,
        "strategy": profile.strategy,
        "scratch_qubits": profile.scratch_qubits,
        "logical_gates": logical,
        "endpoint_outputs_control_1": endpoint_outputs,
        "inverse_composition_identity_on_all_32_states": (
            forward_then_inverse == identity and inverse_then_forward == identity
        ),
        "map_verified_states": 1 << (1 + WIDTH),
    }


def _endpoint_transposition_check() -> dict[str, Any]:
    from qiskit import QuantumCircuit

    from modular_arithmetic import _append_controlled_basis_transposition

    circuit = QuantumCircuit(1 + WIDTH)
    _append_controlled_basis_transposition(circuit, CONTROL_QUBIT, WORK_QUBITS, [], 0, MODULUS)
    observed = _basis_map(circuit)
    expected = [state for state in range(1 << (1 + WIDTH))]
    expected[_packed(1, 0)] = _packed(1, MODULUS)
    expected[_packed(1, MODULUS)] = _packed(1, 0)
    _require(observed == tuple(expected), "endpoint transposition moves a state other than 0 and 15")
    gates = _circuit_gate_counts(circuit)
    _require(gates["basis_edges"] == 2 * WIDTH - 1, f"endpoint transposition uses {gates['basis_edges']} edges")
    return {"exchanged_states": [0, MODULUS], "gates": gates}


def _full_equals_nonzero_then_transposition(base: int, negative: bool) -> None:
    """The full-register circuit is the nonzero-residue circuit, plus the endpoint transposition when negated."""
    from modular_arithmetic import FULL_REGISTER, NONZERO_RESIDUES, _append_controlled_basis_transposition

    circuit = _multiplier_circuit(base, NONZERO_RESIDUES)
    if negative:
        _append_controlled_basis_transposition(circuit, CONTROL_QUBIT, WORK_QUBITS, [], 0, MODULUS)
    _require(
        _basis_map(circuit) == _basis_map(_multiplier_circuit(base, FULL_REGISTER)),
        f"base {base}: full-register circuit differs from the nonzero-residue circuit plus its endpoint rule",
    )


def _yield_record(base: int, phase_bits: int) -> dict[str, Any]:
    from factoring import (
        distribution_success,
        extract_factors,
        ideal_phase_distribution,
        reference_multiplicative_order,
    )

    order = reference_multiplicative_order(base, MODULUS)
    ideal = distribution_success(ideal_phase_distribution(order, phase_bits), phase_bits, MODULUS, base)
    uniform = distribution_success([1.0 / (1 << phase_bits)] * (1 << phase_bits), phase_bits, MODULUS, base)
    return {
        "order": order,
        "inverse": pow(base, -1, MODULUS),
        "factors_from_exact_order": list(extract_factors(base, MODULUS, order)),
        "phase_bits": phase_bits,
        "ideal_factor_yield": ideal["factorable_probability"],
        "ideal_order_recovery_probability": ideal["order_recovery_probability"],
        "uniform_null_factor_yield": uniform["factorable_probability"],
        "uniform_null_order_recovery_probability": uniform["order_recovery_probability"],
    }


def _compile_run(source: Any, backend: Any, seed: int) -> dict[str, Any]:
    from qiskit.converters import circuit_to_dag
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    from compile_evidence import OPTIMIZATION_LEVEL

    compiled = generate_preset_pass_manager(
        optimization_level=OPTIMIZATION_LEVEL, backend=backend, seed_transpiler=seed
    ).run(source)
    estimated_seconds = float(compiled.estimate_duration(backend.target))
    duration_dt = round(estimated_seconds / float(backend.dt))
    _require(
        abs(duration_dt * float(backend.dt) - estimated_seconds) <= 1e-12,
        f"seed {seed}: duration {estimated_seconds} s is not a whole number of dt",
    )
    idle_wires = sum(1 for _ in circuit_to_dag(compiled).idle_wires())
    return {
        "seed_transpiler": seed,
        "cz_count": int(compiled.count_ops().get("cz", 0)),
        "depth": int(compiled.depth()),
        "duration_dt": duration_dt,
        "duration_seconds": duration_dt * float(backend.dt),
        "logical_qubits": source.num_qubits,
        "physical_qubits_used": compiled.num_qubits - idle_wires,
    }


def _dispersion(runs: list[dict[str, Any]], metric: str) -> dict[str, int | float]:
    values = [run[metric] for run in runs]
    return {"median": statistics.median(values), "minimum": min(values), "maximum": max(values)}


def _compile_record(base: int, input_domain: str, backend: Any, seeds: tuple[int, ...]) -> dict[str, Any]:
    source = _multiplier_circuit(base, input_domain)
    runs = [_compile_run(source, backend, seed) for seed in seeds]
    return {
        "input_domain": input_domain,
        "runs": runs,
        "summary": {
            metric: _dispersion(runs, metric)
            for metric in ("cz_count", "depth", "duration_dt", "duration_seconds", "physical_qubits_used")
        },
    }


def _base_record(base: int, phase_bits: int, backend: Any, seeds: tuple[int, ...]) -> dict[str, Any]:
    from modular_arithmetic import FULL_REGISTER, NONZERO_RESIDUES, _mersenne_power_of_two, multiplier_profile

    power = _mersenne_power_of_two(MODULUS, base)
    if power is None:
        raise CensusError(f"base {base} has no signed power-of-two form modulo {MODULUS}")
    _require(
        (-1 if power.negative else 1) * (1 << power.shift) % MODULUS == base,
        f"base {base}: signed form {_signed_form(power.shift, power.negative)} does not equal the base",
    )
    domains = {
        domain: _domain_record(base, domain, power.negative, power.shift)
        for domain in (FULL_REGISTER, NONZERO_RESIDUES)
    }
    _full_equals_nonzero_then_transposition(base, power.negative)
    _require(
        domains[NONZERO_RESIDUES]["strategy"]
        == ("mersenne_signed_rotation" if power.negative else "mersenne_rotation"),
        f"base {base}: unexpected strategy {domains[NONZERO_RESIDUES]['strategy']}",
    )
    yields = _yield_record(base, phase_bits)
    useful = base in FACTOR_USEFUL_BASES
    _require(
        (yields["ideal_factor_yield"] > 0.0) == useful,
        f"base {base}: ideal factor yield {yields['ideal_factor_yield']} contradicts factor-useful={useful}",
    )
    _require(bool(yields["factors_from_exact_order"]) == useful, f"base {base}: exact-order factor extraction differs")
    _require(yields["ideal_order_recovery_probability"] > 0.0, f"base {base}: order is never recovered")
    profile = multiplier_profile(MODULUS, base, input_domain=NONZERO_RESIDUES)
    return {
        "base": base,
        "role": "factor_useful" if useful else "arithmetic_negative_control",
        "signed_form": _signed_form(power.shift, power.negative),
        "shift": power.shift,
        "negative": power.negative,
        "strategy": profile.strategy,
        **yields,
        "domains": domains,
        "compile": {domain: _compile_record(base, domain, backend, seeds) for domain in domains},
    }


def _summary_line(record: dict[str, Any]) -> str:
    full = record["domains"]["full_register"]["logical_gates"]
    nonzero = record["compile"]["nonzero_residues"]["summary"]
    return (
        f"base={record['base']} order={record['order']} inverse={record['inverse']} form={record['signed_form']} "
        f"strategy={record['strategy']} cswap={full['controlled_swaps']} cx={full['controlled_x']} "
        f"edges_full={full['basis_edges']} factor_yield={record['ideal_factor_yield']:.6f} "
        f"order_recovery={record['ideal_order_recovery_probability']:.6f} "
        f"cz_median={nonzero['cz_count']['median']} "
        f"depth={nonzero['depth']['minimum']}-{nonzero['depth']['maximum']}"
    )


def _replay_command(seeds: tuple[int, ...], portable_output: str | None) -> str:
    arguments = ['"$PYTHON"', "scripts/mod15_signed_multiplier_census.py"]
    if seeds != DEFAULT_SEEDS:
        arguments.extend(("--seeds", *(str(seed) for seed in seeds)))
    if portable_output is not None:
        arguments.extend(("--out", portable_output))
    return " ".join(arguments)


def build_census(seeds: tuple[int, ...], output_path: Path | None) -> dict[str, Any]:
    from qiskit_ibm_runtime.fake_provider import FakeFez

    from compile_evidence import OPTIMIZATION_LEVEL, _portable_output_path, _sha256, _versions
    from order_finding import order_finding_plan

    phase_bits = order_finding_plan(MODULUS, 2).phase_bits
    _require(
        len({order_finding_plan(MODULUS, base).phase_bits for base in BASES}) == 1, "phase-bit count varies by base"
    )
    backend = FakeFez()
    records = []
    for base in BASES:
        record = _base_record(base, phase_bits, backend, seeds)
        print(_summary_line(record), flush=True)
        records.append(record)
    _require(
        all(r["ideal_factor_yield"] == 0.0 for r in records if r["base"] == NEGATIVE_CONTROL_BASE),
        "negative control yields factors",
    )
    transposition = _endpoint_transposition_check()
    return {
        "schema_version": 1,
        "capture": "mod15-signed-multiplier-census",
        "qpu_executed": False,
        "replay_command": _replay_command(seeds, _portable_output_path(output_path)),
        "problem": {
            "modulus": MODULUS,
            "work_qubits": WIDTH,
            "phase_bits": phase_bits,
            "bases": list(BASES),
            "factor_useful_bases": list(FACTOR_USEFUL_BASES),
            "arithmetic_negative_control_base": NEGATIVE_CONTROL_BASE,
            "compiled_unit": "one controlled multiplier (control qubit plus four work qubits, no measurement)",
        },
        "compiler": {
            "optimization_level": OPTIMIZATION_LEVEL,
            "duration": "QuantumCircuit.estimate_duration on the FakeFez Target, in dt",
            "seeds": list(seeds),
            "versions": _versions(),
        },
        "backend": {
            "class": "qiskit_ibm_runtime.fake_provider.FakeFez",
            "evidence_surface": "static compiler target; not a live calibration or noise prediction",
            "qubits": backend.num_qubits,
            "dt_seconds": float(backend.dt),
        },
        "source": {"files_sha256": {path: _sha256(REPOSITORY_ROOT / path) for path in SOURCE_PATHS}},
        "endpoint_transposition": transposition,
        "bases": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument("--out", type=Path, help="write the census record as JSON")
    args = parser.parse_args()
    seeds = tuple(args.seeds)
    if not seeds or len(set(seeds)) != len(seeds):
        parser.error("transpiler seeds must form a nonempty set")
    started = time.perf_counter()
    try:
        record = build_census(seeds, args.out)
    except (CensusError, RuntimeError, ValueError) as error:
        print(f"census failure: {error}", file=sys.stderr)
        return 1
    if args.out is not None:
        from compile_evidence import _write_atomic

        _write_atomic(args.out, json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(
        f"census ok: {len(BASES)} bases, {len(seeds)} seeds, {time.perf_counter() - started:.1f} s",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
