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

Preregistered decisions (PREREGISTERED below holds the thresholds; counting standard errors from SAMPLES):
- mesh gate (sim run): every replay iteration's served unitary lies within 1e-6 of ORIGINAL_RUN's under the same
  setting (largest entry modulus); otherwise the QPU job is not sent;
- admission: the predecessor's anchor floor, dark ceiling and sentinel share on the replay anchors and darks;
- persistence: Pearson r of the 46 replay mirror differences with the original ones, its p from PERMUTATIONS
  relabelings; "fixed per mesh" at p < ALPHA with r at least the Fisher-z ALPHA lower bound of the counting ceiling,
  "partly fixed" at p < ALPHA below it, "not reproduced" otherwise;
- anchor replay: the replayed B/A within ANCHOR_REPLAY_BAND of 1.082 reads "anchor error fixed per mesh";
- fresh anchors: the median fresh B/A within FRESH_BAND of the mode-fit 0.992 and their standard deviation above
  SPREAD_FLOOR read "anchor ratio follows the mesh"; every fresh B/A within FRESH_BAND of 1.082 reads "slot
  efficiency"; anything else reads "unresolved";
- fresh failing settings: Pearson r of the nine fresh mirror differences with the original ones; r at least
  BLOCK_R with p < ALPHA reads "failure follows the block and slot"; otherwise "failure follows the mesh";
- frozen map: the per-shifter gain and offset maps of c1_static.npz (x_gain_all, x_offset_all, frozen in commit
  cc8d8107c before this case) applied to each fresh iteration's returned circuit predict its slot levels; Pearson r of
  predicted against observed departures from the ideal, centered, one-sided at MAP_ALPHA each (Bonferroni over the two
  maps); "map carries" for a map at p < MAP_ALPHA, with its share r^2 / ceiling; otherwise "map does not carry";
- correction: the original job's per-iteration level departures applied as a per-mesh table to the replay leave at
  most the allowance (4) of 46 mirror differences above 0.07; reported with the rms before and after.

Outcome map onto A5-191: fixed per mesh, anchor fixed, fresh ratio following the mesh, failure following the mesh and
map not carrying rewrite A5-191 to "per-mesh fixed errors, the anchor pair's among them"; a carrying map keeps the
per-shifter clause with its measured share; "not reproduced" refutes the static reading in favor of drift.

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
    "bootstrap": [FRESH_ANCHOR_SEEDS + len(FAILING) + 2],
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
PREREGISTERED = {
    "anchor_replay_band": 0.02,
    "fresh_band": 0.03,
    "spread_floor": 0.012,
    "block_r": 0.6,
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


def persistence_bound(observed_d: list[float], noise_var: float, n: int = 46) -> dict[str, float]:
    """Counting ceiling of r between two jobs reading one fixed per-mesh error, and its one-sided Fisher-z bound.

    Each mirror difference d = true + noise with noise variance noise_var in each job; r between the jobs then
    reaches var_true / (var_true + noise_var) at most."""
    var_d = float(np.var(observed_d, ddof=1))
    var_true = max(var_d - noise_var, 0.0)
    ceiling = var_true / (var_true + noise_var)
    z = math.atanh(min(ceiling, 0.999999)) - 2.326 / math.sqrt(n - 3)
    return {"var_d": var_d, "noise_var": noise_var, "ceiling": ceiling, "fisher_lower_99": math.tanh(z)}


def plan() -> dict[str, Any]:
    """Sizes, counting errors and the predicted readings under each mechanism, from the retained records only."""
    sys.path.insert(0, str(ROOT / "docs/evidence/pathion-kernel-map/conjectures"))
    import c1_common  # noqa: PLC0415

    keys, d, _, _ = c1_common.signed_diffs(c1_common.observed_rows())
    rows = c1_common.observed_rows()
    cal = c1_common.an.calibrate(rows, c1_common.settings)
    typical = 0.6
    noise_var = 2 * level_se(typical) ** 2
    bound = persistence_bound(list(d), noise_var)
    # No-division residual of the original job (c1_anchor.txt: rms 0.0250 of d) sets the per-mesh level spread.
    per_mesh_level_sd = 0.0250 / math.sqrt(2)
    ba_sd_mesh = math.sqrt(2) * per_mesh_level_sd
    ba_sd_counting = math.sqrt(2) * level_se(1.0)
    failing_d = {key: float(value) for key, value in zip(keys, d, strict=True) if key in FAILING_ITEMS}
    return {
        "iterations": ITERATIONS,
        "expected_seconds": check_duration(),
        "samples_per_iteration": SAMPLES,
        "level_standard_error": {f"L={lv}": level_se(lv) for lv in (0.25, 0.5, 0.75, 1.0)},
        "persistence": bound,
        "original_anchor_efficiency": cal["efficiency"],
        "original_failing_d": {f"{k[0]}/{k[1]}": v for k, v in failing_d.items()},
        "predictions": {
            "per_mesh_fixed": {
                "replay_r": f">= {bound['fisher_lower_99']:.3f} (ceiling {bound['ceiling']:.3f})",
                "replay_ba": f"{ORIGINAL_BA} +- {PREREGISTERED['anchor_replay_band']}",
                "fresh_ba": f"median {MODE_FIT_BA} +- {PREREGISTERED['fresh_band']}, sd about {ba_sd_mesh:.3f}",
                "fresh_failing_r": "near 0 (new meshes draw new errors)",
            },
            "slot_efficiency": {
                "fresh_ba": f"every seed {ORIGINAL_BA} +- {PREREGISTERED['fresh_band']}, sd about {ba_sd_counting:.4f}",
                "fresh_failing_r": f">= {PREREGISTERED['block_r']}",
            },
            "drift": {"replay_r": "below the bound; replay B/A outside its band"},
            "static_shifter_map": {
                "frozen_map_r": "positive at p < 0.005 on the fresh iterations",
                "prior_art": "signed-coherence new-seed score r 0.157 and 0.319 (share 2.5 and 10.5 percent)",
            },
        },
    }


def spec_check() -> dict[str, Any]:
    """Ascella's published imperfections on single-photon levels, for the anchor and every failing setting.

    Perceval's NoiseModel with the processor record's g2 and indistinguishability adds multi-photon events; the
    analysis keeps single-detected-photon events, so the check post-selects one click. Transmittance scales every
    mode alike and drops out of a ratio. Dark counts enter as a per-pulse click probability rate / clock per mode,
    against a signal click probability of about the transmittance per pulse."""
    import perceval as pcvl  # noqa: PLC0415

    designs = design_by_name()
    targets = [(pairs.ANCHOR, 0), (pairs.ANCHOR, 1)] + [(designs[name], o) for name in FAILING for o in (0, 1)]
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
