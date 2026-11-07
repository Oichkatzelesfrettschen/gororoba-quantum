"""Mesh-persistence discriminator for the Ascella two-block mirror failure (ledger row A5-191).

The two-block job (ORIGINAL_RUN, job db6355f7) read 9 of 46 mirrored block readings more than 0.07 apart, against an
allowance of 4; its `sim:ascella` gate run read 0 of 46 (maximum 0.0066), so the failure enters on the chip. Two
readings of the same retained counts compete
(docs/evidence/pathion-kernel-map/conjectures/mechanisms.md, section C1, and c1_anchor_map.txt):

- per-mesh fixed error: every served mesh (a compilation seed with its circuit parameters) carries its own fixed
  departure from its programmed law. The slot efficiencies come from one anchor mesh per slot, so the anchor pair's
  own error sets B/A = 1.082 where the other meshes imply about 0.99, and dividing by it produces the failures (1 of
  46 fail without the division). The signed-coherence program measured exactly this on the same chip: a seed serves
  the byte-identical mesh nine hours and twelve days later, its error persists at the counting ceiling (r 0.885 and
  0.958), and a per-seed table removes about 90 percent of the per-mesh variance
  (docs/design/ascella-signed-coherence-conformance.md, seed-repeat, long-horizon and prospective-correction cases);
- static per-shifter map: one offset or gain per physical shifter acts on every mesh, about 0.02 rad, as A5-191
  states. Fitted on one orientation it predicts the other at correlation +0.54 to +0.88 (c1_static.txt), and it
  reproduces about half the anchor excess in-sample (c1_anchor_map.txt). On unseen meshes the signed-coherence
  program found such maps carry at most about 10 percent of the per-mesh variance (new-seed score r 0.157 and 0.319).

Design. One `qpu:ascella` job of ITERATIONS iterations at SAMPLES single-photon samples each:
- replay: the 52 settings of ORIGINAL_RUN rebuilt with their own compilation seeds and circuit parameters, each
  checked byte-equal to the retained setting, in the original palindromic order, split around the fresh block;
- fresh anchors: the anchor design (A16 block p at level 1 beside block q in its kernel) at FRESH_ANCHOR_SEEDS new
  seeds, each in both slot orientations, so each seed gives its own B/A;
- fresh failing settings: the eight settings that carry the nine failing readings, each at one new seed in both
  orientations;
- fresh dark: the dark design at one new seed in both orientations.
A `sim:ascella` run of the identical request precedes the QPU job and gates it on mesh identity.

Preregistered decisions (PREREGISTERED below holds the thresholds). Each decision names what it excludes; the readings
are not exclusive, a mixture of carriers is allowed, and every decision can read "not read" (a partial run, or a
correlation input that is non-finite or constant) or "unresolved":
- mesh gate (sim run): the run's cases.json is the frozen sim-00 case byte for byte, all ITERATIONS results returned
  with their echoed requests, the replay original names are exactly the original job's 52 names once each, and every
  replay served unitary lies within 1e-6 of the original job's (largest entry modulus); otherwise the QPU job is not
  sent;
- admission: the predecessor's anchor floor, dark ceiling and sentinel share on the replay anchors and darks;
- persistence: Pearson r of the 46 calibrated replay mirror differences with the original ones. The cutoff is the
  first percentile of r under a fixed-mesh model with between-job efficiency drift (PERSISTENCE_CUTOFF: both jobs
  resampled from the original job's per-iteration click laws at SAMPLES with their own calibration rows, the replay's
  mode shares multiplied by a random per-mode ratio of the spread measured between the two retained pathion jobs;
  persistence_plan.json, which also records the no-drift and measured-drift quantiles). r at or above it
  excludes a redraw of the per-mesh errors between the jobs ("fixed per mesh"); r below it with relabeling p < ALPHA
  reads "partly fixed"; otherwise "not reproduced". A time-ordered control reads within the job: per-iteration
  persistence (l_hat - ideal against the original twin) on the replay's early half and late half, reported, and the
  early and late replayed anchors (positions 0, 1 and the last two) within the predecessor's 0.03 drift band; drift
  within the job is read only from that control;
- anchor replay: the replayed B/A within anchor_replay_band of 1.082 excludes a change of the anchor pair's error;
- fresh anchors (engineering thresholds whose classification rates persistence_plan.json records): median within
  fresh_band of the mode-fit 0.992 with standard deviation above spread_floor excludes a slot efficiency of 1.08
  ("anchor ratio follows the mesh"); every seed within fresh_band of 1.082 excludes the per-mesh anchor reading ("slot
  efficiency"); otherwise "unresolved";
- fresh failing settings: the aligned mean A = mean over the nine failing items of sign(original raw d) x fresh raw d,
  against the original mean |raw d| 0.0376 and the per-mesh raw spread 0.025 (standard error 0.0084 for nine items).
  A at or above aligned_block excludes a purely per-mesh failure ("follows the design"); A below aligned_mesh excludes
  a design-tied failure at the original size ("follows the mesh"); between them "unresolved". The two labels assume
  the two extreme readings (all of the failure tied to the design, or none); under a mixture the carried fraction
  A / 0.0376 with its 99 percent interval (half-width about 0.58 for nine items) is the reading, and the labels split
  it at one half;
- frozen map: the per-shifter gain and offset maps of c1_static.npz (x_, a_, c_ with _gain_all and _offset_all, frozen
  in commit cc8d8107c before this case) applied to each fresh iteration's returned circuit (BS.Rx convention checked)
  predict its raw slot levels; Pearson r of predicted against observed departures from the ideal, centered within
  kind; its p from relabelings that permute whole compilation-seed blocks (both orientations and both slots of a seed
  move together), one-sided at MAP_ALPHA each (Bonferroni over the two maps); "map carries" at p < MAP_ALPHA with its
  share r^2 over the ceiling 1 - (mean multinomial variance) / (observed variance); otherwise "map does not carry";
- correction: the original job's per-iteration calibrated departures applied as a per-mesh table to the replay leave at
  most the allowance (4) of 46 mirror differences above 0.07; reported with the rms before and after.

Outcome map onto A5-191: the row is rewritten to the carriers the decisions leave standing. Persistence fixed per mesh,
fresh anchor ratio following the mesh and a failure following the mesh (or a small carried fraction) with no carrying
map give "per-mesh fixed errors, the anchor pair's among them"; a carrying map adds the per-shifter clause with its
share; a design-tied carried fraction adds a block or slot term of that size; "not reproduced" leaves redraw and drift
between the jobs unresolved unless the within-job control reads drift.

Usage:
  "$PYTHON" scripts/ascella_pathion_mesh_persistence.py --plan
  "$PYTHON" scripts/ascella_pathion_mesh_persistence.py --spec-check
  "$PYTHON" scripts/ascella_pathion_mesh_persistence.py --draw DRAW --out DIR --platform {sim:ascella,qpu:ascella}
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import anu_qrng  # noqa: E402
import ascella_pathion_coset_block_pairs as pairs  # noqa: E402
from hypercomplex_cases import photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from parallel import ordered_map  # noqa: E402

FAMILY = "ascella_pathion_mesh_persistence"
ORIGINAL_RUN = "results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
ORIGINAL_SIM_RUN = "results/quandela/runs/2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00"
# The eight settings that carry the nine mirror readings above 0.07 (mirror_test.txt).
FAILING = ("a-h-NN", "b-i-NN", "c-d-TD", "c-d-TN", "c-d-TT", "e-b-TT", "g-h-TT", "i-f-TC")
FAILING_ITEMS = (
    ("a-h-NN", 1),
    ("b-i-NN", 1),
    ("c-d-TD", 0),
    ("c-d-TN", 1),
    ("c-d-TT", 1),
    ("e-b-TT", 0),
    ("e-b-TT", 1),
    ("g-h-TT", 0),
    ("i-f-TC", 1),
)
FRESH_ANCHOR_SEEDS = 7
# Draw layout, index order: fresh anchor seeds, one seed per failing setting, the dark seed, then the permutation
# and bootstrap generator seeds of the analysis.
DRAW_LAYOUT = {
    "anchor": list(range(FRESH_ANCHOR_SEEDS)),
    "failing": list(range(FRESH_ANCHOR_SEEDS, FRESH_ANCHOR_SEEDS + len(FAILING))),
    "dark": [FRESH_ANCHOR_SEEDS + len(FAILING)],
    "permutation": [FRESH_ANCHOR_SEEDS + len(FAILING) + 1],
    "map_permutation": [FRESH_ANCHOR_SEEDS + len(FAILING) + 2],
}
SEED_COUNT = FRESH_ANCHOR_SEEDS + len(FAILING) + 3
SAMPLES = pairs.SAMPLES
SHOTS = pairs.SHOTS
MAX_DURATION = pairs.MAX_DURATION
BUDGET_FRACTION = pairs.BUDGET_FRACTION
# The original job ran 52 iterations at 131,072 shots in 161 s (3.10 s each); the pairs case's 3.2 s bound is kept.
SECONDS_PER_ITERATION = pairs.SECONDS_PER_ITERATION
MAX_CREDITS = pairs.MAX_CREDITS
# Original readings the decisions compare against (mirror_test.txt, c1_anchor.txt).
ORIGINAL_BA = 1.0818
MODE_FIT_BA = 0.992
ALPHA = 0.01
MAP_ALPHA = 0.005
PERMUTATIONS = 20000
# The fixed-mesh plan (persistence_plan.json in the case directory, written by the reading script from PLAN_DRAW)
# freezes the persistence cutoff; the test rebuilds the record and checks the constant against it.
PLAN_DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T165920Z.json"
PERSISTENCE_PLAN = "results/quandela/cases/ascella_pathion_mesh_persistence/persistence_plan.json"
PERSISTENCE_CUTOFF = 0.988
PREREGISTERED: dict[str, Any] = {
    "anchor_replay_band": 0.02,
    "fresh_band": 0.03,
    "spread_floor": 0.012,
    "anchor_drift": pairs.THRESHOLDS["anchor_drift"],
    # Fresh failing settings: original mean |raw d| of the nine items and the per-mesh raw spread of all 46 raw mirror
    # differences of the original job; the aligned-mean thresholds sit at the original mean minus and plus 2.2
    # standard errors of a nine-item mean under the per-mesh reading.
    "original_failing_raw_mean": 0.0376,
    "per_mesh_raw_sd": 0.0251,
    "aligned_block": 0.0196,
    "aligned_mesh": 0.0181,
    "persistence_cutoff": PERSISTENCE_CUTOFF,
    "persistence_plan": PERSISTENCE_PLAN,
    "mirror_spread": pairs.THRESHOLDS["mirror_spread"],
    "mirror_allowance": 4,
    "mesh_identity_tolerance": 1e-6,
}
# Ascella processor record read on 2026-11-07 through qd_platform (qpu:ascella): clock 13.33 MHz, dark counts per
# mode in detections per second, HOM 88.98 percent, g2 2 percent, transmittance 5.46 percent, threshold detectors.
ASCELLA_SPEC: dict[str, Any] = {
    "clock_hz": 13.33e6,
    "dark_counts_per_s": [167, 109, 92, 108, 68, 115, 87, 89, 262, 340, 108, 157],
    "indistinguishability": 0.8898,
    "g2": 0.02,
    "transmittance": 0.0546,
    "detector": "threshold",
}


def original() -> dict[str, Any]:
    return json.loads((ROOT / ORIGINAL_RUN / "cases.json").read_bytes())


def design_by_name() -> dict[str, pairs.Design]:
    return {design.name: design for design in pairs.DESIGNS}


def replay_tasks() -> list[tuple[int, dict[str, Any], pairs.Task]]:
    """The original 52 settings as build tasks, with their own seeds; position is fixed later."""
    designs = design_by_name()
    tasks = []
    for setting in original()["settings"]:
        design = designs[setting["setting"]]
        task: pairs.Task = (
            setting["observation_index"],
            design.name,
            setting["orientation"],
            setting["seed_index"],
            setting["compilation_seed"],
            design.role,
            design.first[0],
            design.first[1],
            design.second[0],
            design.second[1],
            design.group,
        )
        tasks.append((setting["observation_index"], setting, task))
    return tasks


def fresh_entries(seeds: list[int]) -> list[tuple[str, pairs.Design, int, int, int]]:
    """(kind, design, orientation, draw index, seed) of the fresh block, failing pairs interleaved with anchors."""
    designs = design_by_name()
    entries = []
    for k, name in enumerate(FAILING):
        index = DRAW_LAYOUT["failing"][k]
        for orientation in (0, 1):
            entries.append(("fresh-failing", designs[name], orientation, index, seeds[index]))
        if k < FRESH_ANCHOR_SEEDS:
            index = DRAW_LAYOUT["anchor"][k]
            for orientation in (0, 1):
                entries.append(("fresh-anchor", pairs.ANCHOR, orientation, index, seeds[index]))
        if k == len(FAILING) // 2 - 1:
            index = DRAW_LAYOUT["dark"][0]
            for orientation in (0, 1):
                entries.append(("fresh-dark", pairs.DARK, orientation, index, seeds[index]))
    return entries


ITERATIONS = 52 + 2 * (len(FAILING) + FRESH_ANCHOR_SEEDS + 1)


def check_duration() -> float:
    per = max(SECONDS_PER_ITERATION, SHOTS / pairs.THROUGHPUT_BOUND)
    if ITERATIONS > int(BUDGET_FRACTION * MAX_DURATION / per):
        raise ValueError(f"{ITERATIONS} iterations exceed the packing margin of the {MAX_DURATION} s cut")
    return ITERATIONS * per


def level_se(level: float, samples: int = SAMPLES) -> float:
    """Binomial standard error of a level read as twice a click share: sqrt(L (2 - L) / n)."""
    return math.sqrt(level * (2 - level) / samples)


def plan() -> dict[str, Any]:
    """Sizes, counting errors, the frozen persistence plan and the predicted readings under each mechanism."""
    record = json.loads((ROOT / PERSISTENCE_PLAN).read_bytes())
    if record["persistence_cutoff"] != PERSISTENCE_CUTOFF:
        raise ValueError("PERSISTENCE_CUTOFF differs from the frozen persistence plan")
    th = PREREGISTERED
    slot_sd = math.sqrt(2) * level_se(1.0)
    design = th["original_failing_raw_mean"]
    return {
        "iterations": ITERATIONS,
        "expected_seconds": check_duration(),
        "samples_per_iteration": SAMPLES,
        "level_standard_error": {f"L={lv}": level_se(lv) for lv in (0.25, 0.5, 0.75, 1.0)},
        "persistence_plan": record,
        "predictions": {
            "per_mesh_fixed": {
                "persistence_r": f">= {PERSISTENCE_CUTOFF} (fixed-mesh median {record['r_quantiles']['0.5']:.4f})",
                "replay_ba": f"{ORIGINAL_BA} +- {th['anchor_replay_band']}",
                "fresh_ba": f"median {MODE_FIT_BA} +- {th['fresh_band']}, sd about 0.025",
                "fresh_failing_aligned_mean": f"below {th['aligned_mesh']} (near 0)",
            },
            "slot_efficiency": {
                "fresh_ba": f"every seed {ORIGINAL_BA} +- {th['fresh_band']}, sd about {slot_sd:.4f}",
                "fresh_failing_aligned_mean": f"at or above {th['aligned_block']} (near {design:.4f})",
            },
            "static_shifter_map": {
                "frozen_map": "carries at seed-block p < 0.005, with its share",
                "prior_art": "signed-coherence new-seed score r 0.157 and 0.319 (share 2.5 and 10.5 percent)",
            },
            "redraw_or_drift_between_jobs": {"persistence_r": f"below {PERSISTENCE_CUTOFF}"},
        },
    }


def spec_check(limit: int | None = None) -> dict[str, Any]:
    """Ascella's published imperfections on single-photon levels, for the anchor and every failing setting.

    Perceval's NoiseModel with the processor record's g2 and indistinguishability adds multi-photon events; the
    analysis keeps single-detected-photon events, so the check post-selects one click. Transmittance scales every
    mode alike and drops out of a ratio. Dark counts enter as a per-pulse click probability rate / clock per mode,
    against a signal click probability of about the transmittance per pulse."""
    import perceval as pcvl  # noqa: PLC0415

    designs = design_by_name()
    targets = [(pairs.ANCHOR, 0), (pairs.ANCHOR, 1)] + [(designs[name], o) for name in FAILING for o in (0, 1)]
    targets = targets[:limit] if limit else targets
    noise = pcvl.NoiseModel(g2=ASCELLA_SPEC["g2"], indistinguishability=ASCELLA_SPEC["indistinguishability"])
    worst = 0.0
    out = []
    for design, orientation in targets:
        items = [pairs.resolve(*design.first), pairs.resolve(*design.second)]
        if orientation == 1:
            items.reverse()
        psi = np.concatenate([items[0].contraction @ items[0].unit, items[1].contraction @ items[1].unit]) / math.sqrt(
            2
        )
        vector = np.concatenate([psi, [math.sqrt(max(0.0, 1 - float(psi @ psi)))]])
        full = np.eye(pairs.WIDTH, dtype=np.complex128)
        full[: pairs.ACTIVE, : pairs.ACTIVE] = pairs.householder(vector)
        levels = []
        for model in (None, noise):
            processor = pcvl.Processor("SLOS", pcvl.Unitary(pcvl.Matrix(full)), noise=model)
            processor.min_detected_photons_filter(1)
            processor.with_input(pcvl.BasicState([1] + [0] * (pairs.WIDTH - 1)))
            for mode in range(pairs.WIDTH):
                processor.add(mode, pcvl.Detector.threshold())
            probs = processor.probs()["results"]
            single = {tuple(state): p for state, p in probs.items() if sum(tuple(state)) == 1}
            total = sum(p for s, p in single.items() if sum(s[: pairs.ACTIVE]) == 1)
            shares = np.zeros(pairs.WIDTH)
            for state, p in single.items():
                shares[list(state).index(1)] += p
            slot = [2 * float(shares[list(m)].sum()) / total for m in pairs.SLOT_MODES.values()]
            levels.append(slot)
        shift = float(np.max(np.abs(np.subtract(levels[1], levels[0]))))
        worst = max(worst, shift)
        out.append({"setting": design.name, "orientation": orientation, "levels": levels[0], "noisy": levels[1]})
    dark = [rate / ASCELLA_SPEC["clock_hz"] for rate in ASCELLA_SPEC["dark_counts_per_s"]]
    dark_share = sum(dark[: pairs.ACTIVE]) / ASCELLA_SPEC["transmittance"]
    return {
        "worst_level_shift_from_g2_and_indistinguishability": worst,
        "dark_click_share_of_signal_in_modes_0_to_8": dark_share,
        "dark_level_shift_bound": 2 * dark_share,
        "settings": out,
    }


def documents(draw: Path, job: str, platform: str) -> dict[str, bytes]:
    source = json.loads(draw.read_bytes())
    anu_qrng.admit(source)
    seeds = source["values"][:SEED_COUNT]
    previous = {s["compilation_seed"] for s in original()["settings"]}
    if (
        source["type"] != "uint16"
        or len(seeds) != SEED_COUNT
        or len(set(seeds)) != SEED_COUNT
        or any(type(s) is not int or not 0 < s <= 65535 or s in previous for s in seeds)
    ):
        raise ValueError(f"the case needs {SEED_COUNT} distinct nonzero uint16 values unused by the original job")
    check_duration()
    replay = sorted(replay_tasks(), key=lambda entry: entry[0])
    fresh = fresh_entries(seeds)
    half = len(replay) // 2
    order: list[tuple[str, Any]] = (
        [("replay", entry) for entry in replay[:half]]
        + [("fresh", entry) for entry in fresh]
        + [("replay", entry) for entry in replay[half:]]
    )
    tasks: list[pairs.Task] = []
    kinds: list[str] = []
    originals: list[dict[str, Any] | None] = []
    for position, (kind, entry) in enumerate(order):
        if kind == "replay":
            _, setting, task = entry
            tasks.append((position, f"replay-{task[1]}", *task[2:]))
            kinds.append("replay")
            originals.append(setting)
        else:
            label, design, orientation, index, seed = entry
            tasks.append(
                (
                    position,
                    f"{label}-{design.name}",
                    orientation,
                    index,
                    seed,
                    design.role,
                    design.first[0],
                    design.first[1],
                    design.second[0],
                    design.second[1],
                    design.group,
                )
            )
            kinds.append(label)
            originals.append(None)
    settings = ordered_map(pairs.build_iteration, tasks, min_items=1)
    # A replay sends the retained setting verbatim under its new name and position, so its request bytes equal the
    # original's. The rebuilt setting confirms the same design: identical seed, orientation and role, and the target
    # operator and laws within 1e-12. The template decomposition is degenerate (equal columns from phases that differ
    # by pi/2), so rebuilt circuit parameters are not compared.
    request = ("compilation_seed", "orientation", "role")
    for k, (setting, kind, before) in enumerate(zip(settings, kinds, originals, strict=True)):
        if before is None:
            setting["kind"] = kind
            # "setting" names the design, as in the original manifest, so a fresh item pairs with its original.
            setting["setting"] = setting["setting"][len(kind) + 1 :]
            continue
        operator = np.array(setting["operator"]["real"]) + 1j * np.array(setting["operator"]["imaginary"])
        retained = np.array(before["operator"]["real"]) + 1j * np.array(before["operator"]["imaginary"])
        if float(np.max(np.abs(operator - retained))) > 1e-12:
            raise ValueError(f"{setting['name']}: the replay operator differs from the retained setting")
        for key in request:
            if json.dumps(setting[key], sort_keys=True) != json.dumps(before[key], sort_keys=True):
                raise ValueError(f"{setting['name']}: the replay request differs from the retained setting ({key})")
        for key in ("ideal_levels", "ideal_label_law", "column"):
            if float(np.max(np.abs(np.subtract(setting[key], before[key])))) > 1e-12:
                raise ValueError(f"{setting['name']}: the replay law differs from the retained setting ({key})")
        settings[k] = {
            **before,
            "name": setting["name"],
            "observation_index": setting["observation_index"],
            "kind": kind,
            "original_name": before["name"],
        }
    if len(settings) != ITERATIONS:
        raise ValueError("iteration count differs from ITERATIONS")
    mesh, _ = photonic_template(np.eye(pairs.ACTIVE, dtype=np.complex128))
    circuit = {**mesh, "modes": pairs.WIDTH, "input_state": [1] + [0] * (pairs.WIDTH - 1)}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    base_manifest = original()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [platform],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES * len(settings),
        "max_shots": SHOTS * len(settings),
        "max_duration": MAX_DURATION,
        "max_credits": MAX_CREDITS,
        "mitigations": [],
        "output_modes": pairs.WIDTH,
        "logical_modes": list(range(pairs.ACTIVE)),
        "eligibility": base_manifest["eligibility"],
        "expected_seconds": check_duration(),
        "seed_source": {
            "script": "scripts/ascella_pathion_mesh_persistence.py",
            "flag": "--draw",
            "experiment": "ascella-pathion-mesh-persistence",
            "sources": [f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}" for index in range(SEED_COUNT)],
            "layout": DRAW_LAYOUT,
            "usage": (
                "replay settings keep the original job's compilation seeds (identifiers of the meshes they "
                "reproduce); fresh anchor, failing and dark settings take the draw values in layout order, both "
                "orientations of a fresh setting sharing one; the last two values seed the analysis permutation and "
                "bootstrap generators; the same seeds serve the simulator and hardware cases"
            ),
        },
        "plan_seed_source": {
            "script": "scripts/ascella_pathion_mesh_persistence_analysis.py",
            "flag": "--persistence-plan",
            "experiment": "ascella-pathion-mesh-persistence-plan",
            "sources": [f"qrng:{PLAN_DRAW}#{index}" for index in range(2)],
            "usage": "value 0 seeds the fixed-mesh resampling of the persistence plan, value 1 the fresh-anchor "
            "classification simulation; persistence_plan.json is their record",
        },
        "analysis_sources": {
            name: sha256_bytes((ROOT / name).read_bytes())
            for name in (
                "scripts/ascella_pathion_mesh_persistence.py",
                "scripts/ascella_pathion_mesh_persistence_analysis.py",
                "scripts/ascella_pathion_coset_block_pairs.py",
                "scripts/ascella_pathion_four_term_blocks.py",
                "scripts/hypercomplex_cases.py",
                "scripts/qd_platform.py",
                "gororoba_quantum/cd_core.py",
                "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz",
                PERSISTENCE_PLAN,
                PLAN_DRAW,
                f"{ORIGINAL_RUN}/cases.json",
                f"{ORIGINAL_RUN}/results.json",
            )
        },
        "original_run": ORIGINAL_RUN,
        "original_sim_run": ORIGINAL_SIM_RUN,
        "operands": base_manifest["operands"],
        "blocks": base_manifest["blocks"],
        "block_classes": base_manifest["block_classes"],
        "arms": base_manifest["arms"],
        "designs": base_manifest["designs"],
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "question": (
                "Does the two-block mirror failure on qpu:ascella follow fixed per-mesh errors (the anchor pair's "
                "among them), a static per-shifter error map, a true slot efficiency, or drift?"
            ),
            "decisions": __doc__.split("Preregistered decisions")[1].split("Outcome map")[0].strip(),
            "outcome_map": __doc__.split("Outcome map onto A5-191:")[1].split("Usage:")[0].strip(),
            "thresholds": PREREGISTERED,
            "alpha": ALPHA,
            "map_alpha": MAP_ALPHA,
            "permutations": PERMUTATIONS,
            "failing_items": [list(item) for item in FAILING_ITEMS],
            "original_ba": ORIGINAL_BA,
            "mode_fit_ba": MODE_FIT_BA,
            "frozen_maps": {
                "file": "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz",
                "keys": ["x_gain_all", "a_gain_all", "c_gain_all", "x_offset_all", "a_offset_all", "c_offset_all"],
                "commit": "cc8d8107c",
            },
            "slot_modes": base_manifest["preregistered"]["slot_modes"],
            "failure_mode": base_manifest["preregistered"]["failure_mode"],
            "sentinel_modes": base_manifest["preregistered"]["sentinel_modes"],
            "admission_thresholds": {
                k: base_manifest["preregistered"]["thresholds"][k]
                for k in ("anchor_floor", "dark_ceiling", "sentinel_share")
            },
            "spec": ASCELLA_SPEC,
            "boundary": (
                "A test of the instrument behind the pathion block readings; the client computes every cd_core sign, "
                "the replay meshes are the original job's, and sim:ascella checks mesh identity and the pipeline only."
            ),
        },
    }
    template_experiment(manifest, circuit)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--plan", action="store_true", help="print sizes and predictions, no files")
    parser.add_argument("--spec-check", action="store_true", help="Perceval check of the published imperfections")
    parser.add_argument("--draw", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--platform", choices=("sim:ascella", "qpu:ascella"))
    args = parser.parse_args()
    if args.plan:
        print(json.dumps(plan(), indent=1, sort_keys=True))
        return 0
    if args.spec_check:
        print(json.dumps(spec_check(), indent=1, sort_keys=True))
        return 0
    if args.draw is None or args.out is None or args.platform is None:
        parser.error("--draw, --out and --platform are required unless --plan or --spec-check is given")
    payload = documents(
        args.draw.resolve(), "simulator" if args.platform.startswith("sim:") else "hardware", args.platform
    )
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (args.out / name).write_bytes(data)
    print(f"{args.out}: {ITERATIONS} iterations; request sha256 {sha256_bytes(payload['cases.json'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
