"""Belenos job-16 byte replay: one iterated qpu:belenos job that separates a chip change after the 2026-11-27 outage
from a property of the off-cone mechanisms case.

belenos_offcone_mechanisms job-00 to job-02 (2026-11-28) read mesh 29dc6ef8 with routing far outside the envelope of
belenos_mesh/job-16 (2026-10-18), whose circuit and compilation seed 20 they reuse
(docs/design/belenos-offcone-mechanisms-case.md, Findings). The two differ by the outage and by the case's own
choices (a per-iteration input_mode, 715,000 samples per job, sources 20 and 22). This job removes the case's
choices: it replays job-16's circuit.json byte for byte, with its single source mode 20, no per-iteration input_mode
and the default mitigations, at 10000 samples per entry and the two compilation seeds of job-16 (20, the identifier
of mesh 29dc6ef8, and 46667, the identifier of mesh 14a96ca6), alternating.

Usage: "$PYTHON" scripts/belenos_job16_replay.py (--build | --check)
  --build  write results/quandela/cases/belenos_job16_replay/job-00
  --check  rebuild and compare byte for byte
  --offline-plan  print qd_platform.plan of the case against the retained catalogue, with no provider read
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import belenos_offcone_mechanisms as offcone  # noqa: E402
import qd_belenos_mesh as mesh  # noqa: E402

FAMILY = "belenos_job16_replay"
JOB = "job-00"
DESIGN = "docs/design/belenos-job16-replay-case.md"
SOURCE = offcone.SOURCE
PLATFORM = offcone.PLATFORM
CIRCUIT_SHA256 = offcone.CIRCUIT_SHA256
# Both seeds reproduce retained compiled meshes of belenos_mesh/job-16, so they are identifiers that keep their
# values (AGENTS.md, "Seeds"); the job takes them by name from the builder that wrote job-16, and draws no new seed.
SEED_Q1 = mesh.DWELL_Q1_SEED
SEED_REFERENCE = mesh.anu_seed(mesh.DWELL_ANU)
SEEDS = (SEED_Q1, SEED_REFERENCE["value"])
ENTRIES = 10
SAMPLES = 10000
# The builder rules of belenos_offcone_mechanisms: the shot cap is SHOT_HEADROOM x samples, the plan prices the job
# at the rate of the runbook, and the worst entry rate must stay inside max_duration.
MAX_SHOTS_PER_ENTRY = offcone.SHOT_HEADROOM * SAMPLES
# Entries 2, 4, 6 and 8 are seed-20 entries that follow a seed-46667 load, the position of every healthy 29dc6ef8
# entry of job-16 after its first two entries (11 of 11 at in_block_cone 0.982 or more).
POST_LOAD_ENTRIES = (2, 4, 6, 8)
# belenos_mesh/job-16, 29dc6ef8 entries (13): in_block_cone 0.4504 to 0.9941, tvd_cone_from_ideal 0.0775 to 0.8190
# (belenos_offcone_mechanisms_analyze.baseline); the new runs' medians (0.158 to 0.170, 0.868 to 0.889) lie outside.
ENVELOPE = {"in_block_cone_min": 0.450353, "tvd_cone_from_ideal_max": 0.819035, "healthy_in_block_cone": 0.98}


def rows() -> list[dict[str, Any]]:
    return [{"name": f"e{k}-s{SEEDS[k % 2]}-n{SAMPLES}", "compilation_seed": SEEDS[k % 2]} for k in range(ENTRIES)]


def seconds() -> float:
    return round(offcone.JOB_SECONDS + offcone.ENTRY_SECONDS * ENTRIES, 2)


def worst_seconds() -> float:
    return round(offcone.JOB_SECONDS + offcone.WORST_ENTRY_SECONDS * ENTRIES, 2)


def credit_ceiling() -> float:
    return round(offcone.PER_JOB_CREDITS + offcone.CREDITS_PER_SHOT * MAX_SHOTS_PER_ENTRY, 6)


def preregistered() -> dict[str, Any]:
    return {
        "series": "job-16 byte replay after the 2026-11-27 outage (pool row QPU-43)",
        "mesh_variance": {"kind": "anchors", "anchors": 2, "repeats_per_anchor": ENTRIES // 2},
        "question": "do the seed-20 entries of belenos_mesh/job-16's circuit route as they did before the outage "
        "(a property of the off-cone mechanisms case moved them) or as the 2026-11-28 runs did (the chip or the "
        "server moved them)",
        "entries": "ten entries alternating compilation seeds 20 and 46667 from seed 20; every entry is one "
        "single-source computation of belenos_mesh/job-16's circuit.json with no input_mode override and the "
        "server's default mitigations",
        "void": "a seed-20 entry is void when its served mesh sha256 does not start with " + offcone.MESH_PREFIX + "; "
        "a seed-46667 entry is void when it does not start with 14a96ca6; the first entry (index 0) is read and "
        "reported, and decides nothing, since the first two entries of job-16 failed at in_block_cone 0.45",
        "observables": "per seed-20 entry on indices " + ", ".join(str(i) for i in POST_LOAD_ENTRIES) + ": "
        "in_block_cone and tvd_cone_from_ideal (scripts/qd_belenos_cone.py run_cells); per entry: the modes 0, 1 "
        "and 5 with at least 32 one-click samples off the cone, and the mode-6 clicks",
        "envelope": ENVELOPE,
        "readings": {
            "chip_or_server_changed": "at most 1 of the 4 post-load seed-20 entries inside the job-16 envelope "
            "(in_block_cone at or above " + str(ENVELOPE["in_block_cone_min"]) + " and tvd_cone_from_ideal at or "
            "below " + str(ENVELOPE["tvd_cone_from_ideal_max"]) + "); no entry of the ten with a mode among 0, 1 and "
            "5 at 32 or more clicks (0 of 90 in belenos_offcone_mechanisms); mode 6 reading about 7 clicks per "
            "seed-20 entry (mean 7.07 over the 15 source-20 10000-sample entries there, range 0 to 13)",
            "case_property": "at least 3 of the 4 post-load seed-20 entries at in_block_cone "
            + str(ENVELOPE["healthy_in_block_cone"])
            + " or more (11 of 11 post-load entries in job-16); at least 8 of the 10 entries with a mode among 0, 1 "
            "and 5 at 32 or more clicks (23 of 24 in job-16); mode 6 at 0 clicks on every seed-20 entry (13 of 13 in "
            "job-16)",
            "neither": "any other pattern, or a void post-load entry: the routing of 29dc6ef8 is intermittent "
            "and the replay attributes nothing",
        },
        "falsifiers": {
            "chip_or_server_changed": "3 or more post-load seed-20 entries at in_block_cone 0.98 or more",
            "case_property": "at most 1 post-load seed-20 entry at in_block_cone 0.98 or more, or every entry "
            "free of a mode among 0, 1 and 5 at 32 or more clicks",
        },
    }


def documents() -> dict[str, bytes]:
    source = json.loads((SOURCE / "cases.json").read_text(encoding="utf-8"))
    circuit = (SOURCE / "circuit.json").read_bytes()
    offcone.require(hashlib.sha256(circuit).hexdigest() == CIRCUIT_SHA256, "belenos_mesh/job-16 circuit.json changed")
    offcone.require(
        source["circuit"]["sha256"] == CIRCUIT_SHA256, "belenos_mesh/job-16 cases.json names another circuit"
    )
    offcone.require(
        seconds() <= offcone.DURATION_MARGIN * offcone.MAX_DURATION, f"{seconds()} s leaves the duration margin"
    )
    offcone.require(worst_seconds() <= offcone.MAX_DURATION, f"{worst_seconds()} s passes max_duration")
    manifest: dict[str, Any] = {
        "schema": source["schema"],
        "family": FAMILY,
        "job": JOB,
        "platforms": [PLATFORM],
        "command": source["command"],
        "gate_form": source["gate_form"],
        "min_detected_photons": source["min_detected_photons"],
        "iterations": ENTRIES,
        "max_samples": SAMPLES * ENTRIES,
        "max_shots": MAX_SHOTS_PER_ENTRY * ENTRIES,
        "max_duration": offcone.MAX_DURATION,
        "max_credits": credit_ceiling(),
        "expected_seconds": seconds(),
        "census": source["census"],
        "circuit": source["circuit"],
        "blocks": source["blocks"],
        "settings": rows(),
        "design": DESIGN,
        "seed_source": SEED_REFERENCE,
        "seeded_from": {
            "case": "belenos_mesh/job-16",
            "cases_sha256": hashlib.sha256((SOURCE / "cases.json").read_bytes()).hexdigest(),
            "use": "circuit.json byte for byte and the compilation seeds 20 (mesh " + offcone.MESH_PREFIX + ") and "
            "46667 (mesh 14a96ca6) of its entries",
        },
        "preregistered": preregistered(),
    }
    return {f"{JOB}/cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), f"{JOB}/circuit.json": circuit}


def offline_plan() -> dict[str, Any]:
    """qd_platform.plan of the case with every provider read replaced by the retained catalogue record (explorer row,
    processor record, availability) and a stand-in token: the plan's arithmetic, payload and digest, without a
    provider read. The live plan (qd_platform.py plan with the job token) is the check before approval."""
    from unittest import mock

    import qd_platform
    from perceval.providers.quandela.rpc_handler import RPCHandler

    catalogue = json.loads((ROOT / "docs/evidence/quandela/catalogue.json").read_text(encoding="utf-8"))
    # The retained records read "calibration"; the plan admits "available" only, so the rehearsal reads both as
    # available and records that it did.
    processor = {**catalogue["processors"][PLATFORM], "status": "available"}
    row = {**next(r for r in catalogue["explorer_platforms"] if r["name"] == PLATFORM), "status": "available"}
    with (
        mock.patch.object(qd_platform, "explorer_row", lambda platform: row),
        mock.patch.object(qd_platform, "get", lambda route, auth=True: processor),
        mock.patch.object(qd_platform, "availability", lambda: catalogue["account"]["availability"]),
        mock.patch.object(qd_platform, "token", lambda: "offline-stand-in-token"),
        mock.patch.object(RPCHandler, "fetch_platform_details", lambda self: processor),
    ):
        planned = qd_platform.plan(
            offcone.CASES / FAMILY / JOB, PLATFORM, credit_ceiling(), seconds(), offcone.PER_JOB_CREDITS
        )
    planned["offline_basis"] = (
        "retained catalogue " + str(catalogue.get("retrieved_utc")) + " with the explorer and processor status set to "
        "available (the retained records read calibration)"
    )
    return planned


def build(check_only: bool) -> int:
    for name, data in documents().items():
        path = offcone.CASES / FAMILY / name
        if check_only:
            offcone.require(
                path.exists() and path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild"
            )
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(
        f"{FAMILY}: {ENTRIES} entries, {seconds()} s ({worst_seconds()} s at {offcone.WORST_ENTRY_SECONDS} s per "
        f"entry), credit ceiling {credit_ceiling()}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--offline-plan", action="store_true")
    args = parser.parse_args()
    if args.offline_plan:
        planned = offline_plan()
        print(json.dumps(planned, indent=1, sort_keys=True))
        return 0
    return build(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
