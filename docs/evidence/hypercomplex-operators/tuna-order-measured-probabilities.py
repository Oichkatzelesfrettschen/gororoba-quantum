"""Render retained raw frequencies without inferring interval coverage."""

import argparse
import hashlib
import io
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--summary",
    type=Path,
    default=Path("results/quantum_inspire/runs/tuna17-quaternion-order-noise/pilot-summary.json"),
)
parser.add_argument(
    "--output", type=Path, default=Path("docs/evidence/hypercomplex-operators/tuna-order-measured-probabilities.png")
)
parser.add_argument("--check", action="store_true", help="re-render and compare retained figure and metadata")
arguments = parser.parse_args()
summary_path = root / arguments.summary
acquisition = summary_path.parent
summary = json.loads(summary_path.read_text())
for name, digest in summary["analysis_files_sha256"].items():
    if hashlib.sha256((acquisition / name).read_bytes()).hexdigest() != digest:
        raise ValueError("retained analysis binding differs")
settings = summary["settings"]
positions = list(range(len(settings)))
labels = [
    f"{'0' if row['setting']['theta'] == 0 else 'pi/4'}, "
    f"{'0' if row['setting']['phi'] == 0 else 'pi/4'}\n"
    f"{'identity' if row['setting']['representative'] == 0 else 'right-j'}"
    for row in settings
]
figure, axis = plt.subplots(figsize=(11, 5.8), layout="constrained")
axis.scatter(
    positions,
    [row["observed_dark_probability"] for row in settings],
    s=70,
    color="#2455b5",
    label="Measured raw frequency",
)
axis.scatter(
    positions,
    [row["native_dark_probability"] for row in settings],
    marker="_",
    s=300,
    linewidth=2.5,
    color="#b34b16",
    label="Ideal native prediction",
)
axis.set(
    xticks=positions,
    xticklabels=labels,
    ylim=(-0.015, 0.32),
    ylabel="Grouped dark-port probability",
    xlabel="i phase, j phase; global quaternion representative",
)
axis.set_title("Tuna-17 complex-encoded quaternion order pilot", loc="left", fontweight="bold")
axis.grid(axis="y", alpha=0.25)
axis.legend(loc="upper left")
figure.suptitle("24 completed jobs; 393,216 shots; 16,384 shots per job", fontsize=11, x=0.5)
figure.supxlabel(
    "Fixed chronological order and one acquisition per setting confound drift and circuit effects.\n"
    "Raw frequencies establish neither representative equivalence nor fundamental quaternionic physics.",
    fontsize=9,
)
destination = root / arguments.output
image_bytes = io.BytesIO()
figure.savefig(image_bytes, format="png", dpi=170)
plt.close(figure)
metadata = {
    "schema": "hypercomplex-measured-probabilities-figure-v1",
    "summary": str(summary_path.relative_to(root)),
    "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
    "producer": str(Path(__file__).resolve().relative_to(root)),
    "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "png_sha256": hashlib.sha256(image_bytes.getvalue()).hexdigest(),
    "matplotlib_version": matplotlib.__version__,
    "analysis_files_sha256": summary["analysis_files_sha256"],
    "interpretation": (
        "raw measured frequencies and ideal predictions; fixed-order confounding; confidence coverage unestablished"
    ),
}
metadata_bytes = (json.dumps(metadata, indent=2) + "\n").encode()
for path, content in ((destination, image_bytes.getvalue()), (destination.with_suffix(".json"), metadata_bytes)):
    if arguments.check:
        if path.read_bytes() != content:
            raise ValueError(f"retained figure replay differs: {path.relative_to(root)}")
    elif path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"refusing to replace retained bytes: {path.relative_to(root)}")
    else:
        path.write_bytes(content)
print("measured pilot figure: summary/analysis bindings and rendering verified")
