"""Render the exact rank-sector norm model and its planned acquisition points.

Quartic numerators come from the four signed-permutation terms in each sector.
Five full 32-dimensional rational matrix evaluations independently verify every
plotted acquisition value. The figure carries ideal predictions, never samples.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from matplotlib.axes import Axes

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from rank_attachments import COSET_SUBGROUP, path_matrix  # noqa: E402
from rank_sector_experiments import (  # noqa: E402
    PARAMETERS,
    SectorProbe,
    sector_alpha,
    sector_probes,
    sector_terms,
)

COEFFICIENT_POLYNOMIALS = (
    (Fraction(1), Fraction(0), Fraction(0)),
    (Fraction(1), Fraction(-2), Fraction(1)),
    (Fraction(0), Fraction(3, 2), Fraction(-1, 2)),
    (Fraction(0), Fraction(1, 2), Fraction(-1, 2)),
)
COLORS = ("#276B9C", "#C36332", "#8656A1", "#277F68")
STYLES: tuple[Any, ...] = ("-", (0, (5, 2)), (0, (1, 2)), (0, (5, 2, 1, 2)))
MARKERS = ("o", "^", "s", "D")
INK = "#23323B"
MUTED = "#596A75"
PAPER = "#F6F7F3"


@dataclass(frozen=True)
class NormTrace:
    sector: int
    probe: SectorProbe
    coefficients: tuple[Fraction, ...]
    planned: tuple[Fraction, ...]


def validate_output_paths(output: Path, png: Path | None) -> None:
    """Reject SVG/PNG aliases before either format can replace the other."""
    if png is not None and (
        output.resolve() == png.resolve() or (output.exists() and png.exists() and output.samefile(png))
    ):
        raise ValueError("--out and --png must identify distinct files")


def _polynomial(coefficients: tuple[Fraction, ...], parameter: Fraction) -> Fraction:
    return sum((coefficient * parameter**power for power, coefficient in enumerate(coefficients)), Fraction(0))


def _norm_coefficients(sector: int, probe: SectorProbe) -> tuple[Fraction, ...]:
    images = [matrix @ np.asarray(probe.coordinates, dtype=int) for matrix in sector_terms(sector)]
    norm = [Fraction(0)] * 5
    for row in range(4):
        amplitude = [
            sum(
                (
                    polynomial[power] * int(image[row])
                    for polynomial, image in zip(COEFFICIENT_POLYNOMIALS, images, strict=True)
                ),
                Fraction(0),
            )
            for power in range(3)
        ]
        for first_power, first in enumerate(amplitude):
            for second_power, second in enumerate(amplitude):
                norm[first_power + second_power] += first * second
    vector_norm = sum(coordinate**2 for coordinate in probe.coordinates)
    return tuple(coefficient / vector_norm for coefficient in norm)


def verified_traces() -> tuple[NormTrace, ...]:
    """Check all 160 acquisition values with five exact full operator matrices."""
    matrices = {parameter: path_matrix(parameter) for parameter in PARAMETERS}
    traces = []
    for sector in range(8):
        columns = tuple(sector ^ offset for offset in COSET_SUBGROUP)
        for probe in sector_probes(sector):
            coefficients = _norm_coefficients(sector, probe)
            planned = []
            vector_norm = sum(coordinate**2 for coordinate in probe.coordinates)
            for parameter in PARAMETERS:
                alpha = Fraction(2) if parameter <= 1 else parameter**2 - parameter + 2
                if alpha != sector_alpha(parameter):
                    raise RuntimeError("plotted coefficient normalization differs from the acquisition model")
                probability = _polynomial(coefficients, parameter) / alpha**2
                image = [
                    sum(
                        matrices[parameter][row, column] * coordinate
                        for column, coordinate in zip(columns, probe.coordinates, strict=True)
                    )
                    for row in range(32)
                ]
                exact_norm = sum(coordinate**2 for coordinate in image)
                expected = Fraction(int(exact_norm.p), int(exact_norm.q)) / (vector_norm * alpha**2)
                if probability != expected or not 0 <= probability <= 1:
                    raise RuntimeError(f"sector {sector}, {probe.name}, t={parameter}: exact probability mismatch")
                planned.append(probability)
            traces.append(NormTrace(sector, probe, coefficients, tuple(planned)))
    return tuple(traces)


def _probabilities(trace: NormTrace, parameters: NDArray[np.float64]) -> NDArray[np.float64]:
    alpha = np.where(parameters <= 1, 2.0, parameters**2 - parameters + 2)
    numerator = np.polynomial.polynomial.polyval(parameters, [float(value) for value in trace.coefficients])
    probabilities = np.asarray(numerator / alpha**2, dtype=float)
    if not np.all(np.isfinite(probabilities)) or np.min(probabilities) < -1e-12 or np.max(probabilities) > 1 + 1e-12:
        raise RuntimeError(f"sector {trace.sector}, {trace.probe.name}: plotted probability outside [0,1]")
    return probabilities


def _panel(axis: Axes, sector: int, traces: tuple[NormTrace, ...]) -> None:
    parameters = np.linspace(0.0, 2.0, 401)
    acquisition = np.asarray([float(value) for value in PARAMETERS])
    for exceptional in (0, 1, 2):
        axis.axvline(exceptional, color="#BAC6CD", linewidth=1.0, linestyle=(0, (2, 3)), zorder=1)
    for probe_index, trace in enumerate(trace for trace in traces if trace.sector == sector):
        axis.plot(
            parameters,
            _probabilities(trace, parameters),
            color=COLORS[probe_index],
            linestyle=STYLES[probe_index],
            linewidth=2.1,
            zorder=3 + probe_index,
        )
        axis.plot(
            acquisition,
            [float(value) for value in trace.planned],
            color=COLORS[probe_index],
            marker=MARKERS[probe_index],
            markersize=5.8 + 0.7 * (3 - probe_index),
            markerfacecolor="white",
            markeredgewidth=1.25,
            linestyle="none",
            zorder=10 + probe_index,
        )
    axis.set_title(f"SECTOR {sector}", loc="left", color=INK, fontsize=11, fontweight="bold", pad=10)
    axis.set_xlim(-0.04, 2.04)
    axis.set_ylim(-0.045, 1.065)
    axis.set_xticks([0, 0.5, 1, 1.5, 2], ["0", "½", "1", "1½", "2"])
    axis.set_yticks([0, 0.25, 0.5, 0.75, 1])
    axis.set_xlabel("Path parameter  t", fontsize=10, labelpad=6, color=MUTED)
    axis.grid(axis="y", color="#DDE3E3", linewidth=0.7, zorder=0)
    axis.tick_params(axis="both", labelsize=9, colors=MUTED, length=0, pad=6)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.spines["bottom"].set_color("#BAC6CD")
    if sector % 4 == 0:
        axis.set_ylabel("Selector success probability", color=MUTED, fontsize=10, labelpad=12)
    else:
        axis.set_yticklabels([])


def render(traces: tuple[NormTrace, ...], output: Path, png: Path | None) -> None:
    validate_output_paths(output, png)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "svg.hashsalt": "rank-sector-norms-v1",
            "axes.facecolor": "white",
            "figure.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )
    figure = plt.figure(figsize=(15.6, 11.4))
    figure.text(0.065, 0.952, "WHERE THE NORM GOES DARK", fontsize=23, color=INK, weight="bold")
    figure.text(0.065, 0.916, "Eight Cayley–Dickson sectors along one exact algebraic path", fontsize=15, color=INK)
    figure.text(0.065, 0.882, "IDEAL EXACT MODEL  /  PLANNED ACQUISITIONS  /  NOT QPU DATA", fontsize=10, color=MUTED)
    figure.text(
        0.065,
        0.843,
        r"$a(t)=e_1+(t-1)^2e_{10}+\frac{t(3-t)}{2}e_{18}-\frac{t(t-1)}{2}e_{25}$",
        fontsize=16,
        color=INK,
    )
    figure.text(
        0.575,
        0.843,
        r"$P(00)=\frac{\|L_{a(t)}v\|^2}{\alpha(t)^2\|v\|^2}$",
        fontsize=16,
        color=INK,
    )
    figure.text(0.575, 0.811, "α(t) = Σ |aₛ(t)| = 2 on [0, 1];  t² − t + 2 on [1, 2]", fontsize=10.5, color=MUTED)
    figure.text(0.065, 0.779, "SECTORS 0–3", fontsize=11, color=INK, weight="bold")
    figure.text(0.181, 0.779, "Four fixed test vectors; singular directions vary with t.", fontsize=10.5, color=MUTED)
    top = figure.add_gridspec(1, 4, left=0.065, right=0.968, bottom=0.558, top=0.749, wspace=0.21)
    bottom = figure.add_gridspec(1, 4, left=0.065, right=0.968, bottom=0.228, top=0.419, wspace=0.21)
    for sector in range(8):
        _panel(figure.add_subplot((top if sector < 4 else bottom)[0, sector % 4]), sector, traces)
    labels = (
        ("Basis probe", "Kernel at t = 1", "Kernel at t = 2", "Bright at t = 1"),
        ("Persistent kernel", "Pulse: dark at t = 0, 2", "Pulse: dark at t = 1, 2", "Bright direction"),
    )
    for row, names in enumerate(labels):
        handles = [
            Line2D(
                [0],
                [0],
                color=COLORS[index],
                linestyle=STYLES[index],
                marker=MARKERS[index],
                markerfacecolor="white",
                linewidth=2,
                markersize=6,
                label=name,
            )
            for index, name in enumerate(names)
        ]
        figure.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.518, 0.494 if row == 0 else 0.164),
            ncol=4,
            frameon=False,
            fontsize=10,
            handlelength=3.3,
            columnspacing=2.3,
            labelcolor=INK,
        )
    figure.text(0.065, 0.449, "SECTORS 4–7", fontsize=11, color=INK, weight="bold")
    figure.text(
        0.181,
        0.449,
        "A fixed orthonormal singular frame exposes four distinct norm channels.",
        fontsize=10.5,
        color=MUTED,
    )
    figure.text(
        0.065,
        0.112,
        "Markers: planned t = 0, ½, 1, 1½, 2.  Dotted verticals: exceptional t = 0, 1, 2.  "
        "Every panel shows four traces.",
        fontsize=10.2,
        color=INK,
    )
    figure.text(
        0.065,
        0.083,
        "Model coincidences across sectors do not establish a hardware comparison: "
        "each sector occupies its own physical patch.",
        fontsize=10.0,
        color=MUTED,
    )
    figure.text(
        0.065,
        0.047,
        "32-dimensional operator  →  8 four-dimensional sectors  ·  32 probes  ·  "
        "160 verified rational acquisition values",
        fontsize=10.2,
        color=MUTED,
    )
    description = {
        "schema": "rank-sector-norm-figure-v1",
        "source": "gororoba_quantum/rank_sector_experiments.py",
        "renderer": "scripts/render_rank_sector_norms.py",
        "evidence_kind": "ideal exact algebra; no QPU data",
        "parameters": [str(value) for value in PARAMETERS],
        "traces": [
            {
                "sector": trace.sector,
                "probe": trace.probe.name,
                "coordinates": trace.probe.coordinates,
                "squared_norm_coefficients_ascending": [str(value) for value in trace.coefficients],
                "exact_probabilities": [str(value) for value in trace.planned],
            }
            for trace in traces
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output,
        format="svg",
        metadata={
            "Date": None,
            "Creator": "scripts/render_rank_sector_norms.py",
            "Title": "Where the norm goes dark: exact Cayley-Dickson rank-sector predictions",
            "Description": json.dumps(description, sort_keys=True, separators=(",", ":")),
        },
    )
    # Matplotlib path lines carry insignificant trailing spaces that violate whitespace gates.
    svg_lines = output.read_text(encoding="utf-8").splitlines()
    output.write_text("\n".join(line.rstrip(" \t") for line in svg_lines) + "\n", encoding="utf-8")
    if png is not None:
        png.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(png, format="png", dpi=180, metadata={"Software": "scripts/render_rank_sector_norms.py"})
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
    parser.add_argument("--out", type=Path, default=ROOT / "results/ripple/rank-sector-norms.svg")
    parser.add_argument("--png", type=Path, help="optional raster copy for preview")
    parser.add_argument("--check", action="store_true", help="verify retained image bytes without rewriting them")
    args = parser.parse_args()
    try:
        validate_output_paths(args.out, args.png)
    except ValueError as error:
        parser.error(str(error))
    traces = verified_traces()
    if args.check:
        with TemporaryDirectory(prefix="rank-sector-render-") as temporary:
            generated_svg = Path(temporary) / "rank-sector-norms.svg"
            generated_png = Path(temporary) / "rank-sector-norms.png" if args.png is not None else None
            render(traces, generated_svg, generated_png)
            comparisons = [(args.out, generated_svg)]
            if args.png is not None and generated_png is not None:
                comparisons.append((args.png, generated_png))
            for retained, generated in comparisons:
                if not same_image(retained, generated):
                    raise RuntimeError(f"retained {retained.name} differs from the verified exact-model render")
    else:
        render(traces, args.out, args.png)
    print(json.dumps({"sectors": 8, "traces": len(traces), "verified_acquisition_values": 160, "qpu_data": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
