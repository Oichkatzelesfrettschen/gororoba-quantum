"""Belenos off-cone packet mechanisms: one iterated qpu:belenos case that separates three origins of the packets.

Off-cone clicks on qpu:belenos arrive as zero-or-packet counts of about 47 clicks on modes outside a source's light
cone (docs/notes/quandela/strategy.md, "Off-cone clicks"), and three mechanisms survive the retained data:

- episodes: the photon triggers the packets, so the packet rate per sample depends on which detectors the source
  lights;
- window: noise over an acquisition window proportional to the recorded samples (window_samples), or proportional to
  samples over the served physical_perf (window_time), the estimate of the true acquisition time;
- balancing: the server's default DetectorBalancing processing amplifies rare raw clicks into packets. It rescales
  and resamples the modes that carry raw clicks and creates none on a zero-count mode, so mitigations = [] tests
  amplification and no fabrication from zero.

The case keeps the circuit and compilation seed of belenos_mesh/job-16, whose seed 20 served mesh 29dc6ef8, and moves
the one photon between two sources of that circuit's four-mode block, modes 20 and 22, whose cones (modes 8 to 23 and
6 to 23 on 29dc6ef8) both leave the hot channels 0, 1 and 5 off-cone. Source 22 puts 59.8 percent of its ideal photons
on detectors 20 and 21, the detectors source 20 lights alone, so the source-rate ratio the episodes mechanism can
produce on 29dc6ef8 is at most 1.67 (ideal_shares). job-00 and job-02 send the server's default mitigations and job-01
repeats every setting with mitigations = [] between them (Perceval sets the policy once per body, so the arm cannot
be interleaved; the default-off-default order separates the arm from drift between jobs).

Usage: "$PYTHON" scripts/belenos_offcone_mechanisms.py (--build | --check | --power)
  --build  write results/quandela/cases/belenos_offcone_mechanisms/job-00, job-01 and job-02
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
JOBS = ("job-00", "job-01", "job-02")
DEFAULT_JOBS = ("job-00", "job-02")
CASES = ROOT / "results/quandela/cases"
SOURCE = CASES / "belenos_mesh" / "job-16"
SOURCE_RUN = ROOT / "results/quandela/runs/2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16"
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
REPEATS = (5, 5, 5)
SHOT_HEADROOM = 2
MAX_DURATION = 300
DURATION_MARGIN = 0.9
# qpu:belenos job duration: 8.16 s plus 6.00 s per results_list entry in the ten-run fit of
# docs/evidence/quandela/belenos_offcone_packets.json (job_duration_fit, R^2 0.9999, at most 24 entries and 36,000
# samples), and 6.9 to 7.3 s per iteration at 24 x 100,000 samples and up to 9.6 s at 12 x 300,000 samples over the
# 136 completed jobs of docs/runbooks/quandela-credit-optimization.md. The case plans at the runbook's 7.3 s and
# checks the 9.6 s bound against max_duration.
JOB_SECONDS = 8.16
ENTRY_SECONDS = 7.3
WORST_ENTRY_SECONDS = 9.6
PER_JOB_CREDITS = 1.0
CREDITS_PER_SHOT = 1e-6
# Primary presence rate per recorded sample over the 58 iterated cells: the off-cone modes other than mode 5 (49
# presences in 452,000 samples); mode 5 (31 presences) is a separate secondary readout.
PRESENCE_PER_SAMPLE = 49 / 452_000
MODE5_PER_SAMPLE = 31 / 452_000
SECONDARY_MODE = 5
SOURCE_RATIOS = (1.0, 1.25, 1.5, 2.0, 3.0)
MITIGATION_RATIOS = (0.0, 0.25, 0.5, 1.0)
DRIFT_RATIOS = (1.0, 1.5, 2.0)
# physical_perf served at each level on 29dc6ef8, seed 20, within one job (strategy.md, "Timing").
PHYSICAL_PERF = {1500: 0.0030, 10000: 0.0225, 60000: 0.0528}
PACKET_FLOOR = 32
ALPHA = 0.05
HOT_CHANNELS = (0, 1, 5)
LIT_DETECTORS = (20, 21)


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


@functools.cache
def ideal_shares() -> dict[int, dict[str, float]]:
    """Each source's ideal output share on the detectors LIT_DETECTORS and on modes 10 to 19 of the served mesh
    29dc6ef8 (the first entry of the retained belenos_mesh/job-16 run), by exact propagation."""
    inner = mesh.raw_result(SOURCE_RUN)
    elements = mesh.decode(inner["results_list"][0]["computed_circuit"])
    require(mesh.mesh_sha(inner["results_list"][0]["computed_circuit"]).startswith(MESH_PREFIX), "wrong source mesh")
    arch = mesh.run_architecture(elements)
    phases = mesh.mesh_phases(arch, elements)
    out = {}
    for source in SOURCES:
        ideal = mesh.propagate(arch, phases, source)[0]
        out[source] = {
            "detectors_20_21": round(float(sum(ideal[q] for q in LIT_DETECTORS)), 4),
            "modes_10_19": round(float(sum(ideal[10:20])), 4),
        }
    return out


def source_ratio_bound() -> float:
    """The largest source-20 over source-22 presence-rate ratio the episodes mechanism can reach on 29dc6ef8 when
    packets follow the photons on detectors 20 and 21: source 20 lights them with share 1, source 22 with its
    ideal share."""
    shares = ideal_shares()
    return round(shares[20]["detectors_20_21"] / shares[22]["detectors_20_21"], 3)


def exposure(rows: list[dict[str, Any]], **where: int) -> int:
    keys = {"source": "input_mode", "level": "max_samples"}
    return sum(r["max_samples"] for r in rows if all(r[keys[k]] == v for k, v in where.items()))


def power_table(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Exact power of the contrasts at PRESENCE_PER_SAMPLE with Poisson counts. The source and level contrasts pool
    the default jobs (job-00 and job-02); the mitigation contrast sets job-01 against both of them."""
    pooled = len(DEFAULT_JOBS)
    total = sum(r["max_samples"] for r in rows)
    expected = PRESENCE_PER_SAMPLE * total
    rate = {s: PRESENCE_PER_SAMPLE * pooled * exposure(rows, source=s) for s in SOURCES}
    p_source = rate[SOURCES[1]] / (rate[SOURCES[0]] + rate[SOURCES[1]])
    pool_total = rate[SOURCES[0]] + rate[SOURCES[1]]
    bound = source_ratio_bound()

    def fixed_total(ratio: float) -> float:
        # source 20 over source 22 at this ratio, the pooled total held at the retained rate
        return conditional_power(pool_total / (1 + ratio), pool_total * ratio / (1 + ratio), p_source)

    def halved_source(ratio: float) -> float:
        # source 20 keeps the retained rate and source 22 runs at 1 / ratio of it
        return conditional_power(rate[SOURCES[1]] / ratio, rate[SOURCES[0]], p_source)

    ratios = sorted({*SOURCE_RATIOS, bound})
    low, high = LEVELS[0], LEVELS[-1]
    # window_time puts a level's packets in proportion to samples / physical_perf, normalized to the same total.
    weight = {lv: exposure(rows, level=lv) / PHYSICAL_PERF[lv] for lv in LEVELS}
    time_mean = {lv: pooled * expected * weight[lv] / sum(weight.values()) for lv in LEVELS}
    sample_mean = {lv: PRESENCE_PER_SAMPLE * pooled * exposure(rows, level=lv) for lv in LEVELS}
    p_sample = sample_mean[low] / (sample_mean[low] + sample_mean[high])
    p_time = time_mean[low] / (time_mean[low] + time_mean[high])
    return {
        "expected_presences_per_job": round(expected, 2),
        "expected_presences_by_source_per_job": {str(s): round(rate[s] / pooled, 2) for s in SOURCES},
        "expected_mode_5_presences_per_job": round(MODE5_PER_SAMPLE * total, 2),
        "source_contrast": {
            "pooled_jobs": list(DEFAULT_JOBS),
            "null_share_of_second_source": round(p_source, 4),
            "rate_ratio_bound_on_29dc6ef8": bound,
            "power_by_rate_ratio_source_20_over_22": {
                "fixed_total": {str(r): round(fixed_total(r), 4) for r in ratios},
                "source_22_scaled": {str(r): round(halved_source(r), 4) for r in ratios},
            },
        },
        "level_contrast": {
            "pooled_jobs": list(DEFAULT_JOBS),
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
            "null_share_of_job_01": round(1 / (1 + pooled), 4),
            "power_by_rate_ratio_of_job_01": {
                str(r): round(conditional_power(r * expected, pooled * expected, 1 / (1 + pooled)), 4)
                for r in MITIGATION_RATIOS
            },
        },
        "drift_contrast": {
            "null_share_of_job_00": 0.5,
            "power_by_rate_ratio_job_02_over_job_00": {
                str(r): round(conditional_power(expected, r * expected, 0.5), 4) for r in DRIFT_RATIOS
            },
        },
    }


# Documents --------------------------------------------------------------------------------------------------------


def seconds(rows: list[dict[str, Any]]) -> float:
    return round(JOB_SECONDS + ENTRY_SECONDS * len(rows), 2)


def worst_seconds(rows: list[dict[str, Any]]) -> float:
    return round(JOB_SECONDS + WORST_ENTRY_SECONDS * len(rows), 2)


def credit_ceiling(rows: list[dict[str, Any]]) -> float:
    """Per-job credits plus the largest iteration's max_shots at the per-shot price (an iterated job bills at most
    that cap, qd_platform.plan)."""
    return round(PER_JOB_CREDITS + CREDITS_PER_SHOT * max(r["max_shots"] for r in rows), 6)


def preregistered(rows: list[dict[str, Any]]) -> dict[str, Any]:
    shares = ideal_shares()
    bound = source_ratio_bound()
    return {
        "series": "off-cone packet origin on the job-16 circuit and seed (pool row QPU-43)",
        "mesh_variance": {"kind": "anchors", "anchors": 1, "repeats_per_anchor": len(rows)},
        "jobs": "job-00 and job-02 send the server's default mitigations and job-01 sends mitigations = [], run in "
        "the order job-00, job-01, job-02; the three run unconditionally, and no presence count of an earlier job "
        "gates a later one",
        "void": "a source-20 entry is void when its served mesh sha256 does not start with " + MESH_PREFIX + "; a "
        "source-22 entry is void when its returned mesh, whichever it is, leaves any of modes "
        + ", ".join(str(m) for m in HOT_CHANNELS)
        + " inside the cone of that mesh and source (scripts/qd_belenos_cone.py); an entry of either source is void "
        "when its computed_input is not one photon on its setting's input_mode or its recorded samples differ from "
        "its max_samples. The returned mesh sha256 of every entry is reported beside its presences. Entries come "
        "in adjacent source pairs of one level, and a results_list that ends before iterations (a cut at "
        "max_duration) keeps its completed pairs: the contrasts read the observed exposures of the valid entries "
        "and the unpaired trailing entry is dropped. No presence count voids a job",
        "observable": "per entry, over the modes outside the cone of the entry's returned mesh and source "
        "(scripts/qd_belenos_cone.py) other than mode "
        + str(SECONDARY_MODE)
        + ", the presences (the primary count): the off-cone modes whose one-click count is at least "
        + str(PACKET_FLOOR)
        + ". Mode "
        + str(SECONDARY_MODE)
        + " is a separate secondary readout with its own presences, never added to the primary count. An off-cone "
        "count from 1 to " + str(PACKET_FLOOR - 1) + " is a break of the zero-or-packet law and is reported "
        "beside the presences",
        "source_separation": {
            "lit_detectors_of_source_20": list(LIT_DETECTORS),
            "ideal_share_on_detectors_20_21": {str(s): shares[s]["detectors_20_21"] for s in SOURCES},
            "ideal_share_on_modes_10_19": {str(s): shares[s]["modes_10_19"] for s in SOURCES},
            "max_rate_ratio_source_20_over_22": bound,
            "disjoint_source_pair": "none on mesh 29dc6ef8: of the twelve connected sources only 20 and 22 keep "
            "modes 0, 1 and 5 off-cone, and their lit detector sets overlap; a source 22 entry that returns "
            "another mesh brings its own cone and ideal shares, which the live plan read of the returned meshes "
            "states before submission",
            "degenerate_with_window_samples": "source-independent photon-triggered episodes (a packet per photon "
            "burst on any detector) give equal presences per sample for both sources and at every level, which is "
            "the window_samples prediction; the design separates detector-resolved episodes only, and the reading "
            "'window_samples or source-independent episodes' stays one reading",
        },
        "mechanisms": {
            "episodes": "detector-resolved photon-triggered packets: presences per sample follow the photons on "
            "the detectors the source lights, so source 20 reads up to "
            + str(bound)
            + " times the presences per sample of source 22 on 29dc6ef8 (ratio 1 would read no source effect)",
            "window_samples": "noise over a window proportional to the recorded samples at a source-independent "
            "rate, or source-independent photon-triggered episodes: equal presences per sample for both sources "
            "and at every level",
            "window_time": "noise over the true acquisition window, samples over physical_perf: equal for both "
            "sources, and presences per sample at 1500 samples above those at 60000 by physical_perf(60000) / "
            "physical_perf(1500) = " + str(round(PHYSICAL_PERF[60000] / PHYSICAL_PERF[1500], 1)),
            "balancing": "the default DetectorBalancing processing amplifies rare raw clicks into packets (it "
            "creates no click on a zero-count mode): job-01 (mitigations = []) reads fewer presences than the "
            "default jobs on both sides of it",
        },
        "contrasts": {
            "drift": "presences of job-02 against job-00 over their equal exposures: two-sided exact binomial test "
            "of job-02's share of the pair at 1/2, alpha " + str(ALPHA),
            "mitigation": "presences of job-01 against the pooled job-00 and job-02 over their equal exposures: "
            "two-sided exact binomial test of job-01's share of the three at 1/3, alpha " + str(ALPHA),
            "source": "presences of source 22 against source 20 over the pooled default jobs: two-sided exact "
            "binomial test of source 22's share at the exposure share, alpha " + str(ALPHA) + "; pooled over all "
            "three jobs when the mitigation contrast does not reject",
            "level": "presences at 1500 samples against those at 60000 over the same pooled jobs: two-sided exact "
            "binomial test of the 1500 share at the sample-law share, alpha " + str(ALPHA) + ", and the same test "
            "at the time-law share",
        },
        "readings": {
            "balancing": "the drift contrast does not reject and the mitigation contrast rejects with job-01's "
            "share below 1/3",
            "episodes": "the mitigation contrast does not reject and the source contrast rejects with source 22's "
            "share below the exposure share",
            "window_samples": "neither the mitigation nor the source contrast rejects, the sample-law share holds "
            "and the time-law share is rejected (or source-independent photon-triggered episodes)",
            "window_time": "neither the mitigation nor the source contrast rejects, the time-law share holds and "
            "the sample-law share is rejected",
            "no attribution": "any other pattern, a rejected drift contrast, a void job, or a level contrast whose "
            "two tests both hold or both reject",
        },
        "power": power_table(rows),
        "power_basis": "exact Poisson counts at " + format(PRESENCE_PER_SAMPLE, ".4e") + " primary presences per "
        "sample (49 in 452,000 samples of the 58 iterated cells of "
        "docs/evidence/quandela/belenos_offcone_packets.json, modes other than " + str(SECONDARY_MODE) + "); the "
        "source rows hold the pooled total at the retained rate (fixed_total) or scale source 22 down to 1 / ratio "
        "of the retained rate (source_22_scaled); retained packets of one cell co-occur across modes 0 and 5 (20 "
        "cells against 13.9 expected), so the table is an upper bound on every power entry",
    }


def documents() -> dict[str, bytes]:
    source = json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))
    circuit = (SOURCE / "circuit.json").read_bytes()
    require(hashlib.sha256(circuit).hexdigest() == CIRCUIT_SHA256, "belenos_mesh/job-16 circuit.json changed")
    require(source["circuit"]["sha256"] == CIRCUIT_SHA256, "belenos_mesh/job-16 cases.json names another circuit")
    rows = schedule()
    require(len(rows) == 2 * sum(REPEATS), "the schedule lost an entry")
    require(24 <= len(rows) <= 30, f"{len(rows)} entries leave the 24 to 30 entry range")
    for level in LEVELS:
        require(
            exposure(rows, level=level, source=SOURCES[0]) == exposure(rows, level=level, source=SOURCES[1]),
            "levels differ",
        )
    require(seconds(rows) <= DURATION_MARGIN * MAX_DURATION, f"{seconds(rows)} s leaves the duration margin")
    require(worst_seconds(rows) <= MAX_DURATION, f"{worst_seconds(rows)} s passes max_duration at the slow rate")
    prereg = preregistered(rows)
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
            "preregistered": prereg,
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
    print(
        f"{FAMILY}: {len(JOBS)} jobs of {len(rows)} entries, {seconds(rows)} s ({worst_seconds(rows)} s at "
        f"{WORST_ENTRY_SECONDS} s per entry), credit ceiling {credit_ceiling(rows)} per job"
    )
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
