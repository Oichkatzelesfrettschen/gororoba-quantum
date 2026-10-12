"""Exercise folded-audit qualification and caption binding without raw-data writes."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from render_folded_job_review import CONTRACT_CHECKS, ROOT, figure_captions, plot_limits, read_evidence, render

Mutation = Callable[[dict[str, Any]], None]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def assign(path: tuple[str | int, ...], value: Any) -> Mutation:
    def mutate(data: dict[str, Any]) -> None:
        parent: Any = data
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value

    return mutate


def remove(path: tuple[str | int, ...]) -> Mutation:
    def mutate(data: dict[str, Any]) -> None:
        parent: Any = data
        for key in path[:-1]:
            parent = parent[key]
        del parent[path[-1]]

    return mutate


def change_counts(data: dict[str, Any], rung: str, label: int, measured: list[int], replay: list[int]) -> None:
    """Build a consistent alternative measurement for caption and bounds checks."""
    member = next(row for row in data["members"] if (row["rung"], row["phase_label"]) == (rung, label))
    terminal_bit = 0 if rung == "delay" else 1
    successes = sum(count for index, count in enumerate(measured) if index >> terminal_bit == label >> 1)
    replay_successes = sum(count for index, count in enumerate(replay) if index >> terminal_bit == label >> 1)
    member.update(
        bit_counts_integer_order=measured,
        replay_reconstructed_counts_integer_order=replay,
        measured_probabilities_integer_order=[count / 8192 for count in measured],
        replay_probabilities_integer_order=[count / 8192 for count in replay],
        terminal_successes=successes,
        terminal_probability=successes / 8192,
        replay_terminal_probability=replay_successes / 8192,
        hardware_minus_replay=(successes - replay_successes) / 8192,
    )
    members = {row["member"]: row for row in data["members"]}
    for contrast in data["contrasts"]:
        stem, phase = contrast["name"].rsplit("_s", 1)
        arm, reference = stem.split("_minus_")
        difference = (
            members[f"{arm}_s{phase}"]["terminal_probability"]
            - members[f"qpe_{reference}_s{phase}"]["terminal_probability"]
        )
        half_width = contrast["half_width"]
        lower, upper = difference - half_width, difference + half_width
        contrast.update(
            difference=difference, simultaneous_interval=[lower, upper], excludes_zero=lower > 0 or upper < 0
        )


def main() -> int:
    source = ROOT / "results/ripple/folded-job-review.json"
    original = source.read_bytes()
    baseline: dict[str, Any] = json.loads(original)
    rejected = 0
    accepted = 0
    with TemporaryDirectory(prefix="folded-render-contract-") as temporary:
        directory = Path(temporary)
        candidate = directory / "audit.json"

        def write_candidate(data: dict[str, Any]) -> None:
            candidate.write_text(json.dumps(data), encoding="utf-8")

        def rejects(label: str, mutation: Mutation) -> None:
            nonlocal rejected
            data = copy.deepcopy(baseline)
            mutation(data)
            write_candidate(data)
            try:
                read_evidence(candidate)
            except ValueError:
                rejected += 1
            else:
                raise RuntimeError(f"unqualified audit accepted: {label}")

        for check in sorted(CONTRACT_CHECKS):
            rejects(f"missing check {check}", remove(("contract_checks", check)))
            rejects(f"false check {check}", assign(("contract_checks", check), False))
            rejects(f"numeric check {check}", assign(("contract_checks", check), 1))
        for flag in ("raw_unpaired_pub_identity_preserved", "precision_contract_reject_null_remains_null"):
            rejects(f"missing confidence {flag}", remove(("confidence", flag)))
            rejects(f"false confidence {flag}", assign(("confidence", flag), False))
        mutations: list[tuple[str, tuple[str | int, ...], Any]] = [
            ("empty checks", ("contract_checks",), {}),
            ("changed source", ("source_hashes_unchanged_during_audit",), False),
            ("recorded defect", ("defects",), ["mismatch"]),
            ("wrong raw register total", ("raw_register_count",), 15),
            ("wrong shot total", ("raw_pub_shots",), 16),
            ("wrong indexed coverage", ("hash_verified_indexed_files",), 19),
            ("cross-PUB pairing", ("shared_shot_pairing_scope",), "across PUBs"),
            ("invalid source hash", ("source_sha256", "record.json"), "invalid"),
            ("invalid audit hash", ("audit_script_sha256",), "invalid"),
            ("wrong schema", ("schema",), "unknown"),
            ("unsafe run identity", ("run",), "a/b"),
            ("wrong job count", ("jobs",), baseline["jobs"][:1]),
            ("duplicate job", ("jobs", 1), baseline["jobs"][0]),
            ("wrong PUB count", ("jobs", 0, "pubs"), 11),
            ("wrong job shots", ("jobs", 0, "shots_per_pub"), 4096),
            ("negative charge", ("jobs", 0, "charge_seconds"), -1),
            ("nonfinite charge", ("jobs", 0, "charge_seconds"), math.inf),
            ("boolean charge", ("jobs", 0, "charge_seconds"), True),
            ("charge total mismatch", ("timing_totals", "charged_seconds"), 41),
            ("unknown member job", ("members", 0, "job_id"), "unknown"),
            ("duplicate PUB", ("members", 1, "pub"), baseline["members"][0]["pub"]),
            ("PUB kind", ("members", 0, "pub"), "ibm_kingston_static_pub_01"),
            ("PUB index", ("members", 0, "pub"), "ibm_kingston_dynamic_pub_99"),
            ("different backend", ("members", 0, "pub"), "ibm_fez_dynamic_pub_01"),
            ("member name", ("members", 0, "member"), "qpe_archived_s1"),
            ("fractional label", ("members", 0, "phase_label"), 0.0),
            ("boolean label", ("members", 0, "phase_label"), False),
            ("member shots", ("members", 0, "shots"), 4096),
            ("count marginal", ("members", 0, "bit_counts_integer_order"), [8192, 0, 0, 0]),
            ("negative count", ("members", 0, "bit_counts_integer_order"), [-1, 8193, 0, 0]),
            ("fractional count", ("members", 0, "bit_counts_integer_order", 0), 6359.0),
            ("boolean count", ("members", 0, "bit_counts_integer_order", 0), True),
            ("count width", ("members", 0, "bit_counts_integer_order"), [8192]),
            ("count sum", ("members", 0, "bit_counts_integer_order", 0), 6358),
            ("terminal successes", ("members", 0, "terminal_successes"), 8192),
            ("measured vector", ("members", 0, "measured_probabilities_integer_order", 0), 1),
            ("terminal probability", ("members", 0, "terminal_probability"), 1),
            ("boolean probability", ("members", 0, "terminal_probability"), True),
            ("replay counts", ("members", 0, "replay_reconstructed_counts_integer_order"), [8192, 0, 0, 0]),
            ("replay vector", ("members", 0, "replay_probabilities_integer_order", 0), 1),
            ("replay marginal", ("members", 0, "replay_terminal_probability"), 1),
            ("ideal vector", ("members", 0, "exact_ideal_probabilities_integer_order"), [0, 1, 0, 0]),
            ("ideal marginal", ("members", 0, "ideal_terminal_probability"), 0.5),
            ("residual mismatch", ("members", 0, "hardware_minus_replay"), -0.1),
            ("duplicate writer", ("members", 0, "measurement_sites"), [[93, 0], [94, 0]]),
            ("incomplete writer", ("members", 0, "measurement_sites"), [[93, 0]]),
            ("negative writer", ("members", 0, "measurement_sites", 0, 0), -1),
            ("fractional gates", ("members", 0, "cz"), 72.5),
            ("naive timestamp", ("members", 0, "executor_chunk_start"), "2026-10-12T06:02:55"),
            ("reversed window", ("members", 0, "executor_chunk_stop"), baseline["members"][0]["executor_chunk_start"]),
            ("late calibration", ("members", 0, "calibration"), "2026-10-13T00:00:00Z"),
            ("mismatched calibration", ("members", 0, "calibration"), "2026-10-11T00:00:00Z"),
            ("confidence family", ("confidence", "family_alpha"), 0.01),
            ("confidence count", ("confidence", "comparisons"), 16),
            ("confidence per comparison", ("confidence", "per_contrast_alpha"), 0.05),
            ("confidence width", ("confidence", "half_width"), 0.05),
            ("contrast difference", ("contrasts", 0, "difference"), 0.01),
            ("contrast interval", ("contrasts", 0, "simultaneous_interval"), [0, 0]),
            ("contrast width", ("contrasts", 0, "half_width"), 0.05),
            ("contrast zero flag", ("contrasts", 0, "excludes_zero"), True),
            ("ideal contrast", ("contrasts", 0, "ideal_difference"), 1),
            ("retained decision", ("contrasts", 0, "retained_reject_null"), False),
        ]
        for label, path, value in mutations:
            rejects(label, assign(path, value))
        for path in (
            ("source_sha256", "record.json"),
            ("members", 0, "bit_counts_integer_order"),
            ("confidence",),
            ("jobs",),
        ):
            rejects(f"missing {path}", remove(path))

        def equal_residual(data: dict[str, Any]) -> None:
            counts = data["members"][0]["bit_counts_integer_order"]
            change_counts(data, "archived", 0, counts, counts)

        rejects("zero residual breaks highlighted pattern", equal_residual)

        def near_zero_residual(data: dict[str, Any]) -> None:
            equal_residual(data)
            data["members"][0]["hardware_minus_replay"] = -1e-15

        rejects("rounded sign at exact equality", near_zero_residual)

        write_candidate(baseline)
        evidence = read_evidence(candidate)
        captions = figure_captions(evidence)
        require("40 s CHARGED" in captions["acquisition"], "baseline acquisition changed")
        require("4 of 4 delay intervals include zero" in captions["dependence"], "baseline delay conclusion changed")
        require("coherent: 69 CZ, q94; archived: 72 CZ, q93" in captions["metadata"], "baseline writers changed")
        accepted += 1

        alternate = copy.deepcopy(baseline)
        alternate["jobs"][0]["charge_seconds"] = 30
        alternate["jobs"][1]["charge_seconds"] = 10
        for member in alternate["members"]:
            member["pub"] = member["pub"].replace("ibm_kingston", "ibm_fez")
            if member["rung"] == "coherent":
                member["cz"] = 50
                member["measurement_sites"] = [[94, 0], [81, 1]]
                member["executor_chunk_start"] = baseline["members"][0]["executor_chunk_start"]
                member["executor_chunk_stop"] = baseline["members"][0]["executor_chunk_stop"]
        change_counts(alternate, "delay", 0, [7700, 492], [8192, 0])
        write_candidate(alternate)
        evidence = read_evidence(candidate)
        captions = figure_captions(evidence)
        require("(30 s)" in captions["source"] and "(10 s)" in captions["source"], "job charges remain fixed")
        require("ibm_fez" in captions["subtitle"], "backend remains fixed")
        require("coherent: 50 CZ, q81" in captions["metadata"], "gate and writer caption remains fixed")
        require("overlapping" in captions["metadata"], "execution window caption remains fixed")
        require("3 of 4 delay intervals include zero" in captions["dependence"], "delay conclusion remains fixed")
        output = directory / "alternate.svg"
        render(evidence, output, None)
        svg = output.read_text(encoding="utf-8")
        require(all(caption in svg for caption in captions.values()), "render omits derived caption text")
        accepted += 1

        alternate["jobs"][0]["charge_seconds"] = 31
        alternate["timing_totals"]["charged_seconds"] = 41
        change_counts(alternate, "archived", 0, [1, 0, 8191, 0], [8192, 0, 0, 0])
        write_candidate(alternate)
        evidence = read_evidence(candidate)
        require("41 s CHARGED" in figure_captions(evidence)["acquisition"], "total charge remains fixed")
        probability_limits, contrast_limits, residual_limits = plot_limits(evidence)
        for outcome in evidence.outcomes:
            require(
                all(
                    probability_limits[0] < 100 * value < probability_limits[1]
                    for value in (outcome.measured, outcome.ideal, outcome.replay)
                ),
                "probability outside plot",
            )
            require(residual_limits[0] < 100 * outcome.residual < residual_limits[1], "residual outside plot")
        for contrast in evidence.contrasts:
            require(
                contrast_limits[0] < 100 * contrast.lower < 100 * contrast.upper < contrast_limits[1],
                "interval outside plot",
            )
        accepted += 1

        malformed = copy.deepcopy(baseline)
        malformed["contract_checks"] = {}
        write_candidate(malformed)
        cli_svg, cli_png = directory / "rejected.svg", directory / "rejected.png"
        process = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/render_folded_job_review.py"),
                "--evidence",
                str(candidate),
                "--out",
                str(cli_svg),
                "--png",
                str(cli_png),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        require(
            process.returncode != 0 and "audit contract checks are incomplete" in process.stderr,
            "CLI accepted bad evidence",
        )
        require(not cli_svg.exists() and not cli_png.exists(), "CLI wrote output before qualification")
        require(source.read_bytes() == original, "retained audit changed")
    print(
        json.dumps(
            {
                "rejected_mutations": rejected,
                "qualified_inputs": accepted,
                "retained_audit_sha256": hashlib.sha256(original).hexdigest(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
