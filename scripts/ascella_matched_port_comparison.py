"""Compare the single-click output-port distributions of matched Ascella acquisitions, setting by setting.

Each run is a retained results/quandela/runs directory holding a collected results.json whose iterations carry one
counts dictionary per setting, keyed by the 12-mode click pattern. The acquisitions replay one frozen request, so
iteration i of every run holds the same setting; the script requires equal circuit_params and compilation seeds in the
runs' cases.json settings before it compares. A pattern with exactly one click lands on its port; every other
pattern counts as `other`. Per setting it reports the accepted counts, the pairwise total variation distance
between port distributions and the Pearson chi-square of homogeneity over the runs, whose degrees of freedom are
(runs - 1) times (occupied ports - 1). The chi-square treats each run's accepted events as independent draws from one
multinomial, so it measures departure beyond counting error under that assumption and carries no claim about
mesh identity.

Usage: python3 scripts/ascella_matched_port_comparison.py OUT RUN RUN [RUN ...]
RUN is a run directory name under results/quandela/runs; OUT is the JSON record written (created exclusively).
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results/quandela/runs"
PORTS = 12


def load(run: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """(cases.json, results.json) of one retained run."""
    path = RUNS / run
    cases = json.loads((path / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((path / "results.json").read_text(encoding="utf-8"))
    if results.get("partial") is not False or len(results["iterations"]) != len(cases["settings"]):
        raise ValueError(f"{run}: results are partial or do not match the settings")
    return cases, results


def setting_key(setting: dict[str, Any]) -> str:
    """The parameters that identify a setting independently of its cohort labels."""
    return json.dumps(
        {"circuit_params": setting["circuit_params"], "compilation_seed": setting.get("compilation_seed")},
        sort_keys=True,
    )


def ports(counts: dict[str, int]) -> tuple[list[int], int]:
    """Single-click counts per port and the count of every other pattern."""
    accepted = [0] * PORTS
    other = 0
    for key, count in counts.items():
        pattern = [int(part) for part in key.split(",")]
        if len(pattern) != PORTS or min(pattern) < 0:
            raise ValueError(f"count key {key[:40]!r} is not a {PORTS}-mode pattern")
        if sum(pattern) == 1:
            accepted[pattern.index(1)] += count
        else:
            other += count
    return accepted, other


def chi_square(rows: list[list[int]]) -> tuple[float, int]:
    """Pearson chi-square of homogeneity over the occupied ports and its degrees of freedom."""
    totals = [sum(row[port] for row in rows) for port in range(PORTS)]
    occupied = [port for port in range(PORTS) if totals[port] > 0]
    grand = sum(totals)
    statistic = 0.0
    for row in rows:
        size = sum(row)
        for port in occupied:
            expected = size * totals[port] / grand
            statistic += (row[port] - expected) ** 2 / expected
    return statistic, (len(rows) - 1) * (len(occupied) - 1)


def compare(runs: list[str]) -> dict[str, Any]:
    """The per-setting comparison record of the named runs, in the given order."""
    loaded = [load(run) for run in runs]
    keys = [[setting_key(s) for s in cases["settings"]] for cases, _ in loaded]
    if any(k != keys[0] for k in keys):
        raise ValueError("the runs do not carry the same settings in the same order")
    settings = []
    for index in range(len(keys[0])):
        tallies = [ports(results["iterations"][index]["counts"]) for _, results in loaded]
        rows = [accepted for accepted, _ in tallies]
        shares = [[count / sum(row) for count in row] for row in rows]
        statistic, degrees = chi_square(rows)
        settings.append(
            {
                "setting": index,
                "accepted": [sum(row) for row in rows],
                "other": [other for _, other in tallies],
                "total_variation": {
                    f"{runs[a]} | {runs[b]}": 0.5 * sum(abs(x - y) for x, y in zip(shares[a], shares[b], strict=True))
                    for a, b in itertools.combinations(range(len(runs)), 2)
                },
                "chi_square": statistic,
                "degrees_of_freedom": degrees,
            }
        )
    return {"schema": "ascella-matched-port-comparison-v1", "runs": runs, "settings": settings}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(__doc__)
    record = compare(argv[2:])
    with Path(argv[1]).open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    for row in record["settings"]:
        print(row["setting"], row["accepted"], f"chi2 {row['chi_square']:.1f}/{row['degrees_of_freedom']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
