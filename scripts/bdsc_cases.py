"""Belenos six-state qualification case: one runnable Quandela case per observation, and its readout.

docs/evidence/bdsc/qualification_case.json fixes the observations (pair,
completion, processing policy, epoch, six-state label), the trial count and
the shot budget; this script turns each observation into a case directory
that scripts/qd_platform.py plans and submits:

- circuit.json (qd-numeric-circuit-v1): one 24-mode numeric unitary, the
  Householder or Givens completion W of the chip column U24 psi, with
  W e_r = U24 psi on the source mode r and complex entries [re, im];
- cases.json (qd-bdsc-cases-v1): command sample_count, min_detected_photons
  1, max_samples the frozen trials, max_shots twice that, the policy's
  mitigations (null for provider defaults, [] to disable them), the selected
  output modes, the eligibility rule and the ideal selected probability.

Without --draw the cases carry no compilation_seed and no acquisition rank
and read draft: they plan, and they do not submit. With --draw (an
scripts/anu_qrng.py record) value i seeds observation i and value
settings + i ranks it within its epoch.

The readout counts one trial per detection pattern with exactly one click:
selected when that click is on a selected output, eligible either way.
Patterns with zero or several clicks are recorded and excluded.

Usage:
  "$PYTHON" scripts/bdsc_cases.py --write DIR [--draw FILE]
  "$PYTHON" scripts/bdsc_cases.py --check DIR [--draw FILE]
  "$PYTHON" scripts/bdsc_cases.py --local DIR     # Perceval SLOS reproduces every ideal probability
  "$PYTHON" scripts/bdsc_cases.py --readout DIR RUN_DIR...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_certificate as cert  # noqa: E402

import bdsc  # noqa: E402

CASE = ROOT / "docs/evidence/bdsc/qualification_case.json"
TARGET = ROOT / "docs/evidence/bdsc/target.json"
FAMILY = "bdsc_qualification"
CASES_SCHEMA = "qd-bdsc-cases-v1"
CIRCUIT_SCHEMA = "qd-numeric-circuit-v1"
PLATFORMS = ["sim:belenos", "qpu:belenos"]
MAX_DURATION = 300
PAIR_TAGS = {"target-complement": "tc", "middle-middle": "mm"}
COMPLETION_TAGS = {"householder": "h", "givens": "g"}
POLICY_TAGS = {"provider-defaults": "d", "empty-mitigation": "n"}
LABEL_TAGS = {"f": "f", "g": "g", "+": "p", "-": "m", "+i": "pi", "-i": "mi"}
ELIGIBILITY = "exactly one click among the 24 outputs; selected when that click is on a selected output"
COMPLETIONS = {"householder": cert.householder_completion, "givens": cert.givens_completion}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def job_name(observation: dict[str, Any]) -> str:
    return "-".join(
        (
            PAIR_TAGS[observation["pair"]],
            COMPLETION_TAGS[observation["preparation"]],
            POLICY_TAGS[observation["processing"]],
            f"e{observation['epoch']}",
            LABEL_TAGS[observation["label"]],
        )
    )


def load_draw(path: Path | None, settings: int) -> list[int] | None:
    """The first 2 x settings values of an anu_qrng record, which must be checked and long enough."""
    if path is None:
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    values = record["values"]
    raw = record["raw"].encode("utf-8")
    require(sha256_bytes(raw) == record["raw_sha256"], f"{path}: raw bytes differ from their sha256")
    require(values == json.loads(raw)["data"], f"{path}: parsed values differ from the raw response")
    require(len(values) >= 2 * settings, f"{path}: {len(values)} values, the case needs {2 * settings}")
    return [int(v) for v in values[: 2 * settings]]


def circuit_document(observation: dict[str, Any], case: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    u = cert.numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    bank = next(b for b in case["banks"] if b["pair"] == observation["pair"])
    row = next(r for r in bank["settings"] if r["label"] == observation["label"])
    psi = np.array([complex(re, im) for re, im in row["state_e_basis"]])
    column = cert.chip_column(u, psi)
    source = target["source_mode"]
    w = COMPLETIONS[observation["preparation"]](column, source)
    require(np.allclose(w[:, source], column, atol=1e-12), f"{job_name(observation)}: completion misses the column")
    input_state = [0] * cert.MODES
    input_state[source] = 1
    return {
        "schema": CIRCUIT_SCHEMA,
        "modes": cert.MODES,
        "input_state": input_state,
        "components": [{"at": 0, "numeric": [[[float(z.real), float(z.imag)] for z in line] for line in w]}],
    }


def documents(draw: Path | None) -> dict[str, dict[str, bytes]]:
    """{job: {"cases.json": bytes, "circuit.json": bytes}} for every observation of the frozen case."""
    case_bytes = CASE.read_bytes()
    case = json.loads(case_bytes)
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    observations = case["observations"]
    values = load_draw(draw, len(observations))
    trials = case["acquisition"]["trials_per_setting"]
    max_shots = case["resources"]["max_shots_per_setting"]
    ideal = {(b["pair"], r["label"]): r["ideal_selected"]["E0"] for b in case["banks"] for r in b["settings"]}
    ranks: dict[int, int] = {}
    if values is not None:
        for epoch in sorted({o["epoch"] for o in observations}):
            members = [i for i, o in enumerate(observations) if o["epoch"] == epoch]
            order = sorted(members, key=lambda i: (values[len(observations) + i], i))
            ranks.update({i: rank for rank, i in enumerate(order)})
    out: dict[str, dict[str, bytes]] = {}
    for i, observation in enumerate(observations):
        name = job_name(observation)
        circuit_bytes = (json.dumps(circuit_document(observation, case, target), indent=1) + "\n").encode()
        manifest: dict[str, Any] = {
            "schema": CASES_SCHEMA,
            "family": FAMILY,
            "job": name,
            "platforms": PLATFORMS,
            "command": "sample_count",
            "gate_form": "numeric",
            "min_detected_photons": 1,
            "max_samples": trials,
            "max_shots": max_shots,
            "max_duration": MAX_DURATION,
            "mitigations": None if observation["processing"] == "provider-defaults" else [],
            "observation": observation,
            "observation_index": i,
            "selected_modes": target["selected_modes"],
            "source_mode": target["source_mode"],
            "eligibility": ELIGIBILITY,
            "ideal_selected_E0": ideal[(observation["pair"], observation["label"])],
            "qualification_case_sha256": sha256_bytes(case_bytes),
            "target_sha256": target["target_sha256"],
            "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
            "draft": values is None,
        }
        if values is not None:
            manifest["compilation_seed"] = values[i]
            manifest["acquisition_rank"] = ranks[i]
            manifest["draw"] = {"file": str(draw), "seed_index": i, "rank_index": len(observations) + i}
        cases_bytes = (json.dumps(manifest, indent=1) + "\n").encode()
        out[name] = {"cases.json": cases_bytes, "circuit.json": circuit_bytes}
    require(len(out) == len(observations), "two observations share a job name")
    return out


def write(directory: Path, draw: Path | None) -> None:
    for name, files in documents(draw).items():
        (directory / name).mkdir(parents=True, exist_ok=True)
        for file, content in files.items():
            (directory / name / file).write_bytes(content)
    print(f"bdsc cases: wrote {len(list(directory.iterdir()))} case directories under {directory}")


def check(directory: Path, draw: Path | None) -> None:
    fresh = documents(draw)
    present = sorted(p.name for p in directory.iterdir() if p.is_dir())
    require(present == sorted(fresh), f"case directories differ: {sorted(set(present) ^ set(fresh))[:6]}")
    for name, files in fresh.items():
        # Completion entries are floats from a BLAS product, so circuits compare within cert.CHECK_TOLERANCE, and
        # each manifest compares exactly apart from its circuit digest, which must match its own circuit's bytes.
        retained_circuit = (directory / name / "circuit.json").read_bytes()
        cert.close(json.loads(files["circuit.json"]), json.loads(retained_circuit), f"{name}/circuit.json")
        manifest = json.loads((directory / name / "cases.json").read_bytes())
        expected = json.loads(files["cases.json"])
        require(manifest["circuit"]["sha256"] == sha256_bytes(retained_circuit), f"{name}: circuit digest")
        manifest["circuit"]["sha256"] = expected["circuit"]["sha256"]
        require(manifest == expected, f"{name}/cases.json differs from a fresh build")
    print(f"bdsc cases: {len(fresh)} case directories match the frozen case")


def _local_item(case_dir: Path) -> tuple[str, float, float]:
    """(job, ideal selected probability, Perceval SLOS selected probability) for one case directory."""
    import perceval as pcvl
    import qd_platform

    manifest, circuit, _ = qd_platform.load_case(case_dir)
    built = qd_platform.experiment(manifest, circuit)
    processor = pcvl.Processor("SLOS", built)
    probs = processor.probs()["results"]
    selected = set(manifest["selected_modes"])
    p = sum(float(v) for state, v in probs.items() if state.n == 1 and any(state[m] for m in selected))
    return manifest["job"], float(manifest["ideal_selected_E0"]), p


def local(directory: Path) -> None:
    """Perceval SLOS on each built experiment reproduces the case's ideal selected probability to 1e-9."""
    import parallel

    dirs = sorted(p for p in directory.iterdir() if p.is_dir())
    rows = parallel.ordered_map(_local_item, dirs)
    worst = max(abs(a - b) for _, a, b in rows)
    require(worst <= 1e-9, f"SLOS deviates from the ideal selected probability by {worst:.3e}")
    print(f"bdsc cases: Perceval SLOS reproduces {len(rows)} ideal selected probabilities within {worst:.1e}")


def tally(counts: dict[str, int], selected_modes: list[int]) -> dict[str, int]:
    """Selected, eligible and excluded trials from detection-pattern counts under the eligibility rule."""
    selected = set(selected_modes)
    out = {"selected": 0, "eligible": 0, "zero_click": 0, "multi_click": 0}
    for pattern, count in counts.items():
        clicks = [m for m, c in enumerate(pattern.split(",")) if int(c) > 0]
        if not clicks:
            out["zero_click"] += count
        elif len(clicks) > 1:
            out["multi_click"] += count
        else:
            out["eligible"] += count
            out["selected"] += count if clicks[0] in selected else 0
    return out


def readout(directory: Path, runs: list[Path]) -> dict[str, Any]:
    """Every contrast of the frozen case from collected runs, each policy admitted only by its contract."""
    case = json.loads(CASE.read_text(encoding="utf-8"))
    observations = case["observations"]
    contrasts = cert.case_contrasts(observations)
    by_job: dict[str, dict[str, int]] = {}
    for run in runs:
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        result = json.loads((run / "results.json").read_text(encoding="utf-8"))
        require(result.get("status") == "completed", f"{run}: status {result.get('status')}")
        by_job[manifest["job"]] = tally(result["counts"], manifest["selected_modes"])
    names = [job_name(o) for o in observations]
    missing = [n for n in names if n not in by_job]
    require(not missing, f"no collected run for {missing[:6]}")
    k = np.array([by_job[n]["selected"] for n in names])
    n = np.array([by_job[n]["eligible"] for n in names])
    trials = case["acquisition"]["trials_per_setting"]
    require(bool(np.all(n == trials)), "an observation's eligible trials differ from the frozen n")
    contract = json.loads((ROOT / "docs/evidence/bdsc/provider_contract.json").read_text(encoding="utf-8"))
    supported = {c["capability"]: c["status"] for c in contract["capabilities"]}
    admitted_policies = {"empty-mitigation"} if supported.get("uncorrected_observations") == "supported" else set()
    admitted = np.array([o["processing"] in admitted_policies for o in observations])
    result = bdsc.contrast_readout(k, n, contrasts, cert.CASE_ALPHA, admitted)
    return {
        "admitted_policies": sorted(admitted_policies),
        "tallies": by_job,
        "contrasts": [
            {"family": c[0], "terms": [[names[j], w] for j, w in c[2]], "interval": [lo, hi], "status": st}
            for c, lo, hi, st in zip(contrasts, result["lower"], result["upper"], result["status"], strict=True)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--local", type=Path)
    group.add_argument("--readout", type=Path, nargs="+")
    parser.add_argument("--draw", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write, args.draw)
    elif args.check:
        check(args.check, args.draw)
    elif args.local:
        local(args.local)
    else:
        print(json.dumps(readout(args.readout[0], args.readout[1:]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
