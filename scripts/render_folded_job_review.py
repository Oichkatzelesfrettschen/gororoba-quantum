"""Render measured folded-QPE outcomes, bounded contrasts, and replay residuals.

The retained independent audit supplies every plotted value. Contrast intervals
cover the declared twelve-comparison family; replay residuals stay descriptive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

ROOT = Path(__file__).resolve().parents[1]
RUNG_NAMES = ("archived", "delay", "no_feed_forward", "coherent")
DISPLAY_NAMES = ("Archived", "Delay", "No feedback", "Coherent")
COLORS = ("#276B9C", "#C36332", "#8656A1", "#277F68")
INK = "#23323B"
MUTED = "#596A75"
PAPER = "#F6F7F3"
CONTRACT_CHECKS = frozenset(
    (
        "all12_contrasts_match",
        "all16_terminal_estimates_match",
        "all16_measurement_site_maps_match_qpy",
        "all16_replay_quantized_count_estimates_match",
        "all_declared_shot_counts_match",
        "approval_mismatches_empty",
    )
)


@dataclass(frozen=True)
class Outcome:
    rung: str
    label: int
    measured: float
    ideal: float
    replay: float
    residual: float
    job_id: str
    cz: int
    terminal_qubit: int
    start: datetime
    stop: datetime


@dataclass(frozen=True)
class Contrast:
    rung: str
    label: int
    difference: float
    lower: float
    upper: float


@dataclass(frozen=True)
class Job:
    job_id: str
    pubs: int
    charged_seconds: float


@dataclass(frozen=True)
class Evidence:
    digest: str
    run: str
    outcomes: tuple[Outcome, ...]
    contrasts: tuple[Contrast, ...]
    shots: int
    charged_seconds: float
    half_width: float
    backend: str
    jobs: tuple[Job, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    _require(type(value) is int and value >= minimum, f"invalid {label}")
    return int(value)


def _real(value: Any, label: str) -> float:
    _require(type(value) in (int, float), f"invalid {label}")
    number = float(value)
    _require(math.isfinite(number), f"nonfinite {label}")
    return number


def _identity(value: Any, label: str) -> str:
    _require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:+-]+", value) is not None, f"invalid {label}")
    return str(value)


def _timestamp(value: Any) -> datetime:
    _require(isinstance(value, str), "execution timestamp must be a string")
    timestamp = datetime.fromisoformat(value)
    _require(timestamp.utcoffset() is not None, "execution timestamp must include a timezone")
    return timestamp


def _counts(value: Any, width: int, shots: int, label: str) -> list[int]:
    _require(isinstance(value, list) and len(value) == width, f"{label} outcome count differs")
    counts = [_integer(count, label) for count in value]
    _require(sum(counts) == shots, f"{label} differs from shots")
    return counts


def _probabilities(value: Any, expected: list[float], label: str) -> None:
    _require(isinstance(value, list) and len(value) == len(expected), f"{label} outcome count differs")
    _require([_real(item, label) for item in value] == expected, f"{label} differs from its labeled counts or law")


def read_evidence(path: Path) -> Evidence:
    """Validate the fixed 16-PUB, 12-contrast, 8192-shot audited ladder.

    The renderer checks internal evidence consistency. Replaying the independent
    audit against its retained raw archive establishes the separate source link.
    """
    contents = path.read_bytes()
    try:
        return _read_evidence(contents)
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as error:
        raise ValueError(f"incomplete or malformed folded audit: {error}") from error


def _read_evidence(contents: bytes) -> Evidence:
    data = json.loads(contents)
    _require(isinstance(data, dict), "folded audit must be an object")
    _require(data["schema"] == "independent-folded-raw-audit-v1", "unsupported folded audit schema")
    checks = data["contract_checks"]
    _require(isinstance(checks, dict) and set(checks) == CONTRACT_CHECKS, "audit contract checks are incomplete")
    _require(all(checks[name] is True for name in CONTRACT_CHECKS), "audit contract failure")
    _require(data["source_hashes_unchanged_during_audit"] is True, "source hashes changed during audit")
    _require(data["defects"] == [], "audit records defects")
    _require(
        _integer(data["raw_register_count"], "raw register count") == 16
        and _integer(data["raw_pub_shots"], "raw shot count") == 16 * 8192,
        "raw acquisition totals differ",
    )
    _require(
        _integer(data["hash_verified_indexed_files"], "indexed file count") == 20, "indexed raw audit coverage differs"
    )
    _require(data["shared_shot_pairing_scope"] == "within one PUB only", "cross-PUB pairing is unsupported")
    source_hashes = data["source_sha256"]
    _require(isinstance(source_hashes, dict), "source hashes are missing")
    for digest in [data["audit_script_sha256"], *source_hashes.values()]:
        _require(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest) is not None, "invalid source digest")
    _require(
        {"record.json", "collect.json", "isa.qpy", "settled-account-usage.json"} <= set(source_hashes),
        "required audit source identities are missing",
    )
    _require(isinstance(data["jobs"], list) and len(data["jobs"]) == 2, "expected two audited jobs")
    jobs = []
    for job in data["jobs"]:
        job_id = _identity(job["job_id"], "job identity")
        pubs = _integer(job["pubs"], "job PUB count", minimum=1)
        _require(pubs in (4, 12), "job PUB count differs from ladder")
        _require(_integer(job["shots_per_pub"], "job shots", minimum=1) == 8192, "job shot count differs")
        charge = _real(job["charge_seconds"], "job charge")
        _require(charge > 0, "job charge must be positive")
        required_files = {f"raw/{job_id}/{name}" for name in ("index.json", "job_metrics.json", "result_metadata.json")}
        required_files.update(f"raw/{job_id}/pub_{index:02d}.json" for index in range(pubs))
        _require(required_files <= set(source_hashes), "job raw source identities are missing")
        jobs.append(Job(job_id, pubs, charge))
    _require(
        len({job.job_id for job in jobs}) == 2 and sorted(job.pubs for job in jobs) == [4, 12], "job identities differ"
    )
    _require(
        len(data["members"]) == 16 and len(data["contrasts"]) == 12, "expected sixteen outcomes and twelve contrasts"
    )
    members = {(member["rung"], member["phase_label"]): member for member in data["members"]}
    _require(set(members) == {(rung, label) for rung in RUNG_NAMES for label in range(4)}, "member identities differ")
    outcomes = []
    identities: dict[str, list[tuple[str, int]]] = {job.job_id: [] for job in jobs}
    backends = set()
    calibrations = set()
    pub_names = set()
    for rung in RUNG_NAMES:
        for label in range(4):
            member = members[(rung, label)]
            _require(member["member"] == f"qpe_{rung}_s{label}", "member name differs from rung and label")
            _require(type(member["phase_label"]) is int, "phase label must be an integer")
            _require(
                _integer(member["shots"], "member shots", minimum=1) == 8192, "expected 8192 measured shots per PUB"
            )
            job_id = _identity(member["job_id"], "member job")
            _require(job_id in identities, "member job is absent from the job ledger")
            pub = member["pub"]
            match = re.fullmatch(r"(ibm_[a-z0-9]+)_(dynamic|static)_pub_([0-9]+)", pub)
            _require(match is not None and pub not in pub_names, "invalid or duplicate PUB identity")
            if match is None:
                raise ValueError("PUB identity cannot be decoded")
            backend, kind, pub_index = match.groups()
            _require(kind == ("static" if rung == "coherent" else "dynamic"), "PUB execution kind differs from rung")
            backends.add(backend)
            pub_names.add(pub)
            identities[job_id].append((kind, int(pub_index)))
            width = 2 if rung == "delay" else 4
            terminal_bit = 0 if rung == "delay" else 1
            counts = _counts(member["bit_counts_integer_order"], width, 8192, "raw counts")
            replay_counts = _counts(member["replay_reconstructed_counts_integer_order"], width, 8192, "replay counts")
            successes = sum(count for outcome, count in enumerate(counts) if outcome >> terminal_bit == label >> 1)
            replay_successes = sum(
                count for outcome, count in enumerate(replay_counts) if outcome >> terminal_bit == label >> 1
            )
            _require(
                _integer(member["terminal_successes"], "terminal successes") == successes,
                "raw terminal marginal differs",
            )
            _probabilities(
                member["measured_probabilities_integer_order"], [count / 8192 for count in counts], "measured vector"
            )
            _probabilities(
                member["replay_probabilities_integer_order"], [count / 8192 for count in replay_counts], "replay vector"
            )
            expected_ideal = [0.0] * width
            if rung == "delay":
                expected_ideal[label >> 1] = 1.0
            elif rung == "no_feed_forward" and label % 2:
                expected_ideal[label] = expected_ideal[label ^ 2] = 0.5
            else:
                expected_ideal[label] = 1.0
            _probabilities(member["exact_ideal_probabilities_integer_order"], expected_ideal, "ideal vector")
            measured = _real(member["terminal_probability"], "measured terminal probability")
            ideal = _real(member["ideal_terminal_probability"], "ideal terminal probability")
            replay = _real(member["replay_terminal_probability"], "replay terminal probability")
            residual = _real(member["hardware_minus_replay"], "replay residual")
            _require(
                all(math.isfinite(value) and 0 <= value <= 1 for value in (measured, ideal, replay)),
                "invalid probability",
            )
            _require(
                measured == successes / 8192 and replay == replay_successes / 8192,
                "terminal probability differs from labeled counts",
            )
            _require(
                ideal
                == sum(value for outcome, value in enumerate(expected_ideal) if outcome >> terminal_bit == label >> 1),
                "ideal terminal marginal differs",
            )
            _require(residual == measured - replay, "residual differs from marginals")
            sites = member["measurement_sites"]
            _require(isinstance(sites, list) and len(sites) == terminal_bit + 1, "measurement writer count differs")
            writers = {}
            for site in sites:
                _require(isinstance(site, list) and len(site) == 2, "invalid measurement writer")
                qubit = _integer(site[0], "physical measurement qubit")
                bit = _integer(site[1], "classical measurement bit")
                _require(bit not in writers, "repeated classical writer")
                writers[bit] = qubit
            _require(set(writers) == set(range(terminal_bit + 1)), "measurement bits differ")
            start, stop = _timestamp(member["executor_chunk_start"]), _timestamp(member["executor_chunk_stop"])
            calibration = _timestamp(member["calibration"])
            _require(calibration <= start < stop, "invalid execution window or calibration")
            calibrations.add(calibration)
            outcomes.append(
                Outcome(
                    rung,
                    label,
                    measured,
                    ideal,
                    replay,
                    residual,
                    job_id,
                    _integer(member["cz"], "CZ count"),
                    writers[terminal_bit],
                    start,
                    stop,
                )
            )
    _require(len(backends) == 1 and len(calibrations) == 1, "contrast ladder needs one backend and shared calibration")
    for job in jobs:
        entries = identities[job.job_id]
        _require(
            len(entries) == job.pubs and len({kind for kind, _index in entries}) == 1,
            "job membership differs from its PUB ledger",
        )
        _require(sorted(index for _kind, index in entries) == list(range(1, job.pubs + 1)), "job PUB indices differ")
    positive_residuals = {(outcome.rung, outcome.label) for outcome in outcomes if outcome.residual > 0}
    _require(
        positive_residuals == {("no_feed_forward", 1), ("no_feed_forward", 3)},
        "highlighted residual-sign pattern differs",
    )
    _require(
        all(outcome.residual < 0 for outcome in outcomes if (outcome.rung, outcome.label) not in positive_residuals),
        "the other fourteen residuals must be strictly negative",
    )
    confidence = data["confidence"]
    _require(
        _integer(confidence["comparisons"], "confidence comparisons") == 12
        and _real(confidence["family_alpha"], "family alpha") == 0.05,
        "confidence family differs",
    )
    half_width = 2 * math.sqrt(math.log(4 / (0.05 / 12)) / (2 * 8192))
    _require(
        math.isclose(_real(confidence["half_width"], "confidence half-width"), half_width, rel_tol=0, abs_tol=1e-14),
        "confidence formula differs",
    )
    _require(_real(confidence["per_contrast_alpha"], "per-contrast alpha") == 0.05 / 12, "per-contrast alpha differs")
    _require(
        confidence["raw_unpaired_pub_identity_preserved"] is True
        and confidence["precision_contract_reject_null_remains_null"] is True,
        "confidence qualification failed",
    )
    source_contrasts = {contrast["name"]: contrast for contrast in data["contrasts"]}
    _require(len(source_contrasts) == 12, "contrast identities repeat")
    contrasts = []
    for rung in RUNG_NAMES[1:]:
        for label in range(4):
            contrast = source_contrasts[f"qpe_{rung}_minus_archived_s{label}"]
            difference = _real(contrast["difference"], "contrast difference")
            interval = contrast["simultaneous_interval"]
            _require(isinstance(interval, list) and len(interval) == 2, "invalid contrast interval")
            lower, upper = (_real(endpoint, "contrast endpoint") for endpoint in interval)
            expected = (
                members[(rung, label)]["terminal_probability"] - members[("archived", label)]["terminal_probability"]
            )
            _require(difference == expected, "contrast differs from measured marginals")
            _require(
                math.isclose(lower, difference - half_width, rel_tol=0, abs_tol=1e-14),
                "lower confidence endpoint differs",
            )
            _require(
                math.isclose(upper, difference + half_width, rel_tol=0, abs_tol=1e-14),
                "upper confidence endpoint differs",
            )
            _require(contrast["retained_reject_null"] is None, "precision contract changed to a hypothesis decision")
            _require(
                math.isclose(
                    _real(contrast["half_width"], "contrast half-width"), half_width, rel_tol=0, abs_tol=1e-14
                ),
                "contrast half-width differs",
            )
            _require(contrast["excludes_zero"] is (lower > 0 or upper < 0), "contrast zero-inclusion flag differs")
            _require(
                _real(contrast["ideal_difference"], "ideal contrast")
                == members[(rung, label)]["ideal_terminal_probability"]
                - members[("archived", label)]["ideal_terminal_probability"],
                "ideal contrast differs from member laws",
            )
            contrasts.append(Contrast(rung, label, difference, lower, upper))
    charged = _real(data["timing_totals"]["charged_seconds"], "charged total")
    _require(math.fsum(job.charged_seconds for job in jobs) == charged, "charged totals differ")
    return Evidence(
        hashlib.sha256(contents).hexdigest(),
        _identity(data["run"], "run identity"),
        tuple(outcomes),
        tuple(contrasts),
        8192,
        charged,
        half_width,
        next(iter(backends)),
        tuple(jobs),
    )


def figure_captions(evidence: Evidence) -> dict[str, str]:
    """Bind factual captions to the qualified audit rather than one retained run."""
    delay_contrasts = [contrast for contrast in evidence.contrasts if contrast.rung == "delay"]
    including_zero = sum(contrast.lower <= 0 <= contrast.upper for contrast in delay_contrasts)
    delay_statement = (
        f"{including_zero} of {len(delay_contrasts)} delay intervals include zero; equivalence is untested."
    )
    summaries = []
    for rung in ("coherent", "archived"):
        outcomes = [outcome for outcome in evidence.outcomes if outcome.rung == rung]
        cz_counts = "/".join(str(count) for count in sorted({outcome.cz for outcome in outcomes}))
        terminal_writers = "/".join(f"q{qubit}" for qubit in sorted({outcome.terminal_qubit for outcome in outcomes}))
        summaries.append(f"{rung}: {cz_counts} CZ, {terminal_writers}")
    windows = []
    for job in evidence.jobs:
        job_outcomes = [outcome for outcome in evidence.outcomes if outcome.job_id == job.job_id]
        windows.append((min(outcome.start for outcome in job_outcomes), max(outcome.stop for outcome in job_outcomes)))
    separated = windows[0][1] <= windows[1][0] or windows[1][1] <= windows[0][0]
    window_statement = "separate" if separated else "overlapping"
    outcome_map = {(outcome.rung, outcome.label): outcome for outcome in evidence.outcomes}
    odd_ideal_differences = {
        100 * (outcome_map[("no_feed_forward", label)].ideal - outcome_map[("archived", label)].ideal)
        for label in (1, 3)
    }
    odd_ideal = "/".join(f"{difference:+g}" for difference in sorted(odd_ideal_differences))
    return {
        "subtitle": f"Folded phase estimation on {evidence.backend}",
        "acquisition": f"MEASURED QPU DATA  /  {len(evidence.outcomes)} PUBs × {evidence.shots:,} SHOTS  /  "
        f"{evidence.charged_seconds:g} s CHARGED",
        "inference": "Inference: Hoeffding + union bound; 12-family α = 0.05; "
        f"half-width {100 * evidence.half_width:.4f} pp. "
        "Independent stationary repetitions within each PUB are required.",
        "dependence": "Within-shot and cross-PUB dependence are unrestricted by the bound. PUBs remain unpaired. "
        + delay_statement,
        "metadata": f"Audit metadata ({'; '.join(summaries)}); job-window hulls are {window_statement}. "
        f"Odd no-feedback ideal contrast: {odd_ideal} pp.",
        "source": "Jobs: "
        + " · ".join(f"{job.job_id} ({job.charged_seconds:g} s)" for job in evidence.jobs)
        + "   |   Source: audit-qualified raw counts, QPY mappings, and recorded model replay.",
    }


def plot_limits(evidence: Evidence) -> tuple[tuple[float, float], ...]:
    """Keep every probability, contrast endpoint, and residual inside its panel."""
    probability_values = [
        100 * value for outcome in evidence.outcomes for value in (outcome.measured, outcome.ideal, outcome.replay)
    ]
    contrast_values = [
        100 * endpoint for contrast in evidence.contrasts for endpoint in (contrast.lower, contrast.upper)
    ]
    residual_values = [0.0, *(100 * outcome.residual for outcome in evidence.outcomes)]
    residual_padding = max(6.0, (max(residual_values) - min(residual_values)) * 0.17)
    return (
        (min(43.0, min(probability_values) - 4), max(104.0, max(probability_values) + 4)),
        (min(-23.0, min(contrast_values) - 3), max(18.0, max(contrast_values) + 3)),
        (min(-24.0, min(residual_values) - residual_padding), max(20.0, max(residual_values) + residual_padding)),
    )


def _row(rung: str, label: int) -> float:
    return float(RUNG_NAMES.index(rung) * 5 + label)


def _style_axis(axis: Axes, title: str, subtitle: str) -> None:
    axis.set_ylim(19.0, -1.0)
    axis.set_title(title, loc="left", color=INK, fontsize=12.5, fontweight="bold", pad=40)
    axis.text(0, 1.028, subtitle, transform=axis.transAxes, fontsize=9.4, color=MUTED)
    axis.set_yticks([])
    axis.grid(axis="x", color="#E0E6E6", linewidth=0.7, zorder=0)
    axis.tick_params(axis="both", labelsize=10, colors=MUTED, length=0, pad=6)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#BAC6CD")
    for divider in (4, 9, 14):
        axis.axhline(divider, color="#E5E9E7", linewidth=0.8)
    for label in (1, 3):
        position = _row("no_feed_forward", label)
        axis.axhspan(position - 0.44, position + 0.44, color="#F1EAF5", zorder=0)


def validate_output_paths(output: Path, png: Path | None, *, evidence_path: Path | None = None) -> None:
    """Protect the audit and distinguish image destinations before any writes."""
    paths = [("--out", output)]
    if png is not None:
        paths.append(("--png", png))
    if evidence_path is not None:
        paths.append(("--evidence", evidence_path))
    for index, (name, path) in enumerate(paths):
        for other_name, other_path in paths[:index]:
            aliases = path.resolve() == other_path.resolve() or (
                path.exists() and other_path.exists() and path.samefile(other_path)
            )
            _require(not aliases, f"{name} and {other_name} paths must identify distinct files")


def render(evidence: Evidence, output: Path, png: Path | None) -> None:
    validate_output_paths(output, png)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "svg.hashsalt": "folded-job-review-v1",
            "axes.facecolor": "white",
            "figure.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )
    captions = figure_captions(evidence)
    limits = plot_limits(evidence)
    figure = plt.figure(figsize=(17.0, 12.0))
    figure.text(0.055, 0.954, "WHERE HARDWARE DEPARTS FROM THE MODEL", fontsize=23, color=INK, weight="bold")
    figure.text(0.055, 0.918, captions["subtitle"], fontsize=16, color=INK)
    figure.text(0.055, 0.886, captions["acquisition"], fontsize=10.5, color=MUTED)
    grid = figure.add_gridspec(
        1, 3, left=0.155, right=0.967, bottom=0.290, top=0.766, width_ratios=(1.14, 1, 1), wspace=0.24
    )
    probabilities, contrasts, residuals = [figure.add_subplot(grid[0, index]) for index in range(3)]
    _style_axis(probabilities, "01  TERMINAL-BIT SUCCESS", "Each row is one measured circuit and phase label.")
    _style_axis(contrasts, "02  CHANGE FROM ARCHIVED", "95% simultaneous intervals across 12 contrasts.")
    _style_axis(residuals, "03  HARDWARE − FINITE REPLAY", "Descriptive discrepancies; contrast CIs do not apply.")
    probabilities.set_xlim(*limits[0])
    probabilities.set_xlabel("Success probability (%)", color=MUTED, fontsize=10.5, labelpad=12)
    contrasts.set_xlim(*limits[1])
    contrasts.set_xlabel("Difference (percentage points)", color=MUTED, fontsize=10.5, labelpad=12)
    residuals.set_xlim(*limits[2])
    residuals.set_xlabel("Residual (percentage points)", color=MUTED, fontsize=10.5, labelpad=12)
    contrasts.axvline(0, color="#8798A2", linewidth=1.1)
    residuals.axvline(0, color="#8798A2", linewidth=1.1)
    for outcome in evidence.outcomes:
        position = _row(outcome.rung, outcome.label)
        rung_index = RUNG_NAMES.index(outcome.rung)
        color = COLORS[rung_index]
        probabilities.text(
            -0.025,
            position,
            f"{DISPLAY_NAMES[rung_index]}   s{outcome.label}",
            transform=probabilities.get_yaxis_transform(),
            ha="right",
            va="center",
            fontsize=10.5,
            color=color,
        )
        probabilities.plot(
            outcome.ideal * 100,
            position,
            marker="|",
            markersize=11,
            markeredgewidth=1.5,
            color="#93A0A7",
            linestyle="none",
            zorder=2,
        )
        probabilities.plot(
            outcome.replay * 100,
            position,
            marker="D",
            markersize=5.0,
            markeredgewidth=1.2,
            markerfacecolor="white",
            color=MUTED,
            linestyle="none",
            zorder=3,
        )
        probabilities.plot(
            outcome.measured * 100, position, marker="o", markersize=6.2, color=color, linestyle="none", zorder=4
        )
        residual = outcome.residual * 100
        residual_color = COLORS[2] if residual > 0 else "#648493"
        residuals.barh(position, residual, height=0.29, color=residual_color, zorder=3)
        residuals.text(
            residual + (0.65 if residual > 0 else -0.65),
            position,
            f"{residual:+.2f}",
            ha="left" if residual > 0 else "right",
            va="center",
            fontsize=9.5,
            color=residual_color,
            weight="bold" if residual > 0 else "normal",
        )
    for contrast in evidence.contrasts:
        position = _row(contrast.rung, contrast.label)
        color = COLORS[RUNG_NAMES.index(contrast.rung)]
        contrasts.errorbar(
            contrast.difference * 100,
            position,
            xerr=[[100 * (contrast.difference - contrast.lower)], [100 * (contrast.upper - contrast.difference)]],
            fmt="o",
            markersize=5.8,
            color=color,
            elinewidth=1.8,
            capsize=3.3,
            capthick=1.2,
            zorder=4,
        )
    contrasts.text(
        0.50,
        1.5,
        "Reference arm",
        transform=contrasts.get_yaxis_transform(),
        ha="center",
        va="center",
        color=MUTED,
        fontsize=11,
    )
    legend = [
        Line2D([0], [0], marker="o", color=INK, linestyle="none", markersize=6, label="Hardware"),
        Line2D(
            [0],
            [0],
            marker="D",
            color=MUTED,
            markerfacecolor="white",
            linestyle="none",
            markersize=5,
            label="Finite noise replay",
        ),
        Line2D(
            [0],
            [0],
            marker="|",
            color="#93A0A7",
            linestyle="none",
            markersize=10,
            markeredgewidth=1.5,
            label="Exact ideal",
        ),
    ]
    figure.legend(
        handles=legend,
        loc="center left",
        bbox_to_anchor=(0.151, 0.850),
        ncol=3,
        frameon=False,
        fontsize=10,
        labelcolor=INK,
        handletextpad=0.55,
        columnspacing=1.6,
    )
    figure.text(0.055, 0.216, "ODD LABELS REVERSE THE REPLAY RESIDUAL", fontsize=12, color=COLORS[2], weight="bold")
    odd_residuals = [outcome.residual * 100 for outcome in evidence.outcomes if outcome.residual > 0]
    figure.text(
        0.055,
        0.190,
        f"No-feedback s1 / s3 lie {odd_residuals[0]:+.2f} / {odd_residuals[1]:+.2f} pp above replay; "
        "the other 14 outcomes lie below replay. "
        "A uniform subtractive success penalty misses that pattern.",
        fontsize=10.3,
        color=INK,
    )
    figure.text(
        0.055,
        0.154,
        captions["inference"],
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.130,
        captions["dependence"],
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.099,
        captions["metadata"],
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.075,
        "Delay replaces early measurement / feedback with calibrated delay and known-label unconditional correction; "
        "reset remains. These comparisons change several mechanisms.",
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.038,
        captions["source"],
        fontsize=9.3,
        color=MUTED,
    )
    description = {
        "schema": "folded-job-review-figure-v1",
        "renderer": "scripts/render_folded_job_review.py",
        "evidence_schema": "independent-folded-raw-audit-v1",
        "evidence_sha256": evidence.digest,
        "run": evidence.run,
        "evidence_kind": "measured quantum hardware and separately identified model predictions",
        "outcomes": 16,
        "contrast_intervals": 12,
        "shots_per_pub": evidence.shots,
        "charged_seconds": evidence.charged_seconds,
        "residual_inference": "descriptive; contrast intervals do not cover replay residuals",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output,
        format="svg",
        metadata={
            "Date": None,
            "Creator": "scripts/render_folded_job_review.py",
            "Title": "Where hardware departs from the model: measured folded-QPE diagnostics",
            "Description": json.dumps(description, sort_keys=True, separators=(",", ":")),
        },
    )
    # Matplotlib path lines carry insignificant trailing spaces that violate whitespace gates.
    svg_lines = output.read_text(encoding="utf-8").splitlines()
    output.write_text("\n".join(line.rstrip(" \t") for line in svg_lines) + "\n", encoding="utf-8")
    if png is not None:
        png.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(png, format="png", dpi=180, metadata={"Software": "scripts/render_folded_job_review.py"})
    plt.close(figure)


# PNG rasterization depends on the FreeType build matplotlib links; an RMS
# tolerance on 0-255 pixel values accepts glyph antialiasing differences
# between builds while SVG and data outputs stay byte-exact.
PNG_RMS_TOLERANCE = 2.0


def same_image(retained: Path, generated: Path) -> bool:
    """Whether generated reproduces retained: bytes for SVG, tolerance-bounded pixels for PNG."""
    if not retained.is_file():
        return False
    if retained.suffix.lower() != ".png":
        return retained.read_bytes() == generated.read_bytes()
    from matplotlib.testing.compare import compare_images

    return compare_images(str(retained), str(generated), tol=PNG_RMS_TOLERANCE) is None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=ROOT / "results/ripple/folded-job-review.json")
    parser.add_argument("--out", type=Path, default=ROOT / "results/ripple/folded-job-review.svg")
    parser.add_argument("--png", type=Path, help="optional raster copy for preview")
    parser.add_argument("--check", action="store_true", help="verify retained image bytes without rewriting them")
    args = parser.parse_args()
    validate_output_paths(args.out, args.png, evidence_path=args.evidence)
    evidence = read_evidence(args.evidence)
    if args.check:
        with TemporaryDirectory(prefix="folded-job-render-") as temporary:
            generated_svg = Path(temporary) / "folded-job-review.svg"
            generated_png = Path(temporary) / "folded-job-review.png" if args.png is not None else None
            render(evidence, generated_svg, generated_png)
            comparisons = [(args.out, generated_svg)]
            if args.png is not None and generated_png is not None:
                comparisons.append((args.png, generated_png))
            for retained, generated in comparisons:
                if not same_image(retained, generated):
                    raise RuntimeError(f"retained {retained.name} differs from the verified measured-evidence render")
    else:
        render(evidence, args.out, args.png)
    print(
        json.dumps(
            {
                "measured_outcomes": len(evidence.outcomes),
                "simultaneous_contrasts": len(evidence.contrasts),
                "descriptive_residuals": len(evidence.outcomes),
                "shots_per_pub": evidence.shots,
                "charged_seconds": evidence.charged_seconds,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
