"""Contracts of the wide parallel coset-block campaign: member structure, the flip twin's complemented law, the
mirrored repeats, and the predicted signatures of a readout-asymmetry channel and a symmetric contraction on the null
operand. Every check is Statevector or confusion-matrix arithmetic on four qubits."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pathion_parallel_coset_check as ppc_check

import pathion_coset_block as pcb
import pathion_kernel_map as pkm
import pathion_parallel_coset as ppc

GROUP = ppc.pathion_parallel_coset_group()
IDEAL = {member.name: member.ideal for member in GROUP.members}
NULL = (1, 17, 1)
NONNULL = (1, 18, 1)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _distributions(transform: Callable[[str, np.ndarray], np.ndarray]) -> dict[str, np.ndarray]:
    return {name: transform(name, law) for name, law in IDEAL.items()}


def _null_key(key: str) -> str:
    return f"cmap_{pkm.operand_tag(NULL)}_{key}"


def test_member_structure_and_placement_member() -> None:
    names = [member.name for member in GROUP.members]
    _expect(len(names) == 111 and len(set(names)) == 111, f"{len(names)} members, {len(set(names))} distinct")
    _expect(names[0] == "cmap_e1pe17_k0_minus", f"the placement member is {names[0]}")
    _expect(sum(n.startswith("cmap_") for n in names) == 64, "the retained map keeps its 64 members")
    _expect(sum(n.startswith("ftb_") for n in names) == 15, "two four-term blocks of eight and seven arms")
    _expect(sum(n.startswith("cflip_") for n in names) == 16, "flip twins of eight blocks")
    _expect(sum(n.startswith("crep_") for n in names) == 16, "repeats of eight blocks")


def test_repeats_mirror_the_base_arm_order() -> None:
    names = [member.name for member in GROUP.members]
    base = [n for n in names if n.startswith("cmap_e1pe17_k0_")]
    rep = [n for n in names if n.startswith("crep_e1pe17_k0_")]
    _expect(base == ["cmap_e1pe17_k0_minus", "cmap_e1pe17_k0_plus"], f"{base}")
    _expect(rep == ["crep_e1pe17_k0_plus", "crep_e1pe17_k0_minus"], f"{rep}")
    by_name = {member.name: member for member in GROUP.members}
    for name in rep:
        source = by_name[name.replace("crep_", "cmap_", 1)]
        _expect(
            by_name[name].circuit is source.circuit and by_name[name].binding == source.binding, f"{name}: template"
        )


def test_flip_twin_law_is_the_base_law_with_every_index_complemented() -> None:
    for operand, k0, _block in ppc.control_blocks():
        prefix = ppc.block_prefix(operand, k0)
        for arm in ("minus", "plus"):
            flipped = IDEAL[f"{prefix.replace('cmap_', 'cflip_', 1)}_{arm}"]
            base = IDEAL[f"{prefix}_{arm}"]
            _expect(float(np.abs(flipped - ppc.deflip(base)).max()) < 1e-12, f"{prefix} {arm}: complemented law")


def test_ideal_laws_give_the_ideal_summary_and_zero_controls() -> None:
    summary = GROUP.summarize(IDEAL)
    _expect(abs(summary[_null_key("nullity_estimate")]) < 1e-12, "null nullity estimate")
    _expect(abs(summary[f"cmap_{pkm.operand_tag(NONNULL)}_nullity_estimate"] - 12.0) < 1e-9, "nullity-12 estimate")
    for key in ("odd_half_sum", "even_half_sum", "within_minus_half_sum", "within_plus_half_sum", "pair_half_sum_gap"):
        _expect(abs(summary[_null_key(key)]) < 1e-12, f"{key} is zero on the ideal null operand")
    _expect(abs(summary[f"cmap_{pkm.operand_tag(NONNULL)}_even_nullity"] - 12.0) < 1e-9, "even part of N = 12")
    _expect(abs(summary[f"cmap_{pkm.operand_tag(NONNULL)}_odd_nullity"]) < 1e-9, "odd part of N = 12")


def test_readout_asymmetry_is_odd_under_the_flip_and_symmetric_contraction_is_zero() -> None:
    e01, e10 = 0.005, 0.030

    def readout(name: str, law: np.ndarray) -> np.ndarray:
        return ppc.apply_readout(law, e01, e10)

    asym = GROUP.summarize(_distributions(readout))
    odd = asym[_null_key("odd_half_sum")]
    even = asym[_null_key("even_half_sum")]
    base = asym[_null_key("nullity_estimate")]
    flip = asym[_null_key("flip_nullity_estimate")]
    _expect(base > 0.05, f"the base null estimate reads {base} under e10 > e01")
    _expect(flip < -0.05, f"the flip twin reads {flip}, opposite in sign")
    _expect(abs(even) < 0.02 * abs(odd) + 1e-12, f"the even part {even} against the odd part {odd}")

    def contraction(name: str, law: np.ndarray) -> np.ndarray:
        return ppc.contract(law, 0.8)

    sym = GROUP.summarize(_distributions(contraction))
    for key in ("nullity_estimate", "odd_half_sum", "even_half_sum", "within_minus_half_sum"):
        _expect(abs(sym[_null_key(key)]) < 1e-12, f"{key} under symmetric contraction: {sym[_null_key(key)]}")
    _expect(abs(sym[f"cmap_{pkm.operand_tag(NONNULL)}_nullity_estimate"] - 12.0) < 1e-9, "N_hat holds at V = 0.8")


def test_population_bias_before_the_x_is_even_under_the_flip() -> None:
    """A classical bit-flip bias acting before the X lands on both members in the base frame, so the flip leaves it in
    the even part; the same bias after the X (the readout channel) lands in the odd part."""
    e01, e10 = 0.005, 0.030

    def before_x(name: str, law: np.ndarray) -> np.ndarray:
        if name.startswith("cflip_"):
            return ppc.deflip(ppc.apply_readout(ppc.deflip(law), e01, e10))
        return ppc.apply_readout(law, e01, e10)

    def after_x(name: str, law: np.ndarray) -> np.ndarray:
        return ppc.apply_readout(law, e01, e10)

    early = GROUP.summarize(_distributions(before_x))
    late = GROUP.summarize(_distributions(after_x))
    base = early[_null_key("nullity_estimate")]
    _expect(base > 0.05, f"the base null estimate reads {base}")
    _expect(abs(early[_null_key("odd_half_sum")]) < 1e-12, f"odd part {early[_null_key('odd_half_sum')]} before the X")
    _expect(
        abs(early[_null_key("even_nullity")] - base) < 1e-12,
        f"even nullity {early[_null_key('even_nullity')]} vs {base}",
    )
    _expect(
        abs(late[_null_key("even_half_sum")]) < 0.02 * abs(late[_null_key("odd_half_sum")]), "bias after the X is odd"
    )


def test_readout_asymmetry_leaves_within_arm_repeat_at_zero() -> None:
    summary = GROUP.summarize(_distributions(lambda name, law: ppc.apply_readout(law, 0.005, 0.030)))
    for key in ("within_minus_half_sum", "within_plus_half_sum", "pair_half_sum_gap"):
        _expect(abs(summary[_null_key(key)]) < 1e-12, f"{key}: copies of one arm read identically")


def test_block_templates_have_four_qubits_and_clbits() -> None:
    for member in GROUP.members:
        _expect(member.circuit.num_qubits == 4 and member.circuit.num_clbits == 4, f"{member.name}: width")
        _expect(member.ideal.size == 16 and abs(float(member.ideal.sum()) - 1.0) < 1e-12, f"{member.name}: law")


def test_control_blocks_cover_every_coset_of_both_operands() -> None:
    blocks = ppc.control_blocks()
    _expect(len(blocks) == 8, f"{len(blocks)} control blocks")
    for operand in ppc.CONTROL_OPERANDS:
        reps = [k0 for op, k0, _ in blocks if op == operand]
        _expect(reps == pcb.cosets(pcb.default_basis(operand)), f"{operand}: cosets {reps}")


def _record(backend: str, shots: int, pubs: int, dt: int, cz_flip: int = 20) -> dict:
    members = [{"name": "cmap_e1pe17_k0_minus", "cz": 20}, {"name": "cmap_e1pe17_k0_plus", "cz": 20}]
    members += [{"name": "cflip_e1pe17_k0_minus", "cz": cz_flip}, {"name": "cflip_e1pe17_k0_plus", "cz": cz_flip}]
    members += [{"name": "cmap_e1pe17_k0_minus_isolated", "cz": 20}]
    group = {
        "group": ppc_check.GROUP,
        "backend": backend,
        "members": members,
        "replicas": [{"physical_qubits": [1]}] * 12,
    }
    return {
        "groups": [group],
        "shots": shots,
        "policy": {"rep_delay_seconds": 2e-5, "operator_excluded_qubits": {}},
        "execution_pubs": [{"target_gate_lower_bound_dt": dt}] * pubs,
    }


def test_check_script_prices_the_job_with_the_measured_residual_and_admits_a_matching_plan() -> None:
    record = _record("ibm_fez", 14336, 111, 928)
    expected = 2.3 + 14336 * 111 * (2e-5 + 928 * 4e-9 + 8.2e-6)
    _expect(abs(ppc_check.estimated_charge(record, "ibm_fez") - expected) < 1e-9, "charge model")
    _expect(ppc_check.failures(record, 60.0, 10) == [], f"{ppc_check.failures(record, 60.0, 10)}")


def test_check_script_refuses_a_flip_twin_that_routes_deeper_and_a_charge_above_the_ceiling() -> None:
    deeper = ppc_check.failures(_record("ibm_fez", 14336, 111, 928, cz_flip=22), 60.0, 10)
    _expect(any("cflip_e1pe17_k0_minus" in line for line in deeper), f"{deeper}")
    over = ppc_check.failures(_record("ibm_marrakesh", 14336, 111, 928), 60.0, 10)
    _expect(any("estimated charge" in line for line in over), f"{over}")
    few = ppc_check.failures(_record("ibm_fez", 14336, 111, 928), 60.0, 13)
    _expect(any("12 replicas" in line for line in few), f"{few}")
