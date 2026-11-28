"""Offline application of Perceval's error mitigations to retained Belenos counts.

Perceval 1.3.1 splits a mitigation into extend_computation (the computations to run) and parse_results (the
recombination). The three mitigations of the quantum cloud divide by that split:

- DetectorBalancing needs one computation, the probabilities of the unmitigated experiment, so its parse_results
  applies offline to the retained counts of a run submitted with mitigations: [] (the explicit empty list; a run
  without the field carries the server's default mitigation, and balancing it twice is wrong, so read_run refuses
  it unless allow_server_default is set, and the record then says so). The mitigation state comes from the body
  the receipt sent (job-body.json, payload.mitigations, the pcvlar text of an empty list) and must agree with
  cases.json. The detector model is the catalogue's specs.detector (threshold on Belenos) at unit efficiency;
  the receipt's t_out is a relative weight, not an efficiency, so no per-mode efficiency enters. A threshold
  detector at unit efficiency makes DetectorBalancing the identity on every threshold count, whatever the photon
  number: each detected state (entries 0 or 1) has the single sub-state itself, so the perf factor is 1 and the
  distribution is returned unchanged. The balancing row of the record carries "identity" for that reading, and a
  balancing that changes a count needs calibrated per-mode efficiencies, which no retained run holds.
- PhotonRecycling is a function of a count distribution and the ideal photon number, so it applies offline when
  the ideal photon number is at least 3 and the counts hold states with n - 1 and n - 2 photons; any other run is
  recorded as not applicable with Perceval's reason.
- DistinguishablePhotonMitigation extends one computation into sub-computations with fewer input photons, each a
  separate provider job, so no retained run holds the counts it recombines. dpm_overhead returns the number of
  sub-computations, an offline price read before any job.

probs_to_sample_count (the conversion of a distribution to counts) draws from numpy's global generator, which
Perceval leaves unseeded; seeded_counts calls perceval.random_seed(seed) first, and a caller that writes counts takes
the seed through qrng_seeds.add_seed_argument, so a value of a retained QRNG draw is the only admitted source.
This CLI converts no distribution to counts and holds no seed flag; the self-test seeds the conversion with
SELF_TEST_SEED, a value of a retained QRNG draw.

Usage: "$PYTHON" scripts/qd_offline_mitigation.py (--write OUT RUN... | --check OUT RUN... | --self-test)
         [--allow-server-default]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import qd_belenos_mesh as mesh_lib  # noqa: E402

import qd_records  # noqa: E402

SCHEMA = "qd-offline-mitigation-v1"
MODES = mesh_lib.MODES
DIGITS = 9
MIN_RECYCLING_PHOTONS = 3
EMPTY_MITIGATIONS = "pcvlar 0 1 0 list 0"
# Value 1 of docs/evidence/anu_qrng/draw-2026-11-28T081947Z.json: the generator state of the self-test conversion.
SELF_TEST_SEED = 48665


class MitigationError(ValueError):
    pass


def mitigation_state(manifest: dict[str, Any]) -> str:
    """none (mitigations: []), explicit (a named list) or server_default (no field)."""
    if "mitigations" not in manifest:
        return "server_default"
    return "none" if manifest["mitigations"] == [] else "explicit"


def body_state(body: dict[str, Any]) -> str:
    """The mitigation state of the body the receipt sent: payload.mitigations as the pcvlar text of an empty list."""
    payload = body.get("payload")
    if not isinstance(payload, dict):
        raise MitigationError("job-body.json carries no payload")
    if "mitigations" not in payload:
        return "server_default"
    return "none" if payload["mitigations"] == EMPTY_MITIGATIONS else "explicit"


def counts_distribution(text: str) -> Any:
    """The probability distribution of a retained count text ('|s>=n' lines, plain or zipped)."""
    import re

    from perceval.utils import BasicState, BSDistribution

    total = 0
    counts: dict[Any, int] = {}
    for state, n in re.findall(r"\|([0-9,]+)>=(\d+)", mesh_lib.unzip(text)):
        key = BasicState([int(v) for v in state.split(",")])
        counts[key] = counts.get(key, 0) + int(n)
        total += int(n)
    if total == 0:
        raise MitigationError("the count text holds no state")
    dist = BSDistribution()
    for state, n in counts.items():
        dist[state] = n / total
    return dist


def detector_model(kind: str, modes: int) -> list[Any]:
    from perceval.components import Detector

    if kind not in ("threshold", "pnr"):
        raise MitigationError(f"unknown detector {kind}")
    return [Detector.threshold() if kind == "threshold" else Detector.pnr() for _ in range(modes)]


def balance_with_factor(distribution: Any, modes: int, detectors: list[Any]) -> tuple[Any, float]:
    """DetectorBalancing.parse_results on a probs computation: the corrected distribution and its perf factor."""
    from perceval.components import Experiment
    from perceval.runtime.command import Command
    from perceval.runtime.computation import Computation
    from perceval.runtime.error_mitigation import DetectorBalancing
    from perceval.runtime.error_mitigation.imperfections import Imperfections
    from perceval.utils import NoiseModel

    computation = Computation(Command("probs", []), Experiment(modes))
    results = {"results": distribution, "global_perf": 1.0}
    answer = DetectorBalancing().parse_results(computation, [results], Imperfections(NoiseModel(), detectors))
    return answer["results"], float(answer["global_perf"])


def balance_detectors(distribution: Any, modes: int, detectors: list[Any]) -> Any:
    return balance_with_factor(distribution, modes, detectors)[0]


def is_identity(before: Any, after: Any, factor: float) -> bool:
    """True when balancing returned the distribution it was given, state by state, with perf factor 1."""
    if abs(factor - 1.0) > 1e-12 or set(before) != set(after):
        return False
    return all(abs(float(before[s]) - float(after[s])) < 1e-12 for s in before)


def recycle(distribution: Any, ideal_photons: int) -> dict[str, Any]:
    from perceval.runtime.error_mitigation.photon_recycling import photon_recycling

    if ideal_photons < MIN_RECYCLING_PHOTONS:
        return {
            "status": "not_applicable",
            "reason": f"ideal photon count {ideal_photons} is below {MIN_RECYCLING_PHOTONS}",
        }
    try:
        mitigated = photon_recycling(distribution, ideal_photons)
    except ValueError as error:
        return {"status": "not_applicable", "reason": str(error)}
    return {"status": "applied", "states": len(mitigated), "mass_after": float(sum(mitigated.values()))}


def dpm_overhead(occupation: list[int], order: int) -> int:
    from perceval.runtime.error_mitigation import DistinguishablePhotonMitigation
    from perceval.utils import FockState

    return int(DistinguishablePhotonMitigation(order).overhead(FockState(occupation)))


def seeded_counts(distribution: Any, count: int, seed: int) -> dict[str, int]:
    import perceval as pcvl
    from perceval.utils.conversion import probs_to_sample_count

    pcvl.random_seed(seed)
    drawn = probs_to_sample_count(distribution, count=count)
    return {str(state): int(n) for state, n in sorted(drawn.items(), key=lambda kv: str(kv[0]))}


def one_click_share(distribution: Any) -> dict[int, float]:
    mass = {list(state).index(1): float(p) for state, p in distribution.items() if state.n == 1}
    total = sum(mass.values())
    return {mode: p / total for mode, p in mass.items()} if total else {}


def tvd(first: dict[int, float], second: dict[int, float]) -> float:
    return 0.5 * sum(abs(first.get(k, 0.0) - second.get(k, 0.0)) for k in set(first) | set(second))


def round_tree(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, DIGITS)
    if isinstance(value, dict):
        return {k: round_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [round_tree(v) for v in value]
    return value


def read_run(run: Path, allow_server_default: bool = False, only: tuple[int, ...] | None = None) -> dict[str, Any]:
    """Apply the offline mitigations to the entries of a retained run (all, or the indices in only)."""
    records = qd_records.load_run(run)
    qd_records.validate_run(records)
    manifest = records.json_of("cases.json")
    state = mitigation_state(manifest)
    sent = body_state(records.json_of("job-body.json"))
    if sent != state:
        raise MitigationError(f"{run.name}: cases.json reads mitigations {state}, the body sent reads {sent}")
    if state == "server_default" and not allow_server_default:
        raise MitigationError(
            f"{run.name} carries no mitigations field, so the server applied its default mitigation to the counts"
        )
    if state == "explicit":
        raise MitigationError(f"{run.name} names mitigations {manifest['mitigations']}; its counts are mitigated")
    catalogue = mesh_lib.load_catalogue()
    kind = catalogue["processors"][mesh_lib.CHIP]["specs"]["detector"]
    detectors = detector_model(kind, MODES)
    inner = mesh_lib.raw_result(run)
    entries = inner.get("results_list") or [inner]
    rows = []
    for index in range(len(entries)) if only is None else only:
        entry = entries[index]
        raw = counts_distribution(entry["results"])
        photons = int(sum(int(v) for v in entry["computed_input"].rsplit("|", 1)[1].rstrip(">").split(",")))
        balanced, factor = balance_with_factor(raw, MODES, detectors)
        occupation = [int(v) for v in entry["computed_input"].rsplit("|", 1)[1].rstrip(">").split(",")]
        before, after = one_click_share(raw), one_click_share(balanced)
        rows.append(
            {
                "index": index,
                "input_photons": photons,
                "detector_balancing": {
                    "status": "applied",
                    "detector": kind,
                    "mass_before": float(sum(raw.values())),
                    "mass_after": float(sum(balanced.values())),
                    "perf_factor": factor,
                    "states_before": len(raw),
                    "states_after": len(balanced),
                    "one_click_tvd_after_vs_before": tvd(before, after),
                    "identity": is_identity(raw, balanced, factor),
                },
                "photon_recycling": recycle(raw, photons),
                "distinguishable_photon": {
                    "status": "needs_server",
                    "sub_computations_order_1": dpm_overhead(occupation, 1),
                },
            }
        )
    return round_tree(
        {
            "run": run.name,
            "state": state,
            "warning": "server default mitigation applied to the counts before this reading"
            if state == "server_default"
            else None,
            "entries": rows,
        }
    )


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def three_to_one(dist: Any) -> bool:
    """True for the normalized distribution of the counts |1,0>=3 and |0,1>=1."""
    from perceval.utils import BasicState

    return abs(dist[BasicState([1, 0])] - 0.75) <= 1e-12 and abs(sum(dist.values()) - 1.0) <= 1e-12


def self_test() -> int:
    dist = counts_distribution("|1,0>=3\n|0,1>=1\n")
    if not three_to_one(dist):
        raise MitigationError("counts_distribution")
    if recycle(dist, 1)["status"] != "not_applicable":
        raise MitigationError("recycle")
    if seeded_counts(dist, 100, SELF_TEST_SEED) != seeded_counts(dist, 100, SELF_TEST_SEED):
        raise MitigationError("seeded_counts")
    print("qd_offline_mitigation self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--check", nargs="+", metavar=("OUT", "RUN"))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--allow-server-default", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    mode = args.write or args.check
    if not mode or len(mode) < 2:
        parser.error("--write or --check takes OUT and at least one RUN")
    out, runs = Path(mode[0]), [Path(r) for r in mode[1:]]
    record = {
        "schema": SCHEMA,
        "runs": [read_run(run, args.allow_server_default) for run in runs],
    }
    text = dump(record)
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
