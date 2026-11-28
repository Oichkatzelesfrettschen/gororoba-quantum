"""Live-figure noisy simulation of retained Belenos runs on Perceval's SLOS backend.

The module answers one question: can Perceval's source and detector imperfections,
set to a platform record's published figures, produce the routing collapse of
qd_belenos_cone (an iteration whose one-click mass leaves the served mesh's light
cone while an iteration of the same mesh stays inside it)? A figure-driven
simulation is a function of the served circuit, its input and the figures, so
two entries that share a mesh and an input receive one prediction; the retained
entries of one mesh that differ in outcome decide the question.

Per retained entry the simulation deserializes the served computed_circuit and
computed_input, runs Processor("SLOS") with threshold detectors and reads the
exact output distribution, so no random generator runs and no seed enters.
The arms add one imperfection group each:

- ideal: no noise, the served unitary alone;
- noise: perceval.NoiseModel(indistinguishability = HOM, g2, transmittance);
- noise_eff: noise plus a per-mode detector wire efficiency t_out / max t_out
  (the receipt's t_out is a relative sensitivity weight, so the efficiencies
  are a relative-weight reading);
- noise_dark: noise plus the receipt's dark counts as independent clicks per
  clock pulse, rate / (clock x 1e6), over pulses = samples / physical_perf;
- noise_eff_dark: both.

Dark clicks add to the expected one-click counts to first order (a dark click
that coincides with a signal click would read as a two-click sample). Each arm
runs with the served input and with the reference input, the block's source
mode, which removes a per-iteration input_mode switch. Expected counts feed
qd_belenos_cone.cell, so in_block_cone and tvd_cone_from_ideal read exactly as
in the retained reading.

Usage: "$PYTHON" scripts/qd_live_noise_sim.py (--write OUT RUN... | --check OUT RUN... | --self-test)
         [--perfs PATH | --newest-catalogue RUNS_DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import qd_belenos_cone as cone_lib  # noqa: E402
import qd_belenos_mesh as mesh_lib  # noqa: E402

import parallel  # noqa: E402
import qd_records  # noqa: E402

SCHEMA = "qd-live-noise-sim-v1"
CHIP = mesh_lib.CHIP
MODES = mesh_lib.MODES
ARMS = ("ideal", "noise", "noise_eff", "noise_dark", "noise_eff_dark")
COLLAPSE_TVD = 0.3
DIGITS = 6


class SimError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SimError(message)


@dataclass(frozen=True)
class Perfs:
    """Published figures of one platform read, as fractions and per-second rates."""

    hom: float
    g2: float
    transmittance: float
    clock_mhz: float
    t_out: tuple[float, ...]
    dark_per_s: tuple[float, ...]


def read_perfs(path: Path) -> Perfs:
    """Figures from a catalogue (processors[CHIP].perfs), a submission (perfs_at_plan) or a bare perfs record."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if "processors" in data:
        perfs = data["processors"][CHIP]["perfs"]
    elif "perfs_at_plan" in data:
        perfs = data["perfs_at_plan"]
    elif "perfs" in data:
        perfs = data["perfs"]
    else:
        raise SimError(f"{path.name} holds no perfs record")
    for key in ("HOM (%)", "g2 (%)", "Transmittance (%)", "Clock (MHz)", "Dark counts (detection/s)"):
        require(key in perfs, f"{path.name}: the perfs record lacks {key}")
    t_out = perfs["Transmission per mode (%)"]["t_out"]
    dark = perfs["Dark counts (detection/s)"]
    require(len(t_out) == MODES and len(dark) == MODES, f"{path.name}: per-mode figures do not span {MODES} modes")
    return Perfs(
        hom=float(perfs["HOM (%)"]) / 100,
        g2=float(perfs["g2 (%)"]) / 100,
        transmittance=float(perfs["Transmittance (%)"]) / 100,
        clock_mhz=float(perfs["Clock (MHz)"]),
        t_out=tuple(float(v) for v in t_out),
        dark_per_s=tuple(float(v) for v in dark),
    )


def newest_catalogue(runs: Path) -> Path:
    """The platform-before catalogue of the newest run directory that lists CHIP."""
    found = []
    for path in sorted(runs.glob("*/platform-before/catalogue.json")):
        if CHIP in json.loads(path.read_text(encoding="utf-8")).get("processors", {}):
            found.append(path)
    require(bool(found), f"no catalogue under {runs.name} lists {CHIP}")
    return found[-1]


def noise_parameters(perfs: Perfs) -> dict[str, float]:
    """The NoiseModel fields the server recorded for a job: g2, indistinguishability and transmittance."""
    return {
        "g2": perfs.g2,
        "indistinguishability": perfs.hom,
        "transmittance": perfs.transmittance,
    }


def efficiencies(perfs: Perfs) -> list[float]:
    top = max(perfs.t_out)
    return [v / top for v in perfs.t_out]


def beam_splitter_text() -> str:
    from perceval.components import BS
    from perceval.serialization import serialize

    return str(serialize(BS()))


def one_click_distribution(
    input_text: str, circuit_text: str, noise: dict[str, float] | None, weights: list[float] | None
) -> dict[str, Any]:
    """Exact one-click probabilities per mode, conditional on at least one detected photon.

    noise carries the NoiseModel fields as noise_parameters names them, or hom, g2 and transmittance
    for a hand-built fixture; weights set one threshold detector efficiency per mode.
    """
    import perceval as pcvl
    from perceval.serialization import deserialize

    circuit = deserialize(circuit_text)
    model = None
    if noise is not None:
        model = pcvl.NoiseModel(
            indistinguishability=noise.get("indistinguishability", noise.get("hom")),
            g2=noise["g2"],
            transmittance=noise["transmittance"],
        )
    processor = pcvl.Processor("SLOS", circuit, noise=model)
    for mode in range(circuit.m):
        efficiency = 1.0 if weights is None else weights[mode]
        processor.add(mode, pcvl.Detector.ppnr(1, 1, efficiency))
    processor.min_detected_photons_filter(1)
    occupation = [int(v) for v in input_text.rsplit("|", 1)[1].rstrip(">").split(",")]
    processor.with_input(pcvl.BasicState(occupation))
    answer = processor.probs()
    single = [0.0] * circuit.m
    multi = 0.0
    for state, probability in answer["results"].items():
        if state.n == 1:
            single[list(state).index(1)] += float(probability)
        else:
            multi += float(probability)
    return {"p": single, "multi": multi, "global_perf": float(answer["global_perf"])}


def arm_inputs(arm: str, perfs: Perfs) -> tuple[dict[str, float] | None, list[float] | None, bool]:
    require(arm in ARMS, f"unknown arm {arm}")
    noisy = arm != "ideal"
    return (
        noise_parameters(perfs) if noisy else None,
        efficiencies(perfs) if "eff" in arm else None,
        "dark" in arm,
    )


@dataclass(frozen=True)
class Item:
    entry: int
    arm: str
    which: str
    circuit: str
    input_text: str
    perfs: Perfs


def simulate_item(item: Item) -> dict[str, Any]:
    noise, weights, _ = arm_inputs(item.arm, item.perfs)
    return one_click_distribution(item.input_text, item.circuit, noise, weights)


def expected_counts(
    distribution: dict[str, Any], samples: int, served_perf: float, perfs: Perfs, dark: bool
) -> tuple[list[int], int]:
    """Expected one-click counts and the sample total of an arm; dark clicks add rate x pulses / clock per mode."""
    pulses = samples / served_perf
    counts = [samples * p for p in distribution["p"]]
    total = float(samples)
    if dark:
        for mode, rate in zip(range(len(counts)), perfs.dark_per_s, strict=False):
            extra = rate * pulses / (perfs.clock_mhz * 1e6)
            counts[mode] += extra
            total += extra
    return [int(round(c)) for c in counts], int(round(total))


def round_tree(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, DIGITS)
    if isinstance(value, dict):
        return {k: round_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [round_tree(v) for v in value]
    return value


KEEP = (
    "in_block",
    "in_block_cone",
    "tvd_cone_from_ideal",
    "cone_share",
    "n_block",
    "n_off_cone",
    "one_click_samples",
    "shot_floor",
)


def read_run(
    run: Path, perfs: Perfs, arms: tuple[str, ...] = ARMS, only: tuple[int, ...] | None = None
) -> dict[str, Any]:
    """Simulate the entries of a retained run (all, or the indices in only) under each arm and set the readings
    beside the retained ones."""
    retained = cone_lib.run_cells(run)
    records = qd_records.load_run(run)
    manifest = records.json_of("cases.json")
    (block,) = manifest["blocks"]
    low, width = block["offset"], len(block["roles"])
    labels = [low + k for k, role in enumerate(block["roles"]) if role.startswith("label")]
    reference = block["photons"][0]
    inner = mesh_lib.raw_result(run)
    served = inner.get("results_list") or [inner]
    require(len(served) == len(retained), "the retained cells and the served entries differ in number")
    chosen = range(len(served)) if only is None else only
    items: list[Item] = []
    for index in chosen:
        entry = served[index]
        occupation = [0] * MODES
        occupation[reference] = 1
        reference_text = ":PCVL:BasicState:|" + ",".join(str(v) for v in occupation) + ">"
        for arm in arms:
            items.append(Item(index, arm, "served_input", entry["computed_circuit"], entry["computed_input"], perfs))
            if cone_lib.source_mode(entry["computed_input"]) != reference:
                items.append(Item(index, arm, "reference_input", entry["computed_circuit"], reference_text, perfs))
    distributions = parallel.ordered_map(simulate_item, items, min_items=2)
    rows: list[dict[str, Any]] = []
    for index in chosen:
        entry = served[index]
        elements = mesh_lib.decode(entry["computed_circuit"])
        arch = mesh_lib.run_architecture(elements)
        phases = mesh_lib.mesh_phases(arch, elements)
        samples = retained[index]["samples"]
        served_perf = float(entry["physical_perf"])
        row: dict[str, Any] = {
            "name": retained[index]["name"],
            "mesh_sha256": retained[index]["mesh_sha256"],
            "input_mode": cone_lib.source_mode(entry["computed_input"]),
            "served_physical_perf": round(served_perf, 9),
            "retained": {key: retained[index][key] for key in KEEP},
            "arms": {},
        }
        for item, distribution in zip(items, distributions, strict=True):
            if item.entry != index:
                continue
            _, _, dark = arm_inputs(item.arm, perfs)
            counts, total = expected_counts(distribution, samples, served_perf, perfs, dark)
            source = row["input_mode"] if item.which == "served_input" else reference
            reading = cone_lib.cell(
                counts, total, arch, phases, source, low, width, labels, served_perf, perfs.clock_mhz
            )
            out = {key: reading[key] for key in KEEP}
            out["simulated_global_perf"] = distribution["global_perf"]
            out["multi_click_mass"] = distribution["multi"]
            row["arms"].setdefault(item.arm, {})[item.which] = out
        for pair in row["arms"].values():
            pair.setdefault("reference_input", pair["served_input"])
        rows.append(row)
    return round_tree({"run": run.name, "entries": rows, "summary": summarize(rows, arms)})


def summarize(rows: list[dict[str, Any]], arms: tuple[str, ...]) -> dict[str, Any]:
    collapsed = [r for r in rows if (r["retained"]["tvd_cone_from_ideal"] or 0.0) >= COLLAPSE_TVD]
    verdicts: dict[str, str] = {}
    for arm in arms:
        if not collapsed:
            verdicts[arm] = "no_collapse_in_run"
            continue
        reproduced = all(
            (r["arms"][arm]["served_input"]["tvd_cone_from_ideal"] or 0.0) >= COLLAPSE_TVD for r in collapsed
        )
        verdicts[arm] = "reproduces" if reproduced else "does_not_reproduce"
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for r in rows:
        groups.setdefault((r["mesh_sha256"], r["input_mode"]), []).append(r)
    spreads = []
    for (mesh, source), members in sorted(groups.items()):
        observed = [m["retained"]["tvd_cone_from_ideal"] or 0.0 for m in members]
        predicted = {
            arm: [m["arms"][arm]["served_input"]["tvd_cone_from_ideal"] or 0.0 for m in members] for arm in arms
        }
        spreads.append(
            {
                "mesh_sha256": mesh,
                "input_mode": source,
                "entries": len(members),
                "observed_tvd_spread": max(observed) - min(observed),
                "predicted_tvd_spread": {arm: max(v) - min(v) for arm, v in predicted.items()},
            }
        )
    return {
        "collapse_tvd_threshold": COLLAPSE_TVD,
        "collapsed_entries": len(collapsed),
        "collapse_verdicts": verdicts,
        "same_mesh_groups": spreads,
    }


def record(runs: list[Path], perfs_path: Path | None, runs_dir: Path | None) -> dict[str, Any]:
    out: list[dict[str, Any]] = []
    sources = []
    for run in runs:
        if perfs_path is not None:
            path = perfs_path
        elif runs_dir is not None:
            path = newest_catalogue(runs_dir)
        else:
            path = run / "submission.json"
        sources.append({"run": run.name, "perfs": path.name, "sha256": mesh_lib.sha256(path)})
        out.append(read_run(run, read_perfs(path)))
    return {"schema": SCHEMA, "arms": list(ARMS), "perfs_sources": sources, "runs": out}


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def self_test() -> int:
    perfs = Perfs(0.583, 0.011, 0.0269, 4.94, (100.0,) * MODES, (0.0,) * MODES)
    require(noise_parameters(perfs)["indistinguishability"] == 0.583, "noise parameters")
    require(efficiencies(perfs) == [1.0] * MODES, "efficiencies")
    bs = beam_splitter_text()
    ideal = one_click_distribution("|1,0>", bs, None, None)
    require(abs(ideal["p"][0] - 0.5) < 1e-9 and ideal["multi"] == 0.0, "beam splitter splits one photon evenly")
    lossy = one_click_distribution("|1,0>", bs, {"hom": 1.0, "g2": 0.2, "transmittance": 0.1}, [1.0, 0.5])
    require(lossy["p"][0] > lossy["p"][1] and lossy["multi"] > 0.0, "a weaker detector and a g2 component register")
    counts, total = expected_counts(ideal, 1000, 0.01, Perfs(1, 0, 1, 1.0, (1.0,) * MODES, (10.0,) * MODES), True)
    require(total > 1000 and counts[0] > 500, "dark clicks add counts")
    print("qd_live_noise_sim self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--check", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--perfs", type=Path, help="catalogue, submission or perfs JSON for every run")
    parser.add_argument("--newest-catalogue", type=Path, metavar="RUNS_DIR")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    mode = args.write or args.check
    if not mode or len(mode) < 2:
        parser.error("--write or --check takes OUT and at least one RUN")
    out, runs = Path(mode[0]), [Path(r) for r in mode[1:]]
    text = dump(record(runs, args.perfs, args.newest_catalogue))
    if args.write:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
        return 0
    if out.read_text(encoding="utf-8") != text:
        print(f"{out} differs from the recomputed record", file=sys.stderr)
        return 1
    print(f"{out} matches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
