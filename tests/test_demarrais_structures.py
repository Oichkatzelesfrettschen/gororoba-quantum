"""Unit tests for the 16D-to-8192D Cayley-Dickson and Robert de Marrais structures module."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "gororoba_quantum") not in sys.path:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from demarrais_structures import (  # noqa: E402
    TOLERANCE,
    box_kite_6mode_unitary,
    box_kite_12mode_unitary,
    box_kite_frustrated_hamiltonian,
    box_kite_sails,
    certify_all_demarrais_structures,
    certify_cowbird_octonion_egg,
    dekatrisvoudon_8192d_decomposed_unitary,
    emanation_and_dmz_cell_counts,
    kite_chain_midden_quotient,
    pathion_emanation_table,
    run_self_test,
    sand_mandala_12mode_unitary,
    sedenion_box_kite_assessors,
    tower_taxonomy,
    verify_tower_emanation_and_dmz_scaling,
)


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_tower_taxonomy_up_to_8192d() -> None:
    tax = tower_taxonomy()
    _check(len(tax) == 14, f"expected 14 levels (0..13), got {len(tax)}")
    _check(tax[4].dimension == 16 and tax[4].name == "Sedenion", "level 4 mismatch")
    _check(tax[5].dimension == 32 and tax[5].name == "Pathion", "level 5 mismatch")
    _check(tax[6].dimension == 64 and tax[6].name == "Chingon", "level 6 mismatch")
    _check(tax[7].dimension == 128 and tax[7].name == "Routon", "level 7 mismatch")
    _check(tax[8].dimension == 256 and tax[8].name == "Voudon", "level 8 mismatch")
    _check(tax[9].dimension == 512 and tax[9].name == "Eriston", "level 9 mismatch")
    _check(tax[10].dimension == 1024 and tax[10].name == "DekaVoudon", "level 10 mismatch")
    _check(tax[11].dimension == 2048 and tax[11].name == "EndekaVoudon", "level 11 mismatch")
    _check(tax[12].dimension == 4096 and tax[12].name == "DodekaVoudon", "level 12 mismatch")
    _check(tax[13].dimension == 8192 and tax[13].name == "DekatrisVoudon", "level 13 mismatch")
    _check(tax[13].trip_count == 11_180_715, f"unexpected 8192D trip count {tax[13].trip_count}")
    _check(tax[13].midden_part_size == 1024, f"unexpected 8192D midden part size {tax[13].midden_part_size}")
    _check(tax[13].midden_vertices == 3072, f"unexpected 8192D midden vertices {tax[13].midden_vertices}")
    _check(abs(tax[13].flat_band_fraction - 0.5) < TOLERANCE, "flat band fraction != 0.5")


def test_sedenion_box_kites_and_harary_zaslavsky_spectrum() -> None:
    for s in range(1, 8):
        assessors = sedenion_box_kite_assessors(s)
        _check(len(assessors) == 6, f"S={s}: expected 6 assessors")
        sails = box_kite_sails(s)
        _check(len(sails) == 8, f"S={s}: expected 8 sails")
        zigzag = [sail for sail in sails if sail.kind == "zigzag"]
        trefoil = [sail for sail in sails if sail.kind == "trefoil"]
        _check(len(zigzag) == 2 and len(trefoil) == 6, f"S={s}: expected 2 zigzag + 6 trefoil sails")

        h6 = box_kite_frustrated_hamiltonian(s)
        evals = np.linalg.eigvalsh(h6)
        _check(np.allclose(evals, [-4.0, 0.0, 0.0, 0.0, 2.0, 2.0], atol=TOLERANCE), f"S={s}: bad spectrum {evals}")

        u6 = box_kite_6mode_unitary(s)
        _check(np.allclose(u6.T @ u6, np.eye(6), atol=TOLERANCE), f"S={s}: u6 not orthogonal")
        _check(abs(u6[0, 0]) < TOLERANCE, f"S={s}: u6[0,0] != 0")

        u12 = box_kite_12mode_unitary(s, catamaran_twist=True, lanyard_switch=0b010101)
        _check(u12.shape == (12, 12), "u12 shape != (12, 12)")
        _check(np.allclose(u12.conj().T @ u12, np.eye(12), atol=TOLERANCE), "u12 not unitary")


def test_pathion_sand_mandalas_and_dmz_sparsity() -> None:
    for s in range(1, 16):
        mandala = pathion_emanation_table(s)
        _check(mandala.total_off_diagonal_cells == 168, f"S={s}: fillable != 168")
        if s <= 8:
            _check(mandala.filled_cells == 168 and mandala.dmz_empty_cells == 0, f"S={s}: expected full 168")
            _check(not mandala.is_dmz_sparse, f"S={s}: should not be DMZ sparse")
        else:
            _check(mandala.filled_cells == 72 and mandala.dmz_empty_cells == 96, f"S={s}: expected 72 filled / 96 DMZ")
            _check(mandala.is_dmz_sparse, f"S={s}: should be DMZ sparse")
        for variant in ("mandala", "cowbird_egg", "hbk_roundabout_null"):
            u12 = sand_mandala_12mode_unitary(s, variant)
            _check(np.allclose(u12.conj().T @ u12, np.eye(12), atol=TOLERANCE), f"S={s} {variant} not unitary")


def test_cowbird_octonion_eggs_flint_certificate() -> None:
    for idx in range(4):
        cert = certify_cowbird_octonion_egg(idx)
        _check(cert.f2_closed, f"egg {idx} not F_2 closed")
        _check(cert.moufang_verified, f"egg {idx} failed Moufang")
        _check(cert.norm_multiplicative, f"egg {idx} failed norm multiplicativity")
        _check(abs(cert.character_concentration - 1.0) < TOLERANCE, f"egg {idx} concentration != 1.0")


def test_kite_chain_midden_quotients_16d_to_8192d() -> None:
    for level in range(4, 14):
        active = kite_chain_midden_quotient(level, sleeper_null=False)
        null = kite_chain_midden_quotient(level, sleeper_null=True)
        _check(active.dimension == (1 << level), f"N={level} dim mismatch")
        _check(active.part_size == (1 << (level - 3)), f"N={level} part_size mismatch")
        _check(abs(active.flat_band_fraction - 0.5) < TOLERANCE, f"N={level} flat band != 0.5")
        p_disp_active = sum(active.ideal_probabilities.get(str(m), 0.0) for m in range(2, 12))
        p_self_null = sum(null.ideal_probabilities.get(str(m), 0.0) for m in (0, 1))
        _check(abs(p_disp_active - 1.0) < TOLERANCE, f"N={level} active dispersive prob {p_disp_active} != 1.0")
        _check(abs(p_self_null - 1.0) < TOLERANCE, f"N={level} null self prob {p_self_null} != 1.0")


@pytest.mark.audit
def test_emanation_and_dmz_scaling_gpu_and_cpu() -> None:
    # Verify both GPU (prefer_gpu=True) and CPU (prefer_gpu=False) agree identically
    cpu_32 = emanation_and_dmz_cell_counts(32, 9, prefer_gpu=False)
    gpu_32 = emanation_and_dmz_cell_counts(32, 9, prefer_gpu=True)
    _check(cpu_32["active_cells"] == 72 and cpu_32["dmz_empty_cells"] == 96, "32D CPU DMZ mismatch")
    _check(gpu_32["active_cells"] == 72 and gpu_32["dmz_empty_cells"] == 96, "32D GPU DMZ mismatch")

    scaling = verify_tower_emanation_and_dmz_scaling(max_level=13, prefer_gpu=True)
    _check(len(scaling) == 10, f"expected 10 levels (4..13), got {len(scaling)}")
    _check(scaling[-1]["dimension"] == 8192, "max scaling dim != 8192")
    _check(scaling[-1]["total_fillable_cells"] == 16_752_648, "8192D fillable != 16,752,648")
    _check(scaling[-1]["s_high_active_cells"] == 24_552, "8192D high-strut active != 24,552")


def test_dekatrisvoudon_8192d_decomposed_unitary_12_and_24_modes() -> None:
    u12_ctrl = dekatrisvoudon_8192d_decomposed_unitary("lower_dim_control", modes=12, control_level=12)
    u24_ctrl = dekatrisvoudon_8192d_decomposed_unitary("lower_dim_control", modes=24, control_level=12)
    u24_act = dekatrisvoudon_8192d_decomposed_unitary("midden_root_8192d", modes=24, strut_s=1)
    u24_null = dekatrisvoudon_8192d_decomposed_unitary("sleeper_null_8192d", modes=24)

    _check(np.allclose(u12_ctrl.conj().T @ u12_ctrl, np.eye(12), atol=TOLERANCE), "u12_ctrl not unitary")
    _check(np.allclose(u24_ctrl.conj().T @ u24_ctrl, np.eye(24), atol=TOLERANCE), "u24_ctrl not unitary")
    _check(np.allclose(u24_act.conj().T @ u24_act, np.eye(24), atol=TOLERANCE), "u24_act not unitary")
    _check(np.allclose(u24_null.conj().T @ u24_null, np.eye(24), atol=TOLERANCE), "u24_null not unitary")

    # On 24 modes, lower-dimensional controls keep 0 amplitude in upper modes 14..23 from input mode 0
    upper_ctrl_prob = float(np.sum(np.abs(u24_ctrl[14:24, 0]) ** 2))
    upper_act_prob = float(np.sum(np.abs(u24_act[14:24, 0]) ** 2))
    self_null_prob = float(np.sum(np.abs(u24_null[0:2, 0]) ** 2))
    _check(abs(upper_ctrl_prob) < TOLERANCE, f"expected 0 upper prob for 4096D control, got {upper_ctrl_prob}")
    _check(abs(upper_act_prob - 0.25) < TOLERANCE, f"expected 0.25 upper prob for 8192D active, got {upper_act_prob}")
    _check(abs(self_null_prob - 1.0) < TOLERANCE, f"expected 1.0 self prob for 8192D null, got {self_null_prob}")


@pytest.mark.audit
def test_certify_all_and_self_test() -> None:
    summary = certify_all_demarrais_structures()
    _check(summary["tower_max_dim"] == 8192, "max dim != 8192")
    _check(summary["tower_max_name"] == "DekatrisVoudon", "max name != DekatrisVoudon")
    _check(summary["dmz_scaling_8192d_fillable_cells"] == 16_752_648, "certificate fillable != 16,752,648")
    _check(summary["dmz_scaling_8192d_high_strut_active_cells"] == 24_552, "certificate active != 24,552")
    _check(math.isclose(run_self_test(), 0), "run_self_test() returned non-zero")
