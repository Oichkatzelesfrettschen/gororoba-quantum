"""Render measured folded-QPE outcomes, bounded contrasts, and replay residuals.

The retained independent audit supplies every plotted value. Contrast intervals
cover the declared twelve-comparison family; replay residuals stay descriptive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

ROOT = Path(__file__).resolve().parents[1]
RUNG_NAMES = ("archived", "delay", "no_feed_forward", "coherent")
DISPLAY_NAMES = ("Archived", "Delay", "No feedback", "Coherent")
COLORS = ("#276B9C", "#C36332", "#8656A1", "#277F68")
INK = "#23323B"
MUTED = "#596A75"
PAPER = "#F6F7F3"


@dataclass(frozen=True)
class Outcome:
    rung: str
    label: int
    measured: float
    ideal: float
    replay: float
    residual: float


@dataclass(frozen=True)
class Contrast:
    rung: str
    label: int
    difference: float
    lower: float
    upper: float


@dataclass(frozen=True)
class Evidence:
    digest: str
    run: str
    outcomes: tuple[Outcome, ...]
    contrasts: tuple[Contrast, ...]
    shots: int
    charged_seconds: float
    half_width: float


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_evidence(path: Path) -> Evidence:
    """Require the measured audit schema and reconcile the plotted marginals."""
    contents = path.read_bytes()
    data = json.loads(contents)
    _require(data["schema"] == "independent-folded-raw-audit-v1", "unsupported folded audit schema")
    _require(all(value is True for value in data["contract_checks"].values()), "audit contract failure")
    _require(data["source_hashes_unchanged_during_audit"] is True, "source hashes changed during audit")
    _require(data["defects"] == [], "audit records defects")
    _require(
        len(data["members"]) == 16 and len(data["contrasts"]) == 12, "expected sixteen outcomes and twelve contrasts"
    )
    members = {(member["rung"], member["phase_label"]): member for member in data["members"]}
    _require(set(members) == {(rung, label) for rung in RUNG_NAMES for label in range(4)}, "member identities differ")
    outcomes = []
    for rung in RUNG_NAMES:
        for label in range(4):
            member = members[(rung, label)]
            _require(member["shots"] == 8192, "expected 8192 measured shots per PUB")
            measured = float(member["terminal_probability"])
            ideal = float(member["ideal_terminal_probability"])
            replay = float(member["replay_terminal_probability"])
            residual = float(member["hardware_minus_replay"])
            _require(
                all(math.isfinite(value) and 0 <= value <= 1 for value in (measured, ideal, replay)),
                "invalid probability",
            )
            _require(
                measured == member["terminal_successes"] / member["shots"], "measured probability differs from counts"
            )
            _require(sum(member["bit_counts_integer_order"]) == member["shots"], "raw counts differ from shots")
            _require(math.isclose(residual, measured - replay, abs_tol=1e-14), "residual differs from marginals")
            outcomes.append(Outcome(rung, label, measured, ideal, replay, residual))
    positive_residuals = {(outcome.rung, outcome.label) for outcome in outcomes if outcome.residual > 0}
    _require(
        positive_residuals == {("no_feed_forward", 1), ("no_feed_forward", 3)},
        "highlighted residual-sign pattern differs",
    )
    confidence = data["confidence"]
    _require(confidence["comparisons"] == 12 and confidence["family_alpha"] == 0.05, "confidence family differs")
    half_width = 2 * math.sqrt(math.log(4 / (0.05 / 12)) / (2 * 8192))
    _require(math.isclose(confidence["half_width"], half_width, abs_tol=1e-14), "confidence formula differs")
    source_contrasts = {contrast["name"]: contrast for contrast in data["contrasts"]}
    _require(len(source_contrasts) == 12, "contrast identities repeat")
    contrasts = []
    for rung in RUNG_NAMES[1:]:
        for label in range(4):
            contrast = source_contrasts[f"qpe_{rung}_minus_archived_s{label}"]
            difference = float(contrast["difference"])
            lower, upper = map(float, contrast["simultaneous_interval"])
            expected = (
                members[(rung, label)]["terminal_probability"] - members[("archived", label)]["terminal_probability"]
            )
            _require(math.isclose(difference, expected, abs_tol=1e-14), "contrast differs from measured marginals")
            _require(math.isclose(lower, difference - half_width, abs_tol=1e-14), "lower confidence endpoint differs")
            _require(math.isclose(upper, difference + half_width, abs_tol=1e-14), "upper confidence endpoint differs")
            _require(contrast["retained_reject_null"] is None, "precision contract changed to a hypothesis decision")
            contrasts.append(Contrast(rung, label, difference, lower, upper))
    charged = float(data["timing_totals"]["charged_seconds"])
    _require(charged == 40 and sum(job["charge_seconds"] for job in data["jobs"]) == charged, "charged totals differ")
    return Evidence(
        hashlib.sha256(contents).hexdigest(),
        str(data["run"]),
        tuple(outcomes),
        tuple(contrasts),
        8192,
        charged,
        half_width,
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


def render(evidence: Evidence, output: Path, png: Path | None) -> None:
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
    figure = plt.figure(figsize=(17.0, 12.0))
    figure.text(0.055, 0.954, "WHERE HARDWARE DEPARTS FROM THE MODEL", fontsize=23, color=INK, weight="bold")
    figure.text(0.055, 0.918, "Folded phase estimation on ibm_kingston", fontsize=16, color=INK)
    figure.text(
        0.055, 0.886, "MEASURED QPU DATA  /  16 PUBs × 8,192 SHOTS  /  40 s CHARGED", fontsize=10.5, color=MUTED
    )
    grid = figure.add_gridspec(
        1, 3, left=0.155, right=0.967, bottom=0.290, top=0.766, width_ratios=(1.14, 1, 1), wspace=0.24
    )
    probabilities, contrasts, residuals = [figure.add_subplot(grid[0, index]) for index in range(3)]
    _style_axis(probabilities, "01  TERMINAL-BIT SUCCESS", "Each row is one measured circuit and phase label.")
    _style_axis(contrasts, "02  CHANGE FROM ARCHIVED", "95% simultaneous intervals across 12 contrasts.")
    _style_axis(residuals, "03  HARDWARE − FINITE REPLAY", "Descriptive discrepancies; contrast CIs do not apply.")
    probabilities.set_xlim(43, 104)
    probabilities.set_xticks([50, 60, 70, 80, 90, 100])
    probabilities.set_xlabel("Success probability (%)", color=MUTED, fontsize=10.5, labelpad=12)
    contrasts.set_xlim(-23, 18)
    contrasts.set_xticks([-20, -10, 0, 10])
    contrasts.set_xlabel("Difference (percentage points)", color=MUTED, fontsize=10.5, labelpad=12)
    residuals.set_xlim(-24, 20)
    residuals.set_xticks([-20, -10, 0, 10, 20])
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
        "Inference: Hoeffding + union bound; 12-family α = 0.05; half-width 4.0945 pp. "
        "Independent stationary repetitions within each PUB are required.",
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.130,
        "Within-shot and cross-PUB dependence are unrestricted by the bound. PUBs remain unpaired. "
        "Delay intervals include zero; equivalence is untested.",
        fontsize=9.8,
        color=MUTED,
    )
    figure.text(
        0.055,
        0.099,
        "Confounds: coherent routing / terminal writer differ (69 CZ, q94 versus 72 CZ, q93); "
        "the two jobs ran in separate windows. Odd no-feedback ideal contrast is −50 pp.",
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
        "Jobs: db67fqsvf2bc73d0pk4g (29 s) · db67frimb58s738bci4g (11 s)   |   "
        "Source: independently checked raw counts, QPY mappings, and recorded model replay.",
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
    if png is not None:
        png.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(png, format="png", dpi=180, metadata={"Software": "scripts/render_folded_job_review.py"})
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=ROOT / "results/ripple/folded-job-review.json")
    parser.add_argument("--out", type=Path, default=ROOT / "results/ripple/folded-job-review.svg")
    parser.add_argument("--png", type=Path, help="optional raster copy for preview")
    parser.add_argument("--check", action="store_true", help="verify retained image bytes without rewriting them")
    args = parser.parse_args()
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
                if not retained.is_file() or retained.read_bytes() != generated.read_bytes():
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
