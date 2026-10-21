"""Belenos six-state qualification case: one runnable Quandela job per template, policy and epoch, and its readout.

docs/evidence/bdsc/qualification_case.json fixes the observations, the 8 jobs
of 12 iterations, the trials and the shot budget; this script turns each job
into a case directory that scripts/qd_platform.py plans and submits:

- circuit.json (qd-template-circuit-v1): the job's fixed 24-mode template
  from bdsc_certificate.template_ops, outward-ladder or reverse-ladder, with
  the photon on source mode 6;
- cases.json (qd-bdsc-cases-v1): gate_form template, command sample_count,
  min_detected_photons 1, 12 iterations whose settings bind one state's 47
  parameters and carry its chip column, the policy's mitigations (null for
  provider defaults, [] to disable them), max_samples and max_shots summed
  over the iterations, the selected output modes and the eligibility rule.

Without --draw the cases carry no compilation seeds, keep the observation
order and read draft: they plan and do not submit. With --draw (an
scripts/anu_qrng.py record of at least 192 values) value i seeds observation i
and value 96 + i orders it within its job.

The readout counts one trial per detection pattern with exactly one click:
selected when that click is on a selected output, eligible either way.
Patterns with zero or several clicks are tallied and excluded.

Usage:
  "$PYTHON" scripts/bdsc_cases.py --write DIR [--draw FILE]
  "$PYTHON" scripts/bdsc_cases.py --check DIR [--draw FILE]
  "$PYTHON" scripts/bdsc_cases.py --local DIR
  "$PYTHON" scripts/bdsc_cases.py --readout RUN_DIR...
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
CONTRACT = ROOT / "docs/evidence/bdsc/provider_contract.json"
FAMILY = "bdsc_qualification"
CASES_SCHEMA = "qd-bdsc-cases-v1"
CIRCUIT_SCHEMA = "qd-template-circuit-v1"
PLATFORMS = ["sim:belenos", "qpu:belenos"]
MAX_DURATION = 300
TEMPLATE_TAGS = {"outward-ladder": "out", "reverse-ladder": "rev"}
POLICY_TAGS = {"provider-defaults": "def", "empty-mitigation": "none"}
PAIR_TAGS = {"target-complement": "tc", "middle-middle": "mm"}
LABEL_TAGS = {"f": "f", "g": "g", "+": "p", "-": "m", "+i": "pi", "-i": "mi"}
ELIGIBILITY = "exactly one click among the 24 outputs; selected when that click is on a selected output"
# The largest share of an iteration's samples the one-click rule may exclude before the iteration is refused.
ELIGIBLE_LOSS = 0.01


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def job_name(job: dict[str, Any]) -> str:
    return f"{TEMPLATE_TAGS[job['template']]}-{POLICY_TAGS[job['processing']]}-e{job['epoch']}"


def setting_name(observation: dict[str, Any]) -> str:
    return f"{PAIR_TAGS[observation['pair']]}-{LABEL_TAGS[observation['label']]}"


def load_draw(path: Path | None, settings: int) -> list[int] | None:
    """The first 2 x settings values of a keyed ANU Quantum Numbers uint16 record that anu_qrng.admit accepts."""
    if path is None:
        return None
    import anu_qrng

    record = json.loads(path.read_text(encoding="utf-8"))
    anu_qrng.admit(record)
    require(str(record.get("source", "")).startswith(anu_qrng.ENDPOINTS["aqn"]), f"{path}: not the keyed AQN service")
    require(record["type"] == "uint16", f"{path}: type {record['type']!r}, the case draws uint16")
    require(len(record["values"]) >= 2 * settings, f"{path}: {len(record['values'])} values, need {2 * settings}")
    return list(record["values"][: 2 * settings])


def columns(case: dict[str, Any], target: dict[str, Any]) -> dict[tuple[str, str], np.ndarray]:
    """The chip column U24 psi of every bank state, keyed by (pair, label)."""
    u = cert.numeric_unitary([[(Fraction(a), Fraction(b)) for a, b in row] for row in target["U24"]])
    out = {}
    for bank in case["banks"]:
        for row in bank["settings"]:
            psi = np.array([complex(re, im) for re, im in row["state_e_basis"]])
            out[(bank["pair"], row["label"])] = cert.chip_column(u, psi)
    return out


def _job_params(item: tuple[str, list[tuple[int, np.ndarray]], int]) -> dict[int, np.ndarray]:
    """The template parameters of one job's states, keyed by observation index."""
    template, members, source = item
    return {i: cert.template_params(template, column, source) for i, column in members}


def documents(draw: Path | None) -> dict[str, dict[str, bytes]]:
    """{job: {"cases.json": bytes, "circuit.json": bytes}} for every job of the frozen case."""
    case_bytes = CASE.read_bytes()
    case = json.loads(case_bytes)
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    observations = case["observations"]
    values = load_draw(draw, len(observations))
    source = target["source_mode"]
    trials = case["resources"]["eligible_trials_per_setting"]
    max_shots = case["resources"]["max_shots_per_iteration"]
    ideal = {(b["pair"], r["label"]): r["ideal_selected"]["E0"] for b in case["banks"] for r in b["settings"]}
    chip = columns(case, target)
    import parallel

    # Each job's 12 template parameterizations are independent of every other job's, so they run as one pool item.
    items = [
        (
            job["template"],
            [(i, chip[(observations[i]["pair"], observations[i]["label"])]) for i in job["iterations"]],
            source,
        )
        for job in case["jobs"]
    ]
    solved = parallel.ordered_map(_job_params, items, min_items=1)
    out: dict[str, dict[str, bytes]] = {}
    for job, params_by_index in zip(case["jobs"], solved, strict=True):
        ops = cert.template_ops(job["template"], source)
        input_state = [0] * cert.MODES
        input_state[source] = 1
        circuit = {
            "schema": CIRCUIT_SCHEMA,
            "template": job["template"],
            "modes": cert.MODES,
            "input_state": input_state,
            "parameters": sum(1 for _, _, k in ops if k is not None),
            "ops": [list(op) for op in ops],
        }
        circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
        members = list(job["iterations"])
        if values is not None:
            members.sort(key=lambda i: (values[len(observations) + i], i))
        settings = []
        for i in members:
            o = observations[i]
            column = chip[(o["pair"], o["label"])]
            params = params_by_index[i]
            setting: dict[str, Any] = {
                "name": setting_name(o),
                "observation_index": i,
                "circuit_params": {f"x{k}": float(v) for k, v in enumerate(params)},
                "column": [[float(z.real), float(z.imag)] for z in column],
                "ideal_selected_E0": ideal[(o["pair"], o["label"])],
            }
            if values is not None:
                setting["compilation_seed"] = values[i]
            settings.append(setting)
        name = job_name(job)
        manifest: dict[str, Any] = {
            "schema": CASES_SCHEMA,
            "family": FAMILY,
            "job": name,
            "platforms": PLATFORMS,
            "command": "sample_count",
            "gate_form": "template",
            "min_detected_photons": 1,
            "iterations": len(settings),
            "max_samples": trials * len(settings),
            "max_shots": max_shots * len(settings),
            "max_duration": MAX_DURATION,
            "mitigations": None if job["processing"] == "provider-defaults" else [],
            "job_spec": job,
            "settings": settings,
            "selected_modes": target["selected_modes"],
            "eligibility": ELIGIBILITY,
            "qualification_case_sha256": sha256_bytes(case_bytes),
            "target_sha256": target["target_sha256"],
            "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
            "draft": values is None,
        }
        if values is not None and draw is not None:
            manifest["draw"] = {"file": draw.name, "seed_offset": 0, "order_offset": len(observations)}
        out[name] = {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}
    require(len(out) == len(case["jobs"]), "two jobs share a name")
    return out


def write(directory: Path, draw: Path | None) -> None:
    for name, files in documents(draw).items():
        (directory / name).mkdir(parents=True, exist_ok=True)
        for file, content in files.items():
            (directory / name / file).write_bytes(content)
    print(f"bdsc cases: wrote {len(list(directory.iterdir()))} job directories under {directory}")


def check(directory: Path, draw: Path | None) -> None:
    """A rebuild matches: circuits exactly, manifests exactly apart from float parameters and columns, which come
    from a BLAS product and compare within cert.CHECK_TOLERANCE."""
    fresh = documents(draw)
    present = sorted(p.name for p in directory.iterdir() if p.is_dir())
    require(present == sorted(fresh), f"job directories differ: {sorted(set(present) ^ set(fresh))}")
    for name, files in fresh.items():
        retained_circuit = (directory / name / "circuit.json").read_bytes()
        require(retained_circuit == files["circuit.json"], f"{name}/circuit.json differs from a fresh build")
        cert.close(json.loads(files["cases.json"]), json.loads((directory / name / "cases.json").read_bytes()), name)
    print(f"bdsc cases: {len(fresh)} job directories match the frozen case")


def _local_item(case_dir: Path) -> tuple[str, int, float]:
    """(job, iterations, worst deviation of Perceval SLOS from the ideal selected probability over them)."""
    import perceval as pcvl
    import qd_platform

    manifest, circuit, _ = qd_platform.load_case(case_dir)
    built, settings = qd_platform.template_experiment(manifest, circuit)
    selected = set(manifest["selected_modes"])
    parameters = {p.name: p for p in built.get_circuit_parameters().values()}
    worst = 0.0
    for setting in settings:
        for key, value in setting["circuit_params"].items():
            parameters[key].set_value(value)
        probs = pcvl.Processor("SLOS", built).probs()["results"]
        p = sum(float(v) for state, v in probs.items() if state.n == 1 and any(state[m] for m in selected))
        worst = max(worst, abs(p - float(setting["ideal_selected_E0"])))
        for parameter in parameters.values():
            parameter.reset()
    return manifest["job"], len(settings), worst


def local(directory: Path) -> None:
    """Perceval SLOS on every iteration of every runner-built job reproduces the ideal selected probability."""
    import parallel

    dirs = sorted(p for p in directory.iterdir() if p.is_dir())
    # Each item simulates a whole job's iterations, so one item already repays a worker.
    rows = parallel.ordered_map(_local_item, dirs, min_items=1)
    worst = max(w for _, _, w in rows)
    require(worst <= 1e-9, f"SLOS deviates from the ideal selected probability by {worst:.3e}")
    print(f"bdsc cases: Perceval SLOS reproduces {sum(n for _, n, _ in rows)} ideal probabilities within {worst:.1e}")


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


def readout(runs: list[Path], contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Every contrast of the frozen case from collected runs, each policy admitted only by its contract."""
    case_bytes = CASE.read_bytes()
    case = json.loads(case_bytes)
    observations = case["observations"]
    contrasts = cert.case_contrasts(observations)
    trials = case["resources"]["eligible_trials_per_setting"]
    tallies: dict[int, dict[str, int]] = {}
    for run in runs:
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        result = json.loads((run / "results.json").read_text(encoding="utf-8"))
        # collect retains the scrubbed status record, whose own status field names the job's end state.
        state = result.get("status", {})
        require(isinstance(state, dict) and state.get("status") == "completed", f"{run}: the job did not complete")
        require(result.get("partial") is False, f"{run}: a partial result")
        require(not manifest.get("draft", True), f"{run}: a draft case carries no frozen seeds or order")
        require(manifest["qualification_case_sha256"] == sha256_bytes(case_bytes), f"{run}: built from another case")
        require(manifest["target_sha256"] == case["target_sha256"], f"{run}: built for another target")
        per_iteration = result["iterations"]
        require(len(per_iteration) == len(manifest["settings"]), f"{run}: iteration count differs")
        for setting, iteration in zip(manifest["settings"], per_iteration, strict=True):
            # Each returned iteration names the parameters and seed it ran with, so attribution is checked.
            ran = iteration["iteration"]
            require(ran.get("circuit_params") == setting["circuit_params"], f"{run}/{setting['name']}: parameters")
            require(ran.get("compilation_seed") == setting["compilation_seed"], f"{run}/{setting['name']}: seed")
            index = setting["observation_index"]
            require(index not in tallies, f"{run}/{setting['name']}: observation {index} collected twice")
            counted = tally(iteration["counts"], manifest["selected_modes"])
            # Fixed n: an iteration that stopped on its shot limit short of the frozen samples is a stop condition,
            # and one-click eligibility may drop at most ELIGIBLE_LOSS of them (dark counts, multi-photon events).
            samples = iteration.get("samples")
            require(samples == trials, f"{run}/{setting['name']}: {samples} samples, the case froze {trials}")
            require(counted["eligible"] >= (1 - ELIGIBLE_LOSS) * trials, f"{run}/{setting['name']}: eligible short")
            tallies[index] = counted
    missing = [i for i in range(len(observations)) if i not in tallies]
    require(not missing, f"no collected iteration for observations {missing[:6]}")
    k = np.array([tallies[i]["selected"] for i in range(len(observations))])
    n = np.array([tallies[i]["eligible"] for i in range(len(observations))])
    contract = json.loads(CONTRACT.read_text(encoding="utf-8")) if contract is None else contract
    status = {c["capability"]: c["status"] for c in contract["capabilities"]}
    # Binomial intervals need the whole observation contract: uncorrected events and their count provenance.
    contract_holds = all(status.get(c) == "supported" for c in ("uncorrected_observations", "count_provenance"))
    admitted_policies = {"empty-mitigation"} if contract_holds else set()
    admitted = np.array([o["processing"] in admitted_policies for o in observations])
    result = bdsc.contrast_readout(k, n, contrasts, cert.CASE_ALPHA, admitted)
    return {
        "admitted_policies": sorted(admitted_policies),
        "tallies": [tallies[i] for i in range(len(observations))],
        "contrasts": [
            {"family": c[0], "terms": [[j, w] for j, w in c[2]], "interval": [lo, hi], "status": st}
            for c, lo, hi, st in zip(contrasts, result["lower"], result["upper"], result["status"], strict=True)
        ],
    }


def synthetic_draw(directory: Path, settings: int) -> Path:
    """A well-formed AQN uint16 record of 2 x settings seeded values, for the offline self-test only."""
    import anu_qrng

    values = [int(v) for v in np.random.default_rng(11).integers(0, 65536, size=2 * settings)]
    raw = json.dumps({"success": True, "type": "uint16", "length": str(len(values)), "data": values})
    record = anu_qrng.record_from(f"{anu_qrng.ENDPOINTS['aqn']}?length={len(values)}&type=uint16", "self-test", raw)
    path = directory / "draw.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def self_test() -> int:
    """Build seeded jobs, write each as a collected run with ideal E0 counts in collect's shape, and read them out:
    an unsupported contract reads every contrast not_admitted, a supported one reads every contrast compatible, and
    a draft, a short iteration, a swapped seed and a duplicated run are refused."""
    import copy
    import tempfile

    case = json.loads(CASE.read_text(encoding="utf-8"))
    trials = case["resources"]["eligible_trials_per_setting"]
    selected_mode, other_mode = 4, 0
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        draw = synthetic_draw(root, len(case["observations"]))
        runs = []
        for name, files in documents(draw).items():
            run = root / name
            run.mkdir()
            for file, content in files.items():
                (run / file).write_bytes(content)
            manifest = json.loads(files["cases.json"])
            iterations = []
            for setting in manifest["settings"]:
                k = round(setting["ideal_selected_E0"] * trials)
                one = ["0"] * cert.MODES
                one[selected_mode if selected_mode in manifest["selected_modes"] else other_mode] = "1"
                miss = ["0"] * cert.MODES
                miss[next(m for m in range(cert.MODES) if m not in manifest["selected_modes"])] = "1"
                counts = {",".join(one): k, ",".join(miss): trials - k}
                ran = {key: setting.get(key) for key in ("circuit_params", "compilation_seed")}
                iterations.append({"iteration": ran, "counts": counts, "samples": trials})
            result = {"status": {"status": "completed"}, "partial": False, "iterations": iterations}
            (run / "results.json").write_text(json.dumps(result), encoding="utf-8")
            runs.append(run)
        closed = readout(runs)
        require({c["status"] for c in closed["contrasts"]} == {"not_admitted"}, "self-test: unsupported contract")
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        for capability in contract["capabilities"]:
            if capability["capability"] in ("uncorrected_observations", "count_provenance"):
                capability["status"] = "supported"
        opened = readout(runs, contract)
        statuses = {(c["family"], c["status"]) for c in opened["contrasts"]}
        empty = [
            c
            for c, o in zip(opened["contrasts"], cert.case_contrasts(case["observations"]), strict=True)
            if all(case["observations"][j]["processing"] == "empty-mitigation" for j, _ in o[2])
        ]
        require(all(c["status"] == "compatible" for c in empty), f"self-test: ideal counts read {statuses}")
        refusals = 0
        for mutate in ("draft", "short", "seed", "duplicate"):
            target = runs[0]
            saved = {f: (target / f).read_bytes() for f in ("cases.json", "results.json")}
            manifest = json.loads(saved["cases.json"])
            result = json.loads(saved["results.json"])
            batch = list(runs)
            if mutate == "draft":
                manifest["draft"] = True
            elif mutate == "short":
                result["iterations"][0]["samples"] = trials - 1
            elif mutate == "seed":
                result["iterations"][0]["iteration"]["compilation_seed"] += 1
            else:
                batch = [*runs, copy.copy(target)]
            (target / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
            (target / "results.json").write_text(json.dumps(result), encoding="utf-8")
            try:
                readout(batch, contract)
            except ValueError:
                refusals += 1
            for f, content in saved.items():
                (target / f).write_bytes(content)
        require(refusals == 4, f"self-test: {4 - refusals} malformed run sets were read out")
    print(f"bdsc cases self-test: {len(runs)} synthetic jobs read out; 4 malformed run sets refused")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--local", type=Path)
    group.add_argument("--readout", type=Path, nargs="+")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--draw", type=Path)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.write:
        write(args.write, args.draw)
    elif args.check:
        check(args.check, args.draw)
    elif args.local:
        local(args.local)
    else:
        print(json.dumps(readout(args.readout), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
