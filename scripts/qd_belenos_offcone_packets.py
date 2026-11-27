"""Packet reading of Belenos off-cone clicks: bins, single-packet law, exposure fits and held-out cells.

The light-cone record (belenos_light_cone.json, qd_belenos_cone.py) holds each cell's off-cone clicks by mode.
This reading adds the in-cone histogram of every cell from the retained raw runs and asks how off-cone counts
distribute and what they scale with:

- bins of each mode's count per cell (0, 1..31, 32..99, 100 and more), off-cone per mode and in-cone pooled; a
  Poisson count with a continuously varying rate fills 1..31, and the in-cone modes do;
- the single-packet law: counts below PACKET_CEILING on modes other than HOT_MODE, with n, mean and variance (a
  Poisson count of mean about PACKET_UNIT has variance near its mean);
- packets per iterated cell: each nonzero off-cone count of a mode other than HOT_MODE divided by PACKET_UNIT,
  rounded, minimum 1, summed over the cell;
- the fit of one rate times an exposure (recorded samples, wall-time share, acquisition-time estimate) to those
  packets, as Poisson deviance with n - 1 degrees of freedom and log-likelihood;
- the held-out reading: the single-job cells, outside the fit, against the rate fitted on the iterated cells;
- mode HOT_MODE, which follows a separate law, and the packets of the other modes, each per 10,000 samples and per
  acquisition second by physical_perf class.

PACKET_UNIT is the mean of the single-packet law rounded down to the integer that reproduces the counts the
analysis was first read at; the sensitivity of the fit to it is recorded under packet_unit_sensitivity.

--write OUT CONE RUN... writes the record, --check OUT CONE RUN... recomputes it and requires equal bytes, and
--self-test runs paired controls: a background stationary in time must favor the time exposure, a packet process
per recorded sample must favor samples, and Poisson counts with continuous rates must fill 1..31 where the
retained off-cone counts leave it empty. Every synthetic draw takes deterministic quantiles, so no random seed
enters.

Usage: "$PYTHON" scripts/qd_belenos_offcone_packets.py (--write OUT CONE RUN... | --check OUT CONE RUN... | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import qd_belenos_cone as cone_lib  # noqa: E402
import qd_belenos_mesh as mesh_lib  # noqa: E402

SCHEMA = "qd-belenos-offcone-packets-v1"
MODES = mesh_lib.MODES
HOT_MODE = 5
PACKET_CEILING = 70
PACKET_UNIT = 47
UNIT_SENSITIVITY = (47.0, 47.2, 47.6, 48.0)
BIN_LABELS = ("0", "1..31", "32..99", ">=100")
EXPOSURES = ("samples", "wall_share_s", "acquisition_s_estimate")
# Class edges on physical_perf: the 1500-sample iterations (about 0.001 to 0.009), the 0.0085 to 0.0095 group, the
# 0.02 to 0.026 group and the 0.05 to 0.07 budgets.
PERF_EDGES = (0.002, 0.005, 0.015)
GOLDEN = (math.sqrt(5.0) - 1.0) / 2.0


def bin_of(n: int) -> int:
    return 0 if n == 0 else 1 if n < 32 else 2 if n < 100 else 3


def one_click_histogram(counts: dict[tuple[int, ...], int]) -> list[int]:
    single = [0] * MODES
    for state, n in counts.items():
        if sum(state) == 1:
            single[state.index(1)] += n
    return single


def cell_histograms(cone_record: dict[str, Any], runs: list[Path]) -> list[dict[str, Any]]:
    """The cone record's cells in order, each with its one-click histogram read from the run's raw payload."""
    if cone_record["schema"] != cone_lib.SCHEMA:
        raise SystemExit(f"offcone packets: the light-cone record schema is not {cone_lib.SCHEMA}")
    by_run: dict[str, list[dict[str, Any]]] = {}
    for c in cone_record["cells"]:
        by_run.setdefault(c["run"], []).append(c)
    if sorted(r.name for r in runs) != sorted(by_run):
        raise SystemExit("offcone packets: the runs differ from the runs of the light-cone record")
    out = []
    for run in runs:
        inner = mesh_lib.raw_result(run)
        entries = inner.get("results_list") or [inner]
        cells = by_run[run.name]
        if len(entries) != len(cells):
            raise SystemExit(f"{run.name}: {len(entries)} payload entries against {len(cells)} record cells")
        for c, entry in zip(cells, entries, strict=True):
            single = one_click_histogram(mesh_lib.bscount(entry["results"]))
            if sum(single) != c["one_click_samples"]:
                raise SystemExit(f"{run.name}/{c['name']}: one-click total differs from the light-cone record")
            out.append({"cell": c, "single": single})
    return out


def bins_of(counts: list[int]) -> list[int]:
    out = [0, 0, 0, 0]
    for n in counts:
        out[bin_of(n)] += 1
    return out


def bin_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    off: dict[int, list[int]] = {q: [] for q in range(MODES)}
    inside: list[int] = []
    for row in rows:
        members = set(row["cell"]["cone_modes"])
        for q in range(MODES):
            (inside if q in members else off[q]).append(row["single"][q])
    pooled = [sum(col) for col in zip(*(bins_of(v) for v in off.values() if v), strict=True)]
    return {
        "labels": list(BIN_LABELS),
        "in_cone": bins_of(inside),
        "off_cone_pooled": pooled,
        "off_cone_by_mode": {str(q): bins_of(v) for q, v in off.items() if v},
        "in_cone_nonzero_1_31": sum(1 for n in inside if 1 <= n < 32),
        "in_cone_nonzero": sum(1 for n in inside if n),
    }


def packet_law(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [
        n
        for row in rows
        for q, n in row["cell"]["off_cone_by_mode"].items()
        if int(q) != HOT_MODE and n < PACKET_CEILING
    ]
    return {
        "ceiling": PACKET_CEILING,
        "n": len(values),
        "mean": round(statistics.fmean(values), 6),
        "variance": round(statistics.variance(values), 6),
        "multiples_above_ceiling": sorted(
            n
            for row in rows
            for q, n in row["cell"]["off_cone_by_mode"].items()
            if int(q) != HOT_MODE and n >= PACKET_CEILING
        )[:20],
    }


def packets_of(cell: dict[str, Any], unit: float = PACKET_UNIT) -> int:
    return sum(max(1, round(n / unit)) for q, n in cell["off_cone_by_mode"].items() if int(q) != HOT_MODE and n > 0)


def deviance(y: list[int], mu: list[float]) -> float:
    return 2.0 * sum((yi * math.log(yi / mi) if yi else 0.0) - (yi - mi) for yi, mi in zip(y, mu, strict=True))


def log_likelihood(y: list[int], mu: list[float]) -> float:
    return sum(yi * math.log(mi) - mi - math.lgamma(yi + 1) for yi, mi in zip(y, mu, strict=True))


def fit(y: list[int], exposure: list[float]) -> dict[str, Any]:
    rate = sum(y) / sum(exposure)
    mu = [rate * x for x in exposure]
    return {
        "rate": rate,
        "deviance": round(deviance(y, mu), 3),
        "df": len(y) - 1,
        "log_likelihood": round(log_likelihood(y, mu), 3),
    }


def exposure_fits(cells: list[dict[str, Any]], unit: float = PACKET_UNIT) -> dict[str, Any]:
    y = [packets_of(c, unit) for c in cells]
    out: dict[str, Any] = {"packets": sum(y), "cells": len(cells)}
    for name in EXPOSURES:
        f = fit(y, [float(c[name]) for c in cells])
        f["rate"] = float(f"{f['rate']:.6e}")
        out[name] = f
    return out


def held_out(fitted: list[dict[str, Any]], held: list[dict[str, Any]]) -> dict[str, Any]:
    y = [packets_of(c) for c in fitted]
    out: dict[str, Any] = {"cells": len(held), "observed": sum(packets_of(c) for c in held)}
    for name in EXPOSURES:
        rate = sum(y) / sum(float(c[name]) for c in fitted)
        out[name] = round(rate * sum(float(c[name]) for c in held), 3)
    return out


def perf_class(perf: float) -> int:
    return sum(perf >= edge for edge in PERF_EDGES)


def hot_mode(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[int, list[dict[str, Any]]] = {}
    for c in cells:
        groups.setdefault(perf_class(c["physical_perf"]), []).append(c)
    rows = []
    for k, members in sorted(groups.items()):
        clicks = sum(c["off_cone_by_mode"].get(str(HOT_MODE), 0) for c in members)
        samples = sum(c["samples"] for c in members)
        seconds = sum(c["acquisition_s_estimate"] for c in members)
        packets = sum(packets_of(c) for c in members)
        rows.append(
            {
                "class": k,
                "packets_other_modes": packets,
                "packets_per_10000_samples": round(10000 * packets / samples, 3),
                "packets_per_acquisition_s": round(packets / seconds, 3),
                "cells": len(members),
                "physical_perf_min": min(c["physical_perf"] for c in members),
                "physical_perf_max": max(c["physical_perf"] for c in members),
                "mode_clicks": clicks,
                "per_10000_samples": round(10000 * clicks / samples, 3),
                "per_acquisition_s": round(clicks / seconds, 3),
            }
        )
    return rows


def reading(cone_record: dict[str, Any], runs: list[Path]) -> dict[str, Any]:
    rows = cell_histograms(cone_record, runs)
    iterated = [r["cell"] for r in rows if r["cell"]["form"] == "iterated"]
    single = [r["cell"] for r in rows if r["cell"]["form"] == "single"]
    return {
        "schema": SCHEMA,
        "source_schema": cone_record["schema"],
        "runs": [r.name for r in runs],
        "hot_mode": HOT_MODE,
        "packet_unit": PACKET_UNIT,
        "bins_iterated_cells": bin_table([r for r in rows if r["cell"]["form"] == "iterated"]),
        "bins_all_cells": bin_table(rows),
        "single_packet_law_all_cells": packet_law(rows),
        "single_packet_law_iterated_cells": packet_law([r for r in rows if r["cell"]["form"] == "iterated"]),
        "packets_per_cell": [{"run": c["run"], "name": c["name"], "packets": packets_of(c)} for c in iterated],
        "exposure_fits_iterated": exposure_fits(iterated),
        "packet_unit_sensitivity": {str(u): exposure_fits(iterated, u) for u in UNIT_SENSITIVITY},
        "held_out_single_cells": held_out(iterated, single),
        "mode_5_by_physical_perf_class": hot_mode(iterated),
        "perf_class_edges": list(PERF_EDGES),
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def poisson_quantile(mean: float, u: float) -> int:
    """The smallest k with P(N <= k) >= u for N ~ Poisson(mean), 0 < u < 1."""
    k, term = 0, math.exp(-mean)
    total = term
    while total < u and k < 10000:
        k += 1
        term *= mean / k
        total += term
    return k


def quantiles(n: int, offset: float = 0.0) -> list[float]:
    """n deterministic, equidistributed values in (0, 1): the golden-ratio sequence."""
    return [((offset + 0.5 + k * GOLDEN) % 1.0) or 0.5 for k in range(1, n + 1)]


def synthetic(rate_on: str, n: int = 58) -> tuple[list[int], dict[str, list[float]]]:
    """Packet counts of n cells whose recorded samples and acquisition times vary independently over the spans of
    the retained cells (samples 1500 to 60000; times a 36-fold span), under a rate on samples or on time."""
    sample_pool = (1500.0, 10000.0, 40000.0, 60000.0)
    samples = [sample_pool[int(u * 4) % 4] for u in quantiles(n, 0.17)]
    seconds = [0.05 * 36**u for u in quantiles(n, 0.61)]
    exposure = {"samples": samples, "acquisition_s_estimate": seconds}
    base = exposure["samples" if rate_on == "samples" else "acquisition_s_estimate"]
    scale = 4.0 / (sum(base) / n)
    y = [poisson_quantile(scale * x, u) for x, u in zip(base, quantiles(n, 0.33), strict=True)]
    return y, exposure


def self_test() -> int:
    """Paired controls that can fail: each exposure wins on its own synthetic law and loses on the other's."""
    problems = []
    for law, winner, loser in (
        ("time", "acquisition_s_estimate", "samples"),
        ("samples", "samples", "acquisition_s_estimate"),
    ):
        y, exposure = synthetic(law)
        fits = {name: fit(y, x) for name, x in exposure.items()}
        gap = fits[loser]["deviance"] - fits[winner]["deviance"]
        if not (gap > 20 and fits[winner]["deviance"] < 2 * fits[winner]["df"]):
            problems.append(f"{law}-law control: deviance {fits}, the {winner} exposure must win by more than 20")
    # The paired mutant: a real packet process per sample must not read as stationary in time.
    y, exposure = synthetic("samples")
    if fit(y, exposure["acquisition_s_estimate"])["deviance"] <= fit(y, exposure["samples"])["deviance"]:
        problems.append("mutant control: the wrong exposure fits a per-sample process as well as the right one")
    # A Poisson background with continuous rates fills 1..31; one packet law (zero or a size near PACKET_UNIT) does not.
    rates = [0.02 * 3 ** (4 * u) for u in quantiles(400, 0.5)]
    poisson = [poisson_quantile(r * 12.0, u) for r, u in zip(rates, quantiles(400, 0.07), strict=True)]
    packets = [0 if u < 0.85 else PACKET_UNIT + poisson_quantile(0.0, 0.5) for u in quantiles(400, 0.29)]
    if bins_of(poisson)[1] < 40:
        problems.append(f"continuous-rate control: bins {bins_of(poisson)} leave 1..31 nearly empty")
    if bins_of(packets)[1] != 0:
        problems.append(f"packet control: bins {bins_of(packets)} fill 1..31")
    if abs(deviance([3, 0, 2], [3.0, 0.0001, 2.0]) - 2 * 0.0001) > 1e-3:
        problems.append("deviance of an exact fit is not near zero")
    if problems:
        raise SystemExit("offcone packets self-test failed:\n" + "\n".join(problems))
    print("offcone packets self-test passed: exposure pairs, mutant, continuous-rate bins, packet bins")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, nargs="+", metavar=("OUT", "CONE"))
    group.add_argument("--check", type=Path, nargs="+", metavar=("OUT", "CONE"))
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    out, cone_path, *runs = args.write or args.check
    text = dump(reading(json.loads(cone_path.read_text(encoding="utf-8")), runs))
    if args.write:
        out.write_text(text, encoding="utf-8")
        print(f"{out}: written")
        return 0
    if out.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{out}: the packet reading differs from its retained runs")
    print(f"{out}: packet reading replays")
    return 0


if __name__ == "__main__":
    sys.exit(main())
