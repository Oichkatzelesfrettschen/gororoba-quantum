"""Contracts of the 64- and 128-dimensional coset-block campaign.

The dimension parameter of pathion_kernel_map and pathion_coset_block leaves every D = 32 circuit and ideal law
byte-identical (pinned digests of the four D = 32 groups), the blocks of each wide operand tile the map and sum to the
nullity that cd_core certifies, the cocycle-free tiling separates, and the full-width circuit, a stabilizer simulation
of its Clifford blocks and the check script agree with the group's ideal values. Every simulation is a four-qubit
Statevector or a matrix-product-state or stabilizer sample of at most 64 qubits.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np
import pathion_wide_coset_check as check
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

import pathion_coset_block as pcb
import pathion_four_term_block as pft
import pathion_kernel_map as pkm
import pathion_parallel_coset as ppc
import pathion_wide_coset as pw
from experiments import Member, standalone_campaign_groups
from live_run import EXPERIMENT_SOURCE_MANIFEST

# Sampling seed of the simulations: index 2 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json.
SIMULATION_SEED = 25510
GROUP = pw.pathion_wide_coset_group()
IDEAL = {member.name: member.ideal for member in GROUP.members}
OPERAND_KEYS = [op.key for op in pw.WIDE_OPERANDS]
NULLITY = {"n64": 0, "o64": 28, "m64": 28, "n128": 0, "o128": 60, "m128": 60}
# Sums of the ideal N_b: the cocycle-free tiling of both targets reads -2.
IDEAL_SUM = {"n64": 0, "o64": 28, "m64": -2, "n128": 0, "o128": 60, "m128": -2}
CLIFFORD_BLOCKS = {"n64": 7, "o64": 6, "m64": 7, "n128": 15, "o128": 12, "m128": 15}
# sha256 over the member names, circuit instructions (name, qubits, clbits, parameters), ideal laws and bindings of
# each D = 32 group before the dimension parameter existed.
D32_DIGESTS = {
    "pathion_coset_map": "61678aefc3291cbf17628e555323548b8e06f85cb733c739095b5db08dd33911",
    "pathion_kernel_map": "e2253cb52b5db73a7889ba165c07b92757c93c5165c08835feacd49aa58cf718",
    "pathion_parallel_coset": "f0378dd2ffd0ba15908f70ddb8a8208fc92099cea43c0610354fc8f2b3d2a907",
    "pathion_four_term_block": "64f8ac63eefbe7cba69ca7d0250b4569856103b5eb4f52426a50b5b67593033a",
}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _required(circuit: QuantumCircuit | None) -> QuantumCircuit:
    if circuit is None:
        raise AssertionError("a Clifford block circuit is missing")
    return circuit


def _circuit_digest(circuit: QuantumCircuit) -> str:
    h = hashlib.sha256()
    h.update(f"{circuit.num_qubits},{circuit.num_clbits}".encode())
    for inst in circuit.data:
        op = inst.operation
        h.update(op.name.encode())
        h.update(repr([circuit.find_bit(q).index for q in inst.qubits]).encode())
        h.update(repr([circuit.find_bit(c).index for c in inst.clbits]).encode())
        for param in op.params:
            if isinstance(param, (list, tuple, np.ndarray)):
                h.update(np.asarray(param, dtype=complex).tobytes())
            else:
                h.update(repr(param).encode())
    return h.hexdigest()


def _group_digest(members: tuple[Member, ...]) -> str:
    h = hashlib.sha256()
    for member in members:
        part = hashlib.sha256()
        part.update(member.name.encode())
        part.update(_circuit_digest(member.circuit).encode())
        part.update(np.asarray(member.ideal, dtype=float).tobytes())
        part.update(repr(sorted((str(k), v) for k, v in (member.binding or {}).items())).encode())
        h.update(part.hexdigest().encode())
    return h.hexdigest()


def test_d32_circuits_and_ideal_laws_are_byte_identical() -> None:
    built = {
        "pathion_coset_map": pcb.coset_map_members(),
        "pathion_kernel_map": pkm.kernel_map_members(),
        "pathion_parallel_coset": ppc.parallel_members(),
        "pathion_four_term_block": pft.four_term_members(),
    }
    for name, members in built.items():
        _expect(_group_digest(members) == D32_DIGESTS[name], f"{name}: the D = 32 members changed")


def test_dimension_defaults_and_rejections() -> None:
    block = pcb.Block("b", (1, 18, 1), (19, 2, 12), 1)
    _expect(block.dim == 32 and block.tag == "e1pe18_v19-2-12_k1", f"default block {block.tag}")
    wide = pcb.Block("b", (1, 36, 1), pcb.default_basis((1, 36, 1), 64), 0, 64)
    _expect(wide.tag.startswith("d64_e1pe36_"), f"wide block tag {wide.tag}")
    with pytest.raises(ValueError, match="outside the algebra"):
        pcb.Block("b", (1, 36, 1), (37, 2, 4), 0, 32)
    with pytest.raises(ValueError, match="power of two"):
        pkm.data_qubits(48)
    _expect([pkm.data_qubits(d) for d in (32, 64, 128)] == [5, 6, 7], "data qubits")


@pytest.mark.parametrize("key", OPERAND_KEYS)
def test_certified_nullity_equals_the_aligned_pair_count(key: str) -> None:
    op = pw.BY_KEY[key]
    _expect(op.nullity == NULLITY[key], f"{key}: cd_core nullity {op.nullity}")
    _expect(pkm.aligned_pairs(op.operand, dim=op.dim) == op.nullity, f"{key}: aligned pairs")


@pytest.mark.parametrize("key", ["n64", "o64", "n128", "o128"])
def test_blocks_tile_the_map_and_sum_to_the_certified_nullity(key: str) -> None:
    op = pw.BY_KEY[key]
    tiled = pcb.tile(op.operand, op.basis, op.dim)
    aligned = [int(n) for n in tiled["aligned"]]  # type: ignore[attr-defined]
    _expect(len(aligned) == op.dim // 8, f"{key}: {len(aligned)} blocks")
    _expect(bool(tiled["covers_once"]), f"{key}: output cosets do not cover {op.dim} indices once")
    _expect(sum(aligned) == op.nullity == tiled["nullity"], f"{key}: {aligned} against {op.nullity}")
    _expect(float(tiled["contrast_gap"]) < 1e-12, f"{key}: concatenated c(y) differs from the module's c(k)")  # type: ignore[arg-type]


@pytest.mark.parametrize("key", OPERAND_KEYS)
@pytest.mark.parametrize("plus", [False, True])
def test_every_block_law_is_the_full_map_law_on_its_output_coset(key: str, plus: bool) -> None:
    op = pw.BY_KEY[key]
    for block in op.blocks():
        error = pcb.restriction_error(block, plus, cocycle_free=op.cocycle_free)
        _expect(error < 1e-12, f"{key} {block.name}: probability difference {error}")
        _expect(pcb.orientation_error(block) < 1e-12, f"{key} {block.name}: orientation phase")
    _expect(pcb.contrast_restriction_error(op.blocks()[0], cocycle_free=op.cocycle_free) < 1e-12, f"{key}: c(y)")


def test_member_ideal_laws_equal_the_state_vector_law_of_their_circuits() -> None:
    for member in GROUP.members:
        bound = member.circuit.assign_parameters(member.binding or {})
        error = float(np.abs(pcb.block_law(bound) - member.ideal).max())
        _expect(error < 1e-12, f"{member.name}: closed-form law differs by {error}")


def test_closed_form_law_equals_the_state_vector_law_at_d32() -> None:
    blocks = (pcb.Block("ba", (1, 18, 1), (19, 2, 12), 1), pcb.Block("be", (2, 27, 1), (25, 2, 9), 1))
    blocks += (pcb.Block("bt", (17, 2, -1), (19, 2, 12), 0),)
    for block in blocks:
        for plus in (False, True):
            for free in (False, True):
                reference = pcb.block_law(pcb.block_circuit(block, plus, cocycle_free=free))
                closed = pcb.block_law_closed_form(block, plus, cocycle_free=free)
                _expect(float(np.abs(reference - closed).max()) < 1e-12, f"{block.name} plus={plus} free={free}")


def test_group_structure_and_registration() -> None:
    names = [member.name for member in GROUP.members]
    _expect(len(names) == 144 and len(set(names)) == 144, f"{len(names)} members")
    _expect(names[0] == "wide_n64_k0_minus", f"the placement member is {names[0]}")
    blocks = {key: sum(n.startswith(f"wide_{key}_k") and n.endswith("_minus") for n in names) for key in OPERAND_KEYS}
    _expect(blocks == {"n64": 8, "o64": 8, "m64": 8, "n128": 16, "o128": 16, "m128": 16}, f"{blocks}")
    for member in GROUP.members:
        _expect(member.circuit.num_qubits == 4 and member.circuit.num_clbits == 4, f"{member.name}: width")
        _expect(member.ideal.size == 16 and abs(float(member.ideal.sum()) - 1.0) < 1e-12, f"{member.name}: law")


def test_group_is_registered_and_its_source_is_in_the_manifest() -> None:
    _expect(GROUP.name in {g.name for g in standalone_campaign_groups()}, "the group is not registered")
    _expect("pathion_wide_coset.py" in EXPERIMENT_SOURCE_MANIFEST, "the source manifest omits the module")


def test_ideal_summary_reads_the_nullities_and_the_mutation_separates() -> None:
    summary = GROUP.summarize(IDEAL)
    for key in OPERAND_KEYS:
        tag = f"wide_{key}"
        _expect(abs(summary[f"{tag}_nullity_estimate"] - IDEAL_SUM[key]) < 1e-9, f"{key}: N_hat")
        _expect(summary[f"{tag}_certified_nullity"] == NULLITY[key], f"{key}: certified nullity")
        _expect(summary[f"{tag}_sign_agreement"] == summary[f"{tag}_bins"], f"{key}: signs")
        _expect(abs(summary[f"{tag}_visibility_min"] - 1.0) < 1e-9, f"{key}: ideal visibility")
    _expect(abs(summary["wide_o64_selector_contrast_sum"] - 7.0) < 1e-9, "o64 selector contrast N / 4")
    _expect(abs(summary["wide_o128_selector_contrast_sum"] - 15.0) < 1e-9, "o128 selector contrast N / 4")
    _expect(abs(summary["wide_d64_target_minus_mutation"] - 30.0) < 1e-9, "o64 against its mutation")
    _expect(abs(summary["wide_d128_target_minus_mutation"] - 62.0) < 1e-9, "o128 against its mutation")
    _expect(abs(summary["wide_ratio_o128_over_o64_nullity_estimate"] - 60 / 28) < 1e-9, "nullity ratio")


def test_uniform_contraction_leaves_the_summed_estimate_and_the_ratio_unchanged() -> None:
    contracted = {name: ppc.contract(law, 0.7) for name, law in IDEAL.items()}
    summary = GROUP.summarize(contracted)
    for key in OPERAND_KEYS:
        _expect(abs(summary[f"wide_{key}_nullity_estimate"] - IDEAL_SUM[key]) < 1e-9, f"{key}: contracted N_hat")
        _expect(abs(summary[f"wide_{key}_visibility_mean"] - 0.7) < 1e-9, f"{key}: visibility")


def test_readout_asymmetry_biases_the_null_operand_and_inversion_removes_it() -> None:
    e01, e10 = [0.004, 0.006, 0.01, 0.02], [0.02, 0.03, 0.015, 0.05]

    def noisy(law: np.ndarray) -> np.ndarray:
        out = law.copy()
        for clbit in range(4):
            out = ppc.apply_readout_clbit(out, clbit, e01[clbit], e10[clbit])
        return out

    summary = GROUP.summarize({name: noisy(law) for name, law in IDEAL.items()})
    _expect(summary["wide_n128_nullity_estimate"] > 0.1, "the asymmetric channel biases the 16-block null operand")
    restored = GROUP.summarize({name: ppc.invert_readout(noisy(law), e01, e10) for name, law in IDEAL.items()})
    for key in OPERAND_KEYS:
        _expect(abs(restored[f"wide_{key}_nullity_estimate"] - IDEAL_SUM[key]) < 1e-9, f"{key}: inverted N_hat")


@pytest.mark.parametrize("key", OPERAND_KEYS)
def test_clifford_blocks_equal_the_block_law_and_their_count_is_pinned(key: str) -> None:
    op = pw.BY_KEY[key]
    clifford = 0
    for block in op.blocks():
        circuits = [pw.clifford_block_circuit(block, plus, cocycle_free=op.cocycle_free) for plus in (False, True)]
        if circuits[0] is None:
            continue
        clifford += 1
        for plus, circuit in zip((False, True), circuits, strict=True):
            reference = pcb.block_law(pcb.block_circuit(block, plus, cocycle_free=op.cocycle_free))
            _expect(
                float(np.abs(pcb.block_law(_required(circuit)) - reference).max()) < 1e-12,
                f"{key} {block.name}: Clifford law",
            )
    _expect(clifford == CLIFFORD_BLOCKS[key], f"{key}: {clifford} Clifford blocks")


def test_phase_degree_of_known_sign_functions() -> None:
    _expect(pw.phase_degree([1.0, 1.0, 1.0, 1.0]) == 0, "constant")
    _expect(pw.phase_degree([1.0, -1.0, 1.0, -1.0]) == 1, "linear")
    _expect(pw.phase_degree([1.0, 1.0, 1.0, -1.0]) == 2, "CZ")
    _expect(pw.phase_degree([1.0] * 7 + [-1.0]) == 3, "CCZ")


def test_stabilizer_simulation_of_the_clifford_blocks_reads_their_ideal_sum() -> None:
    op = pw.BY_KEY["o128"]
    chosen = [b for b in op.blocks() if pw.clifford_block_circuit(b, False) is not None]
    _expect(len(chosen) == CLIFFORD_BLOCKS["o128"], f"{len(chosen)} Clifford blocks")
    simulator = AerSimulator(method="stabilizer")
    laws: dict[str, np.ndarray] = {}
    for plus in (False, True):
        qc = QuantumCircuit(4 * len(chosen), 4 * len(chosen))
        for index, block in enumerate(chosen):
            part = _required(pw.clifford_block_circuit(block, plus))
            window = range(4 * index, 4 * index + 4)
            qc.compose(part, qubits=window, clbits=window, inplace=True)
        counts = (
            simulator.run(transpile(qc, simulator), shots=2000, seed_simulator=SIMULATION_SEED).result().get_counts()
        )
        for block, law in zip(chosen, pw.block_marginals(counts, len(chosen)), strict=True):
            laws[f"{pw.block_prefix(op, block)}_{'plus' if plus else 'minus'}"] = law
    ideal_sum = 0.0
    n_hat = 0.0
    for block in chosen:
        prefix = pw.block_prefix(op, block)
        est = ppc.estimate(
            laws[f"{prefix}_plus"], laws[f"{prefix}_minus"], IDEAL[f"{prefix}_plus"], IDEAL[f"{prefix}_minus"]
        )
        n_hat += est["nullity_estimate"]
        ideal_sum += float(pcb.output_contrast(IDEAL[f"{prefix}_plus"], IDEAL[f"{prefix}_minus"]).sum() / 2.0)
    _expect(abs(n_hat - ideal_sum) < 1e-9, f"stabilizer N_hat {n_hat} against {ideal_sum}")


@pytest.mark.parametrize("key", OPERAND_KEYS)
def test_full_width_matrix_product_state_reads_the_ideal_sum(key: str) -> None:
    op = pw.BY_KEY[key]
    circuit = pw.full_width_circuit(op, False)
    _expect(circuit.num_qubits == 4 * len(op.blocks()), f"{key}: width {circuit.num_qubits}")
    laws = pw.simulate_full_width(op, 4000, SIMULATION_SEED)
    summary = pw.summarize_operand(op, laws, IDEAL)
    n_hat = summary[f"wide_{key}_nullity_estimate"]
    _expect(abs(n_hat - IDEAL_SUM[key]) < 0.05, f"{key}: full-width N_hat {n_hat} against {IDEAL_SUM[key]}")
    _expect(summary[f"wide_{key}_sign_agreement"] == summary[f"wide_{key}_bins"], f"{key}: signs")


def _record(backend: str, shots: int, pubs: int, dt: int, *, arms: int = 144, cz_plus: int = 20) -> dict:
    names = [f"m{index}" for index in range(arms // 2)]
    members = [{"name": f"{n}_minus", "cz": 20} for n in names] + [{"name": f"{n}_plus", "cz": cz_plus} for n in names]
    members.append({"name": f"{names[0]}_minus_isolated", "cz": 20})
    group = {"group": check.GROUP, "backend": backend, "members": members, "replicas": [{"physical_qubits": [1]}] * 16}
    return {
        "groups": [group],
        "shots": shots,
        "policy": {"rep_delay_seconds": 2e-5, "operator_excluded_qubits": {}},
        "execution_pubs": [{"target_gate_lower_bound_dt": dt}] * pubs,
    }


def _wanted(record: dict) -> set[str]:
    return {m["name"] for m in record["groups"][0]["members"] if not m["name"].endswith("_isolated")}


def test_check_script_prices_with_the_drain_residuals_and_rounds_the_bill_up() -> None:
    record = _record("ibm_fez", 1000, 145, 800)
    expected = 2.3 + 1000 * 145 * (2e-5 + 800 * 4e-9 + 7.2e-6)
    _expect(abs(check.estimated_charge(record, "ibm_fez") - expected) < 1e-9, "charge model")
    kingston = check.estimated_charge(_record("ibm_kingston", 1000, 145, 800), "ibm_kingston")
    _expect(abs(kingston - expected - 1000 * 145 * 2e-6) < 1e-9, "kingston residual")
    billed = math.ceil(expected)
    _expect(check.failures(record, billed + 1.0, 16, _wanted(record)) == [], "admits at one second under the remainder")
    over = check.failures(record, float(billed), 16, _wanted(record))
    _expect(any("worst-case billed" in line for line in over), f"{over}")


def test_check_script_refuses_an_arm_that_routes_deeper_a_missing_member_and_few_replicas() -> None:
    record = _record("ibm_fez", 500, 145, 800, cz_plus=22)
    deeper = check.failures(record, 10.0, 16, _wanted(record))
    _expect(any("22 CZ" in line or "20 CZ against 22" in line for line in deeper), f"{deeper}")
    record = _record("ibm_fez", 500, 145, 800)
    missing = check.failures(record, 10.0, 16, _wanted(record) | {"wide_absent_k0_minus"})
    _expect(any("not planned" in line for line in missing), f"{missing}")
    few = check.failures(record, 10.0, 17, _wanted(record))
    _expect(any("16 replicas" in line for line in few), f"{few}")
    _expect(
        check.failures(_record("ibm_marrakesh", 500, 145, 800), 10.0, 16, set())[0].startswith("no measured"), "backend"
    )
