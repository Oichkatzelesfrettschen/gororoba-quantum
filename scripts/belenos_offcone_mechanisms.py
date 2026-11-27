"""Belenos off-cone packet mechanisms: one iterated qpu:belenos case that separates three origins of the packets.

Off-cone clicks on qpu:belenos arrive as zero-or-packet counts of about 47 clicks on modes outside a source's light
cone (docs/notes/quandela/strategy.md, "Off-cone clicks"), and three mechanisms survive the retained data:

- episodes: the photon triggers the packets, so the packet rate per sample depends on which detectors the source
  lights;
- window: noise over an acquisition window proportional to the recorded samples (window_samples), or proportional to
  samples over the served physical_perf (window_time), the estimate of the true acquisition time;
- balancing: the server's default DetectorBalancing processing rewrites the counts, so a job that sends
  mitigations = [] carries no packets.

The case keeps the circuit and compilation seed of belenos_mesh/job-16, whose seed 20 served mesh 29dc6ef8, and moves
the one photon between two sources of that circuit's four-mode block, modes 20 and 22, whose cones (modes 8 to 23 and
6 to 23 on 29dc6ef8) both leave the hot channels 0, 1 and 5 off-cone. job-00 sends the server's default mitigations;
job-01 repeats every setting with mitigations = [] (Perceval sets the policy once per body, so the arm cannot be
interleaved).

Usage: "$PYTHON" scripts/belenos_offcone_mechanisms.py (--build | --check | --power)
  --build  write results/quandela/cases/belenos_offcone_mechanisms/job-00 and job-01
  --check  rebuild both jobs and compare them byte for byte
  --power  print the exact power table the preregistration carries
"""

from __future__ import annotations

import argparse
import bisect
import functools
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_belenos_mesh as mesh  # noqa: E402

FAMILY = "belenos_offcone_mechanisms"
JOBS = ("job-00", "job-01")
CASES = ROOT / "results/quandela/cases"
SOURCE = CASES / "belenos_mesh" / "job-16"
DESIGN = "docs/design/belenos-offcone-mechanisms-case.md"
PLATFORM = "qpu:belenos"
# The identifier that reproduces mesh 29dc6ef8 on the job-16 circuit; it keeps its value (AGENTS.md, "Seeds").
COMPILATION_SEED = mesh.DWELL_Q1_SEED
MESH_PREFIX = "29dc6ef8"
CIRCUIT_SHA256 = "69326bf0674a45e8c0005b10e2ac72cee36c122691ec0a5b542dbabb6e1fffb9"
# Source modes of the block on modes 20 to 23; both are connected photon-source modes of the qpu:belenos record.
SOURCES = (20, 22)
# Recorded samples per entry and entries per source at each level: the 1500 level opens the job (belenos_mesh
# job-12 passed its 1500-sample opening, five 10000-sample openings failed), 60000 is the largest retained entry.
LEVELS = (1500, 10000, 60000)
REPEATS = (8, 5, 5)
SHOT_HEADROOM = 2
MAX_DURATION = 300
DURATION_MARGIN = 0.9
# qpu:belenos job duration is 8.16 s plus 6.00 s per results_list entry with no positive sample slope
# (docs/evidence/quandela/belenos_offcone_packets.json, job_duration_fit, ten runs, R^2 0.9999).
JOB_SECONDS = 8.16
ENTRY_SECONDS = 6.0
PER_JOB_CREDITS = 1.0
CREDITS_PER_SHOT = 1e-6
# Presence of a packet per recorded sample over the 58 iterated cells (49 presences in 451,500 samples).
PRESENCE_PER_SAMPLE = 49 / 451_500
# physical_perf served at each level on 29dc6ef8, seed 20, within one job (strategy.md, "Timing").
PHYSICAL_PERF = {1500: 0.0030, 10000: 0.0225, 60000: 0.0528}
PACKET_FLOOR = 32
ALPHA = 0.05
HOT_CHANNELS = (0, 1, 5)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"{FAMILY}: {message}")


def schedule() -> list[dict[str, Any]]:
    """The settings: repeat blocks of the levels still owed, each level's two sources alternating their order."""
    rows: list[dict[str, Any]] = []
    for block in range(max(REPEATS)):
        for k, level in enumerate(LEVELS):
            if block >= REPEATS[k]:
                continue
            order = SOURCES if (block + k) % 2 == 0 else SOURCES[::-1]
            for source in order:
                rows.append(
                    {
                        "name": f"e{len(rows):02d}-s{source}-n{level}",
                        "compilation_seed": COMPILATION_SEED,
                        "input_mode": source,
                        "max_samples": level,
                        "max_shots": SHOT_HEADROOM * level,
                    }
                )
    return rows


# Exact power ------------------------------------------------------------------------------------------------------


def binomial_pmf(n: int, k: int, p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return float(k == (n if p >= 1.0 else 0))
    log = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)
    return math.exp(log)


def poisson_pmf(mean: float, t: int) -> float:
    return math.exp(-mean + t * math.log(mean) - math.lgamma(t + 1)) if mean > 0 else float(t == 0)


@functools.cache
def rejection_region(n: int, p0: float) -> tuple[int, ...]:
    """The counts k whose two-sided exact binomial p-value (the sum of the pmf over every count at most as likely as
    k, with scipy's relative tolerance) falls below ALPHA."""
    pmf = [binomial_pmf(n, k, p0) for k in range(n + 1)]
    ranked = sorted(pmf)
    running = [0.0]
    for x in ranked:
        running.append(running[-1] + x)
    return tuple(k for k in range(n + 1) if running[bisect.bisect_right(ranked, pmf[k] * (1 + 1e-7))] < ALPHA)


def conditional_power(mean_low: float, mean_high: float, p0: float) -> float:
    """P(reject the share p0 of the first count) when the counts are Poisson with these means: given the total t, the
    first count is binomial(t, mean_low / (mean_low + mean_high))."""
    total = mean_low + mean_high
    q = mean_low / total
    top = int(total + 12 * math.sqrt(total) + 30)
    return sum(
        poisson_pmf(total, t) * sum(binomial_pmf(t, k, q) for k in rejection_region(t, p0)) for t in range(1, top)
    )


def exposure(rows: list[dict[str, Any]], **where: int) -> int:
    keys = {"source": "input_mode", "level": "max_samples"}
    return sum(r["max_samples"] for r in rows if all(r[keys[k]] == v for k, v in where.items()))


def power_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Exact power of the three contrasts at PRESENCE_PER_SAMPLE, Poisson counts, one job (job-01 repeats job-00)."""
    total = sum(r["max_samples"] for r in rows)
    expected = PRESENCE_PER_SAMPLE * total
    rate = {s: PRESENCE_PER_SAMPLE * exposure(rows, source=s) for s in SOURCES}
    p_source = rate[SOURCES[0]] / (rate[SOURCES[0]] + rate[SOURCES[1]])
    low, high = LEVELS[0], LEVELS[-1]
    # window_time puts a level's packets in proportion to samples / physical_perf, normalized to the same total.
    weight = {lv: exposure(rows, level=lv) / PHYSICAL_PERF[lv] for lv in LEVELS}
    time_mean = {lv: expected * weight[lv] / sum(weight.values()) for lv in LEVELS}
    sample_mean = {lv: PRESENCE_PER_SAMPLE * exposure(rows, level=lv) for lv in LEVELS}
    p_sample = sample_mean[low] / (sample_mean[low] + sample_mean[high])
    p_time = time_mean[low] / (time_mean[low] + time_mean[high])
    return {
        "expected_presences_per_job": round(expected, 2),
        "expected_presences_by_source": {str(s): round(rate[s], 2) for s in SOURCES},
        "source_contrast": {
            "null_share_of_second_source": round(p_source, 4),
            "power_by_rate_ratio": {
                str(ratio): round(conditional_power(rate[SOURCES[0]], ratio * rate[SOURCES[1]], p_source), 4)
                for ratio in (1.0, 1.5, 2.0, 3.0)
            },
        },
        "level_contrast": {
            "levels": [low, high],
            "expected_presences_sample_law": {str(lv): round(sample_mean[lv], 2) for lv in LEVELS},
            "expected_presences_time_law": {str(lv): round(time_mean[lv], 2) for lv in LEVELS},
            "reject_sample_law_when_time_law_holds": round(
                conditional_power(time_mean[low], time_mean[high], p_sample), 4
            ),
            "reject_time_law_when_sample_law_holds": round(
                conditional_power(sample_mean[low], sample_mean[high], p_time), 4
            ),
            "size_of_sample_law_test": round(conditional_power(sample_mean[low], sample_mean[high], p_sample), 4),
        },
        "mitigation_contrast": {
            "null_share_of_job_01": 0.5,
            "power_by_rate_ratio_of_job_01": {
                str(ratio): round(conditional_power(expected, ratio * expected, 0.5), 4)
                for ratio in (0.0, 0.25, 0.5, 1.0)
            },
        },
    }


# Documents --------------------------------------------------------------------------------------------------------


def seconds(rows: list[dict[str, Any]]) -> float:
    return round(JOB_SECONDS + ENTRY_SECONDS * len(rows), 2)


def credit_ceiling(rows: list[dict[str, Any]]) -> float:
    """Per-job credits plus the largest iteration's max_shots at the per-shot price (an iterated job bills at most
    that cap, qd_platform.plan)."""
    return round(PER_JOB_CREDITS + CREDITS_PER_SHOT * max(r["max_shots"] for r in rows), 6)


def preregistered(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "series": "off-cone packet origin on the job-16 circuit and seed (pool row QPU-43)",
        "mesh_variance": {"kind": "anchors", "anchors": 1, "repeats_per_anchor": len(rows)},
        "void": "an entry is void when its served mesh sha256 does not start with " + MESH_PREFIX + ", its "
        "computed_input is not one photon on its setting's input_mode, or its recorded samples differ from its "
        "max_samples; a job whose results_list length differs from iterations is void; job-00 with fewer than 25 "
        "presences in all entries reads 'rate not reproduced' and no contrast reads",
        "observable": "per entry, over the modes outside the cone of the entry's returned mesh and source "
        "(scripts/qd_belenos_cone.py), the presences: the off-cone modes whose one-click count is at least "
        + str(PACKET_FLOOR)
        + ". An off-cone count from 1 to "
        + str(PACKET_FLOOR - 1)
        + " is a break of the zero-or-packet law and is reported beside the presences",
        "mechanisms": {
            "episodes": "the photon triggers packets: presences per sample differ between the two sources, which "
            "light different detectors (source 20 reaches modes 20 and 21 on the ideal block, source 22 all four)",
            "window_samples": "noise over a window proportional to the recorded samples at a source-independent "
            "rate: equal presences per sample for both sources and at every level",
            "window_time": "noise over the true acquisition window, samples over physical_perf: equal for both "
            "sources, and presences per sample at 1500 samples above those at 60000 by physical_perf(60000) / "
            "physical_perf(1500) = " + str(round(PHYSICAL_PERF[60000] / PHYSICAL_PERF[1500], 1)),
            "balancing": "the default DetectorBalancing processing makes the packets: job-01 (mitigations = []) "
            "reads none",
        },
        "contrasts": {
            "mitigation": "total presences of job-01 against job-00 over their equal exposures: two-sided exact "
            "binomial test of job-01's share of the pair at 1/2, alpha " + str(ALPHA),
            "source": "presences of source 22 against source 20 within a job: two-sided exact binomial test of "
            "source 22's share at the exposure share, alpha " + str(ALPHA) + "; pooled over both jobs when the "
            "mitigation contrast does not reject",
            "level": "presences at 1500 samples against those at 60000: two-sided exact binomial test of the 1500 "
            "share at the sample-law share, alpha " + str(ALPHA) + ", and the same test at the time-law share",
        },
        "readings": {
            "balancing": "the mitigation contrast rejects with job-01's share below 1/2",
            "episodes": "the mitigation contrast does not reject and the source contrast rejects",
            "window_samples": "neither the mitigation nor the source contrast rejects, the sample-law share holds "
            "and the time-law share is rejected",
            "window_time": "neither the mitigation nor the source contrast rejects, the time-law share holds and "
            "the sample-law share is rejected",
            "no attribution": "any other pattern, a void job, or a level contrast whose two tests both hold or "
            "both reject",
        },
        "power": power_table(rows),
        "power_basis": "exact Poisson counts at " + format(PRESENCE_PER_SAMPLE, ".4e") + " presences per sample "
        "(49 in 451,500 samples of the 58 iterated cells of docs/evidence/quandela/belenos_offcone_packets.json); "
        "retained packets of one cell co-occur across modes 0 and 5 (20 cells against 13.9 expected), so the table "
        "is an upper bound on every power entry",
    }


def documents() -> dict[str, bytes]:
    source = json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))
    circuit = (SOURCE / "circuit.json").read_bytes()
    require(hashlib.sha256(circuit).hexdigest() == CIRCUIT_SHA256, "belenos_mesh/job-16 circuit.json changed")
    require(source["circuit"]["sha256"] == CIRCUIT_SHA256, "belenos_mesh/job-16 cases.json names another circuit")
    rows = schedule()
    require(len(rows) == 2 * sum(REPEATS), "the schedule lost an entry")
    for level in LEVELS:
        require(
            exposure(rows, level=level, source=SOURCES[0]) == exposure(rows, level=level, source=SOURCES[1]),
            "levels differ",
        )
    require(seconds(rows) <= DURATION_MARGIN * MAX_DURATION, f"{seconds(rows)} s leaves the duration margin")
    out = {}
    for job in JOBS:
        manifest: dict[str, Any] = {
            "schema": source["schema"],
            "family": FAMILY,
            "job": job,
            "platforms": [PLATFORM],
            "command": source["command"],
            "gate_form": source["gate_form"],
            "min_detected_photons": source["min_detected_photons"],
            "iterations": len(rows),
            "max_samples": sum(r["max_samples"] for r in rows),
            "max_shots": sum(r["max_shots"] for r in rows),
            "max_duration": MAX_DURATION,
            "max_credits": credit_ceiling(rows),
            "expected_seconds": seconds(rows),
        }
        if job == "job-01":
            manifest["mitigations"] = []
        manifest |= {
            "census": source["census"],
            "circuit": source["circuit"],
            "blocks": source["blocks"],
            "settings": rows,
            "design": DESIGN,
            "seeded_from": {
                "case": "belenos_mesh/job-16",
                "cases_sha256": hashlib.sha256((SOURCE / "cases.json").read_bytes()).hexdigest(),
                "use": "circuit.json byte for byte and compilation_seed 20, the identifier of mesh " + MESH_PREFIX,
            },
            "preregistered": preregistered(rows),
        }
        out[f"{job}/cases.json"] = (json.dumps(manifest, indent=1) + "\n").encode()
        out[f"{job}/circuit.json"] = circuit
    return out


def build(check_only: bool) -> int:
    for name, data in documents().items():
        path = CASES / FAMILY / name
        if check_only:
            require(path.exists() and path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    rows = schedule()
    print(f"{FAMILY}: {len(rows)} entries, {seconds(rows)} s, credit ceiling {credit_ceiling(rows)} per job")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--power", action="store_true")
    args = parser.parse_args()
    if args.power:
        print(json.dumps(power_table(schedule()), indent=1))
        return 0
    return build(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
