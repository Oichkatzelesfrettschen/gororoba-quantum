"""Bounded fixtures for the Perceval cross-checks of the Belenos mesh and the postselected CZ."""

from __future__ import annotations

from pathlib import Path

import pytest
import qd_native_circuit as native
import qd_perceval_crosscheck as xc

ROOT = Path(__file__).resolve().parents[2]
JOB16 = ROOT / "results/quandela/runs/2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16"


def served() -> list[dict[str, object]]:
    if not (JOB16 / "raw/result.json").exists():
        pytest.skip("results/quandela job-16 is not checked out")
    return xc.served_entries(JOB16)


def test_our_mesh_unitary_equals_perceval_compute_unitary_on_two_served_meshes() -> None:
    entries = served()
    for index in (0, 2):
        row = xc.served_unitary(entries[index])
        if row["max_abs_difference"] > 1e-12 or row["unitarity_error_perceval"] > 1e-12:
            raise AssertionError((index, row))
        if (row["couplers"], row["phase_shifters"], row["mzi_cells"]) != (552, 574, 276):
            raise AssertionError(row)


def test_a_served_circuit_with_a_symbolic_expression_is_refused_not_evaluated() -> None:
    from perceval import BS, PS, Circuit, P
    from perceval.serialization import serialize

    hostile = P("__import__('os').getcwd()")
    for component in (PS(P("a") * 2 + 1), PS(hostile), BS(theta=P("t"))):
        text = str(serialize(Circuit(2).add(0, component)))
        with pytest.raises(native.NativeCircuitError, match="symbolic"):
            xc.native.circuit_from_text(text)


def test_the_served_mesh_builds_without_a_perceval_deserializer(monkeypatch: pytest.MonkeyPatch) -> None:
    import perceval.serialization as serialization

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("deserialize reached a served string")

    monkeypatch.setattr(serialization, "deserialize", forbidden)
    circuit = xc.served_circuit(served()[0])
    if circuit.ncomponents() != 552 + 574:
        raise AssertionError(circuit.ncomponents())


def test_postselected_cz_success_equals_one_ninth_and_five_minus_four_m_over_nine() -> None:
    for overlap in xc.OVERLAPS:
        for rail_input in xc.RAIL_INPUTS:
            native = xc.cz_success("postprocessed cz", rail_input, overlap)
            if abs(native - xc.our_success(rail_input, overlap)) > 1e-12:
                raise AssertionError((overlap, rail_input, native))


def test_rate_ratio_of_the_native_cz_is_five_minus_four_m() -> None:
    for overlap in xc.OVERLAPS:
        rates = {i: xc.cz_success("postprocessed cz", i, overlap) for i in xc.RAIL_INPUTS}
        ratio = rates["10"] * rates["01"] / (rates["00"] * rates["11"])
        if abs(ratio - (5.0 - 4.0 * overlap)) > 1e-9:
            raise AssertionError((overlap, ratio))


def test_heralded_cz_succeeds_with_two_over_twenty_seven_at_unit_overlap() -> None:
    for rail_input in xc.RAIL_INPUTS:
        if abs(xc.cz_success("heralded cz", rail_input, 1.0) - 2.0 / 27.0) > 1e-12:
            raise AssertionError(rail_input)


def test_optimizer_started_at_mesh_phases_reaches_fidelity_one() -> None:
    result = xc.optimizer_check(served()[0])
    if result["variable_phases"] != 574 or result["start_fidelity"] < 1 - 1e-9:
        raise AssertionError(result)
    if result["optimized_vs_target_fidelity"] < 1 - 1e-9:
        raise AssertionError(result)


def test_a_permuted_mesh_phases_lowers_the_start_fidelity() -> None:
    entry = served()[0]
    elements = xc.mesh_lib.decode(str(entry["computed_circuit"]))
    arch = xc.mesh_lib.run_architecture(elements)
    phases = xc.mesh_lib.mesh_phases(arch, elements)
    swapped = list(phases)
    swapped[100], swapped[101] = swapped[101], swapped[100]
    circuit = xc.served_circuit(entry)
    template, _ = xc.symbolic_template(circuit)
    import numpy as np
    from perceval.utils import Matrix

    target = Matrix(np.array(circuit.compute_unitary()))
    if xc.start_fidelity(template, swapped, target) > 1 - 1e-6:
        raise AssertionError("a swap of two phases left the fidelity at one")


def test_native_decomposition_reaches_a_dense_control_and_the_served_unitary_is_recorded() -> None:
    control = xc.decompose(xc.fourier(8))
    if control["status"] != "circuit" or control["max_abs_error"] > 1e-6:
        raise AssertionError(control)
    matrix = xc.served_matrix(served()[0])
    plain = xc.decompose(matrix)
    if plain["status"] != "none":
        raise AssertionError(plain)
    retry = xc.decompose(matrix, allow_error=True)
    if retry["status"] != "circuit" or xc.error_class(retry["max_abs_error"]) != "below_1e-2":
        raise AssertionError(retry)
    if xc.decompose(matrix, allow_error=True) != retry:
        raise AssertionError("the seeded retry did not repeat")


def test_a_decomposition_leaves_the_python_generator_at_the_seeded_start_state() -> None:
    import random

    xc.decompose(xc.fourier(4))
    after = random.getstate()
    xc.decompose(xc.fourier(4))
    if random.getstate() != after:
        raise AssertionError("the decomposition did not reseed the generator before its draws")


def test_the_decade_keeps_five_e_minus_sixteen_apart_from_five_e_minus_ten() -> None:
    if xc.decade(5.3e-16) == xc.decade(4.9e-10) or xc.decade(0.0) is not None:
        raise AssertionError((xc.decade(5.3e-16), xc.decade(4.9e-10)))
