"""Contracts of the 64- and 128-dimensional coset-block campaign.

The dimension parameter of pathion_kernel_map and pathion_coset_block leaves every D = 32 circuit and ideal law
byte-identical (pinned digests of the four D = 32 groups), the blocks of each wide operand tile the map and sum to the
nullity that cd_core certifies, the cocycle-free tiling separates, and the full-width circuit, a stabilizer simulation
of its Clifford blocks and the check script agree with the group's ideal values. Every simulation is a four-qubit
Statevector or a matrix-product-state or stabilizer sample of at most 64 qubits.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pathion_wide_coset_check as check
import pytest
import threadpoolctl
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
GROUP_D32 = pw.pathion_wide_coset_d32_group()
# The ideal law of every block arm, under its body name wide_<operand>_k<coset>_<arm>.
IDEAL = {name: law for name, _, law in GROUP.body_templates}
OPERAND_KEYS = [op.key for op in pw.WIDE_OPERANDS]
NULLITY = {"n64": 0, "o64": 28, "m64": 28, "n128": 0, "o128": 60, "m128": 60}
# Sums of the ideal N_b: the cocycle-free tiling of both targets reads -2.
IDEAL_SUM = {"n64": 0, "o64": 28, "m64": -2, "n128": 0, "o128": 60, "m128": -2}
CLIFFORD_BLOCKS = {"n64": 7, "o64": 6, "m64": 7, "n128": 15, "o128": 12, "m128": 15}
# sha256 over the member names, circuit instructions (name, qubits, clbits, parameters), ideal laws and bindings of
# each D = 32 group before the dimension parameter existed. The bytes hold the rounding of the Haswell OpenBLAS core:
# np.linalg.eigh in pathion_four_term_block rounds its eigenvectors differently on an AVX-512 core, so the digests
# bind only the Haswell identity (docs/design/native-numeric-replay.md, "Contract" 3 and 4).
D32_DIGESTS = {
    "pathion_coset_map": "61678aefc3291cbf17628e555323548b8e06f85cb733c739095b5db08dd33911",
    "pathion_kernel_map": "e2253cb52b5db73a7889ba165c07b92757c93c5165c08835feacd49aa58cf718",
    "pathion_parallel_coset": "f0378dd2ffd0ba15908f70ddb8a8208fc92099cea43c0610354fc8f2b3d2a907",
    "pathion_four_term_block": "64f8ac63eefbe7cba69ca7d0250b4569856103b5eb4f52426a50b5b67593033a",
}
# Member names, circuit digests, ideal laws and bindings of the four D = 32 groups as built on the Haswell core.
D32_REFERENCE = Path(__file__).resolve().parents[1] / "data" / "pathion_d32_members.json"
# Absolute bound of an ideal law entry or a binding angle across arithmetic identities: the eigensolver and
# state-vector rounding differences measure about 1e-15, and the smallest structural change of a D = 32 member
# moves a law entry by far more.
D32_BOUND = 1e-12


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


def _snapshot(members: tuple[Member, ...]) -> list[dict[str, Any]]:
    """Name, circuit digest, ideal law and binding of each member, floats as hexadecimal strings, in member order."""
    ideal_rows = [np.asarray(member.ideal, dtype=float) for member in members]
    return [
        {
            "name": member.name,
            "circuit": _circuit_digest(member.circuit),
            "shape": list(ideal.shape),
            "ideal": [float(x).hex() for x in ideal.ravel()],
            "binding": {str(k): float(v).hex() for k, v in sorted((member.binding or {}).items(), key=str)},
        }
        for member, ideal in zip(members, ideal_rows, strict=True)
    ]


def _bounded_differences(reference: list[dict[str, Any]], built: list[dict[str, Any]], bound: float) -> list[str]:
    """Differences between two snapshots: names, member order, circuit digests, shapes and binding keys must be
    equal; ideal entries and binding angles must be finite and lie within ``bound`` absolute of the reference."""
    if [row["name"] for row in reference] != [row["name"] for row in built]:
        return ["member names or order differ"]
    found: list[str] = []
    for ref, row in zip(reference, built, strict=True):
        name = ref["name"]
        if ref["circuit"] != row["circuit"]:
            found.append(f"{name}: circuit")
        if ref["shape"] != row["shape"] or len(ref["ideal"]) != len(row["ideal"]):
            found.append(f"{name}: ideal shape")
            continue
        if sorted(ref["binding"]) != sorted(row["binding"]):
            found.append(f"{name}: binding keys")
            continue
        pairs = [
            *zip(ref["ideal"], row["ideal"], strict=True),
            *((ref["binding"][k], row["binding"][k]) for k in ref["binding"]),
        ]
        for want, got in pairs:
            low, high = float.fromhex(want), float.fromhex(got)
            if not (np.isfinite(low) and np.isfinite(high)) or abs(low - high) > bound:
                found.append(f"{name}: {want} against {got}")
                break
    return found


def _is_haswell_identity() -> bool:
    """True when the OpenBLAS libraries bundled with numpy and scipy, which run np.linalg.eigh and the matrix
    products of the D = 32 builders, selected the Haswell core, the identity the pinned digests bind. Aer's own
    OpenBLAS selects Zen on AMD and plays no part in those builders."""
    cores = [
        pool.get("architecture")
        for pool in threadpoolctl.threadpool_info()
        if pool.get("internal_api") == "openblas" and "scipy_openblas" in Path(pool["filepath"]).name
    ]
    return bool(cores) and all(core == "Haswell" for core in cores)


def _d32_groups() -> dict[str, tuple[Member, ...]]:
    return {
        "pathion_coset_map": pcb.coset_map_members(),
        "pathion_kernel_map": pkm.kernel_map_members(),
        "pathion_parallel_coset": ppc.parallel_members(),
        "pathion_four_term_block": pft.four_term_members(),
    }


def test_d32_circuits_and_ideal_laws_are_byte_identical() -> None:
    """Exact bytes on the Haswell identity; names, order and circuits exact and floats within D32_BOUND elsewhere."""
    reference = json.loads(D32_REFERENCE.read_text())
    haswell = _is_haswell_identity()
    for name, members in _d32_groups().items():
        if haswell:
            _expect(_group_digest(members) == D32_DIGESTS[name], f"{name}: the D = 32 members changed")
        differences = _bounded_differences(reference[name], _snapshot(members), D32_BOUND)
        _expect(not differences, f"{name}: the D = 32 members changed beyond {D32_BOUND}: {differences[:3]}")


def test_d32_bounded_comparison_rejects_perturbed_members() -> None:
    """Mutation control: a 1e-9 move of one ideal entry or one binding angle, a rename, a lost member, a NaN and a
    changed circuit digest each fail the bounded comparison, and a 1e-13 move passes it."""
    reference = json.loads(D32_REFERENCE.read_text())["pathion_four_term_block"]
    built = _snapshot(pft.four_term_members())
    _expect(not _bounded_differences(reference, built, D32_BOUND), "the unperturbed members differ")

    def shift(value: str, delta: float) -> str:
        return (float.fromhex(value) + delta).hex()

    row = next(
        i for i, member in enumerate(built) if member["binding"] and any(x != "0x0.0p+0" for x in member["ideal"])
    )
    key = sorted(built[row]["binding"])[0]
    mutants: dict[str, list[dict[str, Any]]] = {}
    for label, delta in (("ideal", 1e-9), ("binding", 1e-9)):
        mutant = copy.deepcopy(built)
        if label == "ideal":
            mutant[row]["ideal"][0] = shift(mutant[row]["ideal"][0], delta)
        else:
            mutant[row]["binding"][key] = shift(mutant[row]["binding"][key], delta)
        mutants[label] = mutant
    renamed = copy.deepcopy(built)
    renamed[row]["name"] += "_renamed"
    mutants["rename"] = renamed
    mutants["lost member"] = built[:-1]
    swapped = copy.deepcopy(built)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    mutants["order"] = swapped
    nan = copy.deepcopy(built)
    nan[row]["ideal"][0] = float("nan").hex()
    mutants["nan"] = nan
    circuit = copy.deepcopy(built)
    circuit[row]["circuit"] = "0" * 64
    mutants["circuit"] = circuit
    for label, mutant in mutants.items():
        _expect(bool(_bounded_differences(reference, mutant, D32_BOUND)), f"the {label} mutant passes the bound")
    inside = copy.deepcopy(built)
    inside[row]["ideal"][0] = shift(inside[row]["ideal"][0], 1e-13)
    inside[row]["binding"][key] = shift(inside[row]["binding"][key], 1e-13)
    _expect(not _bounded_differences(reference, inside, D32_BOUND), "a 1e-13 move fails the bound")


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


def test_body_ideal_laws_equal_the_state_vector_law_of_their_bound_templates() -> None:
    bindings = dict(GROUP_D32.body_bindings)
    for name, template, ideal in GROUP_D32.body_templates:
        error = float(np.abs(pcb.block_law(template.assign_parameters(bindings[name])) - ideal).max())
        _expect(error < 1e-12, f"{name}: closed-form law differs by {error}")
    for member in GROUP.members:
        bound = member.circuit.assign_parameters(member.binding or {})
        _expect(float(np.abs(pcb.block_law(bound) - member.ideal).max()) < 1e-12, f"{member.name}: first body law")


def test_closed_form_law_equals_the_state_vector_law_at_d32() -> None:
    blocks = (
        pcb.Block("ba", (1, 18, 1), (19, 2, 12), 1),
        pcb.Block("be", (2, 27, 1), (25, 2, 9), 1),
        pcb.Block("bt", (17, 2, -1), (19, 2, 12), 0),
    )
    for block in blocks:
        for plus in (False, True):
            for free in (False, True):
                reference = pcb.block_law(pcb.block_circuit(block, plus, cocycle_free=free))
                closed = pcb.block_law_closed_form(block, plus, cocycle_free=free)
                _expect(float(np.abs(reference - closed).max()) < 1e-12, f"{block.name} plus={plus} free={free}")


def test_group_holds_one_member_per_operand_arm_with_one_body_per_placement() -> None:
    names = [member.name for member in GROUP.members]
    _expect(names[0] == "wide_n64_minus" and len(names) == 12, f"members {names}")
    _expect(GROUP.per_placement_laws and GROUP.placed_summary is not None, "the group is not per-placement")
    templates = {name: (circuit, ideal) for name, circuit, ideal in GROUP.body_templates}
    _expect(len(templates) == 144, f"{len(templates)} bodies")
    for member in GROUP.members:
        bodies = member.replica_bodies or ()
        _expect(len(bodies) == pw.PLACEMENTS, f"{member.name}: {len(bodies)} bodies")
        _expect(member.circuit is templates[bodies[0]][0], f"{member.name}: first body is not its circuit")
        for body in bodies:
            circuit, ideal = templates[body]
            _expect(circuit.num_qubits == 4 and circuit.num_clbits == 4, f"{body}: width")
            _expect(ideal.size == 16 and abs(float(ideal.sum()) - 1.0) < 1e-12, f"{body}: law")
    _expect(
        [len(m.replica_bodies or ()) for m in GROUP_D32.members] == [pw.PLACEMENTS + 1] * 12, "d32 group: 17 bodies"
    )
    _expect(len(GROUP_D32.body_templates) == 146, f"d32 group: {len(GROUP_D32.body_templates)} bodies")


def test_placements_align_arms_and_the_blocks_of_one_dimension() -> None:
    by_member = {m.name: m.replica_bodies or () for m in GROUP.members}
    for op in pw.WIDE_OPERANDS:
        minus, plus = by_member[f"wide_{op.key}_minus"], by_member[f"wide_{op.key}_plus"]
        _expect(
            [b.removesuffix("_minus") for b in minus] == [b.removesuffix("_plus") for b in plus],
            f"{op.key}: the arms hold different blocks on a placement",
        )
        coset = [b.rsplit("_", 2)[1] for b in minus]
        blocks = len(op.blocks())
        _expect(coset[:blocks] == [f"k{k0}" for k0 in pcb.cosets(op.basis, op.dim)], f"{op.key}: block order")
        _expect(coset == coset[:blocks] * (pw.PLACEMENTS // blocks), f"{op.key}: blocks do not repeat in order")
    for dim in (64, 128):
        indices = {key: [b.rsplit("_", 2)[1] for b in by_member[f"wide_{key}{dim}_minus"]] for key in "nom"}
        _expect(indices["n"] == indices["o"] == indices["m"], f"d{dim}: target, null and mutation misaligned")
    reference = {m.name: (m.replica_bodies or ())[-1] for m in GROUP_D32.members}
    _expect(set(reference.values()) == {"wide_ref32_k0_minus", "wide_ref32_k0_plus"}, f"{set(reference.values())}")
    for name, body in reference.items():
        _expect(body.endswith(name.rsplit("_", 1)[1]), f"{name}: reference arm {body}")


def test_group_is_registered_and_its_source_is_in_the_manifest() -> None:
    _expect(GROUP.name in {g.name for g in standalone_campaign_groups()}, "the group is not registered")
    _expect("pathion_wide_coset.py" in EXPERIMENT_SOURCE_MANIFEST, "the source manifest omits the module")


def _pooled(group, laws: dict[str, np.ndarray], transform=lambda law: law) -> dict[str, float]:
    """live_run's pooled summary: each key's mean over the placements that report it, from body laws by name."""
    bodies = {member.name: member.replica_bodies or () for member in group.members}
    ideal = {name: law for name, _, law in group.body_templates}
    rows = []
    for placement in range(len(next(iter(bodies.values())))):
        dist = {name: transform(laws[names[placement]]) for name, names in bodies.items()}
        ideals = {name: ideal[names[placement]] for name, names in bodies.items()}
        rows.append(group.placed_summary(placement, dist, ideals))
    keys = list(dict.fromkeys(key for row in rows for key in row))
    return {key: float(np.mean([row[key] for row in rows if key in row])) for key in keys}


def test_ideal_summary_reads_the_nullities_and_the_mutation_separates() -> None:
    summary = pw.placed_ideal_summary(GROUP)
    for key in OPERAND_KEYS:
        tag = f"wide_{key}"
        _expect(abs(summary[f"{tag}_nullity_estimate"] - IDEAL_SUM[key]) < 1e-9, f"{key}: N_hat")
        _expect(summary[f"{tag}_certified_nullity"] == NULLITY[key], f"{key}: certified nullity")
        _expect(summary[f"{tag}_sign_agreement"] == summary[f"{tag}_bins"], f"{key}: signs")
        _expect(abs(summary[f"{tag}_visibility_mean"] - 1.0) < 1e-9, f"{key}: ideal visibility")
    _expect(abs(summary["wide_o64_selector_contrast_sum"] - 7.0) < 1e-9, "o64 selector contrast N / 4")
    _expect(abs(summary["wide_o128_selector_contrast_sum"] - 15.0) < 1e-9, "o128 selector contrast N / 4")
    _expect(abs(summary["wide_d64_target_minus_mutation"] - 30.0) < 1e-9, "o64 against its mutation")
    _expect(abs(summary["wide_d128_target_minus_mutation"] - 62.0) < 1e-9, "o128 against its mutation")
    _expect(abs(summary["wide_d128_target_minus_null"] - 60.0) < 1e-9, "o128 against its null control")
    _expect("wide_o128_k0_nullity_estimate" in summary, "per-block keys are reported")


def test_the_pooled_summary_equals_the_ideal_sum_of_the_one_shot_blocks() -> None:
    pooled = pw.placed_ideal_summary(GROUP)
    for op in pw.WIDE_OPERANDS:
        whole = pw.operand_sum(op, IDEAL, IDEAL)
        for key, value in whole.items():
            if key.endswith("_visibility_min"):
                continue
            _expect(abs(pooled[key] - value) < 1e-9, f"{op.key}: {key} pooled {pooled[key]} against the sum {value}")


def test_the_d32_group_reports_the_reference_block_once_per_operand_pair() -> None:
    summary = pw.placed_ideal_summary(GROUP_D32)
    keys = [k for k in summary if k.startswith("wide_ref32_")]
    _expect(len(keys) == 6 * 6, f"{len(keys)} reference keys")
    _expect(all(abs(summary[f"wide_ref32_{op.key}_nullity_estimate"]) < 1e-9 for op in pw.WIDE_OPERANDS), "null block")
    plain = pw.placed_ideal_summary(GROUP)
    _expect(all(abs(summary[k] - plain[k]) < 1e-9 for k in plain), "the reference placement alters an operand value")


def test_uniform_contraction_leaves_the_summed_estimate_unchanged() -> None:
    summary = _pooled(GROUP, IDEAL, lambda law: ppc.contract(law, 0.7))
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

    noisy_laws = {name: noisy(law) for name, law in IDEAL.items()}
    _expect(_pooled(GROUP, noisy_laws)["wide_n128_nullity_estimate"] > 0.1, "the channel biases the null operand")
    restored = _pooled(GROUP, noisy_laws, lambda law: ppc.invert_readout(law, e01, e10))
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
    summary = pw.operand_sum(op, laws, IDEAL)
    n_hat = summary[f"wide_{key}_nullity_estimate"]
    _expect(abs(n_hat - IDEAL_SUM[key]) < 0.05, f"{key}: full-width N_hat {n_hat} against {IDEAL_SUM[key]}")
    _expect(summary[f"wide_{key}_sign_agreement"] == summary[f"wide_{key}_bins"], f"{key}: signs")


def _record(backend: str, shots: int, pubs: int, dt: int, *, plus_cz: int = 20, replicas: int = 16) -> dict:
    members = []
    for op in pw.WIDE_OPERANDS:
        for arm in ("minus", "plus"):
            cz = [plus_cz if arm == "plus" and op.key == "o128" else 20] * replicas
            bodies = [f"b{index}" for index in range(replicas)]
            members.append({"name": f"wide_{op.key}_{arm}", "cz": 20, "replica_cz": cz, "replica_bodies": bodies})
    members.append({"name": "wide_n64_minus_isolated", "cz": 20})
    group = {
        "group": "pathion_wide_coset",
        "backend": backend,
        "members": members,
        "replicas": [{"physical_qubits": [1]}] * replicas,
    }
    return {
        "groups": [group],
        "shots": shots,
        "policy": {"rep_delay_seconds": 2e-5, "operator_excluded_qubits": {}},
        "execution_pubs": [{"target_gate_lower_bound_dt": dt}] * pubs,
    }


def test_check_script_prices_the_drain_residual_and_the_per_pub_term_against_the_ceiling() -> None:
    record = _record("ibm_fez", 10000, 13, 800)
    expected = 2.3 + 13 * (10000 * (2e-5 + 800 * 4e-9 + 7.2e-6) + 5.7e-3)
    _expect(abs(check.estimated_charge(record, "ibm_fez") - expected) < 1e-9, "charge model")
    kingston = check.estimated_charge(_record("ibm_kingston", 10000, 13, 800), "ibm_kingston")
    _expect(abs(kingston - (2.3 + 13 * (10000 * (2e-5 + 800 * 4e-9 + 9.2e-6) + 2.6e-3))) < 1e-9, "kingston terms")
    _expect(check.failures(record, expected + 0.41, 16) == [], "admits 0.4 s under the remainder")
    over = check.failures(record, expected + 0.39, 16)
    _expect(any("worst-case charge" in line for line in over), f"{over}")
    no_reference = _record("ibm_fez", 10000, 13, 800)
    for group in no_reference["groups"]:
        group["members"] = [m for m in group["members"] if not m["name"].endswith("_isolated")]
    _expect(check.failures(no_reference, expected + 1.0, 16) == [], "the isolated reference is optional")


def test_check_script_refuses_an_arm_that_routes_deeper_a_missing_member_and_a_wrong_replica_count() -> None:
    deeper = check.failures(_record("ibm_fez", 500, 13, 800, plus_cz=22), 10.0, 16)
    _expect(any("against" in line and "plus arm" in line for line in deeper), f"{deeper}")
    record = _record("ibm_fez", 500, 13, 800)
    missing = check.failures(
        record, 10.0, 16, {m["name"] for m in record["groups"][0]["members"]} | {"wide_absent_minus"}
    )
    _expect(any("not planned" in line for line in missing), f"{missing}")
    few = check.failures(record, 10.0, 17)
    _expect(any("16 replicas, not 17" in line for line in few), f"{few}")
    many = check.failures(_record("ibm_fez", 500, 13, 800, replicas=17), 10.0, 16)
    _expect(any("17 replicas, not 16" in line for line in many), f"{many}")
    _expect(check.failures(_record("ibm_marrakesh", 500, 13, 800), 10.0, 16)[0].startswith("no measured"), "backend")


def test_the_d32_group_expects_seventeen_placements_by_default() -> None:
    record = _record("ibm_fez", 500, 13, 800, replicas=17)
    record["groups"][0]["group"] = "pathion_wide_coset_d32"
    _expect(check.failures(record, 10.0) == [], f"{check.failures(record, 10.0)}")
