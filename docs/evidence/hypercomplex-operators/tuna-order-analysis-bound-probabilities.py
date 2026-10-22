"""Render retained raw frequencies without inferring interval coverage."""

import argparse
import copy
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[3]


def validate_summary(summary: dict[str, Any], acquisition: Path) -> None:
    """Bind every plotted row to the complete chronological eight-analysis acquisition."""
    names = [f"order-batch-{index:02d}/hypercomplex-analysis.json" for index in range(8)]
    bindings = summary["analysis_files_sha256"]
    if set(bindings) != set(names) or len(summary["settings"]) != 8:
        raise ValueError("pilot needs exactly eight analysis bindings and rows")
    expected_rows = []
    job_ids: list[int] = []
    total_shots = 0
    for index, name in enumerate(names):
        analysis_bytes = (acquisition / name).read_bytes()
        if hashlib.sha256(analysis_bytes).hexdigest() != bindings[name]:
            raise ValueError("retained analysis binding differs")
        analysis = json.loads(analysis_bytes)
        batch = name.split("/")[0]
        receipt_bytes = (acquisition / batch / "submission.json").read_bytes()
        if hashlib.sha256(receipt_bytes).hexdigest() != analysis["receipt_sha256"]:
            raise ValueError("analysis receipt binding differs")
        receipt = json.loads(receipt_bytes)
        science_jobs = [job["job"] for job in receipt["jobs"] if job["file"] == analysis["setting"]["name"] + ".cq"]
        if science_jobs != [analysis["job_id"]]:
            raise ValueError("analysis science job differs from receipt")
        setting = {
            "name": f"order-i{index // 4}-j{index // 2 % 2}-representative{index % 2}",
            "theta": (index // 4) * math.pi / 4,
            "phi": (index // 2 % 2) * math.pi / 4,
            "representative": index % 2,
        }
        if analysis["setting"] != setting:
            raise ValueError("analysis setting differs from frozen chronological design")
        counts = analysis["counts"]
        shots = sum(counts)
        if shots != 16384 or receipt["shots"] != shots or analysis["probabilities"][1] != counts[1] / shots:
            raise ValueError("analysis counts, shots and probabilities differ")
        expected_rows.append(
            {
                "batch": batch,
                "setting": analysis["setting"],
                "science_job": analysis["job_id"],
                "shots": shots,
                "dark_count": counts[1],
                "observed_dark_probability": analysis["probabilities"][1],
                "native_dark_probability": analysis["grouped_predictions"]["native"][1],
                "native_total_variation_residual": analysis["total_variation_residual"]["native"],
                "output_readout_contrast": analysis["readout_contrasts"][1],
            }
        )
        job_ids.extend(job["job"] for job in receipt["jobs"])
        total_shots += receipt["shots"] * len(receipt["jobs"])
    # Canonical JSON also distinguishes integral counts from edited floating-point values.
    if json.dumps(summary["settings"], sort_keys=True) != json.dumps(expected_rows, sort_keys=True):
        raise ValueError("summary plotted rows differ from retained analyses")
    if (
        summary["job_ids"] != job_ids
        or summary["completed_jobs"] != len(job_ids)
        or summary["total_shots"] != total_shots
    ):
        raise ValueError("summary acquisition totals differ from receipts")


def mutation_tests(summary: dict[str, Any], acquisition: Path) -> int:
    """Reject independently changed row values, row membership and binding membership."""
    mutations = []
    for index, row in enumerate(summary["settings"]):
        for field, value in row.items():
            changed = copy.deepcopy(summary)
            if isinstance(value, dict):
                changed["settings"][index][field]["representative"] = 1 - value["representative"]
            elif isinstance(value, str):
                changed["settings"][index][field] += "-edited"
            else:
                changed["settings"][index][field] += 1
            mutations.append(changed)
    for field in ("job_ids", "completed_jobs", "total_shots"):
        changed = copy.deepcopy(summary)
        changed[field] = None
        mutations.append(changed)
    for mode in ("omitted-row", "extra-row", "reordered-rows", "omitted-binding", "extra-binding"):
        changed = copy.deepcopy(summary)
        if mode == "omitted-row":
            changed["settings"].pop()
        elif mode == "extra-row":
            changed["settings"].append(copy.deepcopy(changed["settings"][0]))
        elif mode == "reordered-rows":
            changed["settings"].reverse()
        elif mode == "omitted-binding":
            changed["analysis_files_sha256"].pop(next(iter(changed["analysis_files_sha256"])))
        else:
            changed["analysis_files_sha256"]["extra.json"] = "0" * 64
        mutations.append(changed)
    for changed in mutations:
        try:
            validate_summary(changed, acquisition)
        except ValueError:
            continue
        raise ValueError("corrupted summary passed figure admission")
    return len(mutations)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--summary",
    type=Path,
    default=Path("results/quantum_inspire/runs/tuna17-quaternion-order-noise/pilot-summary.json"),
)
parser.add_argument(
    "--output",
    type=Path,
    default=Path("docs/evidence/hypercomplex-operators/tuna-order-analysis-bound-probabilities.png"),
)
parser.add_argument("--check", action="store_true", help="re-render and compare retained figure and metadata")
parser.add_argument("--self-test", action="store_true", help="reject corrupted summary mutations")
arguments = parser.parse_args()
summary_path = root / arguments.summary
acquisition = summary_path.parent
summary = json.loads(summary_path.read_text())
validate_summary(summary, acquisition)
if arguments.self_test:
    print(f"measured pilot summary: {mutation_tests(summary, acquisition)} mutations rejected")
    raise SystemExit(0)
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
    "schema": "hypercomplex-measured-probabilities-figure-v2",
    "predecessor_metadata": "docs/evidence/hypercomplex-operators/tuna-order-measured-probabilities.json",
    "predecessor_metadata_sha256": hashlib.sha256(
        (root / "docs/evidence/hypercomplex-operators/tuna-order-measured-probabilities.json").read_bytes()
    ).hexdigest(),
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
