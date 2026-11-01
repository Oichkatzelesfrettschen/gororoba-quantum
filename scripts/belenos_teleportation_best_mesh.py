"""Belenos best-mesh teleportation: screen compilation seeds per input, select the best mesh, replay it.

docs/design/belenos-best-mesh-teleportation-case.md fixes the request. The circuits are those of
qd_teleportation_rehearsal job-02 (layout JOB_02_LAYOUT): three photons, the postselected CNOT, the partial Bell
analyzer and the receiver read in the input's basis, one template iteration per input and compilation seed. Per-seed
compiled-mesh error dominates this chip's error budget and a seed reproduces its mesh, so the case screens CANDIDATES
seeds per input, selects per input the seed whose screen correctness is highest, and replays the selected seeds in
two confirm jobs whose correctness is tested against the screen's mesh average.

Each input's candidates are, in order, its job-02 seed, its job-03 seed (both imported by name: they identify the
meshes the split rehearsal measured) and four seeds of the ANU QRNG draw NEW_SEED_DRAW, input i (design order +Z, -Z,
+X, -X, +Y, -Y) taking indices 4 i to 4 i + 3 in index order, registered in docs/evidence/qrng_seeds/allocations.json.
SCREEN_JOBS run the 36 screen iterations in rounds: round r gives input i its candidate (r + i) mod CANDIDATES, so
every round carries every input and the old seeds spread over the jobs.

--check rebuilds the screen cases, compares them with the retained bytes, binds every iteration through
qd_platform.template_experiment, and requires each iteration's template unitary to equal its setting's chip operator.
--build JOB writes a screen case. --select RUN x 4 scores the screen runs, applies the preregistered selection and
writes the confirm cases. --analyze writes the pooled analysis of the four screen and two confirm runs.

Usage:
  "$PYTHON" scripts/belenos_teleportation_best_mesh.py [--check | --build JOB | --select RUN x 4 | --analyze RUN x 6]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from qd_network_protocol import decode_bit  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402
from qd_teleportation_rehearsal import (  # noqa: E402
    JOB_02_COMPILATION_SEEDS,
    JOB_03_COMPILATION_SEEDS,
    MAX_DURATION,
    MIN_CLICKS,
    MODES,
    REQUESTS,
    Request,
    anytime_lower_bound,
    bound_setting,
    build_setting,
    circuit_document,
    expected_bit,
    frames,
    inputs,
    operator_of,
    tally,
)
from scipy.stats import norm  # noqa: E402

from parallel import ordered_map  # noqa: E402

FAMILY = "belenos_teleportation_best_mesh"
CASES = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/belenos-best-mesh-teleportation-case.md"
PLATFORM = "qpu:belenos"
JOB_02_LAYOUT = REQUESTS["job-02"].layout
JOB_02_READ = REQUESTS["job-02"].anchor_read
LABELS = tuple(row["label"] for row in inputs())
CANDIDATES = 6
NEW_SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T153446Z.json"
# Four new candidates per input, indices 0 to 23 of NEW_SEED_DRAW in index order.
NEW_SEEDS = (
    51401,
    52848,
    53584,
    4407,
    34754,
    9700,
    9812,
    57266,
    4690,
    43808,
    64772,
    3678,
    64944,
    63035,
    32405,
    47098,
    24660,
    13879,
    34472,
    49149,
    11654,
    6614,
    63506,
    22774,
)
SCREEN_JOBS = ("screen-00", "screen-01", "screen-02", "screen-03")
CONFIRM_JOBS = ("confirm-00", "confirm-01")
ITERATIONS_PER_SCREEN = len(LABELS) * CANDIDATES // len(SCREEN_JOBS)
SCREEN_SAMPLES = 600
CONFIRM_SAMPLES = 1200
# max_shots per iteration: samples times the largest shots per sample of the job-02 and job-03 iterations (2,660,
# -Z of block B, which reached its 3,000,000 cap at 1,127 samples) times SHOT_MARGIN, rounded up to SHOT_QUANTUM.
SHOTS_PER_SAMPLE = 2660
SHOT_MARGIN = 1.15
SHOT_QUANTUM = 100_000
# Seconds per iteration of these circuits: job-02 ran six 1,200-sample iterations in 184 s.
SECONDS_PER_ITERATION = 31.0
DURATION_MARGIN = 0.9
ALPHA = 0.05
# The anytime-valid bound of the confirm pool: lambda tuned to the planned accepted events of two confirm jobs at the
# job-02 and job-03 acceptance (1,816 accepted over 14,400 samples).
BOUND_ALPHA = 0.01
PLANNED_CONFIRM_ACCEPTED = 1816
ANYTIME_LAMBDA = math.sqrt(8.0 * math.log(1.0 / BOUND_ALPHA) / PLANNED_CONFIRM_ACCEPTED)
TOLERANCE = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def old_seeds(label: str) -> tuple[int, int]:
    """The job-02 seed and the job-03 seed of an input; job-03 ran the inputs in mirrored order."""
    index = LABELS.index(label)
    return JOB_02_COMPILATION_SEEDS[index], JOB_03_COMPILATION_SEEDS[len(LABELS) - 1 - index]


def candidates(label: str) -> tuple[int, ...]:
    index = LABELS.index(label)
    return (*old_seeds(label), *NEW_SEEDS[4 * index : 4 * index + 4])


def screen_rows() -> list[dict[str, Any]]:
    """The 36 screen iterations in submission order: round r gives input i its candidate (r + i) mod CANDIDATES."""
    rows = []
    for round_ in range(CANDIDATES):
        for index, row in enumerate(inputs()):
            candidate = (round_ + index) % CANDIDATES
            rows.append({**row, "candidate": candidate, "seed": candidates(row["label"])[candidate]})
    return rows


def job_rows(job: str) -> list[dict[str, Any]]:
    position = SCREEN_JOBS.index(job)
    return screen_rows()[position * ITERATIONS_PER_SCREEN : (position + 1) * ITERATIONS_PER_SCREEN]


def shots(samples: int) -> int:
    return int(math.ceil(samples * SHOTS_PER_SAMPLE * SHOT_MARGIN / SHOT_QUANTUM)) * SHOT_QUANTUM


def credit_ceiling(samples: int) -> float:
    return round(1.0 + shots(samples) * 1e-6, 6)


def preregistered() -> dict[str, Any]:
    return {
        "screen": f"{len(SCREEN_JOBS)} jobs of {ITERATIONS_PER_SCREEN} iterations at {SCREEN_SAMPLES} samples; each "
        f"input runs {CANDIDATES} candidate seeds: its job-02 seed, its job-03 seed and four new seeds",
        "event": "an accepted event carries exactly three threshold clicks across all 24 returned modes, two on the "
        "analyzer in a frame-table pattern, one on b and none on the heralds or outside the logical modes; it is "
        "correct when the frame-decoded receiver bit equals the input's expected bit",
        "selection": "per input, the candidate with the highest screen correctness (correct / accepted); ties go to "
        "more accepted events, then to the lower candidate index; a candidate with no accepted event is not selected",
        "confirm": f"{len(CONFIRM_JOBS)} jobs that each replay the six selected seeds at {CONFIRM_SAMPLES} samples, "
        "the first in design order and the second mirrored",
        "baseline": "per input, the mean over its candidates of their screen correctness, averaged over the six "
        "inputs; its variance is the sum over inputs of the between-candidate sample variance over the candidate "
        "count, divided by 36",
        "primary": "confirm correctness (per input, correct over accepted pooled over the confirm jobs, averaged over "
        "the six inputs) minus the baseline, z = difference / sqrt(confirm binomial variance + baseline variance), "
        f"one-sided at alpha {ALPHA}; the selected candidates' screen scores enter no test",
        "secondary": f"the confirm pool's correctness and its anytime-valid lower bound at alpha {BOUND_ALPHA} and "
        f"lambda {ANYTIME_LAMBDA:.6f}; whether each replay returns its screen iteration's computed_circuit; whether "
        "the job-02 and job-03 seeds return their retained meshes",
        "excluded": "no classical comparison: a mesh selected per input from that input's own screen data makes the "
        "instrument depend on the input label, which the rehearsal's classical comparisons exclude",
        "stopping": "the case stops for the owner when the first screen job runs past 270 s, a job returns fewer "
        "iterations than requested, the platform's HOM, g2 or transmittance read changes between screen and "
        "confirm, or a confirm replay returns a mesh other than its screen iteration's",
    }


def build_documents(job: str, rows: Sequence[Mapping[str, Any]], samples: int) -> dict[str, bytes]:
    request = Request(job, JOB_02_LAYOUT, tuple(row["seed"] for row in rows), JOB_02_READ)
    built = ordered_map(build_setting, [(index, dict(row), request) for index, row in enumerate(rows)], min_items=1)
    template = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == template, f"iteration {index} needs another mesh than iteration 0")
    settings = []
    for (_, setting), row in zip(built, rows, strict=True):
        setting = {key: value for key, value in setting.items() if key != "seed"}
        setting["name"] = f"{row['label']}-c{row['candidate']}"
        settings.append(setting)
    circuit_bytes = (json.dumps(circuit_document(template, JOB_02_LAYOUT), indent=1) + "\n").encode()
    count = len(settings)
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": count,
        "min_detected_photons": MIN_CLICKS,
        "max_samples": samples * count,
        "max_shots": shots(samples) * count,
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": sorted(JOB_02_LAYOUT),
        "layout": {"logical": ["q0", "q1", "a0", "a1", "b0", "b1", "h0", "h1"], "chip_modes": list(JOB_02_LAYOUT)},
        "frames": {pattern: list(frame) for pattern, frame in sorted(frames().items())},
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": preregistered(),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def screen_documents(job: str) -> dict[str, bytes]:
    return build_documents(job, job_rows(job), SCREEN_SAMPLES)


def confirm_rows(selected: Mapping[str, int], job: str) -> list[dict[str, Any]]:
    rows = [
        {**row, "candidate": selected[row["label"]], "seed": candidates(row["label"])[selected[row["label"]]]}
        for row in inputs()
    ]
    return rows if CONFIRM_JOBS.index(job) == 0 else rows[::-1]


def bound_seconds(iterations: int) -> float:
    return SECONDS_PER_ITERATION * iterations


def check_documents(job: str, retained: Mapping[str, bytes], built: Mapping[str, bytes]) -> str:
    for name, data in built.items():
        require(retained[name] == data, f"{job}/{name} differs from the builder's bytes")
    manifest = json.loads(retained["cases.json"])
    circuit = json.loads(retained["circuit.json"])
    _, settings = template_experiment(manifest, circuit)
    require(len(settings) == manifest["iterations"], f"{job}: {len(settings)} settings bound")
    require(bound_seconds(len(settings)) <= DURATION_MARGIN * MAX_DURATION, f"{job}: duration bound")
    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        parameter = parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))
        chip.add(mode, pcvl.BS.Rx(theta=parameter) if kind == "BS" else pcvl.PS(parameter))
    for setting in settings:
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())
        require(np.abs(unitary - operator_of(setting)).max() < TOLERANCE, f"{job} {setting['name']}: unitary differs")
    return f"{FAMILY} {job}: {len(settings)} iterations bound, bound {bound_seconds(len(settings)):.0f} s"


def check() -> int:
    for label in LABELS:
        require(len(set(candidates(label))) == CANDIDATES, f"{label}: a candidate seed repeats")
    rows = screen_rows()
    require(len({(row["label"], row["candidate"]) for row in rows}) == len(rows), "a screen pair repeats")
    for job in SCREEN_JOBS:
        retained = {name: (CASES / job / name).read_bytes() for name in ("cases.json", "circuit.json")}
        print(check_documents(job, retained, screen_documents(job)))
    for job in CONFIRM_JOBS:
        if (CASES / job / "cases.json").exists():
            selection = json.loads((CASES / "selection.json").read_text(encoding="utf-8"))
            retained = {name: (CASES / job / name).read_bytes() for name in ("cases.json", "circuit.json")}
            built = build_documents(job, confirm_rows(selection["selected"], job), CONFIRM_SAMPLES)
            print(check_documents(job, retained, built))
    return 0


def write_case(job: str, built: Mapping[str, bytes]) -> None:
    out = CASES / job
    out.mkdir(parents=True, exist_ok=True)
    for name, data in built.items():
        path = out / name
        require(not path.exists() or path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        path.write_bytes(data)
    print(f"{FAMILY} {job}: {out.relative_to(ROOT)} cases.json {sha256_bytes(built['cases.json'])}")


def mesh_digest(entry: Mapping[str, Any]) -> str | None:
    circuit = (entry.get("result_fields") or {}).get("computed_circuit")
    return hashlib.sha256(json.dumps(circuit, sort_keys=True).encode()).hexdigest() if circuit else None


def score_run(run: Path) -> list[dict[str, Any]]:
    """Per counted iteration: input, candidate, seed, accepted, correct and the returned mesh digest."""
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    layout = tuple(manifest["layout"]["chip_modes"])
    table = frames()
    rows = []
    for entry in results.get("iterations") or []:
        if "counts" not in entry:
            continue
        setting = manifest["settings"][bound_setting(manifest["settings"], entry)]
        accepted, _ = tally(entry["counts"], layout)
        correct = sum(
            count
            for (pattern, raw), count in accepted.items()
            if decode_bit(setting["basis"], raw, *table[pattern]) == expected_bit(setting["label"])
        )
        rows.append(
            {
                "job": manifest["job"],
                "label": setting["label"],
                "candidate": int(setting["name"].rsplit("-c", 1)[1]),
                "seed": setting["compilation_seed"],
                "accepted": sum(accepted.values()),
                "correct": correct,
                "shots": (entry.get("result_fields") or {}).get("nb_shots_used"),
                "mesh": mesh_digest(entry),
            }
        )
    return rows


def select(screen: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    """The preregistered selection: highest correctness, then more accepted events, then the lower candidate."""
    selected = {}
    for label in LABELS:
        rows = [row for row in screen if row["label"] == label and row["accepted"] > 0]
        require(bool(rows), f"{label}: no candidate returned an accepted event")
        best = min(rows, key=lambda row: (-row["correct"] / row["accepted"], -row["accepted"], row["candidate"]))
        selected[label] = best["candidate"]
    return selected


def baseline(screen: Sequence[Mapping[str, Any]]) -> tuple[float, float]:
    """The mesh average over the screened candidates and its variance from the between-candidate spread."""
    means, variance = [], 0.0
    for label in LABELS:
        values = [row["correct"] / row["accepted"] for row in screen if row["label"] == label and row["accepted"]]
        require(len(values) >= 2, f"{label}: fewer than two scored candidates")
        means.append(float(np.mean(values)))
        variance += float(np.var(values, ddof=1)) / len(values)
    return float(np.mean(means)), variance / len(LABELS) ** 2


def primary(screen: Sequence[Mapping[str, Any]], confirm: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    base, base_var = baseline(screen)
    per_input, conf_var = {}, 0.0
    for label in LABELS:
        rows = [row for row in confirm if row["label"] == label]
        accepted = sum(row["accepted"] for row in rows)
        correct = sum(row["correct"] for row in rows)
        require(accepted > 0, f"{label}: the confirm runs returned no accepted event")
        value = correct / accepted
        per_input[label] = {"correct": correct, "accepted": accepted, "correctness": value}
        conf_var += value * (1 - value) / accepted
    confirmed = float(np.mean([entry["correctness"] for entry in per_input.values()]))
    conf_var /= len(LABELS) ** 2
    z = (confirmed - base) / math.sqrt(conf_var + base_var)
    correct = sum(entry["correct"] for entry in per_input.values())
    accepted = sum(entry["accepted"] for entry in per_input.values())
    return {
        "baseline": base,
        "baseline_variance": base_var,
        "confirmed": confirmed,
        "confirmed_variance": conf_var,
        "difference": confirmed - base,
        "z": z,
        "p_value": float(norm.sf(z)),
        "selected_beats_mesh_average": bool(z > norm.isf(ALPHA)),
        "per_input": per_input,
        "pooled": {
            "correct": correct,
            "accepted": accepted,
            "correctness": correct / accepted,
            "lower_bound": anytime_lower_bound(correct, accepted, ANYTIME_LAMBDA, BOUND_ALPHA),
        },
    }


def load_screen(runs: Sequence[Path]) -> list[dict[str, Any]]:
    loaded = []
    jobs = []
    for run in runs:
        manifest_bytes = (run / "cases.json").read_bytes()
        job = json.loads(manifest_bytes)["job"]
        require(
            manifest_bytes == (CASES / job / "cases.json").read_bytes(), f"{run}: cases.json is not the frozen case"
        )
        jobs.append(job)
        loaded.extend(score_run(run))
    require(sorted(jobs) == sorted(set(jobs)), f"runs repeat a job: {jobs}")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", choices=SCREEN_JOBS)
    group.add_argument("--select", type=Path, nargs=len(SCREEN_JOBS), metavar="RUN")
    group.add_argument("--analyze", type=Path, nargs=len(SCREEN_JOBS) + len(CONFIRM_JOBS), metavar="RUN")
    args = parser.parse_args()
    if args.build:
        write_case(args.build, screen_documents(args.build))
        return 0
    if args.select:
        screen = load_screen(args.select)
        require(len(screen) == len(LABELS) * CANDIDATES, f"the screen returned {len(screen)} of 36 iterations")
        selected = select(screen)
        record = {"selected": selected, "screen": screen, "screen_runs": [run.name for run in args.select]}
        (CASES / "selection.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        for job in CONFIRM_JOBS:
            write_case(job, build_documents(job, confirm_rows(selected, job), CONFIRM_SAMPLES))
        print(json.dumps(selected))
        return 0
    if args.analyze:
        screen = load_screen(args.analyze[: len(SCREEN_JOBS)])
        confirm = load_screen(args.analyze[len(SCREEN_JOBS) :])
        record = {"screen": screen, "confirm": confirm, "primary": primary(screen, confirm)}
        text = json.dumps(record, indent=1, sort_keys=True) + "\n"
        for run in args.analyze:
            (run / "best-mesh-analysis.json").write_text(text, encoding="utf-8")
        print(json.dumps(record["primary"], indent=1))
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
