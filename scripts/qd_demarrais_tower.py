"""4-way photonic campaign for the 16D-to-8192D Cayley-Dickson & Robert de Marrais hierarchy.

Targets:
  - `sim:ascella` <-> `qpu:ascella` (12 spatial modes, 12 SNSPD detectors, single-rail)
  - `sim:belenos` <-> `qpu:belenos` (24 spatial modes, 12-mode active window 0..11, 24 SNSPD detectors)

Packed multi-iteration jobs (maximizing the 300 s job envelope at ~1.2 credits per QPU job):
  1. `job-dm1` (`demarrais_boxkite_catamaran`, 21 settings):
     - All 7 Sedenion Box-Kites (S = 1..7) across 3 structural arms:
       (a) Base Harary-Zaslavsky frustrated octahedron (Zigzag (-,-,-) vs. Trefoil (+,+,-) vents),
       (b) De Marrais Catamaran Twist (Royal Hunt Brocade L/U swap),
       (c) Harary-Zaslavsky Lanyard Switching Gauge (switching-equivalent spin-glass transform).
  2. `job-dm2` (`demarrais_sand_mandala_cowbird`, 24 settings):
     - 8 Pathion (32D) Sand Mandalas (Emanation Tables S = 8..15: full 168-cell S=8 vs. 72-cell DMZ I_2 * 3C_4 S=9..15),
     - 8 Cowbird Octonion Egg settings (4 Table-2 Cowbird Eggs x
       {active octonion character, associative Clifford control}),
     - 4 Hidden Box-Kite (HBK) Roundabout Theorem null controls ("all edges support zero-divisor currents or none do"),
     - 4 Catamaran-Mandala cross-level bridge settings.
  3. `job-dm3` (`demarrais_midden_tower_8192d`, 20 settings):
     - All 10 Cayley-Dickson doubling levels from N = 4 (16D Sedenion, K_{2,2,2}) through
       N = 13 (8192D DekatrisVoudon, K_{1024,1024,1024}) across 2 arms:
       (a) Exact 12-mode equitable-partition Midden Quotient unitary,
       (b) Sleeper-Cell / Roundabout Null control (U = I_12).

Usage:
  "$PYTHON" scripts/qd_demarrais_tower.py --self-test
  "$PYTHON" scripts/qd_demarrais_tower.py --build [--job all|job-dm1|job-dm2|job-dm3]
  "$PYTHON" scripts/qd_demarrais_tower.py --dry-run [--job job-dm3]
  "$PYTHON" scripts/qd_demarrais_tower.py --analyze RUN_DIR
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "gororoba_quantum") not in sys.path:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from demarrais_structures import (  # noqa: E402
    box_kite_12mode_unitary,
    certify_cowbird_octonion_egg,
    dekatrisvoudon_8192d_decomposed_unitary,
    kite_chain_midden_quotient,
    pathion_emanation_table,
    require,
    sand_mandala_12mode_unitary,
    tower_taxonomy,
)
from parallel import ordered_map  # noqa: E402

FAMILY = "demarrais_tower_8192d"
CASE_ROOT = ROOT / "results/quandela/cases" / FAMILY
PLATFORMS = ["qpu:ascella", "sim:ascella", "qpu:belenos", "sim:belenos"]

ASCELLA_MODES = 12
BELENOS_MODES = 24
WINDOW_MODES = 12

DEFAULT_SAMPLES_PER_ITERATION = 10000
DEFAULT_SHOTS_FACTOR = 10
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9

JOB_NAMES = ("job-dm1", "job-dm2", "job-dm3", "job-dm4")


def schedule_dm1() -> list[dict[str, Any]]:
    """Build the 21-setting schedule for DM-1: 7 Box-Kites x (Base, Catamaran Twist, Lanyard Switch)."""
    rows: list[dict[str, Any]] = []
    for strut_s in range(1, 8):
        rows.append(
            {
                "job": "job-dm1",
                "subfamily": "box_kite_base",
                "strut_s": strut_s,
                "catamaran_twist": False,
                "lanyard_switch": 0,
                "arm": "active_frustrated",
                "label": f"bk_s{strut_s}_base",
            }
        )
        rows.append(
            {
                "job": "job-dm1",
                "subfamily": "catamaran_twist",
                "strut_s": strut_s,
                "catamaran_twist": True,
                "lanyard_switch": 0,
                "arm": "catamaran_brocade",
                "label": f"bk_s{strut_s}_catamaran",
            }
        )
        rows.append(
            {
                "job": "job-dm1",
                "subfamily": "zaslavsky_lanyard",
                "strut_s": strut_s,
                "catamaran_twist": False,
                "lanyard_switch": 0b010101 ^ strut_s,
                "arm": "lanyard_switched",
                "label": f"bk_s{strut_s}_lanyard",
            }
        )
    return rows


def schedule_dm2() -> list[dict[str, Any]]:
    """Build the 24-setting schedule for DM-2: Pathion Sand Mandalas (S=8..15), Cowbird Eggs, HBK Nulls, Bridges."""
    rows: list[dict[str, Any]] = []
    # 1. 8 Sand Mandalas S = 8..15 (S=8 full 168-cell, S=9..15 DMZ 72-cell I_2 * 3C_4)
    for strut_s in range(8, 16):
        mandala = pathion_emanation_table(strut_s)
        rows.append(
            {
                "job": "job-dm2",
                "subfamily": "sand_mandala",
                "strut_s": strut_s,
                "filled_cells": mandala.filled_cells,
                "dmz_empty_cells": mandala.dmz_empty_cells,
                "arm": "mandala_full_168" if strut_s == 8 else "mandala_dmz_72",
                "label": f"mandala_s{strut_s}_cells{mandala.filled_cells}",
            }
        )
    # 2. 8 Cowbird Octonion Egg settings (4 eggs x {active Cowbird character, associative control})
    for egg_idx in range(4):
        cert = certify_cowbird_octonion_egg(egg_idx)
        rows.append(
            {
                "job": "job-dm2",
                "subfamily": "cowbird_egg",
                "strut_s": egg_idx + 1,
                "egg_index": egg_idx,
                "basis_indices": list(cert.basis_indices),
                "arm": "cowbird_moufang",
                "label": f"cowbird_egg{egg_idx}_active",
            }
        )
        rows.append(
            {
                "job": "job-dm2",
                "subfamily": "cowbird_control",
                "strut_s": egg_idx + 1,
                "egg_index": egg_idx,
                "basis_indices": list(cert.basis_indices),
                "arm": "hbk_roundabout_null",
                "label": f"cowbird_egg{egg_idx}_control",
            }
        )
    # 3. 4 Hidden Box-Kite (HBK) Roundabout Theorem nulls
    for hbk_idx in range(4):
        rows.append(
            {
                "job": "job-dm2",
                "subfamily": "hbk_roundabout_null",
                "strut_s": 9 + hbk_idx,
                "arm": "hbk_roundabout_null",
                "label": f"hbk_s{9 + hbk_idx}_roundabout_null",
            }
        )
    # 4. 4 Catamaran-Mandala cross-level bridges (S = 1..4 with catamaran twist + lanyard switch)
    for bridge_s in range(1, 5):
        rows.append(
            {
                "job": "job-dm2",
                "subfamily": "catamaran_mandala_bridge",
                "strut_s": bridge_s,
                "catamaran_twist": True,
                "lanyard_switch": 0b110011 ^ bridge_s,
                "arm": "catamaran_bridge",
                "label": f"bridge_s{bridge_s}_catamaran_mandala",
            }
        )
    return rows


def schedule_dm3() -> list[dict[str, Any]]:
    """Build the 20-setting schedule for DM-3: 10 CD levels (16D Sedenion -> 8192D DekatrisVoudon) x 2 arms."""
    rows: list[dict[str, Any]] = []
    tax = tower_taxonomy()
    for level in range(4, 14):
        info = tax[level]
        rows.append(
            {
                "job": "job-dm3",
                "subfamily": "kite_chain_midden_active",
                "level": level,
                "dimension": info.dimension,
                "algebra_name": info.name,
                "latin_name": info.latin_name,
                "midden_part_size": info.midden_part_size,
                "trip_count": info.trip_count,
                "sleeper_null": False,
                "arm": "midden_quotient_active",
                "label": f"n{level:02d}_{info.dimension}d_{info.name.lower()}_midden",
            }
        )
        rows.append(
            {
                "job": "job-dm3",
                "subfamily": "kite_chain_sleeper_null",
                "level": level,
                "dimension": info.dimension,
                "algebra_name": info.name,
                "latin_name": info.latin_name,
                "midden_part_size": info.midden_part_size,
                "trip_count": info.trip_count,
                "sleeper_null": True,
                "arm": "sleeper_cell_null",
                "label": f"n{level:02d}_{info.dimension}d_{info.name.lower()}_sleeper_null",
            }
        )
    return rows


def schedule_dm4() -> list[dict[str, Any]]:
    """Build the 24-setting schedule for DM-4: 8192D DekatrisVoudon Decomposed Exploration vs. Lower-Dim Controls.

    - Settings 0..8 (9 Lower-Dimensional Control Anchors): N = 4..12 (16D Sedenion -> 4096D DodekaVoudon).
    - Settings 9..20 (12 Microscopic 8192D DekatrisVoudon Decomposed Exploration Settings):
      * 7 inherited Box-Kite Midden roots (S = 1..7) inside K_{1024,1024,1024}
      * High-Strut DMZ Mandala Shell S = 2049 = 2^11 + 1 (24,552 active cells / 16,728,096 DMZ empty cells)
      * Deep 8192D Cowbird Octonion Egg (embedded at generator G = 4096)
      * 8192D Catamaran Royal Hunt Brocade Twist
      * 8192D Harary-Zaslavsky Lanyard Spin-Glass Gauge
      * 8192D Zigzag (-,-,-) vs. Trefoil (+,+,-) Chiral Projection
    - Settings 21..23 (3 Strict 8192D Falsification & Roundabout Null Controls):
      * 8192D Sleeper-Cell Midden Null (U = I)
      * 8192D Hidden Box-Kite (HBK) Roundabout Theorem Null
      * 8192D Associative Clifford Character Control
    """
    rows: list[dict[str, Any]] = []
    tax = tower_taxonomy()
    # 1. 9 Lower-dimensional control anchors (N = 4..12: 16D -> 4096D)
    for level in range(4, 13):
        info = tax[level]
        rows.append(
            {
                "job": "job-dm4",
                "subfamily": "dekatrisvoudon_8192d_decomposed",
                "variant": "lower_dim_control",
                "control_level": level,
                "dimension": info.dimension,
                "algebra_name": info.name,
                "strut_s": ((level - 4) % 7) + 1,
                "full_chip_modes": True,
                "arm": "lower_dim_control_active",
                "label": f"ctrl_n{level:02d}_{info.dimension}d_{info.name.lower()}",
            }
        )
    # 2. 7 Microscopic 8192D DekatrisVoudon Midden roots (S = 1..7 in K_{1024,1024,1024})
    for strut_s in range(1, 8):
        rows.append(
            {
                "job": "job-dm4",
                "subfamily": "dekatrisvoudon_8192d_decomposed",
                "variant": "midden_root_8192d",
                "control_level": 13,
                "dimension": 8192,
                "algebra_name": "DekatrisVoudon",
                "strut_s": strut_s,
                "full_chip_modes": True,
                "arm": "explore_8192d_midden_root",
                "label": f"explore_8192d_midden_s{strut_s}",
            }
        )
    # 3. 5 Specialized 8192D DekatrisVoudon structural probes
    for variant, s_val, arm_name, lbl in (
        ("dmz_2049_8192d", 2049, "explore_8192d_dmz_shell", "explore_8192d_dmz_s2049_24552cells"),
        ("cowbird_egg_8192d", 1, "explore_8192d_cowbird_egg", "explore_8192d_cowbird_octonion_egg"),
        ("catamaran_8192d", 2, "explore_8192d_catamaran", "explore_8192d_catamaran_brocade_twist"),
        ("lanyard_8192d", 3, "explore_8192d_lanyard", "explore_8192d_zaslavsky_lanyard_gauge"),
        ("zigzag_trefoil_8192d", 4, "explore_8192d_zigzag_trefoil", "explore_8192d_zigzag_trefoil_chiral"),
    ):
        rows.append(
            {
                "job": "job-dm4",
                "subfamily": "dekatrisvoudon_8192d_decomposed",
                "variant": variant,
                "control_level": 13,
                "dimension": 8192,
                "algebra_name": "DekatrisVoudon",
                "strut_s": s_val,
                "full_chip_modes": True,
                "arm": arm_name,
                "label": lbl,
            }
        )
    # 4. 3 Strict 8192D Null & Associative Falsification Controls
    for variant, arm_name, lbl in (
        ("sleeper_null_8192d", "sleeper_null_8192d", "null_8192d_sleeper_cell"),
        ("hbk_roundabout_null_8192d", "roundabout_null_8192d", "null_8192d_hbk_roundabout"),
        ("clifford_associative_null_8192d", "clifford_null_8192d", "null_8192d_associative_clifford"),
    ):
        rows.append(
            {
                "job": "job-dm4",
                "subfamily": "dekatrisvoudon_8192d_decomposed",
                "variant": variant,
                "control_level": 13,
                "dimension": 8192,
                "algebra_name": "DekatrisVoudon",
                "strut_s": 1,
                "full_chip_modes": True,
                "arm": arm_name,
                "label": lbl,
            }
        )
    return rows


def schedule_for_job(job_name: str) -> list[dict[str, Any]]:
    if job_name == "job-dm1":
        return schedule_dm1()
    if job_name == "job-dm2":
        return schedule_dm2()
    if job_name == "job-dm3":
        return schedule_dm3()
    if job_name == "job-dm4":
        return schedule_dm4()
    raise ValueError(f"unknown job_name {job_name!r}, expected one of {JOB_NAMES}")


def unitary_for_spec(spec: dict[str, Any], modes: int = WINDOW_MODES) -> np.ndarray:
    sub = spec["subfamily"]
    if sub == "dekatrisvoudon_8192d_decomposed":
        return dekatrisvoudon_8192d_decomposed_unitary(
            str(spec["variant"]),
            modes=modes,
            strut_s=int(spec.get("strut_s", 1)),
            control_level=int(spec.get("control_level", 13)),
        )
    if sub in ("box_kite_base", "catamaran_twist", "zaslavsky_lanyard", "catamaran_mandala_bridge"):
        return box_kite_12mode_unitary(
            int(spec["strut_s"]),
            catamaran_twist=bool(spec.get("catamaran_twist", False)),
            lanyard_switch=int(spec.get("lanyard_switch", 0)),
        )
    if sub == "sand_mandala":
        return sand_mandala_12mode_unitary(int(spec["strut_s"]), mode_variant="mandala")
    if sub == "cowbird_egg":
        return sand_mandala_12mode_unitary(int(spec["strut_s"]), mode_variant="cowbird_egg")
    if sub in ("cowbird_control", "hbk_roundabout_null"):
        return sand_mandala_12mode_unitary(int(spec["strut_s"]), mode_variant="hbk_roundabout_null")
    if sub in ("kite_chain_midden_active", "kite_chain_sleeper_null"):
        return kite_chain_midden_quotient(
            int(spec["level"]),
            sleeper_null=bool(spec["sleeper_null"]),
        ).unitary_12x12
    raise ValueError(f"unknown subfamily {sub!r}")


def build_setting_item(item: tuple[int, dict[str, Any], int]) -> tuple[dict[str, Any], dict[str, Any]]:
    idx, spec, total_modes = item
    use_full_chip = bool(spec.get("full_chip_modes", False))
    active_modes = total_modes if use_full_chip else WINDOW_MODES
    u_active = unitary_for_spec(spec, modes=active_modes)
    mesh, params = photonic_template(u_active)

    u_full = np.eye(total_modes, dtype=complex)
    u_full[:active_modes, :active_modes] = u_active

    col = [[float(v.real), float(v.imag)] for v in u_full[:, 0]]
    probs = {
        str(m): round(float(abs(u_full[m, 0]) ** 2), 6)
        for m in range(active_modes)
        if abs(u_full[m, 0]) ** 2 > TOLERANCE
    }
    p_0 = float(abs(u_full[0, 0]) ** 2 + abs(u_full[1, 0]) ** 2)
    p_dispersive = float(sum(abs(u_full[m, 0]) ** 2 for m in range(2, active_modes)))
    p_upper_8192d_shell = (
        float(sum(abs(u_full[m, 0]) ** 2 for m in range(12, active_modes))) if active_modes == 24 else 0.0
    )
    p_sum = p_0 + p_dispersive
    d_contrast = (p_dispersive - p_0) / p_sum if p_sum > TOLERANCE else 0.0

    setting_record = {
        "name": f"iter{idx:02d}-{spec['label']}",
        "observation_index": idx,
        **spec,
        "circuit_params": params,
        "column": col,
        "operator": encoded(u_full),
        "ideal": {
            "probabilities": probs,
            "self_assessor_probability": round(p_0, 6),
            "dispersive_midden_probability": round(p_dispersive, 6),
            "upper_8192d_shell_probability": round(p_upper_8192d_shell, 6),
            "d_observable": round(d_contrast, 6),
        },
    }
    return mesh, setting_record


def build_documents(
    job_name: str,
    chip: str = "ascella",
    samples_per_iteration: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
) -> dict[str, bytes]:
    require(chip in ("ascella", "belenos"), f"chip must be 'ascella' or 'belenos', got {chip!r}")
    total_modes = ASCELLA_MODES if chip == "ascella" else BELENOS_MODES
    platforms = ["qpu:ascella", "sim:ascella"] if chip == "ascella" else ["qpu:belenos", "sim:belenos"]

    schedule = schedule_for_job(job_name)
    built = ordered_map(
        build_setting_item,
        [(idx, spec, total_modes) for idx, spec in enumerate(schedule)],
        min_items=1,
    )
    template_mesh = built[0][0]
    for idx, (mesh, _) in enumerate(built):
        require(mesh == template_mesh, f"{job_name} setting {idx} mesh differs from setting 0")

    settings = [setting for _, setting in built]
    circuit = {
        **template_mesh,
        "modes": total_modes,
        "input_state": [1] + [0] * (total_modes - 1),
    }
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()

    shots_per_iteration = samples_per_iteration * shots_factor
    credit_ceiling = round(1.0 + 1e-6 * shots_per_iteration, 6)
    sec_per_iter = round(2.0 * (samples_per_iteration / float(DEFAULT_SAMPLES_PER_ITERATION)), 2)
    est_seconds = round(30.0 + len(settings) * sec_per_iter, 1)

    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": f"{FAMILY}_{chip}",
        "job": job_name,
        "platforms": platforms,
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "samples_per_iteration": samples_per_iteration,
        "shots_per_iteration": shots_per_iteration,
        "max_samples": samples_per_iteration * len(settings),
        "max_shots": shots_per_iteration * len(settings),
        "max_duration": MAX_DURATION,
        "credit_ceiling": credit_ceiling,
        "timing_model": {
            "overhead_seconds": 30.0,
            "seconds_per_iteration": sec_per_iter,
            "estimated_duration_seconds": est_seconds,
            "max_duration": MAX_DURATION,
        },
        "mitigations": [],
        "output_modes": total_modes,
        "logical_modes": list(range(WINDOW_MODES)),
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "tower_ceiling_dimension": 8192,
            "tower_ceiling_name": "DekatrisVoudon",
            "observable": "D_midden = (P_dispersive - P_self) / (P_dispersive + P_self)",
            "active_midden_ideal_d": 1.0,
            "sleeper_null_ideal_d": -1.0,
            "ideal_contrast_delta": 2.0,
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def build_all_cases(
    jobs: Sequence[str] = JOB_NAMES,
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
) -> int:
    for chip in ("ascella", "belenos"):
        for job_name in jobs:
            out_dir = CASE_ROOT / chip / job_name
            out_dir.mkdir(parents=True, exist_ok=True)
            docs = build_documents(job_name, chip=chip, samples_per_iteration=samples, shots_factor=shots_factor)
            for fname, content in docs.items():
                (out_dir / fname).write_bytes(content)
            manifest = json.loads(docs["cases.json"].decode())
            print(
                f"Built {out_dir.relative_to(ROOT)}: {manifest['iterations']} settings, "
                f"modes={manifest['output_modes']}, max_samples={manifest['max_samples']}, "
                f"credit_ceiling={manifest['credit_ceiling']}"
            )
    return 0


def check_all_cases(jobs: Sequence[str] = JOB_NAMES) -> int:
    for chip in ("ascella", "belenos"):
        for job_name in jobs:
            out_dir = CASE_ROOT / chip / job_name
            docs = build_documents(job_name, chip=chip)
            for fname, content in docs.items():
                path = out_dir / fname
                require(path.is_file(), f"missing case file {path}")
                require(path.read_bytes() == content, f"stale case file {path}")
    return 0


def analyze_run(run_dir: Path) -> dict[str, Any]:
    manifest = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    entries = results.get("iterations")
    if not isinstance(entries, list):
        # qd_platform.collect writes results.json with `counts` as a list of dicts when template iterations run
        counts_list = results.get("counts")
        require(isinstance(counts_list, list), f"{run_dir}: missing iterations or counts list in results.json")
        entries = [
            {"counts": item} if isinstance(item, dict) and "counts" not in item else item for item in counts_list
        ]

    settings = manifest["settings"]
    require(len(entries) == len(settings), f"{run_dir}: {len(entries)} result entries != {len(settings)} settings")

    reports: list[dict[str, Any]] = []
    active_d_vals: list[float] = []
    null_d_vals: list[float] = []

    unavailable: list[dict[str, Any]] = []
    for s, entry in zip(settings, entries, strict=True):
        # A partial collection marks iterations the provider never returned as {"missing": true} and a failed one
        # by its "error"; neither carries counts to compare.
        if not isinstance(entry, dict) or entry.get("missing") or "error" in entry or "counts" not in entry:
            reason = "missing" if isinstance(entry, dict) and entry.get("missing") else "error"
            if isinstance(entry, dict) and "error" in entry:
                reason = f"error: {entry['error']}"
            unavailable.append({"name": s["name"], "arm": s["arm"], "reason": reason})
            continue
        counts = entry["counts"]
        use_full_chip = bool(s.get("full_chip_modes", False))
        active_limit = int(manifest["output_modes"]) if use_full_chip else WINDOW_MODES
        c_self = 0
        c_disp = 0
        c_upper_8192d = 0
        c_leak = 0
        for state_str, cnt in counts.items():
            if not isinstance(cnt, int | float):
                continue
            occ = [int(v) for v in state_str.strip("|>").split(",")]
            occupied = [m for m, n in enumerate(occ) if n > 0]
            if len(occupied) == 1:
                m = occupied[0]
                if m in (0, 1):
                    c_self += int(cnt)
                elif 2 <= m < active_limit:
                    c_disp += int(cnt)
                    if m >= WINDOW_MODES:
                        c_upper_8192d += int(cnt)
                else:
                    c_leak += int(cnt)

        if c_self + c_disp == 0:
            # No detection on the self or dispersive modes measures nothing about this setting's observable.
            unavailable.append({"name": s["name"], "arm": s["arm"], "reason": "no accepted detections"})
            continue
        d_obs = (c_disp - c_self) / (c_self + c_disp)
        ideal_d = float(s["ideal"]["d_observable"])
        arm = s["arm"]
        if "null" in arm:
            null_d_vals.append(d_obs)
        else:
            active_d_vals.append(d_obs)

        reports.append(
            {
                "name": s["name"],
                "subfamily": s["subfamily"],
                "arm": arm,
                "c_self": c_self,
                "c_dispersive": c_disp,
                "c_upper_8192d_shell": c_upper_8192d,
                "c_leakage": c_leak,
                "d_observable": round(d_obs, 6),
                "ideal_d": round(ideal_d, 6),
                "abs_error": round(abs(d_obs - ideal_d), 6),
            }
        )

    mean_active = float(np.mean(active_d_vals)) if active_d_vals else None
    mean_null = float(np.mean(null_d_vals)) if null_d_vals else None
    contrast = mean_active - mean_null if mean_active is not None and mean_null is not None else None
    # The contrast decides only against a measured null arm and only when every setting returned counts.
    if unavailable:
        verdict = "UNADJUDICATED: settings without counts"
    elif contrast is None:
        verdict = "UNADJUDICATED: no null arm"
    else:
        verdict = "CONFORMANT" if contrast > 1.0 else "FALSIFIED"

    def rounded(value: float | None) -> float | None:
        return None if value is None else round(value, 6)

    summary = {
        "schema": "qd-demarrais-tower-analysis-v1",
        "family": manifest["family"],
        "job": manifest["job"],
        "job_id": manifest["job"],
        "iterations": len(settings),
        "mean_active_d": rounded(mean_active),
        "mean_null_d": rounded(mean_null),
        "measured_contrast_delta": rounded(contrast),
        "verdict": verdict,
        "unavailable_settings": unavailable,
        "settings": reports,
    }
    (run_dir / "analysis.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return summary


def render_circuit_svg(modes: int, output_path: Path) -> int:
    """Render vectorized Clements interferometer layout SVG via Perceval and drawsvg."""
    import perceval as pcvl

    u12 = kite_chain_midden_quotient(13, sleeper_null=False).unitary_12x12
    u_full = np.eye(modes, dtype=complex)
    u_full[: min(modes, WINDOW_MODES), : min(modes, WINDOW_MODES)] = u12[
        : min(modes, WINDOW_MODES), : min(modes, WINDOW_MODES)
    ]
    mesh, params = photonic_template(u_full)
    circuit = pcvl.Circuit(modes)
    for kind, mode, idx in mesh["ops"]:
        val = float(params[f"x{idx}"])
        if kind == "PS":
            circuit.add(int(mode), pcvl.components.PS(val))
        else:
            circuit.add((int(mode), int(mode) + 1), pcvl.components.BS.Rx(val))
    pcvl.pdisplay_to_file(circuit, str(output_path))
    require(output_path.is_file() and output_path.stat().st_size > 1000, f"failed to render SVG {output_path}")
    return int(output_path.stat().st_size)


def _twin_setting_counts(item: tuple[dict[str, Any], int, float, list[float], int]) -> dict[str, int]:
    """One setting's single-photon SLOS distribution mixed with the dark-count floor, as rounded sample counts."""
    import perceval as pcvl

    s, output_modes, dark_leak_fraction, dark_weights, samples_per_iter = item
    active_modes = output_modes if bool(s.get("full_chip_modes", False)) else WINDOW_MODES
    u_full = np.eye(output_modes, dtype=complex)
    u_full[:active_modes, :active_modes] = unitary_for_spec(s, modes=active_modes)
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(u_full)))
    backend.set_input_state(pcvl.BasicState([1] + [0] * (output_modes - 1)))
    dist = backend.prob_distribution()
    state_counts: dict[str, int] = {}
    for mode_idx in range(output_modes):
        bstate = pcvl.BasicState([1 if m == mode_idx else 0 for m in range(output_modes)])
        p_eff = (1.0 - dark_leak_fraction) * float(dist.get(bstate, 0.0)) + dark_leak_fraction * dark_weights[mode_idx]
        cnt = int(round(p_eff * samples_per_iter))
        if cnt > 0:
            state_counts[str(bstate)] = cnt
    return state_counts


def simulate_local_twin(
    job_name: str,
    platform: str,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Run local Perceval SLOS + hardware-calibrated noisy digital twin for any of the 4 photonic targets.

    - For `sim:ascella` and `sim:belenos`, models the ideal/simulator permanent distribution across all settings.
    - For `qpu:ascella` (HOM=89.1%, Transmittance=5.75%, g2=1.9%) and `qpu:belenos` (HOM=91.52%,
      Transmittance=8.99%, g2=0.72%), mixes the exact SLOS distribution with the measured SNSPD dark-count
      and multi-photon g2 leakage floor per detector port, then runs `analyze_run`.
    """
    require(platform in PLATFORMS, f"unsupported platform {platform!r}")
    chip = "belenos" if "belenos" in platform else "ascella"
    docs = build_documents(job_name, chip=chip)
    manifest = json.loads(docs["cases.json"].decode())
    settings = manifest["settings"]
    output_modes = int(manifest["output_modes"])

    # Live measured hardware detector dark-count profiles (detections/s at 13.33 MHz / 80 MHz clock)
    if platform == "qpu:ascella":
        dark_rates = np.array(
            [361.0, 398.0, 351.0, 91.0, 142.0, 433.0, 262.0, 703.0, 3412.0, 4305.0, 5815.0, 727.0],
            dtype=float,
        )
        dark_leak_fraction = 0.01315
    elif platform == "qpu:belenos":
        dark_rates = np.ones(output_modes, dtype=float) * 180.0
        dark_leak_fraction = 0.0085
    else:
        dark_rates = np.zeros(output_modes, dtype=float)
        dark_leak_fraction = 0.0

    dark_weights = dark_rates / float(np.sum(dark_rates)) if np.sum(dark_rates) > 0 else np.zeros(output_modes)

    samples_per_iter = int(manifest.get("samples_per_iteration", DEFAULT_SAMPLES_PER_ITERATION))
    weights = [float(w) for w in dark_weights]
    items = [(s, output_modes, dark_leak_fraction, weights, samples_per_iter) for s in settings]
    counts_list: list[dict[str, int]] = ordered_map(_twin_setting_counts, items, min_items=2)

    target_dir = out_dir or (ROOT / "docs/local/demarrais-twin" / f"{platform.replace(':', '_')}-{job_name}")
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "cases.json").write_bytes(docs["cases.json"])
    (target_dir / "circuit.json").write_bytes(docs["circuit.json"])
    results_payload = {
        "schema": "qd-results-local-twin-v1",
        "platform": platform,
        "job": job_name,
        "counts": counts_list,
    }
    (target_dir / "results.json").write_text(json.dumps(results_payload, indent=1) + "\n", encoding="utf-8")
    summary = analyze_run(target_dir)
    summary["platform"] = platform
    (target_dir / "analysis.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    return summary


def run_self_test() -> dict[str, Any]:
    import tempfile

    import perceval as pcvl

    tax = tower_taxonomy()
    for chip in ("ascella", "belenos"):
        for job_name in JOB_NAMES:
            docs = build_documents(job_name, chip=chip, samples_per_iteration=1000, shots_factor=10)
            manifest = json.loads(docs["cases.json"].decode())
            circuit = json.loads(docs["circuit.json"].decode())
            exp, compiled_settings = template_experiment(manifest, circuit)
            require(
                exp is not None and len(compiled_settings) == len(manifest["settings"]),
                f"{chip}/{job_name}: template_experiment failed",
            )

    with tempfile.TemporaryDirectory() as tmp:
        svg_bytes = render_circuit_svg(12, Path(tmp) / "ascella-12mode.svg")
        require(svg_bytes > 1000, f"expected SVG > 1000 bytes, got {svg_bytes}")

    # Verify SLOS exact single-photon probability distribution on 8192D DekatrisVoudon Midden Quotient (N=13)
    midden_8192 = kite_chain_midden_quotient(13, sleeper_null=False)
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(midden_8192.unitary_12x12)))
    backend.set_input_state(pcvl.BasicState([1] + [0] * 11))
    dist = backend.prob_distribution()
    p_self = sum(dist.get(pcvl.BasicState([1 if m == target else 0 for m in range(12)]), 0.0) for target in (0, 1))
    p_disp = sum(
        dist.get(pcvl.BasicState([1 if m == target else 0 for m in range(12)]), 0.0) for target in range(2, 12)
    )
    d_slos = (p_disp - p_self) / (p_disp + p_self)
    require(abs(d_slos - 1.0) < 1e-6, f"SLOS 8192D DekatrisVoudon D_midden {d_slos} != 1.0")

    result = {
        "tower_levels": len(tax),
        "max_dimension": tax[13].dimension,
        "max_name": tax[13].name,
        "slos_8192d_midden_contrast": round(float(d_slos), 6),
        "svg_schematic_bytes": svg_bytes,
    }
    print(json.dumps(result, indent=2))
    return result


def main(argv: list[str] | None = None) -> int:
    from collections.abc import Sequence as Seq

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run template compilation and SLOS self-tests")
    parser.add_argument("--build", action="store_true", help="Build case directories under results/quandela/cases/")
    parser.add_argument("--job", default="all", help="Job name (all, job-dm1, job-dm2, job-dm3)")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES_PER_ITERATION)
    parser.add_argument("--shots-factor", type=int, default=DEFAULT_SHOTS_FACTOR)
    parser.add_argument("--analyze", type=Path, help="Analyze a collected run directory")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0
    if args.build:
        jobs: Seq[str] = JOB_NAMES if args.job == "all" else [args.job]
        return build_all_cases(jobs=jobs, samples=args.samples, shots_factor=args.shots_factor)
    if args.analyze:
        print(json.dumps(analyze_run(args.analyze), indent=2))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
